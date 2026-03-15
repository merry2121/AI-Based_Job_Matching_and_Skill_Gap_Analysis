import spacy
import pandas as pd

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def load_skill_set(csv_path='data/synthetic_resumes.csv'):
    """Load all skills from the synthetic resumes to build a skill dictionary."""
    df = pd.read_csv(csv_path)
    all_skills = set()
    for skills_str in df['skills']:
        for skill in skills_str.split(', '):
            all_skills.add(skill.lower())
    return all_skills

# Global skill set (loaded once when module is imported)
SKILL_SET = load_skill_set()

def extract_skills(text):
    """Extract skills from text by matching against SKILL_SET and using NER."""
    text_lower = text.lower()
    found = set()
    # Keyword matching
    for skill in SKILL_SET:
        if skill in text_lower:
            found.add(skill)
    # Optional: use spaCy NER to catch skill names that might be entities
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
            candidate = ent.text.lower()
            if candidate in SKILL_SET:
                found.add(candidate)
    return list(found)