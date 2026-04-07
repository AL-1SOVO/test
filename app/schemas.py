from pydantic import BaseModel
from typing import List


class ResumeAnalyzeRequest(BaseModel):
    resume_text: str


class JDAnalyzeRequest(BaseModel):
    jd_text: str


class ResumeMatchRequest(BaseModel):
    resume_text: str
    jd_text: str


class ResumeAnalyzeResponse(BaseModel):
    text_length: int
    skills: List[str]
    has_project_experience: bool
    has_education: bool
    suggestions: List[str]


class JDAnalyzeResponse(BaseModel):
    skill_keywords: List[str]
    experience_keywords: List[str]
    has_degree_requirement: bool
    job_direction: str


class ResumeMatchResponse(BaseModel):
    matched_keywords: List[str]
    missing_keywords: List[str]
    match_score: int
    suggestions: List[str]