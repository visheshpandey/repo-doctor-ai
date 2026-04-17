import os
from backend.api.schemas import AnalysisResult
from backend.report.templates import REPORT_TEMPLATE
from backend.config import settings
from backend.utils.helpers import ensure_dir

def generate_markdown_report(result: AnalysisResult, report_id: str) -> str:
    # Format Dead Code
    if result.dead_code:
        dead_code_section = "\n".join([f"- `{item.function_name}` in `{item.file_path}` (Line {item.line_number})" for item in result.dead_code])
    else:
        dead_code_section = "*No dead code detected.*"

    # Format Unused Imports
    if result.unused_imports:
        unused_imports_section = "\n".join([f"- `{item.import_name}` in `{item.file_path}` (Line {item.line_number})" for item in result.unused_imports])
    else:
        unused_imports_section = "*No unused imports detected.*"

    # Format Unused Dependencies
    if result.unused_dependencies:
        unused_dependencies_section = "\n".join([f"- `{dep}`" for dep in result.unused_dependencies])
    else:
        unused_dependencies_section = "*No unused dependencies detected.*"

    report_content = REPORT_TEMPLATE.format(
        repo_url=result.repo_url,
        report_id=report_id,
        dead_code_count=len(result.dead_code),
        unused_import_count=len(result.unused_imports),
        unused_dep_count=len(result.unused_dependencies),
        dead_code_section=dead_code_section,
        unused_imports_section=unused_imports_section,
        unused_dependencies_section=unused_dependencies_section,
        ai_suggestions=result.ai_suggestions or "*No AI suggestions generated.*"
    )

    return report_content

def save_report(report_id: str, content: str):
    ensure_dir(settings.reports_dir)
    filepath = os.path.join(settings.reports_dir, f"{report_id}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def get_report(report_id: str) -> str:
    filepath = os.path.join(settings.reports_dir, f"{report_id}.md")
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()
