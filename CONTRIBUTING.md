# Contributing to Mpers Trading Bot

Thank you for your interest in contributing to the Mpers Trading Bot project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Review Process](#code-review-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone. We expect all contributors to:

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, trolling, or discriminatory comments
- Publishing others' private information without permission
- Personal or political attacks
- Other conduct which could reasonably be considered inappropriate

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/mpers-trading-bot.git
   cd mpers-trading-bot
   ```

3. **Add upstream remote**:

   ```bash
   git remote add upstream https://github.com/rohteemie/mpers-trading-bot.git
   ```

4. **Create a branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

### Installation

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Install the package in development mode:

   ```bash
   pip install -e .
   ```

4. Verify the setup:

   ```bash
   pytest
   ```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line Length**: Maximum 100 characters
- **Imports**: Organized using `isort`
- **Formatting**: Automatic using `black`
- **Naming Conventions**:
  - Classes: `PascalCase`
  - Functions/Variables: `snake_case`
  - Constants: `UPPER_CASE`
  - Private methods/attributes: `_leading_underscore`

### Code Quality Tools

Before committing, ensure your code passes all quality checks:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Check style
flake8 src/ tests/
pycodestyle src/ tests/

# Analyze code
pylint src/mpers_bot/
```

### Documentation

- **Docstrings**: All public modules, classes, and functions must have docstrings
- **Format**: Use Google-style docstrings
- **Comments**: Use inline comments sparingly and only when necessary

Example docstring:

```python
def calculate_position_size(account_balance, risk_percent, stop_loss):
    """Calculate the position size based on risk parameters.

    Args:
        account_balance (float): Total account balance in base currency
        risk_percent (float): Risk percentage per trade (0-100)
        stop_loss (float): Stop loss distance in pips

    Returns:
        float: Position size in lots

    Raises:
        ValueError: If risk_percent is not between 0 and 100
    """
    pass
```

### Type Hints

Use type hints for function parameters and return values:

```python
from typing import List, Dict, Optional

def process_data(data: List[Dict], limit: Optional[int] = None) -> Dict:
    """Process trading data."""
    pass
```

## Making Changes

### Branch Naming

Use descriptive branch names with prefixes:

- `feature/` - New features (e.g., `feature/add-rsi-indicator`)
- `bugfix/` - Bug fixes (e.g., `bugfix/fix-order-validation`)
- `docs/` - Documentation changes (e.g., `docs/update-readme`)
- `refactor/` - Code refactoring (e.g., `refactor/simplify-strategy-engine`)
- `test/` - Test improvements (e.g., `test/add-integration-tests`)

### Commit Messages

Write clear, concise commit messages:

```bash
<type>: <subject>

<body>

<footer>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semi colons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat: add RSI indicator implementation

Implement the Relative Strength Index (RSI) technical indicator
with configurable period and overbought/oversold thresholds.

Closes #42
```

```bash
fix: correct position size calculation

Fix floating point precision issue in position size calculation
that caused incorrect lot sizes for small accounts.

Fixes #123
```

## Testing

### Writing Tests

- Write tests for all new features and bug fixes
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test setup

Example test:

```python
def test_calculate_position_size_with_valid_inputs():
    """Test position size calculation with valid parameters."""
    # Arrange
    account_balance = 10000
    risk_percent = 2.0
    stop_loss = 50

    # Act
    position_size = calculate_position_size(account_balance, risk_percent, stop_loss)

    # Assert
    assert position_size > 0
    assert position_size <= account_balance * 0.02
```

### Running Tests

Run the full test suite:

```bash
pytest
```

Run specific tests:

```bash
pytest tests/test_indicators.py
pytest tests/test_indicators.py::test_rsi_calculation
```

Run with coverage:

```bash
pytest --cov=mpers_bot --cov-report=html
```

### Test Coverage

- Aim for at least 80% code coverage
- All new code should have corresponding tests
- Critical paths should have 100% coverage

## Submitting Changes

### Before Submitting

1. **Update your branch** with the latest upstream changes:

   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests**:

   ```bash
   pytest
   ```

3. **Run code quality checks**:

   ```bash
   black src/ tests/
   isort src/ tests/
   flake8 src/ tests/
   pylint src/mpers_bot/
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. Push your changes to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Go to the GitHub repository and create a Pull Request

3. Fill in the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Screenshots (if applicable)

4. Ensure CI checks pass

### Pull Request Template

```markdown
## Description
Brief description of what this PR does

## Related Issues
Closes #123

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
- [ ] All tests pass
- [ ] Added new tests for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All CI checks pass
```

## Code Review Process

### What to Expect

- Reviews typically happen within 2-3 business days
- Reviewers may request changes or ask questions
- Be responsive to feedback and questions
- Multiple rounds of review may be necessary

### Review Criteria

Reviewers will check for:

- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Code Quality**: Is the code clean and maintainable?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow our coding standards?
- **Performance**: Are there any performance concerns?
- **Security**: Are there any security issues?

### Addressing Feedback

1. Make requested changes in new commits
2. Push changes to your branch
3. Respond to comments to explain changes
4. Request re-review when ready

## Additional Guidelines

### Performance Considerations

- Profile code for performance bottlenecks
- Use appropriate data structures and algorithms
- Consider memory usage for large datasets
- Cache expensive operations when appropriate

### Security Best Practices

- Never commit sensitive data (API keys, passwords)
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices

### Documentations

- Update README.md for user-facing changes
- Update ROADMAP.md for new features
- Add inline documentation for complex logic
- Create examples for new features

## Getting Help

If you have questions or need help:

- Check existing documentation
- Search closed issues for similar problems
- Open a new issue with the "question" label
- Join our community discussions

## Recognition

Contributors will be recognized in:

- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Mpers Trading Bot! 🚀

---

**Questions?** Open an issue or reach out to the maintainers.
