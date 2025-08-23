"""
Medical Disease Schema
Comprehensive disease classifications with ICD-10 codes and symptom mappings
"""

from medical_symptom_schema import SYMPTOMS

# Disease definitions with medical classifications
# Each disease has: ID, name, ICD-10 code, category, symptom_ids, severity_patterns
DISEASES = {
    # Respiratory Infections
    0: {
        "name": "Common Cold",
        "medical_name": "Acute Nasopharyngitis",
        "icd_10": "J00",
        "category": "Respiratory Infection",
        "description": "Viral infection of upper respiratory tract",
        "typical_duration": "7-10 days",
        "symptom_ids": [7, 8, 6, 3, 1, 12],  # Runny nose, congestion, sore throat, cough, fatigue, headache
        "symptom_patterns": {
            7: {"frequency": 0.9, "severity_range": (0.3, 0.7)},  # Runny nose - very common, moderate
            8: {"frequency": 0.85, "severity_range": (0.3, 0.7)}, # Nasal congestion
            6: {"frequency": 0.7, "severity_range": (0.2, 0.5)},  # Sore throat
            3: {"frequency": 0.6, "severity_range": (0.2, 0.5)},  # Cough
            1: {"frequency": 0.5, "severity_range": (0.2, 0.4)},  # Fatigue
            12: {"frequency": 0.4, "severity_range": (0.2, 0.4)}, # Headache
            0: {"frequency": 0.1, "severity_range": (0.1, 0.3)}   # Fever (rare in common cold)
        },
        "etymology": "From 'cold' weather association (medieval belief)",
        "differential_diagnosis": ["Flu", "Allergic Rhinitis", "Sinusitis"]
    },
    
    1: {
        "name": "Influenza",
        "medical_name": "Influenza",
        "icd_10": "J11",
        "category": "Respiratory Infection",
        "description": "Viral infection caused by influenza viruses",
        "typical_duration": "5-7 days",
        "symptom_ids": [0, 1, 3, 12, 16, 6, 4],  # Fever, fatigue, cough, headache, muscle pain, sore throat, dyspnea
        "symptom_patterns": {
            0: {"frequency": 0.95, "severity_range": (0.6, 0.9)},  # Fever - almost always, high
            1: {"frequency": 0.9, "severity_range": (0.7, 0.9)},   # Fatigue - severe
            3: {"frequency": 0.85, "severity_range": (0.4, 0.7)},  # Cough
            12: {"frequency": 0.8, "severity_range": (0.5, 0.8)},  # Headache
            16: {"frequency": 0.75, "severity_range": (0.5, 0.8)}, # Myalgia
            6: {"frequency": 0.6, "severity_range": (0.3, 0.6)},   # Sore throat
            4: {"frequency": 0.3, "severity_range": (0.3, 0.7)}    # Shortness of breath
        },
        "etymology": "Italian 'influenza' - influence (of the stars)",
        "differential_diagnosis": ["COVID-19", "Common Cold", "Bacterial Pneumonia"]
    },
    
    2: {
        "name": "Allergic Rhinitis",
        "medical_name": "Allergic Rhinitis",
        "icd_10": "J30.9",
        "category": "Allergic Condition",
        "description": "Inflammation of nasal passages due to allergen exposure",
        "typical_duration": "Seasonal or perennial",
        "symptom_ids": [7, 8, 22, 28, 12],  # Runny nose, congestion, itching, watery eyes, headache
        "symptom_patterns": {
            7: {"frequency": 0.95, "severity_range": (0.4, 0.8)},  # Rhinorrhea
            8: {"frequency": 0.9, "severity_range": (0.4, 0.8)},   # Nasal congestion
            22: {"frequency": 0.85, "severity_range": (0.3, 0.7)}, # Pruritus (nose/eyes)
            28: {"frequency": 0.7, "severity_range": (0.2, 0.5)},  # Eye symptoms
            12: {"frequency": 0.4, "severity_range": (0.2, 0.5)},  # Headache
            0: {"frequency": 0.0, "severity_range": (0.0, 0.0)}    # No fever
        },
        "etymology": "Greek 'rhino' (nose) + '-itis' (inflammation)",
        "differential_diagnosis": ["Common Cold", "Sinusitis", "Vasomotor Rhinitis"]
    },
    
    # Gastrointestinal Disorders
    3: {
        "name": "Gastroenteritis",
        "medical_name": "Acute Gastroenteritis",
        "icd_10": "K52.9",
        "category": "Gastrointestinal",
        "description": "Inflammation of stomach and intestines",
        "typical_duration": "1-3 days",
        "symptom_ids": [9, 10, 11, 1, 0, 12],  # Nausea, vomiting, diarrhea, fatigue, fever, headache
        "symptom_patterns": {
            9: {"frequency": 0.9, "severity_range": (0.5, 0.8)},   # Nausea
            10: {"frequency": 0.8, "severity_range": (0.4, 0.8)},  # Vomiting
            11: {"frequency": 0.85, "severity_range": (0.5, 0.9)}, # Diarrhea
            1: {"frequency": 0.7, "severity_range": (0.4, 0.7)},   # Fatigue
            0: {"frequency": 0.5, "severity_range": (0.2, 0.5)},   # Fever
            12: {"frequency": 0.4, "severity_range": (0.2, 0.5)}   # Headache
        },
        "etymology": "Greek 'gaster' (stomach) + 'enteron' (intestine)",
        "differential_diagnosis": ["Food Poisoning", "IBS", "Appendicitis"]
    },
    
    # Cardiovascular Conditions
    4: {
        "name": "Hypertension",
        "medical_name": "Essential Hypertension",
        "icd_10": "I10",
        "category": "Cardiovascular",
        "description": "Persistently elevated blood pressure",
        "typical_duration": "Chronic condition",
        "symptom_ids": [12, 13, 28, 4, 19],  # Headache, dizziness, vision changes, dyspnea, tachycardia
        "symptom_patterns": {
            12: {"frequency": 0.4, "severity_range": (0.3, 0.6)},  # Headache
            13: {"frequency": 0.3, "severity_range": (0.2, 0.5)},  # Dizziness
            28: {"frequency": 0.2, "severity_range": (0.2, 0.5)},  # Blurred vision
            4: {"frequency": 0.25, "severity_range": (0.2, 0.6)},  # Shortness of breath
            19: {"frequency": 0.2, "severity_range": (0.2, 0.5)},  # Rapid heartbeat
            # Note: Often asymptomatic
        },
        "etymology": "Greek 'hyper' (over) + 'tension' (pressure)",
        "differential_diagnosis": ["Secondary Hypertension", "White Coat Hypertension"]
    },
    
    # Metabolic Disorders
    5: {
        "name": "Type 2 Diabetes",
        "medical_name": "Type 2 Diabetes Mellitus",
        "icd_10": "E11",
        "category": "Metabolic/Endocrine",
        "description": "Chronic metabolic disorder with insulin resistance",
        "typical_duration": "Chronic condition",
        "symptom_ids": [26, 1, 28, 2, 27, 22],  # Polyuria, fatigue, blurred vision, weight loss, dysuria, pruritus
        "symptom_patterns": {
            26: {"frequency": 0.7, "severity_range": (0.4, 0.7)},  # Frequent urination
            1: {"frequency": 0.8, "severity_range": (0.4, 0.7)},   # Fatigue
            28: {"frequency": 0.4, "severity_range": (0.2, 0.6)},  # Blurred vision
            2: {"frequency": 0.5, "severity_range": (0.2, 0.5)},   # Weight loss
            27: {"frequency": 0.3, "severity_range": (0.2, 0.5)},  # Painful urination
            22: {"frequency": 0.3, "severity_range": (0.2, 0.5)}   # Itching
        },
        "etymology": "Greek 'diabetes' (siphon) + Latin 'mellitus' (honeyed)",
        "differential_diagnosis": ["Type 1 Diabetes", "LADA", "Metabolic Syndrome"]
    },
    
    # Musculoskeletal Disorders
    6: {
        "name": "Rheumatoid Arthritis",
        "medical_name": "Rheumatoid Arthritis",
        "icd_10": "M06.9",
        "category": "Autoimmune/Rheumatologic",
        "description": "Chronic autoimmune disorder affecting joints",
        "typical_duration": "Chronic condition with flares",
        "symptom_ids": [15, 23, 1, 0, 16],  # Joint pain, swelling, fatigue, fever, muscle pain
        "symptom_patterns": {
            15: {"frequency": 1.0, "severity_range": (0.5, 0.9)},  # Joint pain - always present
            23: {"frequency": 0.9, "severity_range": (0.4, 0.8)},  # Joint swelling
            1: {"frequency": 0.8, "severity_range": (0.4, 0.7)},   # Fatigue
            0: {"frequency": 0.3, "severity_range": (0.1, 0.3)},   # Low-grade fever
            16: {"frequency": 0.6, "severity_range": (0.3, 0.6)}   # Muscle pain
        },
        "etymology": "Greek 'rheuma' (flow) + 'arthron' (joint)",
        "differential_diagnosis": ["Osteoarthritis", "Lupus", "Fibromyalgia"]
    },
    
    # Neurological Disorders
    7: {
        "name": "Migraine",
        "medical_name": "Migraine without aura",
        "icd_10": "G43.0",
        "category": "Neurological",
        "description": "Recurrent headache disorder with neurological features",
        "typical_duration": "4-72 hours per episode",
        "symptom_ids": [12, 9, 28, 13, 22],  # Headache, nausea, visual disturbance, dizziness, photophobia
        "symptom_patterns": {
            12: {"frequency": 1.0, "severity_range": (0.7, 1.0)},  # Severe headache
            9: {"frequency": 0.8, "severity_range": (0.4, 0.8)},   # Nausea
            28: {"frequency": 0.6, "severity_range": (0.3, 0.7)},  # Visual disturbances
            13: {"frequency": 0.5, "severity_range": (0.3, 0.6)},  # Dizziness
            22: {"frequency": 0.7, "severity_range": (0.5, 0.8)}   # Light sensitivity
        },
        "etymology": "Greek 'hemikrania' (half skull)",
        "differential_diagnosis": ["Tension Headache", "Cluster Headache", "Sinusitis"]
    },
    
    # Mental Health Disorders
    8: {
        "name": "Major Depression",
        "medical_name": "Major Depressive Disorder",
        "icd_10": "F32",
        "category": "Mental Health",
        "description": "Persistent depressed mood and loss of interest",
        "typical_duration": "Episodes lasting weeks to months",
        "symptom_ids": [25, 1, 24, 12, 2],  # Depression, fatigue, anxiety, headache, weight changes
        "symptom_patterns": {
            25: {"frequency": 1.0, "severity_range": (0.6, 1.0)},  # Depression - core symptom
            1: {"frequency": 0.9, "severity_range": (0.5, 0.9)},   # Fatigue
            24: {"frequency": 0.7, "severity_range": (0.4, 0.8)},  # Anxiety
            12: {"frequency": 0.5, "severity_range": (0.2, 0.5)},  # Headache
            2: {"frequency": 0.6, "severity_range": (0.2, 0.5)}    # Weight changes
        },
        "etymology": "Latin 'deprimere' (to press down)",
        "differential_diagnosis": ["Bipolar Disorder", "Adjustment Disorder", "Dysthymia"]
    },
    
    # Infectious Diseases
    9: {
        "name": "COVID-19",
        "medical_name": "Coronavirus Disease 2019",
        "icd_10": "U07.1",
        "category": "Infectious Disease",
        "description": "Respiratory illness caused by SARS-CoV-2",
        "typical_duration": "7-14 days (acute phase)",
        "symptom_ids": [0, 3, 4, 1, 12, 16, 6, 28, 29],  # Fever, cough, dyspnea, fatigue, headache, myalgia, throat, smell/taste loss
        "symptom_patterns": {
            0: {"frequency": 0.8, "severity_range": (0.4, 0.9)},   # Fever
            3: {"frequency": 0.75, "severity_range": (0.3, 0.8)},  # Cough
            4: {"frequency": 0.4, "severity_range": (0.3, 0.9)},   # Shortness of breath
            1: {"frequency": 0.85, "severity_range": (0.5, 0.9)},  # Fatigue
            12: {"frequency": 0.6, "severity_range": (0.3, 0.7)},  # Headache
            16: {"frequency": 0.5, "severity_range": (0.4, 0.7)},  # Muscle pain
            6: {"frequency": 0.4, "severity_range": (0.2, 0.5)},   # Sore throat
            28: {"frequency": 0.5, "severity_range": (0.7, 1.0)},  # Loss of taste/smell (unique)
        },
        "etymology": "Corona (crown) + virus + disease + 2019",
        "differential_diagnosis": ["Influenza", "Pneumonia", "Common Cold"]
    },
    
    # Additional Diseases
    10: {
        "name": "Pneumonia",
        "medical_name": "Community-Acquired Pneumonia",
        "icd_10": "J18.9",
        "category": "Respiratory Infection",
        "description": "Infection that inflames air sacs in lungs",
        "typical_duration": "1-3 weeks",
        "symptom_ids": [0, 3, 4, 18, 1, 12, 5],
        "symptom_patterns": {
            0: {"frequency": 0.9, "severity_range": (0.6, 0.9)},   # High fever
            3: {"frequency": 0.95, "severity_range": (0.5, 0.9)},  # Productive cough
            4: {"frequency": 0.85, "severity_range": (0.5, 0.9)},  # Dyspnea
            18: {"frequency": 0.7, "severity_range": (0.4, 0.8)},  # Chest pain
            1: {"frequency": 0.9, "severity_range": (0.6, 0.8)},   # Fatigue
            12: {"frequency": 0.5, "severity_range": (0.3, 0.6)},  # Headache
            5: {"frequency": 0.6, "severity_range": (0.4, 0.7)}    # Wheezing
        },
        "etymology": "Greek 'pneumon' (lung) + '-ia' (condition)",
        "differential_diagnosis": ["Bronchitis", "COVID-19", "Tuberculosis"]
    },
    
    11: {
        "name": "Urinary Tract Infection",
        "medical_name": "Cystitis",
        "icd_10": "N39.0",
        "category": "Genitourinary",
        "description": "Infection in any part of urinary system",
        "typical_duration": "3-7 days with treatment",
        "symptom_ids": [27, 26, 0, 17, 9],
        "symptom_patterns": {
            27: {"frequency": 0.95, "severity_range": (0.5, 0.9)}, # Dysuria
            26: {"frequency": 0.9, "severity_range": (0.5, 0.8)},  # Frequent urination
            0: {"frequency": 0.3, "severity_range": (0.2, 0.5)},   # Low fever
            17: {"frequency": 0.6, "severity_range": (0.3, 0.7)},  # Lower back pain
            9: {"frequency": 0.2, "severity_range": (0.2, 0.4)}    # Nausea
        },
        "etymology": "Greek 'kystis' (bladder) + '-itis' (inflammation)",
        "differential_diagnosis": ["Kidney Stones", "Pyelonephritis", "Interstitial Cystitis"]
    },
    
    12: {
        "name": "Anxiety Disorder",
        "medical_name": "Generalized Anxiety Disorder",
        "icd_10": "F41.1",
        "category": "Mental Health",
        "description": "Excessive, persistent worry and fear",
        "typical_duration": "Chronic condition requiring management",
        "symptom_ids": [24, 19, 4, 13, 1, 12, 16, 9],
        "symptom_patterns": {
            24: {"frequency": 1.0, "severity_range": (0.6, 1.0)},  # Anxiety - core
            19: {"frequency": 0.7, "severity_range": (0.3, 0.7)},  # Rapid heartbeat
            4: {"frequency": 0.6, "severity_range": (0.3, 0.6)},   # Shortness of breath
            13: {"frequency": 0.5, "severity_range": (0.3, 0.6)},  # Dizziness
            1: {"frequency": 0.8, "severity_range": (0.4, 0.7)},   # Fatigue
            12: {"frequency": 0.6, "severity_range": (0.3, 0.7)},  # Headache
            16: {"frequency": 0.7, "severity_range": (0.3, 0.6)},  # Muscle tension
            9: {"frequency": 0.4, "severity_range": (0.2, 0.5)}    # Nausea
        },
        "etymology": "Latin 'anxietas' (troubled mind)",
        "differential_diagnosis": ["Panic Disorder", "PTSD", "Hyperthyroidism"]
    },
    
    13: {
        "name": "Sinusitis",
        "medical_name": "Acute Sinusitis",
        "icd_10": "J01.90",
        "category": "Respiratory",
        "description": "Inflammation of the sinuses",
        "typical_duration": "7-10 days",
        "symptom_ids": [12, 8, 7, 0, 18, 6],
        "symptom_patterns": {
            12: {"frequency": 0.9, "severity_range": (0.5, 0.8)},  # Facial pain/headache
            8: {"frequency": 0.95, "severity_range": (0.6, 0.9)},  # Nasal congestion
            7: {"frequency": 0.8, "severity_range": (0.4, 0.8)},   # Thick nasal discharge
            0: {"frequency": 0.4, "severity_range": (0.1, 0.4)},   # Low fever
            18: {"frequency": 0.7, "severity_range": (0.4, 0.7)},  # Facial pressure
            6: {"frequency": 0.5, "severity_range": (0.2, 0.5)}    # Sore throat
        },
        "etymology": "Latin 'sinus' (curve) + '-itis' (inflammation)",
        "differential_diagnosis": ["Allergic Rhinitis", "Migraine", "Dental Infection"]
    },
    
    14: {
        "name": "Bronchitis",
        "medical_name": "Acute Bronchitis",
        "icd_10": "J20.9",
        "category": "Respiratory",
        "description": "Inflammation of the bronchial tubes",
        "typical_duration": "10-14 days",
        "symptom_ids": [3, 5, 4, 1, 0, 18],
        "symptom_patterns": {
            3: {"frequency": 1.0, "severity_range": (0.5, 0.9)},   # Persistent cough
            5: {"frequency": 0.7, "severity_range": (0.3, 0.7)},   # Wheezing
            4: {"frequency": 0.5, "severity_range": (0.2, 0.6)},   # Mild dyspnea
            1: {"frequency": 0.7, "severity_range": (0.3, 0.6)},   # Fatigue
            0: {"frequency": 0.3, "severity_range": (0.1, 0.4)},   # Low fever
            18: {"frequency": 0.6, "severity_range": (0.2, 0.5)}   # Chest discomfort
        },
        "etymology": "Greek 'bronchos' (windpipe) + '-itis' (inflammation)",
        "differential_diagnosis": ["Pneumonia", "Asthma", "COPD"]
    }
}

# Helper functions for disease lookup and analysis
def get_disease_by_name(name):
    """Find disease by common name"""
    for did, disease in DISEASES.items():
        if disease['name'].lower() == name.lower():
            return did, disease
    return None, None

def get_diseases_by_symptom(symptom_id):
    """Find all diseases that include a specific symptom"""
    diseases = []
    for did, disease in DISEASES.items():
        if symptom_id in disease['symptom_ids']:
            frequency = disease['symptom_patterns'].get(symptom_id, {}).get('frequency', 0)
            diseases.append((did, disease['name'], frequency))
    return sorted(diseases, key=lambda x: x[2], reverse=True)

def calculate_symptom_match_score(symptom_list, disease_id):
    """Calculate how well a set of symptoms matches a disease pattern"""
    disease = DISEASES.get(disease_id)
    if not disease:
        return 0
    
    score = 0
    total_weight = 0
    
    # Check for presence of expected symptoms
    for symptom_id in disease['symptom_ids']:
        pattern = disease['symptom_patterns'].get(symptom_id, {})
        frequency = pattern.get('frequency', 0)
        total_weight += frequency
        
        if symptom_id in symptom_list:
            score += frequency
    
    # Penalize for unexpected symptoms
    for symptom_id in symptom_list:
        if symptom_id not in disease['symptom_ids']:
            score -= 0.1  # Small penalty for unexpected symptoms
    
    return max(0, score / total_weight) if total_weight > 0 else 0

def get_differential_diagnosis(symptom_list):
    """Get ranked list of possible diseases based on symptoms"""
    scores = []
    for did, disease in DISEASES.items():
        score = calculate_symptom_match_score(symptom_list, did)
        if score > 0:
            scores.append((did, disease['name'], score))
    
    return sorted(scores, key=lambda x: x[2], reverse=True)

if __name__ == "__main__":
    print("Medical Disease Schema loaded")
    print(f"Total diseases defined: {len(DISEASES)}")
    
    # Example: Find diseases associated with fever
    print("\nDiseases associated with fever:")
    fever_diseases = get_diseases_by_symptom(0)  # 0 is fever
    for did, name, frequency in fever_diseases[:5]:
        print(f"  {name}: {frequency*100:.0f}% chance of fever")
    
    # Example: Differential diagnosis
    print("\nDifferential diagnosis for symptoms: Fever, Cough, Fatigue")
    symptoms = [0, 3, 1]  # Fever, Cough, Fatigue
    differential = get_differential_diagnosis(symptoms)
    for did, name, score in differential[:3]:
        print(f"  {name}: {score*100:.1f}% match")
