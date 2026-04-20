from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter()

def recalculate_change_score(candidate_id: int, db: Session) -> int:
    checks = db.query(models.SectionCheck).filter(
        models.SectionCheck.candidate_id == candidate_id
    ).all()
    if not checks:
        return 100
    changed = sum(1 for c in checks if c.status == models.SectionStatus.CHANGED)
    total = len(checks)
    score = int(((total - changed) / total) * 100)
    return score

@router.get("/pending", response_model=List[schemas.CandidateDetail])
def get_pending_candidates(
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidates = db.query(models.Candidate).filter(
        models.Candidate.verification_status == models.VerificationStatus.PENDING
    ).order_by(models.Candidate.created_at).all()
    return candidates

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

@router.post("/claim/{candidate_id}")
def claim_candidate(
    candidate_id: int,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.verification_status = models.VerificationStatus.IN_PROGRESS
    candidate.verifier_id = current_user.id
    db.commit()
    return {"message": "Candidate claimed"}

@router.get("/sections/{candidate_id}")
def get_section_checks(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    checks = db.query(models.SectionCheck).filter(
        models.SectionCheck.candidate_id == candidate_id
    ).all()
    result = []
    for c in checks:
        result.append({
            "id": c.id,
            "section_type": c.section_type.value,
            "section_ref_id": c.section_ref_id,
            "status": c.status.value,
            "checked_at": c.checked_at.isoformat() if c.checked_at else None,
            "checked_by": c.checked_by.full_name if c.checked_by else None,
            "note": c.note,
            "change_history": c.change_history or []
        })
    return result

@router.post("/sections/{candidate_id}/check")
def mark_section_checked(
    candidate_id: int,
    body: dict,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    section_type = body.get("section_type")
    section_ref_id = body.get("section_ref_id")
    note = body.get("note", "")

    existing = db.query(models.SectionCheck).filter(
        models.SectionCheck.candidate_id == candidate_id,
        models.SectionCheck.section_type == models.SectionType(section_type),
        models.SectionCheck.section_ref_id == section_ref_id
    ).first()

    if existing:
        existing.status = models.SectionStatus.CHECKED
        existing.checked_at = datetime.utcnow()
        existing.checked_by_id = current_user.id
        existing.note = note
    else:
        check = models.SectionCheck(
            candidate_id=candidate_id,
            section_type=models.SectionType(section_type),
            section_ref_id=section_ref_id,
            status=models.SectionStatus.CHECKED,
            checked_at=datetime.utcnow(),
            checked_by_id=current_user.id,
            note=note,
            change_history=[]
        )
        db.add(check)

    db.commit()
    return {"message": "Section marked as checked"}

@router.post("/sections/{candidate_id}/change")
def mark_section_changed(
    candidate_id: int,
    body: dict,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    section_type = body.get("section_type")
    section_ref_id = body.get("section_ref_id")
    old_value = body.get("old_value", "")
    new_value = body.get("new_value", "")
    note = body.get("note", "")

    existing = db.query(models.SectionCheck).filter(
        models.SectionCheck.candidate_id == candidate_id,
        models.SectionCheck.section_type == models.SectionType(section_type),
        models.SectionCheck.section_ref_id == section_ref_id
    ).first()

    history_entry = {
        "date": datetime.utcnow().isoformat(),
        "checked_by": current_user.full_name,
        "old_value": old_value,
        "new_value": new_value,
        "note": note
    }

    if existing:
        history = existing.change_history or []
        history.append(history_entry)
        existing.change_history = history
        existing.status = models.SectionStatus.CHANGED
        existing.checked_at = datetime.utcnow()
        existing.checked_by_id = current_user.id
        existing.note = note
    else:
        check = models.SectionCheck(
            candidate_id=candidate_id,
            section_type=models.SectionType(section_type),
            section_ref_id=section_ref_id,
            status=models.SectionStatus.CHANGED,
            checked_at=datetime.utcnow(),
            checked_by_id=current_user.id,
            note=note,
            change_history=[history_entry]
        )
        db.add(check)

    db.commit()

    score = recalculate_change_score(candidate_id, db)
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    candidate.change_score = score
    db.commit()

    return {"message": "Section marked as changed", "new_score": score}

@router.post("/complete/{candidate_id}")
def complete_verification(
    candidate_id: int,
    current_user: models.User = Depends(auth.require_role([models.UserRole.VERIFIER, models.UserRole.ADMIN])),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    candidate.verification_status = models.VerificationStatus.COMPLETED
    candidate.verified_at = datetime.utcnow()
    db.commit()
    return {"message": "Verification completed"}

@router.get("/stats")
def get_verification_stats(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == models.UserRole.VERIFIER:
        return {
            "total_verified": db.query(models.Candidate).filter(
                models.Candidate.verifier_id == current_user.id,
                models.Candidate.verification_status == models.VerificationStatus.COMPLETED
            ).count(),
            "in_progress": db.query(models.Candidate).filter(
                models.Candidate.verifier_id == current_user.id,
                models.Candidate.verification_status == models.VerificationStatus.IN_PROGRESS
            ).count(),
            "available": db.query(models.Candidate).filter(
                models.Candidate.verification_status == models.VerificationStatus.PENDING
            ).count()
        }
    batches = db.query(models.CandidateBatch).filter(
        models.CandidateBatch.recruiter_id == current_user.id
    ).all()
    total = sum(b.total_candidates for b in batches)
    verified = sum(b.verified_count for b in batches)
    return {
        "total_batches": len(batches),
        "total_candidates": total,
        "verified_candidates": verified,
        "pending_candidates": total - verified
    }