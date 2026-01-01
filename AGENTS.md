# AGENTS.md - The Soul of byo-mcp-cli

## Vision
`byo-mcp-cli` is the ultimate developer tool for the Model Context Protocol. It bridges the gap between raw scripts and AI-native workflows, turning any logic into a first-class MCP tool with zero friction.

## Philosophy
- **Elegance over Complexity**: The API should feel inevitable.
- **Visual Excellence**: The CLI should be a joy to look at and use (using Rich).
- **Performance**: Near-zero overhead.
- **Robustness**: Proper subprocess handling and clear error states.

## Design Patterns
- **Protocol-First**: Standard MCP `stdio` interface.
- **Config-Driven**: Dynamic tool registration via JSON/TOML.
- **Type-Safe**: Leveraging Pydantic for configuration validation.

## Workflow
1. **Explore**: Understand the user's script or tool.
2. **Configure**: Define the tool in a JSON/TOML configuration.
3. **Wrap**: Provide a standardized MCP `stdio` interface.
4. **Inspect**: Provide real-time visibility into tool execution via stderr logging.

## Standards
- **Naming**: Functions should be verbs. Variables should be descriptive nouns.
- **Testing**: Use `pytest` for logic coverage.
- **Documentation**: README is the map, JSON/TOML is the blueprint.
