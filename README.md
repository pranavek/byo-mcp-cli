# BYO-MCP-CLI (Bring Your Own CLI to MCP)

Transform any CLI tool into an MCP (Model Context Protocol) server instantly.

## What is this?
CLI-as-MCP is a lightweight bridge that converts command-line interface (CLI) tools into MCP servers, making them accessible to AI assistants like Claude Desktop or any MCP-enabled agent.

Instead of building custom MCP servers for every tool, simply wrap your existing CLI tools and expose them as MCP tools via a simple JSON configuration.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/byo-mcp-cli.git
   cd byo-mcp-cli
   ```

2. **Set up a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate 
   ```

3. **Install the package**:

   **Developer mode (Recommended)**: Any changes you make to the source code will take effect immediately.
   ```bash
   pip install -e .
   ```

   **Standard mode**: A clean install where code is copied to your environment.
   ```bash
   pip install .
   ```

   *Alternatively, if you use `uv`:*
   ```bash
   uv pip install -e .
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

## How to use with Claude Desktop

To use `byo-mcp-cli` with Claude Desktop, add it to your `claude_desktop_config.json`:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "my-cli-tools": {
      "command": "python",
      "args": [
        "-m",
        "byo_mcp.main",
        "--config",
        "C:/absolute/path/to/your/configs/gh-cli.toml"
      ]
    }
  }
}
```

*Note: Use absolute paths for both the python executable (if not in PATH) and the config file.*

## ⚠️ Security Considerations

This tool is designed to provide maximum flexibility by wrapping existing CLI tools. However, this comes with important security implications:

1. **Command Injection**: `byo-mcp-cli` uses `shell=True` to execute commands. Since arguments are provided by an LLM, there is a risk of command injection. For example, if a tool takes a filename as a parameter, an LLM could potentially pass `; rm -rf /` or similar malicious strings.
2. **System Access**: The MCP server runs with the same permissions as the user who started it. Any CLI tool you expose will be accessible to the LLM with those permissions.
3. **Local Trust**: This tool is intended for local use. Avoid exposing the MCP server over a public network.
4. **Configuration Review**: Always review the `command` templates in your TOML/JSON files. Ensure you are not exposing dangerous commands or tools that could be abused to gain unauthorized access to your system.

**Best Practices:**
- Only expose the minimum set of tools required.
- Use tools that have built-in safety checks where possible.
- Be cautious when using this with highly autonomous agents.
