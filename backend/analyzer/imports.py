from typing import Dict, List

def find_unused_imports(parsed_files: Dict[str, 'RepoAstVisitor']) -> List[dict]:
    """
    Finds imports that are declared but never used in the same file.
    """
    unused_imports = []

    for file_path, visitor in parsed_files.items():
        used_names = visitor.called_functions # this now contains all loaded names
        
        # Check standard imports (import X)
        for import_name, info in visitor.imported_modules.items():
            if import_name not in used_names:
                unused_imports.append({
                    'file_path': file_path,
                    'import_name': info['name'],
                    'line_number': info['line']
                })
                
        # Check from imports (from X import Y)
        for import_name, info in visitor.imported_names.items():
            if import_name not in used_names:
                unused_imports.append({
                    'file_path': file_path,
                    'import_name': f"{info['module']}.{info['name']}" if info['module'] else info['name'],
                    'line_number': info['line']
                })

    return unused_imports
