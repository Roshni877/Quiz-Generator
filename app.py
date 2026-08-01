from flask import Flask, render_template, request, session, jsonify, redirect, url_for, make_response
from data_loader import QuizDataLoader
import os
from datetime import datetime
import io
import json
# Make reportlab optional — if unavailable, PDF export will be disabled
PDF_AVAILABLE = True
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except Exception:
    PDF_AVAILABLE = False

app = Flask(__name__)
app.secret_key = 'quiz_app_secret_key_2024'

# Initialize data loader
data_loader = QuizDataLoader()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/categories')
def categories():
    """Show category selection"""
    categories_list = data_loader.get_categories()
    return render_template('categories.html', categories=categories_list)

@app.route('/quiz/<category>')
def start_quiz(category):
    """Start a new quiz with selected category"""
    questions = data_loader.fetch_questions(category)
    
    if not questions:
        return redirect(url_for('categories'))
    
    # Store in session
    session['questions'] = questions
    session['category'] = category
    session['current_index'] = 0
    session['score'] = 0
    session['answers'] = []
    
    return redirect(url_for('quiz'))

@app.route('/quiz')
def quiz():
    """Quiz page"""
    if 'questions' not in session or not session['questions']:
        return redirect(url_for('categories'))
    
    questions = session['questions']
    current_index = session.get('current_index', 0)
    
    if current_index >= len(questions):
        return redirect(url_for('results'))
    
    current_question = questions[current_index]
    
    return render_template(
        'quiz.html',
        question=current_question,
        question_number=current_index + 1,
        total_questions=len(questions),
        progress_percent=((current_index) / len(questions)) * 100
    )

@app.route('/api/submit-answer', methods=['POST'])
def submit_answer():
    """Submit answer via API"""
    if 'questions' not in session:
        return jsonify({'error': 'No quiz in progress'}), 400
    
    data = request.json
    selected_answer = data.get('answer', '')
    
    questions = session['questions']
    current_index = session.get('current_index', 0)
    
    if current_index >= len(questions):
        return jsonify({'error': 'Quiz completed'}), 400
    
    current_question = questions[current_index]
    is_correct = selected_answer == current_question['answer']
    
    # Track answer
    session['answers'].append({
        'question': current_question['question'],
        'user_answer': selected_answer,
        'correct_answer': current_question['answer'],
        'is_correct': is_correct,
        'explanation': current_question['explanation']
    })
    
    if is_correct:
        session['score'] = session.get('score', 0) + 1
    
    session.modified = True
    
    return jsonify({
        'is_correct': is_correct,
        'correct_answer': current_question['answer'],
        'explanation': current_question['explanation']
    })

@app.route('/api/next-question', methods=['POST'])
def next_question():
    """Move to next question"""
    if 'questions' not in session:
        return jsonify({'error': 'No quiz in progress'}), 400
    
    current_index = session.get('current_index', 0)
    session['current_index'] = current_index + 1
    session.modified = True
    
    questions = session['questions']
    if session['current_index'] >= len(questions):
        return jsonify({'redirect': url_for('results')})
    
    return jsonify({'success': True})

@app.route('/results')
def results():
    """Show results page"""
    if 'questions' not in session:
        return redirect(url_for('categories'))
    
    questions = session['questions']
    answers = session.get('answers', [])
    score = session.get('score', 0)
    category = session.get('category', 'Unknown')
    
    percentage = (score / len(questions)) * 100
    grade = 'A+' if percentage >= 90 else 'A' if percentage >= 80 else 'B' if percentage >= 70 else 'C' if percentage >= 60 else 'D'
    
    # Generate personalized study plan based on wrong answers
    study_plan = generate_study_plan(answers)

    # If user saved a custom version during review, show that instead
    custom = session.get('custom_plan')
    if custom:
        study_plan = {'schedule': study_plan.get('schedule', {}), 'text': custom}

    return render_template(
        'results.html',
        score=score,
        total=len(questions),
        percentage=percentage,
        grade=grade,
        category=category,
        answers=answers,
        study_plan=study_plan,
        pdf_available=PDF_AVAILABLE
    )


def generate_study_plan(answers, days=7):
    """Create a simple personalized study plan from answers.
    Prioritizes topics with most wrong answers and spreads over `days`.
    Returns a dict with schedule and a plain-text version.
    """
    # Count wrong answers by topic/category or by keywords
    weakness_counts = {}
    for a in answers:
        if not a.get('is_correct'):
            topic = a.get('category') or a.get('question')[:50]
            weakness_counts[topic] = weakness_counts.get(topic, 0) + 1

    # If no detailed categories, fallback to generic topics grouped from questions text
    if not weakness_counts:
        # No wrong answers — recommend mixed review
        schedule = {f'Day {i+1}': 'Mixed review: 10 practice questions' for i in range(days)}
        plan_text = '\n'.join([f"{k}: {v}" for k, v in schedule.items()])
        return {'schedule': schedule, 'text': plan_text}

    # Sort weaknesses by count
    sorted_weak = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)

    # Build schedule: allocate top weaknesses across days
    schedule = {}
    day = 0
    for topic, count in sorted_weak:
        # assign this topic to a day (round-robin)
        key = f'Day {(day % days) + 1}'
        entry = schedule.get(key, [])
        entry.append(f"Practice {count + 2} Qs on: {topic}")
        schedule[key] = entry
        day += 1

    # Ensure each day has at least one item
    for i in range(days):
        key = f'Day {i+1}'
        if key not in schedule:
            schedule[key] = ["Mixed review: 10 practice questions"]

    # Convert lists to readable strings
    schedule_readable = {k: '; '.join(v) for k, v in schedule.items()}
    plan_text = '\n'.join([f"{k}: {v}" for k, v in schedule_readable.items()])

    return {'schedule': schedule_readable, 'text': plan_text}


@app.route('/download-study-plan')
def download_study_plan():
    """Provide study plan as downloadable text file."""
    answers = session.get('answers', [])
    if not answers:
        return redirect(url_for('results'))

    study_plan = generate_study_plan(answers)
    text = study_plan.get('text', '')

    buf = io.BytesIO()
    buf.write(text.encode('utf-8'))
    buf.seek(0)

    resp = make_response(buf.read())
    resp.headers.set('Content-Type', 'text/plain')
    resp.headers.set('Content-Disposition', 'attachment', filename='study_plan.txt')
    return resp


@app.route('/api/save-plan', methods=['POST'])
def api_save_plan():
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    session['custom_plan'] = text
    session.modified = True
    return jsonify({'success': True})


@app.route('/download-study-plan-pdf', methods=['POST'])
def download_study_plan_pdf():
    # Accept JSON or form data with 'text'
    if not PDF_AVAILABLE:
        # PDF support not available — redirect to TXT download instead
        return redirect(url_for('download_study_plan'))

    data = None
    if request.is_json:
        data = request.get_json()
        text = data.get('text', '')
    else:
        text = request.form.get('text', '')

    if not text:
        # fallback to session plan
        text = session.get('custom_plan') or generate_study_plan(session.get('answers', [])).get('text', '')

    buf = io.BytesIO()
    p = canvas.Canvas(buf, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin
    p.setFont('Helvetica-Bold', 14)
    p.drawString(margin, y, 'Personalized Study Plan')
    p.setFont('Helvetica', 10)
    y -= 30

    # Wrap lines
    for line in text.split('\n'):
        # simple wrapping
        parts = [line[i:i+90] for i in range(0, len(line), 90)]
        for part in parts:
            if y < margin + 20:
                p.showPage()
                y = height - margin
                p.setFont('Helvetica', 10)
            p.drawString(margin, y, part)
            y -= 14

    p.showPage()
    p.save()
    buf.seek(0)

    resp = make_response(buf.read())
    resp.headers.set('Content-Type', 'application/pdf')
    resp.headers.set('Content-Disposition', 'attachment', filename='study_plan.pdf')
    return resp

@app.route('/restart')
def restart():
    """Restart quiz - clear session"""
    session.clear()
    return redirect(url_for('categories'))

@app.route('/home')
def home():
    """Go back home"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
