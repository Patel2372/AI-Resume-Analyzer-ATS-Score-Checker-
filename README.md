# AI Resume Analyzer and ATS Score Checker using Django

A complete Django-based resume analysis and career assistant project. It parses PDF/DOCX resumes, compares them with job descriptions, calculates an ATS-style score, identifies skill gaps, predicts suitable job roles, rewrites weak resume content, recommends a learning path, and generates a PDF report.

## Features

- User registration/login/logout
- PDF and DOCX resume upload
- Resume text extraction and section detection
- Skills, keywords, education, experience, projects, certifications extraction
- Job description analysis
- ATS score with detailed breakdown
- Keyword and skill matching
- Semantic similarity using TF-IDF + cosine similarity
- ATS-friendly structure checks
- Resume quality score
- Strengths, weaknesses, and improvement priorities
- Job role prediction
- Skill-gap analysis and learning roadmap
- Rule-based AI resume rewriter that works without an external API
- Multiple resume versions
- Analysis history
- Job recommendations
- Downloadable PDF analysis report
- Django Admin support
- Responsive Bootstrap UI

## Recommended environment

Python 3.10+
Django 5.2.17

## Windows setup

1. Extract the ZIP.
2. Open the project folder in VS Code.
3. Create a virtual environment:

   python -m venv venv

4. Activate it:

   venv\Scripts\activate

5. Install dependencies:

   pip install -r requirements.txt

6. Run migrations:

   python manage.py migrate

7. Create an admin user (optional):

   python manage.py createsuperuser

8. Start the server:

   python manage.py runserver

9. Open:

   http://127.0.0.1:8000/

## Important notes

- Uploaded files are stored in `media/`.
- SQLite is used by default, so the project is easy to run for a college demo.
- Semantic matching uses scikit-learn. If scikit-learn is unavailable, the engine automatically falls back to token overlap instead of crashing.
- PDF/DOCX parsing errors are reported as user-friendly validation errors.
- No external AI API key is required for the included rewrite feature. You can replace the rewrite service later with a hosted LLM if required.

## Main flow

Register -> Dashboard -> Upload Resume -> Enter Job Description -> Analyze -> View ATS report -> Rewrite content -> Download PDF report.

## Parser accuracy improvements

The PDF resume parser is layout-aware for common one-page, two-column resume designs. It uses PDF block coordinates to reduce column-order scrambling and specifically improves detection of the candidate name, section content, projects, education, experience, certificates, tools, languages, and soft skills.

For best results, use text-based PDFs (not scanned image-only PDFs) with standard headings.

## Parser accuracy update
The resume parser is layout-aware for two-column PDF resumes. It preserves the header name, headline, technical skills, education, all work/internship entries, projects and hackathon projects, certificates, tools, soft skills, languages, LinkedIn, GitHub and location without relying on the scrambled linear PDF text order.

## Resume parser reliability update

The parser now prefers line-based section extraction when PDF coordinate blocks do not contain separately identifiable section headings. This prevents a full-page PDF text block from overriding the normal section parser. The Projects section is parsed as project records with their wrapped bullet text and GitHub reference attached to the correct project. Internship entries, achievements, and other sections are no longer copied into the project list. Wrapped experience bullet lines are grouped with their role. Certifications and languages separated by pipes are split into separate items.

Run checks locally after installing dependencies:

```powershell
python verify_project.py
python manage.py test
```

PDF parsing is layout-dependent, so test with multiple resumes (single-column, two-column, and scanned PDFs). Scanned/image-only PDFs require OCR, which is not included in this version; they will be reported as having no readable text rather than guessed.
