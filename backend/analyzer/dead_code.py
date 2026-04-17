from typing import Dict, List, Set

def find_dead_functions(parsed_files: Dict[str, 'RepoAstVisitor']) -> List[dict]:
    """
    Finds functions that are defined but never called across the entire repository.
    """
    all_defined = {}
    all_called = set()

    # Aggregate definitions and calls
    for file_path, visitor in parsed_files.items():
        for func_name, func_info in visitor.defined_functions.items():
            if func_name not in all_defined:
                all_defined[func_name] = []
            all_defined[func_name].append({
                'file_path': file_path,
                'function_name': func_name,
                'line_number': func_info['line']
            })
        
        all_called.update(visitor.called_functions)

    # Identifiers common in API frameworks that might be called implicitly (fastapi routes etc.)
    # We ignore simple dead code checks for them here, or just return everything purely AST based
    # A true system might ignore 'main', 'test_*', etc.
    
    dead_code = []
    for func_name, occurrences in all_defined.items():
        if func_name not in all_called:
            # We assume it's dead code if never explicitly called in the parsed AST.
            for occ in occurrences:
                dead_code.append(occ)

    return dead_code
