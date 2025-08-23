"""
PDF Export Functionality
Exports diagnosis results to PDF format
"""

import os
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("ReportLab not installed. PDF export will use text format.")
    print("To install: pip install reportlab")

class PDFExporter:
    def __init__(self, export_dir="exports"):
        """Initialize PDF exporter"""
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        
    def export_diagnosis_to_pdf(self, patient_info, symptoms, diagnosis_results, filename=None):
        """Export diagnosis results to PDF"""
        if not REPORTLAB_AVAILABLE:
            return self.export_to_text(patient_info, symptoms, diagnosis_results, filename)
        
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"diagnosis_report_{timestamp}.pdf"
        
        filepath = self.export_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12
        )
        
        # Title
        elements.append(Paragraph("Medical Diagnosis Report", title_style))
        elements.append(Spacer(1, 12))
        
        # Patient Information
        elements.append(Paragraph("Patient Information", heading_style))
        patient_data = [
            ["Patient ID:", patient_info.get('patient_id', 'N/A')],
            ["Date:", datetime.now().strftime('%B %d, %Y')],
            ["Time:", datetime.now().strftime('%I:%M %p')],
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5aa0')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 20))
        
        # Symptoms Reported
        elements.append(Paragraph("Symptoms Reported", heading_style))
        symptom_data = [["Symptom", "Severity", "Description"]]
        
        for symptom, severity in symptoms.items():
            severity_desc = self._get_severity_description(severity)
            symptom_data.append([
                symptom,
                f"{severity}/10 ({severity_desc})",
                self._get_severity_color_block(severity)
            ])
        
        symptom_table = Table(symptom_data, colWidths=[2.5*inch, 2*inch, 2*inch])
        symptom_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ]))
        elements.append(symptom_table)
        elements.append(Spacer(1, 20))
        
        # Primary Diagnosis
        elements.append(Paragraph("Primary Diagnosis", heading_style))
        primary = diagnosis_results['primary_diagnosis']
        
        diag_data = [
            ["Diagnosis:", primary['name']],
            ["Medical Name:", primary['medical_name']],
            ["ICD-10 Code:", primary['icd_10']],
            ["Confidence:", f"{primary['confidence']*100:.1f}%"],
            ["Description:", primary['description']]
        ]
        
        diag_table = Table(diag_data, colWidths=[2*inch, 4.5*inch])
        diag_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c5aa0')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (1, 3), (1, 3), self._get_confidence_color(primary['confidence'])),
        ]))
        elements.append(diag_table)
        elements.append(Spacer(1, 20))
        
        # Differential Diagnosis
        elements.append(Paragraph("Differential Diagnosis", heading_style))
        diff_data = [["Rank", "Condition", "Probability", "ICD-10"]]

        diffs = diagnosis_results.get('differential_diagnosis')
        if not diffs and 'all_probabilities' in diagnosis_results:
            diffs = [
                {
                    'disease': p.get('disease',''),
                    'probability': p.get('probability',0.0),
                    'icd_10': p.get('icd_10','N/A')
                }
                for p in diagnosis_results['all_probabilities']
            ]
        for i, prob in enumerate((diffs or [])[:5], 1):
            diff_data.append([
                str(i),
                prob.get('disease',''),
                f"{float(prob.get('probability',0.0))*100:.1f}%",
                prob.get('icd_10', 'N/A')
            ])
        
        diff_table = Table(diff_data, colWidths=[0.7*inch, 2.5*inch, 1.5*inch, 1.5*inch])
        diff_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ]))
        elements.append(diff_table)
        elements.append(Spacer(1, 20))
        
        # Recommendations
        elements.append(Paragraph("Recommendations", heading_style))
        for i, rec in enumerate(diagnosis_results['recommendations'][:5], 1):
            para = Paragraph(f"{i}. {rec}", styles['Normal'])
            elements.append(para)
            elements.append(Spacer(1, 6))
        
        elements.append(Spacer(1, 30))
        
        # Disclaimer
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.HexColor('#cccccc'),
            borderPadding=10
        )
        
        disclaimer = """
        <b>MEDICAL DISCLAIMER</b><br/>
        This diagnosis is generated by an AI system for educational purposes only. 
        It should NOT be used as a substitute for professional medical advice. 
        Always consult a qualified healthcare provider for medical diagnosis and treatment.
        """
        
        elements.append(Paragraph(disclaimer, disclaimer_style))
        
        # Build PDF
        doc.build(elements)
        
        return str(filepath)
    
    def _get_severity_description(self, severity):
        """Convert severity to description"""
        if severity < 2:
            return "Mild"
        elif severity < 4:
            return "Mild-Moderate"
        elif severity < 6:
            return "Moderate"
        elif severity < 8:
            return "Moderate-Severe"
        else:
            return "Severe"
    
    def _get_severity_color_block(self, severity):
        """Get visual representation of severity"""
        if severity < 3:
            return "▪▫▫▫▫"  # 1/5 filled
        elif severity < 5:
            return "▪▪▫▫▫"  # 2/5 filled
        elif severity < 7:
            return "▪▪▪▫▫"  # 3/5 filled
        elif severity < 9:
            return "▪▪▪▪▫"  # 4/5 filled
        else:
            return "▪▪▪▪▪"  # 5/5 filled
    
    def _get_confidence_color(self, confidence):
        """Get color based on confidence level"""
        if confidence > 0.8:
            return colors.lightgreen
        elif confidence > 0.6:
            return colors.lightyellow
        else:
            return colors.lightcoral
    
    def export_to_text(self, patient_info, symptoms, diagnosis_results, filename=None):
        """Export to text file if ReportLab not available"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"diagnosis_report_{timestamp}.txt"
        
        filepath = self.export_dir / filename
        
        with open(filepath, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("MEDICAL DIAGNOSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Patient ID: {patient_info.get('patient_id', 'N/A')}\n")
            f.write(f"Date: {datetime.now().strftime('%B %d, %Y')}\n")
            f.write(f"Time: {datetime.now().strftime('%I:%M %p')}\n")
            
            f.write("\n" + "-" * 70 + "\n")
            f.write("SYMPTOMS REPORTED\n")
            f.write("-" * 70 + "\n")
            
            for symptom, severity in symptoms.items():
                f.write(f"{symptom}: {severity}/10 ({self._get_severity_description(severity)})\n")
            
            f.write("\n" + "-" * 70 + "\n")
            f.write("PRIMARY DIAGNOSIS\n")
            f.write("-" * 70 + "\n")
            
            primary = diagnosis_results['primary_diagnosis']
            f.write(f"Diagnosis: {primary['name']} ({primary['medical_name']})\n")
            f.write(f"ICD-10 Code: {primary['icd_10']}\n")
            f.write(f"Confidence: {primary['confidence']*100:.1f}%\n")
            f.write(f"Description: {primary['description']}\n")
            
            f.write("\n" + "-" * 70 + "\n")
            f.write("DIFFERENTIAL DIAGNOSIS\n")
            f.write("-" * 70 + "\n")
            diffs = diagnosis_results.get('differential_diagnosis')
            if not diffs and 'all_probabilities' in diagnosis_results:
                diffs = [
                    {
                        'disease': p.get('disease',''),
                        'probability': p.get('probability',0.0)
                    }
                    for p in diagnosis_results['all_probabilities']
                ]
            for i, prob in enumerate((diffs or [])[:5], 1):
                f.write(f"{i}. {prob.get('disease','')}: {float(prob.get('probability',0.0))*100:.1f}%\n")
            
            f.write("\n" + "-" * 70 + "\n")
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 70 + "\n")
            
            for i, rec in enumerate(diagnosis_results['recommendations'][:5], 1):
                f.write(f"{i}. {rec}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("MEDICAL DISCLAIMER\n")
            f.write("This diagnosis is generated by an AI system for educational purposes only.\n")
            f.write("Always consult a qualified healthcare provider for medical diagnosis and treatment.\n")
            f.write("=" * 70 + "\n")
        
        return str(filepath)

# Test the exporter
if __name__ == "__main__":
    exporter = PDFExporter()
    
    # Test data
    patient_info = {"patient_id": "TEST001"}
    symptoms = {"Fever": 7, "Cough": 5, "Fatigue": 8}
    diagnosis_results = {
        "primary_diagnosis": {
            "name": "Influenza",
            "medical_name": "Influenza",
            "icd_10": "J11",
            "confidence": 0.85,
            "description": "Viral infection caused by influenza viruses"
        },
        "all_probabilities": [
            {"disease": "Influenza", "probability": 0.85, "icd_10": "J11"},
            {"disease": "COVID-19", "probability": 0.10, "icd_10": "U07.1"},
            {"disease": "Common Cold", "probability": 0.05, "icd_10": "J00"}
        ],
        "recommendations": [
            "Rest and stay hydrated",
            "Take fever-reducing medication as needed",
            "See a doctor if symptoms worsen",
            "Consider getting tested for influenza",
            "Avoid contact with others to prevent spread"
        ]
    }
    
    # Export
    filepath = exporter.export_to_text(patient_info, symptoms, diagnosis_results)
    print(f"Report exported to: {filepath}")
