from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter()

def generate_cv_html(candidate: models.Candidate, db: Session) -> str:
    status_config = {
        models.ClaimStatus.VERIFIED: {
            "icon": "✓",
            "color": "#22c55e",
            "bg": "#f0fdf4",
            "label": "Verified"
        },
        models.ClaimStatus.UNCERTAIN: {
            "icon": "?",
            "color": "#f59e0b",
            "bg": "#fffbeb",
            "label": "Uncertain"
        },
        models.ClaimStatus.INCONSISTENT: {
            "icon": "✗",
            "color": "#ef4444",
            "bg": "#fef2f2",
            "label": "Inconsistent"
        },
        models.ClaimStatus.PENDING: {
            "icon": "○",
            "color": "#9ca3af",
            "bg": "#f9fafb",
            "label": "Not Verified"
        }
    }
    
    employment = db.query(models.Employment).filter(
        models.Employment.candidate_id == candidate.id
    ).order_by(models.Employment.order).all()
    
    education = db.query(models.Education).filter(
        models.Education.candidate_id == candidate.id
    ).order_by(models.Education.order).all()
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verified CV - {candidate.full_name}</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #1f2937;
                background: #f9fafb;
                padding: 2rem;
            }}
            .container {{ 
                max-width: 850px;
                margin: 0 auto;
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                padding: 3rem;
            }}
            .header {{
                border-bottom: 3px solid #2563eb;
                padding-bottom: 2rem;
                margin-bottom: 2rem;
            }}
            .name {{ 
                font-size: 2.5rem;
                font-weight: 700;
                color: #111827;
                margin-bottom: 0.5rem;
            }}
            .contact {{
                color: #6b7280;
                font-size: 0.95rem;
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
            }}
            .contact a {{
                color: #2563eb;
                text-decoration: none;
            }}
            .section {{
                margin-bottom: 2.5rem;
            }}
            .section-title {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #111827;
                margin-bottom: 1.5rem;
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #e5e7eb;
            }}
            .entry {{
                margin-bottom: 1.5rem;
                padding: 1rem;
                border-radius: 8px;
                position: relative;
            }}
            .entry-header {{
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 0.5rem;
            }}
            .entry-title {{
                font-size: 1.1rem;
                font-weight: 600;
                color: #111827;
            }}
            .entry-subtitle {{
                font-size: 0.95rem;
                color: #4b5563;
                margin-bottom: 0.25rem;
            }}
            .entry-dates {{
                font-size: 0.875rem;
                color: #6b7280;
            }}
            .verification-badge {{
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
                padding: 0.375rem 0.75rem;
                border-radius: 6px;
                font-size: 0.875rem;
                font-weight: 500;
            }}
            .verification-icon {{
                font-weight: bold;
                font-size: 1rem;
            }}
            .verification-note {{
                margin-top: 0.75rem;
                padding: 0.75rem;
                background: #f9fafb;
                border-left: 3px solid #d1d5db;
                font-size: 0.875rem;
                color: #4b5563;
                border-radius: 4px;
            }}
            .legend {{
                margin-top: 3rem;
                padding: 1.5rem;
                background: #f9fafb;
                border-radius: 8px;
            }}
            .legend-title {{
                font-weight: 600;
                margin-bottom: 1rem;
                color: #111827;
            }}
            .legend-items {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 1rem;
            }}
            .legend-item {{
                display: flex;
                align-items: center;
                gap: 0.5rem;
                font-size: 0.875rem;
            }}
            .footer {{
                margin-top: 3rem;
                padding-top: 2rem;
                border-top: 1px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-size: 0.875rem;
            }}
            @media print {{
                body {{ padding: 0; background: white; }}
                .container {{ box-shadow: none; padding: 1.5rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 class="name">{candidate.full_name}</h1>
                <div class="contact">
                    {f'<span>✉ {candidate.email}</span>' if candidate.email else ''}
                    {f'<span>📞 {candidate.phone}</span>' if candidate.phone else ''}
                    {f'<span><a href="{candidate.linkedin_url}" target="_blank">🔗 LinkedIn</a></span>' if candidate.linkedin_url else ''}
                </div>
            </div>
    """
    
    if employment:
        html += """
            <div class="section">
                <h2 class="section-title">Professional Experience</h2>
        """
        
        for emp in employment:
            config = status_config[emp.claim_status]
            dates = f"{emp.start_date or 'Unknown'} - {emp.end_date or 'Present' if emp.is_current else emp.end_date or 'Unknown'}"
            
            html += f"""
                <div class="entry" style="background: {config['bg']}; border-left: 4px solid {config['color']};">
                    <div class="entry-header">
                        <div>
                            <div class="entry-title">{emp.position}</div>
                            <div class="entry-subtitle">{emp.company_name}</div>
                            <div class="entry-dates">{dates}</div>
                        </div>
                        <span class="verification-badge" style="background: {config['bg']}; color: {config['color']}; border: 1px solid {config['color']};">
                            <span class="verification-icon">{config['icon']}</span>
                            {config['label']}
                        </span>
                    </div>
            """
            
            if emp.description:
                html += f'<p style="margin-top: 0.75rem; color: #4b5563;">{emp.description}</p>'
            
            if emp.verification_note:
                html += f"""
                    <div class="verification-note">
                        <strong>Verification Note:</strong> {emp.verification_note}
                    </div>
                """
            
            html += "</div>"
        
        html += "</div>"
    
    if education:
        html += """
            <div class="section">
                <h2 class="section-title">Education</h2>
        """
        
        for edu in education:
            config = status_config[edu.claim_status]
            dates = f"{edu.start_date or 'Unknown'} - {edu.end_date or 'Present' if edu.is_current else edu.end_date or 'Unknown'}"
            
            html += f"""
                <div class="entry" style="background: {config['bg']}; border-left: 4px solid {config['color']};">
                    <div class="entry-header">
                        <div>
                            <div class="entry-title">{edu.institution}</div>
                            {f'<div class="entry-subtitle">{edu.degree}{" in " + edu.field_of_study if edu.field_of_study else ""}</div>' if edu.degree else ''}
                            <div class="entry-dates">{dates}</div>
                        </div>
                        <span class="verification-badge" style="background: {config['bg']}; color: {config['color']}; border: 1px solid {config['color']};">
                            <span class="verification-icon">{config['icon']}</span>
                            {config['label']}
                        </span>
                    </div>
            """
            
            if edu.verification_note:
                html += f"""
                    <div class="verification-note">
                        <strong>Verification Note:</strong> {edu.verification_note}
                    </div>
                """
            
            html += "</div>"
        
        html += "</div>"
    
    html += """
        <div class="legend">
            <div class="legend-title">Verification Status Legend</div>
            <div class="legend-items">
    """
    
    for status, config in status_config.items():
        html += f"""
            <div class="legend-item">
                <span class="verification-badge" style="background: {config['bg']}; color: {config['color']}; border: 1px solid {config['color']};">
                    <span class="verification-icon">{config['icon']}</span>
                    {config['label']}
                </span>
            </div>
        """
    
    html += """
            </div>
        </div>
    """
    
    verified_by = db.query(models.User).filter(models.User.id == candidate.verifier_id).first()
    verifier_name = verified_by.full_name if verified_by else "Unknown"
    verification_date = candidate.verified_at.strftime("%B %d, %Y") if candidate.verified_at else "Not completed"
    
    html += f"""
        <div class="footer">
            <p><strong>Verification Report</strong></p>
            <p>Verified by: {verifier_name} | Date: {verification_date}</p>
            <p style="margin-top: 0.5rem; color: #9ca3af; font-size: 0.8rem;">
                Generated by CV Verification Service
            </p>
        </div>
        </div>
    </body>
    </html>
    """
    
    return html

@router.post("/generate/{candidate_id}", response_model=schemas.ReportResponse)
def generate_report(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    candidate = db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if candidate.verification_status != models.VerificationStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Candidate verification not completed yet")
    
    html_content = generate_cv_html(candidate, db)
    
    report = models.Report(
        candidate_id=candidate_id,
        html_content=html_content,
        generated_by=current_user.id
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    return report

@router.get("/{report_id}/html", response_class=HTMLResponse)
def get_report_html(
    report_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report.html_content

@router.get("/candidate/{candidate_id}/latest", response_class=HTMLResponse)
def get_latest_report(
    candidate_id: int,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    report = db.query(models.Report).filter(
        models.Report.candidate_id == candidate_id
    ).order_by(models.Report.generated_at.desc()).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report found for this candidate")
    
    return report.html_content