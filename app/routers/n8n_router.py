from fastapi import APIRouter, Depends
from starlette.requests import Request
import logging

# 로거 설정
logger = logging.getLogger(__name__)

# APIRouter 인스턴스 생성
router = APIRouter(
    prefix="/api/v1/n8n",
    tags=["n8n"]
)

@router.post("/trigger")
async def n8n_trigger(request: Request):
    """
    n8n 워크플로우에서 호출할 수 있는 샘플 엔드포인트입니다.
    POST 요청으로 받은 데이터를 로깅하고 성공 메시지를 반환합니다.
    """
    logger.info("Received a trigger from n8n.")
    
    # n8n에서 보낸 데이터 본문을 비동기적으로 읽습니다.
    try:
        data = await request.json()
        logger.info(f"Data from n8n: {data}")
        # 여기에 n8n 요청에 대한 응답으로 수행할 비즈니스 로직을 추가할 수 있습니다.
        # 예를 들어, 특정 서비스를 호출하거나 데이터베이스 작업을 수행할 수 있습니다.
        return {"status": "success", "message": "n8n trigger received successfully.", "received_data": data}
    except Exception as e:
        logger.error(f"Could not parse JSON from n8n trigger: {e}")
        return {"status": "error", "message": "Failed to parse JSON data."}

@router.get("/health-check")
async def n8n_health_check():
    """
    n8n 연동을 위한 간단한 상태 확인 엔드포인트입니다.
    """
    logger.info("n8n health check endpoint was called.")
    return {"status": "ok", "message": "n8n endpoint is healthy."}
