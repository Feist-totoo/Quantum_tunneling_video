(function () {
    var bridge = new File("D:/MY_WORLD/Tools/After Effects MCP/build/scripts/mcp-bridge-auto.jsx");
    var status = new File("C:/Users/liuzh/Desktop/1/ae_project/config/ae_mcp_bootstrap_status.txt");

    function writeStatus(message) {
        status.encoding = "UTF-8";
        if (status.open("w")) {
            status.write(message);
            status.close();
        }
    }

    try {
        var scriptingAllowed = false;
        try {
            scriptingAllowed = app.preferences.getPrefAsLong(
                "Main Pref Section",
                "Pref_SCRIPTING_FILE_NETWORK_SECURITY"
            ) === 1;
        } catch (readLegacyPrefError) {}
        try {
            scriptingAllowed = scriptingAllowed || app.preferences.getPrefAsLong(
                "Main Pref Section v2",
                "Pref_SCRIPTING_FILE_NETWORK_SECURITY"
            ) === 1;
        } catch (readV2PrefError) {}

        if (!scriptingAllowed) {
            throw new Error(
                "Please enable Allow Scripts to Write Files and Access Network in After Effects preferences."
            );
        }

        if (!bridge.exists) {
            throw new Error("MCP bridge script not found: " + bridge.fsName);
        }

        $.evalFile(bridge);
        writeStatus("OK\nAE_VERSION=" + app.version + "\nBRIDGE=" + bridge.fsName + "\n");
    } catch (error) {
        writeStatus("ERROR\n" + error.toString() + "\n");
        alert("AE MCP bootstrap failed:\n" + error.toString());
    }
})();
