# JobGenius AI

**JobGenius AI** is an AI-powered job recommendation platform for tech professionals. It scrapes, analyzes, and recommends jobs based on your skills and experience, using advanced AI models for both matching and generating job highlights.

---

## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Ollama Integration](#ollama-integration)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [How to Run](#how-to-run)
- [Admin Functionality](#admin-functionality)
- [Data Files](#data-files)
- [Security Notes](#security-notes)
- [License](#license)

---

## Features

- **AI-powered job matching**: Enter your skills and experience to get personalized job recommendations.
- **Ollama LLM highlights**: Each job listing includes a one-sentence AI-generated highlight, powered by a local Ollama LLM (llama3:8b).
- **Modern frontend**: Responsive, glassmorphic UI built with Flask and Bootstrap.
- **Admin refresh**: Secure, password-protected admin route to refresh and rescrape job data.
- **Remote & on-site jobs**: Aggregates jobs from multiple tech fields and locations.
- **Experience filtering**: Matches jobs based on your years of experience.

---

## Technologies Used

- **Python 3.8+**
- **Flask** (web framework)
- **Pandas** (data processing)
- **NumPy** (embeddings, data)
- **Requests** (API calls, Ollama integration)
- **scikit-learn** (embeddings similarity)
- **sentence-transformers** (for skill embeddings)
- **Bootstrap 5** (frontend styling)
- **Ollama** (local LLM for job highlights, requires llama3:8b model)

---

## Ollama Integration

- **Purpose**: Ollama is used to generate a concise, attractive highlight (tagline) for each job, summarizing the main tech stack or appeal.
- **How it works**:  
  - When jobs are scraped, the job description is sent to the local Ollama server (`llama3:8b` model) via its REST API.
  - The LLM returns a one-sentence summary, which is stored in the `Highlight` column of the job CSV.
- **Requirements**:  
  - Ollama must be installed and running locally.  
  - The model `llama3:8b` is automatically pulled if not present.
  - Ollama is started automatically if not already running when the app launches.

---

## Project Structure

```
AIjobrec/
│
├── app.py                  # Main Flask app (entry point)
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── data/
│   ├── scraped_jobs.csv    # Scraped job data (with skills, experience, highlights)
│   └── job_embeddings.npy  # (Optional) Embeddings for jobs (if using embedding-based search)
├── recommender/
│   ├── scraper.py          # Job scraping, skill/experience extraction, Ollama highlight generation
│   ├── embedder.py         # Embedding generation for skills (sentence-transformers)
│   └── recommender.py      # (Optional) Embedding-based job recommendation logic
├── templates/
│   ├── home.html           # Landing page
│   ├── search.html         # Job search and results
│   ├── admin_refresh.html  # Admin-only refresh page
│   ├── about.html, contact.html, index.html # Info pages
└── ...
```

---

## Setup & Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/zainejaz67/JobGeniusAI.git
   cd JobGeniusAI
   ```

2. **Install Python dependencies**
   ```sh
   pip install -r requirements.txt
   ```
   *You may also need to install `sentence-transformers` if not present:*
   ```sh
   pip install sentence-transformers
   ```

3. **Install Ollama and the llama3:8b model**
   - Download and install Ollama from [https://ollama.com/](https://ollama.com/)
   - The app will attempt to start Ollama and pull the model automatically, but you can do it manually:
     ```sh
     ollama serve
     ollama pull llama3:8b
     ```

4. **Set up API keys**
   - The job scraper uses the [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch/) via RapidAPI.
   - Replace the placeholder API key in `recommender/scraper.py` with your own.

---

## How to Run

1. **Start Ollama (if not already running)**
   ```sh
   ollama serve
   ```
   *(Optional: The app will try to start Ollama automatically if not running.)*

2. **Run the Flask app**
   ```sh
   python app.py
   ```
   - The app will be available at [http://localhost:5000](http://localhost:5000)

3. **Using the app**
   - Go to `/search` to enter your skills and experience and get job recommendations.
   - Each job card shows matched skills, experience, and an AI-generated highlight.

---

## Admin Functionality

- **Purpose**: Allows an admin to refresh the job database by scraping new jobs and regenerating highlights.
- **How to use**:
  1. Go to `/admin/refresh` in your browser.
  2. Enter the admin password (default: `admin123`, change this in `app.py` for security).
  3. On success, the job data is refreshed and new highlights are generated using Ollama.
- **Security**: Only users with the password can trigger a refresh. The password is stored in `app.py` as `ADMIN_PASSWORD`.

---

## Data Files

- **data/scraped_jobs.csv**:  
  Contains all scraped jobs with columns:
  - `Title`, `Company`, `Location`, `Skills`, `Experience`, `Highlight`, `Link`
- **data/job_embeddings.npy**:  
  (Optional) NumPy array of job skill embeddings, used for advanced similarity search.

---

## Security Notes

- **Admin password**: Change the default password in `app.py` before deploying.
- **API keys**: Never commit your real API keys to public repositories.
- **Ollama**: Runs locally; no job data is sent to external LLMs.
