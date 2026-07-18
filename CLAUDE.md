# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

This repository contains machine learning assignments using Jupyter notebooks in a Dockerized environment.

### Environment Setup
- Docker container based on `python:3.11-slim` with UV package manager
- Dependencies managed via `requirements/base.txt`
- To build and run the container:
  ```bash
  docker build -t ml-assignments .
  docker run -p 8888:8888 -v $(pwd)/workspace:/home/dev/project ml-assignments
  ```

### Working with Notebooks
- Jupyter notebooks are located in `workspace/notebooks/`
- Assignment-specific notebooks are organized in subdirectories (e.g., `workspace/notebooks/m2-891/`)
- Outputs from notebook executions are stored in `workspace/outputs/`
- Data files used by notebooks are in `workspace/data/`

### Common Commands
- Install additional packages: `uv pip install <package-name>`
- Start Jupyter server: `jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root`
- Access Jupyter interface at http://localhost:8888 when container is running
- Execute notebooks: `jupyter nbconvert --to notebook --execute <notebook.ipynb> --output <output.ipynb>`

### Repository Structure
- `.devcontainer/` - VS Code development container configuration
- `requirements/` - Python package requirements files
- `workspace/` - Main working directory containing:
  - `data/` - Input data files
  - `notebooks/` - Jupyter notebooks organized by module/assignment
  - `outputs/` - Generated outputs from notebook executions

### Best Practices
- Keep notebooks in the `workspace/notebooks/` directory structure
- Store generated outputs in `workspace/outputs/` to avoid cluttering notebook directories
- Use relative paths when referencing data files from within notebooks
- Commit notebook outputs selectively - prefer storing them in the outputs directory