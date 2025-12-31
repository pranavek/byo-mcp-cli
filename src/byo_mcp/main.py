import asyncio
import json
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

import click
from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ErrorData,
    JSONRPCResponse,
    TextContent,
    Tool,
)
from pydantic import BaseModel
from rich.console import Console
from rich.panel import Panel
from rich.logging import RichHandler
import logging

# Setup rich logging to stderr
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(stderr=True))]
)
log = logging.getLogger("byo-mcp")
console = Console(stderr=True)

class CLIConfig(BaseModel):
    name: str
    tools: List[Dict[str, Any]]

def run_cli_command(command_template: str, arguments: Dict[str, Any]) -> str:
    """Execute a CLI command with interpolated arguments."""
    try:
        # Interpolate arguments into the command template
        # We use .format() which is safe if the user controls the config.
        # However, we should be careful with shell injection if arguments come from untrusted sources.
        # For MCP, the LLM provides arguments.
        command = command_template.format(**arguments)
        
        log.info(f"Executing: [bold cyan]{command}[/bold cyan]")
        
        process = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60 # 1 minute timeout for CLI tools
        )
        
        output = []
        if process.stdout:
            output.append(process.stdout.strip())
        if process.stderr:
            output.append(f"Standard Error:\n{process.stderr.strip()}")
            
        if not output:
            if process.returncode == 0:
                return "Command executed successfully (no output)."
            else:
                return f"Command failed with return code {process.returncode}."
            
        return "\n".join(output)
    except KeyError as e:
        return f"Error: Missing required argument {e} for command template."
    except Exception as e:
        log.error(f"Execution error: {e}")
        return f"Error executing command: {str(e)}"

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib

async def serve(config_path: str):
    """Run the MCP server with the given configuration."""
    # Load environment variables from .env if it exists
    load_dotenv()
    
    if not os.path.exists(config_path):
        console.print(f"[red]Error: Config file not found at {config_path}[/red]")
        sys.exit(1)
        
    try:
        with open(config_path, 'rb') as f:
            if config_path.endswith('.toml'):
                config_data = tomllib.load(f)
            else:
                # Fallback to JSON
                config_data = json.loads(f.read().decode('utf-8'))
    except Exception as e:
        console.print(f"[red]Error parsing config ({config_path}): {e}[/red]")
        sys.exit(1)

    server_name = config_data.get("name", "byo-mcp-server")
    server = Server(server_name)
    
    tools_config = config_data.get("tools", [])
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        return [
            Tool(
                name=t["name"],
                description=t["description"],
                inputSchema=t["parameters"]
            )
            for t in tools_config
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        tool_cfg = next((t for t in tools_config if t["name"] == name), None)
        if not tool_cfg:
            log.error(f"Tool not found: {name}")
            return [TextContent(type="text", text=f"Error: Tool {name} not found.")]
            
        command_template = tool_cfg["command"]
        result = run_cli_command(command_template, arguments)
        
        return [TextContent(type="text", text=result)]

    console.print(Panel.fit(
        f"[bold blue]BYO-MCP-CLI[/bold blue]\n"
        f"Server: [green]{server_name}[/green]\n"
        f"Tools Loaded: [yellow]{len(tools_config)}[/yellow]\n"
        f"Config: [dim]{config_path}[/dim]",
        title="Server Status",
        border_style="blue"
    ))
    
    async with stdio_server() as (read_stream, write_stream):
        log.info("Server listening on stdio...")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

@click.command()
@click.option("--config", required=True, help="Path to the TOML or JSON configuration file")
@click.option("--env", help="Path to a .env file", default=".env")
def main(config, env):
    """Bring Your Own CLI to MCP.
    
    Transform any CLI tool into an MCP server by providing a TOML or JSON configuration.
    """
    if os.path.exists(env):
        load_dotenv(env)
        log.info(f"Loaded environment variables from {env}")
        
    try:
        asyncio.run(serve(config))
    except KeyboardInterrupt:
        log.info("Server stopped by user.")
    except Exception as e:
        log.critical(f"Unhandled exception: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
