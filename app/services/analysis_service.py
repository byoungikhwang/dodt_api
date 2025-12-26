import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import silhouette_score
from fastapi import UploadFile
import io
import json
import random
import uuid
import os
from typing import List

from app.config.settings import settings
from app.repositories.users_repository import UserRepository
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.style_log_repository import StyleLogRepository

class AnalysisService:
    def __init__(
        self, 
        user_repo: UserRepository, 
        analysis_repo: AnalysisRepository,
        style_log_repo: StyleLogRepository
    ):
        self.user_repo = user_repo
        self.analysis_repo = analysis_repo
        self.style_log_repo = style_log_repo
        
    async def process_csv(self, file: UploadFile, user: dict):
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)

        # Save file
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
        df = pd.read_csv(io.BytesIO(content))
        
        # Basic Preprocessing
        df = df.fillna(0)
        label_encoders = {}
        for column in df.select_dtypes(include=['object']).columns:
            if column != 'user_id':
                le = LabelEncoder()
                df[column] = le.fit_transform(df[column].astype(str))
                label_encoders[column] = le
        
        features = df.select_dtypes(include=['number'])
        if 'user_id' in features.columns:
            features = features.drop('user_id', axis=1)
            
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features)
        
        # Clustering
        best_k = 3
        best_score = -1
        for k in range(3, 8):
            if len(df) < k: break
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(scaled_features)
            score = silhouette_score(scaled_features, labels)
            if score > best_score:
                best_score = score
                best_k = k
        
        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(scaled_features)
        
        # Generate Personas
        personas = []
        for i in range(best_k):
            cluster_data = df[df['cluster'] == i]
            size = len(cluster_data)
            personas.append({
                "id": i,
                "name": f"Persona Type {i+1}",
                "summary": f"This group represents {size} users with distinct behaviors.",
                "features": cluster_data.mean(numeric_only=True).to_dict(),
                "motivation": "Value for money" if i % 2 == 0 else "Premium quality",
                "risk_signal": "High churn risk" if size < len(df)/best_k else "Loyal",
                "content_preference": "Email newsletters" if i % 2 == 0 else "Social media ads"
            })
            
        result = {
            "clusters": best_k,
            "personas": personas,
            "total_users": len(df)
        }

        # Save to DB via repository
        if user and "sub" in user:
            await self.analysis_repo.create_analysis_result(
                user_id=int(user["sub"]),
                filename=file.filename,
                filelink=f"/static/files/{unique_filename}",
                result=result
            )
            
        return result

    async def simulate_message(self, message: str, personas: list):
        # Mock simulation
        results = []
        for p in personas:
            sentiment = random.choice(["Positive", "Neutral", "Negative"])
            results.append({
                "persona_id": p["id"],
                "reaction": sentiment,
                "reason": f"The message aligns with their motivation: {p.get('motivation', 'Unknown')}",
                "suggestion": "Make it shorter" if sentiment == "Negative" else "Good to go"
            })
        return results

    async def get_all_analysis_results(self) -> List[dict]:
        """
        Fetches all analysis results and enriches them with user email.
        """
        raw_results = await self.analysis_repo.get_all_analysis_results()
        enriched_results = []
        for result in raw_results:
            user_email = await self.user_repo.get_user_email_by_id(result["user_id"])
            enriched_result = dict(result)
            enriched_result["user_email"] = user_email if user_email else "Unknown User"
            enriched_results.append(enriched_result)
        return enriched_results

    async def get_all_style_logs(self) -> List[dict]:
        """
        Fetches all style logs.
        """
        logs = await self.style_log_repo.get_all_style_logs()
        return [dict(log) for log in logs]