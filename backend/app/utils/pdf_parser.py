import pdfplumber
import io
import re
from typing import Dict, Any, List

def parse_pdf_cv(pdf_content: bytes) -> Dict[str, Any]:
    """
    Parse PDF CV and extract structured data.
    
    This is a basic parser - for production, you'd want ML-based parsing.
    """
    
    try:
        candidate = {
            "full_name": None,
            "email": None,
            "phone": None,
            "linkedin_url": None,
            "employment": [],
            "education": []
        }
        
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        lines = full_text.split('\n')
        
        # Extract name (usually first non-empty line)
        for line in lines:
            line = line.strip()
            if line and len(line) > 2:
                candidate["full_name"] = line
                break
        
        # Extract email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, full_text)
        if emails:
            candidate["email"] = emails[0]
        
        # Extract phone
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, full_text)
            if phones:
                candidate["phone"] = phones[0]
                break
        
        # Extract LinkedIn
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[\w-]+'
        linkedins = re.findall(linkedin_pattern, full_text)
        if linkedins:
            candidate["linkedin_url"] = linkedins[0]
        
        # Parse employment
        employment_section = extract_section(full_text, 
            ['experience', 'work experience', 'professional experience', 'employment history', 'work history'])
        
        if employment_section:
            candidate["employment"] = parse_employment_section(employment_section)
        
        # Parse education
        education_section = extract_section(full_text,
            ['education', 'academic background', 'qualifications', 'academic history'])
        
        if education_section:
            candidate["education"] = parse_education_section(education_section)
        
        return candidate
    
    except Exception as e:
        raise ValueError(f"Error parsing PDF: {str(e)}")

def extract_section(text: str, headers: List[str]) -> str:
    """Extract section from CV text based on header keywords"""
    text_lower = text.lower()
    
    for header in headers:
        pattern = r'\n\s*' + re.escape(header) + r'\s*\n'
        match = re.search(pattern, text_lower)
        
        if match:
            start = match.end()
            
            next_sections = ['education', 'experience', 'skills', 'projects', 'certifications', 
                           'awards', 'publications', 'languages', 'references']
            
            end = len(text)
            for next_section in next_sections:
                if next_section != header:
                    next_pattern = r'\n\s*' + re.escape(next_section) + r'\s*\n'
                    next_match = re.search(next_pattern, text_lower[start:])
                    if next_match:
                        end = start + next_match.start()
                        break
            
            return text[start:end].strip()
    
    return ""

def parse_employment_section(text: str) -> List[Dict[str, Any]]:
    """Parse employment entries from text"""
    employment = []
    
    lines = text.split('\n')
    current_entry = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if line looks like a date range
        date_pattern = r'(\d{4}|\w{3}\s+\d{4})\s*[-–—]\s*(\d{4}|\w{3}\s+\d{4}|Present|Current)'
        date_match = re.search(date_pattern, line, re.IGNORECASE)
        
        if date_match:
            if current_entry:
                employment.append(current_entry)
            
            current_entry = {
                "company": "Unknown Company",
                "position": "Unknown Position",
                "start_date": date_match.group(1),
                "end_date": date_match.group(2),
                "is_current": "present" in date_match.group(2).lower() or "current" in date_match.group(2).lower(),
                "description": ""
            }
            
            clean_line = line[:date_match.start()].strip()
            if clean_line:
                parts = clean_line.split('|')
                if len(parts) >= 2:
                    current_entry["position"] = parts[0].strip()
                    current_entry["company"] = parts[1].strip()
                else:
                    current_entry["position"] = clean_line
        
        elif current_entry:
            if current_entry["description"]:
                current_entry["description"] += " " + line
            else:
                current_entry["description"] = line
    
    if current_entry:
        employment.append(current_entry)
    
    if not employment:
        employment.append({
            "company": "See PDF for details",
            "position": "Unable to parse automatically",
            "start_date": None,
            "end_date": None,
            "is_current": False,
            "description": "Please review PDF manually"
        })
    
    return employment

def parse_education_section(text: str) -> List[Dict[str, Any]]:
    """Parse education entries from text"""
    education = []
    
    lines = text.split('\n')
    current_entry = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'diploma', 'bsc', 'msc', 'ba', 'ma', 'mba']
        
        if any(keyword in line.lower() for keyword in degree_keywords):
            if current_entry:
                education.append(current_entry)
            
            current_entry = {
                "institution": "Unknown Institution",
                "degree": line,
                "field": None,
                "start_date": None,
                "end_date": None
            }
        
        date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|Present|Current)'
        date_match = re.search(date_pattern, line, re.IGNORECASE)
        
        if date_match and current_entry:
            current_entry["start_date"] = date_match.group(1)
            current_entry["end_date"] = date_match.group(2)
        
        if current_entry and not any(keyword in line.lower() for keyword in degree_keywords):
            if not date_match:
                current_entry["institution"] = line
    
    if current_entry:
        education.append(current_entry)
    
    if not education:
        education.append({
            "institution": "See PDF for details",
            "degree": "Unable to parse automatically",
            "field": None,
            "start_date": None,
            "end_date": None
        })
    
    return education