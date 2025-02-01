import fitz  # PyMuPDF
from flask import Flask, render_template, request, jsonify, redirect, session, flash
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError
from firebase_config.firebase import signup_user, verify_token
import google.generativeai as genai
from audio import AudioTranscriber
from job_description_parser import parse_job_description
from resume_parser import parse_resume
from rich import _console
import firebase_admin

# Initialize Firebase Admin SDK with credentials directly
cred = credentials.Certificate({
    "type": "service_account",
  "project_id": "interview-9cc2a",
  "private_key_id": "73db5f26129dc00ed0d812d197ccfb0b52529d89",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCUevqAoopeq0aq\n4WJ/X6lUOjVhoZOysLJ60wgLijMjrikeqPX011Xbv5IRj4VrfQx3RB+Q2fsrKW5Z\nMa6G51zSORm5H4xvfmX11Xel8e4eUn3RjWJ5juERFoOf1VA4Pdv91YZNgF+3NlCp\nqvdnbvjuTYCC487cujMYLmdxTqwdmYgV6a2LECKszXbTS49/iru5iU0230mI+yoV\naA4kitX9vDtTOJ6m68DmrFA+p6uMEhNqXLZJPEaMDz98vlkd452yS4Dj2vR3s2Or\nOjV8T9dRO1VVkbInatpEsLkkPjp9CPCVyl8RezdTS6+u0NX/aAozldN1eKOO7bnr\nTIVI98L5AgMBAAECggEACpaYfYrZxjV9lRr8fKvUNeruupccor4CBEs/RB9nVTCK\nwyJ2Y67lcwW+w1zSPV+N/4VOoPRCeon6Ugb+dKVUE7O5t19eEudXGwhNf3p4qhXk\n3ggwkQ2U1DSgT0oVbeVPZlMPQECa0sRfTTIhcXFS9B93vh3Dty7aDOvmOYjMMlIQ\nJpkaXY3QHSKxmz24Jku6SRYhkh5kihAAe5QOmCECZINYl4hZrqlrJHpz3EzCCQXd\nFh7LgiA9KZcqbIikaxqfljAoBk1BaEtjGFA3NmTkyhQH60ePgZ6WIngd475WdjzX\nde4vpPBQThC5yMYKS1EHp4SU0xJdWxbs1X9noV7YWQKBgQDRoLmAYqowm5xsA8EG\nDRZt11wroktjDLPgJ5AmFw9W/iO64LLH+AsSEoaie3cFVWySUdPxfGz7LLUJ61Ei\n0gpkqz+OU7VABhCHD5f1uoOGkdViLGjuqdZNA2wgLEb2Q/PopaFhsyiSZFfRWXb8\nwd4RUXymmpHfOJWsJUGOkbl2xQKBgQC1U3WGp5ueJtbIstH41cyLoJXiKZKvxAi0\nIxydWqhNbI+0TOTral+joelZzZBTgyXlOpysUa9e/fDmWYXrSw1OIIEvlj1UY8nz\nfmStqTKL6ISnB/4vsUjdD9hruwObgYINusWeygtBrynG+JiJfjZ3Y03hFxdGoHEX\nTxvpAai+pQKBgGO9Q0WwrCVAhOZnytlkNL3CcBpat9/C1XrbmBxncGcFuF5cNvQq\nMqpAokqA0Bp7kJL12A/YEcpYdTLpAcu9gDBxwmWnsl9qA0cfxj+mpJnMnWh+lNap\nfEtcS3/rUUAvCMgytlxT8APnNllnZdPRMiWvTc2/UZSRybUEbPK2pzW5AoGBAIEL\niXuwcwbF21vwL5DpD25bdfAD6DogyJTy3B18dITNeyQ1CUIlbTU2OK1Jp6pXjrOp\n1/CnHaj8DuLQ2YcP3cM5TNdCFBmn/wTEcgBJhwidDTMWdCcbA6EX8s0Qxkt4iscc\noiIU5pfzgkbxixVm9npW+Qj1dwIzkuiky1czcBVlAoGBAMhAq4WdrI0LW3JyG8eg\nv1libqC/SSe9JiIdmDV/CFQda6Lk9yF6e/K3j5ssMX0kr0k8a+QGtbawNxNYTLmX\n/5heO4BH+5uvNlUY/c1/xf8F4iwe3OwOXqqHiVVcsAq/W6W5RnBe39cuUfPA8G0W\nQWA2IZTvAx5UgSlz6Fg1bYC2\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-fbsvc@interview-9cc2a.iam.gserviceaccount.com",
  "client_id": "104905277470582170878",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40interview-9cc2a.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "AIzaSyBTxAWlKXvZ-E8rNXmnGdZdpgxQhO0V5hE"  

def parse_pdf(file):
    """Extract text from a PDF file."""
    try:
        doc = fitz.open(stream=file, filetype="pdf")  # Open the file directly from the stream
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {e}")

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyCVne5Ru2NBatL22caSJpgN_6gZxDmMPPY"  
genai.configure(api_key=GOOGLE_API_KEY)

# Global variables
transcriber = AudioTranscriber()
@app.route("/", methods=["GET", "POST"])
def login_signup():
    """Login or Signup Page."""
    if request.method == "POST":
        action = request.form.get("action")
        email = request.form.get("email")
        password = request.form.get("password")

        if action == "signup":
            result = signup_user(email, password)  # Ensure signup_user() is implemented properly
            if result["success"]:
                session["user_id"] = result["uid"]
                print("Session user_id:", session.get("user_id"))
                return redirect("/upload")
            else:
                return render_template("index.html", error=result["error"])

        elif action == "login":
            id_token = request.form.get("id_token")  # Frontend sends the Firebase ID token
            result = verify_token(id_token)
            if result["success"]:
                session["user_id"] = result["uid"]
                _console.log("Session user_id:", session.get("user_id"))
                return redirect("/upload")
            else:
                return render_template("index.html", error="Invalid credentials. Please try again.")

    return render_template("index.html")

@app.route("/verify_token", methods=["POST"])
def verify_token_route():
    """Verify Firebase token"""
    data = request.get_json()
    id_token = data.get("idToken")
    
    try:
        # Verify token
        decoded_token = auth.verify_id_token(id_token)
        user_id = decoded_token["uid"]
        
        # Store user_id in session
        session["user_id"] = user_id
        print("User ID in session:", session.get("user_id"))  # Debugging line
        
        return jsonify({"success": True})
    except Exception as e:
        print("Error verifying token:", e)  # Debugging line
        return jsonify({"success": False, "error": str(e)})

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Handle Forgot Password functionality"""
    if request.method == "POST":
        email = request.form["email"]
        
        try:
            # Send password reset email using Firebase
            auth.send_password_reset_email(email)
            flash("Password reset link sent to your email address.", "success")
            return redirect("/")
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/forgot-password")
        
    return render_template("forgot_password.html")

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Handle Reset Password functionality"""
    if request.method == "POST":
        oob_code = request.form["oobCode"]
        new_password = request.form["new_password"]
        
        try:
            # Reset password using the reset code and new password
            auth.confirm_password_reset(oob_code, new_password)
            flash("Password has been successfully reset.", "success")
            return redirect("/login")
        except FirebaseError as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect("/forgot-password")
    
    # Ensure the oobCode is passed as part of the query string
    oob_code = request.args.get('oobCode')
    if oob_code:
        return render_template("reset_password.html", oobCode=oob_code)
    else:
        flash("Invalid reset link.", "danger")
        return redirect("/forgot-password")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    """Resume and Job Description Upload Page."""
    if "user_id" not in session:
        return redirect("/")  # Redirect to login if not authenticated

    if request.method == "POST":
        resume_file = request.files.get("resume")
        job_description = request.form.get("job_description", "")

        if not resume_file or not job_description:
            return jsonify({"error": "Both resume and job description are required."}), 400

        try:
            if resume_file.filename.endswith(".pdf"):
                resume_text = parse_pdf(resume_file.read())
            else:
                return jsonify({"error": "Only PDF resumes are supported."}), 400
        except Exception as e:
            return jsonify({"error": f"Error processing resume: {e}"}), 400

        # Parse job description
        try:
            parsed_job_description = parse_job_description(job_description)
        except Exception as e:
            return jsonify({"error": f"Error parsing job description: {e}"}), 400

        return render_template("dashboard.html", resume=resume_text, job_description=parsed_job_description)

    return render_template("dashboard.html")

@app.route("/start_interview", methods=["POST"])
def start_interview():
    """Handle the start of an interview by processing the resume and job description."""
    if "user_id" not in session:
        return redirect("/")  # Redirect to login if not authenticated

    resume_text = request.form.get("resume_text", "")
    job_description = request.form.get("job_description", "")

    # Generate introduction using Gemini (from interviewee's perspective)
    try:
        model = genai.GenerativeModel("gemini-pro")
        prompt = f"""
        You are a job candidate preparing for an interview. Based on the following resume and job description, craft a professional and confident introduction for yourself as if you were speaking to the interviewer. Highlight your most relevant skills, experiences, and achievements that align with the job description.

        Resume: {resume_text}
        Job Description: {job_description}

        Your introduction should:
        1. Start with a greeting and a thank you.
        2. Briefly mention your background and key skills.
        3. Highlight 1-2 achievements or experiences that are most relevant to the job.
        4. Conclude with enthusiasm for the role and the company.

        Write the introduction in the first person (e.g., "I have experience in...").
        """
        introduction = model.generate_content(prompt).text
    except Exception as e:
        introduction = "Thank you for the opportunity to interview for this role. I’m excited to discuss how my skills and experiences align with the position."

    return render_template(
        "interview.html",
        resume=resume_text,
        job_description=job_description,
        introduction=introduction,
    )

@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        transcription = transcriber.transcribe_audio()
        if transcription.get("success"):
            return jsonify({"transcription": transcription.get("transcription")})  # Ensure transcription text is returned
        else:
            return jsonify({"error": "Could not transcribe audio."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_response', methods=['POST'])
def generate_response():
    question = request.json.get('question', '')
    resume_text = request.json.get('resume_text', '')
    job_description = request.json.get('job_description', '')

    if not question:
        return jsonify({"error": "Question is required."}), 400

    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Respond to the following interview question:
        Question: {question}
        Skills: {resume_text}
        Job: {job_description}
        """
        # Reduced prompt length to only necessary data
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/logout")
def logout():
    """Logout user."""
    session.pop("user_id", None)
    return redirect("/")

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

application = DispatcherMiddleware(app)


if __name__ == "__main__":
    run_simple("0.0.0.0", 8080, application)

