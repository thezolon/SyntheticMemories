# Deployment Guide

This guide covers deploying the OpenClaw workspace monorepo in various environments.

## Prerequisites

- Python 3.10 or higher
- Git
- 4GB+ RAM (for memory-agent embedding models)
- Linux, macOS, or WSL2

## Local Development Deployment

### 1. Clone and Bootstrap

```bash
git clone <repository-url>
cd workspace
./scripts/bootstrap.sh
```

The bootstrap script will:
- Create a Python virtual environment
- Install all project dependencies
- Install memory-agent in editable mode
- Verify the installation with basic tests

### 2. Activate Environment

```bash
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Verify Installation

```bash
# Check memory-agent CLI
memory --version
memory --help

# Run tests
cd memory-agent
pytest
```

## Production Deployment

### Option 1: Systemd Service (Linux)

Create `/etc/systemd/system/memory-agent.service`:

```ini
[Unit]
Description=Memory Agent Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/workspace
Environment="PATH=/path/to/workspace/venv/bin"
ExecStart=/path/to/workspace/venv/bin/memory serve
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable memory-agent
sudo systemctl start memory-agent
sudo systemctl status memory-agent
```

### Option 2: Docker Deployment

Create `Dockerfile` in workspace root:

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -e ./memory-agent

EXPOSE 8000

CMD ["memory", "serve"]
```

Build and run:
```bash
docker build -t memory-agent .
docker run -d -p 8000:8000 -v $(pwd)/memory:/app/memory memory-agent
```

### Option 3: Manual Installation

```bash
# Install to system Python (not recommended)
pip install ./memory-agent

# Or install from package
cd memory-agent
python -m build
pip install dist/memory_agent-*.whl
```

## Configuration

### Environment Variables

Create `.env` in workspace root:

```bash
# Memory agent settings
MEMORY_AGENT_DATA_DIR=/path/to/data
MEMORY_AGENT_MODEL=all-MiniLM-L6-v2

# Optional: API keys for extended features
OPENAI_API_KEY=sk-...
```

### Data Directories

Default data locations:
- Memory storage: `memory-agent/data/`
- Models cache: `memory-agent/models/`
- Agent memory: `memory/`

Override with environment variables or config files.

## Updating

```bash
# Pull latest changes
git pull origin main

# Rebuild environment
./scripts/bootstrap.sh

# Restart services if running
sudo systemctl restart memory-agent  # systemd
# or
docker-compose restart                # docker
```

## Monitoring

### Logs

- **Systemd**: `journalctl -u memory-agent -f`
- **Docker**: `docker logs -f <container-id>`
- **Local**: Check `CI_RUNS/` for build/test logs

### Health Checks

```bash
# Test memory-agent
memory status

# Run health checks
cd memory-agent
pytest tests/test_integration.py
```

## Troubleshooting

### Memory Agent Won't Start

1. Check Python version: `python --version` (need 3.10+)
2. Check dependencies: `pip list | grep memory-agent`
3. Check logs for errors
4. Verify data directory permissions

### Missing Dependencies

```bash
# Reinstall from requirements
pip install -r memory-agent/requirements.txt

# Or use bootstrap
./scripts/bootstrap.sh
```

### Model Download Issues

Memory-agent downloads embedding models on first run. If downloads fail:

```bash
# Pre-download models
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

## Security Considerations

- **Never commit** `.env` files or API keys
- Run services as non-root user
- Use firewall rules to restrict access
- Enable HTTPS for web interfaces
- Regularly update dependencies: `pip install --upgrade -r requirements.txt`

## Backup

Important directories to backup:
```bash
tar -czf backup-$(date +%F).tar.gz \
  memory/ \
  memory-agent/data/ \
  MEMORY.md \
  SOUL.md \
  USER.md
```

Automate with cron:
```cron
0 2 * * * cd /path/to/workspace && ./scripts/backup.sh
```

## Support

- GitHub Issues: Report bugs and request features
- Documentation: Check `docs/` directory
- Memory Agent Docs: See `memory-agent/docs/`
