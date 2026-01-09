# GitHub Copilot Agentic Workflow Test

A simple Python project for testing multi-agent workflows with a Calculator class and comprehensive pytest test suite.

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   └── calculator.py       # Calculator class with basic arithmetic operations
├── tests/
│   └── test_calculator.py  # Pytest tests for Calculator
├── .github/
│   └── copilot-instructions.md  # Project conventions and coding standards
├── pyproject.toml          # Project configuration and pytest settings
├── requirements.txt        # Project dependencies
├── .gitignore             # Python gitignore patterns
└── README.md              # This file
```

## Features

The Calculator class provides the following operations:
- **add(a, b)**: Add two numbers
- **subtract(a, b)**: Subtract b from a
- **multiply(a, b)**: Multiply two numbers
- **divide(a, b)**: Divide a by b (with division by zero handling)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ltpitt/github-copilot-agentic-workflow-test.git
cd github-copilot-agentic-workflow-test
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run tests with coverage:
```bash
pytest --cov=src
```

## Test Coverage

The project includes 17 comprehensive tests covering:
- Addition (positive, negative, mixed numbers, zero)
- Subtraction (positive, negative, mixed numbers, zero)
- Multiplication (positive, negative, mixed numbers, zero)
- Division (positive, negative, mixed numbers, division by zero error handling, float results)

## Development

This project follows Python best practices:
- PEP 8 style guidelines
- Google-style docstrings for all classes and methods
- Comprehensive test coverage with pytest
- Clean project structure with separate src and tests directories

For more details on project conventions, see [.github/copilot-instructions.md](.github/copilot-instructions.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
