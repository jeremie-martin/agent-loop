"""Tests for loop logic."""

from unittest.mock import patch

from agent_loop.loop import LoopRunner
from agent_loop.preset import Mode, Preset


class TestConsecutiveFailures:
    """Tests for consecutive failure threshold."""

    @patch("agent_loop.loop.run_opencode")
    def test_stops_after_max_consecutive_failures(self, mock_run):
        """Loop stops after reaching max consecutive failures."""
        mock_run.return_value = False  # Always fail

        preset = Preset(name="test", description="", modes=[Mode(name="review", prompt="Review.")])
        runner = LoopRunner(preset, dry_run=True, max_consecutive_failures=2)

        # First failure - should continue
        result = runner._run_iteration()
        assert result is True
        assert runner._consecutive_failures == 1

        # Second failure - should stop
        result = runner._run_iteration()
        assert result is False
        assert runner._consecutive_failures == 2

    @patch("agent_loop.loop.run_opencode")
    def test_success_resets_failure_counter(self, mock_run):
        """Successful iteration resets failure counter."""
        mock_run.return_value = True  # Success

        preset = Preset(name="test", description="", modes=[Mode(name="review", prompt="Review.")])
        runner = LoopRunner(preset, dry_run=True, max_consecutive_failures=3)

        # Simulate previous failures
        runner._consecutive_failures = 2

        # Successful iteration
        runner._run_iteration()

        assert runner._consecutive_failures == 0

    @patch("agent_loop.loop.run_opencode")
    def test_none_threshold_allows_unlimited_failures(self, mock_run):
        """None threshold allows unlimited consecutive failures."""
        mock_run.return_value = False  # Always fail

        preset = Preset(name="test", description="", modes=[Mode(name="review", prompt="Review.")])
        runner = LoopRunner(preset, dry_run=True, max_consecutive_failures=None)

        # Many consecutive failures should still return True (continue)
        for i in range(10):
            result = runner._run_iteration()
            assert result is True
            assert runner._consecutive_failures == i + 1


class TestModelPassthrough:
    """Tests for model being passed to run_opencode."""

    @patch("agent_loop.loop.run_opencode")
    def test_model_passed_to_run_opencode(self, mock_run):
        """Preset model is passed to run_opencode."""
        mock_run.return_value = True

        preset = Preset(
            name="test",
            description="",
            modes=[Mode(name="review", prompt="Review.")],
            model="custom-model-v1",
        )
        runner = LoopRunner(preset, dry_run=True)

        runner._run_iteration()

        # Verify model was passed
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["model"] == "custom-model-v1"

    @patch("agent_loop.loop.run_opencode")
    def test_none_model_passed_when_not_specified(self, mock_run):
        """None model passed when preset doesn't specify one."""
        mock_run.return_value = True

        preset = Preset(name="test", description="", modes=[Mode(name="review", prompt="Review.")])
        runner = LoopRunner(preset, dry_run=True)

        runner._run_iteration()

        call_kwargs = mock_run.call_args[1]
        assert call_kwargs["model"] is None
