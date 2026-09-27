from fastapi import FastAPI
from pydantic import BaseModel, Field
from src.pipeline import analyze_resume_job

app = FastAPI(title="TalentLens AI API", version="1.0.0")

class AnalyzeRequest(BaseModel):
    resume_text: str = Field(min_length=100)
    job_text: str = Field(min_length=50)

@app.get("/health")
def health():
    return {"status": "ok", "service": "TalentLens AI"}

@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    return analyze_resume_job(request.resume_text, request.job_text)
