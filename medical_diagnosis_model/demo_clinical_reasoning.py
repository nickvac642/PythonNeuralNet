"""
Demo: Clinical Reasoning Improvements
Shows how the system now thinks like a doctor
"""

from medical_neural_network_v2 import ClinicalReasoningNetwork
from medical_disease_schema_v2 import DISEASES_V2

def print_section(title):
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print('='*80)

print_section("CLINICAL REASONING DEMO - Addressing Doctor's Feedback")

print("""
Doctor's Feedback Addressed:
1. "The differential isn't the greatest" → Now shows medically relevant alternatives
2. "Can't jump to influenza without confirmatory test" → Now distinguishes between
   syndrome-level diagnosis (Viral URI, ILI) and specific diagnosis (confirmed Flu)
""")

# Initialize enhanced network
print("\nInitializing Clinical Reasoning Network...")
clinical_net = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=3000)

# Train with clinical patterns
print("Training with clinical reasoning patterns...")
clinical_net.train(cases_per_disease=30, verbose=False)
print("✓ Training complete")

# Test Case 1: Original flu-like symptoms
print_section("TEST CASE 1: Flu-like Symptoms (No Test Results)")

symptoms_case1 = {
    "Fever": 8,
    "Fatigue": 9,
    "Cough": 6,
    "Headache": 7,
    "Muscle Pain": 8,
    "Sore Throat": 4
}

print("\nPatient Presentation:")
for symptom, severity in symptoms_case1.items():
    print(f"  • {symptom}: {severity}/10")

# Get diagnosis WITHOUT test results
results1 = clinical_net.diagnose_with_reasoning(symptoms_case1, has_test_results=None)

print(f"\nDiagnosis WITHOUT confirmatory testing:")
print(f"Primary: {results1['primary_diagnosis']['name']}")
print(f"Note: {results1['primary_diagnosis']['diagnostic_certainty']}")

print("\nAppropriate Differential Diagnosis:")
for i, diff in enumerate(results1['differential_diagnosis'][:5], 1):
    print(f"{i}. {diff['disease']} - {diff['probability']*100:.1f}%")
    print(f"   Certainty level: {diff['diagnostic_certainty']}")

print("\nClinical Reasoning:")
reasoning = results1['clinical_reasoning']
print(f"Syndrome identified: {reasoning['syndrome_identified']}")
print(f"Key findings: {len(reasoning['key_findings'])} symptoms typical for diagnosis")

# Test Case 2: Same symptoms WITH positive flu test
print_section("TEST CASE 2: Same Symptoms WITH Positive Flu Test")

print("Lab Results: Influenza A/B Rapid Test: POSITIVE for Influenza A")

results2 = clinical_net.diagnose_with_reasoning(
    symptoms_case1, 
    has_test_results={"Influenza A/B Test": "Positive"}
)

print(f"\nDiagnosis WITH confirmatory testing:")
print(f"Primary: {results2['primary_diagnosis']['name']}")
print(f"Certainty: {results2['primary_diagnosis']['diagnostic_certainty']}")

# Test Case 3: Milder symptoms (more like common cold)
print_section("TEST CASE 3: Mild URI Symptoms")

symptoms_case3 = {
    "Runny Nose": 6,
    "Nasal Congestion": 7,
    "Sore Throat": 4,
    "Cough": 3,
    "Fatigue": 3
}

print("\nPatient Presentation:")
for symptom, severity in symptoms_case3.items():
    print(f"  • {symptom}: {severity}/10")

results3 = clinical_net.diagnose_with_reasoning(symptoms_case3)

print(f"\nDiagnosis:")
print(f"Primary: {results3['primary_diagnosis']['name']}")
print(f"ICD-10: {results3['primary_diagnosis']['icd_10']}")

print("\nDifferential (now shows related conditions):")
for i, diff in enumerate(results3['differential_diagnosis'][:4], 1):
    print(f"{i}. {diff['disease']} - {diff['probability']*100:.1f}%")

# Test Case 4: Sore throat without cough (Centor criteria)
print_section("TEST CASE 4: Applying Clinical Rules (Centor Criteria)")

symptoms_case4 = {
    "Sore Throat": 8,
    "Fever": 6,
    "Headache": 5,
    "Swelling": 5  # Lymph nodes
}

print("\nPatient Presentation:")
for symptom, severity in symptoms_case4.items():
    print(f"  • {symptom}: {severity}/10")
print("  • Cough: ABSENT (important!)")

results4 = clinical_net.diagnose_with_reasoning(symptoms_case4)

print(f"\nDiagnosis considers Centor criteria:")
print(f"Primary: {results4['primary_diagnosis']['name']}")

if results4['required_tests']:
    print(f"\nRequired testing: {', '.join(results4['required_tests'])}")

# Summary of improvements
print_section("SUMMARY OF IMPROVEMENTS")

print("""
1. SYNDROME-LEVEL DIAGNOSIS:
   - "Viral URI" instead of jumping to "Influenza"
   - "Influenza-like Illness" when flu suspected but not confirmed
   - "COVID-19-like Illness" for suspected COVID

2. DIAGNOSTIC CERTAINTY LEVELS:
   - CLINICAL: Can diagnose without tests (Viral URI)
   - PRESUMPTIVE: Likely but benefits from testing (ILI)
   - CONFIRMATORY: Requires specific test (Influenza, COVID-19)

3. APPROPRIATE DIFFERENTIALS:
   - Respiratory symptoms → respiratory conditions
   - No more "Rheumatoid Arthritis" in flu differential
   - Clinically relevant alternatives

4. CLINICAL DECISION RULES:
   - Centor criteria for strep throat
   - Severity assessment for disposition
   - Red flag identification

5. TESTING GUIDANCE:
   - Tells you WHEN testing is needed
   - Distinguishes syndromic from specific diagnosis
   - Evidence-based recommendations
""")

# Show available diagnoses
print_section("ENHANCED DISEASE DATABASE")

print("Syndrome-level diagnoses (no test required):")
clinical_diagnoses = [d for d in DISEASES_V2.values() 
                     if d['diagnostic_certainty'] == 'CLINICAL']
for disease in clinical_diagnoses[:5]:
    print(f"  • {disease['name']} ({disease['icd_10']})")

print("\nSpecific diagnoses (test required):")
confirmatory_diagnoses = [d for d in DISEASES_V2.values() 
                         if d['diagnostic_certainty'] == 'CONFIRMATORY']
for disease in confirmatory_diagnoses[:5]:
    print(f"  • {disease['name']} ({disease['icd_10']}) - Requires: {disease['required_tests'][0]}")
