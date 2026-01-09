"""Tests for the Calculator class."""

import pytest
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from calculator import Calculator


@pytest.fixture
def calculator():
    """Fixture to provide a Calculator instance for tests."""
    return Calculator()


class TestAdd:
    """Tests for the add method."""

    def test_add_positive_numbers(self, calculator):
        """Test adding two positive numbers."""
        assert calculator.add(2, 3) == 5

    def test_add_negative_numbers(self, calculator):
        """Test adding two negative numbers."""
        assert calculator.add(-2, -3) == -5

    def test_add_mixed_numbers(self, calculator):
        """Test adding positive and negative numbers."""
        assert calculator.add(5, -3) == 2

    def test_add_zero(self, calculator):
        """Test adding zero."""
        assert calculator.add(5, 0) == 5
        assert calculator.add(0, 5) == 5


class TestSubtract:
    """Tests for the subtract method."""

    def test_subtract_positive_numbers(self, calculator):
        """Test subtracting two positive numbers."""
        assert calculator.subtract(5, 3) == 2

    def test_subtract_negative_numbers(self, calculator):
        """Test subtracting two negative numbers."""
        assert calculator.subtract(-5, -3) == -2

    def test_subtract_mixed_numbers(self, calculator):
        """Test subtracting with mixed signs."""
        assert calculator.subtract(5, -3) == 8

    def test_subtract_zero(self, calculator):
        """Test subtracting zero."""
        assert calculator.subtract(5, 0) == 5


class TestMultiply:
    """Tests for the multiply method."""

    def test_multiply_positive_numbers(self, calculator):
        """Test multiplying two positive numbers."""
        assert calculator.multiply(3, 4) == 12

    def test_multiply_negative_numbers(self, calculator):
        """Test multiplying two negative numbers."""
        assert calculator.multiply(-3, -4) == 12

    def test_multiply_mixed_numbers(self, calculator):
        """Test multiplying with mixed signs."""
        assert calculator.multiply(3, -4) == -12

    def test_multiply_by_zero(self, calculator):
        """Test multiplying by zero."""
        assert calculator.multiply(5, 0) == 0
        assert calculator.multiply(0, 5) == 0


class TestDivide:
    """Tests for the divide method."""

    def test_divide_positive_numbers(self, calculator):
        """Test dividing two positive numbers."""
        assert calculator.divide(10, 2) == 5

    def test_divide_negative_numbers(self, calculator):
        """Test dividing two negative numbers."""
        assert calculator.divide(-10, -2) == 5

    def test_divide_mixed_numbers(self, calculator):
        """Test dividing with mixed signs."""
        assert calculator.divide(10, -2) == -5

    def test_divide_by_zero(self, calculator):
        """Test that dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculator.divide(10, 0)

    def test_divide_with_float_result(self, calculator):
        """Test division with float result."""
        assert calculator.divide(5, 2) == 2.5
