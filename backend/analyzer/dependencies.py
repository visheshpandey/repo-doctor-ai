import os
from typing import Dict, List, Set

# Some standard library modules to common ignore. Ideally we'd test against `sys.stdlib_module_names` if available.
# But for now, we just map what we find in requirements.txt to imports.

def get_requirements(repo_path: str) -> List[str]:
    req_path = os.path.join(repo_path, 'requirements.txt')
    if not os.path.exists(req_path):
        return []
    
    with open(req_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    deps = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # simple parse, ignoring ==, >= etc
            pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
            # typical mapping e.g., python-dotenv -> dotenv, GitPython -> git
            # for a basic prototype we just normalize to lower and replace - with _ optionally
            deps.append(pkg_name)
    return deps

def find_unused_dependencies(repo_path: str, parsed_files: Dict[str, 'RepoAstVisitor']) -> List[str]:
    declared_deps = get_requirements(repo_path)
    if not declared_deps:
        return []

    # Gather all base modules imported
    all_imported_bases = set()
    for visitor in parsed_files.values():
        for info in visitor.imported_modules.values():
            if info['base_module']:
                all_imported_bases.add(info['base_module'].lower())
        for info in visitor.imported_names.values():
            if info['base_module']:
                all_imported_bases.add(info['base_module'].lower())
                
    unused = []
    for dep in declared_deps:
        dep_normalized = dep.lower().replace('-', '_')
        # specific hardcoded mappings often needed
        mapping = {
            'python_dotenv': 'dotenv',
            'gitpython': 'git',
            'fastapi': 'fastapi',
            'uvicorn': 'uvicorn',
            'pydantic': 'pydantic'
        }
        actual_module = mapping.get(dep_normalized, dep_normalized)
        
        if actual_module not in all_imported_bases:
            # Maybe it provides CLI or is not imported directly (like uvicorn).
            # But according to rules, we report what is not imported.
            unused.append(dep)
            
    return unused
