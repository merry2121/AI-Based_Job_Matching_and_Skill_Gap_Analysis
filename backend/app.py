from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import PyPDF2
import uvicorn
from datetime import datetime

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="secret123")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# User storage
users = {
    "admin": {"password": "admin123", "role": "admin", "full_name": "Administrator", "email": "admin@example.com"}
}

# Job recommendations
FIXED_JOBS = [
    {"id": 1, "title": "Senior Software Engineer", "company": "Google Ethiopia", "location": "Addis Ababa", 
     "skills": "Python, Java, JavaScript, React, SQL, Docker, AWS", "match_score": 95, "missing_skills": "Kubernetes"},
    {"id": 2, "title": "Full Stack Developer", "company": "Meta", "location": "Remote", 
     "skills": "JavaScript, React, Node.js, Python, MongoDB, Express", "match_score": 88, "missing_skills": "TypeScript"},
    {"id": 3, "title": "Data Scientist", "company": "Microsoft", "location": "Remote", 
     "skills": "Python, SQL, Machine Learning, Pandas, NumPy, TensorFlow", "match_score": 82, "missing_skills": "Spark"},
    {"id": 4, "title": "DevOps Engineer", "company": "Amazon", "location": "Addis Ababa", 
     "skills": "Docker, Kubernetes, AWS, Linux, Git, Jenkins", "match_score": 76, "missing_skills": "Terraform"},
    {"id": 5, "title": "Frontend Developer", "company": "Spotify", "location": "Remote", 
     "skills": "JavaScript, React, HTML, CSS, TypeScript, Tailwind", "match_score": 91, "missing_skills": "Vue.js"},
]

# ============================================================
# LEARNING RESOURCES FOR SKILL GAP
# ============================================================
LEARNING_RESOURCES = {
    "python": [
        {"platform": "YouTube", "course": "Python for Beginners", "url": "https://www.youtube.com/results?search_query=python+for+beginners", "duration": "4-6 weeks"},
        {"platform": "Coursera", "course": "Python for Everybody", "url": "https://www.coursera.org/specializations/python", "duration": "2-3 months"}
    ],
    "javascript": [
        {"platform": "YouTube", "course": "JavaScript Tutorial for Beginners", "url": "https://www.youtube.com/results?search_query=javascript+tutorial", "duration": "3-5 weeks"},
        {"platform": "FreeCodeCamp", "course": "JavaScript Algorithms", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "duration": "2 months"}
    ],
    "react": [
        {"platform": "YouTube", "course": "React Complete Guide", "url": "https://www.youtube.com/results?search_query=react+tutorial", "duration": "4-6 weeks"},
        {"platform": "Scrimba", "course": "Learn React for Free", "url": "https://scrimba.com/learn/learnreact", "duration": "3 weeks"}
    ],
    "sql": [
        {"platform": "YouTube", "course": "SQL Tutorial - Full Course", "url": "https://www.youtube.com/results?search_query=sql+tutorial", "duration": "2-3 weeks"},
        {"platform": "Mode Analytics", "course": "SQL Tutorial", "url": "https://mode.com/sql-tutorial/", "duration": "2 weeks"}
    ],
    "docker": [
        {"platform": "YouTube", "course": "Docker Tutorial for Beginners", "url": "https://www.youtube.com/results?search_query=docker+tutorial", "duration": "1-2 weeks"},
        {"platform": "Docker Docs", "course": "Get Started with Docker", "url": "https://docs.docker.com/get-started/", "duration": "1 week"}
    ],
    "aws": [
        {"platform": "YouTube", "course": "AWS Certified Cloud Practitioner", "url": "https://www.youtube.com/results?search_query=aws+cloud+practitioner", "duration": "4-6 weeks"},
        {"platform": "AWS Skill Builder", "course": "AWS Cloud Practitioner Essentials", "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/", "duration": "3 weeks"}
    ],
    "machine learning": [
        {"platform": "YouTube", "course": "Machine Learning Course", "url": "https://www.youtube.com/results?search_query=machine+learning+course", "duration": "8-10 weeks"},
        {"platform": "Coursera", "course": "Machine Learning by Andrew Ng", "url": "https://www.coursera.org/learn/machine-learning", "duration": "3 months"}
    ],
    "django": [
        {"platform": "YouTube", "course": "Django Tutorial for Beginners", "url": "https://www.youtube.com/results?search_query=django+tutorial", "duration": "3-4 weeks"},
        {"platform": "Django Girls", "course": "Django Tutorial", "url": "https://tutorial.djangogirls.org/", "duration": "2 weeks"}
    ]
}

def get_learning_recommendations(missing_skills):
    """Generate learning recommendations for missing skills"""
    recommendations = []
    for skill in missing_skills[:5]:
        skill_lower = skill.lower()
        if skill_lower in LEARNING_RESOURCES:
            resources = LEARNING_RESOURCES[skill_lower][:2]
            recommendations.append({
                "skill": skill,
                "resources": resources,
                "estimated_time": resources[0]["duration"] if resources else "2-4 weeks"
            })
        else:
            recommendations.append({
                "skill": skill,
                "resources": [
                    {"platform": "YouTube", "course": f"Learn {skill} Tutorial", "url": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+tutorial", "duration": "2-4 weeks"},
                    {"platform": "Coursera/edX", "course": f"{skill} Certification", "url": f"https://www.coursera.org/search?query={skill.replace(' ', '%20')}", "duration": "4-6 weeks"}
                ],
                "estimated_time": "2-4 weeks"
            })
    return recommendations

# Data storage
applications = []
messages = []
payments = []
job_postings = []

# ============================================================
# HOMEPAGE HTML
# ============================================================
HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Job Matching Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: white;
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
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            display: flex;
            flex-direction: row;
            border: 1px solid #e2e8f0;
        }
        .left { flex: 1; padding: 60px 40px; background: white; }
        .right { flex: 1; background: #1e293b; padding: 60px 40px; color: white; }
        h1 { font-size: 2.4rem; font-weight: 700; color: #1e293b; margin-bottom: 24px; }
        .left p { font-size: 1.1rem; color: #64748b; margin-bottom: 40px; }
        .button-group { display: flex; gap: 16px; }
        .btn { padding: 12px 32px; font-size: 1rem; font-weight: 600; border-radius: 40px; text-decoration: none; cursor: pointer; border: none; }
        .btn-primary { background: #1e293b; color: white; }
        .btn-primary:hover { background: #0f172a; }
        .btn-secondary { background: #f1f5f9; color: #1e293b; }
        .btn-secondary:hover { background: #e2e8f0; }
        .right h2 { font-size: 2rem; font-weight: 600; margin-bottom: 24px; }
        .feature { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; }
        @media (max-width: 768px) { .container { flex-direction: column; } }
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
            <div class="feature"><span>✓ Personalised job recommendations</span></div>
            <div class="feature"><span>✓ Identify skill gaps instantly</span></div>
            <div class="feature"><span>✓ Get tailored learning recommendations</span></div>
            <div class="feature"><span>✓ Rank candidates with AI accuracy</span></div>
        </div>
    </div>
</body>
</html>
"""

# ============================================================
# LOGIN PAGE HTML
# ============================================================
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - AI Job Matching</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: white; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-container { background: white; border-radius: 20px; padding: 40px; width: 400px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        h2 { text-align: center; color: #1e293b; margin-bottom: 30px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #e2e8f0; border-radius: 8px; }
        input:focus { outline: none; border-color: #1e293b; }
        button { width: 100%; padding: 12px; background: #1e293b; color: white; border: none; border-radius: 40px; cursor: pointer; font-weight: 600; }
        button:hover { background: #0f172a; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #1e293b; text-decoration: none; }
        .error { background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; }
        .success { background: #d1fae5; color: #065f46; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Sign In</h2>
        <div id="msg"></div>
        <form id="loginForm" autocomplete="off">
            <input type="text" id="username" placeholder="Username" required autocomplete="off">
            <input type="password" id="password" placeholder="Password" required autocomplete="new-password">
            <button type="submit">Sign In</button>
        </form>
        <div class="links"><a href="/register">Create Account</a></div>
    </div>
    <script>
        const url = new URLSearchParams(window.location.search);
        if (url.get('registered') === 'success') {
            document.getElementById('msg').innerHTML = '<div class="success">Registration successful! Please login.</div>';
        }
        if (url.get('error')) {
            document.getElementById('msg').innerHTML = '<div class="error">' + decodeURIComponent(url.get('error')) + '</div>';
        }
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData();
            fd.append('username', document.getElementById('username').value);
            fd.append('password', document.getElementById('password').value);
            const res = await fetch('/login', { method: 'POST', body: fd });
            if (res.redirected) window.location.href = res.url;
        });
    </script>
</body>
</html>
"""

# ============================================================
# REGISTER PAGE HTML
# ============================================================
REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Register - AI Job Matching</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: white; min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .register-container { background: white; border-radius: 20px; padding: 40px; width: 450px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; }
        h2 { text-align: center; color: #1e293b; margin-bottom: 30px; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #e2e8f0; border-radius: 8px; }
        input:focus, select:focus { outline: none; border-color: #1e293b; }
        .radio-group { margin: 15px 0; }
        .radio-group label { margin-right: 20px; cursor: pointer; }
        .radio-group input { width: auto; margin-right: 5px; }
        button { width: 100%; padding: 12px; background: #1e293b; color: white; border: none; border-radius: 40px; cursor: pointer; font-weight: 600; }
        button:hover { background: #0f172a; }
        .links { text-align: center; margin-top: 20px; }
        .links a { color: #1e293b; text-decoration: none; }
        .error { background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 15px; }
    </style>
</head>
<body>
    <div class="register-container">
        <h2>Create Account</h2>
        <div id="error"></div>
        <form id="registerForm" autocomplete="off">
            <input type="text" id="full_name" placeholder="Full Name" required autocomplete="off">
            <input type="text" id="username" placeholder="Username" required autocomplete="off">
            <input type="email" id="email" placeholder="Email" required autocomplete="off">
            <input type="password" id="password" placeholder="Password" required autocomplete="new-password">
            <div class="radio-group">
                <label><input type="radio" name="role" value="seeker" checked> Job Seeker</label>
                <label><input type="radio" name="role" value="employer"> Employer</label>
            </div>
            <button type="submit">Register</button>
        </form>
        <div class="links"><a href="/login">Already have an account? Login</a></div>
    </div>
    <script>
        document.getElementById('registerForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData();
            fd.append('full_name', document.getElementById('full_name').value);
            fd.append('username', document.getElementById('username').value);
            fd.append('email', document.getElementById('email').value);
            fd.append('password', document.getElementById('password').value);
            fd.append('role', document.querySelector('input[name="role"]:checked').value);
            const res = await fetch('/register', { method: 'POST', body: fd });
            if (res.redirected) window.location.href = res.url;
        });
    </script>
</body>
</html>
"""

# ============================================================
# SEEKER DASHBOARD HTML
# ============================================================
SEEKER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>!!! NEW VERSION - DEC 2024 !!!</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; }
        header { background: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
        .role-badge { background: #1e293b; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; margin-left: 15px; }
        .logout-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; border: none; margin-left: 15px; cursor: pointer; font-weight: 600; }
        .logout-btn:hover { background: #0f172a; }
        .home-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; text-decoration: none; margin-right: 10px; font-weight: 600; }
        .home-btn:hover { background: #0f172a; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .upload-section { background: white; padding: 40px; border-radius: 20px; margin-bottom: 30px; text-align: center; border: 1px solid #e2e8f0; }
        .upload-area { border: 2px dashed #cbd5e1; border-radius: 16px; padding: 50px; margin: 20px 0; cursor: pointer; background: #f8fafc; }
        .upload-area:hover { background: #f1f5f9; border-color: #1e293b; }
        .job-card { background: white; padding: 24px; border-radius: 16px; margin-bottom: 16px; border: 1px solid #e2e8f0; }
        .match-score { display: inline-block; background: #1e293b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }
        .btn-upload { background: #1e293b; color: white; border: none; padding: 12px 32px; border-radius: 40px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn-apply { background: #1e293b; color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; margin-top: 10px; font-weight: 600; }
        .btn-learning { background: #1e293b; color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; margin-top: 10px; font-weight: 600; margin-right: 10px; }
        .btn-apply:hover, .btn-upload:hover, .btn-learning:hover { background: #0f172a; }
        .loading { display: none; text-align: center; padding: 40px; }
        .spinner { border: 4px solid #e2e8f0; border-top: 4px solid #1e293b; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        input[type="file"] { display: none; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #e2e8f0; border-radius: 8px; cursor: pointer; color: #1e293b; font-weight: 600; }
        .tab.active { background: #1e293b; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .confirm-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);
            display: flex; justify-content: center; align-items: center; z-index: 1000;
        }
        .confirm-box { background: white; padding: 30px; border-radius: 20px; text-align: center; max-width: 400px; }
        .confirm-box button { margin: 10px; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .confirm-yes { background: #ef4444; color: white; border: none; }
        .confirm-no { background: #e2e8f0; color: #1e293b; border: none; }
        .message-input { width: 100%; padding: 12px; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; }
    </style>
</head>
<body>
    <header>
        <div class="logo">🤝 AI Job Matcher</div>
        <div>
            <a href="/" class="home-btn">🏠 Home</a>
            <span>Welcome, <strong id="username"></strong>!</span>
            <span class="role-badge">Job Seeker</span>
            <button class="logout-btn" onclick="showLogoutConfirm()">Logout</button>
        </div>
    </header>
    <div class="container">
        <div class="nav-tabs">
            <div class="tab active" onclick="showTab('find')">Find Jobs</div>
            <div class="tab" onclick="showTab('applications')">My Applications</div>
            <div class="tab" onclick="showTab('messages')">Messages</div>
        </div>
        
        <div id="find" class="tab-content active">
            <div class="upload-section">
                <h3>📄 Upload Your CV</h3>
                <div class="upload-area" onclick="document.getElementById('cvFile').click()">
                    <div style="font-size: 48px;">📁</div>
                    <p>Click to select your CV file (PDF)</p>
                </div>
                <input type="file" id="cvFile" accept=".pdf" onchange="updateFileName()">
                <div id="fileName" style="margin-top: 10px;"></div>
                <button class="btn-upload" onclick="uploadCV()">🔍 Find Matching Jobs</button>
                <div id="loading" class="loading"><div class="spinner"></div><p>Analyzing your skills...</p></div>
            </div>
            <div id="results"></div>
        </div>
        
        <div id="applications" class="tab-content">
            <div class="upload-section">
                <h3>📋 My Job Applications</h3>
                <div id="applicationsList">No applications yet.</div>
            </div>
        </div>
        
        <div id="messages" class="tab-content">
            <div class="upload-section">
                <h3>💬 Conversations with Employers</h3>
                <div id="messagesList">No messages yet.</div>
            </div>
        </div>
    </div>
    <div id="confirmModal" style="display:none;" class="confirm-modal">
        <div class="confirm-box"><h3>Confirm Logout</h3><p>Are you sure you want to logout?</p>
        <button class="confirm-yes" onclick="logout()">Yes</button><button class="confirm-no" onclick="closeModal()">Cancel</button></div>
    </div>
    <script>
        let currentUser = '{{ username }}';
        document.getElementById('username').innerText = currentUser;
        
        function showLogoutConfirm() { document.getElementById('confirmModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('confirmModal').style.display = 'none'; }
        function logout() { window.location.href = '/logout'; }
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            if (tabName === 'applications') loadApplications();
            if (tabName === 'messages') loadMessages();
        }
        
        function updateFileName() { const f = document.getElementById('cvFile').files[0]; if(f) document.getElementById('fileName').innerHTML = '✓ Selected: ' + f.name; }
        
        async function uploadCV() {
            const file = document.getElementById('cvFile').files[0];
            if (!file) { alert('Please select a PDF file'); return; }
            document.getElementById('loading').style.display = 'block';
            const fd = new FormData(); fd.append('cv', file);
            const res = await fetch('/match-cv', { method: 'POST', body: fd });
            const data = await res.json();
            displayResults(data.jobs);
            document.getElementById('loading').style.display = 'none';
        }
        
        function displayResults(jobs) {
            if (!jobs || jobs.length === 0) {
                document.getElementById('results').innerHTML = '<div class="upload-section"><p>No matching jobs found.</p></div>';
                return;
            }
            let html = '<div class="upload-section"><h3>🎯 Your Top 5 Job Matches</h3>';
            jobs.forEach((job, i) => {
                html += `<div class="job-card"><h4>${i+1}. ${job.title}</h4><p><strong>${job.company}</strong> • ${job.location}</p>
                <span class="match-score">${job.match_score}% Match</span><p>📊 Skills: ${job.skills}</p>
                <p style="color:#64748b;">⚠️ Missing: ${job.missing_skills}</p>
                <div><button class="btn-learning" onclick="showLearning('${job.id}', '${job.title.replace(/'/g, "\\'")}', '${job.missing_skills.replace(/'/g, "\\'")}')">📚 Get Learning Plan</button>
                <button class="btn-apply" onclick="applyJob(${job.id}, '${job.title.replace(/'/g, "\\'")}', '${job.company.replace(/'/g, "\\'")}', ${job.match_score})">Apply Now</button></div></div>`;
            });
            html += '</div>';
            document.getElementById('results').innerHTML = html;
        }
        
        async function showLearning(jobId, jobTitle, missingSkills) {
            const skills = missingSkills.split(',').map(s => s.trim()).filter(s => s !== 'None' && s !== '');
            if (skills.length === 0) {
                alert('No missing skills identified! You are well qualified for this position.');
                return;
            }
            const response = await fetch('/get-learning-plan', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({skills: skills})
            });
            const data = await response.json();
            let modalHtml = `<div id="learningModal" style="position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.5); display:flex; justify-content:center; align-items:center; z-index:1000;">
                <div style="background:white; border-radius:20px; padding:30px; max-width:600px; max-height:80%; overflow-y:auto;">
                    <h3>📚 Learning Plan for ${jobTitle}</h3>
                    <p><strong>Missing Skills to Learn:</strong></p>`;
            data.recommendations.forEach(rec => {
                modalHtml += `<div style="margin:15px 0; padding:15px; background:#f8fafc; border-radius:10px;">
                    <h4>🎯 ${rec.skill}</h4>
                    <p><strong>Estimated Time:</strong> ${rec.estimated_time}</p>
                    <p><strong>Recommended Resources:</strong></p><ul>`;
                rec.resources.forEach(res => {
                    modalHtml += `<li><a href="${res.url}" target="_blank">${res.platform}: ${res.course}</a> (${res.duration})</li>`;
                });
                modalHtml += `</ul></div>`;
            });
            modalHtml += `<button onclick="document.getElementById('learningModal').remove()" style="background:#1e293b; color:white; border:none; padding:10px 20px; border-radius:8px; margin-top:15px; cursor:pointer;">Close</button>
                    </div></div>`;
            document.body.insertAdjacentHTML('beforeend', modalHtml);
        }
        
        async function applyJob(jobId, title, company, score) {
            const message = prompt(`Apply for ${title} at ${company}\\n\\nMatch Score: ${score}%\\n\\nEnter a cover letter:`);
            if (message !== null) {
                const fd = new FormData();
                fd.append('job_id', jobId); fd.append('job_title', title); fd.append('company', company);
                fd.append('match_score', score); fd.append('message', message || '');
                await fetch('/apply-job', { method: 'POST', body: fd });
                alert('Application submitted!'); loadApplications(); showTab('applications');
            }
        }
        
        async function loadApplications() {
            const res = await fetch('/get-applications');
            const data = await res.json();
            const container = document.getElementById('applicationsList');
            if (data.applications.length === 0) container.innerHTML = '<p>No applications yet.</p>';
            else {
                let html = '';
                data.applications.forEach(app => {
                    html += `<div class="job-card"><h4>${app.job_title}</h4><p><strong>${app.company}</strong></p>
                    <span class="match-score">${app.match_score}% Match</span><p><strong>Status:</strong> ${app.status}</p>
                    <p><strong>Applied:</strong> ${app.applied_at}</p><p><strong>Your Message:</strong> ${app.message || 'No message'}</p></div>`;
                });
                container.innerHTML = html;
            }
        }
        
        async function loadMessages() {
            const res = await fetch('/get-messages');
            const data = await res.json();
            const container = document.getElementById('messagesList');
            if (data.messages.length === 0) container.innerHTML = '<p>No messages yet.</p>';
            else {
                let html = '';
                const grouped = {};
                data.messages.forEach(msg => { if(!grouped[msg.conversation_id]) grouped[msg.conversation_id] = []; grouped[msg.conversation_id].push(msg); });
                for (let convId in grouped) {
                    const msgs = grouped[convId];
                    const otherUser = msgs[0].from_name === currentUser ? msgs[0].to_name : msgs[0].from_name;
                    html += `<div class="job-card"><h4>💬 Conversation with: ${otherUser}</h4>`;
                    msgs.forEach(msg => {
                        const isMe = msg.from_name === currentUser;
                        html += `<div style="margin-top:10px; padding:10px; background:${isMe ? '#e2e8f0' : '#f8fafc'}; border-radius:8px;">
                            <strong>${isMe ? 'You' : msg.from_name}:</strong> ${msg.message}<div style="font-size:11px; color:#94a3b8;">${msg.created_at}</div></div>`;
                    });
                    html += `<div style="margin-top:15px;"><textarea id="reply_${convId}" class="message-input" placeholder="Type your reply..."></textarea>
                    <button class="btn-apply" onclick="sendReply('${convId}', '${otherUser}')">Send Reply</button></div></div>`;
                }
                container.innerHTML = html;
            }
        }
        
        async function sendReply(conversationId, toUser) {
            const msgBox = document.getElementById(`reply_${conversationId}`);
            const message = msgBox.value;
            if (!message.trim()) return;
            const fd = new FormData();
            fd.append('to_user', toUser);
            fd.append('message', message);
            fd.append('conversation_id', conversationId);
            await fetch('/send-reply', { method: 'POST', body: fd });
            msgBox.value = '';
            loadMessages();
        }
    </script>
</body>
</html>
"""

# ============================================================
# EMPLOYER DASHBOARD HTML
# ============================================================
EMPLOYER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Employer Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; }
        header { background: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
        .role-badge { background: #1e293b; color: white; padding: 5px 15px; border-radius: 20px; font-size: 12px; margin-left: 15px; }
        .logout-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; border: none; margin-left: 15px; cursor: pointer; font-weight: 600; }
        .logout-btn:hover { background: #0f172a; }
        .home-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; text-decoration: none; margin-right: 10px; font-weight: 600; }
        .home-btn:hover { background: #0f172a; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .upload-section { background: white; padding: 40px; border-radius: 20px; margin-bottom: 30px; text-align: center; border: 1px solid #e2e8f0; }
        .upload-area { border: 2px dashed #cbd5e1; border-radius: 16px; padding: 50px; margin: 20px 0; cursor: pointer; background: #f8fafc; }
        .upload-area:hover { background: #f1f5f9; border-color: #1e293b; }
        .candidate-card { background: white; padding: 24px; border-radius: 16px; margin-bottom: 16px; border: 1px solid #e2e8f0; }
        .match-score { display: inline-block; background: #1e293b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 600; }
        .btn-pay { background: #1e293b; color: white; border: none; padding: 14px 32px; border-radius: 40px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 20px; }
        .btn-pay:hover { background: #0f172a; }
        .btn-contact { background: #1e293b; color: white; border: none; padding: 8px 20px; border-radius: 8px; cursor: pointer; margin-top: 10px; font-weight: 600; }
        .btn-contact:hover { background: #0f172a; }
        .loading { display: none; text-align: center; padding: 40px; }
        .spinner { border: 4px solid #e2e8f0; border-top: 4px solid #1e293b; border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; margin: 0 auto 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        input[type="file"] { display: none; }
        .nav-tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: #e2e8f0; border-radius: 8px; cursor: pointer; color: #1e293b; font-weight: 600; }
        .tab.active { background: #1e293b; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .payment-card { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 15px; border-radius: 12px; margin-bottom: 20px; }
        .payment-amount { font-size: 24px; font-weight: bold; color: #1e293b; }
        .form-group { text-align: left; margin-bottom: 15px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: 600; color: #1e293b; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px; }
        .row-2 { display: flex; gap: 20px; }
        .row-2 > div { flex: 1; }
        .confirm-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);
            display: flex; justify-content: center; align-items: center; z-index: 1000;
        }
        .confirm-box { background: white; padding: 30px; border-radius: 20px; text-align: center; max-width: 400px; }
        .confirm-box button { margin: 10px; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .confirm-yes { background: #ef4444; color: white; border: none; }
        .confirm-no { background: #e2e8f0; color: #1e293b; border: none; }
        .message-input { width: 100%; padding: 12px; margin-top: 10px; border: 1px solid #e2e8f0; border-radius: 8px; }
    </style>
</head>
<body>
    <header>
        <div class="logo">🤝 AI Job Matcher</div>
        <div>
            <a href="/" class="home-btn">🏠 Home</a>
            <span>Welcome, <strong id="username"></strong>!</span>
            <span class="role-badge">Employer</span>
            <button class="logout-btn" onclick="showLogoutConfirm()">Logout</button>
        </div>
    </header>
    <div class="container">
        <div class="nav-tabs">
            <div class="tab active" onclick="showTab('post')">📝 Post a Job & Find Candidates</div>
            <div class="tab" onclick="showTab('history')">💳 Payment History</div>
            <div class="tab" onclick="showTab('messages')">💬 Messages</div>
        </div>
        
        <div id="post" class="tab-content active">
            <div class="upload-section">
                <h3>💰 Post a New Job - 50 ETB</h3>
                <div class="payment-card"><p>Job posting fee: <span class="payment-amount">50 ETB</span> per job</p>
                <p style="font-size:12px;">After payment, top 5 matching candidates will be displayed</p></div>
                <div style="display:flex; gap:10px; justify-content:center; margin-bottom:20px;">
                    <button type="button" class="tab" style="background:#1e293b; color:white;" onclick="showInputMethod('form')">✏️ Fill Form</button>
                    <button type="button" class="tab" onclick="showInputMethod('pdf')">📄 Upload PDF</button>
                </div>
                <div id="formMethod">
                    <form id="postJobForm">
                        <div class="form-group"><label>Job Title *</label><input type="text" id="title" required></div>
                        <div class="row-2"><div class="form-group"><label>Location *</label><input type="text" id="location" required></div>
                        <div class="form-group"><label>Salary Range</label><input type="text" id="salary"></div></div>
                        <div class="form-group"><label>Job Description *</label><textarea id="description" rows="4" required></textarea></div>
                        <div class="form-group"><label>Required Skills *</label><input type="text" id="skills" placeholder="Python, JavaScript, SQL" required></div>
                        <button type="submit" class="btn-pay">💳 Pay 50 ETB & Post Job</button>
                    </form>
                </div>
                <div id="pdfMethod" style="display:none;">
                    <div class="upload-area" onclick="document.getElementById('jobFile').click()">
                        <div style="font-size:48px;">📋</div><p>Click to upload Job Description (PDF)</p>
                    </div>
                    <input type="file" id="jobFile" accept=".pdf" onchange="updateFileName()">
                    <div id="fileName" style="margin-top:10px;"></div>
                    <button class="btn-pay" onclick="processPDFAndPay()">💳 Pay 50 ETB & Post Job from PDF</button>
                </div>
            </div>
            <div id="results" style="display:none;"><div class="upload-section"><h3>🎯 Top 5 Matching Candidates</h3><div id="candidatesList"></div></div></div>
        </div>
        
        <div id="history" class="tab-content"><div class="upload-section"><h3>💳 Payment History</h3><div id="paymentsList">Loading...</div></div></div>
        <div id="messages" class="tab-content"><div class="upload-section"><h3>💬 Conversations with Candidates</h3><div id="messagesList">Loading...</div></div></div>
    </div>
    <div id="confirmModal" style="display:none;" class="confirm-modal">
        <div class="confirm-box"><h3>Confirm Logout</h3><p>Are you sure you want to logout?</p>
        <button class="confirm-yes" onclick="logout()">Yes</button><button class="confirm-no" onclick="closeModal()">Cancel</button></div>
    </div>
    <script>
        let currentUser = '{{ username }}';
        document.getElementById('username').innerText = currentUser;
        
        function showLogoutConfirm() { document.getElementById('confirmModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('confirmModal').style.display = 'none'; }
        function logout() { window.location.href = '/logout'; }
        
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            if (tabName === 'history') loadPayments();
            if (tabName === 'messages') loadMessages();
        }
        
        function showInputMethod(method) {
            document.getElementById('formMethod').style.display = method === 'form' ? 'block' : 'none';
            document.getElementById('pdfMethod').style.display = method === 'pdf' ? 'block' : 'none';
        }
        
        function updateFileName() { const f = document.getElementById('jobFile').files[0]; if(f) document.getElementById('fileName').innerHTML = '✓ Selected: ' + f.name; }
        
        document.getElementById('postJobForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData();
            fd.append('title', document.getElementById('title').value);
            fd.append('location', document.getElementById('location').value);
            fd.append('description', document.getElementById('description').value);
            fd.append('skills', document.getElementById('skills').value);
            fd.append('salary', document.getElementById('salary').value);
            const res = await fetch('/post-job-and-match', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.success) { alert('✅ Payment successful!'); displayCandidates(data.candidates); loadPayments(); }
            else alert('Error: ' + data.error);
        });
        
        async function processPDFAndPay() {
            const file = document.getElementById('jobFile').files[0];
            if (!file) { alert('Select a PDF'); return; }
            const fd = new FormData(); fd.append('job_desc', file);
            const res = await fetch('/post-job-from-pdf', { method: 'POST', body: fd });
            const data = await res.json();
            if (data.success) { alert('✅ Payment successful!'); displayCandidates(data.candidates); loadPayments(); }
            else alert('Error: ' + data.error);
        }
        
        function displayCandidates(candidates) {
            const container = document.getElementById('candidatesList');
            const resultsDiv = document.getElementById('results');
            if (!candidates || candidates.length === 0) container.innerHTML = '<p>No matching candidates found.</p>';
            else {
                let html = '';
                candidates.forEach((c, i) => {
                    html += `<div class="candidate-card"><h4>${i+1}. ${c.name}</h4><p><strong>Experience:</strong> ${c.experience}</p>
                    <p><strong>Education:</strong> ${c.education}</p><p><strong>Email:</strong> ${c.email}</p>
                    <span class="match-score">${c.match_score}% Match</span><p>🎯 Skills: ${c.skills}</p>
                    <button class="btn-contact" onclick="contactCandidate(${c.id}, '${c.name}', '${c.email}')">✉️ Send Message</button></div>`;
                });
                container.innerHTML = html;
            }
            resultsDiv.style.display = 'block';
            resultsDiv.scrollIntoView({ behavior: 'smooth' });
        }
        
        async function contactCandidate(id, name, email) {
            const message = prompt(`Send message to ${name} (${email}):`);
            if (message && message.trim()) {
                const fd = new FormData();
                fd.append('candidate_id', id); fd.append('candidate_name', name);
                fd.append('candidate_email', email); fd.append('message', message);
                await fetch('/send-message', { method: 'POST', body: fd });
                alert(`Message sent to ${name}!`); loadMessages();
            }
        }
        
        async function loadPayments() {
            const res = await fetch('/get-payments');
            const data = await res.json();
            const container = document.getElementById('paymentsList');
            if (data.payments.length === 0) container.innerHTML = '<p>No payments yet.</p>';
            else {
                let html = '<table style="width:100%"><tr style="background:#f1f5f9;"><th>Amount</th><th>Type</th><th>Status</th><th>Date</th></tr>';
                data.payments.forEach(p => { html += `<tr><td style="padding:10px;">${p.amount} ETB</td><td style="padding:10px;">${p.type}</td><td style="padding:10px;">${p.status}</td><td style="padding:10px;">${p.date}</td></tr>`; });
                html += '</table>';
                container.innerHTML = html;
            }
        }
        
        async function loadMessages() {
            const res = await fetch('/get-messages');
            const data = await res.json();
            const container = document.getElementById('messagesList');
            if (data.messages.length === 0) container.innerHTML = '<p>No messages yet.</p>';
            else {
                let html = '';
                const grouped = {};
                data.messages.forEach(msg => { if(!grouped[msg.conversation_id]) grouped[msg.conversation_id] = []; grouped[msg.conversation_id].push(msg); });
                for (let convId in grouped) {
                    const msgs = grouped[convId];
                    const otherUser = msgs[0].from_name === currentUser ? msgs[0].to_name : msgs[0].from_name;
                    html += `<div class="candidate-card"><h4>💬 Conversation with: ${otherUser}</h4>`;
                    msgs.forEach(msg => {
                        const isMe = msg.from_name === currentUser;
                        html += `<div style="margin-top:10px; padding:10px; background:${isMe ? '#e2e8f0' : '#f8fafc'}; border-radius:8px;">
                            <strong>${isMe ? 'You' : msg.from_name}:</strong> ${msg.message}<div style="font-size:11px; color:#94a3b8;">${msg.created_at}</div></div>`;
                    });
                    html += `<div style="margin-top:15px;"><textarea id="reply_${convId}" class="message-input" placeholder="Type your reply..."></textarea>
                    <button class="btn-contact" onclick="sendReply('${convId}', '${otherUser}')">Send Reply</button></div></div>`;
                }
                container.innerHTML = html;
            }
        }
        
        async function sendReply(conversationId, toUser) {
            const msgBox = document.getElementById(`reply_${conversationId}`);
            const message = msgBox.value;
            if (!message.trim()) return;
            const fd = new FormData();
            fd.append('to_user', toUser);
            fd.append('message', message);
            fd.append('conversation_id', conversationId);
            await fetch('/send-reply', { method: 'POST', body: fd });
            msgBox.value = '';
            loadMessages();
        }
    </script>
</body>
</html>
"""

# ============================================================
# ADMIN DASHBOARD HTML
# ============================================================
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f8fafc; }
        header { background: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #e2e8f0; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
        .logout-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; border: none; margin-left: 15px; cursor: pointer; font-weight: 600; }
        .logout-btn:hover { background: #0f172a; }
        .home-btn { background: #1e293b; padding: 8px 20px; border-radius: 8px; color: white; text-decoration: none; margin-right: 10px; font-weight: 600; }
        .home-btn:hover { background: #0f172a; }
        .container { max-width: 1200px; margin: 40px auto; padding: 0 20px; }
        .card { background: white; border-radius: 20px; padding: 30px; margin-bottom: 30px; border: 1px solid #e2e8f0; overflow-x: auto; }
        .card h2 { margin-bottom: 20px; color: #1e293b; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f8fafc; font-weight: 600; color: #1e293b; }
        .delete-btn { background: #ef4444; color: white; border: none; padding: 5px 12px; border-radius: 5px; cursor: pointer; }
        .admin-note { background: #fef3c7; padding: 15px; border-radius: 10px; margin-bottom: 20px; color: #92400e; }
        .confirm-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5);
            display: flex; justify-content: center; align-items: center; z-index: 1000;
        }
        .confirm-box { background: white; padding: 30px; border-radius: 20px; text-align: center; max-width: 400px; }
        .confirm-box button { margin: 10px; padding: 10px 20px; border-radius: 8px; cursor: pointer; }
        .confirm-yes { background: #ef4444; color: white; border: none; }
        .confirm-no { background: #e2e8f0; color: #1e293b; border: none; }
    </style>
</head>
<body>
    <header>
        <div class="logo">🛡️ Admin Dashboard</div>
        <div>
            <a href="/" class="home-btn">🏠 Home</a>
            <span>Welcome, <strong id="username"></strong>!</span>
            <button class="logout-btn" onclick="showLogoutConfirm()">Logout</button>
        </div>
    </header>
    <div class="container">
        <div class="admin-note"><strong>👑 Admin Access:</strong> You have full control over the platform.</div>
        <div class="card"><h2>👥 Registered Users</h2><table id="usersTable"><thead><tr><th>Username</th><th>Role</th><th>Full Name</th><th>Email</th><th>Action</th></tr></thead><tbody id="usersBody"></tbody></table></div>
        <div class="card"><h2>📋 All Job Applications</h2><table id="appsTable"><thead><tr><th>Job Title</th><th>Candidate</th><th>Match Score</th><th>Status</th><th>Date</th></tr></thead><tbody id="appsBody"></tbody></table></div>
        <div class="card"><h2>💰 All Payments</h2><table id="paymentsTable"><thead><tr><th>User</th><th>Amount</th><th>Type</th><th>Status</th><th>Date</th></tr></thead><tbody id="paymentsBody"></tbody></td></div>
        <div class="card"><h2>💬 All Messages</h2><table id="msgsTable"><thead><tr><th>From</th><th>To</th><th>Message</th><th>Date</th></tr></thead><tbody id="msgsBody"></tbody></table></div>
    </div>
    <div id="confirmModal" style="display:none;" class="confirm-modal">
        <div class="confirm-box"><h3>Confirm Logout</h3><p>Are you sure you want to logout?</p>
        <button class="confirm-yes" onclick="logout()">Yes</button><button class="confirm-no" onclick="closeModal()">Cancel</button></div>
    </div>
    <script>
        let currentUser = '{{ username }}';
        document.getElementById('username').innerText = currentUser;
        
        function showLogoutConfirm() { document.getElementById('confirmModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('confirmModal').style.display = 'none'; }
        function logout() { window.location.href = '/logout'; }
        
        async function loadUsers() {
            const res = await fetch('/admin/users');
            const users = await res.json();
            const body = document.getElementById('usersBody');
            body.innerHTML = '';
            users.forEach(u => {
                body.innerHTML += `<tr><td>${u.username}</td><td>${u.role}</td><td>${u.full_name || '-'}</td><td>${u.email || '-'}</td>
                <td>${u.username !== 'admin' ? `<button class="delete-btn" onclick="del('${u.username}')">Delete</button>` : 'Admin'}</td></tr>`;
            });
        }
        async function del(username) { if(confirm('Delete this user?')) { await fetch(`/admin/delete-user/${username}`, { method: 'POST' }); loadUsers(); } }
        async function loadApplications() {
            const res = await fetch('/admin/applications');
            const apps = await res.json();
            const body = document.getElementById('appsBody');
            body.innerHTML = '';
            apps.forEach(app => { body.innerHTML += `<tr><td>${app.job_title}</td><td>${app.candidate_name}</td><td>${app.match_score}%</td><td>${app.status}</td><td>${app.applied_at || ''}</td></tr>`; });
        }
        async function loadPayments() {
            const res = await fetch('/admin/payments');
            const payments = await res.json();
            const body = document.getElementById('paymentsBody');
            body.innerHTML = '';
            payments.forEach(p => { body.innerHTML += `<tr><td>${p.user}</td><td>${p.amount} ETB</td><td>${p.type}</td><td>${p.status}</td><td>${p.date}</td></tr>`; });
        }
        async function loadMessages() {
            const res = await fetch('/admin/messages');
            const msgs = await res.json();
            const body = document.getElementById('msgsBody');
            body.innerHTML = '';
            msgs.forEach(msg => { body.innerHTML += `<tr><td>${msg.from_name}</td><td>${msg.to_name}</td><td>${msg.message.substring(0, 100)}${msg.message.length > 100 ? '...' : ''}</td><td>${msg.created_at}</td></tr>`; });
        }
        loadUsers(); loadApplications(); loadPayments(); loadMessages();
    </script>
</body>
</html>
"""

# ============================================================
# ROUTES
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=HOME_HTML)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return HTMLResponse(content=LOGIN_HTML)

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in users and users[username]["password"] == password:
        request.session["user"] = {"username": username, "role": users[username]["role"]}
        if users[username]["role"] == "employer":
            return RedirectResponse(url="/employer", status_code=302)
        elif users[username]["role"] == "admin":
            return RedirectResponse(url="/admin", status_code=302)
        return RedirectResponse(url="/seeker", status_code=302)
    return RedirectResponse(url="/login?error=Invalid%20credentials", status_code=302)

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return HTMLResponse(content=REGISTER_HTML)

@app.post("/register")
async def register(request: Request, full_name: str = Form(...), username: str = Form(...), 
                   email: str = Form(...), password: str = Form(...), role: str = Form(...)):
    if username in users:
        return RedirectResponse(url="/register?error=Username%20exists", status_code=302)
    users[username] = {"password": password, "role": role, "full_name": full_name, "email": email}
    return RedirectResponse(url="/login?registered=success", status_code=302)

@app.get("/seeker", response_class=HTMLResponse)
async def seeker(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "seeker":
        return RedirectResponse(url="/login", status_code=302)
    return HTMLResponse(content=SEEKER_HTML.replace("{{ username }}", user["username"]))

@app.get("/employer", response_class=HTMLResponse)
async def employer(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "employer":
        return RedirectResponse(url="/login", status_code=302)
    return HTMLResponse(content=EMPLOYER_HTML.replace("{{ username }}", user["username"]))

@app.get("/admin", response_class=HTMLResponse)
async def admin(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return RedirectResponse(url="/login", status_code=302)
    return HTMLResponse(content=ADMIN_HTML.replace("{{ username }}", user["username"]))

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

# ============================================================
# API ENDPOINTS
# ============================================================

@app.post("/match-cv")
async def match_cv(cv: UploadFile = File(...)):
    sorted_jobs = sorted(FIXED_JOBS, key=lambda x: x["match_score"], reverse=True)
    return {"jobs": sorted_jobs}

@app.post("/get-learning-plan")
async def get_learning_plan(request: Request):
    data = await request.json()
    skills = data.get('skills', [])
    recommendations = get_learning_recommendations(skills)
    return {"recommendations": recommendations, "match_score": "Based on your skills gap analysis"}

@app.post("/apply-job")
async def apply_job(request: Request, job_id: int = Form(...), job_title: str = Form(...), 
                    company: str = Form(...), match_score: float = Form(...), message: str = Form("")):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    applications.append({
        "id": len(applications) + 1,
        "candidate_name": user["username"],
        "job_id": job_id,
        "job_title": job_title,
        "company": company,
        "match_score": match_score,
        "status": "Pending Review",
        "message": message,
        "applied_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return RedirectResponse(url="/seeker", status_code=302)

@app.post("/post-job-and-match")
async def post_job_and_match(request: Request, title: str = Form(...), location: str = Form(...),
                              description: str = Form(...), skills: str = Form(...), salary: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return {"success": False, "error": "Not authenticated"}
    
    payments.append({
        "id": len(payments) + 1,
        "user": user["username"],
        "amount": 50,
        "type": "Job Posting",
        "status": "Completed",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    job_skills_lower = [s.strip().lower() for s in skills.split(',')]
    
    # Use sample candidates for matching
    candidates = [
        {"id": 1, "name": "Meron Alemu", "skills": ["python", "javascript", "react", "sql"], "experience": "3 years", "education": "BSc CS", "email": "meron@example.com"},
        {"id": 2, "name": "Kebede Tesfaye", "skills": ["java", "spring", "sql", "docker"], "experience": "5 years", "education": "BSc SE", "email": "kebede@example.com"},
        {"id": 3, "name": "Tigist Worku", "skills": ["javascript", "react", "node.js", "mongodb"], "experience": "4 years", "education": "BSc IT", "email": "tigist@example.com"},
        {"id": 4, "name": "Abebech Demeke", "skills": ["python", "machine learning", "pandas", "sql"], "experience": "2 years", "education": "MSc DS", "email": "abebech@example.com"},
        {"id": 5, "name": "Yonas Desta", "skills": ["python", "django", "postgresql", "aws"], "experience": "3 years", "education": "MSc CS", "email": "yonas@example.com"},
    ]
    
    results = []
    for c in candidates:
        candidate_skills_lower = [s.lower() for s in c["skills"]]
        matched = sum(1 for skill in candidate_skills_lower if skill in job_skills_lower)
        score = int((matched / len(candidate_skills_lower)) * 100) if len(candidate_skills_lower) > 0 else 50
        results.append({
            "id": c["id"],
            "name": c["name"],
            "skills": ", ".join(candidate_skills_lower),
            "experience": c["experience"],
            "education": c["education"],
            "email": c["email"],
            "match_score": max(score, 50)
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {"success": True, "candidates": results[:5]}

@app.post("/post-job-from-pdf")
async def post_job_from_pdf(request: Request, job_desc: UploadFile = File(...)):
    user = request.session.get("user")
    if not user:
        return {"success": False, "error": "Not authenticated"}
    
    pdf = PyPDF2.PdfReader(job_desc.file)
    text = ""
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted
    
    payments.append({
        "id": len(payments) + 1,
        "user": user["username"],
        "amount": 50,
        "type": "Job Posting (PDF)",
        "status": "Completed",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    
    # Sample candidates for matching
    candidates = [
        {"id": 1, "name": "Meron Alemu", "skills": ["python", "javascript", "react", "sql"], "experience": "3 years", "education": "BSc CS", "email": "meron@example.com"},
        {"id": 2, "name": "Kebede Tesfaye", "skills": ["java", "spring", "sql", "docker"], "experience": "5 years", "education": "BSc SE", "email": "kebede@example.com"},
        {"id": 3, "name": "Tigist Worku", "skills": ["javascript", "react", "node.js", "mongodb"], "experience": "4 years", "education": "BSc IT", "email": "tigist@example.com"},
        {"id": 4, "name": "Abebech Demeke", "skills": ["python", "machine learning", "pandas", "sql"], "experience": "2 years", "education": "MSc DS", "email": "abebech@example.com"},
        {"id": 5, "name": "Yonas Desta", "skills": ["python", "django", "postgresql", "aws"], "experience": "3 years", "education": "MSc CS", "email": "yonas@example.com"},
    ]
    
    text_lower = text.lower()
    results = []
    for c in candidates:
        candidate_skills_lower = [s.lower() for s in c["skills"]]
        matched = sum(1 for skill in candidate_skills_lower if skill in text_lower)
        score = int((matched / len(candidate_skills_lower)) * 100) if len(candidate_skills_lower) > 0 else 50
        results.append({
            "id": c["id"],
            "name": c["name"],
            "skills": ", ".join(c["skills"]),
            "experience": c["experience"],
            "education": c["education"],
            "email": c["email"],
            "match_score": max(score, 50)
        })
    results.sort(key=lambda x: x["match_score"], reverse=True)
    
    return {"success": True, "candidates": results[:5]}

@app.post("/send-message")
async def send_message(request: Request, candidate_id: int = Form(...), candidate_name: str = Form(...),
                       candidate_email: str = Form(...), message: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return {"error": "Not authenticated"}
    
    conversation_id = f"{min(user['username'], candidate_name)}_{max(user['username'], candidate_name)}"
    
    messages.append({
        "id": len(messages) + 1,
        "conversation_id": conversation_id,
        "from_name": user["username"],
        "to_name": candidate_name,
        "to_email": candidate_email,
        "message": message,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return {"success": True}

@app.post("/send-reply")
async def send_reply(request: Request, to_user: str = Form(...), message: str = Form(...), conversation_id: str = Form(...)):
    user = request.session.get("user")
    if not user:
        return {"error": "Not authenticated"}
    
    messages.append({
        "id": len(messages) + 1,
        "conversation_id": conversation_id,
        "from_name": user["username"],
        "to_name": to_user,
        "to_email": f"{to_user}@example.com",
        "message": message,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    return {"success": True}

@app.get("/get-applications")
async def get_applications(request: Request):
    user = request.session.get("user")
    if not user:
        return {"applications": []}
    return {"applications": [a for a in applications if a["candidate_name"] == user["username"]]}

@app.get("/get-messages")
async def get_messages(request: Request):
    user = request.session.get("user")
    if not user:
        return {"messages": []}
    user_msgs = [m for m in messages if m["from_name"] == user["username"] or m["to_name"] == user["username"]]
    return {"messages": user_msgs}

@app.get("/get-payments")
async def get_payments(request: Request):
    user = request.session.get("user")
    if not user:
        return {"payments": []}
    return {"payments": [p for p in payments if p["user"] == user["username"]]}

# ============================================================
# ADMIN API ENDPOINTS
# ============================================================

@app.get("/admin/users")
async def admin_users(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return []
    return [{"username": u, "role": d["role"], "full_name": d.get("full_name", ""), "email": d.get("email", "")} for u, d in users.items()]

@app.post("/admin/delete-user/{username}")
async def admin_delete_user(request: Request, username: str):
    user = request.session.get("user")
    if not user or user["role"] != "admin" or username == "admin":
        return {"error": "Unauthorized"}
    if username in users:
        del users[username]
    return {"success": True}

@app.get("/admin/applications")
async def admin_applications(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return []
    return applications

@app.get("/admin/payments")
async def admin_payments(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return []
    return payments

@app.get("/admin/messages")
async def admin_messages(request: Request):
    user = request.session.get("user")
    if not user or user["role"] != "admin":
        return []
    return messages

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("✅ SERVER READY!")
    print("=" * 60)
    print("🔑 LOGIN CREDENTIALS:")
    print("   👑 Admin:    admin / admin123")
    print("   👤 Job Seeker: (register new account)")
    print("   🏢 Employer:   (register new account)")
    print("=" * 60)
    print("📍 ACCESS PAGES:")
    print("   🏠 Home:      http://localhost:5000")
    print("   👑 Admin:     http://localhost:5000/admin")
    print("   👤 Seeker:    http://localhost:5000/seeker")
    print("   🏢 Employer:  http://localhost:5000/employer")
    print("=" * 60)
    print("📚 LEARNING RECOMMENDATIONS: Enabled for job seekers")
    print("💰 PAYMENTS: Recorded and visible in admin dashboard")
    print("💬 TWO-WAY MESSAGING: Enabled")
    print("=" * 60 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=5000)