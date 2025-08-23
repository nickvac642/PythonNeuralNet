"""
Quick Medical Diagnosis Demo
Demonstrates the interactive interface with a subset of symptoms
"""

from medical_neural_network import MedicalDiagnosisNetwork
from medical_symptom_schema import SYMPTOMS
from medical_disease_schema import DISEASES

# Select key symptoms for demo
DEMO_SYMPTOMS = [0, 1, 3, 6, 9, 12, 16]  # Fever, Fatigue, Cough, Sore Throat, Nausea, Headache, Muscle Pain

def run_quick_demo():
    print("=" * 70)
    print("MEDICAL DIAGNOSIS DEMO - Quick Version".center(70))
    print("=" * 70)
    print("\nThis demo will ask about 7 common symptoms.")
    print("Answer 'yes' or 'no' for each symptom.")
    print("\n⚠️  This is for demonstration purposes only.\n")
    print("=" * 70)
    
    input("\nPress Enter to begin...")
    
    # Load or train model
    network = MedicalDiagnosisNetwork(hidden_neurons=15, learning_rate=0.3, epochs=5000)
    try:
        network.load_model("trained_medical_model.json")
    except:
        print("\nTraining model... (this will take a moment)")
        network.train(cases_per_disease=50, verbose=False)
        network.save_model("trained_medical_model.json")
    
    # Collect symptoms
    symptom_responses = {}
    
    for i, symptom_id in enumerate(DEMO_SYMPTOMS):
        symptom = SYMPTOMS[symptom_id]
        print(f"\n{'─' * 60}")
        print(f"Question {i+1} of {len(DEMO_SYMPTOMS)}")
        print(f"{'─' * 60}")
        
        print(f"\nSYMPTOM: {symptom['name'].upper()}")
        print(f"Medical term: {symptom['medical_term']}")
        print(f"Description: {symptom['description']}")
        
        # Get yes/no
        while True:
            response = input("\nDo you have this symptom? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                has_symptom = True
                break
            elif response in ['no', 'n']:
                has_symptom = False
                break
            else:
                print("Please enter 'yes' or 'no'")
        
        # If yes, ask severity
        if has_symptom:
            print(f"\nHow severe is your {symptom['name']}?")
            print("Rate from 0 (very mild) to 10 (severe)")
            
            while True:
                try:
                    severity = float(input("Severity (0-10): "))
                    if 0 <= severity <= 10:
                        symptom_responses[symptom['name']] = severity
                        break
                    else:
                        print("Please enter a number between 0 and 10")
                except ValueError:
                    print("Please enter a valid number")
    
    # Show summary
    print("\n" + "=" * 70)
    print("SYMPTOM SUMMARY".center(70))
    print("=" * 70)
    
    if not symptom_responses:
        print("\nNo symptoms reported - you appear to be healthy!")
        return
    else:
        print(f"\nYou reported {len(symptom_responses)} symptom(s):")
        for symptom, severity in symptom_responses.items():
            print(f"  • {symptom}: {severity}/10")
    
    # Get diagnosis
    print("\nAnalyzing symptoms...")
    results = network.diagnose(symptom_responses)
    
    # Display results
    print("\n" + "=" * 70)
    print("DIAGNOSIS RESULTS".center(70))
    print("=" * 70)
    
    primary = results['primary_diagnosis']
    print(f"\nMost likely diagnosis: {primary['name'].upper()}")
    print(f"Medical name: {primary['medical_name']}")
    print(f"Confidence: {primary['confidence']*100:.1f}%")
    print(f"\nDescription: {primary['description']}")
    print(f"ICD-10 Code: {primary['icd_10']}")
    
    # Show top 3 possibilities
    print("\nDifferential Diagnosis:")
    for i, prob in enumerate(results['all_probabilities'][:3]):
        print(f"{i+1}. {prob['disease']}: {prob['probability']*100:.1f}%")
    
    # Key recommendations
    print("\nKey Recommendations:")
    for i, rec in enumerate(results['recommendations'][:3], 1):
        print(f"{i}. {rec}")
    
    print("\n" + "=" * 70)
    print("⚠️  Remember: Always consult a healthcare professional!")
    print("=" * 70)

if __name__ == "__main__":
    run_quick_demo()
