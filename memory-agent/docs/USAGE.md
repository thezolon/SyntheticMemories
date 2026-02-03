# Memory Agent Usage Guide

## Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd memory-agent
```

### 2. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Setup
```bash
python scripts/setup.py
python scripts/download_models.py
```

## Basic Usage

### Adding Memories

Store a simple text memory:
```bash
python src/main.py add "Met with Sarah to discuss the Q1 roadmap"
```

Add a memory with tags:
```bash
python src/main.py add "Read about RAG systems" --tag learning --tag ai
```

Add from a file:
```bash
python src/main.py add --file notes.txt --tag meeting
```

### Searching Memories

Search semantically:
```bash
python src/main.py search "what did Sarah say about Q1?"
```

Limit results:
```bash
python src/main.py search "machine learning" --limit 10
```

### Asking Questions

Ask questions powered by LLM:
```bash
python src/main.py ask "When is the project deadline?"
```

### Managing Memories

Show a specific memory:
```bash
python src/main.py show mem_abc123
```

List recent memories:
```bash
python src/main.py list
```

Filter by tag:
```bash
python src/main.py list --tag work
```

Delete a memory:
```bash
python src/main.py delete mem_abc123
```

### Statistics

View memory statistics:
```bash
python src/main.py stats
```

## Configuration

Configuration file location: `~/.memory-agent/config.yaml`

Example configuration:
```yaml
embedding:
  model_name: sentence-transformers/all-MiniLM-L6-v2
  device: cpu
  batch_size: 32

llm:
  model_path: ~/.memory-agent/models/llm/llama-2-7b-chat.Q4_K_M.gguf
  context_size: 2048
  n_threads: 4
  n_gpu_layers: 0

storage:
  data_dir: ~/.memory-agent/data
  models_dir: ~/.memory-agent/models
```

## Advanced Usage

### Using GPU

Edit `~/.memory-agent/config.yaml`:
```yaml
embedding:
  device: cuda

llm:
  n_gpu_layers: 35  # Adjust based on VRAM
```

### Custom Models

Download a different LLM:
```bash
# Using Ollama
ollama pull mistral

# Or download GGUF manually
wget https://huggingface.co/.../model.gguf -O ~/.memory-agent/models/llm/custom.gguf
```

Update config:
```yaml
llm:
  model_path: ~/.memory-agent/models/llm/custom.gguf
```

## Tips & Best Practices

### 1. Be Specific
Instead of: "Had a meeting"
Better: "Met with John and Sarah to discuss Q1 marketing strategy. Decided to focus on content marketing."

### 2. Use Tags Consistently
Create a tagging system:
- `work` / `personal`
- `meetings` / `notes` / `ideas`
- `urgent` / `followup`

### 3. Regular Searches
Search your memories regularly to reinforce connections and discover patterns.

### 4. Backup Your Data
```bash
# Backup entire directory
cp -r ~/.memory-agent ~/.memory-agent.backup

# Or just the data
tar -czf memory-backup.tar.gz ~/.memory-agent/data
```

### 5. Cleanup Old Memories
Periodically review and delete outdated memories to keep your database relevant.

## Troubleshooting

### "Model not found"
Run the model download script:
```bash
python scripts/download_models.py
```

### Slow queries
- Reduce batch size in config
- Enable GPU if available
- Consider using a smaller embedding model

### Out of memory
- Use quantized models (Q4 or Q5)
- Reduce `context_size` in config
- Close other applications

### Import errors
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Data Privacy

All data stays local:
- Memories: `~/.memory-agent/data/`
- Models: `~/.memory-agent/models/`
- Config: `~/.memory-agent/config.yaml`
- Logs: `~/.memory-agent/logs/`

To completely remove all data:
```bash
rm -rf ~/.memory-agent
```

## Getting Help

```bash
# General help
python src/main.py --help

# Command-specific help
python src/main.py add --help
python src/main.py search --help
```

## Example Workflow

```bash
# Day 1: Add some memories
memory add "Project kickoff meeting. Timeline: 3 months, budget: $50k" --tag work --tag project-x
memory add "Learned about vector databases. Lance seems promising." --tag learning
memory add "Dentist appointment scheduled for March 15 at 2pm" --tag personal

# Day 2: Search and query
memory search "project timeline"
# Returns: Project kickoff meeting...

memory ask "What's the budget for the project?"
# Returns: The budget is $50k, as mentioned in the project kickoff meeting.

memory list --tag personal
# Shows: Dentist appointment...

# Day 3: Stats and maintenance
memory stats
# Total memories: 3
# Storage used: 245 KB

memory delete mem_old123  # Remove outdated memory
```

## Next Steps

- Read [DESIGN.md](../DESIGN.md) for philosophy
- Read [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details
- Check [ROADMAP.md](../ROADMAP.md) for upcoming features
- Contribute: Issues and PRs welcome!
