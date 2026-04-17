import os
from backend.services.repo_service import clone_repo, cleanup_repo
from backend.analyzer.file_scanner import get_python_files
from backend.analyzer.ast_parser import parse_file
from backend.analyzer.dead_code import find_dead_functions
from backend.analyzer.imports import find_unused_imports
from backend.analyzer.dependencies import find_unused_dependencies
from backend.services.ai_service import generate_suggestions
from backend.api.schemas import AnalysisResult, DeadCodeItem, UnusedImportItem
from backend.utils.logger import get_logger

logger = get_logger(__name__)

async def run_analysis(repo_url: str, report_id: str) -> AnalysisResult:
    target_dir = ""
    try:
        # Step 1: Clone repo
        target_dir = clone_repo(repo_url, report_id)
        
        # Step 2: Scan for Python files
        py_files = get_python_files(target_dir)
        logger.info(f"Found {len(py_files)} Python files")
        
        # Step 3: Parse ASTs
        parsed_files = {}
        for f in py_files:
            try:
                parsed_files[f] = parse_file(f)
            except Exception as e:
                logger.error(f"Error parsing file {f}: {e}")
        
        # Step 4: Detect Issues
        dead_functions = find_dead_functions(parsed_files)
        unused_imports = find_unused_imports(parsed_files)
        unused_deps = find_unused_dependencies(target_dir, parsed_files)
        
        # Prepare result with relative paths instead of absolute
        def make_relative(path: str) -> str:
            return os.path.relpath(path, target_dir)
        
        dc_items = [
            DeadCodeItem(
                file_path=make_relative(x['file_path']), 
                function_name=x['function_name'], 
                line_number=x['line_number']
            ) for x in dead_functions
        ]
        
        ui_items = [
            UnusedImportItem(
                file_path=make_relative(x['file_path']),
                import_name=x['import_name'],
                line_number=x['line_number']
            ) for x in unused_imports
        ]
        
        result = AnalysisResult(
            repo_url=repo_url,
            dead_code=dc_items,
            unused_imports=ui_items,
            unused_dependencies=unused_deps
        )
        
        # Step 5: AI Suggestions
        result.ai_suggestions = generate_suggestions(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise e
    finally:
        if target_dir:
            cleanup_repo(target_dir)
