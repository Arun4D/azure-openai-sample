from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

pdf.cell(200, 10, txt="Medical Report", ln=True, align='C')
pdf.ln(10)

pdf.multi_cell(0, 10, txt="""
Patient Name: John Doe
Patient ID: 123456
Date of Birth: 1985-05-15
Date of Report: 2025-05-20

Summary:
The patient presented with symptoms of mild chest pain and shortness of breath. An ECG was performed, showing normal sinus rhythm. Blood tests, including troponin levels, were within normal limits. A chest X-ray showed no acute abnormalities.

Diagnosis:
- Non-cardiac chest pain (likely musculoskeletal)
- Mild anxiety

Recommendations:
- Continue current medications
- Avoid heavy lifting for the next 2 weeks
- Follow-up with primary care in 1 week
- Seek immediate care if symptoms worsen or new symptoms develop

Physician: Dr. Jane Smith
""")

pdf.output("sample_medical_report.pdf")
print("Sample medical report PDF generated: sample_medical_report.pdf")
