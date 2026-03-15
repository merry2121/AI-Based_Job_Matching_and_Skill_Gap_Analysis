import pandas as pd
from skill_extractor import extract_skills
from matcher import rank_resumes
from skill_gap import analyze_skill_gap, recommend_skills

# Load data
resumes_df = pd.read_csv('data/synthetic_resumes.csv')

# Sample job description (you can replace with a real one later)
sample_job_text = "We are looking for a Python developer with experience in Django, SQL, and Machine Learning."
job_skills = extract_skills(sample_job_text)
print("Job required skills:", job_skills)

# Use the 'skills' column as the resume text (in a real system you'd use full text)
resume_texts = resumes_df['skills'].tolist()

# Rank resumes
ranked = rank_resumes(sample_job_text, resume_texts)
print("\nTop 5 ranked resumes (index, match %):")
for idx, score in ranked[:5]:
    print(f"  Index {idx}: {score}%")

# Show skill gap for the top candidate
top_idx = ranked[0][0]
candidate_skills = extract_skills(resume_texts[top_idx])
missing = analyze_skill_gap(job_skills, candidate_skills)
print(f"\nMissing skills for top candidate (index {top_idx}): {missing}")
print("Recommendations:", recommend_skills(missing))