import argparse
import os
import sys
import http.server
import socketserver
import json
import re
import webbrowser
from dotenv import load_dotenv

# Import our custom modules
from src.db import JobDB
from src.imap_client import GmailClient
from src.parser import clean_email_html
from src.evaluator import JobEvaluator
from src.generator import generate_dashboard

load_dotenv()

# Custom HTTP Server for Dashboard with status update API
class DashboardHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence standard HTTP logging to keep console clean
        pass

    def do_GET(self):
        # Serve the generated dashboard
        if self.path in ["/", "/index.html", "/dashboard.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                with open("dashboard.html", "rb") as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"<h1>Dashboard not generated yet. Run Python main.py first!</h1>")
        else:
            # Fallback for images, files
            super().do_GET()

    def do_POST(self):
        # Route: API endpoint to update job status
        match = re.match(r"^/api/jobs/(\d+)/status$", self.path)
        if match:
            job_id = int(match.group(1))
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                new_status = data.get("status")
                if new_status in ["new", "applied", "rejected"]:
                    db = JobDB()
                    success = db.update_job_status(job_id, new_status)
                    if success:
                        # Regenerate static html in database update
                        generate_dashboard(db.get_all_jobs())
                        
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                        return
            except Exception as e:
                print(f"Error updating status: {e}")
                
        self.send_response(400)
        self.end_headers()

def run_server(port=8000):
    handler = DashboardHTTPHandler
    # Bind to localhost
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        print(f"\\n[INFO] Dashboard server running at: {url}")
        print("[INFO] Press Ctrl+C to stop the server.")
        # Open in default browser automatically
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\n[INFO] Server stopped.")

def run_dry_run():
    print("[INFO] Starting Dry-Run using a simulated job email...")
    
    # Check if DB needs initialization
    db = JobDB()
    evaluator = JobEvaluator()
    
    # 1. Simulated Job Email (LinkedIn-like Job Alert)
    mock_email = {
        "message_id": "mock_email_linkedin_123456",
        "sender": "jobs-listings@linkedin.com",
        "subject": "LinkedIn Job Alert: Director of Product Management - Bengaluru",
        "date": "2026-06-11 10:00:00",
        "body": """
        <div>
          <h1>Director of Product Management</h1>
          <h2>Grab - Bengaluru, Karnataka, India</h2>
          <p><strong>About Grab:</strong> Grab is Southeast Asia's leading superapp. We are expanding our tech center in Bengaluru and looking for a Director of Product Management to lead our payments platform division.</p>
          
          <p><strong>Responsibilities:</strong></p>
          <ul>
            <li>Define the long-term vision, strategy, and roadmap for fintech payments globally.</li>
            <li>Lead and scale a team of 12+ Product Managers and Product Owners in Bengaluru.</li>
            <li>Collaborate with engineering, analytics, design, and operations heads to deliver products.</li>
          </ul>

          <p><strong>Requirements:</strong></p>
          <ul>
            <li>12+ years of overall experience with 10+ years in Product Management.</li>
            <li>Strong experience in Fintech, Payments, or Transactional Platforms.</li>
            <li>Proven leadership capability managing other high-performing PMs.</li>
            <li>MBA or technical degree from a premier institute is preferred.</li>
          </ul>

          <p><strong>Location:</strong> Bengaluru (Hybrid - 3 days in office)</p>
          <p><strong>Salary Range:</strong> ₹6,500,000 - ₹9,000,000 INR per annum</p>
          
          <p><a href="https://linkedin.com/jobs/view/grab-director-pm">Click here to Apply Now</a></p>
        </div>
        """
    }
    
    if db.is_email_processed(mock_email["message_id"]):
        print("[INFO] Mock email has already been processed. Fetching jobs list and generating dashboard...")
        jobs = db.get_all_jobs()
        generate_dashboard(jobs)
        return
        
    print(f"Cleaned Body Preview:\\n{clean_email_html(mock_email['body'])[:200]}...")
    
    # 2. Evaluate
    print("[INFO] Evaluating job using Gemini API...")
    if not evaluator.api_key:
        print("[WARNING] No GEMINI_API_KEY found. Generating a mock evaluation for visualization.")
        evaluation = {
            "job_title": "Director of Product Management",
            "company": "Grab",
            "location": "Bengaluru",
            "job_type": "Hybrid",
            "experience_required": "12+ years overall, 10+ PM",
            "relevance_score": 9,
            "explanation": "Perfect match: Matches role (Director), location (Bengaluru), and requires 10+ years of experience in product leadership.",
            "skills": ["Fintech", "Payments", "Product Strategy", "Team Management", "Scaling Platforms"],
            "salary": "₹6,500,000 - ₹9,000,000 INR"
        }
    else:
        # Call Gemini
        cleaned_body = clean_email_html(mock_email["body"])
        evaluation = evaluator.evaluate_email(
            email_subject=mock_email["subject"],
            email_sender=mock_email["sender"],
            email_body=cleaned_body
        )
    
    print(f"Gemini Evaluation Result:")
    print(f" - Title: {evaluation['job_title']} at {evaluation['company']}")
    print(f" - Score: {evaluation['relevance_score']}/10")
    print(f" - Reason: {evaluation['explanation']}")
    
    # 3. Store
    job_data = {
        "email_message_id": mock_email["message_id"],
        "email_date": mock_email["date"],
        "sender": mock_email["sender"],
        "subject": mock_email["subject"],
        **evaluation
    }
    
    db.insert_job(job_data)
    db.mark_email_processed(mock_email["message_id"])
    print("[INFO] Job saved to jobs.db")
    
    # 4. Generate Dashboard
    generate_dashboard(db.get_all_jobs())
    print("[SUCCESS] Dry-run complete. Run 'python main.py --serve' to view the dashboard.")

def run_fetch_pipeline():
    print("[INFO] Starting Gmail Job Email Fetcher & Matcher pipeline...")
    
    db = JobDB()
    evaluator = JobEvaluator()
    
    # Verify API key
    if not evaluator.api_key:
        print("[ERROR] GEMINI_API_KEY is not set. Cannot run job evaluation.")
        print("[ERROR] Please add your GEMINI_API_KEY in the .env file.")
        sys.exit(1)
        
    client = GmailClient()
    try:
        print("[INFO] Connecting to Gmail IMAP...")
        client.connect()
        print("[INFO] Searching for job emails...")
        emails = client.fetch_job_emails(max_emails=15)
    except Exception as e:
        print(f"[ERROR] Failed to fetch emails: {e}")
        print("[ERROR] Please verify your EMAIL_ADDRESS and EMAIL_PASSWORD (App Password) in the .env file.")
        sys.exit(1)
    finally:
        client.disconnect()

    if not emails:
        print("[INFO] No new unread job-related emails found in your inbox.")
        # Regenerate dashboard to make sure it exists
        generate_dashboard(db.get_all_jobs())
        return

    print(f"[INFO] Found {len(emails)} unread job-related emails. Checking for duplicates...")
    new_jobs_added = 0

    for idx, mail in enumerate(emails):
        msg_id = mail["message_id"]
        
        # Check if already processed
        if db.is_email_processed(msg_id):
            continue
            
        print(f"\n[{idx+1}/{len(emails)}] Processing: \"{mail['subject']}\"")
        
        # Clean HTML body
        cleaned_body = clean_email_html(mail["body"])
        
        # Limit token count (Gemini Flash can handle easily, but keeping text clean is good)
        if len(cleaned_body) > 12000:
            cleaned_body = cleaned_body[:12000] + "...\\n[Text Truncated]"

        print(f" -> Sending description to Gemini for evaluation...")
        evaluation = evaluator.evaluate_email(
            email_subject=mail["subject"],
            email_sender=mail["sender"],
            email_body=cleaned_body
        )
        
        # Skip emails classified as non-jobs (score of 0 and explanation "Not a job email")
        if evaluation["relevance_score"] == 0 and "not a job" in evaluation["explanation"].lower():
            print(f" -> Skipped (Not a job email).")
            # Still mark as processed so we don't fetch it again
            db.mark_email_processed(msg_id)
            continue

        # Insert to DB
        job_record = {
            "email_message_id": msg_id,
            "email_date": mail["date"],
            "sender": mail["sender"],
            "subject": mail["subject"],
            **evaluation
        }
        
        db.insert_job(job_record)
        db.mark_email_processed(msg_id)
        
        print(f" -> Match Score: {evaluation['relevance_score']}/10 ({evaluation['job_title']} at {evaluation['company']})")
        new_jobs_added += 1

    print(f"\\n[INFO] Pipeline complete. Added {new_jobs_added} new matching jobs.")
    
    # Regenerate dashboard with the complete set of jobs
    generate_dashboard(db.get_all_jobs())
    print("[SUCCESS] Dashboard regenerated. Run 'python main.py --serve' to view results.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Radar AI Agent")
    parser.add_argument("--serve", action="store_true", help="Start the dashboard local web server")
    parser.add_argument("--dry-run", action="store_true", help="Simulate parsing using mock email data")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the dashboard server on (default 8000)")
    
    args = parser.parse_args()
    
    if args.serve:
        run_server(port=args.port)
    elif args.dry_run:
        run_dry_run()
    else:
        # Default is to run fetcher pipeline
        run_fetch_pipeline()
