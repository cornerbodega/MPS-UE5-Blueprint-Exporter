# Blueprint Exporter for Claude Code - Setup Guide

This MVP allows you to export UE5 blueprint data to Claude Code-friendly documentation format.

## Project Structure

```
exporter_fps_mvp/
├── Plugins/
│   └── BlueprintExporter/          # C++ Plugin (Full blueprint graph access)
│       ├── BlueprintExporter.uplugin
│       ├── Source/
│       │   └── BlueprintExporter/
│       │       ├── BlueprintExporter.Build.cs
│       │       ├── Public/
│       │       │   └── BlueprintExporter.h
│       │       └── Private/
│       │           └── BlueprintExporter.cpp
│       └── Resources/
├── Content/
│   └── Python/
│       └── blueprint_watcher.py     # Python orchestration script
└── ClaudeCodeDocs/                  # Output directory (auto-generated)
    └── Blueprints/
        ├── index.md
        ├── Characters/
        │   ├── BP_PlayerCharacter.md
        │   └── BP_PlayerCharacter.json
        └── ...
```

## Installation Steps

### Step 1: Enable Python in UE5

1. Open UE5 Editor with your project
2. Go to `Edit > Plugins`
3. Search for "Python Editor Script Plugin"
4. Enable the plugin and restart the editor

### Step 2: Compile the C++ Plugin

#### Option A: Using UE5 Editor (Recommended)
1. Right-click on `exporter_fps_mvp.uproject`
2. Select "Generate Visual Studio project files" (or Xcode on Mac)
3. Open the generated project file
4. Build the project in Development Editor configuration
5. The plugin will be compiled automatically

#### Option B: Using Command Line (Mac)
```bash
cd "/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp"

# Generate project files
/Users/Shared/Epic\ Games/UE_5.X/Engine/Build/BatchFiles/Mac/GenerateProjectFiles.sh -project="exporter_fps_mvp.uproject"

# Build the plugin
/Users/Shared/Epic\ Games/UE_5.X/Engine/Build/BatchFiles/Mac/Build.sh exporter_fps_mvpEditor Mac Development -project="exporter_fps_mvp.uproject"
```

Replace `5.X` with your actual UE5 version number.

### Step 3: Verify Plugin Loaded

1. Open UE5 Editor
2. Go to `Edit > Plugins`
3. Search for "Blueprint Exporter"
4. It should show as enabled (blue checkmark)

## Usage

### Method 1: Using Python Script (Quick Start)

1. In UE5 Editor, open the Output Log: `Window > Developer Tools > Output Log`

2. Run the Python script:
```python
py "/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp/Content/Python/blueprint_watcher.py"
```

Or use a relative path:
```python
import unreal
unreal.EditorUtil.get_editor_subsystem(unreal.EditorUtilitySubsystem).run_script("Content/Python/blueprint_watcher.py")
```

3. The script will export all blueprints to `ClaudeCodeDocs/Blueprints/`

### Method 2: Using Blueprint/Python in Editor

Create an Editor Utility Widget with a button:

```python
import unreal
import sys
sys.path.append("/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp/Content/Python")

import blueprint_watcher
blueprint_watcher.export_all_blueprints()
```

### Method 3: Using C++ Plugin Directly (Advanced)

In any blueprint or C++ code:

```cpp
// Get all blueprints
TArray<UBlueprint*> Blueprints = UBlueprintExporterLibrary::GetAllProjectBlueprints();

// Export a single blueprint
FString OutputPath = "/path/to/output.json";
UBlueprintExporterLibrary::ExportBlueprintToFile(Blueprint, OutputPath);

// Export all blueprints to a directory
FString OutputDir = "/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp/ClaudeCodeDocs/Blueprints";
int32 Count = UBlueprintExporterLibrary::ExportAllBlueprints(OutputDir);
```

## Output Format

### JSON Format
Each blueprint is exported to a JSON file with complete structure:

```json
{
  "name": "BP_PlayerCharacter",
  "path": "/Game/Characters/BP_PlayerCharacter",
  "parent_class": "Character",
  "graphs": [...],
  "variables": [...],
  "functions": [...],
  "components": [...],
  "dependencies": [...]
}
```

### Markdown Format
Human-readable documentation:

```markdown
# BP_PlayerCharacter

**Type:** Blueprint Actor
**Parent Class:** Character

## Components
- CameraComponent (UCameraComponent)
- SpringArmComponent (USpringArmComponent)

## Variables
| Name | Type | Default | Category |
|------|------|---------|----------|
| Health | float | 100.0 | Stats |
...
```

## Using with Claude Code

Once blueprints are exported:

1. Open Claude Code in your project directory:
```bash
cd "/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp"
claude-code
```

2. Ask questions about your blueprints:
```
> How does BP_PlayerCharacter handle taking damage?

> What blueprints depend on BP_Weapon?

> Show me all event graphs that use the Sprint function

> List all blueprints that have a Health variable
```

Claude Code will read the exported Markdown/JSON files and answer your questions!

## Auto-Refresh (Future Enhancement)

To automatically export blueprints when they change:

1. Edit `Content/Python/blueprint_watcher.py`
2. Set `INCLUDE_GRAPH_NODES = True` (after C++ plugin is working)
3. Use UE5's startup scripts to run the watcher on editor launch

Add to `Config/DefaultEngine.ini`:
```ini
[/Script/PythonScriptPlugin.PythonScriptPluginSettings]
+StartupScripts=/Game/Python/blueprint_watcher.py
```

## Troubleshooting

### Plugin Won't Compile
- Verify UE5 is installed correctly
- Check that you have the correct UE5 version
- Make sure you selected "Development Editor" configuration
- On Mac, install Xcode Command Line Tools: `xcode-select --install`

### Python Script Errors
- Enable Python plugin first
- Check Output Log for detailed error messages
- Verify file paths are correct

### No Blueprints Exported
- Check that you have blueprints in your project
- Verify the output directory is writable
- Check Output Log for errors

### C++ Plugin Functions Not Available in Python
- The plugin must be compiled successfully first
- Check that the plugin is enabled in Editor
- Try restarting the editor

## Next Steps

1. ✅ Install and compile the plugin
2. ✅ Run the Python export script
3. ✅ Verify output in `ClaudeCodeDocs/Blueprints/`
4. ✅ Test with Claude Code
5. [ ] Enhance export with more metadata
6. [ ] Implement auto-refresh watcher
7. [ ] Create Editor Utility Widget for easy access

## Configuration

Edit `Content/Python/blueprint_watcher.py` to customize:

```python
# Output directory
OUTPUT_DIR = "ClaudeCodeDocs/Blueprints"

# Generate markdown files
GENERATE_MARKDOWN = True

# Include detailed graph nodes (requires C++ plugin)
INCLUDE_GRAPH_NODES = True
```

## Support

For issues or questions:
- Check UE5 Output Log for error messages
- Verify all paths are correct
- Make sure Python and C++ plugins are both enabled
- Check that blueprints exist in your project

## Architecture Reference

See `UE5_BLUEPRINT_ANALYZER_MVP.md` in the main project directory for detailed architecture and design decisions.
