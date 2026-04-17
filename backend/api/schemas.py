from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional

class AnalyzeRequest(BaseModel):
    repo_url: HttpUrl

class AnalyzeResponse(BaseModel):
    report_id: str
    message: str

class ErrorResponse(BaseModel):
    detail: str

# Internal Models for Analysis
class DeadCodeItem(BaseModel):
    file_path: str
    function_name: str
    line_number: int

class UnusedImportItem(BaseModel):
    file_path: str
    import_name: str
    line_number: int

class AnalysisResult(BaseModel):
    repo_url: str
    dead_code: List[DeadCodeItem]
    unused_imports: List[UnusedImportItem]
    unused_dependencies: List[str]
    ai_suggestions: Optional[str] = None
