# Contributing to rpi-simple-debugger

Thank you for your interest in contributing to rpi-simple-debugger! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project welcomes contributions from everyone. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A Raspberry Pi (recommended for hardware testing, but not required for development)

### Finding Issues to Work On

- Check the [Issues](https://github.com/Ponsriram/rpi-simple-debugger/issues) page for open issues
- Look for issues labeled `good first issue` for beginner-friendly tasks
- Feel free to open a new issue to discuss features or bugs before starting work

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/rpi-simple-debugger.git
cd rpi-simple-debugger

# Add upstream remote
git remote add upstream https://github.com/Ponsriram/rpi-simple-debugger.git
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
# Install the package in editable mode with all dependencies
pip install -e .[raspberry]

# Install WebSocket support for uvicorn
pip install websockets

# Install development dependencies
pip install pytest pytest-cov black isort mypy
```

### 4. Verify Installation

```bash
# Run tests
pytest

# Start the server (will run with mock GPIO on non-Raspberry Pi)
uvicorn rpi_simple_debugger.app:create_app --factory --reload
```

## Development Workflow

### 1. Create a Feature Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create a new feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write clear, concise code following our [Coding Standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/rpi_simple_debugger --cov-report=html

# Format code
black src/ tests/
isort src/ tests/

# Type check
mypy src/
```

### 4. Commit Your Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "Add feature: your feature description"
```

**Commit Message Guidelines:**
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues and pull requests when relevant

Examples:
- `Add WiFi signal strength monitoring`
- `Fix GPIO cleanup on shutdown`
- `Update documentation for WebSocket API`
- `Refactor network monitor for better error handling`

### 5. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Standards

### Python Style

We follow PEP 8 with some specific guidelines:

- **Line length:** Maximum 88 characters (Black default)
- **Imports:** Use `isort` to organize imports
- **Type hints:** Use type hints for all function signatures
- **Docstrings:** Use Google-style docstrings

### Code Formatting

Use [Black](https://black.readthedocs.io/) for automatic code formatting:

```bash
black src/ tests/
```

Use [isort](https://pycqa.github.io/isort/) for import sorting:

```bash
isort src/ tests/
```

### Type Checking

We use type hints and check them with [mypy](http://mypy-lang.org/):

```bash
mypy src/
```

### Example Code Style

```python
from __future__ import annotations

from typing import Optional


def process_gpio_state(
    pin: int,
    value: int,
    label: Optional[str] = None,
) -> dict[str, Any]:
    """Process GPIO state and return formatted data.

    Args:
        pin: BCM pin number.
        value: Pin state (0 or 1).
        label: Optional human-readable label.

    Returns:
        Dictionary containing formatted GPIO state.

    Raises:
        ValueError: If pin number is invalid.
    """
    if pin < 0:
        raise ValueError(f"Invalid pin number: {pin}")

    return {
        "pin": pin,
        "value": value,
        "label": label,
    }
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Name test functions with `test_` prefix
- Use descriptive test names that explain what is being tested

Example:

```python
def test_gpio_monitor_detects_pin_change():
    """Test that GPIO monitor correctly detects when a pin changes state."""
    # Test implementation
    pass
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_gpio_monitor.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/rpi_simple_debugger --cov-report=html
```

### Test Coverage

Aim for at least 80% test coverage for new code. View coverage report:

```bash
pytest --cov=src/rpi_simple_debugger --cov-report=html
# Open htmlcov/index.html in your browser
```

## Documentation

### Code Documentation

- Add docstrings to all public functions, classes, and methods
- Use Google-style docstrings
- Include type hints in function signatures
- Add inline comments for complex logic

### User Documentation

When adding or modifying features:

1. Update `README.md` with user-facing changes
2. Update `docs/GUIDE.md` for detailed explanations
3. Add examples to demonstrate new functionality
4. Update API reference if endpoints change

## Submitting Changes

### Pull Request Process

1. **Update your branch** with the latest upstream changes:
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/your-feature-name
   git rebase main
   ```

2. **Ensure all tests pass** and code is formatted:
   ```bash
   pytest
   black src/ tests/
   isort src/ tests/
   mypy src/
   ```

3. **Create a Pull Request** on GitHub with:
   - Clear title describing the change
   - Detailed description of what changed and why
   - Reference to related issues (e.g., "Fixes #123")
   - Screenshots/examples for UI changes
   - List of breaking changes (if any)

4. **Respond to feedback** from reviewers

5. **Squash commits** if requested before merging

### Pull Request Template

```markdown
## Description
Brief description of the changes.

## Related Issue
Fixes #(issue number)

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes.

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Added tests for new functionality
```

## Project Structure

```
rpi-simple-debugger/
├── src/
│   └── rpi_simple_debugger/
│       ├── __init__.py
│       ├── app.py              # FastAPI application
│       ├── config.py           # Configuration handling
│       ├── gpio_monitor.py     # GPIO monitoring
│       ├── network_monitor.py  # WiFi/Bluetooth monitoring
│       └── system_monitor.py   # System health monitoring
├── tests/
│   ├── test_imports.py
│   └── ws_subscriber.py        # WebSocket client example
├── docs/
│   └── GUIDE.md               # Comprehensive guide
├── pyproject.toml             # Project configuration
├── README.md                  # Main documentation
├── CONTRIBUTING.md            # This file
└── LICENSE                    # MIT License
```

## Questions?

If you have questions about contributing:

1. Check existing [Issues](https://github.com/Ponsriram/rpi-simple-debugger/issues)
2. Create a new issue with the `question` label
3. Contact the maintainers

Thank you for contributing to rpi-simple-debugger! 🎉
