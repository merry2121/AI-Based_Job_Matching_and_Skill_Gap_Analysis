from datetime import datetime, timedelta
from .auth import generate_reset_token, verify_reset_token
from .auth import verify_password, get_password_hash, validate_password
import os
from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import PyPDF2
import pandas as pd

# Local modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from scripts.skill_extractor import extract_skills
from scripts.matcher import compute_match_score
from scripts.skill_gap import analyze_skill_gap, recommend_skills

# Database & Auth
from .database import SessionLocal, engine
from .models import Base, User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Session middleware
app.add_middleware(SessionMiddleware, secret_key="your-very-secret-key-change-this")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
app.mount("/static", StaticFiles(directory="backend/static"), name="static")
templates = Jinja2Templates(directory="backend/templates")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Global data stores (loaded at startup)
jobs_df = None
resumes_df = None
job_texts = []
job_skills = []
resume_texts = []
resume_skills = []

def extract_text_from_pdf(file: UploadFile) -> str:
    pdf_reader = PyPDF2.PdfReader(file.file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

# ================== UPDATED SCORE SCALING ==================
def scale_score(score: float) -> float:
    # score is 0-100 from compute_match_score
    # Boost by factor 10, cap at 100
    boosted = min(100, score * 10)
    return round(boosted, 2)

@app.on_event("startup")
async def load_data():
    global jobs_df, resumes_df, job_texts, job_skills, resume_texts, resume_skills
    jobs_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ethiopian_jobs.csv')
    if os.path.exists(jobs_path):
        jobs_df = pd.read_csv(jobs_path)
        job_texts = jobs_df['description'].tolist()
        job_skills = [skills.split(', ') for skills in jobs_df['skills']]
        print(f"Loaded {len(job_texts)} jobs.")
    else:
        print("Warning: ethiopian_jobs.csv not found.")
        job_texts = []
        job_skills = []

    resumes_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'synthetic_resumes.csv')
    if os.path.exists(resumes_path):
        resumes_df = pd.read_csv(resumes_path)
        resume_texts = resumes_df['skills'].tolist()
        resume_skills = [skills.split(', ') for skills in resumes_df['skills']]
        print(f"Loaded {len(resume_texts)} resumes.")
    else:
        print("Warning: synthetic_resumes.csv not found.")
        resume_texts = []
        resume_skills = []

# ---------- Authentication ----------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Job Matcher</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Inter', sans-serif;
                background: #f8fafc;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                max-width: 1000px;
                width: 100%;
                background: white;
                border-radius: 32px;
                box-shadow: 0 20px 40px -10px rgba(0,0,0,0.1);
                overflow: hidden;
                display: flex;
                flex-direction: row;
            }
            .left {
                flex: 1;
                padding: 60px 40px;
                background: linear-gradient(145deg, #ffffff 0%, #f9f9f9 100%);
            }
            .right {
                flex: 1;
                background: linear-gradient(135deg, #2b3a67 0%, #1b2a4e 100%);
                padding: 60px 40px;
                color: white;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            h1 {
                font-size: 2.4rem;
                font-weight: 700;
                color: #1e293b;
                margin-bottom: 24px;
                line-height: 1.2;
            }
            .left p {
                font-size: 1.1rem;
                color: #475569;
                margin-bottom: 40px;
                line-height: 1.6;
            }
            .button-group {
                display: flex;
                gap: 16px;
            }
            .btn {
                padding: 12px 32px;
                font-size: 1rem;
                font-weight: 600;
                border-radius: 40px;
                text-decoration: none;
                transition: all 0.2s;
                display: inline-block;
            }
            .btn-primary {
                background: #1e293b;
                color: white;
                border: 1px solid #1e293b;
            }
            .btn-primary:hover {
                background: #0f172a;
                border-color: #0f172a;
            }
            .btn-secondary {
                background: transparent;
                color: #1e293b;
                border: 1px solid #1e293b;
            }
            .btn-secondary:hover {
                background: #f1f5f9;
            }
            .right h2 {
                font-size: 2rem;
                font-weight: 600;
                margin-bottom: 24px;
            }
            .right p {
                font-size: 1.1rem;
                opacity: 0.9;
                line-height: 1.6;
                margin-bottom: 32px;
            }
            .feature {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
            }
            .feature svg {
                width: 24px;
                height: 24px;
                fill: none;
                stroke: white;
                stroke-width: 2;
                stroke-linecap: round;
                stroke-linejoin: round;
            }
            .feature span {
                font-size: 1rem;
                font-weight: 400;
            }
            @media (max-width: 768px) {
                .container {
                    flex-direction: column;
                }
                .left, .right {
                    padding: 40px 24px;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="left">
                <h1>AI‑Powered Job Matching & Skill Gap Analysis</h1>
                <p>Intelligent career guidance for job seekers and smarter recruitment for employers.</p>
                <div class="button-group">
                    <a href="/login" class="btn btn-primary">Sign In</a>
                    <a href="/register" class="btn btn-secondary">Create Account</a>
                </div>
            </div>
            <div class="right">
                <h2>Why choose us?</h2>
                <div class="feature">
                    <svg viewBox="0 0 24 24">
                        <path d="M20 7L9 18L4 13" stroke="white" stroke-width="2"/>
                    </svg>
                    <span>Personalised job recommendations</span>
                </div>
                <div class="feature">
                    <svg viewBox="0 0 24 24">
                        <path d="M20 7L9 18L4 13" stroke="white" stroke-width="2"/>
                    </svg>
                    <span>Identify skill gaps instantly</span>
                </div>
                <div class="feature">
                    <svg viewBox="0 0 24 24">
                        <path d="M20 7L9 18L4 13" stroke="white" stroke-width="2"/>
                    </svg>
                    <span>Get tailored learning recommendations</span>
                </div>
                <div class="feature">
                    <svg viewBox="0 0 24 24">
                        <path d="M20 7L9 18L4 13" stroke="white" stroke-width="2"/>
                    </svg>
                    <span>Rank candidates with AI accuracy</span>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, reset: str = None):
    message = None
    if reset == "success":
        message = "Password reset successful. Please log in."
    return templates.TemplateResponse("login.html", {"request": request, "message": message})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    request.session["user"] = {"id": user.id, "username": user.username, "role": user.role}
    return RedirectResponse(url=f"/{user.role}", status_code=302)

@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@app.post("/forgot-password")
async def forgot_password(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # Don't reveal that email doesn't exist
        return templates.TemplateResponse(
            "forgot_password.html",
            {"request": request, "message": "If your email exists, you'll receive a reset link."}
        )
    # Generate token
    token = generate_reset_token(email)
    # Store token and expiry in database
    user.reset_token = token
    user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # Simulate sending email – print the link to console
    reset_link = f"http://127.0.0.1:8000/reset-password/{token}"
    print(f"RESET LINK: {reset_link}")

    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request, "message": "If your email exists, you'll receive a reset link."}
    )

@app.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_page(request: Request, token: str, db: Session = Depends(get_db)):
    # Verify token
    email = verify_reset_token(token)
    if not email:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "Invalid or expired token.", "token": None}
        )
    # Check if token matches database and not expired
    user = db.query(User).filter(User.email == email, User.reset_token == token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "Invalid or expired token.", "token": None}
        )
    return templates.TemplateResponse(
        "reset_password.html",
        {"request": request, "token": token}
    )

@app.post("/reset-password/{token}")
async def reset_password(
    request: Request,
    token: str,
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": "Passwords do not match."}
        )
    # Validate password strength
    from .auth import validate_password
    is_valid, msg = validate_password(password)
    if not is_valid:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "token": token, "error": msg}
        )

    email = verify_reset_token(token)
    if not email:
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "Invalid or expired token.", "token": None}
        )
    user = db.query(User).filter(User.email == email, User.reset_token == token).first()
    if not user or user.reset_token_expiry < datetime.utcnow():
        return templates.TemplateResponse(
            "reset_password.html",
            {"request": request, "error": "Invalid or expired token.", "token": None}
        )

    # Update password
    user.hashed_password = get_password_hash(password)
    user.reset_token = None
    user.reset_token_expiry = None
    db.commit()

    return RedirectResponse(url="/login?reset=success", status_code=302)

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ================== DEBUGGED REGISTRATION ==================
@app.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Validate password strength (character checks)
    is_valid, msg = validate_password(password)
    if not is_valid:
        return templates.TemplateResponse("register.html", {"request": request, "error": msg})

    # 2. Check for existing user
    existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
    if existing:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username or email already exists"})

    # 3. Truncate to 72 bytes manually (guarantees no bcrypt error)
    password_bytes = password.encode('utf-8')
    byte_len = len(password_bytes)
    print(f"Password byte length: {byte_len}")
    if byte_len > 72:
        truncated_password = password_bytes[:72].decode('utf-8', errors='ignore')
        print("Password truncated to 72 bytes.")
    else:
        truncated_password = password

    # 4. Hash the truncated password
    try:
        print(f"Calling get_password_hash with password of length {len(truncated_password)} chars")
        hashed = get_password_hash(truncated_password)
        print("Hashing succeeded.")
    except Exception as e:
        print(f"Hashing error: {type(e).__name__}: {e}")
        # Fallback: try a different truncation (latin-1) to be absolutely safe
        try:
            print("Attempting fallback truncation (latin-1)")
            fallback = password.encode('latin-1', errors='ignore')[:72].decode('latin-1')
            hashed = get_password_hash(fallback)
            print("Fallback succeeded.")
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return templates.TemplateResponse("register.html", {"request": request, "error": "Technical error during registration. Please try a different password."})

    # 5. Create user
    try:
        new_user = User(username=username, email=email, hashed_password=hashed, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print(f"Database error: {e}")
        return templates.TemplateResponse("register.html", {"request": request, "error": "Registration failed due to a technical issue. Please try again."})

    # 6. Auto-login
    request.session["user"] = {"id": new_user.id, "username": new_user.username, "role": new_user.role}
    return RedirectResponse(url=f"/{role}", status_code=302)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# ---------- Protected Dashboards ----------
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=303, detail="Not authenticated", headers={"Location": "/login"})
    return user

@app.get("/seeker", response_class=HTMLResponse)
async def seeker_page(request: Request, user: dict = Depends(get_current_user)):
    if user["role"] != "seeker":
        return RedirectResponse(url="/employer", status_code=302)
    return templates.TemplateResponse("seeker.html", {"request": request, "user": user})

@app.get("/employer", response_class=HTMLResponse)
async def employer_page(request: Request, user: dict = Depends(get_current_user)):
    if user["role"] != "employer":
        return RedirectResponse(url="/seeker", status_code=302)
    return templates.TemplateResponse("employer.html", {"request": request, "user": user})

# ---------- API Endpoints ----------
@app.post("/match-seeker/")
async def match_seeker(
    request: Request,
    cv: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    if user["role"] != "seeker":
        raise HTTPException(status_code=403, detail="Forbidden")
    if not job_texts:
        raise HTTPException(status_code=500, detail="Job data not loaded")
    try:
        cv_text = extract_text_from_pdf(cv)
        cv_skills = extract_skills(cv_text)
        scores = []
        for job_desc, job_skill_set in zip(job_texts, job_skills):
            raw_score = compute_match_score(job_desc, cv_text)
            boosted_score = scale_score(raw_score)
            missing = analyze_skill_gap(job_skill_set, cv_skills)
            recs = recommend_skills(missing)
            scores.append({"score": boosted_score, "missing": missing, "recs": recs})
        results = []
        for i, score_info in enumerate(scores):
            job = jobs_df.iloc[i]
            results.append({
                "title": job['title'],
                "company": job['company'],
                "location": job['location'],
                "score": score_info['score'],
                "missing": score_info['missing'],
                "recommendations": score_info['recs']
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        top5 = results[:5]
        for idx, r in enumerate(top5):
            r['rank'] = idx + 1
        return {"jobs": top5}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================== MODIFIED EMPLOYER ENDPOINT (NO RECOMMENDATIONS) ==================
@app.post("/match-employer/")
async def match_employer(
    request: Request,
    jobdesc: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    if user["role"] != "employer":
        raise HTTPException(status_code=403, detail="Forbidden")
    if not resume_texts:
        raise HTTPException(status_code=500, detail="Resume data not loaded")
    try:
        job_text = extract_text_from_pdf(jobdesc)
        job_skillset = extract_skills(job_text)
        scores = []
        for resume_text, resume_skill_set in zip(resume_texts, resume_skills):
            raw_score = compute_match_score(job_text, resume_text)
            boosted_score = scale_score(raw_score)
            missing = analyze_skill_gap(job_skillset, resume_skill_set)
            # recs not included for employer
            scores.append({"score": boosted_score, "missing": missing})
        results = []
        for i, score_info in enumerate(scores):
            candidate = resumes_df.iloc[i]
            results.append({
                "name": candidate['name'],
                "email": candidate['email'],
                "score": score_info['score'],
                "missing": score_info['missing']
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        top5 = results[:5]
        for idx, r in enumerate(top5):
            r['rank'] = idx + 1
        return {"candidates": top5}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))