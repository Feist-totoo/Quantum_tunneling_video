"""Local command-line client for the After Effects MCP configured in Codex.

Run with the Python interpreter from the Resolve MCP virtual environment, which
already contains the MCP Python SDK. Configuration is read from the user's
existing Codex config; no credentials or duplicated settings are stored here.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import sys
import tomllib
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


CONFIG_PATH = Path.home() / ".codex" / "config.toml"
SERVER_NAME = "after-effects"


def jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return value


def server_parameters() -> StdioServerParameters:
    with CONFIG_PATH.open("rb") as handle:
        config = tomllib.load(handle)
    server = config["mcp_servers"][SERVER_NAME]
    environment = os.environ.copy()
    environment.update({str(key): str(value) for key, value in server.get("env", {}).items()})
    return StdioServerParameters(
        command=server["command"],
        args=list(server.get("args", [])),
        env=environment,
    )


async def run(command: str, tool_name: str | None, arguments: dict[str, Any]) -> Any:
    async with stdio_client(server_parameters()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            if command == "list":
                response = await session.list_tools()
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                    }
                    for tool in response.tools
                ]
            if command == "schema":
                response = await session.list_tools()
                for tool in response.tools:
                    if tool.name == tool_name:
                        return {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema,
                        }
                raise ValueError(f"unknown tool: {tool_name}")
            if not tool_name:
                raise ValueError("call requires a tool name")
            return jsonable(await session.call_tool(tool_name, arguments=arguments))


def main() -> int:
    parser = argparse.ArgumentParser(description="Call the configured After Effects MCP")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    schema_parser = subparsers.add_parser("schema")
    schema_parser.add_argument("tool")
    call_parser = subparsers.add_parser("call")
    call_parser.add_argument("tool")
    call_parser.add_argument("arguments", nargs="?", default="{}")
    call_parser.add_argument("--image-out")
    call_parser.add_argument("--images-out-dir")
    args = parser.parse_args()

    try:
        arguments = json.loads(args.arguments) if args.command == "call" else {}
        if not isinstance(arguments, dict):
            raise ValueError("arguments must decode to a JSON object")
        result = asyncio.run(run(args.command, getattr(args, "tool", None), arguments))
        image_out = getattr(args, "image_out", None)
        images_out_dir = getattr(args, "images_out_dir", None)
        if images_out_dir:
            output_dir = Path(images_out_dir).expanduser().resolve()
            output_dir.mkdir(parents=True, exist_ok=True)
            image_blocks = [
                item
                for item in result.get("content", [])
                if item.get("type") == "image" and item.get("data")
            ]
            if not image_blocks:
                raise ValueError("tool result did not contain any image blocks")
            for index, block in enumerate(image_blocks, start=1):
                mime = str(block.get("mimeType", "image/png"))
                extension = ".jpg" if "jpeg" in mime else ".png"
                output_path = output_dir / f"frame_{index:03d}{extension}"
                output_path.write_bytes(base64.b64decode(block["data"]))
                block["data"] = f"<written to {output_path}>"
        if image_out:
            block = next(
                (
                    item
                    for item in result.get("content", [])
                    if item.get("type") == "image" and item.get("data")
                ),
                None,
            )
            if block is None:
                raise ValueError("tool result did not contain an image block")
            output_path = Path(image_out).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(base64.b64decode(block["data"]))
            block["data"] = f"<written to {output_path}>"
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(f"After Effects MCP client failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
