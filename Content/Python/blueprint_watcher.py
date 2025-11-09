"""
UE5 Blueprint Watcher and Exporter
Monitors blueprints for changes and exports them to Claude Code-friendly format

Usage:
1. Place this file in your UE5 project's Content/Python directory
2. In UE5 Editor: Window > Developer Tools > Output Log
3. Run: py "Content/Python/blueprint_watcher.py"

Or set to auto-run in Project Settings > Python > Startup Scripts
"""

import unreal
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Output directory (relative to project root)
OUTPUT_DIR = "ClaudeCodeDocs/Blueprints"

# Refresh interval for file watcher (seconds)
REFRESH_INTERVAL = 5.0

# Whether to generate markdown files (in addition to JSON)
GENERATE_MARKDOWN = True

# Whether to include detailed node information (if C++ plugin available)
INCLUDE_GRAPH_NODES = True  # C++ plugin is now installed and compiled


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_project_root():
    """Get the project root directory"""
    return unreal.SystemLibrary.get_project_directory()


def ensure_output_dir():
    """Create output directory if it doesn't exist"""
    output_path = os.path.join(get_project_root(), OUTPUT_DIR)
    os.makedirs(output_path, exist_ok=True)
    return output_path


def get_output_path(blueprint_path: str, extension: str) -> str:
    """
    Convert blueprint path to output file path
    /Game/Characters/BP_Player -> ClaudeCodeDocs/Blueprints/Characters/BP_Player.json
    """
    output_root = ensure_output_dir()

    # Remove /Game/ prefix
    relative_path = blueprint_path.replace("/Game/", "")

    # Split into directory and filename
    parts = relative_path.split("/")
    filename = parts[-1] + extension
    subdirs = parts[:-1]

    # Create subdirectory structure
    subdir_path = os.path.join(output_root, *subdirs)
    os.makedirs(subdir_path, exist_ok=True)

    return os.path.join(subdir_path, filename)


# ============================================================================
# BLUEPRINT DATA EXTRACTION (Python API)
# ============================================================================

def extract_blueprint_metadata(blueprint: unreal.Blueprint) -> Dict[str, Any]:
    """
    Extract blueprint metadata using Python API
    Note: This doesn't include graph nodes (need C++ for that)
    """
    data = {
        "name": blueprint.get_name(),
        "path": blueprint.get_path_name(),
        "class_type": "Blueprint",
        "exported_at": datetime.now().isoformat(),
        "parent_class": None,
        "variables": [],
        "functions": [],
        "components": [],
        "interfaces": [],
        "metadata": {}
    }

    # Get parent class
    if hasattr(blueprint, 'parent_class') and blueprint.parent_class:
        data["parent_class"] = blueprint.parent_class.get_name()

    # Get generated class
    generated_class = blueprint.generated_class()
    if generated_class:
        data["generated_class"] = generated_class.get_name()

        # Extract class default object (CDO) for component information
        cdo = generated_class.get_default_object()
        if cdo:
            data["components"] = extract_components(cdo)

    # Get blueprint description/category if available
    if hasattr(blueprint, 'blueprint_description'):
        data["metadata"]["description"] = blueprint.blueprint_description

    # Get implemented interfaces
    if hasattr(blueprint, 'implemented_interfaces'):
        for interface in blueprint.implemented_interfaces:
            data["interfaces"].append(interface.get_name())

    return data


def extract_components(cdo) -> List[Dict[str, str]]:
    """Extract component information from blueprint CDO"""
    components = []

    # Try to get components (this works for Actor blueprints)
    if hasattr(cdo, 'get_components_by_class'):
        all_components = cdo.get_components_by_class(unreal.ActorComponent)
        for comp in all_components:
            components.append({
                "name": comp.get_name(),
                "class": comp.get_class().get_name(),
                "type": "ActorComponent"
            })

    return components


# ============================================================================
# BLUEPRINT DATA EXTRACTION (C++ Plugin - Optional)
# ============================================================================

def extract_blueprint_data_full(blueprint: unreal.Blueprint) -> Dict[str, Any]:
    """
    Extract full blueprint data including graph nodes
    Requires BlueprintExporter C++ plugin
    """
    if INCLUDE_GRAPH_NODES:
        try:
            # Call the C++ plugin function
            json_string = unreal.BlueprintExporterLibrary.extract_blueprint_data(blueprint)
            return json.loads(json_string)
        except AttributeError as e:
            unreal.log_warning(f"BlueprintExporter plugin not found: {e}")
            unreal.log_warning("Falling back to metadata-only export")
            return extract_blueprint_metadata(blueprint)
        except Exception as e:
            unreal.log_error(f"Error extracting blueprint data: {e}")
            return extract_blueprint_metadata(blueprint)
    else:
        return extract_blueprint_metadata(blueprint)


# ============================================================================
# MARKDOWN GENERATION
# ============================================================================

def generate_markdown(data: Dict[str, Any]) -> str:
    """Generate human-readable Markdown from blueprint data"""

    exported_time = data.get('exported_at', datetime.now().isoformat())

    md = f"""# {data['name']}

**Type:** {data.get('class_type', 'Blueprint')}
**Path:** `{data.get('path', 'Unknown')}`
**Parent Class:** {data.get('parent_class', 'None')}
**Exported:** {exported_time}

"""

    # Description
    if data.get('metadata', {}).get('description'):
        md += f"## Description\n\n{data['metadata']['description']}\n\n"

    # Components
    if data['components']:
        md += "## Components\n\n"
        for comp in data['components']:
            md += f"- **{comp['name']}** ({comp['class']})\n"
        md += "\n"

    # Variables
    if data['variables']:
        md += "## Variables\n\n"
        md += "| Name | Type | Category | Exposed |\n"
        md += "|------|------|----------|----------|\n"
        for var in data['variables']:
            md += f"| {var.get('name', 'N/A')} | {var.get('type', 'N/A')} | {var.get('category', 'N/A')} | {var.get('is_exposed', 'N/A')} |\n"
        md += "\n"

    # Functions
    if data['functions']:
        md += "## Functions\n\n"
        for func in data['functions']:
            params = ", ".join([f"{p['name']}: {p['type']}" for p in func.get('parameters', [])])
            md += f"### {func['name']}({params})\n\n"
            if func.get('description'):
                md += f"{func['description']}\n\n"
        md += "\n"

    # Interfaces
    if data.get('interfaces'):
        md += "## Implemented Interfaces\n\n"
        for interface in data['interfaces']:
            md += f"- {interface}\n"
        md += "\n"

    # Graphs (from C++ plugin)
    if data.get('graphs'):
        md += "## Graphs\n\n"
        for graph in data['graphs']:
            graph_name = graph.get('name', 'Unknown')
            nodes = graph.get('nodes', [])
            md += f"### {graph_name}\n\n"
            md += f"**Total Nodes:** {len(nodes)}\n\n"

            # Show key nodes (events, functions)
            event_nodes = [n for n in nodes if 'Event' in n.get('type', '')]
            if event_nodes:
                md += "**Events:**\n"
                for node in event_nodes[:5]:  # Limit to first 5
                    md += f"- {node.get('title', 'Unknown')}\n"
                md += "\n"
        md += "\n"

    # Dependencies
    if data.get('dependencies'):
        md += "## Dependencies\n\n"
        for dep in data['dependencies'][:10]:  # Limit to first 10
            md += f"- `{dep}`\n"
        md += "\n"

    return md


# ============================================================================
# EXPORT FUNCTIONS
# ============================================================================

def export_blueprint(blueprint: unreal.Blueprint) -> bool:
    """Export a single blueprint to JSON and Markdown"""
    try:
        blueprint_path = blueprint.get_path_name()

        # Extract data
        data = extract_blueprint_data_full(blueprint)

        # Save JSON
        json_path = get_output_path(blueprint_path, ".json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        unreal.log(f"Exported JSON: {json_path}")

        # Generate and save Markdown
        if GENERATE_MARKDOWN:
            md_content = generate_markdown(data)
            md_path = get_output_path(blueprint_path, ".md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            unreal.log(f"Exported Markdown: {md_path}")

        return True

    except Exception as e:
        unreal.log_error(f"Failed to export blueprint {blueprint.get_name()}: {str(e)}")
        return False


def export_all_blueprints() -> int:
    """Export all blueprints in the project"""
    unreal.log("Starting blueprint export...")

    # Get asset registry
    asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()

    # Get all blueprint assets
    filter = unreal.ARFilter(
        class_names=["Blueprint"],
        recursive_paths=True
    )

    assets = asset_registry.get_assets(filter)

    exported_count = 0
    for asset_data in assets:
        asset = asset_data.get_asset()
        if isinstance(asset, unreal.Blueprint):
            if export_blueprint(asset):
                exported_count += 1

    # Generate index
    generate_index()

    unreal.log(f"Export complete! Exported {exported_count} blueprints to {OUTPUT_DIR}")
    return exported_count


def generate_index():
    """Generate an index file listing all exported blueprints"""
    output_root = ensure_output_dir()
    index_path = os.path.join(output_root, "index.md")

    # Collect all exported markdown files
    blueprint_files = []
    for root, dirs, files in os.walk(output_root):
        for file in files:
            if file.endswith('.md') and file != 'index.md':
                rel_path = os.path.relpath(os.path.join(root, file), output_root)
                blueprint_files.append(rel_path)

    blueprint_files.sort()

    # Generate index content
    content = f"""# Blueprint Index

**Total Blueprints:** {len(blueprint_files)}
**Last Updated:** {datetime.now().isoformat()}

## All Blueprints

"""

    current_category = None
    for bp_file in blueprint_files:
        # Extract category from path
        parts = bp_file.split(os.sep)
        if len(parts) > 1:
            category = parts[0]
            if category != current_category:
                current_category = category
                content += f"\n### {category}\n\n"

        bp_name = parts[-1].replace('.md', '')
        content += f"- [{bp_name}]({bp_file})\n"

    # Write index
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(content)

    unreal.log(f"Generated index: {index_path}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    unreal.log("=" * 60)
    unreal.log("UE5 Blueprint Exporter for Claude Code")
    unreal.log("=" * 60)

    # Export all blueprints
    export_all_blueprints()

    unreal.log("\nExport complete! You can now use Claude Code to analyze your blueprints.")
    unreal.log(f"Documentation location: {os.path.join(get_project_root(), OUTPUT_DIR)}")
    unreal.log("\nTo re-export, run this script again or implement the watcher (see below).")


# ============================================================================
# FILE WATCHER (Optional - for auto-refresh)
# ============================================================================

def start_watcher():
    """
    Start watching for blueprint changes
    Note: This requires running in a separate thread or using UE5's tick system
    """
    unreal.log_warning("Auto-refresh watcher not yet implemented")
    unreal.log_warning("For now, manually re-run this script to refresh exports")

    # TODO: Implement using unreal.register_slate_post_tick_callback
    # or by creating an Editor Utility Widget with a timer


# Run main function when script is executed
if __name__ == "__main__":
    main()
