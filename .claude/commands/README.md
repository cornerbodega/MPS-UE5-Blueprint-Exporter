# Claude Code Commands

This directory contains slash commands for Claude Code to help users install and use the UE5 Blueprint Exporter.

## Available Commands

### `/setup-ue5-project`
**Complete guided installation for a UE5 project**

Automatically:
- Verifies your UE5 project exists
- Copies the BlueprintExporter plugin
- Copies Python scripts
- Generates your custom export command
- Provides next steps

**Usage:**
```
/setup-ue5-project
```

Then follow the prompts!

---

### `/install`
**Quick installation prompt**

Simple command that guides you through manual installation steps.

**Usage:**
```
/install
```

---

## How It Works

These commands leverage Claude Code's slash command system to provide:
- ✅ Interactive installation
- ✅ Automatic file copying
- ✅ Path validation
- ✅ Custom command generation
- ✅ Error handling

## For Developers

To add new commands:

1. Create a new `.md` file in this directory
2. Add frontmatter with `description`
3. Write the command prompt/instructions
4. Commands are automatically available in Claude Code

Example:
```markdown
---
description: Your command description
---

Command instructions here...
```
