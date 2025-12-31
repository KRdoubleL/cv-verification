from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter()

@router.get("/pending", response_model=List[schemas.CandidateDetail])
def get_pending_candidates(
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidates = db.query(models.Candidate).filter(
        models.Candidate.verification_status == models.VerificationStatus.PENDING
    ).order_by(models.Candidate.created_at).all()
    
    return candidates

@router.post("/claim/{candidate_id}")
def claim_candidate(
    candidate_id: int,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.verification_status != models.VerificationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Candidate already claimed or completed")
    
    candidate.verification_status = models.VerificationStatus.IN_PROGRESS
    candidate.verifier_id = current_user.id
    db.commit()
    
    return {"message": "Candidate claimed successfully"}

@router.get("/my-queue", response_model=List[schemas.CandidateDetail])
def get_my_queue(
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidates = db.query(models.Candidate).filter(
        models.Candidate.verifier_id == current_user.id,
        models.Candidate.verification_status == models.VerificationStatus.IN_PROGRESS
    ).order_by(models.Candidate.created_at).all()
    
    return candidates

@router.put("/employment/{employment_id}")
def update_employment_verification(
    employment_id: int,
    update: schemas.EmploymentUpdate,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    employment = db.query(models.Employment).filter(models.Employment.id == employment_id).first()
    if not employment:
        raise HTTPException(status_code=404, detail="Employment not found")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.id == employment.candidate_id).first()
    if candidate.verifier_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
    
    employment.claim_status = update.claim_status
    employment.verification_note = update.verification_note
    employment.verification_sources = update.verification_sources
    employment.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(employment)
    
    return employment

@router.put("/education/{education_id}")
def update_education_verification(
    education_id: int,
    update: schemas.EducationUpdate,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    education = db.query(models.Education).filter(models.Education.id == education_id).first()
    if not education:
        raise HTTPException(status_code=404, detail="Education not found")
    
    candidate = db.query(models.Candidate).filter(models.Candidate.id == education.candidate_id).first()
    if candidate.verifier_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
    
    education.claim_status = update.claim_status
    education.verification_note = update.verification_note
    education.verification_sources = update.verification_sources
    education.verified_at = datetime.utcnow()
    
    db.commit()
    db.refresh(education)
    
    return education

@router.post("/complete/{candidate_id}")
def complete_verification(
    candidate_id: int,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.verifier_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your candidate")
    
    pending_employment = db.query(models.Employment).filter(
        models.Employment.candidate_id == candidate_id,
        models.Employment.claim_status == models.ClaimStatus.PENDING
    ).count()
    
    pending_education = db.query(models.Education).filter(
        models.Education.candidate_id == candidate_id,
        models.Education.claim_status == models.ClaimStatus.PENDING
    ).count()
    
    if pending_employment > 0 or pending_education > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete: {pending_employment} employment and {pending_education} education entries still pending"
        )
    
    candidate.verification_status = models.VerificationStatus.COMPLETED
    candidate.verified_at = datetime.utcnow()
    
    batch = db.query(models.CandidateBatch).filter(models.CandidateBatch.id == candidate.batch_id).first()
    batch.verified_count = db.query(models.Candidate).filter(
        models.Candidate.batch_id == batch.id,
        models.Candidate.verification_status == models.VerificationStatus.COMPLETED
    ).count()
    
    if batch.verified_count == batch.total_candidates:
        batch.status = models.VerificationStatus.COMPLETED
        batch.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Verification completed successfully"}

@router.get("/stats")
def get_verification_stats(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == models.UserRole.VERIFIER:
        total_verified = db.query(models.Candidate).filter(
            models.Candidate.verifier_id == current_user.id,
            models.Candidate.verification_status == models.VerificationStatus.COMPLETED
        ).count()
        
        in_progress = db.query(models.Candidate).filter(
            models.Candidate.verifier_id == current_user.id,
            models.Candidate.verification_status == models.VerificationStatus.IN_PROGRESS
        ).count()
        
        return {
            "total_verified": total_verified,
            "in_progress": in_progress,
            "available": db.query(models.Candidate).filter(
                models.Candidate.verification_status == models.VerificationStatus.PENDING
            ).count()
        }
    
    elif current_user.role == models.UserRole.RECRUITER:
        batches = db.query(models.CandidateBatch).filter(
            models.CandidateBatch.recruiter_id == current_user.id
        ).all()
        
        total_candidates = sum(b.total_candidates for b in batches)
        verified_candidates = sum(b.verified_count for b in batches)
        
        return {
            "total_batches": len(batches),
            "total_candidates": total_candidates,
            "verified_candidates": verified_candidates,
            "pending_candidates": total_candidates - verified_candidates
        }
    
    return {}