import ast
from typing import Dict, List, Set

class RepoAstVisitor(ast.NodeVisitor):
    def __init__(self):
        self.defined_functions: Dict[str, dict] = {} # name -> {name, line}
        self.called_functions: Set[str] = set()
        self.imported_modules: Dict[str, dict] = {} # module_name -> {name, line}
        self.imported_names: Dict[str, dict] = {} # specific_name -> {name, line}

    def visit_FunctionDef(self, node):
        if not node.name.startswith('__'):
            self.defined_functions[node.name] = {
                'name': node.name,
                'line': node.lineno
            }
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.called_functions.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.called_functions.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called_functions.add(node.func.attr)
        self.generic_visit(node)

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            # Split by dot to get the base module imported, or just store the full name.
            base_module = alias.name.split('.')[0]
            self.imported_modules[name] = {
                'name': alias.name,
                'alias': alias.asname,
                'base_module': base_module,
                'line': node.lineno
            }
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module if node.module else ""
        base_module = module.split('.')[0] if module else ""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imported_names[name] = {
                'name': alias.name,
                'module': module,
                'base_module': base_module,
                'line': node.lineno
            }
        self.generic_visit(node)

def parse_file(file_path: str) -> RepoAstVisitor:
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()
    tree = ast.parse(source, filename=file_path)
    visitor = RepoAstVisitor()
    visitor.visit(tree)
    return visitor
