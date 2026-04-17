import os
from typing import List

def get_python_files(repo_path: str) -> List[str]:
    """Recursively finds all Python files in the given directory."""
    python_files = []
    for root, _, files in os.walk(repo_path):
        # Ignore common non-source directories
        if '/.' in root.replace('\\', '/') or 'venv' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files
