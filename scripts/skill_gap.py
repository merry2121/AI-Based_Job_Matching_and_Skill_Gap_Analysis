def analyze_skill_gap(job_skills, candidate_skills):
    """Return missing skills (skills in job but not in candidate)."""
    job_set = set(job_skills)
    candidate_set = set(candidate_skills)
    missing = job_set - candidate_set
    return list(missing)

def recommend_skills(missing_skills, top_n=3):
    """Simple recommendation: return the missing skills as learning suggestions."""
    return [f"Learn {skill}" for skill in list(missing_skills)[:top_n]]