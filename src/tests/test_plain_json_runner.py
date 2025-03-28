import pytest

from bfcl.runners import PlainJsonRunner


class TestPlainJsonRunner:
    """Test the PlainJsonRunner class."""

    @pytest.fixture
    def runner(self):
        """Return a fixture for the PlainJsonRunner instance."""
        return PlainJsonRunner()

    def test_positive_irrelevance(self, runner):
        """Test the positive irrelevance sample."""
        sample = {
            "id": "live_irrelevance_9-0-9",
            "completion": "I'm sorry, I don't understand. Can you please rephrase your question?",
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_irrelevance(self, runner):
        """Test the negative irrelevance sample."""
        sample = {
            "id": "live_irrelevance_9-0-9",
            "completion": '[{"test_name": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_positive_relevance(self, runner):
        """Test the positive relevance sample."""
        sample = {
            "id": "live_relevance_15-15-0",
            "completion": '[{"test_name": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_relevance(self, runner):
        """Test the negative relevance sample."""
        sample = {
            "id": "live_relevance_15-15-0",
            "completion": "I'm sorry, I don't understand. Can you please rephrase your question?",
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_positive_ast_simple_with_optional_parameter(self, runner):
        """Test the positive ast simple sample with optional parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5, "z": 0}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_ast_simple_without_optional_parameter(self, runner):
        """Test the positive ast simple sample without optional parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_ast_simple_value_error(self, runner):
        """Test the negative ast simple sample with value error."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 5, "y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("value_error")

    def test_negative_ast_simple_type_error(self, runner):
        """Test the negative ast simple sample with type error."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": [5], "y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").startswith("type_error")

    def test_negative_ast_simple_missing_required_parameter(self, runner):
        """Test the negative ast simple sample with missing required parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"y": 5, "z": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_ast_simple_unexpected_parameter(self, runner):
        """Test the negative ast simple sample with unexpected parameter."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot": {"x": 4, "y": 5, "w": 1}}]'}
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("unexpected_param")

    def test_negative_ast_simple_invalid_json_format(self, runner):
        """Test the negative ast simple sample with invalid JSON format."""
        sample = {"id": "simple_2", "completion": '[{"math.hypot":, {"x": 4, "y": 5, "w": 1}}]'}
        result = runner.run(**sample)
        assert result.get("formatted") is False

    def test_positive_ast_multiple_with_optional_parameter(self, runner):
        """Test the positive ast multiple sample with optional parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2], "rounding": 0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_positive_ast_multiple_without_optional_parameter(self, runner):
        """Test the positive ast multiple sample without optional parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2]}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is True

    def test_negative_ast_multiple_missing_required_parameter(self, runner):
        """Test the negative ast multiple sample with missing required parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "rounding": 0}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("missing_required")

    def test_negative_ast_multiple_unexpected_parameter(self, runner):
        """Test the negative ast multiple sample with unexpected parameter."""
        sample = {
            "id": "multiple_3",
            "completion": '[{"EuclideanDistance.calculate": {"pointA": [3, 4], "pointB": [1, 2], "rounding": 0, "unexpected_param": 1}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False and result.get("errors")[0].get("error_type").endswith("unexpected_param")
