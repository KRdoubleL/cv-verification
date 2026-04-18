import pdfplumber
import io
import re
import json
import os
from typing import Dict, Any
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_content: bytes) -> str:
    with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text.strip()

def parse_pdf_cv(pdf_content: bytes) -> Dict[str, Any]:
    try:
        raw_text = extract_text_from_pdf(pdf_content)

        if not raw_text:
            raise ValueError("Could not extract text from PDF")

        prompt = f"""Extract structured data from this CV/resume text. The CV may be in any language (German, French, Spanish, etc.) - extract the data regardless of language but return field names in English.

Return ONLY a valid JSON object with exactly this structure, no other text:

{{
  "full_name": "string or null",
  "email": "string or null",
  "phone": "string or null",
  "linkedin_url": "string or null",
  "current_position": "string or null",
  "current_company": "string or null",
  "summary": "string or null",
  "skills": ["skill1", "skill2"],
  "employment": [
    {{
      "company": "string",
      "position": "string",
      "start_date": "string or null",
      "end_date": "string or null",
      "is_current": boolean,
      "description": "string or null"
    }}
  ],
  "education": [
    {{
      "institution": "string",
      "degree": "string or null",
      "field": "string or null",
      "start_date": "string or null",
      "end_date": "string or null"
    }}
  ]
}}

Section headers in other languages to look for:
- Experience: "Berufserfahrung", "Expérience", "Experiencia", "Опыт работы", "Досвід роботи"
- Education: "Ausbildung", "Formation", "Educación", "Образование", "Освіта"
- Skills: "Kenntnisse", "Compétences", "Habilidades", "Навыки"
- Summary: "Zusammenfassung", "Profil", "Résumé", "Resumen"

CV Text:
{raw_text[:4000]}"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=2000
        )

        result_text = response.choices[0].message.content.strip()
        result_text = re.sub(r'^```json\s*', '', result_text)
        result_text = re.sub(r'\s*```$', '', result_text)

        candidate_data = json.loads(result_text)

        candidate_data.setdefault("full_name", "Unknown")
        candidate_data.setdefault("email", None)
        candidate_data.setdefault("phone", None)
        candidate_data.setdefault("linkedin_url", None)
        candidate_data.setdefault("employment", [])
        candidate_data.setdefault("education", [])
        candidate_data.setdefault("skills", [])
        candidate_data.setdefault("summary", None)
        candidate_data.setdefault("current_position", None)
        candidate_data.setdefault("current_company", None)

        return candidate_data

    except Exception as e:
        return {
            "full_name": "Unknown",
            "email": None,
            "phone": None,
            "linkedin_url": None,
            "employment": [],
            "education": [],
            "skills": [],
            "summary": None,
            "current_position": None,
            "current_company": None,
            "parse_error": str(e)
        }