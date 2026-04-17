from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.api.schemas import AnalyzeRequest, AnalyzeResponse, AnalysisResult
from backend.services.analysis_service import run_analysis
from backend.report.generator import generate_markdown_report, save_report, get_report
from backend.utils.helpers import generate_report_id
from backend.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_repo(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    report_id = generate_report_id()
    repo_url = str(request.repo_url)
    
    # We could do this in the background, but the requirements just say it should return the result or report ID.
    # We will do it synchronously for simplicity so the front-end can immediately get the response, or 
    # we could return the ID immediately and let it generate in background. The prompt says "output: analysis result or report ID".
    # Since it's an AI task that takes time, generating and returning the ID immediately is better for production.
    
    def process_analysis(url: str, r_id: str):
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(run_analysis(url, r_id))
            report_content = generate_markdown_report(result, r_id)
            save_report(r_id, report_content)
            logger.info(f"Report {r_id} generation complete.")
        except Exception as e:
            logger.error(f"Failed to generate report {r_id}: {e}")
            # Could save an error report here
            save_report(r_id, f"# Error Analysis Failed\n\nError: {str(e)}")
        finally:
            loop.close()

    background_tasks.add_task(process_analysis, repo_url, report_id)
    
    return AnalyzeResponse(
        report_id=report_id,
        message="Analysis started in the background. Please check the report endpoint later with this ID."
    )

@router.get("/report/{report_id}", responses={
    200: {
        "content": {"text/markdown": {}}
    }
})
async def retrieve_report(report_id: str):
    content = get_report(report_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Report not found or still generating.")
    
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content, media_type="text/markdown")
