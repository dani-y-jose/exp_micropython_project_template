#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v uv >/dev/null 2>&1; then
    echo "error: 'uv' not found on PATH. Install from https://docs.astral.sh/uv/ first." >&2
    exit 1
fi

mkdir -p .vscode

echo "==> Installing micropython-esp32-stubs into .vscode/stubs"
uv pip install --target .vscode/stubs micropython-esp32-stubs

echo "==> Fetching ssd1306.py for autocomplete (driver is mip-installed at runtime)"
curl -fsSL -o .vscode/stubs/ssd1306.py \
    https://raw.githubusercontent.com/micropython/micropython-lib/master/micropython/drivers/display/ssd1306/ssd1306.py

echo "==> Writing .vscode/settings.json"
cat > .vscode/settings.json <<'JSON'
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportMissingModuleSource": "none"
    },
    "python.analysis.typeCheckingMode": "basic",
    "python.autoComplete.extraPaths": [
        "${workspaceFolder}/.vscode/stubs"
    ],
    "python.analysis.extraPaths": [
        "${workspaceFolder}/.vscode/stubs"
    ]
}
JSON

echo "==> Writing .vscode/tasks.json"
cat > .vscode/tasks.json <<'JSON'
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "MicroPython: Live Run (RAM)",
            "type": "shell",
            "command": "uvx mpremote mount . run ${file}",
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "presentation": {
                "reveal": "always",
                "panel": "shared",
                "clear": true
            },
            "problemMatcher": []
        },
        {
            "label": "MicroPython: Upload to Flash",
            "type": "shell",
            "command": "uvx mpremote cp -r lib : + cp ${file} :main.py + reset",
            "group": "build",
            "presentation": {
                "reveal": "always",
                "panel": "shared",
                "clear": true
            },
            "problemMatcher": []
        }
    ]
}
JSON

echo
echo "Done."
echo "  - Stubs installed at .vscode/stubs"
echo "  - VS Code settings + tasks written to .vscode/"
echo "  - Run a script with: Cmd+Shift+B (Live Run) or pick 'MicroPython: Upload to Flash' from Tasks: Run Task"
