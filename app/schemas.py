# app/schemas.py
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, List
from datetime import date, datetime

# ===============================================
# User Schemas
# ===============================================

class UserBase(BaseModel):
    """
    모든 User 모델이 공통으로 가지는 기본 필드
    """
    email: EmailStr
    custom_id: str
    name: Optional[str] = None
    picture: Optional[HttpUrl] = None
    role: str = "MEMBER"

class UserCreate(UserBase):
    """
    사용자 생성 시 필요한 데이터. UserBase를 상속받음.
    """
    pass

class UserUpdate(BaseModel):
    """
    사용자 정보 수정 시 필요한 데이터. 모든 필드는 선택적.
    """
    name: Optional[str] = None
    role: Optional[str] = None
    credits: Optional[int] = None

class UserInDB(UserBase):
    """
    데이터베이스에 저장된 완전한 사용자 정보
    """
    id: int
    credits: int
    last_credit_grant_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # FastAPI 1.0.0 이전 버전에서는 orm_mode = True

class User(UserInDB):
    """
    API 응답으로 클라이언트에게 노출될 사용자 정보
    """
    pass


# ===============================================
# Analysis Result Schemas
# ===============================================

class AnalysisResultBase(BaseModel):
    """
    분석 결과의 기본 필드
    """
    user_id: int
    # 분석 결과 데이터는 JSON 형태로 가정
    result_data: Optional[dict] = None

class AnalysisResultCreate(AnalysisResultBase):
    """
    분석 결과 생성 시 필요한 데이터
    """
    pass

class AnalysisResultInDB(AnalysisResultBase):
    """
    데이터베이스에 저장된 완전한 분석 결과 정보
    """
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisResult(AnalysisResultInDB):
    """
    API 응답으로 클라이언트에게 노출될 분석 결과 정보
    """
    pass
