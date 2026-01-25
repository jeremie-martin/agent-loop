"""Tests for runner module."""

from unittest.mock import patch
import pytest

from agent_loop.runner import DEFAULT_MODEL, run_opencode


class TestRunOpencode:
    """Tests for run_opencode()."""

    @pytest.mark.parametrize("model", [None, "custom-model"])
    def test_dry_run_returns_true_without_executing(self, model):
        """Dry run returns True without executing subprocess."""
        result = run_opencode("test prompt", dry_run=True, model=model)
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

    @pytest.mark.parametrize("returncode,expected", [(0, True), (1, False)])
    @patch("agent_loop.runner.subprocess.run")
    def test_returns_bool_based_on_subprocess_result(self, mock_subprocess, returncode, expected):
        """Returns True on success, False on failure."""
        mock_subprocess.return_value.returncode = returncode

        result = run_opencode("test prompt", dry_run=False)

        assert result is expected
