# UE5 Blueprint Exporter for Claude Code

Export Unreal Engine 5 blueprints to JSON and Markdown format for AI-powered analysis with Claude Code.

![UE5](https://img.shields.io/badge/UE5-5.3-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Mac%20%7C%20Windows-lightgrey)

## Features

- ✅ **Full Blueprint Graph Extraction** - Extract complete node graphs with connections, pins, and values
- ✅ **Variables & Functions** - Export all blueprint variables, functions, and parameters
- ✅ **Components & Dependencies** - Track components and asset dependencies
- ✅ **JSON + Markdown Output** - Machine-readable JSON and human-friendly Markdown
- ✅ **Claude Code Integration** - Designed for AI-powered blueprint analysis
- ✅ **C++ Plugin + Python** - Robust extraction using UE5 Editor API

## Quick Start

### 1. Installation

Copy the plugin and Python scripts to your UE5 project:

```
YourProject/
├── Plugins/BlueprintExporter/     ← Copy this folder
└── Content/Python/                 ← Copy Python scripts
    ├── blueprint_watcher.py
    └── generate_markdown_from_json.py
```

### 2. Enable Python Plugin

1. Open your project in **UE5 Editor**
2. **Edit → Plugins** → Search "Python Editor Script Plugin"
3. Enable and restart

### 3. Compile the C++ Plugin

- Right-click your `.uproject` → **Generate Visual Studio/Xcode files**
- Reopen the project → Click **Yes** when prompted to compile

### 4. Run the Export

In UE5 **Output Log**:

```python
import sys; sys.path.append("/absolute/path/to/YourProject/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
```

## Output Example

```
YourProject/ClaudeCodeDocs/Blueprints/
├── index.md
├── Characters/
│   ├── BP_Player.json          # Full blueprint data
│   └── BP_Player.md            # Human-readable summary
└── Weapons/
    ├── BP_Rifle.json
    └── BP_Rifle.md
```

### Sample Markdown Output

```markdown
# BP_PlayerCharacter

**Type:** Blueprint
**Parent Class:** Character
**Components:**
- FirstPersonCamera (CameraComponent)
- FirstPersonMesh (SkeletalMeshComponent)

**Variables:**
| Name | Type | Default |
|------|------|---------|
| Health | float | 100.0 |
| MaxHealth | float | 100.0 |

**Graphs:**
### EventGraph
**Total Nodes:** 24
**Function Calls:**
- Jump
- Add Movement Input
- Get Actor Forward Vector
```

## Usage with Claude Code

Once exported, ask Claude Code about your blueprints:

```bash
cd /path/to/your/project
claude-code
```

**Example questions:**
- "How does BP_PlayerCharacter handle movement?"
- "What components does BP_Weapon have?"
- "Show me all blueprints that reference BP_GameMode"
- "List all variables in BP_InventorySystem"

## What Gets Exported

### From C++ Plugin:
- ✅ Complete graph structure (nodes, pins, connections)
- ✅ Node positions and types
- ✅ Variables with types and defaults
- ✅ Functions with parameters and implementations
- ✅ Components with class information
- ✅ All asset dependencies

### Output Formats:
- **JSON** - Complete machine-readable data for programmatic access
- **Markdown** - Human-readable summaries optimized for Claude Code

## Configuration

Edit `Content/Python/blueprint_watcher.py`:

```python
# Output directory
OUTPUT_DIR = "ClaudeCodeDocs/Blueprints"

# Generate markdown
GENERATE_MARKDOWN = True

# Include graph nodes (requires C++ plugin)
INCLUDE_GRAPH_NODES = True
```

## System Requirements

- **Unreal Engine 5.0+** (tested on 5.3)
- **Python 3** (included with UE5)
- **C++ Compiler:**
  - Mac: Xcode Command Line Tools
  - Windows: Visual Studio 2019/2022
- **Claude Code** (optional, for AI analysis)

## Documentation

- [**SETUP_INSTRUCTIONS.md**](SETUP_INSTRUCTIONS.md) - Detailed installation guide
- [**BLUEPRINT_EXPORTER_README.md**](BLUEPRINT_EXPORTER_README.md) - Architecture & design

## Architecture

```
┌─────────────────────────────────────┐
│   UE5 Editor (Python Plugin)        │
│   - blueprint_watcher.py            │
│   - Orchestrates export             │
└──────────────┬──────────────────────┘
               │ calls
               ▼
┌─────────────────────────────────────┐
│   C++ Plugin (BlueprintExporter)    │
│   - Extracts graph nodes            │
│   - Serializes to JSON              │
└──────────────┬──────────────────────┘
               │ outputs
               ▼
┌─────────────────────────────────────┐
│   ClaudeCodeDocs/Blueprints/        │
│   - .json (full data)               │
│   - .md (human-readable)            │
└─────────────────────────────────────┘
```

## Troubleshooting

### "BlueprintExporter plugin not found"
- Ensure the plugin compiled successfully
- Check **Edit → Plugins** for "Blueprint Exporter"
- Restart the editor

### "Could not load Python file"
- Use **absolute path** in Python command
- Verify `blueprint_watcher.py` exists in `Content/Python/`

### No Markdown Files
Run the markdown generator separately:
```python
import sys; sys.path.append("/path/to/Content/Python"); import generate_markdown_from_json; generate_markdown_from_json.process_json_files()
```

## Contributing

Contributions welcome! This tool is designed to make UE5 blueprints accessible to AI analysis.

### Areas for Enhancement:
- [ ] Auto-refresh on blueprint changes
- [ ] MCP server integration
- [ ] Blueprint comparison/diff
- [ ] Visual graph generation
- [ ] Blueprint search interface

## License

MIT License - Feel free to use in your projects!

## Credits

Built for use with [Claude Code](https://claude.com/claude-code) by Anthropic.

Uses:
- UE5 C++ Editor Plugin API
- UE5 Python Scripting Plugin
- Blueprint Graph Node Extraction
- JSON Serialization

---

**Made with ❤️ for the UE5 and AI community**
