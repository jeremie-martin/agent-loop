"""Tests for runner module."""

from unittest.mock import patch

from agent_loop.runner import DEFAULT_MODEL, run_opencode


class TestRunOpencode:
    """Tests for run_opencode()."""

    def test_dry_run_returns_true(self):
        """Dry run returns True without executing."""
        result = run_opencode("test prompt", dry_run=True)
        assert result is True

    def test_dry_run_with_model(self):
        """Dry run works with custom model."""
        result = run_opencode("test prompt", dry_run=True, model="custom-model")
        assert result is True

    @patch("agent_loop.runner.subprocess.run")
    def test_uses_default_model_when_none(self, mock_subprocess):
        """Default model used when model is None."""
        mock_subprocess.return_value.returncode = 0

        run_opencode("test prompt", dry_run=False, model=None)

        call_args = mock_subprocess.call_args[0][0]
        assert "-m" in call_args
        model_idx = call_args.index("-m")
        assert call_args[model_idx + 1] == DEFAULT_MODEL

    @patch("agent_loop.runner.subprocess.run")
    def test_uses_custom_model_when_provided(self, mock_subprocess):
        """Custom model used when provided."""
        mock_subprocess.return_value.returncode = 0

        run_opencode("test prompt", dry_run=False, model="custom-model-v2")

        call_args = mock_subprocess.call_args[0][0]
        model_idx = call_args.index("-m")
        assert call_args[model_idx + 1] == "custom-model-v2"

    @patch("agent_loop.runner.subprocess.run")
    def test_returns_true_on_success(self, mock_subprocess):
        """Returns True when command succeeds."""
        mock_subprocess.return_value.returncode = 0

        result = run_opencode("test prompt", dry_run=False)

        assert result is True

    @patch("agent_loop.runner.subprocess.run")
    def test_returns_false_on_failure(self, mock_subprocess):
        """Returns False when command fails."""
        mock_subprocess.return_value.returncode = 1

        result = run_opencode("test prompt", dry_run=False)

        assert result is False
