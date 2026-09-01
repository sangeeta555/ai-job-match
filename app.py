import io
import os
import ssl
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
from google import genai
from google.genai import types
import httpx
from pydantic import BaseModel, Field
import PyPDF2

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Initialize Gemini client using API key from .env
gemini_api_key = os.getenv("GEMINI_API_KEY")

try:
    ssl_context = ssl.create_default_context()
    ssl_context.load_default_certs()
    client = genai.Client(
        api_key=gemini_api_key,
        http_options=types.HttpOptions(httpx_client=httpx.Client(verify=ssl_context))
    )
except Exception:
    client = genai.Client(api_key=gemini_api_key)


class MatchAnalysis(BaseModel):
    match_score: int = Field(ge=0, le=100, description="Match score integer between 0 and 100")
    matching_skills: list[str] = Field(description="Array of matching skills")
    missing_skills: list[str] = Field(description="Array of missing skills")
    experience_match: str = Field(description="Short evaluation of experience match")
    gaps: list[str] = Field(description="Array of identified experience/skill gaps")
    recommendations: list[str] = Field(description="Array of practical recommendations based on gaps")


class ImprovedSection(BaseModel):
    section: str = Field(description="Name of the resume section being improved (e.g. Summary, Skills, Experience, Future Learning)")
    suggestion: str = Field(description="Actionable improvement suggestion for this section based on gaps and recommendations")


class ResumeImprovementResponse(BaseModel):
    improved_sections: list[ImprovedSection] = Field(description="List of section improvement suggestions")


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/ai/test", methods=["GET"])
def test_ai():
    try:
        if not gemini_api_key:
            return jsonify({
                "success": False,
                "message": "gemini api connection failed"
            }), 500

        # Perform a minimal real Gemini API request
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents="ping"
        )

        if response and response.text:
            return jsonify({
                "success": True,
                "message": "gemini API connection working"
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "gemini api connection failed"
            }), 500
    except Exception:
        return jsonify({
            "success": False,
            "message": "gemini api connection failed"
        }), 500


@app.route("/api/analyze", methods=["POST"])
def analyze_match():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON body"
        }), 400

    resume = data.get("resume")
    job_description = data.get("job_description")

    # Validation: resume and job_description required, must be non-whitespace text
    if not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "Resume is required and must contain non-whitespace text"
        }), 400

    if not isinstance(job_description, str) or not job_description.strip():
        return jsonify({
            "success": False,
            "message": "Job description is required and must contain non-whitespace text"
        }), 400

    prompt = f"""you are an AI job matching assistant 

compare the candidates resume against the supplied job description

evaluate only information explicitly present in the supplied resume and job description 
do not invent:
-skills 
-work exprience
_education 
-certificates
-projects

REturn a match analysis containing:
-match_score:integer from 0 to 100
-matching_skills:array of strings
-missing_skills:array of  strings
-expirence_match:short string
-gaps:array of strings
-recomendations:array of strings

the recomendations must be practical and based on only on the identified gaps

Candidate Resume:
{resume.strip()}

Job Description:
{job_description.strip()}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=MatchAnalysis,
            )
        )

        if not response or not response.text:
            return jsonify({
                "success": False,
                "message": "AI response validation failed"
            }), 502

        # Explicitly validate structured response with Pydantic
        validated_analysis = MatchAnalysis.model_validate_json(response.text)

        # Return JSON with exactly the required fields
        return jsonify({
            "success": True,
            "match_score": validated_analysis.match_score,
            "matching_skills": validated_analysis.matching_skills,
            "missing_skills": validated_analysis.missing_skills,
            "experience_match": validated_analysis.experience_match,
            "gaps": validated_analysis.gaps,
            "recommendations": validated_analysis.recommendations
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "AI response validation failed"
        }), 502


@app.route("/api/improve-resume", methods=["POST"])
def improve_resume():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON body"
        }), 400

    resume = data.get("resume")
    gaps = data.get("gaps", [])
    recommendations = data.get("recommendations", [])

    # Validation: resume is required and must contain non-whitespace text
    if not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "Resume is required and must contain non-whitespace text"
        }), 400

    if not isinstance(gaps, list):
        gaps = []

    if not isinstance(recommendations, list):
        recommendations = []

    formatted_gaps = "\n".join(f"- {g}" for g in gaps) if gaps else "None provided"
    formatted_recs = "\n".join(f"- {r}" for r in recommendations) if recommendations else "None provided"

    prompt = f"""you are an AI job matching and resume improvement assistant.

suggest improvements to the candidates resume based only on the provided gaps and recommendations.

critical rule:
never invent:
-work experience
-projects
-skills
-certifications
-education
-achievements

the ai may:
-improve wording
-improve clarity
-suggest where existing experience could be presented better
-suggest what the student should learn or add in the future

do not rewrite the entire resume automatically.

Candidate Resume:
{resume.strip()}

Identified Gaps:
{formatted_gaps}

Recommendations:
{formatted_recs}
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ResumeImprovementResponse,
            )
        )

        if not response or not response.text:
            return jsonify({
                "success": False,
                "message": "resume improvement failed"
            }), 502

        validated_improvement = ResumeImprovementResponse.model_validate_json(response.text)

        return jsonify({
            "success": True,
            "improved_sections": [
                {
                    "section": item.section,
                    "suggestion": item.suggestion
                }
                for item in validated_improvement.improved_sections
            ]
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "resume improvement failed"
        }), 502


@app.route("/api/explain-match", methods=["POST"])
def explain_match():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON body"
        }), 400

    resume = data.get("resume")
    job_description = data.get("job_description")
    analysis = data.get("analysis")

    # Validation: all three fields required
    if not isinstance(resume, str) or not resume.strip():
        return jsonify({
            "success": False,
            "message": "resume is required and must contain non-whitespace text"
        }), 400

    if not isinstance(job_description, str) or not job_description.strip():
        return jsonify({
            "success": False,
            "message": "job_description is required and must contain non-whitespace text"
        }), 400

    if not isinstance(analysis, dict):
        return jsonify({
            "success": False,
            "message": "analysis object is required"
        }), 400

    # Extract analysis fields safely
    match_score = analysis.get("match_score", 0)
    matching_skills = analysis.get("matching_skills", [])
    missing_skills = analysis.get("missing_skills", [])
    experience_match = analysis.get("experience_match", "")
    gaps = analysis.get("gaps", [])
    recommendations = analysis.get("recommendations", [])

    formatted_matching = ", ".join(matching_skills) if matching_skills else "None"
    formatted_missing = ", ".join(missing_skills) if missing_skills else "None"
    formatted_gaps = "\n".join(f"- {g}" for g in gaps) if gaps else "None"
    formatted_recs = "\n".join(f"- {r}" for r in recommendations) if recommendations else "None"

    prompt = f"""You are an AI job matching assistant helping a student understand their job match results.

Explain in a beginner-friendly way why the candidate received a match score of {match_score}/100.

Base your explanation ONLY on the resume, job description, and analysis provided below.
Do NOT recalculate the score.
Do NOT invent any information not present in the supplied data.

Your explanation must:
- Be written in clear, simple language a student can understand
- Mention the strongest matches (skills and experience that aligned well)
- Explain the most important gaps (what was missing or mismatched)
- Explain what the candidate could realistically improve to increase their score

Candidate Resume:
{resume.strip()}

Job Description:
{job_description.strip()}

Match Analysis:
- Match Score: {match_score}/100
- Matching Skills: {formatted_matching}
- Missing Skills: {formatted_missing}
- Experience Match: {experience_match}
- Gaps:
{formatted_gaps}
- Recommendations:
{formatted_recs}

Write a single cohesive paragraph or short explanation (not bullet points). Keep it encouraging and actionable.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if not response or not response.text or not response.text.strip():
            return jsonify({
                "success": False,
                "message": "match explanation failed"
            }), 502

        return jsonify({
            "success": True,
            "explanation": response.text.strip()
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "match explanation failed"
        }), 502


@app.route("/api/extract-resume", methods=["POST"])
def extract_resume():
    if "resume_pdf" not in request.files:
        return jsonify({
            "success": False,
            "message": "resume pdf is required"
        }), 400

    file = request.files["resume_pdf"]
    if not file or not file.filename or not file.filename.strip():
        return jsonify({
            "success": False,
            "message": "resume pdf is required"
        }), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "message": "only pdf files are allowed"
        }), 400

    try:
        pdf_bytes = io.BytesIO(file.read())
        reader = PyPDF2.PdfReader(pdf_bytes)
        
        extracted_text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text_parts.append(page_text)
                
        extracted_text = "\n".join(extracted_text_parts).strip()
        
        if not extracted_text:
            return jsonify({
                "success": False,
                "message": "could not extract text from pdf"
            }), 400

        return jsonify({
            "success": True,
            "resume_text": extracted_text
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "could not extract text from pdf"
        }), 400


if __name__ == "__main__":
    app.run(debug=True, port=5000)
