"""Small local client for the Resolve MCP configured in Codex.

Use the Resolve MCP virtual-environment Python to run this file.  It reads the
existing Codex TOML configuration, starts the configured stdio server, and
either lists tools or calls one tool.  No credentials are copied into this
project.
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
SERVER_NAME = "davinci-resolve"


def _server_parameters() -> StdioServerParameters:
    with CONFIG_PATH.open("rb") as handle:
        config = tomllib.load(handle)
    server = config["mcp_servers"][SERVER_NAME]
    env = os.environ.copy()
    env.update({str(key): str(value) for key, value in server.get("env", {}).items()})
    return StdioServerParameters(
        command=server["command"],
        args=list(server.get("args", [])),
        env=env,
    )


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {key: _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


async def _run(
    command: str,
    tool_name: str | None,
    arguments: dict[str, Any],
    batch: list[dict[str, Any]] | None = None,
) -> Any:
    params = _server_parameters()
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            if command == "list":
                response = await session.list_tools()
                return [tool.name for tool in response.tools]
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
            if command == "batch":
                results = []
                for index, item in enumerate(batch or []):
                    name = item.get("tool")
                    call_arguments = item.get("arguments", {})
                    if not isinstance(name, str) or not isinstance(call_arguments, dict):
                        raise ValueError(f"invalid batch item at index {index}")
                    response = await session.call_tool(name, arguments=call_arguments)
                    results.append({"tool": name, "response": _jsonable(response)})
                return results
            if not tool_name:
                raise ValueError("call requires a tool name")
            if command == "confirm":
                preview_response = await session.call_tool(tool_name, arguments=arguments)
                preview = _jsonable(preview_response)
                token = (
                    (preview.get("structuredContent") or {})
                    .get("result", {})
                    .get("confirm_token")
                )
                if not token:
                    raise ValueError("tool did not return a confirmation token")
                confirmed_arguments = dict(arguments)
                confirmed_params = dict(confirmed_arguments.get("params") or {})
                confirmed_params["confirm_token"] = token
                confirmed_arguments["params"] = confirmed_params
                response = await session.call_tool(tool_name, arguments=confirmed_arguments)
                return {
                    "preview": preview,
                    "response": _jsonable(response),
                }
            response = await session.call_tool(tool_name, arguments=arguments)
            return _jsonable(response)


def main() -> int:
    parser = argparse.ArgumentParser(description="List or call the configured Resolve MCP tools")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list")
    schema_parser = subparsers.add_parser("schema")
    schema_parser.add_argument("tool")
    call_parser = subparsers.add_parser("call")
    call_parser.add_argument("tool")
    call_parser.add_argument("arguments", nargs="?", default="{}", help="JSON object")
    call_parser.add_argument(
        "--image-out",
        help="Write the first image content block returned by the tool to this path",
    )
    confirm_parser = subparsers.add_parser(
        "confirm", help="Preflight and confirm a destructive tool call in one MCP session"
    )
    confirm_parser.add_argument("tool")
    confirm_parser.add_argument("arguments", nargs="?", default="{}", help="JSON object")
    batch_parser = subparsers.add_parser("batch")
    batch_parser.add_argument("path", help="JSON file containing [{tool, arguments}, ...]")
    args = parser.parse_args()

    try:
        arguments = json.loads(args.arguments) if args.command in {"call", "confirm"} else {}
        if not isinstance(arguments, dict):
            raise ValueError("arguments must decode to a JSON object")
        batch = None
        if args.command == "batch":
            batch = json.loads(Path(args.path).read_text(encoding="utf-8"))
            if not isinstance(batch, list):
                raise ValueError("batch file must decode to a JSON list")
        result = asyncio.run(
            _run(args.command, getattr(args, "tool", None), arguments, batch=batch)
        )
        image_out = getattr(args, "image_out", None)
        if image_out:
            image_block = next(
                (
                    block
                    for block in result.get("content", [])
                    if block.get("type") == "image" and block.get("data")
                ),
                None,
            )
            if image_block is None:
                raise ValueError("tool result did not contain an image block")
            output_path = Path(image_out).expanduser().resolve()
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(base64.b64decode(image_block["data"]))
            image_block["data"] = f"<written to {output_path}>"
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(f"Resolve MCP client failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
