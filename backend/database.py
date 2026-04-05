import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "job_matching.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            company_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS seeker_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cv_filename TEXT,
            cv_text TEXT,
            skills TEXT,
            education TEXT,
            experience TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            skills_required TEXT,
            salary_range TEXT,
            is_active BOOLEAN DEFAULT 1,
            is_paid BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER NOT NULL,
            seeker_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            match_score REAL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            message TEXT,
            FOREIGN KEY (job_id) REFERENCES job_postings(id),
            FOREIGN KEY (seeker_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id),
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_type TEXT NOT NULL,
            job_posting_id INTEGER,
            status TEXT DEFAULT 'completed',
            transaction_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (job_posting_id) REFERENCES job_postings(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized!")

def create_user(username, email, password, role, full_name=None, company_name=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password, role, full_name, company_name) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, email, password, role, full_name, company_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        print(f"User created: {username}")
        return user_id
    except Exception as e:
        print(f"Error creating user: {e}")
        conn.close()
        return None

def get_user_by_username(username):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, role, full_name, company_name FROM users WHERE LOWER(username) = LOWER(?)", (username,))
        user = cursor.fetchone()
        conn.close()
        if user:
            return {
                "id": user[0], 
                "username": user[1], 
                "email": user[2], 
                "password": user[3], 
                "role": user[4], 
                "full_name": user[5], 
                "company_name": user[6]
            }
        return None
    except Exception as e:
        print(f"Error in get_user_by_username: {e}")
        return None

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password, role FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "email": user[2], "password": user[3], "role": user[4]}
    return None

def update_user_password(email, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE LOWER(email) = LOWER(?)", (password, email))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, full_name, company_name, created_at FROM users")
    users = cursor.fetchall()
    conn.close()
    return [{"id": u[0], "username": u[1], "email": u[2], "role": u[3], "full_name": u[4], "company_name": u[5], "created_at": u[6]} for u in users]

def save_seeker_profile(user_id, cv_filename, cv_text, skills, education, experience):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO seeker_profiles (user_id, cv_filename, cv_text, skills, education, experience, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (user_id, cv_filename, cv_text, skills, education, experience))
    conn.commit()
    conn.close()

def get_seeker_profile(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT cv_filename, cv_text, skills, education, experience FROM seeker_profiles WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    conn.close()
    if profile:
        return {"cv_filename": profile[0], "cv_text": profile[1], "skills": profile[2], "education": profile[3], "experience": profile[4]}
    return None

def create_job_posting(employer_id, title, company, location, description, skills_required, salary_range, is_paid=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_postings (employer_id, title, company, location, description, skills_required, salary_range, is_paid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (employer_id, title, company, location, description, skills_required, salary_range, is_paid))
    conn.commit()
    job_id = cursor.lastrowid
    conn.close()
    return job_id

def get_job_postings(employer_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if employer_id:
        cursor.execute("SELECT id, title, company, location, description, skills_required, salary_range, is_active, is_paid, created_at FROM job_postings WHERE employer_id = ?", (employer_id,))
    else:
        cursor.execute("SELECT id, employer_id, title, company, location, description, skills_required, salary_range, is_active, is_paid, created_at FROM job_postings WHERE is_active = 1")
    jobs = cursor.fetchall()
    conn.close()
    return jobs

def create_application(job_id, seeker_id, match_score, message=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO applications (job_id, seeker_id, match_score, message)
        VALUES (?, ?, ?, ?)
    """, (job_id, seeker_id, match_score, message))
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    return app_id

def get_applications_for_seeker(seeker_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.job_id, j.title, j.company, j.location, a.match_score, a.status, a.applied_at
        FROM applications a
        JOIN job_postings j ON a.job_id = j.id
        WHERE a.seeker_id = ?
        ORDER BY a.applied_at DESC
    """, (seeker_id,))
    apps = cursor.fetchall()
    conn.close()
    return apps

def get_applications_for_employer(employer_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.job_id, j.title, a.seeker_id, u.username, u.full_name, a.match_score, a.status, a.applied_at
        FROM applications a
        JOIN job_postings j ON a.job_id = j.id
        JOIN users u ON a.seeker_id = u.id
        WHERE j.employer_id = ?
        ORDER BY a.applied_at DESC
    """, (employer_id,))
    apps = cursor.fetchall()
    conn.close()
    return apps

def get_all_applications():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, j.title, u.username, a.match_score, a.status, a.applied_at
        FROM applications a
        JOIN job_postings j ON a.job_id = j.id
        JOIN users u ON a.seeker_id = u.id
        ORDER BY a.applied_at DESC
    """)
    apps = cursor.fetchall()
    conn.close()
    return apps

def get_all_payments():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, u.username, p.amount, p.payment_type, p.status, p.created_at
        FROM payments p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.created_at DESC
    """)
    payments = cursor.fetchall()
    conn.close()
    return payments

def send_message(application_id, sender_id, receiver_id, message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (application_id, sender_id, receiver_id, message)
        VALUES (?, ?, ?, ?)
    """, (application_id, sender_id, receiver_id, message))
    conn.commit()
    conn.close()

def get_messages(application_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sender_id, receiver_id, message, is_read, created_at
        FROM messages
        WHERE application_id = ?
        ORDER BY created_at ASC
    """, (application_id,))
    messages = cursor.fetchall()
    conn.close()
    return messages

def create_payment(user_id, amount, payment_type, job_posting_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO payments (user_id, amount, payment_type, job_posting_id, status)
        VALUES (?, ?, ?, ?, 'completed')
    """, (user_id, amount, payment_type, job_posting_id))
    conn.commit()
    payment_id = cursor.lastrowid
    conn.close()
    return payment_id

# Initialize database
init_db()
print("Database ready!")
# Add this function to database.py

def get_all_resumes_from_db():
    """Get all resumes from the resumes database"""
    resumes_db_path = os.path.join(os.path.dirname(__file__), 'resumes.db')
    
    if not os.path.exists(resumes_db_path):
        print("Resumes database not found! Run generate_resumes.py first.")
        return []
    
    conn = sqlite3.connect(resumes_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, location, skills, education, experience FROM resumes")
    resumes = cursor.fetchall()
    conn.close()
    
    return [{
        "id": r[0],
        "name": r[1],
        "email": r[2],
        "phone": r[3],
        "location": r[4],
        "skills": r[5].split(', ') if r[5] else [],
        "education": r[6],
        "experience": r[7]
    } for r in resumes]

def search_resumes_by_skills(skills_list):
    """Search resumes by matching skills"""
    resumes_db_path = os.path.join(os.path.dirname(__file__), 'resumes.db')
    
    if not os.path.exists(resumes_db_path):
        return []
    
    conn = sqlite3.connect(resumes_db_path)
    cursor = conn.cursor()
    
    # Build query
    results = []
    for skill in skills_list:
        cursor.execute("SELECT id, name, email, location, skills, education, experience FROM resumes WHERE LOWER(skills) LIKE ?", (f'%{skill.lower()}%',))
        for row in cursor.fetchall():
            if row[0] not in [r.get('id') for r in results]:
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "location": row[3],
                    "skills": row[4],
                    "education": row[5],
                    "experience": row[6]
                })
    
    conn.close()
    return results
    def get_all_resumes_from_db():
    """Get all resumes from the resumes database"""
    resumes_db_path = os.path.join(os.path.dirname(__file__), 'resumes.db')
    
    if not os.path.exists(resumes_db_path):
        print("Resumes database not found! Run generate_resumes.py first.")
        return []
    
    conn = sqlite3.connect(resumes_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, location, skills, education, experience FROM resumes")
    resumes = cursor.fetchall()
    conn.close()
    
    return [{
        "id": r[0],
        "name": r[1],
        "email": r[2],
        "phone": r[3],
        "location": r[4],
        "skills": r[5].split(', ') if r[5] else [],
        "education": r[6],
        "experience": r[7]
    } for r in resumes]

def search_resumes_by_skills(skills_list):
    """Search resumes by matching skills"""
    resumes_db_path = os.path.join(os.path.dirname(__file__), 'resumes.db')
    
    if not os.path.exists(resumes_db_path):
        return []
    
    conn = sqlite3.connect(resumes_db_path)
    cursor = conn.cursor()
    
    results = []
    for skill in skills_list:
        cursor.execute("SELECT id, name, email, location, skills, education, experience FROM resumes WHERE LOWER(skills) LIKE ?", (f'%{skill.lower()}%',))
        for row in cursor.fetchall():
            if row[0] not in [r.get('id') for r in results]:
                results.append({
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "location": row[3],
                    "skills": row[4],
                    "education": row[5],
                    "experience": row[6]
                })
    
    conn.close()
    return results