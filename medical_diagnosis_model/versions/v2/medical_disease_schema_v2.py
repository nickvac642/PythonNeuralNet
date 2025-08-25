"""
Enhanced Medical Disease Schema V2
Includes syndrome-level diagnoses, diagnostic certainty, and clinical reasoning
"""

from medical_symptom_schema import SYMPTOMS

# Diagnostic certainty levels
DIAGNOSTIC_CERTAINTY = {
    "CLINICAL": "Can be diagnosed based on symptoms alone",
    "PRESUMPTIVE": "Likely diagnosis but benefits from testing",
    "CONFIRMATORY": "Requires specific testing for definitive diagnosis",
    "EXCLUSION": "Diagnosis made after ruling out other conditions"
}

# Disease categories for better differential diagnosis
DISEASE_CATEGORIES = {
    "Respiratory Febrile": ["Viral URI", "Influenza-like Illness", "COVID-19-like Illness", 
                           "Pneumonia Syndrome", "Acute Bronchitis", "Streptococcal Pharyngitis"],
    "Respiratory Allergic": ["Allergic Rhinitis", "Asthma Exacerbation"],
    "Gastrointestinal": ["Acute Gastroenteritis", "Food Poisoning", "Viral Gastroenteritis"],
    "Cardiovascular": ["Hypertension", "Acute Coronary Syndrome"],
    "Metabolic": ["Type 2 Diabetes", "Metabolic Syndrome"],
    "Rheumatologic": ["Rheumatoid Arthritis", "Osteoarthritis", "Fibromyalgia"],
    "Neurological": ["Migraine", "Tension Headache", "Cluster Headache"],
    "Psychiatric": ["Major Depression", "Generalized Anxiety Disorder", "Panic Disorder"],
    "Genitourinary": ["Urinary Tract Infection", "Pyelonephritis"],
    "General/Systemic": ["Viral Syndrome", "Febrile Illness of Unknown Origin"]
}

# Enhanced disease definitions with clinical reasoning
DISEASES_V2 = {
    # Syndrome-level diagnoses (what doctors actually diagnose without tests)
    0: {
        "name": "Viral Upper Respiratory Infection",
        "medical_name": "Viral URI",
        "icd_10": "J06.9",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "CLINICAL",
        "description": "Clinical syndrome of upper respiratory symptoms likely viral in origin",
        "typical_duration": "7-10 days",
        "required_tests": [],  # Clinical diagnosis
        "supportive_tests": ["Respiratory viral panel (if severe)"],
        "symptom_ids": [7, 8, 6, 3, 1, 12, 0],  # Runny nose, congestion, sore throat, cough, fatigue, headache, low fever
        "symptom_patterns": {
            7: {"frequency": 0.85, "severity_range": (0.3, 0.7)},   # Runny nose
            8: {"frequency": 0.80, "severity_range": (0.3, 0.7)},   # Nasal congestion
            6: {"frequency": 0.70, "severity_range": (0.2, 0.6)},   # Sore throat
            3: {"frequency": 0.75, "severity_range": (0.2, 0.6)},   # Cough
            1: {"frequency": 0.60, "severity_range": (0.2, 0.5)},   # Fatigue
            12: {"frequency": 0.50, "severity_range": (0.2, 0.5)},  # Headache
            0: {"frequency": 0.30, "severity_range": (0.1, 0.3)}    # LOW fever or none
        },
        "clinical_pearls": [
            "Most common respiratory diagnosis",
            "Cough may persist 2-3 weeks",
            "Antibiotics not indicated"
        ],
        "red_flags": ["Dyspnea", "Chest pain", "High fever >103°F"],
        "differential_diagnosis": ["Common Cold", "Influenza", "COVID-19", "Allergic Rhinitis"]
    },
    
    1: {
        "name": "Influenza-like Illness",
        "medical_name": "ILI (Influenza-like Illness)",
        "icd_10": "J11.1",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "PRESUMPTIVE",
        "description": "Clinical syndrome consistent with influenza but not laboratory confirmed",
        "typical_duration": "5-7 days",
        "required_tests": ["Influenza A/B antigen or PCR for confirmation"],
        "supportive_tests": ["CBC", "CRP if pneumonia suspected"],
        "symptom_ids": [0, 1, 3, 12, 16, 6],  # High fever, severe fatigue, cough, headache, myalgia
        "symptom_patterns": {
            0: {"frequency": 0.90, "severity_range": (0.6, 0.9)},   # HIGH fever
            1: {"frequency": 0.95, "severity_range": (0.7, 0.9)},   # SEVERE fatigue
            3: {"frequency": 0.85, "severity_range": (0.4, 0.7)},   # Cough
            12: {"frequency": 0.80, "severity_range": (0.5, 0.8)},  # Headache
            16: {"frequency": 0.85, "severity_range": (0.6, 0.8)},  # Myalgia (key symptom)
            6: {"frequency": 0.60, "severity_range": (0.3, 0.6)}    # Sore throat
        },
        "clinical_pearls": [
            "Abrupt onset is characteristic",
            "Myalgia more prominent than with common cold",
            "Consider antiviral if <48 hours of symptoms"
        ],
        "red_flags": ["Dyspnea", "Persistent fever", "Altered mental status"],
        "differential_diagnosis": ["COVID-19", "Viral URI", "Early bacterial pneumonia"]
    },
    
    2: {
        "name": "COVID-19-like Illness",
        "medical_name": "Suspected COVID-19",
        "icd_10": "U07.2",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "CONFIRMATORY",
        "description": "Clinical syndrome consistent with COVID-19 pending confirmation",
        "typical_duration": "7-14 days (acute phase)",
        "required_tests": ["SARS-CoV-2 PCR or antigen test"],
        "supportive_tests": ["Chest X-ray", "D-dimer", "CRP", "Ferritin if severe"],
        "symptom_ids": [0, 3, 4, 1, 12, 16, 6, 28, 11],  # Includes loss of taste/smell
        "symptom_patterns": {
            0: {"frequency": 0.75, "severity_range": (0.4, 0.9)},   # Variable fever
            3: {"frequency": 0.80, "severity_range": (0.3, 0.8)},   # Dry cough
            4: {"frequency": 0.40, "severity_range": (0.3, 0.9)},   # Dyspnea (concerning)
            1: {"frequency": 0.85, "severity_range": (0.5, 0.9)},   # Significant fatigue
            28: {"frequency": 0.60, "severity_range": (0.8, 1.0)},  # Anosmia/ageusia (specific)
            12: {"frequency": 0.65, "severity_range": (0.3, 0.7)},  # Headache
            16: {"frequency": 0.50, "severity_range": (0.4, 0.7)},  # Myalgia
            6: {"frequency": 0.50, "severity_range": (0.2, 0.5)},   # Sore throat
            11: {"frequency": 0.30, "severity_range": (0.3, 0.7)}   # GI symptoms
        },
        "clinical_pearls": [
            "Loss of taste/smell highly specific",
            "GI symptoms more common than flu",
            "Silent hypoxia possible",
            "Consider monoclonal antibodies if high risk"
        ],
        "red_flags": ["SpO2 <94%", "Respiratory rate >24", "Confusion"],
        "differential_diagnosis": ["Influenza", "Viral URI", "Pneumonia"]
    },
    
    3: {
        "name": "Viral Syndrome",
        "medical_name": "Viral Syndrome, Unspecified",
        "icd_10": "B34.9",
        "category": "General/Systemic",
        "diagnostic_certainty": "CLINICAL",
        "description": "Nonspecific viral illness with systemic symptoms",
        "typical_duration": "3-7 days",
        "required_tests": [],
        "supportive_tests": ["CBC if prolonged", "Mono spot if adolescent"],
        "symptom_ids": [1, 0, 12, 16, 9],  # Fatigue, low fever, headache, myalgia, mild nausea
        "symptom_patterns": {
            1: {"frequency": 0.90, "severity_range": (0.4, 0.7)},   # Fatigue prominent
            0: {"frequency": 0.60, "severity_range": (0.2, 0.5)},   # Low-grade fever
            12: {"frequency": 0.70, "severity_range": (0.3, 0.6)},  # Headache
            16: {"frequency": 0.60, "severity_range": (0.3, 0.6)},  # Myalgia
            9: {"frequency": 0.30, "severity_range": (0.2, 0.4)}    # Mild nausea
        },
        "clinical_pearls": [
            "Diagnosis of exclusion",
            "Supportive care mainstay",
            "Consider EBV in young adults"
        ],
        "red_flags": ["Persistent fever >1 week", "Severe headache", "Neck stiffness"],
        "differential_diagnosis": ["Early bacterial infection", "Mononucleosis", "HIV seroconversion"]
    },
    
    4: {
        "name": "Acute Gastroenteritis",
        "medical_name": "Acute Gastroenteritis, Unspecified",
        "icd_10": "K52.9",
        "category": "Gastrointestinal",
        "diagnostic_certainty": "CLINICAL",
        "description": "Acute inflammation of GI tract, likely infectious",
        "typical_duration": "1-3 days",
        "required_tests": [],
        "supportive_tests": ["Stool studies if bloody/prolonged", "BMP if dehydrated"],
        "symptom_ids": [11, 9, 10, 1, 0, 17],  # Diarrhea, nausea, vomiting, fatigue, low fever, cramping
        "symptom_patterns": {
            11: {"frequency": 0.95, "severity_range": (0.5, 0.9)},  # Diarrhea
            9: {"frequency": 0.85, "severity_range": (0.4, 0.8)},   # Nausea
            10: {"frequency": 0.70, "severity_range": (0.3, 0.8)},  # Vomiting
            1: {"frequency": 0.80, "severity_range": (0.4, 0.7)},   # Fatigue
            0: {"frequency": 0.40, "severity_range": (0.1, 0.4)},   # Low fever
            17: {"frequency": 0.60, "severity_range": (0.4, 0.7)}   # Abdominal cramping
        },
        "clinical_pearls": [
            "Viral > bacterial in most cases",
            "Focus on hydration",
            "BRAT diet outdated advice"
        ],
        "red_flags": ["Bloody diarrhea", "Severe dehydration", "High fever", ">10 stools/day"],
        "differential_diagnosis": ["Food poisoning", "C. diff (if recent antibiotics)", "IBD flare"]
    },
    
    5: {
        "name": "Pneumonia Syndrome",
        "medical_name": "Community-Acquired Pneumonia Syndrome",
        "icd_10": "J18.9",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "PRESUMPTIVE",
        "description": "Clinical syndrome of lung infection requiring imaging confirmation",
        "typical_duration": "1-3 weeks",
        "required_tests": ["Chest X-ray", "CBC", "BMP"],
        "supportive_tests": ["Blood cultures if hospitalized", "Sputum culture", "Procalcitonin"],
        "symptom_ids": [0, 3, 4, 18, 1, 5],  # Fever, productive cough, dyspnea, pleuritic chest pain
        "symptom_patterns": {
            0: {"frequency": 0.85, "severity_range": (0.5, 0.9)},   # Fever
            3: {"frequency": 0.95, "severity_range": (0.5, 0.9)},   # Productive cough
            4: {"frequency": 0.75, "severity_range": (0.4, 0.8)},   # Dyspnea
            18: {"frequency": 0.65, "severity_range": (0.4, 0.8)},  # Pleuritic chest pain
            1: {"frequency": 0.90, "severity_range": (0.5, 0.8)},   # Fatigue
            5: {"frequency": 0.50, "severity_range": (0.3, 0.7)}    # Wheezing/rales
        },
        "clinical_pearls": [
            "Diagnosis requires infiltrate on imaging",
            "Use CURB-65 for severity",
            "Atypical presentation in elderly"
        ],
        "red_flags": ["Hypoxia", "Hypotension", "Confusion", "Respiratory rate >30"],
        "differential_diagnosis": ["Bronchitis", "CHF", "PE", "Lung cancer"]
    },
    
    # Add the original specific diagnoses that require confirmation
    6: {
        "name": "Influenza (Confirmed)",
        "medical_name": "Influenza A or B",
        "icd_10": "J09-J11",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "CONFIRMATORY",
        "description": "Laboratory-confirmed influenza infection",
        "typical_duration": "5-7 days",
        "required_tests": ["Positive influenza A/B test"],
        "supportive_tests": [],
        "symptom_ids": [0, 1, 3, 12, 16, 6, 4],
        "symptom_patterns": {
            # Same as ILI but confirmed
            0: {"frequency": 0.95, "severity_range": (0.7, 0.9)},
            1: {"frequency": 0.95, "severity_range": (0.7, 0.9)},
            3: {"frequency": 0.85, "severity_range": (0.4, 0.7)},
            12: {"frequency": 0.80, "severity_range": (0.5, 0.8)},
            16: {"frequency": 0.85, "severity_range": (0.6, 0.8)},
            6: {"frequency": 0.60, "severity_range": (0.3, 0.6)},
            4: {"frequency": 0.30, "severity_range": (0.3, 0.7)}
        },
        "clinical_pearls": [
            "Oseltamivir within 48 hours",
            "High-risk patients benefit most from treatment",
            "Can shed virus before symptoms"
        ],
        "red_flags": ["Secondary bacterial pneumonia", "Myocarditis", "Encephalopathy"],
        "differential_diagnosis": ["If positive test, diagnosis confirmed"]
    },
    
    7: {
        "name": "COVID-19 (Confirmed)",
        "medical_name": "SARS-CoV-2 Infection",
        "icd_10": "U07.1",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "CONFIRMATORY",
        "description": "Laboratory-confirmed SARS-CoV-2 infection",
        "typical_duration": "7-14 days (acute)",
        "required_tests": ["Positive SARS-CoV-2 test"],
        "supportive_tests": ["CXR", "D-dimer", "Inflammatory markers if severe"],
        "symptom_ids": [0, 3, 4, 1, 12, 16, 6, 28, 11],
        "symptom_patterns": {
            # Same as COVID-like illness but confirmed
            0: {"frequency": 0.75, "severity_range": (0.4, 0.9)},
            3: {"frequency": 0.80, "severity_range": (0.3, 0.8)},
            4: {"frequency": 0.40, "severity_range": (0.3, 0.9)},
            1: {"frequency": 0.85, "severity_range": (0.5, 0.9)},
            28: {"frequency": 0.60, "severity_range": (0.8, 1.0)},
            12: {"frequency": 0.65, "severity_range": (0.3, 0.7)},
            16: {"frequency": 0.50, "severity_range": (0.4, 0.7)},
            6: {"frequency": 0.50, "severity_range": (0.2, 0.5)},
            11: {"frequency": 0.30, "severity_range": (0.3, 0.7)}
        },
        "clinical_pearls": [
            "Monitor oxygen saturation",
            "Consider antivirals in high risk",
            "Watch for day 7-10 deterioration",
            "Long COVID possible"
        ],
        "red_flags": ["Silent hypoxia", "D-dimer elevation", "Cytokine storm markers"],
        "differential_diagnosis": ["If positive test, diagnosis confirmed"]
    },
    
    # Include other important diagnoses
    8: {
        "name": "Streptococcal Pharyngitis",
        "medical_name": "Group A Strep Pharyngitis",
        "icd_10": "J02.0",
        "category": "Respiratory Infection",
        "diagnostic_certainty": "CONFIRMATORY",
        "description": "Bacterial throat infection requiring antibiotics",
        "typical_duration": "5-7 days with treatment",
        "required_tests": ["Rapid strep test or throat culture"],
        "supportive_tests": [],
        "symptom_ids": [6, 0, 12, 23, 1],  # Severe sore throat, fever, headache, lymph nodes
        "symptom_patterns": {
            6: {"frequency": 1.0, "severity_range": (0.6, 0.9)},    # SEVERE sore throat
            0: {"frequency": 0.85, "severity_range": (0.5, 0.8)},   # Fever
            12: {"frequency": 0.60, "severity_range": (0.3, 0.6)},  # Headache
            23: {"frequency": 0.80, "severity_range": (0.4, 0.7)},  # Lymphadenopathy
            1: {"frequency": 0.50, "severity_range": (0.3, 0.5)},   # Fatigue
            3: {"frequency": 0.1, "severity_range": (0.0, 0.2)}     # ABSENCE of cough (key)
        },
        "clinical_pearls": [
            "Centor criteria guide testing",
            "Absence of cough is key feature",
            "Treat to prevent rheumatic fever"
        ],
        "red_flags": ["Drooling", "Trismus", "Unilateral swelling (abscess)"],
        "differential_diagnosis": ["Viral pharyngitis", "Mono", "Peritonsillar abscess"]
    },
    
    9: {
        "name": "Allergic Rhinitis",
        "medical_name": "Allergic Rhinitis",
        "icd_10": "J30.9",
        "category": "Allergic Condition",
        "diagnostic_certainty": "CLINICAL",
        "description": "IgE-mediated nasal inflammation from allergen exposure",
        "typical_duration": "Seasonal or perennial",
        "required_tests": [],
        "supportive_tests": ["Allergy testing if severe", "IgE levels"],
        "symptom_ids": [7, 8, 22, 28, 12],
        "symptom_patterns": {
            7: {"frequency": 0.95, "severity_range": (0.4, 0.8)},   # Clear rhinorrhea
            8: {"frequency": 0.90, "severity_range": (0.4, 0.8)},   # Nasal congestion
            22: {"frequency": 0.85, "severity_range": (0.4, 0.8)},  # Itchy nose/eyes
            28: {"frequency": 0.70, "severity_range": (0.3, 0.6)},  # Watery eyes
            12: {"frequency": 0.40, "severity_range": (0.2, 0.5)},  # Sinus headache
            0: {"frequency": 0.0, "severity_range": (0.0, 0.0)}     # NO FEVER (key)
        },
        "clinical_pearls": [
            "No fever distinguishes from infection",
            "Allergic salute and shiners",
            "Seasonal pattern helpful"
        ],
        "red_flags": ["Unilateral symptoms", "Bloody discharge", "Facial pain"],
        "differential_diagnosis": ["Viral URI", "Sinusitis", "Vasomotor rhinitis"]
    },
    
    10: {
        "name": "Urinary Tract Infection",
        "medical_name": "Uncomplicated Cystitis",
        "icd_10": "N39.0",
        "category": "Genitourinary",
        "diagnostic_certainty": "PRESUMPTIVE",
        "description": "Bacterial infection of bladder",
        "typical_duration": "3-5 days with treatment",
        "required_tests": ["Urinalysis"],
        "supportive_tests": ["Urine culture if recurrent/complicated"],
        "symptom_ids": [27, 26, 17, 0, 9],
        "symptom_patterns": {
            27: {"frequency": 0.95, "severity_range": (0.5, 0.9)},  # Dysuria
            26: {"frequency": 0.90, "severity_range": (0.5, 0.8)},  # Frequency/urgency
            17: {"frequency": 0.60, "severity_range": (0.3, 0.6)},  # Suprapubic pain
            0: {"frequency": 0.20, "severity_range": (0.1, 0.3)},   # Usually no fever
            9: {"frequency": 0.15, "severity_range": (0.1, 0.3)}    # Mild nausea
        },
        "clinical_pearls": [
            "Uncomplicated in healthy women",
            "3 days of antibiotics sufficient",
            "Pyridium for symptom relief"
        ],
        "red_flags": ["Fever", "Flank pain", "Prior resistant organisms"],
        "differential_diagnosis": ["Pyelonephritis", "Vaginitis", "Interstitial cystitis"]
    }
}

# Clinical decision rules
CLINICAL_RULES = {
    "centor_criteria": {
        "description": "For strep throat probability",
        "criteria": {
            "fever": 1,
            "absence_of_cough": 1,
            "tender_lymph_nodes": 1,
            "tonsillar_exudate": 1,
            "age_15_44": 0,
            "age_under_15": 1,
            "age_over_44": -1
        },
        "interpretation": {
            0: "Low risk (<10%), no testing",
            1: "Low risk (<10%), no testing",
            2: "Intermediate (15%), consider testing",
            3: "High risk (35%), test",
            4: "High risk (55%), test or empiric treatment"
        }
    },
    
    "curb_65": {
        "description": "Pneumonia severity",
        "criteria": {
            "confusion": 1,
            "urea_high": 1,
            "respiratory_rate_30": 1,
            "blood_pressure_low": 1,
            "age_65_plus": 1
        },
        "interpretation": {
            0: "Outpatient",
            1: "Consider admission",
            2: "Admit",
            3: "ICU consideration",
            4: "ICU",
            5: "ICU"
        }
    }
}

# Helper functions for clinical reasoning
def get_syndrome_from_symptoms(symptom_ids):
    """Determine likely syndrome based on symptom pattern"""
    respiratory_symptoms = [3, 4, 5, 6, 7, 8]  # Cough, dyspnea, wheeze, sore throat, rhinorrhea, congestion
    gi_symptoms = [9, 10, 11]  # Nausea, vomiting, diarrhea
    systemic_symptoms = [0, 1, 16]  # Fever, fatigue, myalgia
    
    resp_count = sum(1 for s in symptom_ids if s in respiratory_symptoms)
    gi_count = sum(1 for s in symptom_ids if s in gi_symptoms)
    systemic_count = sum(1 for s in symptom_ids if s in systemic_symptoms)
    
    # Heuristic: fever + any key upper-respiratory symptom is enough to call it respiratory febrile
    if 0 in symptom_ids and any(s in symptom_ids for s in (3, 6, 7, 8)):
        return "Respiratory Febrile"

    if resp_count >= 2 and systemic_count >= 1:
        return "Respiratory Febrile"
    elif gi_count >= 2:
        return "Gastrointestinal"
    elif systemic_count >= 2 and resp_count == 0 and gi_count == 0:
        return "General/Systemic"
    else:
        return "Undifferentiated"

def get_appropriate_differential(primary_syndrome):
    """Get relevant differential diagnosis based on syndrome"""
    syndrome_differentials = {
        "Respiratory Febrile": [
            "Viral Upper Respiratory Infection",
            "Influenza-like Illness",
            "COVID-19-like Illness",
            "Pneumonia Syndrome",
            "Streptococcal Pharyngitis"
        ],
        "Gastrointestinal": [
            "Acute Gastroenteritis",
            "Food Poisoning",
            "Viral Gastroenteritis",
            "Bacterial Gastroenteritis"
        ],
        "General/Systemic": [
            "Viral Syndrome",
            "Early Bacterial Infection",
            "Mononucleosis"
        ]
    }
    
    return syndrome_differentials.get(primary_syndrome, ["Viral Syndrome"])

def requires_testing(disease_name):
    """Check if a diagnosis requires confirmatory testing"""
    confirmatory_diagnoses = [
        "Influenza (Confirmed)",
        "COVID-19 (Confirmed)",
        "Streptococcal Pharyngitis",
        "Pneumonia Syndrome"
    ]
    return disease_name in confirmatory_diagnoses

def get_syndrome_diagnosis(specific_diagnosis):
    """Convert specific diagnosis to syndrome level if no test available"""
    syndrome_mapping = {
        "Influenza (Confirmed)": "Influenza-like Illness",
        "COVID-19 (Confirmed)": "COVID-19-like Illness",
        "Streptococcal Pharyngitis": "Viral Upper Respiratory Infection",
        "Pneumonia Syndrome": "Acute Bronchitis"
    }
    return syndrome_mapping.get(specific_diagnosis, specific_diagnosis)

# Clinical severity assessment
def assess_severity(symptom_ids, severity_vector):
    """Assess overall illness severity"""
    red_flag_symptoms = {
        4: 0.5,   # Dyspnea threshold
        18: 0.6,  # Chest pain threshold
        14: 0.5,  # Confusion threshold
        13: 0.7   # Severe dizziness threshold
    }
    
    # Check for red flags
    for symptom_id, threshold in red_flag_symptoms.items():
        if symptom_id in symptom_ids and symptom_id < len(severity_vector) and severity_vector[symptom_id] > threshold:
            return "SEVERE - Immediate evaluation needed"
    
    # Calculate average severity of present symptoms
    present_severities = [severity_vector[sid] for sid in symptom_ids if sid < len(severity_vector) and severity_vector[sid] > 0]
    
    if not present_severities:
        return "MILD"
    
    avg_severity = sum(present_severities) / len(present_severities)
    
    if avg_severity > 0.7:
        return "SEVERE"
    elif avg_severity > 0.5:
        return "MODERATE"
    else:
        return "MILD"

if __name__ == "__main__":
    print("Enhanced Medical Disease Schema V2 loaded")
    print(f"Total diagnoses: {len(DISEASES_V2)}")
    print(f"Including {sum(1 for d in DISEASES_V2.values() if d['diagnostic_certainty'] == 'CLINICAL')} clinical diagnoses")
    print(f"and {sum(1 for d in DISEASES_V2.values() if d['diagnostic_certainty'] == 'CONFIRMATORY')} requiring confirmation")
