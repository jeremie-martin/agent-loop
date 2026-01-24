"""Core loop logic for the agent loop."""

import signal
import sys
from datetime import datetime

from .git import commit_changes, generate_squash_message_with_agent, get_current_commit, get_repo, has_changes, squash_commits
from .preset import Preset
from .runner import run_opencode


class LoopRunner:
    """Manages the agent loop execution."""

    def __init__(
        self,
        preset: Preset,
        dry_run: bool = False,
        verbose: bool = False,
        auto_squash: bool = True,
        max_iterations: int | None = None,
    ):
        self.preset = preset
        self.dry_run = dry_run
        self.verbose = verbose
        self.auto_squash = auto_squash
        self.max_iterations = max_iterations
        self.iteration = 0
        self.start_commit: str | None = None
        self._interrupted = False

    def _log(self, message: str) -> None:
        """Print a log message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def _verbose(self, message: str) -> None:
        """Print a verbose log message."""
        if self.verbose:
            self._log(message)

    def _run_iteration(self) -> bool:
        """Run a single iteration of the loop.

        Returns True to continue, False to stop.
        """
        mode_idx = self.iteration % len(self.preset.modes)
        mode = self.preset.modes[mode_idx]

        print()
        print("=" * 60)
        self._log(f"Iteration {self.iteration + 1} [{mode.name}]")
        print("=" * 60)

        # Run the agent
        success = run_opencode(
            prompt=self.preset.get_full_prompt(mode),
            dry_run=self.dry_run,
            verbose=self.verbose,
        )

        if not success:
            self._log("Agent returned non-zero; continuing to next iteration")

        # Commit changes if any
        if not self.dry_run:
            repo = get_repo()
            if has_changes(repo):
                msg = f"[{mode.name}] iteration {self.iteration + 1}"
                commit_changes(repo, msg)
                self._log(f"Committed: {msg}")
            else:
                self._log("No changes to commit")

        self.iteration += 1
        return True

    def _handle_interrupt(self, signum: int, frame) -> None:
        """Handle Ctrl+C gracefully."""
        if self._interrupted:
            # Second interrupt - force exit
            print("\nForce stopping...")
            sys.exit(1)

        self._interrupted = True
        print("\n")
        self._log("Stopping loop (press Ctrl+C again to force quit)...")

    def run(self) -> None:
        """Run the main loop until interrupted."""
        print(f"Starting agent loop: {self.preset.name}")
        print(f"Description: {self.preset.description}")
        print(f"Modes: {', '.join(m.name for m in self.preset.modes)}")
        if self.max_iterations:
            print(f"Max iterations: {self.max_iterations}")
        if self.dry_run:
            print("[DRY RUN MODE - no changes will be made]")
        print("Press Ctrl+C to stop")

        if not self.dry_run:
            repo = get_repo()
            self.start_commit = get_current_commit(repo)
            self._verbose(f"Start commit: {self.start_commit[:8]}")

        # Set up signal handler
        original_handler = signal.signal(signal.SIGINT, self._handle_interrupt)

        try:
            while not self._interrupted:
                if self.max_iterations and self.iteration >= self.max_iterations:
                    self._log(f"Reached max iterations ({self.max_iterations})")
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
            self._log("No commits to squash")
            return

        print()
        self._log(f"Squashing commits since {self.start_commit[:8]}...")
        self._log("Generating commit message...")

        # Use agent to generate a meaningful squash message
        message = generate_squash_message_with_agent(repo, self.start_commit)

        if not message:
            # Fallback if agent fails
            message = f"[agent-loop] {self.preset.name}: {self.iteration} iterations"
            self._log("Agent failed to generate message, using fallback")

        if squash_commits(repo, self.start_commit, message):
            self._log(f"Squashed into: {message}")
        else:
            self._log("Squash failed or no commits to squash")


def run_loop(
    preset: Preset,
    dry_run: bool = False,
    verbose: bool = False,
    auto_squash: bool = True,
    max_iterations: int | None = None,
) -> None:
    """Run the agent loop with the given preset."""
    runner = LoopRunner(preset, dry_run=dry_run, verbose=verbose, auto_squash=auto_squash, max_iterations=max_iterations)
    runner.run()
