# OpenClaw Workspace Monorepo

A unified workspace for OpenClaw agent operations, including memory systems, skills, and tooling.

## Structure

```
workspace/
├── memory-agent/       # Privacy-first local cognitive memory agent
├── SyntheticMemories/  # Human-inspired memory architecture (episodic, semantic, procedural)
├── skills/             # Skill packages for agent capabilities
├── scripts/            # Utility scripts for bootstrapping and packaging
├── memory/             # Agent memory and daily logs
├── docs/               # Documentation
└── CI_RUNS/            # CI/CD execution logs
```

## Quick Start

### 1. Bootstrap the environment

```bash
./scripts/bootstrap.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up memory-agent in development mode

### 2. Run memory-agent CLI

```bash
# After bootstrapping, the 'memory' command is available
memory --help
```

### 3. Run tests

```bash
cd memory-agent
pytest
```

## Projects

### memory-agent
Privacy-first local cognitive memory agent with:
- Local RAG (Retrieval-Augmented Generation)
- Sentence embeddings via local models
- CLI interface for memory operations
- No cloud dependencies

See [memory-agent/README.md](memory-agent/README.md) for details.

### SyntheticMemories
Biologically-inspired memory system with:
- **Episodic memory**: Specific events and experiences
- **Semantic memory**: Facts and concepts  
- **Procedural memory**: Skills and how-to knowledge
- **Memory links**: Associative connections

See [SyntheticMemories/README.md](SyntheticMemories/README.md) for details.

### Skills
Modular capabilities for the agent:
- `advanced-memory`: Enhanced memory operations
- `galaxyrvr`: Rover control interface
- `health-check`: System health monitoring
- `homeassistant`: Home automation integration
- `plex`: Media server integration
- `unifi`: Network management

## Development

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for development guidelines.

See [docs/DEPLOY.md](docs/DEPLOY.md) for deployment instructions.

## Agent Configuration

Key files for agent operation:
- `AGENTS.md` - Workspace guidelines and best practices
- `SOUL.md` - Agent identity and personality
- `USER.md` - User context and preferences
- `MEMORY.md` - Long-term curated memories
- `TOOLS.md` - Local tool configurations

## License

MIT - See individual project directories for specific licensing.
