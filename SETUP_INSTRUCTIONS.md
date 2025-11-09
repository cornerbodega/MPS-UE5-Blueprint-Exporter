# UE5 Blueprint Exporter - Setup Instructions

## What This Does
Exports UE5 blueprints to JSON and Markdown format for use with Claude Code or AI analysis. Extracts full blueprint data including:
- Graph nodes and connections
- Variables, functions, components
- Dependencies and references
- All organized in human-readable format

## Installation (5 minutes)

### Step 1: Extract Files to Your Project

1. **Unzip** `UE5_Blueprint_Exporter.zip`

2. **Copy these folders** to your UE5 project root:
   ```
   YourProject/
   ├── Plugins/BlueprintExporter/          ← Copy this folder
   └── Content/Python/                      ← Copy these Python files
       ├── blueprint_watcher.py
       └── generate_markdown_from_json.py
   ```

### Step 2: Enable Python Plugin in UE5

1. Open your project in **UE5 Editor**
2. Go to **Edit → Plugins**
3. Search for **"Python Editor Script Plugin"**
4. **Enable** it and restart the editor

### Step 3: Compile the C++ Plugin

**If your project is Blueprint-only**, you'll need to add C++ support first:

#### Option A: Let UE5 Compile Automatically (Easiest)
1. Close UE5 Editor
2. Right-click your `.uproject` file → **Generate Xcode/Visual Studio files**
3. Open the `.uproject` again
4. UE5 will detect the new plugin and ask to compile → Click **Yes**

#### Option B: Manual Compilation (Mac)
```bash
cd /path/to/your/project

# Generate project files
"/Users/Shared/Epic Games/UE_5.X/Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh" \
  -project="YourProject.uproject" -game

# Build the plugin
"/Users/Shared/Epic Games/UE_5.X/Engine/Build/BatchFiles/Mac/Build.sh" \
  YourProjectEditor Mac Development "YourProject.uproject" -WaitMutex
```

Replace `5.X` with your UE5 version (e.g., `5.3`).

#### Option C: Windows
```cmd
cd C:\Path\To\YourProject

:: Generate project files
"C:\Program Files\Epic Games\UE_5.X\Engine\Build\BatchFiles\GenerateProjectFiles.bat" ^
  -project="YourProject.uproject"

:: Build
"C:\Program Files\Epic Games\UE_5.X\Engine\Build\BatchFiles\Build.bat" ^
  YourProjectEditor Win64 Development "YourProject.uproject"
```

### Step 4: Run the Export

**⚠️ IMPORTANT:** UE5's Python console doesn't support multi-line commands. Use single-line commands only.

1. In UE5 Editor, open **Window → Developer Tools → Output Log**

2. At the bottom, find the Python command input (looks like: `Cmd: ▊`)

3. **Run this single-line command** (replace with YOUR absolute path):
   ```python
   import sys; sys.path.append("ABSOLUTE_PATH_TO_YOUR_PROJECT/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
   ```

   **Example:**
   ```python
   import sys; sys.path.append("/Users/yourname/Documents/Unreal Projects/MyProject/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
   ```

4. **Alternative (Better for Debugging):**

   Use absolute path with the test script:
   ```python
   py "/ABSOLUTE/PATH/TO/YOUR/PROJECT/Content/Python/test_export.py"
   ```

   Example:
   ```python
   py "/Users/yourname/Documents/Unreal Projects/MyProject/Content/Python/test_export.py"
   ```

   This provides detailed error messages in the Output Log.

5. **Check the Output Log** for results (NOT the Python console):
   ```
   ============================================================
   UE5 Blueprint Exporter for Claude Code
   ============================================================
   Export complete! Exported X blueprints to ClaudeCodeDocs/Blueprints
   ```

### Step 5: View the Results

Exported files will be in:
```
YourProject/ClaudeCodeDocs/Blueprints/
├── index.md                    ← Overview of all blueprints
├── YourGameFolder/
│   ├── BP_YourBlueprint.json  ← Full data (machine-readable)
│   └── BP_YourBlueprint.md    ← Human-readable summary
└── ...
```

## Usage with Claude Code

Once exported, you can ask Claude Code questions about your blueprints:

```bash
cd /path/to/your/project
claude-code
```

Then ask:
- "How does BP_PlayerCharacter handle movement?"
- "What components does BP_Weapon have?"
- "Show me all blueprints that use BP_GameMode"
- "List all variables in BP_InventorySystem"

## Troubleshooting

### Export Command Shows No Output
- **Check the Output Log window** (not the Python console) - that's where results appear
- Look for messages starting with "UE5 Blueprint Exporter for Claude Code"
- If nothing appears, the script may have failed silently

### Multi-Line Commands Don't Work
**Problem:** UE5 Python console can't handle newlines

**Solution:** Always use single-line commands:
```python
# ✅ CORRECT (single line)
import sys; sys.path.append("/path/to/Python"); import blueprint_watcher; blueprint_watcher.main()

# ❌ WRONG (multi-line - will fail silently)
import sys
sys.path.append("/path/to/Python")
import blueprint_watcher
```

Or use the test script with absolute path:
```python
py "/absolute/path/to/your/project/Content/Python/test_export.py"
```

### "BlueprintExporter plugin not found"
- Make sure the plugin compiled successfully
- Check **Edit → Plugins** and verify "Blueprint Exporter" is enabled
- Try restarting the editor

### "Could not load Python file"
- Use the **absolute path** in your Python command
- Verify `blueprint_watcher.py` is in `Content/Python/`
- Make sure Python plugin is enabled

### No Markdown Files Generated
The export likely failed. Use the test script for detailed errors:
```python
py "/absolute/path/to/your/project/Content/Python/test_export.py"
```
Check the Output Log for error messages.

### Compilation Errors
If you get C++ compilation errors:
1. Make sure you have Xcode (Mac) or Visual Studio (Windows) installed
2. Check that your UE5 version matches (this was built for UE5.3)
3. Try cleaning: Delete `Intermediate/` and `Binaries/` folders, then rebuild

## Re-exporting After Blueprint Changes

Just run the Python command again:
```python
import sys; sys.path.append("/your/project/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
```

## Configuration

Edit `Content/Python/blueprint_watcher.py` to customize:

```python
# Output directory (relative to project root)
OUTPUT_DIR = "ClaudeCodeDocs/Blueprints"

# Generate markdown files in addition to JSON
GENERATE_MARKDOWN = True

# Include detailed graph nodes (requires C++ plugin)
INCLUDE_GRAPH_NODES = True
```

## What Gets Exported

### JSON Files (Full Data)
- Complete graph structure with all nodes
- Node positions and connections
- Pin types and default values
- Variables with full metadata
- Functions with parameters
- Components with class info
- All asset dependencies

### Markdown Files (Human-Readable)
- Blueprint overview
- Component list
- Variable table
- Function signatures
- Graph summaries (node counts, key events)
- Dependency list

## System Requirements

- **UE5** (tested on 5.3, should work on 5.0+)
- **Python 3** (included with UE5)
- **Xcode** (Mac) or **Visual Studio** (Windows) for C++ compilation
- **Claude Code** (optional, for AI analysis)

## Support

For issues or questions:
- Check the `BLUEPRINT_EXPORTER_README.md` for detailed architecture info
- Verify all paths are absolute (not relative)
- Check UE5 Output Log for detailed error messages

## Credits

Built with:
- UE5 C++ Editor Plugin API
- UE5 Python Scripting Plugin
- Blueprint graph node extraction
- JSON serialization

Designed for use with Claude Code for AI-powered blueprint analysis.
