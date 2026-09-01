import requests

print("Testing PDF extraction...")
with open("sample_resume.pdf", "rb") as f:
    r_extract = requests.post("http://127.0.0.1:5000/api/extract-resume", files={"resume_pdf": f})
    assert r_extract.status_code == 200, f"Extract failed: {r_extract.text}"
    resume_text = r_extract.json()["resume_text"]
    print("1. PDF Extraction Succeeded:")
    print(resume_text)

print("\nTesting Match Analysis...")
job_desc = "Senior Python Developer with 4+ years experience in Flask, Docker, Kubernetes, and AWS."
r_analyze = requests.post("http://127.0.0.1:5000/api/analyze", json={
    "resume": resume_text,
    "job_description": job_desc
})
assert r_analyze.status_code == 200, f"Analyze failed: {r_analyze.text}"
analysis_data = r_analyze.json()
print("2. Match Analysis Succeeded:")
print(f"Match Score: {analysis_data.get('match_score')}%")
print(f"Matching Skills: {analysis_data.get('matching_skills')}")
print(f"Missing Skills: {analysis_data.get('missing_skills')}")

print("\nTesting Improve Resume...")
r_improve = requests.post("http://127.0.0.1:5000/api/improve-resume", json={
    "resume": resume_text,
    "gaps": analysis_data.get("gaps", []),
    "recommendations": analysis_data.get("recommendations", [])
})
assert r_improve.status_code == 200, f"Improve failed: {r_improve.text}"
improve_data = r_improve.json()
print("3. Improve Resume Succeeded:")
for item in improve_data.get("improved_sections", []):
    print(f"- [{item.get('section')}]: {item.get('suggestion')}")

print("\nTesting Explain Match...")
r_explain = requests.post("http://127.0.0.1:5000/api/explain-match", json={
    "resume": resume_text,
    "job_description": job_desc,
    "analysis": analysis_data
})
assert r_explain.status_code == 200, f"Explain failed: {r_explain.text}"
explain_data = r_explain.json()
print("4. Explain Match Succeeded:")
print(explain_data.get("explanation"))

print("\nSUCCESS: All 4 features verified end-to-end!")
