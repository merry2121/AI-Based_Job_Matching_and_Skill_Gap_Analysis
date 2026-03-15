import random
import pandas as pd
from faker import Faker

fake = Faker()

# Ethiopian names
first_names = ["Abebe", "Almaz", "Meron", "Yonas", "Betelhem", "Henok", "Selam", "Biruk", "Ephrem", "Tsion"]
last_names = ["Tesfaye", "Hailu", "Demeke", "Mekonnen", "Berhanu", "Alemu", "Tadesse", "Wondimu", "Gebre", "Kebede"]

# Skills list (abbreviated for space; in your actual file, paste the full list from the previous message)
# I'll include a shorter version here for brevity, but you MUST replace this with the full list from our chat.
# Please scroll up and copy the FULL skills list from my earlier message (it's very long).
# For now, I'll put a placeholder. Replace this entire list with the full one.
skills_pool = [
    "Python", "Java", "SQL", "Machine Learning", "Data Analysis", "Excel", "Communication",
    "Project Management", "Amharic", "English", "Teamwork", "Leadership", "Customer Service",
    "Accounting", "Marketing", "Sales", "Teaching", "Research", "Writing", "Microsoft Office",
    "HTML", "CSS", "JavaScript", "Django", "Flask", "Pandas", "NumPy", "Scikit-learn",
    "TensorFlow", "PyTorch", "AWS", "Docker", "Git", "Linux", "Networking",
    "Cybersecurity", "Ethical Hacking", "Cisco", "CCNA", "Oracle", "SAP",
    "QuickBooks", "Tax Preparation", "Auditing", "Financial Reporting",
    "Economics", "Statistics", "R", "SPSS", "Stata", "EViews", "Qualtrics",
    "Survey Design", "Interviewing", "Focus Groups", "Qualitative Analysis",
    "NVivo", "Atlas.ti", "Content Analysis", "Amharic Translation",
    "Oromo", "Tigrinya", "Somali", "Afar", "English Translation",
    # ... (the full list is much longer)
]

def generate_resume():
    name = random.choice(first_names) + " " + random.choice(last_names)
    email = name.lower().replace(" ", ".") + "@example.com"
    phone = fake.phone_number()
    education = random.choice(["Bachelor's in Computer Science", "Bachelor's in Business", "Master's in Engineering", "Diploma in IT"])
    experience_years = random.randint(0, 15)
    # Randomly select 5-15 skills
    skills = random.sample(skills_pool, k=random.randint(5, 15))
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "education": education,
        "experience_years": experience_years,
        "skills": ", ".join(skills)
    }

if __name__ == "__main__":
    resumes = [generate_resume() for _ in range(500)]  # generate 500 resumes
    df = pd.DataFrame(resumes)
    df.to_csv('data/synthetic_resumes.csv', index=False)
    print("Generated 500 synthetic resumes and saved to data/synthetic_resumes.csv")