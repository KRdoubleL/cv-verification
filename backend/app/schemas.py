from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    RECRUITER = "recruiter"
    VERIFIER = "verifier"
    ADMIN = "admin"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ClaimStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNCERTAIN = "UNCERTAIN"
    INCONSISTENT = "INCONSISTENT"
    PENDING = "PENDING"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    company: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class EmploymentBase(BaseModel):
    company_name: str
    position: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False
    description: Optional[str] = None

class EmploymentCreate(EmploymentBase):
    order: int = 0

class EmploymentUpdate(BaseModel):
    claim_status: ClaimStatus
    verification_note: Optional[str] = None
    verification_sources: Optional[List[str]] = None

class Employment(EmploymentBase):
    id: int
    candidate_id: int
    claim_status: ClaimStatus
    verification_note: Optional[str]
    verification_sources: Optional[List[str]]
    verified_at: Optional[datetime]
    order: int

    class Config:
        from_attributes = True

class EducationBase(BaseModel):
    institution: str
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_current: bool = False

class EducationCreate(EducationBase):
    order: int = 0

class EducationUpdate(BaseModel):
    claim_status: ClaimStatus
    verification_note: Optional[str] = None
    verification_sources: Optional[List[str]] = None

class Education(EducationBase):
    id: int
    candidate_id: int
    claim_status: ClaimStatus
    verification_note: Optional[str]
    verification_sources: Optional[List[str]]
    verified_at: Optional[datetime]
    order: int

    class Config:
        from_attributes = True

class CandidateBase(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None

class CandidateCreate(CandidateBase):
    employment_history: List[EmploymentCreate] = []
    education_history: List[EducationCreate] = []

class CandidateDetail(CandidateBase):
    id: int
    batch_id: int
    verification_status: VerificationStatus
    verifier_id: Optional[int]
    verified_at: Optional[datetime]
    created_at: datetime
    employment_history: List[Employment] = []
    education_history: List[Education] = []

    class Config:
        from_attributes = True

class CandidateBatchCreate(BaseModel):
    batch_name: str
    upload_type: str

class CandidateBatch(BaseModel):
    id: int
    batch_name: str
    recruiter_id: int
    upload_type: str
    status: VerificationStatus
    uploaded_at: datetime
    completed_at: Optional[datetime]
    total_candidates: int
    verified_count: int

    class Config:
        from_attributes = True

class CandidateBatchDetail(CandidateBatch):
    candidates: List[CandidateDetail] = []

class CSVUploadResponse(BaseModel):
    batch_id: int
    batch_name: str
    total_candidates: int
    message: str

class ReportGenerate(BaseModel):
    candidate_id: int

class ReportResponse(BaseModel):
    id: int
    candidate_id: int
    html_content: str
    generated_at: datetime

    class Config:
        from_attributes = True