"""Agent Loop - CLI tool for running LLM agents in iterative refinement loops."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("agent-loop")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
