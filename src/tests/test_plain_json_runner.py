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
            "completion": '[{"func_name": "test_name", "args": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
        }
        result = runner.run(**sample)
        assert result.get("correct") is False

    def test_positive_relevance(self, runner):
        """Test the positive relevance sample."""
        sample = {
            "id": "live_relevance_15-15-0",
            "completion": '[{"func_name": "test_name", "args": {"arg1": "test_arg1", "arg2": "test_arg2"}}]',
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
