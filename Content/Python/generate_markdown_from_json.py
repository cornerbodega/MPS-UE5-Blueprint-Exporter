"""
Generate Markdown files from existing JSON exports
Run this to create markdown files from the C++ plugin JSON exports
"""

import json
import os
from pathlib import Path
from datetime import datetime

# Configuration
PROJECT_ROOT = "/Users/fromastermarv/Documents/Unreal Projects/exporter_fps_mvp"
JSON_DIR = os.path.join(PROJECT_ROOT, "ClaudeCodeDocs/Blueprints")


def generate_markdown(data):
    """Generate human-readable Markdown from blueprint data"""

    exported_time = data.get('exported_at', datetime.now().isoformat())

    md = f"""# {data.get('name', 'Unknown')}

**Type:** {data.get('class_type', 'Blueprint')}
**Path:** `{data.get('path', 'Unknown')}`
**Parent Class:** {data.get('parent_class', 'None')}
**Generated Class:** {data.get('generated_class', 'None')}
**Exported:** {exported_time}

"""

    # Components
    components = data.get('components', [])
    if components:
        md += "## Components\n\n"
        for comp in components:
            md += f"- **{comp.get('name', 'Unknown')}** ({comp.get('class', 'Unknown')})\n"
        md += "\n"

    # Variables
    variables = data.get('variables', [])
    if variables:
        md += "## Variables\n\n"
        md += "| Name | Type | Category | Default |\n"
        md += "|------|------|----------|----------|\n"
        for var in variables:
            name = var.get('name', 'N/A')
            var_type = var.get('type', 'N/A')
            category = var.get('category', 'N/A')
            default = var.get('default_value', '')
            md += f"| {name} | {var_type} | {category} | {default} |\n"
        md += "\n"

    # Functions
    functions = data.get('functions', [])
    if functions:
        md += "## Functions\n\n"
        for func in functions:
            params = func.get('parameters', [])
            param_str = ", ".join([f"{p.get('name', '')}: {p.get('type', '')}" for p in params])
            md += f"### {func.get('name', 'Unknown')}({param_str})\n\n"
        md += "\n"

    # Graphs (from C++ plugin)
    graphs = data.get('graphs', [])
    if graphs:
        md += "## Graphs\n\n"
        for graph in graphs:
            graph_name = graph.get('name', 'Unknown')
            nodes = graph.get('nodes', [])
            md += f"### {graph_name}\n\n"
            md += f"**Total Nodes:** {len(nodes)}\n\n"

            # Show key nodes (events)
            event_nodes = [n for n in nodes if 'Event' in n.get('type', '')]
            if event_nodes:
                md += "**Event Nodes:**\n"
                for node in event_nodes[:10]:
                    title = node.get('title', 'Unknown').replace('\n', ' - ')
                    md += f"- {title}\n"
                md += "\n"

            # Show function calls
            call_nodes = [n for n in nodes if 'CallFunction' in n.get('type', '')]
            if call_nodes and len(call_nodes) <= 20:
                md += "**Function Calls:**\n"
                for node in call_nodes[:20]:
                    title = node.get('title', 'Unknown').replace('\n', ' - ')
                    md += f"- {title}\n"
                md += "\n"
        md += "\n"

    # Dependencies
    dependencies = data.get('dependencies', [])
    if dependencies:
        md += "## Dependencies\n\n"
        for dep in dependencies[:15]:
            md += f"- `{dep}`\n"
        if len(dependencies) > 15:
            md += f"\n_...and {len(dependencies) - 15} more_\n"
        md += "\n"

    return md


def process_json_files():
    """Process all JSON files and create markdown"""

    json_files = []
    for root, dirs, files in os.walk(JSON_DIR):
        for file in files:
            if file.endswith('.json') and file != 'index.json':
                json_files.append(os.path.join(root, file))

    print(f"Found {len(json_files)} JSON files")

    success_count = 0
    for json_path in json_files:
        try:
            # Read JSON
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Generate markdown
            md_content = generate_markdown(data)

            # Write markdown
            md_path = json_path.replace('.json', '.md')
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_content)

            print(f"✓ Created: {os.path.basename(md_path)}")
            success_count += 1

        except Exception as e:
            print(f"✗ Failed: {os.path.basename(json_path)} - {e}")

    print(f"\n✅ Successfully created {success_count} markdown files!")


if __name__ == "__main__":
    process_json_files()
