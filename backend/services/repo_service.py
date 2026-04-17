import os
import shutil
from git import Repo
import git
from backend.utils.logger import get_logger
from backend.utils.helpers import ensure_dir
from backend.config import settings

logger = get_logger(__name__)

def clone_repo(repo_url: str, report_id: str) -> str:
    """Clones a github repo to a temporary directory."""
    ensure_dir(settings.temp_repos_dir)
    target_dir = os.path.join(settings.temp_repos_dir, report_id)
    
    logger.info(f"Cloning {repo_url} into {target_dir}")
    try:
        Repo.clone_from(repo_url, target_dir, multi_options=["-c", "core.longpaths=true"], allow_unsafe_options=True)
        logger.info(f"Successfully cloned {repo_url}")
        return target_dir
    except git.exc.GitCommandError as e:
        logger.error(f"Failed to clone repo: {e}")
        raise ValueError(f"Failed to clone repository: {str(e)}")

def cleanup_repo(target_dir: str):
    """Deletes the temporary repository directory."""
    if os.path.exists(target_dir):
        logger.info(f"Cleaning up {target_dir}")
        shutil.rmtree(target_dir, ignore_errors=True)
