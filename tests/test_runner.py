"""Tests for runner module."""

from unittest.mock import patch
import pytest

from agent_loop.runner import DEFAULT_MODEL, run_opencode


class TestRunOpencode:
    """Tests for run_opencode()."""

    @pytest.mark.parametrize("dry_run,model", [(True, None), (True, "custom-model")])
    def test_dry_run_returns_true_without_executing(self, dry_run, model):
        """Dry run returns True without executing subprocess."""
        result = run_opencode("test prompt", dry_run=dry_run, model=model)
        assert result is True

    @pytest.mark.parametrize("model,expected", [(None, DEFAULT_MODEL), ("custom-model-v2", "custom-model-v2")])
    @patch("agent_loop.runner.subprocess.run")
    def test_uses_correct_model(self, mock_subprocess, model, expected):
        """Correct model used based on parameter."""
        mock_subprocess.return_value.returncode = 0

        run_opencode("test prompt", dry_run=False, model=model)

        call_args = mock_subprocess.call_args[0][0]
        assert "-m" in call_args
        model_idx = call_args.index("-m")
        assert call_args[model_idx + 1] == expected

    @pytest.mark.parametrize("returncode,expected", [(0, True), (1, False)])
    @patch("agent_loop.runner.subprocess.run")
    def test_returns_bool_based_on_subprocess_result(self, mock_subprocess, returncode, expected):
        """Returns True on success, False on failure."""
        mock_subprocess.return_value.returncode = returncode

        result = run_opencode("test prompt", dry_run=False)

        assert result is expected
