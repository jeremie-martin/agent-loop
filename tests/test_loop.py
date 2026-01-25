"""Tests for loop logic."""

from unittest.mock import patch
import pytest

from agent_loop.loop import LoopRunner
from agent_loop.preset import Mode, Preset, ReviewConfig


class TestModeCycling:
    """Tests for mode cycling through iterations."""

    @patch("agent_loop.loop.run_opencode")
    def test_modes_cycle_in_order(self, mock_run):
        """Modes cycle in order: first, second, back to first."""
        mock_run.return_value = True

        preset = Preset(
            name="test",
            description="",
            modes=[
                Mode(name="accuracy", prompt="Check accuracy."),
                Mode(name="clarity", prompt="Check clarity."),
            ],
        )
        runner = LoopRunner(preset, dry_run=True)

        # First iteration: first mode
        runner._run_iteration()
        assert runner.iteration == 1

        # Second iteration: second mode
        runner._run_iteration()
        assert runner.iteration == 2

        # Third iteration: wraps back to first mode
        runner._run_iteration()
        assert runner.iteration == 3


class TestReviewCycleTrigger:
    """Tests for review cycle triggering."""

    @pytest.mark.parametrize(
        "review_config,expected_calls",
        [
            (ReviewConfig(enabled=True), [False, True, False]),
            (ReviewConfig(enabled=False), [False, False]),
            (None, [False, False]),
        ],
    )
    @patch("agent_loop.loop.run_opencode")
    @patch("agent_loop.loop.run_review_cycle")
    def test_review_cycle_triggered_correctly(self, mock_review, mock_run, review_config, expected_calls):
        """Review cycle runs only when enabled and after completing a mode cycle."""
        mock_run.return_value = True
        mock_review.return_value = True

        preset = Preset(
            name="test",
            description="",
            modes=[
                Mode(name="accuracy", prompt="Check accuracy."),
                Mode(name="clarity", prompt="Check clarity."),
            ],
            review=review_config,
        )
        runner = LoopRunner(preset, dry_run=True)

        for expected_call in expected_calls:
            mock_review.reset_mock()
            runner._run_iteration()
            if expected_call:
                mock_review.assert_called_once()
            else:
                mock_review.assert_not_called()


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
