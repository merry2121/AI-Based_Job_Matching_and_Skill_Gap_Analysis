import random
import pandas as pd

# Ethiopian companies
companies = [
    "Ethio Telecom", "Commercial Bank of Ethiopia", "Dashen Bank", "Habesha Breweries",
    "Ethiopian Airlines", "Ministry of Education", "Addis Ababa University", "Awash Bank",
    "NIB Insurance", "Ethiopian Shipping Lines", "Homegrown Ethiopia", "SOS Children's Villages",
    "CARE Ethiopia", "Oxfam GB", "UNICEF Ethiopia", "World Food Programme",
    "Techno Serve", "PSI Ethiopia", "Population Services International", "Pathfinder International"
]

job_titles = [
    "Software Developer", "Data Analyst", "Project Manager", "Accountant", "Marketing Officer",
    "Sales Representative", "Customer Service Officer", "Human Resources Assistant",
    "Network Administrator", "Graphic Designer", "Content Writer", "Teacher", "Nurse",
    "Civil Engineer", "Architect", "Electrician", "Mechanic", "Chef", "Hotel Manager",
    "Tour Guide", "Translator (Amharic/English)", "Financial Analyst", "Auditor",
    "Procurement Officer", "Logistics Coordinator", "Administrative Assistant"
]

skills_pool = [
    "Python", "Java", "SQL", "Machine Learning", "Data Analysis", "Excel", "Communication",
    "Project Management", "Amharic", "English", "Teamwork", "Leadership", "Customer Service",
    "Accounting", "Marketing", "Sales", "Teaching", "Research", "Writing", "Microsoft Office",
    "HTML", "CSS", "JavaScript", "Django", "Flask", "Pandas", "NumPy", "Scikit-learn",
    "TensorFlow", "PyTorch", "AWS", "Docker", "Git", "Linux", "Networking",
    "Cybersecurity", "Ethical Hacking", "Cisco", "CCNA", "Oracle", "SAP", "QuickBooks"
]

def generate_job():
    title = random.choice(job_titles)
    company = random.choice(companies)
    location = random.choice(["Addis Ababa", "Bahir Dar", "Gondar", "Hawassa", "Mekelle", "Dire Dawa", "Jimma", "Debre Zeit", "Adama"])
    education = random.choice(["Bachelor's", "Master's", "Diploma", "High School"])
    experience = random.randint(0, 10)
    skills = random.sample(skills_pool, k=random.randint(3, 8))
    description = f"We are looking for a {title} at {company} in {location}. "
    description += f"Requirements: {education} degree, {experience} years experience, skills: {', '.join(skills)}."
    return {
        "title": title,
        "company": company,
        "location": location,
        "education": education,
        "experience": experience,
        "skills": ", ".join(skills),
        "description": description
    }

if __name__ == "__main__":
    jobs = [generate_job() for _ in range(1500)]  # generate 1500 jobs
    df = pd.DataFrame(jobs)
    df.to_csv('data/ethiopian_jobs.csv', index=False)
    print("Generated 1500 Ethiopian jobs and saved to data/ethiopian_jobs.csv")