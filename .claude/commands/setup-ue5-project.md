---
description: Install Blueprint Exporter to a UE5 project
---

You are an expert UE5 Blueprint Exporter installation assistant.

## Steps:

1. Ask the user for their UE5 project absolute path
2. Verify the .uproject file exists
3. Copy plugin files: `Plugins/BlueprintExporter` → `[ProjectPath]/Plugins/BlueprintExporter`
4. Copy Python scripts: `Content/Python/*.py` → `[ProjectPath]/Content/Python/`
5. Copy test script: `Content/Python/test_export.py` → `[ProjectPath]/Content/Python/`
6. **Enable the plugin** in `[ProjectPath]/[ProjectName].uproject` by adding to the "Plugins" array:
   ```json
   {
     "Name": "BlueprintExporter",
     "Enabled": true
   }
   ```
   If the "Plugins" array doesn't exist, create it.
7. Create `[ProjectPath]/RUN_EXPORT.txt` with this exact format:
   ```
   import sys; sys.path.append("[ProjectPath]/Content/Python"); import blueprint_watcher; blueprint_watcher.main()
   ```
   Replace [ProjectPath] with the actual project path.
8. Tell the user to restart UE5 to compile the plugin, then run the command from RUN_EXPORT.txt in UE5's Python console

## Final Output:

Just say:
```
✅ Installed! Next steps:
1. Restart Unreal Engine (plugin will compile on startup)
2. Once loaded, copy the command from:
   [ProjectPath]/RUN_EXPORT.txt
```
