# Contributing to Wohnung Agent

Thank you for your interest in contributing to Wohnung Agent! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful to all contributors.

## How to Contribute

### Reporting Bugs

Before creating a bug report, check the [GitHub Issues](https://github.com/jfheinrich-eu/apartment-agent/issues) to see if the problem has already been reported.

When filing a bug report, include:
- A clear, descriptive title
- Exact steps to reproduce the problem
- Expected behavior and actual behavior
- Environment (Python version, OS, etc.)
- Relevant configuration and logs

### Suggesting Features

Feature suggestions are welcome! Use GitHub Issues with:
- A clear, descriptive title
- Detailed description of the proposed feature
- Use cases and benefits
- Possible implementation approach (if applicable)

### Pull Requests

1. **Fork and Branch**: Fork the repository and create a branch from `main` with a descriptive name (e.g., `feature/add-immobilienscout-adapter` or `fix/config-validation`)

2. **Local Setup**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e ".[dev]"
   ```

3. **Make Changes**: Ensure your changes:
   - Follow PEP 8 style guidelines
   - Include type hints on all public functions
   - Add or update docstrings (especially "why" behind the code)
   - Are focused on a single concern

4. **Test Locally**:
   ```bash
   make test          # Run all tests
   make lint          # Run static checks
   make format        # Format code with black (if installed)
   ```

5. **Commit and Push**:
   - Use clear, descriptive commit messages
   - Reference related issues if applicable
   - Sign-off on your commits (`git commit -s`) if desired

6. **Create a Pull Request**:
   - Provide a clear description of changes
   - Link related issues (e.g., "Closes #123")
   - Ensure all checks pass before requesting review
   - Be responsive to feedback and review comments

## Development Guidelines

### Architecture

The project uses an adapter-based architecture:
- **Adapters** (`wohnung_agent/adapters/`): Data source implementations
- **Models** (`wohnung_agent/models.py`): Pydantic data structures
- **Filter Engine** (`wohnung_agent/filter_engine.py`): Scoring and filtering logic
- **Database** (`wohnung_agent/database.py`): SQLite persistence
- **Config** (`wohnung_agent/config_loader.py`): Configuration loading and validation

### Code Style

- Python 3.11+
- PEP 8 compliant
- Type hints required for all public APIs
- Use f-strings for string formatting
- Prefer `pathlib.Path` over string paths
- Parametrized SQL queries (no string interpolation)

### Testing

- Tests go in `tests/` directory
- Use `pytest` for test framework
- Aim for >80% code coverage
- Test both happy path and error cases
- Use fixtures for common setup

### Logging

- Use `LOGGER.info()` for important events
- Use `LOGGER.warning()` for recoverable issues
- Use `LOGGER.exception()` in exception handlers to capture tracebacks
- Include context (e.g., URLs, file paths, IDs) in log messages

## Git Workflow

```bash
# Create and switch to feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Descriptive message"

# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions, feel free to:
- Open a GitHub Discussion
- Create a GitHub Issue with the `question` label
- Check the [README](README.md) for more information

Thank you for contributing!
