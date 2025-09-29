from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from werkzeug.utils import secure_filename
import uuid
from graph import create_workflow
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Store workflow instances by session ID
workflows = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload_cv', methods=['POST'])
def upload_cv():
    if 'cv_file' not in request.files:
        return redirect(request.url)

    file = request.files['cv_file']
    if file.filename == '':
        return redirect(request.url)

    if file and file.filename.lower().endswith('.pdf'):
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id

        # Create workflow instance for this session
        workflows[session_id] = create_workflow()

        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
        file.save(file_path)

        # Parse CV directly without workflow for now
        from nodes.parse_cv import parse_cv_node

        initial_state = {
            "cv_file_path": file_path,
            "session_id": session_id
        }

        # Execute CV parsing
        try:
            result = parse_cv_node(initial_state)

            if result.get('cv_data') and not result.get('error_message'):
                # Store result for later use
                session['cv_parse_result'] = result
                return render_template('confirm_cv.html', cv_data=result['cv_data'])
            else:
                error_msg = result.get('error_message', 'Unknown error processing CV')
                return f"Error processing CV: {error_msg}", 500
        except Exception as e:
            return f"CV parsing error: {str(e)}", 500

    return redirect(url_for('index'))

@app.route('/confirm_cv', methods=['POST'])
def confirm_cv():
    session_id = session.get('session_id')
    if not session_id or session_id not in workflows:
        return redirect(url_for('index'))

    # Get confirmed CV data from form with improved parsing
    confirmed_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        'phone': request.form.get('phone'),
        'location': request.form.get('location'),
        'summary': request.form.get('summary'),
        'skills': [skill.strip() for skill in request.form.getlist('skills') if skill.strip()],
        'experience': parse_experience_data(request.form),
        'education': parse_education_data(request.form),
        'certifications': [cert.strip() for cert in request.form.getlist('certifications') if cert.strip()]
    }

    # Store confirmed CV data in session
    session['confirmed_cv_data'] = confirmed_data

    return render_template('job_input.html')

def parse_experience_data(form):
    """Parse experience data from form fields"""
    experience = []
    titles = form.getlist('exp_title')
    companies = form.getlist('exp_company')
    starts = form.getlist('exp_start')
    ends = form.getlist('exp_end')
    responsibilities = form.getlist('exp_responsibilities')

    for i in range(len(titles)):
        if titles[i].strip():  # Only add if title is present
            exp_item = {
                'title': titles[i].strip(),
                'company': companies[i].strip() if i < len(companies) else '',
                'start_date': starts[i].strip() if i < len(starts) else '',
                'end_date': ends[i].strip() if i < len(ends) else '',
                'responsibilities': [resp.strip() for resp in responsibilities[i].split(';') if resp.strip()] if i < len(responsibilities) and responsibilities[i] else []
            }
            experience.append(exp_item)

    return experience

def parse_education_data(form):
    """Parse education data from form fields"""
    education = []
    degrees = form.getlist('edu_degree')
    institutions = form.getlist('edu_institution')
    dates = form.getlist('edu_date')
    gpas = form.getlist('edu_gpa')

    for i in range(len(degrees)):
        if degrees[i].strip():  # Only add if degree is present
            edu_item = {
                'degree': degrees[i].strip(),
                'institution': institutions[i].strip() if i < len(institutions) else '',
                'graduation_date': dates[i].strip() if i < len(dates) else '',
                'gpa': gpas[i].strip() if i < len(gpas) and gpas[i].strip() else None
            }
            education.append(edu_item)

    return education

@app.route('/analyze_job', methods=['POST'])
def analyze_job():
    session_id = session.get('session_id')
    if not session_id:
        return redirect(url_for('index'))

    job_description = request.form.get('job_description')
    confirmed_cv_data = session.get('confirmed_cv_data')

    if not job_description or not confirmed_cv_data:
        return "Missing data", 400

    try:
        # Import nodes for direct execution
        from nodes.parse_job import parse_job_node
        from nodes.compare import compare_node
        from nodes.summary import summary_node

        # Parse job description
        job_state = {
            "job_description": job_description,
            "session_id": session_id
        }
        job_result = parse_job_node(job_state)

        if job_result.get('error_message'):
            return f"Job parsing error: {job_result['error_message']}", 500

        # Compare CV with job
        compare_state = {
            "confirmed_cv_data": confirmed_cv_data,
            "job_requirements": job_result.get('job_requirements'),
            "session_id": session_id
        }
        compare_result = compare_node(compare_state)

        if compare_result.get('error_message'):
            return f"Comparison error: {compare_result['error_message']}", 500

        # Generate summary
        summary_state = {
            "comparison_result": compare_result.get('comparison_result'),
            "job_requirements": job_result.get('job_requirements'),
            "confirmed_cv_data": confirmed_cv_data,
            "session_id": session_id
        }
        final_result = summary_node(summary_state)

        if final_result.get('error_message'):
            return f"Summary error: {final_result['error_message']}", 500

        return render_template('result.html', analysis=final_result.get('final_analysis'))

    except Exception as e:
        return f"Analysis error: {str(e)}", 500

@app.route('/cleanup')
def cleanup():
    session_id = session.get('session_id')
    if session_id:
        # Clean up uploaded file
        # (In production, you might want a more sophisticated cleanup strategy)
        session.clear()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)