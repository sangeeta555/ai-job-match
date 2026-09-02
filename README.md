# AI Job Match Assistant

A beginner-friendly Flask application powered by the Google GenAI SDK (Gemini API) that evaluates candidate resumes against job descriptions, identifies skill gaps, recommends targeted career improvements, and provides actionable, structured feedback.

---

## Features

- **PDF Resume Upload & Text Extraction**: Upload PDF resumes directly to extract readable plain text seamlessly.
- **AI Match Analysis**: Generates structured match metrics including match score (0–100%), matching skills, missing skills, experience match evaluation, gaps, and recommendations.
- **Resume Improvement Suggestions**: Recommends targeted, section-by-section resume enhancements based strictly on identified gaps without inventing fake experience.
- **Beginner-Friendly Match Explanation**: Explains why a candidate received a specific score in clear, encouraging, easy-to-understand language.
- **Interactive Web Interface**: Clean HTML/CSS/JavaScript interface allowing text paste, PDF upload, interactive analysis, and on-demand report expansions.

---

## Tech Stack

- **Backend**: Python 3.14, Flask
- **AI SDK**: Google GenAI Python SDK (`google-genai`), Pydantic (Structured Output Validation)
- **PDF Extraction**: `PyPDF2`
- **Environment Management**: `python-dotenv`
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (Fetch API)

---

## Project Structure

```
ai-job-match/
├── .env                  # Environment variables (API Key, Flask settings)
├── .gitignore            # Git ignore rules
├── app.py                # Flask application & API routes
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web frontend interface
└── README.md             # Project documentation
```

---

## Setup & Configuration

### Prerequisites
- Python 3.10+
- A Google Gemini API Key

### Installation

1. **Navigate to the project directory**:
   ```bash
   cd ai-job-match
   ```

2. **Create and activate a virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create or edit the `.env` file in the root directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

---

## Security Note About API Keys

> [!CAUTION]
> **Never commit your `.env` file or API keys to public repositories.**
> - Keep `GEMINI_API_KEY` stored exclusively inside `.env`.
> - Ensure `.env` is listed in your `.gitignore` file.
> - Avoid logging or exposing API keys in client-side responses or console logs.

---

## How to Run

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## How to Use

1. **Input Resume**: Either paste resume text directly into the text area or select a `.pdf` file and click **Upload PDF**.
2. **Input Job Description**: Paste the target job description into the second text area.
3. **Analyze Match**: Click **Analyze Match** to generate the AI match report.
4. **Improve Resume**: Click **Improve My Resume** below the report to view section-specific resume suggestions.
5. **Explain Match**: Click **Explain My Match** below the report for an easy-to-understand explanation of the score.

---

## API Endpoints

### 1. `GET /`
- **Description**: Renders the main web interface (`templates/index.html`).

### 2. `GET /api/ai/test`
- **Description**: Health check endpoint testing connectivity to the Gemini API.
- **Response**: `{"success": true, "message": "gemini API connection working"}`

### 3. `POST /api/extract-resume`
- **Description**: Extracts readable text from an uploaded PDF file.
- **Content-Type**: `multipart/form-data`
- **Body**: `resume_pdf` (File)
- **Response**: `{"success": true, "resume_text": "..."}`

### 4. `POST /api/analyze`
- **Description**: Analyzes resume against job description using Gemini structured JSON outputs.
- **Content-Type**: `application/json`
- **Body**:
  ```json
  {
    "resume": "Resume text...",
    "job_description": "Job description text..."
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "match_score": 75,
    "matching_skills": ["Python", "Flask"],
    "missing_skills": ["Docker", "AWS"],
    "experience_match": "Candidate meets experience requirements.",
    "gaps": ["No containerization experience"],
    "recommendations": ["Learn Docker"]
  }
  ```

### 5. `POST /api/improve-resume`
- **Description**: Generates section-by-section improvement suggestions based on analysis gaps.
- **Content-Type**: `application/json`
- **Body**: `{"resume": "...", "gaps": [...], "recommendations": [...]}`
- **Response**: `{"success": true, "improved_sections": [{"section": "...", "suggestion": "..."}]}`

### 6. `POST /api/explain-match`
- **Description**: Provides a clear explanation of why the match score was awarded.
- **Content-Type**: `application/json`
- **Body**: `{"resume": "...", "job_description": "...", "analysis": {...}}`
- **Response**: `{"success": true, "explanation": "..."}`

---

## Future Improvements

- Support for additional document formats (`.docx`, `.txt`).
- Export match reports and improvement suggestions as downloadable PDFs.
- Categorized skill breakdown (e.g. Languages, Frameworks, DevOps, Databases).
- Multi-job comparison feature in a single session.
