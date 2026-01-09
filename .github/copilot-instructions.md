# GitHub Copilot Instructions

## Project Conventions

### Python Style Guide
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings to all classes and methods using Google-style format
- Keep lines under 100 characters where practical

### Code Structure
- Source code lives in `src/` directory
- Tests live in `tests/` directory
- Each test file should correspond to a source file (e.g., `test_calculator.py` for `calculator.py`)

### Testing
- Use pytest for all tests
- Organize tests into classes grouped by method/functionality
- Include docstrings for all test methods explaining what is being tested
- Test both happy paths and edge cases (e.g., division by zero)
- Use pytest fixtures for common test setup

### Documentation
- All public classes and methods must have docstrings
- Docstrings should include:
  - Brief description
  - Args section for parameters
  - Returns section for return values
  - Raises section for exceptions

### Error Handling
- Use descriptive error messages
- Raise appropriate exception types (e.g., ValueError for invalid inputs)
- Handle edge cases explicitly (e.g., division by zero)

### Dependencies
- List all dependencies in `requirements.txt`
- Pin major versions to ensure compatibility
- Keep dependencies minimal

### Running Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run tests with coverage
pytest --cov=src
```
