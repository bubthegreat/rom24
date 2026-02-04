# UV Package Manager Migration

This project has been migrated from pip/setuptools to **UV**, a modern, fast Python package manager from Astral (the creators of Ruff).

## What Changed

### ✅ Migrated to UV
- **Package management**: Now using `uv` instead of `pip`
- **Configuration**: All dependencies now in `pyproject.toml` (single source of truth)
- **Lock file**: `uv.lock` ensures reproducible builds
- **GitHub Actions**: All workflows updated to use UV
- **Dockerfile**: Already using UV (no changes needed)

### ❌ Removed Files
- `setup.py` - Replaced by `pyproject.toml`
- `requirements.txt` - Dependencies now in `pyproject.toml`

## Installation

### Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

### Install Project Dependencies

```bash
# Install production dependencies
uv sync

# Install with dev dependencies
uv sync --all-extras

# Or just dev dependencies
uv sync --extra dev
```

## Usage

### Running the Application

```bash
# Run rom24
uv run rom24

# Or activate the virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
rom24
```

### Development Commands

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=rom24

# Run mypy type checking
uv run mypy src

# Run black formatter
uv run black src

# Run ruff linter
uv run ruff check src

# Format with ruff
uv run ruff format src
```

### Adding Dependencies

```bash
# Add a production dependency
uv add package-name

# Add a dev dependency
uv add --dev package-name

# Remove a dependency
uv remove package-name
```

### Updating Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Update a specific package
uv lock --upgrade-package package-name
```

## Benefits of UV

1. **⚡ Fast**: 10-100x faster than pip
2. **🔒 Reliable**: Lock file ensures reproducible builds
3. **🎯 Simple**: Single tool for all Python package management
4. **🔄 Compatible**: Works with existing pip/PyPI ecosystem
5. **📦 Modern**: Built with Rust, designed for modern Python workflows

## Migration Notes

- The `pyproject.toml` now contains all project metadata and dependencies
- Dev dependencies are in `[project.optional-dependencies.dev]`
- The entry point `rom24` is defined in `[project.scripts]`
- Python 3.12+ is required (down from 3.14 in the old config)
- All GitHub Actions workflows now use UV for faster CI/CD

## Troubleshooting

### UV not found
Make sure UV is installed and in your PATH:
```bash
uv --version
```

### Dependencies not syncing
Try removing the virtual environment and re-syncing:
```bash
rm -rf .venv
uv sync --all-extras
```

### Lock file conflicts
Update the lock file:
```bash
uv lock
```

## Documentation

- UV Documentation: https://docs.astral.sh/uv/
- UV GitHub: https://github.com/astral-sh/uv
- Astral Blog: https://astral.sh/blog

