"""Core loop logic for the agent loop."""

import signal
import sys

from loguru import logger

from .git import generate_squash_message_with_agent, get_current_commit, get_repo, squash_commits
from .preset import Preset
from .review import run_review_cycle
from .runner import run_opencode


class LoopRunner:
    """Manages the agent loop execution."""

    def __init__(
        self,
        preset: Preset,
        dry_run: bool = False,
        auto_squash: bool = True,
        max_iterations: int | None = None,
    ):
        self.preset = preset
        self.dry_run = dry_run
        self.auto_squash = auto_squash
        self.max_iterations = max_iterations
        self.iteration = 0
        self.start_commit: str | None = None
        self._interrupted = False

    def _run_iteration(self) -> bool:
        """Run a single iteration of the loop.

        Returns True to continue, False to stop.
        """
        mode_idx = self.iteration % len(self.preset.modes)
        mode = self.preset.modes[mode_idx]
        is_cycle_complete = mode_idx == len(self.preset.modes) - 1

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"Iteration {self.iteration + 1} [{mode.name}]")
        logger.info("=" * 60)

        prompt = self.preset.get_full_prompt(mode)

        # Run the agent (agents commit their own changes via prompts)
        success = run_opencode(prompt=prompt, dry_run=self.dry_run)

        if not success:
            logger.warning("Agent returned non-zero; continuing to next iteration")

        self.iteration += 1

        # Run review after completing a full cycle of all modes
        if is_cycle_complete and self.preset.review and self.preset.review.enabled:
            self._run_review_cycle()

        return True

    def _run_review_cycle(self) -> None:
        """Run a review cycle to validate changes."""
        if not self.preset.review:
            return

        logger.info("")
        logger.info("-" * 60)
        logger.info("Running review cycle...")
        logger.info("-" * 60)

        success = run_review_cycle(
            preset=self.preset,
            config=self.preset.review,
            dry_run=self.dry_run,
        )

        if success:
            logger.info("Review cycle completed")
        else:
            logger.warning("Review cycle had issues")

    def _handle_interrupt(self, signum: int, frame) -> None:
        """Handle Ctrl+C gracefully."""
        if self._interrupted:
            # Second interrupt - force exit
            logger.warning("Force stopping...")
            sys.exit(1)

        self._interrupted = True
        logger.info("")
        logger.info("Stopping loop (press Ctrl+C again to force quit)...")

    def run(self) -> None:
        """Run the main loop until interrupted."""
        logger.info(f"Starting agent loop: {self.preset.name}")
        logger.info(f"Description: {self.preset.description}")
        logger.info(f"Modes: {', '.join(m.name for m in self.preset.modes)}")
        if self.preset.review and self.preset.review.enabled:
            logger.info("Review: enabled (runs after each cycle)")
        if self.max_iterations:
            logger.info(f"Max iterations: {self.max_iterations}")
        if self.dry_run:
            logger.warning("[DRY RUN MODE - no changes will be made]")
        logger.info("Press Ctrl+C to stop")

        if not self.dry_run:
            repo = get_repo()
            self.start_commit = get_current_commit(repo)
            logger.debug(f"Start commit: {self.start_commit[:8]}")

        # Set up signal handler
        original_handler = signal.signal(signal.SIGINT, self._handle_interrupt)

        try:
            while not self._interrupted:
                if self.max_iterations and self.iteration >= self.max_iterations:
                    logger.info(f"Reached max iterations ({self.max_iterations})")
                    break
                self._run_iteration()
        finally:
            signal.signal(signal.SIGINT, original_handler)

        # Handle squash on stop
        if self.auto_squash and not self.dry_run and self.start_commit:
            self._do_squash()

    def _do_squash(self) -> None:
        """Squash commits made during the loop."""
        if not self.start_commit:
            return

        repo = get_repo()
        current = get_current_commit(repo)

        if current == self.start_commit:
            logger.info("No commits to squash")
            return

        logger.info("")
        logger.info(f"Squashing commits since {self.start_commit[:8]}...")
        logger.debug("Generating commit message with agent...")

        # Use agent to generate a meaningful squash message
        message = generate_squash_message_with_agent(repo, self.start_commit)

        if not message:
            # Fallback if agent fails
            message = f"[agent-loop] {self.preset.name}: {self.iteration} iterations"
            logger.warning("Agent failed to generate message, using fallback")

        if squash_commits(repo, self.start_commit, message):
            logger.info(f"Squashed into: {message}")
        else:
            logger.error("Squash failed or no commits to squash")


def run_loop(
    preset: Preset,
    dry_run: bool = False,
    auto_squash: bool = True,
    max_iterations: int | None = None,
) -> None:
    """Run the agent loop with the given preset."""
    runner = LoopRunner(preset, dry_run=dry_run, auto_squash=auto_squash, max_iterations=max_iterations)
    runner.run()
