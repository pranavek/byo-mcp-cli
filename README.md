# BYO-MCP-CLI (Bring Your Own CLI to MCP)

Transform any CLI tool into an MCP (Model Context Protocol) server instantly.

## What is this?
CLI-as-MCP is a lightweight bridge that converts command-line interface (CLI) tools into MCP servers, making them accessible to AI assistants like Claude Desktop or any MCP-enabled agent.

Instead of building custom MCP servers for every tool, simply wrap your existing CLI tools and expose them as MCP tools via a simple JSON configuration.

## Installation

```bash
pip install -e .
```

## Usage

Run the server with a configuration file:

```bash
byo-mcp --config configs/gh-cli.toml
```

## Configuration Format (TOML)

Create a TOML file (e.g., `configs/gh-cli.toml`):

```toml
name = "GitHub CLI"

[[tools]]
name = "gh_repo_view"
description = "View a GitHub repository"
command = "gh repo view {repo}"

[tools.parameters]
type = "object"
required = ["repo"]
[tools.parameters.properties.repo]
type = "string"
description = "Repository name (owner/repo)"

[[tools]]
name = "gh_issue_list"
description = "List issues in a repository"
command = "gh issue list --repo {repo} --limit {limit}"

[tools.parameters]
type = "object"
required = ["repo"]
[tools.parameters.properties.repo]
type = "string"
description = "Repository name"
[tools.parameters.properties.limit]
type = "integer"
description = "Max issues to list"
default = 10
```

## Benefits of TOML

- **Multi-line strings**: Perfect for complex CLI commands.
- **Comments**: Document your tools right in the config.
- **Readability**: Much cleaner syntax than JSON for configuration.
