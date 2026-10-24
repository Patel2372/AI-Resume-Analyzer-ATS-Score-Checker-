from pathlib import Path
import ast, compileall, sys
ROOT = Path(__file__).resolve().parent
errors=[]
required=['manage.py','requirements.txt','README.md','config/settings.py','config/urls.py','resume_analyzer/models.py','resume_analyzer/forms.py','resume_analyzer/views.py','resume_analyzer/services/engine.py','resume_analyzer/services/reports.py','templates/base.html','templates/home.html','static/css/app.css']
for rel in required:
    if not (ROOT/rel).exists(): errors.append(f'Missing required file: {rel}')
py_files=list(ROOT.rglob('*.py'))
for p in py_files:
    try: ast.parse(p.read_text(encoding='utf-8'))
    except Exception as e: errors.append(f'Syntax error {p.relative_to(ROOT)}: {e}')
if not compileall.compile_dir(str(ROOT),quiet=1,maxlevels=10): errors.append('compileall failed')
sys.path.insert(0,str(ROOT))
try:
    from resume_analyzer.services.engine import analyze_resume, extract_skills, rewrite_resume_text
    r='Jenil Patel\njenil@example.com\nSkills\nPython Django SQL Git REST API\nEducation\nB.Tech Computer Engineering\nProjects\nDeveloped a Django backend and SQL application.'
    j='Python Developer\nWe need Python, Django, SQL, REST API, Docker, AWS and Git.'
    result=analyze_resume(r,j)
    assert 0 <= result['ats_score'] <= 100
    assert 'python' in result['matched_skills']
    assert 'docker' in result['missing_skills']
    assert rewrite_resume_text('Worked on Python project.') != 'Worked on Python project.'
except Exception as e: errors.append(f'Engine self-test failed: {type(e).__name__}: {e}')
if errors:
    print('VERIFY FAILED'); [print('-',e) for e in errors]; raise SystemExit(1)
print('VERIFY PASSED'); print(f'Python files checked: {len(py_files)}'); print('Core engine smoke test: PASSED')
