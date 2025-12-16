import logging # 로깅 임포트 추가
import google.generativeai as genai
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.config.settings import settings # settings 임포트 추가

router = APIRouter()

logger = logging.getLogger(__name__) # 로거 인스턴스 생성

GEMINI_API_KEY = settings.GEMINI_API_KEY # settings 사용
MODEL_NAME = settings.GOOGLE_GEMINI_MODEL_NAME # settings 사용

# Gemini 설정 초기화
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# --- 데이터 모델 ---
class StyleRequest(BaseModel):
    user_id: str
    prompt: str
    gender: str

# --- Gemini AI 로직 함수 ---
def generate_fashion_prompt(user_prompt: str, gender: str) -> str:
    if not GEMINI_API_KEY:
        return "Error: API Key missing in .env"

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        system_instruction = f"""
        You are a professional fashion photographer's assistant.
        Convert the following user request into a detailed image generation prompt.
        Target: {gender} model.
        Style: {user_prompt}
        Output: A single paragraph, high-quality description suitable for Stable Diffusion.
        """
        response = model.generate_content(system_instruction)
        return response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        return f"Error generating prompt: {str(e)}"

# --- 백그라운드 작업 함수 ---
def process_style_generation(data: StyleRequest):
    logger.info(f"🔄 Processing background task for user: {data.user_id}")
    final_prompt = generate_fashion_prompt(data.prompt, data.gender)
    logger.info(f"✨ Gemini Result: {final_prompt}")
    # TODO: DB 저장 로직 추가 (app/services/.. 활용)
    # 예: INSERT INTO style_logs ...
    logger.info("✅ Background task completed.")

# --- API 엔드포인트 ---
@router.post("/api/v1/recommend")
async def recommend_style(request: StyleRequest, background_tasks: BackgroundTasks):
    """
    n8n 요청 수신 -> 백그라운드 작업 등록 -> 즉시 응답
    """
    background_tasks.add_task(process_style_generation, request)
    return {
        "status": "queued",
        "message": "Style generation started",
        "user_id": request.user_id
    }