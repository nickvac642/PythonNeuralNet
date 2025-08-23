"""
Interactive Medical Diagnosis System
User-friendly interface that guides through symptom assessment
"""

from medical_neural_network import MedicalDiagnosisNetwork
from medical_symptom_schema import SYMPTOMS
from medical_disease_schema import DISEASES
import os

class InteractiveMedicalDiagnosis:
    def __init__(self):
        self.network = MedicalDiagnosisNetwork(hidden_neurons=15, learning_rate=0.3, epochs=5000)
        self.symptom_responses = {}
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self):
        """Display the application header"""
        print("=" * 80)
        print("MEDICAL SYMPTOM ASSESSMENT SYSTEM".center(80))
        print("=" * 80)
        print("\nThis system will guide you through a comprehensive symptom assessment.")
        print("Please answer each question honestly for the most accurate diagnosis.")
        print("\n⚠️  DISCLAIMER: This is for educational purposes only.")
        print("Always consult a healthcare professional for medical advice.\n")
        print("=" * 80)
    
    def ask_symptom(self, symptom_id, symptom_info):
        """Ask about a single symptom with description"""
        print(f"\n{'─' * 60}")
        print(f"SYMPTOM {symptom_id + 1} of {len(SYMPTOMS)}")
        print(f"{'─' * 60}")
        
        print(f"\n{symptom_info['name'].upper()}")
        print(f"Medical Term: {symptom_info['medical_term']}")
        print(f"\nDescription: {symptom_info['description']}")
        
        # Add helpful context based on symptom type
        if symptom_info['severity_scale'] == "temperature":
            print("\nNote: Fever is typically defined as temperature above 100.4°F (38°C)")
        elif symptom_info['severity_scale'] == "frequency":
            print("\nNote: Consider if this occurs more frequently than normal for you")
        
        return self.get_yes_no_response()
    
    def get_yes_no_response(self):
        """Get yes/no response from user"""
        while True:
            response = input("\nDo you have this symptom? (yes/no/y/n): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no' (or 'y' or 'n')")
    
    def ask_severity(self, symptom_name, severity_scale):
        """Ask about symptom severity"""
        print(f"\nHow severe is your {symptom_name}?")
        
        if severity_scale == "0-10":
            print("Rate from 0 (none) to 10 (worst imaginable)")
            scale_desc = {
                0: "No symptoms",
                1-3: "Mild - noticeable but not limiting",
                4-6: "Moderate - interferes with some activities",
                7-9: "Severe - significantly limits activities",
                10: "Worst imaginable"
            }
            print("\nSeverity Scale:")
            print("  0     = No symptoms")
            print("  1-3   = Mild (noticeable but not limiting)")
            print("  4-6   = Moderate (interferes with some activities)")
            print("  7-9   = Severe (significantly limits activities)")
            print("  10    = Worst imaginable")
            
        elif severity_scale == "temperature":
            print("What is your temperature in Fahrenheit?")
            print("(Normal is around 98.6°F)")
            
        elif severity_scale == "frequency":
            print("How many times per day?")
            
        while True:
            try:
                if severity_scale == "0-10":
                    value = float(input("\nSeverity (0-10): "))
                    if 0 <= value <= 10:
                        return value
                    else:
                        print("Please enter a number between 0 and 10")
                elif severity_scale == "temperature":
                    value = float(input("\nTemperature (°F): "))
                    if 95 <= value <= 107:
                        # Convert to 0-10 scale
                        if value <= 98.6:
                            return 0
                        elif value >= 104:
                            return 10
                        else:
                            return (value - 98.6) / (104 - 98.6) * 10
                    else:
                        print("Please enter a realistic temperature (95-107°F)")
                elif severity_scale == "frequency":
                    value = float(input("\nTimes per day: "))
                    if value >= 0:
                        # Convert to 0-10 scale (10+ times = severity 10)
                        return min(value, 10)
                    else:
                        print("Please enter a positive number")
                else:
                    # Default 0-10 scale
                    value = float(input("\nSeverity (0-10): "))
                    if 0 <= value <= 10:
                        return value
            except ValueError:
                print("Please enter a valid number")
    
    def collect_symptoms(self):
        """Collect all symptom information from user"""
        self.clear_screen()
        self.display_header()
        
        input("\nPress Enter to begin the symptom assessment...")
        
        # Track symptoms for summary
        reported_symptoms = []
        
        # Ask about each symptom
        for symptom_id, symptom_info in SYMPTOMS.items():
            self.clear_screen()
            has_symptom = self.ask_symptom(symptom_id, symptom_info)
            
            if has_symptom:
                severity = self.ask_severity(
                    symptom_info['name'], 
                    symptom_info['severity_scale']
                )
                self.symptom_responses[symptom_info['name']] = severity
                reported_symptoms.append((symptom_info['name'], severity))
            
            # Option to skip remaining symptoms
            if (symptom_id + 1) < len(SYMPTOMS):
                print(f"\n{'─' * 60}")
                skip = input("\nPress Enter to continue or type 'skip' to finish: ").lower().strip()
                if skip == 'skip':
                    print("\nSkipping remaining symptoms...")
                    break
        
        return reported_symptoms
    
    def display_summary(self, reported_symptoms):
        """Display summary of reported symptoms"""
        self.clear_screen()
        print("=" * 80)
        print("SYMPTOM SUMMARY".center(80))
        print("=" * 80)
        
        if not reported_symptoms:
            print("\nNo symptoms reported.")
        else:
            print(f"\nYou reported {len(reported_symptoms)} symptom(s):\n")
            for symptom, severity in reported_symptoms:
                severity_desc = self.get_severity_description(severity)
                print(f"  • {symptom}: {severity_desc} (severity: {severity:.1f}/10)")
        
        print("\n" + "=" * 80)
        input("\nPress Enter to see diagnosis...")
    
    def get_severity_description(self, severity):
        """Convert numeric severity to description"""
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
    
    def display_diagnosis(self, results):
        """Display diagnosis results in user-friendly format"""
        self.clear_screen()
        print("=" * 80)
        print("DIAGNOSIS RESULTS".center(80))
        print("=" * 80)
        
        primary = results['primary_diagnosis']
        
        # Primary diagnosis
        print(f"\n{'PRIMARY DIAGNOSIS':^80}")
        print("─" * 80)
        print(f"\n{primary['name'].upper()} ({primary['medical_name']})")
        print(f"Confidence: {primary['confidence']*100:.1f}%")
        print(f"\nDescription: {primary['description']}")
        print(f"ICD-10 Code: {primary['icd_10']}")
        
        # Show confidence interpretation
        confidence = primary['confidence']
        if confidence > 0.8:
            confidence_desc = "HIGH CONFIDENCE - Strong symptom match"
        elif confidence > 0.6:
            confidence_desc = "MODERATE CONFIDENCE - Good symptom match"
        elif confidence > 0.4:
            confidence_desc = "LOW CONFIDENCE - Partial symptom match"
        else:
            confidence_desc = "VERY LOW CONFIDENCE - Poor symptom match"
        
        print(f"\nDiagnosis Confidence: {confidence_desc}")
        
        # Differential diagnosis
        print(f"\n{'DIFFERENTIAL DIAGNOSIS':^80}")
        print("─" * 80)
        print("\nOther possible conditions to consider:")
        
        for i, prob in enumerate(results['all_probabilities'][1:4]):  # Show next 3
            print(f"\n{i+2}. {prob['disease']} - {prob['probability']*100:.1f}% probability")
            disease_id = self.get_disease_id_by_name(prob['disease'])
            if disease_id is not None:
                disease = DISEASES[disease_id]
                print(f"   {disease['description']}")
        
        # Symptom analysis
        print(f"\n{'SYMPTOM ANALYSIS':^80}")
        print("─" * 80)
        
        analysis = results['symptoms_analysis']
        
        if analysis['expected_symptoms_present']:
            print("\n✓ Symptoms consistent with diagnosis:")
            for symptom in analysis['expected_symptoms_present'][:5]:  # Show top 5
                print(f"  • {symptom['symptom']} (typical in {symptom['typical_frequency']*100:.0f}% of cases)")
        
        if analysis['expected_symptoms_absent']:
            print("\n⚠ Common symptoms NOT present:")
            for symptom in analysis['expected_symptoms_absent'][:3]:  # Show top 3
                print(f"  • {symptom['symptom']} (present in {symptom['typical_frequency']*100:.0f}% of cases)")
        
        if analysis['unexpected_symptoms']:
            print("\n❓ Symptoms not typical for this diagnosis:")
            for symptom in analysis['unexpected_symptoms'][:3]:  # Show top 3
                print(f"  • {symptom['symptom']}")
        
        # Recommendations
        print(f"\n{'RECOMMENDATIONS':^80}")
        print("─" * 80)
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"\n{i}. {rec}")
        
        # Medical disclaimer
        print(f"\n{'⚠️  IMPORTANT MEDICAL DISCLAIMER ⚠️':^80}")
        print("─" * 80)
        print("\nThis diagnosis is generated by an AI system for educational purposes only.")
        print("It should NOT be used as a substitute for professional medical advice.")
        print("If you are experiencing concerning symptoms, please consult a healthcare provider.")
        
        print("\n" + "=" * 80)
    
    def get_disease_id_by_name(self, name):
        """Find disease ID by name"""
        for did, disease in DISEASES.items():
            if disease['name'] == name:
                return did
        return None
    
    def run(self):
        """Run the interactive diagnosis system"""
        # Check if we have a trained model
        try:
            print("Loading trained medical model...")
            self.network.load_model("trained_medical_model.json")
            print("Model loaded successfully!")
        except:
            print("No trained model found. Training new model...")
            print("This may take a few minutes...")
            self.network.train(cases_per_disease=50, verbose=True)
            self.network.save_model("trained_medical_model.json")
        
        while True:
            # Reset symptoms
            self.symptom_responses = {}
            
            # Collect symptoms
            reported_symptoms = self.collect_symptoms()
            
            # Show summary
            self.display_summary(reported_symptoms)
            
            # Get diagnosis
            if self.symptom_responses:
                results = self.network.diagnose(self.symptom_responses)
                self.display_diagnosis(results)
            else:
                print("\nNo symptoms reported - unable to provide diagnosis.")
            
            # Ask if user wants to try again
            print("\n" + "=" * 80)
            again = input("\nWould you like to assess different symptoms? (yes/no): ").lower().strip()
            if again not in ['yes', 'y']:
                print("\nThank you for using the Medical Diagnosis System.")
                print("Remember to consult a healthcare professional for any medical concerns.")
                break

# Run the interactive system
if __name__ == "__main__":
    system = InteractiveMedicalDiagnosis()
    system.run()
