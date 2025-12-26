from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.services.analysis_service import AnalysisService
from app.dependencies.auth import get_current_user
from app.dependencies.services import get_analysis_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a CSV file.")
    
    try:
        # The 'conn' argument is no longer passed to the service
        result = await analysis_service.process_csv(file, current_user)
        return result
    except Exception as e:
        # It's better to have more specific exception handling
        # and logging in a real application.
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-message")
async def simulate_message(
    payload: dict,
    # This endpoint does not require user authentication in this example
    # current_user: dict = Depends(get_current_user), 
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    # payload: {"message": "...", "personas": [...]}
    if "message" not in payload or "personas" not in payload:
        raise HTTPException(status_code=400, detail="Payload must include 'message' and 'personas'")
        
    return await analysis_service.simulate_message(payload["message"], payload["personas"])
