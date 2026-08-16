import os
import shutil
import tempfile
import re
from pathlib import Path
from typing import Tuple, Optional, Dict
import git
from app.core.config import settings
from app.core.logging import logger


class RepoService:
    """
    Manages cloning, sandboxing, metadata extraction, and cleanup of repositories.
    Never executes arbitrary repository code.
    """

    @staticmethod
    def is_local_path(url: str) -> bool:
        p = Path(url)
        return p.exists() and p.is_dir()

    @classmethod
    def clone_repository(cls, repo_url: str, branch: Optional[str] = "main") -> Tuple[str, str, str, str]:
        """
        Clones a remote GitHub/GitLab repository or validates a local repository path.

        Returns:
            Tuple of (local_dir_path, commit_hash, branch_name, repo_name)
        """
        # If local directory
        if cls.is_local_path(repo_url):
            local_path = str(Path(repo_url).resolve())
            repo_name = Path(local_path).name
            commit_hash = "local-snapshot"
            try:
                repo = git.Repo(local_path)
                commit_hash = repo.head.commit.hexsha[:8]
                branch = repo.active_branch.name
            except Exception:
                pass
            return local_path, commit_hash, branch or "main", repo_name

        # Parse repo name from URL (e.g., https://github.com/owner/repo-name -> repo-name)
        clean_url = repo_url.rstrip("/")
        if clean_url.endswith(".git"):
            clean_url = clean_url[:-4]
        repo_name = clean_url.split("/")[-1] or "repository"

        # Create temporary directory inside configured storage dir
        storage_base = Path(settings.STORAGE_DIR).resolve()
        storage_base.mkdir(parents=True, exist_ok=True)
        temp_dir = tempfile.mkdtemp(prefix=f"codeguard_{repo_name}_", dir=str(storage_base))

        logger.info(f"Cloning {repo_url} (branch: {branch}) into {temp_dir} with depth=1...")

        try:
            # Clone shallowly to save disk and memory
            clone_kwargs = {"depth": 1}
            if branch and branch != "main":
                clone_kwargs["branch"] = branch

            repo = git.Repo.clone_from(repo_url, temp_dir, **clone_kwargs)
            commit_hash = repo.head.commit.hexsha[:8]
            active_branch = branch or "main"
            try:
                active_branch = repo.active_branch.name
            except Exception:
                pass

            logger.info(f"Successfully cloned {repo_name} (commit {commit_hash})")
            return temp_dir, commit_hash, active_branch, repo_name

        except Exception as e:
            # If specified branch failed, try cloning default branch
            if branch and branch != "main":
                try:
                    logger.info(f"Retrying clone with default branch...")
                    repo = git.Repo.clone_from(repo_url, temp_dir, depth=1)
                    commit_hash = repo.head.commit.hexsha[:8]
                    return temp_dir, commit_hash, "default", repo_name
                except Exception as inner_e:
                    cls.cleanup_temp_dir(temp_dir)
                    raise RuntimeError(f"Failed to clone repository '{repo_url}': {inner_e}") from inner_e

            cls.cleanup_temp_dir(temp_dir)
            raise RuntimeError(f"Failed to clone repository '{repo_url}': {e}") from e

    @staticmethod
    def cleanup_temp_dir(temp_dir: str) -> None:
        """Removes the cloned temporary directory cleanly."""
        try:
            if temp_dir and Path(temp_dir).exists() and "codeguard_" in temp_dir:
                # Handle readonly git files on Windows
                def on_rm_error(func, path, exc_info):
                    try:
                        os.chmod(path, 0o777)
                        func(path)
                    except Exception:
                        pass

                shutil.rmtree(temp_dir, onerror=on_rm_error)
                logger.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logger.warning(f"Error during cleanup of {temp_dir}: {e}")
