import os
import fnmatch
from typing import List, Tuple
from pathlib import Path
from app.core.config import settings
from app.core.logging import logger

try:
    import pathspec
    HAS_PATHSPEC = True
except ImportError:
    HAS_PATHSPEC = False

# Directories and patterns to ignore by default
DEFAULT_IGNORED_DIRS = {
    ".git",
    ".svn",
    ".hg",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    "venv",
    ".venv",
    "env",
    ".env",
    "node_modules",
    "dist",
    "build",
    ".eggs",
    "site-packages",
    "migrations",
}

DEFAULT_IGNORED_PATTERNS = [
    "*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.dylib",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg", "*.webp",
    "*.mp4", "*.mp3", "*.wav", "*.zip", "*.tar", "*.gz", "*.7z",
    "*.pdf", "*.docx", "*.xlsx", "*.sqlite", "*.db", "*.bin"
]


def discover_python_files(repo_path: str) -> Tuple[List[str], int, int]:
    """
    Safely discovers all relevant Python source files in a repository.
    Respects .gitignore if present, skips virtualenvs and cache dirs,
    and applies size limits.

    Returns:
        Tuple of (list_of_relative_file_paths, total_files_count, total_lines_of_code)
    """
    base_path = Path(repo_path).resolve()
    if not base_path.exists() or not base_path.is_dir():
        logger.error(f"Repository path does not exist: {repo_path}")
        return [], 0, 0

    # Check for .gitignore
    gitignore_path = base_path / ".gitignore"
    spec = None
    git_ignore_patterns = []
    if gitignore_path.exists():
        try:
            with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                if HAS_PATHSPEC:
                    spec = pathspec.PathSpec.from_lines("gitwildmatch", lines)
                else:
                    git_ignore_patterns = [
                        line.strip() for line in lines
                        if line.strip() and not line.startswith("#")
                    ]
        except Exception as e:
            logger.warning(f"Error parsing .gitignore: {e}")

    discovered_files: List[str] = []
    total_lines = 0

    for root, dirs, files in os.walk(base_path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORED_DIRS and not d.startswith(".")]

        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(base_path).as_posix()

            # Ignore non-python files for Python MVP analysis
            if file_path.suffix.lower() != ".py":
                continue

            # Check gitignore
            if spec and spec.match_file(rel_path):
                continue
            elif git_ignore_patterns:
                if any(fnmatch.fnmatch(rel_path, pat) or fnmatch.fnmatch(file, pat) for pat in git_ignore_patterns):
                    continue

            # Check file size limit
            try:
                size_kb = file_path.stat().st_size / 1024
                if size_kb > settings.MAX_FILE_SIZE_KB:
                    logger.warning(f"Skipping oversized file {rel_path} ({size_kb:.1f} KB)")
                    continue
            except OSError:
                continue

            # Count lines
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = sum(1 for _ in f)
                    total_lines += lines
            except Exception:
                lines = 0

            discovered_files.append(rel_path)

            if len(discovered_files) >= settings.MAX_FILES_TO_ANALYZE:
                logger.info(f"Reached maximum file limit ({settings.MAX_FILES_TO_ANALYZE})")
                break
        
        if len(discovered_files) >= settings.MAX_FILES_TO_ANALYZE:
            break

    logger.info(f"Discovered {len(discovered_files)} Python files ({total_lines} total lines) in {repo_path}")
    return discovered_files, len(discovered_files), total_lines
