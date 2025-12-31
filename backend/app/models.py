from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class UserRole(enum.Enum):
    RECRUITER = "recruiter"
    VERIFIER = "verifier"
    ADMIN = "admin"

class VerificationStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class ClaimStatus(enum.Enum):
    VERIFIED = "VERIFIED"
    UNCERTAIN = "UNCERTAIN"
    INCONSISTENT = "INCONSISTENT"
    PENDING = "PENDING"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    company = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    uploaded_batches = relationship("CandidateBatch", back_populates="recruiter", foreign_keys="CandidateBatch.recruiter_id")
    verified_candidates = relationship("Candidate", back_populates="verifier", foreign_keys="Candidate.verifier_id")

class CandidateBatch(Base):
    __tablename__ = "candidate_batches"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_name = Column(String, nullable=False)
    recruiter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    upload_type = Column(String, nullable=False)
    status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    total_candidates = Column(Integer, default=0)
    verified_count = Column(Integer, default=0)
    
    recruiter = relationship("User", back_populates="uploaded_batches", foreign_keys=[recruiter_id])
    candidates = relationship("Candidate", back_populates="batch", cascade="all, delete-orphan")

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("candidate_batches.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    linkedin_url = Column(String, nullable=True)
    raw_cv_data = Column(JSON, nullable=True)
    verifier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verification_status = Column(Enum(VerificationStatus), default=VerificationStatus.PENDING)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    batch = relationship("CandidateBatch", back_populates="candidates")
    verifier = relationship("User", back_populates="verified_candidates", foreign_keys=[verifier_id])
    employment_history = relationship("Employment", back_populates="candidate", cascade="all, delete-orphan")
    education_history = relationship("Education", back_populates="candidate", cascade="all, delete-orphan")

class Employment(Base):
    __tablename__ = "employment"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    company_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    is_current = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    claim_status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    verification_note = Column(Text, nullable=True)
    verification_sources = Column(JSON, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    order = Column(Integer, default=0)
    
    candidate = relationship("Candidate", back_populates="employment_history")

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=True)
    field_of_study = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    is_current = Column(Boolean, default=False)
    claim_status = Column(Enum(ClaimStatus), default=ClaimStatus.PENDING)
    verification_note = Column(Text, nullable=True)
    verification_sources = Column(JSON, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    order = Column(Integer, default=0)
    
    candidate = relationship("Candidate", back_populates="education_history")

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    html_content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    candidate = relationship("Candidate")
    generator = relationship("User")