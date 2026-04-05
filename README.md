# AI-Based Job Matching & Skill Gap Analysis

What is this project?
A web application that helps job seekers find the right jobs based on their skills and shows them what skills they're missing for their dream job.

How it works
1. User creates an account and uploads their resume
2. System extracts skills from the resume
3. System matches user skills with job requirements
4. User sees:
   - Match percentage for each job
   - Missing skills (skill gap)
   - Recommendations to improve

Features
- User registration and login
- Resume upload and parsing
- Job search and matching
- Skill gap analysis
- Admin panel to manage jobs and users
- Payment system for premium features

Tech Stack
- Python + Flask (backend)
- HTML, CSS, JavaScript (frontend)
- JSON (database)

Project Structure

backend/
├── app.py              # Main application
├── users.json          # Stores user data
├── templates/          # HTML pages
│   ├── index.html      # Homepage
│   ├── admin.html      # Admin dashboard
│   └── payment.html    # Payment page

Who is this for?
Job seekers looking for personalized job recommendations
Career changers wanting to identify skill gaps
Recruiters who want to match candidates with jobs

Future Improvements
Add machine learning for better matching
Connect to real job APIs (LinkedIn, Indeed)
Build mobile app version

Author
GitHub: @merry2121

