"""
Medical Symptom Schema
A comprehensive mapping of symptoms with medical terminology and classifications
"""

# Symptom categories for better organization
SYMPTOM_CATEGORIES = {
    "General/Constitutional": [0, 1, 2],
    "Respiratory": [3, 4, 5],
    "ENT (Ear, Nose, Throat)": [6, 7, 8],
    "Gastrointestinal": [9, 10, 11],
    "Neurological": [12, 13, 14],
    "Musculoskeletal": [15, 16, 17],
    "Cardiovascular": [18, 19, 20],
    "Dermatological": [21, 22, 23],
    "Psychological": [24, 25],
    "Urological": [26, 27],
    "Sensory": [28, 29]
}

# Symptom definitions with medical terminology
# Each symptom has: ID, common name, medical term, ICD-10 symptom code, description, severity scale
SYMPTOMS = {
    # General/Constitutional Symptoms
    0: {
        "name": "Fever",
        "medical_term": "Pyrexia",
        "icd_10": "R50.9",
        "description": "Elevated body temperature above normal range (>100.4°F/38°C)",
        "severity_scale": "temperature",  # 98.6-106°F
        "etymology": "Latin 'febris' - heat, fever"
    },
    1: {
        "name": "Fatigue",
        "medical_term": "Asthenia",
        "icd_10": "R53.83",
        "description": "Persistent tiredness not relieved by rest",
        "severity_scale": "0-10",
        "etymology": "Greek 'asthenes' - without strength"
    },
    2: {
        "name": "Weight Loss",
        "medical_term": "Cachexia",
        "icd_10": "R63.4",
        "description": "Unintentional decrease in body weight",
        "severity_scale": "percentage",
        "etymology": "Greek 'kakos' (bad) + 'hexis' (condition)"
    },
    
    # Respiratory Symptoms
    3: {
        "name": "Cough",
        "medical_term": "Tussis",
        "icd_10": "R05",
        "description": "Sudden expulsion of air from lungs",
        "severity_scale": "0-10",
        "etymology": "Latin 'tussis' - cough"
    },
    4: {
        "name": "Shortness of Breath",
        "medical_term": "Dyspnea",
        "icd_10": "R06.02",
        "description": "Difficulty breathing or feeling of breathlessness",
        "severity_scale": "0-10",
        "etymology": "Greek 'dys' (difficult) + 'pnoia' (breathing)"
    },
    5: {
        "name": "Wheezing",
        "medical_term": "Sibilant Rhonchi",
        "icd_10": "R06.2",
        "description": "High-pitched whistling sound when breathing",
        "severity_scale": "0-10",
        "etymology": "Latin 'sibilare' - to hiss"
    },
    
    # ENT Symptoms
    6: {
        "name": "Sore Throat",
        "medical_term": "Pharyngitis",
        "icd_10": "J02.9",
        "description": "Pain or irritation in the throat",
        "severity_scale": "0-10",
        "etymology": "Greek 'pharynx' (throat) + '-itis' (inflammation)"
    },
    7: {
        "name": "Runny Nose",
        "medical_term": "Rhinorrhea",
        "icd_10": "J34.89",
        "description": "Excess nasal drainage",
        "severity_scale": "0-10",
        "etymology": "Greek 'rhino' (nose) + 'rhoia' (flow)"
    },
    8: {
        "name": "Nasal Congestion",
        "medical_term": "Nasal Obstruction",
        "icd_10": "J34.89",
        "description": "Blockage of nasal passages",
        "severity_scale": "0-10",
        "etymology": "Latin 'congestio' - accumulation"
    },
    
    # Gastrointestinal Symptoms
    9: {
        "name": "Nausea",
        "medical_term": "Nausea",
        "icd_10": "R11.0",
        "description": "Feeling of sickness with inclination to vomit",
        "severity_scale": "0-10",
        "etymology": "Greek 'nausia' - seasickness"
    },
    10: {
        "name": "Vomiting",
        "medical_term": "Emesis",
        "icd_10": "R11.10",
        "description": "Forceful expulsion of stomach contents",
        "severity_scale": "frequency",
        "etymology": "Greek 'emein' - to vomit"
    },
    11: {
        "name": "Diarrhea",
        "medical_term": "Diarrhea",
        "icd_10": "K59.1",
        "description": "Loose, watery stools occurring more than three times in one day",
        "severity_scale": "frequency",
        "etymology": "Greek 'dia' (through) + 'rhein' (flow)"
    },
    
    # Neurological Symptoms
    12: {
        "name": "Headache",
        "medical_term": "Cephalgia",
        "icd_10": "R51",
        "description": "Pain in any region of the head",
        "severity_scale": "0-10",
        "etymology": "Greek 'kephale' (head) + 'algos' (pain)"
    },
    13: {
        "name": "Dizziness",
        "medical_term": "Vertigo",
        "icd_10": "R42",
        "description": "Sensation of spinning or loss of balance",
        "severity_scale": "0-10",
        "etymology": "Latin 'vertere' - to turn"
    },
    14: {
        "name": "Confusion",
        "medical_term": "Disorientation",
        "icd_10": "R41.0",
        "description": "Inability to think clearly or coherently",
        "severity_scale": "0-10",
        "etymology": "Latin 'confundere' - to mix together"
    },
    
    # Musculoskeletal Symptoms
    15: {
        "name": "Joint Pain",
        "medical_term": "Arthralgia",
        "icd_10": "M25.50",
        "description": "Pain in one or more joints",
        "severity_scale": "0-10",
        "etymology": "Greek 'arthron' (joint) + 'algos' (pain)"
    },
    16: {
        "name": "Muscle Pain",
        "medical_term": "Myalgia",
        "icd_10": "M79.1",
        "description": "Pain in muscle or group of muscles",
        "severity_scale": "0-10",
        "etymology": "Greek 'mys' (muscle) + 'algos' (pain)"
    },
    17: {
        "name": "Back Pain",
        "medical_term": "Dorsalgia",
        "icd_10": "M54.9",
        "description": "Pain in the back region",
        "severity_scale": "0-10",
        "etymology": "Latin 'dorsum' (back) + Greek 'algos' (pain)"
    },
    
    # Cardiovascular Symptoms
    18: {
        "name": "Chest Pain",
        "medical_term": "Thoracalgia",
        "icd_10": "R07.9",
        "description": "Pain or discomfort in the chest area",
        "severity_scale": "0-10",
        "etymology": "Greek 'thorax' (chest) + 'algos' (pain)"
    },
    19: {
        "name": "Rapid Heartbeat",
        "medical_term": "Tachycardia",
        "icd_10": "R00.0",
        "description": "Heart rate over 100 beats per minute",
        "severity_scale": "bpm",
        "etymology": "Greek 'tachys' (fast) + 'kardia' (heart)"
    },
    20: {
        "name": "Irregular Heartbeat",
        "medical_term": "Arrhythmia",
        "icd_10": "I49.9",
        "description": "Abnormal heart rhythm",
        "severity_scale": "frequency",
        "etymology": "Greek 'a' (without) + 'rhythmos' (rhythm)"
    },
    
    # Dermatological Symptoms
    21: {
        "name": "Rash",
        "medical_term": "Exanthem",
        "icd_10": "R21",
        "description": "Change in skin color or texture",
        "severity_scale": "area_coverage",
        "etymology": "Greek 'exanthema' - eruption"
    },
    22: {
        "name": "Itching",
        "medical_term": "Pruritus",
        "icd_10": "L29.9",
        "description": "Uncomfortable sensation causing desire to scratch",
        "severity_scale": "0-10",
        "etymology": "Latin 'prurire' - to itch"
    },
    23: {
        "name": "Swelling",
        "medical_term": "Edema",
        "icd_10": "R60.9",
        "description": "Abnormal accumulation of fluid in tissues",
        "severity_scale": "0-10",
        "etymology": "Greek 'oidema' - swelling"
    },
    
    # Psychological Symptoms
    24: {
        "name": "Anxiety",
        "medical_term": "Anxiety Disorder",
        "icd_10": "F41.9",
        "description": "Excessive worry or fear",
        "severity_scale": "0-10",
        "etymology": "Latin 'anxius' - troubled in mind"
    },
    25: {
        "name": "Depression",
        "medical_term": "Major Depressive Disorder",
        "icd_10": "F32.9",
        "description": "Persistent sadness and loss of interest",
        "severity_scale": "0-10",
        "etymology": "Latin 'deprimere' - to press down"
    },
    
    # Urological Symptoms
    26: {
        "name": "Frequent Urination",
        "medical_term": "Polyuria",
        "icd_10": "R35.0",
        "description": "Abnormally large volume of urination",
        "severity_scale": "frequency",
        "etymology": "Greek 'poly' (many) + 'ouron' (urine)"
    },
    27: {
        "name": "Painful Urination",
        "medical_term": "Dysuria",
        "icd_10": "R30.0",
        "description": "Pain or burning sensation during urination",
        "severity_scale": "0-10",
        "etymology": "Greek 'dys' (difficult) + 'ouron' (urine)"
    },
    
    # Sensory Symptoms
    28: {
        "name": "Blurred Vision",
        "medical_term": "Visual Disturbance",
        "icd_10": "H53.8",
        "description": "Lack of sharpness in vision",
        "severity_scale": "0-10",
        "etymology": "Latin 'visio' - sight"
    },
    29: {
        "name": "Hearing Loss",
        "medical_term": "Hypoacusis",
        "icd_10": "H91.90",
        "description": "Partial or total inability to hear",
        "severity_scale": "decibels",
        "etymology": "Greek 'hypo' (under) + 'akousis' (hearing)"
    }
}

# Function to get symptom by name
def get_symptom_by_name(name):
    """Find symptom ID by common name"""
    for sid, symptom in SYMPTOMS.items():
        if symptom['name'].lower() == name.lower():
            return sid, symptom
    return None, None

# Function to get symptom by medical term
def get_symptom_by_medical_term(term):
    """Find symptom ID by medical terminology"""
    for sid, symptom in SYMPTOMS.items():
        if symptom['medical_term'].lower() == term.lower():
            return sid, symptom
    return None, None

# Function to search symptoms by ICD-10 code
def get_symptoms_by_icd10_prefix(prefix):
    """Find all symptoms matching an ICD-10 code prefix"""
    matching = []
    for sid, symptom in SYMPTOMS.items():
        if symptom['icd_10'].startswith(prefix):
            matching.append((sid, symptom))
    return matching

# Severity interpretation functions
def interpret_severity(symptom_id, value):
    """Convert raw severity value to standardized 0-1 scale"""
    symptom = SYMPTOMS.get(symptom_id)
    if not symptom:
        return 0
    
    scale = symptom['severity_scale']
    
    if scale == "0-10":
        return value / 10.0
    elif scale == "temperature":
        # Normal is 98.6°F, max fever around 106°F
        if value <= 98.6:
            return 0
        elif value >= 106:
            return 1
        else:
            return (value - 98.6) / (106 - 98.6)
    elif scale == "percentage":
        return min(value / 100.0, 1.0)
    elif scale == "frequency":
        # More than 10 times per day is severe
        return min(value / 10.0, 1.0)
    elif scale == "bpm":
        # Normal 60-100, concerning >150
        if value <= 100:
            return 0
        elif value >= 150:
            return 1
        else:
            return (value - 100) / 50.0
    elif scale == "area_coverage":
        # Percentage of body covered
        return min(value / 100.0, 1.0)
    elif scale == "decibels":
        # Hearing loss in dB
        return min(value / 60.0, 1.0)  # 60dB loss is severe
    
    return 0

if __name__ == "__main__":
    print("Medical Symptom Schema loaded")
    print(f"Total symptoms defined: {len(SYMPTOMS)}")
    print("\nExample symptom lookup:")
    sid, symptom = get_symptom_by_name("Fever")
    if symptom:
        print(f"\nSymptom ID {sid}: {symptom['name']}")
        print(f"Medical term: {symptom['medical_term']}")
        print(f"ICD-10 code: {symptom['icd_10']}")
        print(f"Etymology: {symptom['etymology']}")
