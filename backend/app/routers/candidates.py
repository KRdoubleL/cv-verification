from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import uuid

from ..database import get_db
from .. import models, schemas, auth
from ..utils.csv_parser import parse_csv_candidates
from ..utils.pdf_parser import parse_pdf_cv

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload/csv", response_model=schemas.CSVUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    batch_name: str = Form(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.RECRUITER, models.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only recruiters can upload candidates")

    contents = await file.read()

    try:
        candidates_data = parse_csv_candidates(contents)

        batch = models.CandidateBatch(
            batch_name=batch_name,
            recruiter_id=current_user.id,
            upload_type="csv",
            total_candidates=len(candidates_data)
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        for candidate_data in candidates_data:
            candidate = models.Candidate(
                batch_id=batch.id,
                full_name=candidate_data["full_name"],
                email=candidate_data.get("email"),
                phone=candidate_data.get("phone"),
                linkedin_url=candidate_data.get("linkedin_url"),
                raw_cv_data=candidate_data,
                parsed_cv_data=candidate_data
            )
            db.add(candidate)
            db.flush()

            for i, emp in enumerate(candidate_data.get("employment", [])):
                employment = models.Employment(
                    candidate_id=candidate.id,
                    company_name=emp.get("company", "Unknown"),
                    position=emp.get("position", "Unknown"),
                    start_date=emp.get("start_date"),
                    end_date=emp.get("end_date"),
                    is_current=emp.get("is_current", False),
                    description=emp.get("description"),
                    order=i
                )
                db.add(employment)

            for i, edu in enumerate(candidate_data.get("education", [])):
                education = models.Education(
                    candidate_id=candidate.id,
                    institution=edu.get("institution", "Unknown"),
                    degree=edu.get("degree"),
                    field_of_study=edu.get("field"),
                    start_date=edu.get("start_date"),
                    end_date=edu.get("end_date"),
                    order=i
                )
                db.add(education)

        db.commit()

        return {
            "batch_id": batch.id,
            "batch_name": batch.batch_name,
            "total_candidates": batch.total_candidates,
            "message": f"Successfully uploaded {batch.total_candidates} candidates"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing CSV: {str(e)}")


@router.post("/upload/pdf", response_model=schemas.PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    batch_name: str = Form(...),
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [models.UserRole.RECRUITER, models.UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only recruiters can upload candidates")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    contents = await file.read()

    try:
        # Save PDF to disk
        file_id = str(uuid.uuid4())
        pdf_filename = f"{file_id}_{file.filename}"
        pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)

        with open(pdf_path, "wb") as f:
            f.write(contents)

        # Parse with OpenAI
        candidate_data = parse_pdf_cv(contents)

        batch = models.CandidateBatch(
            batch_name=batch_name,
            recruiter_id=current_user.id,
            upload_type="pdf",
            total_candidates=1
        )
        db.add(batch)
        db.commit()
        db.refresh(batch)

        candidate = models.Candidate(
            batch_id=batch.id,
            full_name=candidate_data.get("full_name", "Unknown"),
            email=candidate_data.get("email"),
            phone=candidate_data.get("phone"),
            linkedin_url=candidate_data.get("linkedin_url"),
            raw_cv_data=candidate_data,
            parsed_cv_data=candidate_data,
            pdf_path=pdf_path,
            change_score=100
        )
        db.add(candidate)
        db.flush()

        for i, emp in enumerate(candidate_data.get("employment", [])):
            employment = models.Employment(
                candidate_id=candidate.id,
                company_name=emp.get("company", "Unknown"),
                position=emp.get("position", "Unknown"),
                start_date=emp.get("start_date"),
                end_date=emp.get("end_date"),
                is_current=emp.get("is_current", False),
                description=emp.get("description"),
                order=i
            )
            db.add(employment)

        for i, edu in enumerate(candidate_data.get("education", [])):
            education = models.Education(
                candidate_id=candidate.id,
                institution=edu.get("institution", "Unknown"),
                degree=edu.get("degree"),
                field_of_study=edu.get("field"),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
                order=i
            )
            db.add(education)

        db.commit()
        db.refresh(candidate)

        return {
            "batch_id": batch.id,
            "batch_name": batch.batch_name,
            "candidate_id": candidate.id,
            "candidate_name": candidate.full_name,
            "message": f"Successfully uploaded and parsed CV for {candidate.full_name}"
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")


@router.get("/pdf/{candidate_id}")
def get_candidate_pdf(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if not candidate.pdf_path or not os.path.exists(candidate.pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        candidate.pdf_path,
        media_type="application/pdf",
        filename=f"{candidate.full_name}_cv.pdf"
    )


@router.get("/batches", response_model=List[schemas.CandidateBatch])
def get_batches(
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    if current_user.role == models.UserRole.RECRUITER:
        batches = db.query(models.CandidateBatch).filter(
            models.CandidateBatch.recruiter_id == current_user.id
        ).order_by(models.CandidateBatch.uploaded_at.desc()).all()
    else:
        batches = db.query(models.CandidateBatch).order_by(
            models.CandidateBatch.uploaded_at.desc()
        ).all()
    return batches


@router.get("/batch/{batch_id}", response_model=schemas.CandidateBatchDetail)
def get_batch(
    batch_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    batch = db.query(models.CandidateBatch).filter(models.CandidateBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    if current_user.role == models.UserRole.RECRUITER and batch.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this batch")

    return batch


@router.get("/{candidate_id}", response_model=schemas.CandidateDetail)
def get_candidate(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


@router.delete("/{candidate_id}")
def delete_candidate(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    # Only recruiter who owns the batch or admin can delete
    batch = db.query(models.CandidateBatch).filter(models.CandidateBatch.id == candidate.batch_id).first()
    if current_user.role == models.UserRole.RECRUITER and batch.recruiter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Delete PDF file from disk
    if candidate.pdf_path and os.path.exists(candidate.pdf_path):
        os.remove(candidate.pdf_path)

    db.delete(candidate)
    db.commit()
    return {"message": "Candidate deleted successfully"}