"""
Demo Interface Example
Shows what the interactive medical diagnosis looks like
"""

print("""
======================================================================
           MEDICAL DIAGNOSIS DEMO - Quick Version           
======================================================================

This demo will ask about 7 common symptoms.
Answer 'yes' or 'no' for each symptom.

⚠️  This is for demonstration purposes only.

======================================================================

Press Enter to begin...

─────────────────────────────────────────────────────────────
Question 1 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: FEVER
Medical term: Pyrexia
Description: Elevated body temperature above normal range (>100.4°F/38°C)

Do you have this symptom? (yes/no): yes

How severe is your Fever?
Rate from 0 (very mild) to 10 (severe)
Severity (0-10): 7

─────────────────────────────────────────────────────────────
Question 2 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: FATIGUE
Medical term: Asthenia
Description: Persistent tiredness not relieved by rest

Do you have this symptom? (yes/no): yes

How severe is your Fatigue?
Rate from 0 (very mild) to 10 (severe)
Severity (0-10): 8

─────────────────────────────────────────────────────────────
Question 3 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: COUGH
Medical term: Tussis
Description: Sudden expulsion of air from lungs

Do you have this symptom? (yes/no): yes

How severe is your Cough?
Rate from 0 (very mild) to 10 (severe)
Severity (0-10): 5

─────────────────────────────────────────────────────────────
Question 4 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: SORE THROAT
Medical term: Pharyngitis
Description: Pain or irritation in the throat

Do you have this symptom? (yes/no): no

─────────────────────────────────────────────────────────────
Question 5 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: NAUSEA
Medical term: Nausea
Description: Feeling of sickness with inclination to vomit

Do you have this symptom? (yes/no): no

─────────────────────────────────────────────────────────────
Question 6 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: HEADACHE
Medical term: Cephalgia
Description: Pain in any region of the head

Do you have this symptom? (yes/no): yes

How severe is your Headache?
Rate from 0 (very mild) to 10 (severe)
Severity (0-10): 6

─────────────────────────────────────────────────────────────
Question 7 of 7
─────────────────────────────────────────────────────────────

SYMPTOM: MUSCLE PAIN
Medical term: Myalgia
Description: Pain in muscle or group of muscles

Do you have this symptom? (yes/no): yes

How severe is your Muscle Pain?
Rate from 0 (very mild) to 10 (severe)
Severity (0-10): 7

======================================================================
                        SYMPTOM SUMMARY                        
======================================================================

You reported 5 symptom(s):
  • Fever: 7.0/10
  • Fatigue: 8.0/10
  • Cough: 5.0/10
  • Headache: 6.0/10
  • Muscle Pain: 7.0/10

Analyzing symptoms...

======================================================================
                      DIAGNOSIS RESULTS                      
======================================================================

Most likely diagnosis: INFLUENZA
Medical name: Influenza
Confidence: 98.7%

Description: Viral infection caused by influenza viruses
ICD-10 Code: J11

Differential Diagnosis:
1. Influenza: 98.7%
2. COVID-19: 0.8%
3. Common Cold: 0.3%

Key Recommendations:
1. High confidence diagnosis - consider standard treatment protocols
2. Expected recovery: 5-7 days
3. Rule out: COVID-19, Common Cold, Bacterial Pneumonia

======================================================================
⚠️  Remember: Always consult a healthcare professional!
======================================================================
""")
