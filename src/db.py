import sqlite3
import json
import os

class JobDB:
    def __init__(self, db_path="jobs.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table to keep track of processed emails (using Message-ID or custom UID)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_emails (
                    email_id TEXT PRIMARY KEY,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table for job records
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email_message_id TEXT UNIQUE,
                    email_date TEXT,
                    sender TEXT,
                    subject TEXT,
                    job_title TEXT,
                    company TEXT,
                    location TEXT,
                    job_type TEXT,
                    experience_required TEXT,
                    relevance_score INTEGER,
                    explanation TEXT,
                    skills TEXT,
                    salary TEXT,
                    status TEXT DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def is_email_processed(self, email_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_emails WHERE email_id = ?", (email_id,))
            return cursor.fetchone() is not None

    def mark_email_processed(self, email_id):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO processed_emails (email_id) VALUES (?)", (email_id,))
            conn.commit()

    def insert_job(self, job_data):
        """
        job_data: dict containing:
            email_message_id, email_date, sender, subject, job_title, company,
            location, job_type, experience_required, relevance_score, explanation, skills, salary
        """
        # Convert skills list to JSON string if it's a list
        skills = job_data.get("skills", [])
        if isinstance(skills, list):
            skills = json.dumps(skills)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO jobs (
                        email_message_id, email_date, sender, subject, job_title, company,
                        location, job_type, experience_required, relevance_score, explanation, skills, salary, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'new')
                """, (
                    job_data.get("email_message_id"),
                    job_data.get("email_date"),
                    job_data.get("sender"),
                    job_data.get("subject"),
                    job_data.get("job_title"),
                    job_data.get("company"),
                    job_data.get("location"),
                    job_data.get("job_type"),
                    job_data.get("experience_required"),
                    job_data.get("relevance_score"),
                    job_data.get("explanation"),
                    skills,
                    job_data.get("salary"),
                ))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                # Job with this email_message_id already exists
                return None

    def get_all_jobs(self):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY relevance_score DESC, email_date DESC")
            rows = cursor.fetchall()
            
            jobs = []
            for row in rows:
                job = dict(row)
                # Parse skills JSON back to list
                try:
                    job["skills"] = json.loads(job["skills"]) if job["skills"] else []
                except json.JSONDecodeError:
                    job["skills"] = []
                jobs.append(job)
            return jobs

    def update_job_status(self, job_id, status):
        """status should be one of 'new', 'applied', 'rejected'"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE jobs SET status = ? WHERE id = ?", (status, job_id))
            conn.commit()
            return cursor.rowcount > 0
