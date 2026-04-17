REPORT_TEMPLATE = """# RepoDoctor AI Analysis Report

**Repository URL:** {repo_url}
**Report ID:** {report_id}

## Summary

* **Dead Code Functions:** {dead_code_count}
* **Unused Imports:** {unused_import_count}
* **Unused Dependencies:** {unused_dep_count}

## 🗑️ Dead Code Detection

{dead_code_section}

## 📦 Unused Imports

{unused_imports_section}

## 📚 Unused Dependencies

{unused_dependencies_section}

## 🤖 AI Suggestions

{ai_suggestions}
"""
