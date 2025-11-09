# UE5 Blueprint Exporter for Claude Code

> **Export Unreal Engine 5 blueprints to JSON and Markdown for AI-powered analysis**

Transform your UE5 blueprints into Claude Code-friendly documentation. Ask questions about your project in natural language, understand complex blueprint logic, and generate comprehensive documentation automatically.

[![UE5](https://img.shields.io/badge/UE5-5.3-0E1128?logo=unrealengine)](https://www.unrealengine.com/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Mac%20%7C%20Windows-lightgrey)](#system-requirements)

---

## ✨ Why Use This?

**Problem:** UE5 blueprints are visual and locked inside .uasset files. You can't:
- Search across all blueprints easily
- Ask AI questions about your blueprint logic
- Generate documentation automatically
- Understand complex blueprint relationships

**Solution:** This tool extracts *everything* from your blueprints into readable formats:

```
Ask Claude Code: "How does BP_PlayerCharacter handle movement?"

Claude reads the exported data and explains:
  ✓ Input actions (IA_Move, IA_Look)
  ✓ Movement functions (Add Movement Input)
  ✓ Direction vectors (Forward/Right)
  ✓ Complete execution flow
```

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **🔍 Full Graph Extraction** | Complete node graphs with connections, pins, and default values |
| **📊 Variables & Functions** | All blueprint variables, functions, parameters, and return types |
| **🔧 Components** | Component hierarchy with class information |
| **🔗 Dependencies** | Track all asset references and dependencies |
| **📄 Dual Output** | JSON (machine-readable) + Markdown (AI-friendly) |
| **🤖 Claude Code Ready** | Optimized for natural language queries |

---

## 📦 Quick Start

### 1️⃣ Download & Install

**Option A: Automated with Claude Code** 🚀 (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/UE5-Blueprint-Exporter.git
   cd UE5-Blueprint-Exporter
   ```

2. Start Claude Code:
   ```bash
   claude-code
   ```

3. In Claude Code, type the slash command:
   ```
   /setup-ue5-project
   ```

4. Provide your UE5 project path when asked

5. Claude Code will automatically:
   - ✅ Copy plugin files to your project
   - ✅ Copy Python scripts to your project
   - ✅ Generate your custom export command
   - ✅ Show you the next steps

**That's it!** No manual file copying needed.

**Option B: Manual**

Copy to your UE5 project:
```
YourProject/
├── Plugins/
│   └── BlueprintExporter/          ← Copy entire folder
└── Content/
    └── Python/                      ← Copy Python scripts
        ├── blueprint_watcher.py
        └── generate_markdown_from_json.py
```

### 2️⃣ Enable Python Plugin

1. Open your project in **UE5 Editor**
2. Go to **Edit → Plugins**
3. Search **"Python Editor Script Plugin"**
4. **Enable** and **Restart** editor

### 3️⃣ Compile the C++ Plugin

**Automatic (Recommended):**
1. Right-click your `.uproject` file
2. Select **"Generate Visual Studio/Xcode project files"**
3. Re-open the project
4. Click **"Yes"** when UE5 asks to compile the plugin

**Manual (if needed):**
- See [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) for detailed compilation steps

### 4️⃣ Export Your Blueprints

**⚠️ IMPORTANT:** UE5's Python console doesn't support multi-line commands. Use the **single-line command** below.

**In UE5 Editor:**

1. Open **Window → Developer Tools → Output Log** (check the Output Log for results)
2. At the bottom, find the Python command input field (looks like: `Cmd: ▊`)
3. **Run this single-line command** (all on ONE line):

```python
import sys; sys.path.append("/Users/yourname/Documents/Unreal Projects/YourProject/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
```

**Real Example:**
```python
import sys; sys.path.append("/Users/fromastermarv/Documents/Unreal Projects/BlueprintDemo3/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
```

4. Press **Enter**
5. **Check the Output Log window** (not the Python console) for results

**Alternative Method (Better for Debugging):**

Use the simplified test script (use ABSOLUTE path):
```python
py "/ABSOLUTE/PATH/TO/YOUR/PROJECT/Content/Python/test_export.py"
```

Example:
```python
py "/Users/fromastermarv/Documents/Unreal Projects/BlueprintDemo3/Content/Python/test_export.py"
```

This runs the export with better error reporting visible in the Output Log.

**You'll see in Output Log:**
```
============================================================
UE5 Blueprint Exporter for Claude Code
============================================================
Export complete! Exported 50 blueprints

HOW TO USE WITH CLAUDE CODE:
------------------------------------------------------------
Copy this prompt:

I have exported UE5 blueprints to /Your/Project/ClaudeCodeDocs/Blueprints/
Please read the index.md file to see all available blueprints,
then answer my questions about the blueprint logic.
------------------------------------------------------------

Example questions:
- How does BP_FirstPersonCharacter handle movement?
- Walk me through the weapon firing sequence
```

---

## 📂 Output Structure

```
YourProject/ClaudeCodeDocs/Blueprints/
├── index.md                              # Overview with all blueprints
│
├── Characters/
│   ├── BP_PlayerCharacter.json          # Full blueprint data
│   ├── BP_PlayerCharacter.md            # Human-readable summary
│   ├── BP_Enemy.json
│   └── BP_Enemy.md
│
└── Weapons/
    ├── BP_Rifle.json
    └── BP_Rifle.md
```

### 📋 Sample Markdown Output

```markdown
# BP_PlayerCharacter

**Type:** Blueprint
**Parent Class:** Character
**Generated Class:** BP_PlayerCharacter_C

## Components
- FirstPersonCamera (CameraComponent)
- FirstPersonMesh (SkeletalMeshComponent)

## Variables
| Name | Type | Default |
|------|------|---------|
| Health | float | 100.0 |
| bHasRifle | bool | false |

## Graphs

### EventGraph
**Total Nodes:** 24

**Event Nodes:**
- Event BeginPlay

**Function Calls:**
- Jump
- Add Movement Input
- Get Actor Forward Vector
- Add Controller Pitch Input

## Dependencies
- /Game/FirstPerson/Input/Actions/IA_Move
- /Game/FirstPerson/Input/Actions/IA_Jump
```

---

## 💬 Usage with Claude Code

Once exported, use **Claude Code** to analyze your blueprints in natural language:

```bash
cd /path/to/your/ue5/project
claude-code
```

### Example Questions:

**Understanding Logic:**
> "How does BP_PlayerCharacter handle movement?"

**Finding Connections:**
> "What blueprints depend on BP_GameMode?"

**Exploring Components:**
> "List all weapons in my project and their components"

**Variables & State:**
> "Show me all blueprints with a 'Health' variable"

**Debugging:**
> "Which blueprints call the 'TakeDamage' function?"

---

## 🔧 What Gets Exported

### Complete Blueprint Data:

| Data Type | Details |
|-----------|---------|
| **Graphs** | EventGraph, UserConstructionScript, Custom Functions |
| **Nodes** | Node type, title, category, position (x, y) |
| **Pins** | Name, direction, type, default values |
| **Connections** | Node-to-node execution flow |
| **Variables** | Name, type, category, default value, exposed status |
| **Functions** | Name, parameters, return type, graph implementation |
| **Components** | Name, class, hierarchy |
| **Dependencies** | All referenced assets, blueprints, and classes |

---

## ⚙️ Configuration

Edit `Content/Python/blueprint_watcher.py` to customize:

```python
# Output directory (relative to project root)
OUTPUT_DIR = "ClaudeCodeDocs/Blueprints"

# Generate markdown files (recommended for Claude Code)
GENERATE_MARKDOWN = True

# Include detailed graph nodes (requires C++ plugin)
INCLUDE_GRAPH_NODES = True
```

---

## 🛠️ System Requirements

| Component | Requirement |
|-----------|-------------|
| **Unreal Engine** | 5.0 or higher (tested on 5.3) |
| **Python** | 3.x (included with UE5) |
| **C++ Compiler** | Xcode (Mac) or Visual Studio 2019/2022 (Windows) |
| **Claude Code** | Optional, for AI-powered analysis |

---

## 📖 Documentation

- **[SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)** - Detailed installation guide with troubleshooting
- **[BLUEPRINT_EXPORTER_README.md](BLUEPRINT_EXPORTER_README.md)** - Architecture, design decisions, and MVP details

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   UE5 Editor (Python Plugin)            │
│   blueprint_watcher.py                  │
│   • Orchestrates export                 │
│   • Generates markdown                  │
└──────────────┬──────────────────────────┘
               │ calls C++ API
               ▼
┌─────────────────────────────────────────┐
│   C++ Plugin (BlueprintExporter)        │
│   BlueprintExporter.cpp                 │
│   • Extracts graph nodes                │
│   • Serializes to JSON                  │
│   • Accesses internal blueprint data    │
└──────────────┬──────────────────────────┘
               │ writes files
               ▼
┌─────────────────────────────────────────┐
│   Output: ClaudeCodeDocs/Blueprints/    │
│   • .json (full graph data)             │
│   • .md (human-readable)                │
│   • index.md (project overview)         │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Export Command Shows No Output
✅ **Solution:**
- **Check the Output Log window** (not the Python console) - that's where `unreal.log()` messages appear
- Look for text starting with "UE5 Blueprint Exporter for Claude Code"
- If you see nothing, the script may have crashed silently

### Script Runs But Nothing Happens
✅ **Solution:**
Use the test script for better error reporting (use absolute path):
```python
py "/absolute/path/to/your/project/Content/Python/test_export.py"
```
This will show detailed error messages in the Output Log.

### Multi-Line Commands Don't Work
✅ **Problem:** UE5 Python console can't handle newlines properly

**Solution:** Always use single-line commands:
```python
# ✅ CORRECT (single line)
import sys; sys.path.append("/path/to/Python"); import blueprint_watcher; blueprint_watcher.main()

# ❌ WRONG (multi-line - will fail)
import sys
sys.path.append("/path/to/Python")
import blueprint_watcher
blueprint_watcher.main()
```

Or use `py "path/to/script.py"` to run a script file.

### "BlueprintExporter plugin not found"
✅ **Solution:**
- Verify plugin compiled (check **Edit → Plugins**)
- Look for "Blueprint Exporter" (should be enabled)
- Try regenerating project files and rebuilding

### "Could not load Python file"
✅ **Solution:**
- Use **absolute path** in the Python command
- Verify `blueprint_watcher.py` exists in `Content/Python/`
- Check for typos in the path

### No Markdown Files Generated
✅ **Solution:**
The export might have failed silently. Check:
1. Run `py "/absolute/path/to/your/project/Content/Python/test_export.py"` for detailed errors
2. Verify the plugin is compiled and enabled
3. Check Output Log for error messages

### Compilation Errors on Mac
✅ **Solution:**
- Install Xcode Command Line Tools: `xcode-select --install`
- Verify UE5 version matches (built for 5.3)

---

## 🤝 Contributing

Contributions are welcome! This is an open-source tool for the UE5 and AI community.

### Ideas for Enhancement:
- [ ] **Auto-refresh** - Watch for blueprint changes and auto-export
- [ ] **MCP Server** - Model Context Protocol integration
- [ ] **Blueprint Diff** - Compare blueprint versions
- [ ] **Visual Graphs** - Generate node graph images
- [ ] **Search Interface** - Web UI for blueprint search
- [ ] **Blueprint Stats** - Complexity metrics and analysis

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

Feel free to use in personal and commercial projects!

---

## 🙏 Credits

**Built for:** [Claude Code](https://claude.com/claude-code) by Anthropic

**Technologies:**
- UE5 C++ Editor Plugin API
- UE5 Python Scripting Plugin
- Blueprint Graph Node Extraction
- JSON Serialization

**Special Thanks:**
- Unreal Engine community
- Claude Code users
- Contributors and testers

---

## 🌟 Star This Repository!

If this tool helps you, please **⭐ star the repository** to help others discover it!

### Share Your Results:
- Tweet [@UnrealEngine](https://twitter.com/UnrealEngine) with your use case
- Share in [Unreal Slackers Discord](https://unrealslackers.org/)
- Post in [r/unrealengine](https://reddit.com/r/unrealengine)

---

**Made with ❤️ for the UE5 and AI community**

[Report Bug](https://github.com/YOUR_USERNAME/UE5-Blueprint-Exporter/issues) · [Request Feature](https://github.com/YOUR_USERNAME/UE5-Blueprint-Exporter/issues) · [Discussions](https://github.com/YOUR_USERNAME/UE5-Blueprint-Exporter/discussions)
