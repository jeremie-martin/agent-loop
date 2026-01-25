"""Git operations for the agent loop."""

import subprocess
from pathlib import Path

from git import Repo
from git.exc import InvalidGitRepositoryError

from .runner import DEFAULT_MODEL


def get_repo(path: Path | None = None) -> Repo:
    """Get the git repository at the given path."""
    try:
        return Repo(path or Path.cwd(), search_parent_directories=True)
    except InvalidGitRepositoryError:
        raise RuntimeError("Not in a git repository")


def get_current_commit(repo: Repo) -> str:
    """Get the current HEAD commit hash."""
    return repo.head.commit.hexsha


def has_changes(repo: Repo) -> bool:
    """Check if there are uncommitted changes (staged or unstaged)."""
    return repo.is_dirty(untracked_files=True)


def commit_changes(repo: Repo, message: str) -> bool:
    """Stage all changes and commit.

    Returns True if a commit was made, False if there were no changes.
    """
    if not has_changes(repo):
        return False

    repo.git.add("-A")
    repo.index.commit(message)
    return True


def get_commits_since(repo: Repo, commit_hash: str) -> list[str]:
    """Get all commit hashes since the given commit (exclusive).

    Returns commits in order from oldest to newest.
    """
    try:
        commits = list(repo.iter_commits(f"{commit_hash}..HEAD"))
        return [c.hexsha for c in reversed(commits)]
    except Exception:
        return []


def squash_commits(repo: Repo, since_commit: str, message: str | None = None) -> bool:
    """Squash all commits since the given commit into one.

    Args:
        repo: The git repository.
        since_commit: The commit hash to squash from (exclusive).
        message: Optional commit message. If None, generates one from the squashed commits.

    Returns:
        True if squash was successful, False otherwise.
    """
    commits = get_commits_since(repo, since_commit)
    if not commits:
        return False

    if message is None:
        # Collect messages from all commits being squashed
        commit_messages = []
        for c in commits:
            commit_obj = repo.commit(c)
            msg = commit_obj.message
            if isinstance(msg, bytes):
                msg = msg.decode("utf-8")
            commit_messages.append(f"- {msg.strip().split(chr(10))[0]}")
        message = "Squashed commits:\n" + "\n".join(commit_messages)

    # Soft reset to the starting commit, then recommit everything
    repo.git.reset("--soft", since_commit)
    repo.git.add("-A")
    repo.index.commit(message)
    return True


def generate_squash_message_with_agent(repo: Repo, since_commit: str) -> str | None:
    """Use an agent to generate a meaningful squash commit message.

    Returns the generated message, or None if generation failed.
    """
    commits = get_commits_since(repo, since_commit)
    if not commits:
        return None

    # Get the diff
    try:
        diff = repo.git.diff(since_commit, "HEAD", stat=True)
    except Exception:
        diff = "(could not generate diff)"

    # Collect commit messages
    commit_info = []
    for c in commits:
        commit_obj = repo.commit(c)
        msg = commit_obj.message
        if isinstance(msg, bytes):
            msg = msg.decode("utf-8")
        commit_info.append(msg.strip())

    prompt = f"""Write a git commit message summarizing these changes. Be specific about what was actually changed.

Individual commits:
{chr(10).join(f"- {m}" for m in commit_info)}

Files changed:
{diff}

Output ONLY the commit message—no preamble, no explanation. First line under 72 chars, then blank line, then brief body if needed.
"""

    cmd = ["opencode", "run", prompt, "-m", DEFAULT_MODEL]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Clean up the output
        message = result.stdout.strip()
        # Strip markdown code blocks if present
        if message.startswith("```") and message.endswith("```"):
            lines = message.split("\n")
            # Remove first and last lines (the ``` markers)
            message = "\n".join(lines[1:-1]).strip()
        if message:
            return message
    except Exception:
        pass

    return None
