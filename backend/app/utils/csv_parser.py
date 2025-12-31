import pandas as pd
import io
from typing import List, Dict, Any

def parse_csv_candidates(csv_content: bytes) -> List[Dict[str, Any]]:
    """
    Parse CSV file containing candidate data.
    
    Expected CSV format (flexible column names):
    - Full Name / Name / Candidate Name
    - Email
    - Phone
    - LinkedIn / LinkedIn URL
    - Company 1, Position 1, Start Date 1, End Date 1, Current 1
    - Company 2, Position 2, Start Date 2, End Date 2, Current 2
    - Education 1, Degree 1, Field 1, Edu Start 1, Edu End 1
    - Education 2, Degree 2, Field 2, Edu Start 2, Edu End 2
    """
    
    try:
        df = pd.read_csv(io.BytesIO(csv_content))
        df.columns = df.columns.str.strip().str.lower()
        
        candidates = []
        
        for _, row in df.iterrows():
            candidate = {
                "full_name": None,
                "email": None,
                "phone": None,
                "linkedin_url": None,
                "employment": [],
                "education": []
            }
            
            for name_col in ['full name', 'name', 'candidate name', 'full_name']:
                if name_col in df.columns:
                    candidate["full_name"] = str(row[name_col]) if pd.notna(row[name_col]) else None
                    break
            
            if not candidate["full_name"]:
                continue
            
            for email_col in ['email', 'email address', 'e-mail']:
                if email_col in df.columns:
                    candidate["email"] = str(row[email_col]) if pd.notna(row[email_col]) else None
                    break
            
            for phone_col in ['phone', 'phone number', 'telephone', 'mobile']:
                if phone_col in df.columns:
                    candidate["phone"] = str(row[phone_col]) if pd.notna(row[phone_col]) else None
                    break
            
            for linkedin_col in ['linkedin', 'linkedin url', 'linkedin_url', 'linkedin profile']:
                if linkedin_col in df.columns:
                    candidate["linkedin_url"] = str(row[linkedin_col]) if pd.notna(row[linkedin_col]) else None
                    break
            
            # Parse employment history (up to 5 entries)
            for i in range(1, 6):
                company_col = f'company {i}' if f'company {i}' in df.columns else f'company{i}'
                position_col = f'position {i}' if f'position {i}' in df.columns else f'position{i}'
                
                if company_col in df.columns and pd.notna(row[company_col]):
                    employment = {
                        "company": str(row[company_col]),
                        "position": str(row[position_col]) if position_col in df.columns and pd.notna(row[position_col]) else "Unknown",
                        "start_date": None,
                        "end_date": None,
                        "is_current": False,
                        "description": None
                    }
                    
                    start_col = f'start date {i}' if f'start date {i}' in df.columns else f'start_date_{i}'
                    end_col = f'end date {i}' if f'end date {i}' in df.columns else f'end_date_{i}'
                    current_col = f'current {i}' if f'current {i}' in df.columns else f'current_{i}'
                    desc_col = f'description {i}' if f'description {i}' in df.columns else f'description_{i}'
                    
                    if start_col in df.columns and pd.notna(row[start_col]):
                        employment["start_date"] = str(row[start_col])
                    
                    if end_col in df.columns and pd.notna(row[end_col]):
                        employment["end_date"] = str(row[end_col])
                    
                    if current_col in df.columns and pd.notna(row[current_col]):
                        employment["is_current"] = str(row[current_col]).lower() in ['true', 'yes', '1', 'current']
                    
                    if desc_col in df.columns and pd.notna(row[desc_col]):
                        employment["description"] = str(row[desc_col])
                    
                    candidate["employment"].append(employment)
            
            # Parse education history (up to 3 entries)
            for i in range(1, 4):
                edu_col = f'education {i}' if f'education {i}' in df.columns else f'institution {i}'
                
                if edu_col in df.columns and pd.notna(row[edu_col]):
                    education = {
                        "institution": str(row[edu_col]),
                        "degree": None,
                        "field": None,
                        "start_date": None,
                        "end_date": None
                    }
                    
                    degree_col = f'degree {i}' if f'degree {i}' in df.columns else f'degree_{i}'
                    field_col = f'field {i}' if f'field {i}' in df.columns else f'field_of_study_{i}'
                    edu_start_col = f'edu start {i}' if f'edu start {i}' in df.columns else f'edu_start_{i}'
                    edu_end_col = f'edu end {i}' if f'edu end {i}' in df.columns else f'edu_end_{i}'
                    
                    if degree_col in df.columns and pd.notna(row[degree_col]):
                        education["degree"] = str(row[degree_col])
                    
                    if field_col in df.columns and pd.notna(row[field_col]):
                        education["field"] = str(row[field_col])
                    
                    if edu_start_col in df.columns and pd.notna(row[edu_start_col]):
                        education["start_date"] = str(row[edu_start_col])
                    
                    if edu_end_col in df.columns and pd.notna(row[edu_end_col]):
                        education["end_date"] = str(row[edu_end_col])
                    
                    candidate["education"].append(education)
            
            candidates.append(candidate)
        
        return candidates
    
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")