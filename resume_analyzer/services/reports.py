from io import BytesIO


def build_pdf_report(analysis, result):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
        from reportlab.lib import colors
    except ImportError as exc:
        raise RuntimeError('ReportLab is not installed. Run pip install -r requirements.txt') from exc

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle('Title2', parent=styles['Title'], fontSize=20, spaceAfter=10)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=13, spaceBefore=8, spaceAfter=5)
    body = ParagraphStyle('Body2', parent=styles['BodyText'], leading=14)
    story = [Paragraph('AI Resume Analyzer - ATS Report', title)]
    story.append(Paragraph(f'<b>Resume:</b> {analysis.resume.title}', body))
    story.append(Paragraph(f'<b>Target Job:</b> {analysis.job.title}', body))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f'<b>ATS Score: {result["ats_score"]}%</b>', styles['Heading1']))
    story.append(Paragraph(f'<b>Resume Quality: {result["resume_quality"]}%</b>', body))

    story.append(Paragraph('Score Breakdown', h2))
    data = [['Metric', 'Score']] + [[k, f'{v}%'] for k,v in result['score_breakdown'].items()]
    table = Table(data, colWidths=[90*mm, 55*mm])
    table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#0f172a')),('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('GRID',(0,0),(-1,-1),0.5,colors.lightgrey),('PADDING',(0,0),(-1,-1),6)
    ]))
    story.append(table)

    for heading, items in [
        ('Matched Skills', result['matched_skills']),
        ('Missing Skills', result['missing_skills']),
        ('Matched Keywords', result['matched_keywords']),
        ('Missing Keywords', result['missing_keywords']),
        ('Strengths', result['strengths']),
        ('Weaknesses', result['weaknesses']),
    ]:
        story.append(Paragraph(heading, h2))
        if items:
            for item in items:
                story.append(Paragraph(f'• {item}', body))
        else:
            story.append(Paragraph('None detected.', body))

    story.append(Paragraph('Recommended Job Roles', h2))
    for item in result['predicted_roles']:
        story.append(Paragraph(f'• {item["role"]}: {item["match"]}% match', body))

    story.append(Paragraph('Learning Recommendations', h2))
    for item in result['learning_recommendations']:
        story.append(Paragraph(f'• {item["skill"]}: {item["next_step"]}', body))

    doc.build(story)
    buffer.seek(0)
    return buffer
