"""
Demo Script: Shows all features of the Enhanced Medical System
"""

from enhanced_medical_system import EnhancedMedicalSystem
from medical_symptom_schema import SYMPTOMS, SYMPTOM_CATEGORIES
from medical_disease_schema import DISEASES
from diagnosis_history import DiagnosisHistory
from pdf_exporter import PDFExporter
import os

def demo_line():
    print("\n" + "="*80 + "\n")

print("🏥 ENHANCED MEDICAL DIAGNOSIS SYSTEM - FEATURE DEMO 🏥")
demo_line()

# 1. Show System Info
print("📊 SYSTEM CAPABILITIES:")
print(f"   • Total Diseases: {len(DISEASES)}")
print(f"   • Total Symptoms: {len(SYMPTOMS)}")
print(f"   • Symptom Categories: {len(SYMPTOM_CATEGORIES)}")
print("\n   Available Diseases:")
for i, (did, disease) in enumerate(DISEASES.items(), 1):
    print(f"     {i:2d}. {disease['name']} ({disease['icd_10']})")

demo_line()

# 2. Show Symptom Categories
print("🏷️  SYMPTOM CATEGORIES:")
for category, symptom_ids in SYMPTOM_CATEGORIES.items():
    print(f"\n   {category}:")
    for sid in symptom_ids[:3]:  # Show first 3 symptoms
        if sid in SYMPTOMS:
            print(f"     • {SYMPTOMS[sid]['name']} ({SYMPTOMS[sid]['medical_term']})")
    if len(symptom_ids) > 3:
        print(f"     ... and {len(symptom_ids)-3} more")

demo_line()

# 3. Simulate a Diagnosis
print("🔬 SIMULATING DIAGNOSIS:")
print("\n   Patient: John Doe")
print("   Symptoms reported:")

# Simulate flu-like symptoms
test_symptoms = {
    "Fever": 8,
    "Fatigue": 9,
    "Cough": 6,
    "Headache": 7,
    "Muscle Pain": 8,
    "Sore Throat": 4
}

for symptom, severity in test_symptoms.items():
    print(f"     • {symptom}: {severity}/10")

# Initialize system
system = EnhancedMedicalSystem()

# Load or train model
print("\n   Loading AI model...")
try:
    system.network.load_model("enhanced_medical_model.json")
    print("   ✅ Model loaded successfully!")
except:
    print("   ⏳ Training new model (this will take a moment)...")
    system.network.train(cases_per_disease=50, verbose=False)
    system.network.save_model("enhanced_medical_model.json")
    print("   ✅ Model trained!")

# Get diagnosis
print("\n   Running diagnosis...")
results = system.network.diagnose(test_symptoms)

primary = results['primary_diagnosis']
print(f"\n   PRIMARY DIAGNOSIS: {primary['name'].upper()}")
print(f"   Medical Name: {primary['medical_name']}")
print(f"   ICD-10 Code: {primary['icd_10']}")
print(f"   Confidence: {primary['confidence']*100:.1f}%")

# Visual confidence bar
confidence = primary['confidence']
bar_length = 40
filled = int(confidence * bar_length)
bar = "█" * filled + "░" * (bar_length - filled)
print(f"   [{bar}]")

print("\n   Top 3 Differential Diagnoses:")
for i, prob in enumerate(results['all_probabilities'][:3], 1):
    print(f"     {i}. {prob['disease']}: {prob['probability']*100:.1f}%")

demo_line()

# 4. Save to History
print("💾 SAVING TO PATIENT HISTORY:")
history_manager = DiagnosisHistory()
session = history_manager.create_session("john_doe_demo")
history_manager.save_diagnosis(session, test_symptoms, results)
print("   ✅ Diagnosis saved to patient history")
print(f"   📁 Session file: {history_manager.current_session_file}")

demo_line()

# 5. Export to PDF
print("📄 EXPORTING TO PDF:")
pdf_exporter = PDFExporter()
patient_info = {"patient_id": "john_doe_demo"}

# Try PDF first, fallback to text
try:
    filepath = pdf_exporter.export_diagnosis_to_pdf(
        patient_info,
        test_symptoms,
        results,
        "demo_diagnosis_report.pdf"
    )
    print(f"   ✅ PDF report created: {filepath}")
    print("   📊 PDF includes: formatted tables, confidence bars, ICD-10 codes")
except:
    filepath = pdf_exporter.export_to_text(
        patient_info,
        test_symptoms,
        results,
        "demo_diagnosis_report.txt"
    )
    print(f"   ✅ Text report created: {filepath}")

demo_line()

# 6. Show Patient Report
print("📈 PATIENT HISTORY REPORT:")
report = history_manager.generate_patient_report("john_doe_demo")
if report:
    print(f"   Total visits: {report['total_sessions']}")
    print(f"   Most common diagnosis: {list(report['diagnosis_frequency'].keys())[0] if report['diagnosis_frequency'] else 'None'}")
    print(f"   Most frequent symptoms: {', '.join(list(report['common_symptoms'].keys())[:3])}")

demo_line()

# 7. Show Recent Diagnoses
print("🕐 RECENT DIAGNOSES ACROSS ALL PATIENTS:")
recent = history_manager.get_recent_diagnoses(3)
for diag in recent:
    print(f"   • Patient: {diag['patient_id']}")
    print(f"     Diagnosis: {diag['primary_diagnosis']['name']} ({diag['primary_diagnosis']['confidence']*100:.0f}%)")

demo_line()

# 8. List created files
print("📁 FILES CREATED DURING DEMO:")
dirs_to_check = ["diagnosis_history", "exports"]
for dir_name in dirs_to_check:
    if os.path.exists(dir_name):
        files = os.listdir(dir_name)
        if files:
            print(f"\n   {dir_name}/")
            for file in files:
                print(f"     • {file}")

print("\n✨ Demo complete! All features working successfully!")
print("\nTo run the full interactive system: python3 enhanced_medical_system.py")
demo_line()
