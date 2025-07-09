import requests
import pandas as pd
import re

API_KEY = "6e0b6dd3c2msh413e3d4dfd18ff2p1d8a55jsn000218a5bb11"  # Replace this with your actual key

# Standard list of tech skills/keywords to look for
SKILL_KEYWORDS = [
    'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'go', 'ruby', 'php', 'swift', 'kotlin',
    'scala', 'r', 'matlab', 'sql', 'nosql', 'html', 'css', 'react', 'angular', 'vue', 'django', 'flask',
    'spring', 'node', 'express', 'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
    'matplotlib', 'seaborn', 'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'linux', 'git', 'hadoop',
    'spark', 'tableau', 'powerbi', 'machine learning', 'deep learning', 'nlp', 'computer vision',
    'data analysis', 'data science', 'statistics', 'bash', 'shell', 'rest', 'graphql', 'api', 'mongodb',
    'postgresql', 'mysql', 'redis', 'elasticsearch', 'jira', 'agile', 'scrum', 'ci/cd', 'devops', 'cloud'
]

# Compile regex for skill matching
SKILL_REGEX = re.compile(r'\b(' + '|'.join(re.escape(skill) for skill in SKILL_KEYWORDS) + r')\b', re.IGNORECASE)

# Regex for experience extraction (e.g., '3+ years', 'at least 5 years', 'minimum 2 years')
EXPERIENCE_REGEX = re.compile(r'(\d+)[+]?\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience)?', re.IGNORECASE)

def ollama_generate(prompt, model='llama3:8b'):
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={'model': model, 'prompt': prompt, 'stream': False},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get('response', '').strip()
    except Exception as e:
        print(f"Ollama error: {e}")
        return ''

def extract_skills_from_text(text):
    if not isinstance(text, str):
        return []
    found = set(match.group(0).lower() for match in SKILL_REGEX.finditer(text))
    return [skill.capitalize() for skill in found]

def extract_experience_from_text(text):
    if not isinstance(text, str):
        return None
    matches = EXPERIENCE_REGEX.findall(text)
    if matches:
        return max(int(m) for m in matches)
    return None

def ollama_highlight(text):
    if not isinstance(text, str) or not text.strip():
        return ''
    prompt = (
        "In one short sentence, what is the main tech stack or most attractive aspect of this job? Only output the sentence, no extra text.\nJob Description:\n" + text.strip()
    )
    return ollama_generate(prompt)

def fetch_jobs(queries=None, num_pages=2):
    """
    Fetch jobs for multiple CS fields/queries, for both remote and on-site, aggregate, deduplicate, and return as DataFrame.
    Uses Ollama llama3:8b for highlight generation.
    """
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    if queries is None:
        queries = [
            "machine learning", "data science", "software engineer", "web developer", "devops"
        ]
    all_jobs = []
    seen = set()
    locations = ["remote", "on site"]
    for query in queries:
        for location in locations:
            print(f"Fetching jobs for: {query} ({location})")
            for page in range(1, num_pages + 1):
                params = {"query": f"{query} in {location}", "page": page}
                response = requests.get(url, headers=headers, params=params)
                if response.status_code != 200:
                    print(f"API request failed with status {response.status_code}")
                    continue
                data = response.json().get("data", [])
                print(f"Page {page} - {query} ({location}) - Number of jobs fetched: {len(data)}")
                for job in data:
                    job_key = job.get("job_id") or (job.get("job_title"), job.get("employer_name"), job.get("job_city"))
                    if job_key in seen:
                        continue
                    seen.add(job_key)
                    job_desc = job.get("job_description", "")
                    skills = extract_skills_from_text(job_desc)
                    skills_str = ", ".join(skills) if skills else ""
                    highlight = ollama_highlight(job_desc)
                    print(f"Highlight for {job.get('job_title')}: {highlight}")
                    if not highlight:
                        highlight = (job_desc[:120] + '...') if job_desc else ''
                    highlights = job.get("job_highlights", {})
                    qualifications = highlights.get("Qualifications") if isinstance(highlights, dict) else None
                    experience = None
                    if qualifications and isinstance(qualifications, list):
                        for qual in qualifications:
                            exp = extract_experience_from_text(qual)
                            if exp is not None:
                                experience = exp
                                break
                    if experience is None:
                        experience = extract_experience_from_text(job_desc)
                    if experience is None and isinstance(highlights, dict):
                        for v in highlights.values():
                            if isinstance(v, list):
                                for item in v:
                                    exp = extract_experience_from_text(item)
                                    if exp is not None:
                                        experience = exp
                                        break
                            if experience is not None:
                                break
                    all_jobs.append({
                        "Title": job.get("job_title"),
                        "Company": job.get("employer_name"),
                        "Location": job.get("job_city", job.get("job_location", "Unknown")),
                        "Skills": skills_str,
                        "Experience": experience if experience is not None else "",
                        "Highlight": highlight,
                        "Link": job.get("job_apply_link", "N/A")
                    })
    print(f"Total unique jobs fetched: {len(all_jobs)}")
    return pd.DataFrame(all_jobs)
