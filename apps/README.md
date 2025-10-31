# Applications

This directory contains runnable applications and demos built with the Mirror-OS framework.

## Structure

### `/dashboard/`
Interactive web dashboard for visualizing and managing Mirror-OS data flows, relational profiles, and system diagnostics.

**Tech Stack:** React + TypeScript frontend, Python FastAPI backend, PostgreSQL database

**Quick Start:**
```bash
cd dashboard
docker-compose up
# Access at http://localhost:3000
```

### `/relational-analyzer/`
Core analytical engine for computing relational fitness, truth-distortion metrics, and applying Relational Math principles to real-world datasets.

**Features:**
- Truth-Distortion unified analysis
- NFL competition models (Graph Neural Networks)
- Dataset exploration tools
- RM Translation Layer implementations

**Quick Start:**
```bash
cd relational-analyzer
python analyze.py --help
```

### `/mirror-os-app/`
Main Mirror-OS application interface - TypeScript/React implementation of the core Mirror-OS concepts and visualization tools.

### `/examples/`
Example implementations and demonstrations:
- `Architect_Lens_Examples.md` - Practical examples using the Architect Lens framework

## Development

Each app is independently runnable. See individual README files in each subdirectory for specific setup instructions.
