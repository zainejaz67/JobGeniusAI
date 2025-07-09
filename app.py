import subprocess
import requests
import time
from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
from recommender.scraper import fetch_jobs
from recommender.embedder import generate_job_embeddings

# --- Ollama automation ---
def ensure_ollama_running():
    # Check if Ollama API is up
    try:
        requests.get('http://localhost:11434', timeout=2)
        print("Ollama is already running.")
        return
    except Exception:
        print("Starting Ollama server...")
        subprocess.Popen(['ollama', 'serve'])
        # Wait for Ollama to start
        for _ in range(10):
            try:
                requests.get('http://localhost:11434', timeout=2)
                print("Ollama started.")
                return
            except Exception:
                time.sleep(1)
        print("Warning: Ollama did not start in time.")

def ensure_model_pulled(model='llama3:8b'):
    try:
        resp = requests.get('http://localhost:11434/api/tags', timeout=5)
        if model in resp.text:
            print(f"Model {model} is already pulled.")
            return
    except Exception:
        pass
    print(f"Pulling model {model}...")
    subprocess.run(['ollama', 'pull', model])

# Ensure Ollama and model are ready
ensure_ollama_running()
ensure_model_pulled('llama3:8b')

# Abbreviation mapping for user input
ABBREVIATION_MAP = {
    'ml': 'machine learning',
    'nlp': 'natural language processing',
    'cv': 'computer vision',
    'dl': 'deep learning',
    'ai': 'artificial intelligence',
    'db': 'database',
    'sql': 'sql',
    'js': 'javascript',
    'py': 'python',
    'tf': 'tensorflow',
    'pt': 'pytorch',
    'ds': 'data science',
    'devops': 'devops',
    'api': 'api',
    'ui': 'user interface',
    'ux': 'user experience',
}

def expand_abbreviations(text):
    words = [w.strip().lower() for w in text.split(',')]
    expanded = [ABBREVIATION_MAP.get(w, w) for w in words]
    expanded = [e for e in expanded if isinstance(e, str)]
    return ', '.join(expanded)

app = Flask(__name__)

# Always fetch fresh jobs when the app starts (DISABLED, now only on demand)
# print("Fetching fresh jobs for all CS fields (remote and on-site)...")
# df = fetch_jobs()
# df.to_csv('data/scraped_jobs.csv', index=False)
# print("Job data refreshed!")

def get_jobs_df():
    return pd.read_csv('data/scraped_jobs.csv')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    jobs = []
    user_skills = []
    error = None
    refreshed = False
    user_experience = None
    if request.method == 'POST':
        if 'refresh' in request.form:
            # Refresh jobs: fetch new data and overwrite CSV
            df = fetch_jobs()
            df.to_csv('data/scraped_jobs.csv', index=False)
            refreshed = True
        else:
            user_input = request.form.get('skills', '')
            user_input_expanded = expand_abbreviations(user_input)
            user_skills = [s.strip().lower() for s in user_input_expanded.split(',') if s.strip()]
            REQUIRED_SKILL_MATCHES = 3
            user_experience = request.form.get('user_experience', '').strip()
            try:
                user_experience_val = int(user_experience) if user_experience else None
            except ValueError:
                user_experience_val = None
            df = get_jobs_df()
            # Generate embeddings if not present (optional, not used here)
            if not os.path.exists('data/job_embeddings.npy'):
                generate_job_embeddings(df['Skills'].tolist())
            matching_jobs = []
            for idx, row in df.iterrows():
                job_skills = [s.strip().lower() for s in str(row['Skills']).split(',') if s.strip()]
                matched = set(user_skills) & set(job_skills)
                # Experience filter
                job_exp = row.get('Experience', '')
                try:
                    job_exp_val = int(job_exp) if job_exp else None
                except ValueError:
                    job_exp_val = None
                exp_ok = (
                    user_experience_val is None or
                    job_exp_val is None or
                    user_experience_val >= job_exp_val
                )
                if len(matched) >= REQUIRED_SKILL_MATCHES and exp_ok:
                    highlight_val = getattr(row, 'Highlight', '')
                    if pd.isna(highlight_val):
                        highlight_val = ''
                    matching_jobs.append({
                        'Title': row['Title'],
                        'Company': row['Company'],
                        'Location': row['Location'],
                        'Skills': row['Skills'],
                        'Experience': row.get('Experience', ''),
                        'Highlight': highlight_val,
                        'Link': row['Link'],
                        'Matched': ', '.join(matched),
                        'NumMatched': len(matched),
                        'TotalUserSkills': len(user_skills)
                    })
            if not matching_jobs:
                error = f"No jobs found matching at least {REQUIRED_SKILL_MATCHES} of your skills and experience criteria."
            else:
                jobs = sorted(matching_jobs, key=lambda x: -x['NumMatched'])[:10]
    return render_template('search.html', jobs=jobs, user_skills=user_skills, error=error, refreshed=refreshed, user_experience=user_experience)

ADMIN_PASSWORD = 'admin123'  # Change this to a strong password

@app.route('/admin/refresh', methods=['GET', 'POST'])
def admin_refresh():
    status = None
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            df = fetch_jobs()
            df.to_csv('data/scraped_jobs.csv', index=False)
            status = 'Job data refreshed successfully!'
        else:
            status = 'Incorrect password.'
    return render_template('admin_refresh.html', status=status)

if __name__ == '__main__':
    app.run(debug=True) 