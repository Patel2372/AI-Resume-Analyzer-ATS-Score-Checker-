from pathlib import Path
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.contrib.auth.models import User

from .models import Resume, JobDescription, Analysis
from .services.engine import analyze_resume, extract_skills, rewrite_resume_text


class EngineTestCase(TestCase):
    def test_skill_extraction(self):
        skills = extract_skills('Python Django SQL Docker AWS and Git')
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertIn('docker', skills)

    def test_analysis(self):
        resume = 'Jenil Patel\nPython Django SQL Git\nSkills\nPython Django SQL\nProjects\nBuilt backend with REST API.'
        job = 'Python Developer\nRequired: Python Django SQL REST API Docker Git AWS'
        result = analyze_resume(resume, job)
        self.assertGreaterEqual(result['ats_score'], 0)
        self.assertLessEqual(result['ats_score'], 100)
        self.assertIn('docker', result['missing_skills'])

    def test_rewrite(self):
        out = rewrite_resume_text('Worked on Python project.')
        self.assertNotEqual(out, 'Worked on Python project.')

class ResumeParsingRegressionTests(TestCase):
    def test_projects_are_not_split_into_each_bullet(self):
        from .services.engine import parse_resume
        text = '''JENIL PATEL
PROFESSIONAL SUMMARY
Computer Engineering student.
TECHNICAL SKILLS
Python, Django, SQL
EDUCATION
B.Tech Computer Engineering | 2024-2027
PROJECTS
AI Resume Analyzer | Python, Django
• Built a Django application to parse resumes and extract sections.
• Added ATS scoring and skill gap analysis.
GitHub: AI-Resume-Analyzer
Smart Classroom System | Arduino, ESP8266
• Automated appliances using PIR and LDR sensors.
• Implemented face recognition attendance.
INTERNSHIP EXPERIENCE
Cybersecurity Intern | Example Company | Nov 2025 - Dec 2025
• Used Nmap and Wireshark.
CERTIFICATIONS
AWS Cloud Fundamentals | NPTEL - IoT
LANGUAGES
English | Hindi | Gujarati
'''
        parsed = parse_resume(text)
        self.assertEqual(len(parsed['projects']), 2)
        self.assertIn('ATS scoring', parsed['projects'][0])
        self.assertNotIn('Cybersecurity Intern', ' '.join(parsed['projects']))
        self.assertEqual(len(parsed['experience_items']), 1)
        self.assertEqual(len(parsed['certifications']), 2)
        self.assertEqual(parsed['languages'], ['English', 'Hindi', 'Gujarati'])
