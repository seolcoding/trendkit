# Contributing to trendkit

First off, thank you for considering contributing to trendkit!

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Roadmap Items](#roadmap-items)

---

## Code of Conduct

Be kind, respectful, and constructive. We're all here to build something useful together.

---

## Getting Started

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Development Setup

```bash
# Clone the repository
git clone https://github.com/seolcoding/trendkit.git
cd trendkit

# Install dependencies with uv
uv sync --all-extras

# Or with pip
pip install -e ".[all]"

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=trendkit --cov-report=html
```

### Project Structure

```
trendkit/
├── src/trendkit/
│   ├── __init__.py          # Package exports
│   ├── core.py              # Main API functions
│   ├── types.py             # Type definitions
│   ├── cli.py               # CLI entry point
│   ├── mcp_server.py        # MCP server
│   └── backends/
│       ├── rss.py           # RSS backend (trendspyg)
│       ├── pytrends_backend.py  # pytrends backend
│       └── selenium_backend.py  # Selenium backend
├── tests/
│   └── test_api.py          # API tests
├── docs/
│   ├── PRD.md               # Product requirements
│   ├── ROADMAP.md           # Feature roadmap
│   ├── TODO.md              # Task list
│   └── CONTRIBUTING.md      # This file
└── pyproject.toml           # Project config
```

---

## How to Contribute

### Reporting Bugs

1. Search [existing issues](https://github.com/seolcoding/trendkit/issues) first
2. Create a new issue with:
   - Clear title
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Relevant code snippets

### Suggesting Features

1. Check [ROADMAP.md](./ROADMAP.md) for planned features
2. Open an issue with `[Feature]` prefix
3. Describe the use case and proposed solution

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add/update tests
5. Run tests: `uv run pytest`
6. Commit with clear message
7. Push and create a Pull Request

---

## Pull Request Process

### Before Submitting

- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code follows style guide
- [ ] New features have tests
- [ ] Documentation updated if needed

### PR Title Format

```
[Type] Brief description

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation
- refactor: Code refactoring
- test: Test additions
- chore: Maintenance
```

Examples:
- `[feat] Add cache layer for trending()`
- `[fix] Handle rate limit errors gracefully`
- `[docs] Update MCP setup instructions`

### Review Process

1. Maintainer reviews within 48h
2. Address feedback if any
3. Maintainer merges after approval

---

## Style Guide

### Python Code

- **Formatter**: We use `ruff format`
- **Linter**: We use `ruff check`
- **Type hints**: Required for all public functions

```bash
# Format code
uv run ruff format .

# Check linting
uv run ruff check .

# Type check
uv run mypy src/
```

### Code Style Examples

```python
# Good: Type hints + docstring
def trending(
    geo: str = "KR",
    limit: int = 10,
    format: Format = "minimal"
) -> list[str] | list[dict]:
    """Get realtime trending keywords.

    Args:
        geo: Country code (default: KR)
        limit: Maximum results (default: 10)
        format: Output format (minimal/standard/full)

    Returns:
        List of keywords or keyword dicts
    """
    ...

# Bad: No types, no docs
def trending(geo="KR", limit=10, format="minimal"):
    ...
```

### Commit Messages

```
<type>: <description>

[optional body]

Types: feat, fix, docs, refactor, test, chore
```

Examples:
```
feat: add cache layer with TTL support

- Add in-memory LRU cache
- Support TTL configuration
- Add cache invalidation API
```

---

## Roadmap Items

Looking for something to work on? Check these priority items:

### Good First Issues

- [ ] Add more Geo codes to documentation
- [ ] Improve error messages
- [ ] Add CLI `--version` flag

### Medium Difficulty

- [ ] Implement in-memory cache
- [ ] Add retry logic for rate limits
- [ ] Expand test coverage to 80%+

### Advanced

- [ ] LangChain Tool integration
- [ ] Scheduler feature
- [ ] Webhook notifications

See [ROADMAP.md](./ROADMAP.md) and [TODO.md](./TODO.md) for full list.

---

## Questions?

- Open an issue with `[Question]` prefix
- Tag `@seolcoding` for urgent matters

---

Thank you for contributing!
