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

def generate_detailed_node_graph(nodes: List[Dict[str, Any]]) -> str:
    """Generate detailed node-by-node breakdown showing execution and data flow"""
    md = ""

    # Build connection map for easier lookup
    connection_map = {}
    for node in nodes:
        node_id = node.get('id', '')
        connections = node.get('connections', [])
        connection_map[node_id] = connections

    # Categorize nodes by type
    event_nodes = [n for n in nodes if 'Event' in n.get('type', '')]
    function_nodes = [n for n in nodes if 'CallFunction' in n.get('type', '')]
    variable_nodes = [n for n in nodes if 'Variable' in n.get('type', '')]
    other_nodes = [n for n in nodes if n not in event_nodes + function_nodes + variable_nodes]

    # Show execution flow starting from events
    if event_nodes:
        md += "#### Execution Flow\n\n"
        for event_node in event_nodes:
            md += generate_execution_chain(event_node, nodes, connection_map)
        md += "\n"

    # Show all function calls with details
    if function_nodes:
        md += "#### Function Calls\n\n"
        for func_node in function_nodes:
            md += generate_function_call_detail(func_node)
        md += "\n"

    # Show variable usage
    if variable_nodes:
        md += "#### Variables Used\n\n"
        for var_node in variable_nodes:
            title = var_node.get('title', 'Unknown').replace('\n', ' ')
            node_type = var_node.get('type', 'Unknown')
            md += f"- **{title}** ({node_type})\n"
        md += "\n"

    # Show complete node details
    md += "#### All Nodes (Detailed)\n\n"
    for idx, node in enumerate(nodes, 1):
        md += generate_node_detail(node, idx)

    return md


def generate_execution_chain(start_node: Dict[str, Any], all_nodes: List[Dict[str, Any]], connection_map: Dict) -> str:
    """Trace execution flow from an event node"""
    md = f"**{start_node.get('title', 'Unknown Event')}**\n\n"

    # Build node lookup
    node_lookup = {n.get('id'): n for n in all_nodes}

    # Trace execution chain
    visited = set()
    current_node = start_node
    step = 1

    while current_node and current_node.get('id') not in visited:
        node_id = current_node.get('id')
        visited.add(node_id)

        # Show current node
        title = current_node.get('title', 'Unknown').replace('\n', ' → ')
        node_type = current_node.get('type', 'Unknown')
        md += f"{step}. **{title}** `[{node_type}]`\n"

        # Show input pins with values
        pins = current_node.get('pins', [])
        input_pins = [p for p in pins if p.get('direction') == 'input' and p.get('type') != 'exec']
        if input_pins:
            md += "   - Inputs:\n"
            for pin in input_pins:
                pin_name = pin.get('display_name', pin.get('name', 'Unknown'))
                pin_type = pin.get('type', 'Unknown')
                default_val = pin.get('default_value', '')
                if default_val:
                    md += f"     - {pin_name}: `{pin_type}` = `{default_val}`\n"
                else:
                    md += f"     - {pin_name}: `{pin_type}`\n"

        # Show output pins
        output_pins = [p for p in pins if p.get('direction') == 'output' and p.get('type') != 'exec']
        if output_pins:
            md += "   - Outputs:\n"
            for pin in output_pins:
                pin_name = pin.get('display_name', pin.get('name', 'Unknown'))
                pin_type = pin.get('type', 'Unknown')
                md += f"     - {pin_name}: `{pin_type}`\n"

        md += "\n"

        # Find next node in execution chain (follow exec output pins)
        connections = current_node.get('connections', [])
        next_node = None
        if connections:
            # Try to find the next connected node
            for conn_id in connections:
                if conn_id in node_lookup:
                    next_node = node_lookup[conn_id]
                    break

        current_node = next_node
        step += 1

        # Safety limit
        if step > 50:
            md += "   _(Execution chain continues...)_\n\n"
            break

    md += "\n"
    return md


def generate_function_call_detail(node: Dict[str, Any]) -> str:
    """Generate detailed breakdown of a function call node"""
    title = node.get('title', 'Unknown Function').replace('\n', ' → ')
    category = node.get('category', '')

    md = f"- **{title}**"
    if category:
        md += f" _{category}_"
    md += "\n"

    # Show pins
    pins = node.get('pins', [])
    input_pins = [p for p in pins if p.get('direction') == 'input' and p.get('type') != 'exec']
    output_pins = [p for p in pins if p.get('direction') == 'output' and p.get('type') != 'exec']

    if input_pins:
        md += "  - Parameters:\n"
        for pin in input_pins:
            pin_name = pin.get('display_name', pin.get('name', 'Unknown'))
            pin_type = pin.get('type', 'Unknown')
            default_val = pin.get('default_value', '')
            if default_val:
                md += f"    - `{pin_name}`: {pin_type} = `{default_val}`\n"
            else:
                md += f"    - `{pin_name}`: {pin_type}\n"

    if output_pins:
        md += "  - Returns:\n"
        for pin in output_pins:
            pin_name = pin.get('display_name', pin.get('name', 'Unknown'))
            pin_type = pin.get('type', 'Unknown')
            md += f"    - `{pin_name}`: {pin_type}\n"

    md += "\n"
    return md


def generate_node_detail(node: Dict[str, Any], index: int) -> str:
    """Generate complete detail for a single node"""
    node_id = node.get('id', 'Unknown')
    title = node.get('title', 'Unknown').replace('\n', ' → ')
    node_type = node.get('type', 'Unknown')
    category = node.get('category', '')
    position = node.get('position', {})

    md = f"**Node {index}: {title}**\n"
    md += f"- Type: `{node_type}`\n"
    if category:
        md += f"- Category: `{category}`\n"
    md += f"- ID: `{node_id}`\n"
    md += f"- Position: ({position.get('x', 0)}, {position.get('y', 0)})\n"

    # Show all pins
    pins = node.get('pins', [])
    if pins:
        md += "- Pins:\n"
        for pin in pins:
            pin_name = pin.get('display_name', pin.get('name', 'Unknown'))
            pin_dir = pin.get('direction', 'unknown')
            pin_type = pin.get('type', 'Unknown')
            default_val = pin.get('default_value', '')

            pin_str = f"  - [{pin_dir}] `{pin_name}`: {pin_type}"
            if default_val:
                pin_str += f" = `{default_val}`"
            md += pin_str + "\n"

    # Show connections
    connections = node.get('connections', [])
    if connections:
        md += f"- Connected to: {', '.join([f'`{c}`' for c in connections])}\n"

    md += "\n"
    return md


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

    # Graphs (from C++ plugin) - DETAILED NODE-BY-NODE LOGIC
    if data.get('graphs'):
        md += "## Graphs & Node Logic\n\n"
        for graph in data['graphs']:
            graph_name = graph.get('name', 'Unknown')
            nodes = graph.get('nodes', [])
            md += f"### {graph_name}\n\n"
            md += f"**Total Nodes:** {len(nodes)}\n\n"

            if nodes:
                md += generate_detailed_node_graph(nodes)
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
    count = export_all_blueprints()

    # Get full path for Claude Code
    project_root = get_project_root()
    full_docs_path = os.path.join(project_root, OUTPUT_DIR)

    unreal.log("\n" + "=" * 60)
    unreal.log(f"✓ Exported {count} blueprints")
    unreal.log(f"✓ Location: {OUTPUT_DIR}/")
    unreal.log("=" * 60)
    unreal.log("\n📍 FOR CLAUDE CODE:")
    unreal.log(f"\n   The blueprint documentation is located at:")
    unreal.log(f"   {full_docs_path}")
    unreal.log("\n   Copy this message to Claude Code:")
    unreal.log(f"   \"My UE5 blueprint docs are in: {full_docs_path}\"")
    unreal.log("\n" + "=" * 60)
    unreal.log("\nNEXT: Ask Claude Code about your blueprints:")
    unreal.log("\nExample questions:")
    unreal.log("  • How does movement input work in the character blueprint?")
    unreal.log("  • Show me the node-by-node logic for jumping")
    unreal.log("  • What components are in my blueprints?")
    unreal.log("  • Explain the execution flow for [specific event]")
    unreal.log("\n" + "=" * 60)


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
