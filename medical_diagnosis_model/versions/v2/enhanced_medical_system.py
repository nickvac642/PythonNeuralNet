"""
Enhanced Medical Diagnosis System
Integrates all features: categories, history, PDF export, and more diseases
"""

import os
from datetime import datetime
from medical_neural_network_v2 import ClinicalReasoningNetwork
from medical_symptom_schema import SYMPTOMS, SYMPTOM_CATEGORIES, get_symptom_by_name
from medical_disease_schema import DISEASES
from medical_disease_schema_v2 import DISEASES_V2
from diagnosis_history import DiagnosisHistory
from pdf_exporter import PDFExporter

class EnhancedMedicalSystem:
    def __init__(self):
        """Initialize the enhanced medical system with all features"""
        self.network = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=1000)
        self.history_manager = DiagnosisHistory()
        self.pdf_exporter = PDFExporter()
        self.current_session = None
        self.patient_id = None
        
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_main_menu(self):
        """Display the main menu"""
        self.clear_screen()
        print("=" * 80)
        print("ENHANCED MEDICAL DIAGNOSIS SYSTEM".center(80))
        print("=" * 80)
        print("\nWelcome to the AI-Powered Medical Diagnosis System")
        print("Now with 15 diseases, symptom categories, history tracking, and PDF export!")
        print("\n" + "─" * 80)
        
        print("\nMAIN MENU:")
        print("1. New Diagnosis")
        print("2. View Patient History")
        print("3. Generate Patient Report")
        print("4. View Recent Diagnoses")
        print("5. System Information")
        print("6. Exit")
        
        print("\n" + "─" * 80)
        
        while True:
            choice = input("\nSelect an option (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            print("Please enter a valid option (1-6)")
    
    def get_patient_id(self):
        """Get or create patient ID"""
        print("\nPATIENT IDENTIFICATION")
        print("─" * 40)
        print("1. New Patient")
        print("2. Existing Patient")
        
        choice = input("\nSelect option (1-2): ").strip()
        
        if choice == '1':
            name = input("Enter patient name (or press Enter for anonymous): ").strip()
            if name:
                patient_id = name.replace(' ', '_').lower()
                patient_id = f"{patient_id}_{datetime.now().strftime('%Y%m%d')}"
            else:
                patient_id = None
            return patient_id
        else:
            patients = self.history_manager.get_all_patients()
            if not patients:
                print("No existing patients found. Creating new patient...")
                return None
            
            print("\nExisting Patients:")
            for i, patient in enumerate(patients, 1):
                print(f"{i}. {patient}")
            
            while True:
                try:
                    idx = int(input(f"\nSelect patient (1-{len(patients)}): ")) - 1
                    if 0 <= idx < len(patients):
                        return patients[idx]
                except ValueError:
                    pass
                print("Invalid selection")
    
    def conduct_diagnosis_by_category(self):
        """Conduct diagnosis with symptom categories"""
        symptom_responses = {}
        
        print("\n" + "=" * 80)
        print("SYMPTOM ASSESSMENT BY CATEGORY".center(80))
        print("=" * 80)
        print("\nWe'll go through symptoms organized by body system.")
        print("You can skip entire categories if not relevant.")
        
        input("\nPress Enter to begin...")
        
        # Go through each category
        for category_name, symptom_ids in SYMPTOM_CATEGORIES.items():
            self.clear_screen()
            print("=" * 80)
            print(f"CATEGORY: {category_name}".center(80))
            print("=" * 80)
            
            # Show symptoms in this category
            print("\nSymptoms in this category:")
            for sid in symptom_ids:
                if sid in SYMPTOMS:
                    print(f"  • {SYMPTOMS[sid]['name']}")
            
            # Ask if relevant
            print("\n" + "─" * 60)
            check = input("\nDo you have any symptoms in this category? (yes/no/skip all): ").lower().strip()
            
            if check == 'skip all' or check == 'skip':
                print("Skipping remaining categories...")
                break
            elif check in ['no', 'n']:
                continue
            
            # Ask about each symptom in category
            for sid in symptom_ids:
                if sid not in SYMPTOMS:
                    continue
                    
                symptom = SYMPTOMS[sid]
                
                print("\n" + "─" * 60)
                print(f"\n{symptom['name'].upper()}")
                print(f"Medical term: {symptom['medical_term']}")
                print(f"Description: {symptom['description']}")
                
                has_symptom = self.get_yes_no_response()
                
                if has_symptom:
                    severity = self.ask_severity(symptom['name'], symptom['severity_scale'])
                    symptom_responses[symptom['name']] = severity
        
        return symptom_responses
    
    def get_yes_no_response(self):
        """Get yes/no response"""
        while True:
            response = input("\nDo you have this symptom? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            print("Please enter 'yes' or 'no'")
    
    def ask_severity(self, symptom_name, severity_scale):
        """Ask about symptom severity"""
        print(f"\nHow severe is your {symptom_name}?")
        
        if severity_scale == "0-10":
            print("Rate from 0 (none) to 10 (worst imaginable)")
            print("  0-2  = Mild")
            print("  3-5  = Moderate")
            print("  6-8  = Severe")
            print("  9-10 = Very Severe")
        
        while True:
            try:
                value = float(input("\nSeverity (0-10): "))
                if 0 <= value <= 10:
                    return value
                print("Please enter a number between 0 and 10")
            except ValueError:
                print("Please enter a valid number")
    
    def display_diagnosis_results(self, results, symptom_responses):
        """Display comprehensive diagnosis results"""
        self.clear_screen()
        print("=" * 80)
        print("DIAGNOSIS RESULTS".center(80))
        print("=" * 80)
        
        primary = results['primary_diagnosis']
        
        # Primary diagnosis with visual confidence
        print(f"\nPRIMARY DIAGNOSIS: {primary['name'].upper()}")
        print(f"Medical Name: {primary['medical_name']}")
        print(f"ICD-10 Code: {primary['icd_10']}")
        
        # Visual confidence bar
        confidence = primary['confidence']
        bar_length = 40
        filled = int(confidence * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"\nConfidence: [{bar}] {confidence*100:.1f}%")
        
        # Confidence interpretation
        if confidence > 0.8:
            conf_msg = "HIGH CONFIDENCE - Strong symptom match"
            conf_color = "🟢"
        elif confidence > 0.6:
            conf_msg = "MODERATE CONFIDENCE - Good symptom match"
            conf_color = "🟡"
        else:
            conf_msg = "LOW CONFIDENCE - Consider other possibilities"
            conf_color = "🔴"
        
        print(f"{conf_color} {conf_msg}")
        
        print(f"\nDescription: {primary['description']}")
        
        # Disease information (try v2 schema first, then fallback to v1 if present)
        printed_meta = False
        for did, disease in DISEASES_V2.items():
            if disease['name'] == primary['name']:
                print(f"Category: {disease.get('category','N/A')}")
                if 'typical_duration' in disease:
                    print(f"Typical Duration: {disease['typical_duration']}")
                if 'etymology' in disease:
                    print(f"Etymology: {disease['etymology']}")
                printed_meta = True
                break
        if not printed_meta:
            for did, disease in DISEASES.items():
                if disease['name'] == primary['name']:
                    print(f"Category: {disease.get('category','N/A')}")
                    if 'typical_duration' in disease:
                        print(f"Typical Duration: {disease['typical_duration']}")
                    if 'etymology' in disease:
                        print(f"Etymology: {disease['etymology']}")
                    break
        
        # Differential diagnosis table
        print("\n" + "─" * 80)
        print("DIFFERENTIAL DIAGNOSIS".center(80))
        print("─" * 80)
        print(f"{'Rank':<6} {'Disease':<30} {'Probability':<15} {'ICD-10':<10}")
        print("─" * 60)
        
        # v2 results store differential under 'differential_diagnosis'
        diffs = results.get('differential_diagnosis') or []
        # Fallback to older 'all_probabilities' if present
        if not diffs and 'all_probabilities' in results:
            diffs = [
                {
                    'disease': p.get('disease',''),
                    'probability': p.get('probability',0.0),
                    'icd_10': p.get('icd_10','N/A')
                }
                for p in results['all_probabilities']
            ]
        for i, prob in enumerate(diffs[:5], 1):
            p = float(prob.get('probability', 0.0))
            prob_bar = "▪" * int(p * 10)
            print(f"{i:<6} {prob.get('disease',''):<30} {p*100:>6.1f}% {prob_bar:<10} {prob.get('icd_10', 'N/A')}")
        
        # Symptom analysis
        print("\n" + "─" * 80)
        print("SYMPTOM ANALYSIS".center(80))
        print("─" * 80)
        
        analysis = results['symptoms_analysis']
        
        print(f"\n✓ Symptoms matching {primary['name']}:")
        if analysis['expected_symptoms_present']:
            for symptom in analysis['expected_symptoms_present'][:5]:
                print(f"  • {symptom['symptom']} - Present (typical in {symptom['typical_frequency']*100:.0f}% of cases)")
        
        if analysis['expected_symptoms_absent']:
            print(f"\n⚠ Common symptoms NOT present:")
            for symptom in analysis['expected_symptoms_absent'][:3]:
                print(f"  • {symptom['symptom']} - Absent (present in {symptom['typical_frequency']*100:.0f}% of cases)")
        
        if analysis['unexpected_symptoms']:
            print(f"\n❓ Symptoms not typical for {primary['name']}:")
            for symptom in analysis['unexpected_symptoms'][:3]:
                print(f"  • {symptom['symptom']}")
        
        # Recommendations
        print("\n" + "─" * 80)
        print("RECOMMENDATIONS".center(80))
        print("─" * 80)
        
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"\n{i}. {rec}")
        
        # Options
        print("\n" + "=" * 80)
        print("\nOPTIONS:")
        print("1. Save to patient history")
        print("2. Export to PDF")
        print("3. Both")
        print("4. Neither (return to menu)")
        
        return results
    
    def view_patient_history(self):
        """View patient history"""
        patients = self.history_manager.get_all_patients()
        
        if not patients:
            print("\nNo patient history found.")
            input("Press Enter to continue...")
            return
        
        print("\n" + "=" * 80)
        print("PATIENT HISTORY".center(80))
        print("=" * 80)
        
        print("\nSelect patient:")
        for i, patient in enumerate(patients, 1):
            print(f"{i}. {patient}")
        
        while True:
            try:
                idx = int(input(f"\nSelect patient (1-{len(patients)}): ")) - 1
                if 0 <= idx < len(patients):
                    patient_id = patients[idx]
                    break
            except ValueError:
                pass
            print("Invalid selection")
        
        # Get history
        history = self.history_manager.get_patient_history(patient_id)
        
        print(f"\n" + "─" * 80)
        print(f"History for patient: {patient_id}")
        print("─" * 80)
        
        for session in history:
            date = datetime.fromisoformat(session['timestamp'])
            print(f"\nSession Date: {date.strftime('%B %d, %Y %I:%M %p')}")
            
            for diag in session['diagnoses']:
                print(f"\n  Symptoms reported:")
                for symptom, severity in diag['symptoms_reported'].items():
                    print(f"    • {symptom}: {severity}/10")
                
                print(f"\n  Primary Diagnosis: {diag['primary_diagnosis']['name']}")
                print(f"  Confidence: {diag['primary_diagnosis']['confidence']*100:.1f}%")
                print(f"  ICD-10: {diag['primary_diagnosis']['icd_10']}")
        
        input("\nPress Enter to continue...")
    
    def generate_patient_report(self):
        """Generate comprehensive patient report"""
        patients = self.history_manager.get_all_patients()
        
        if not patients:
            print("\nNo patients found.")
            input("Press Enter to continue...")
            return
        
        print("\nSelect patient for report:")
        for i, patient in enumerate(patients, 1):
            print(f"{i}. {patient}")
        
        while True:
            try:
                idx = int(input(f"\nSelect patient (1-{len(patients)}): ")) - 1
                if 0 <= idx < len(patients):
                    patient_id = patients[idx]
                    break
            except ValueError:
                pass
            print("Invalid selection")
        
        report = self.history_manager.generate_patient_report(patient_id)
        
        if not report:
            print("No data found for patient.")
            return
        
        print("\n" + "=" * 80)
        print(f"PATIENT REPORT: {patient_id}".center(80))
        print("=" * 80)
        
        print(f"\nTotal visits: {report['total_sessions']}")
        print(f"First visit: {datetime.fromisoformat(report['first_visit']).strftime('%B %d, %Y')}")
        print(f"Last visit: {datetime.fromisoformat(report['last_visit']).strftime('%B %d, %Y')}")
        
        print("\nMost Common Diagnoses:")
        for disease, count in list(report['diagnosis_frequency'].items())[:5]:
            print(f"  • {disease}: {count} time(s)")
        
        print("\nMost Frequent Symptoms:")
        for symptom, data in list(report['common_symptoms'].items())[:5]:
            print(f"  • {symptom}: {data['count']} time(s), avg severity: {data['avg_severity']:.1f}/10")
        
        input("\nPress Enter to continue...")
    
    def view_recent_diagnoses(self):
        """View recent diagnoses across all patients"""
        recent = self.history_manager.get_recent_diagnoses(10)
        
        if not recent:
            print("\nNo recent diagnoses found.")
            input("Press Enter to continue...")
            return
        
        print("\n" + "=" * 80)
        print("RECENT DIAGNOSES".center(80))
        print("=" * 80)
        
        for diag in recent:
            date = datetime.fromisoformat(diag['timestamp'])
            print(f"\nDate: {date.strftime('%B %d, %Y %I:%M %p')}")
            print(f"Patient: {diag['patient_id']}")
            print(f"Diagnosis: {diag['primary_diagnosis']['name']} ({diag['primary_diagnosis']['confidence']*100:.1f}% confidence)")
            print(f"Symptoms: {', '.join(diag['symptoms_reported'].keys())}")
            print("─" * 60)
        
        input("\nPress Enter to continue...")
    
    def show_system_info(self):
        """Show system information"""
        print("\n" + "=" * 80)
        print("SYSTEM INFORMATION".center(80))
        print("=" * 80)
        
        print(f"\nTotal Diseases in Database: {len(DISEASES)}")
        print(f"Total Symptoms Tracked: {len(SYMPTOMS)}")
        print(f"Symptom Categories: {len(SYMPTOM_CATEGORIES)}")
        
        print("\nDiseases Available:")
        for i, (did, disease) in enumerate(DISEASES.items(), 1):
            print(f"  {i:2d}. {disease['name']} ({disease['icd_10']}) - {disease['category']}")
        
        print("\nFeatures:")
        print("  ✓ Neural Network with 15 diseases")
        print("  ✓ Symptom categorization by body system")
        print("  ✓ Patient history tracking")
        print("  ✓ PDF export capability")
        print("  ✓ ICD-10 medical coding")
        print("  ✓ Differential diagnosis")
        print("  ✓ Etymology insights")
        print("  ✓ Confidence scoring")
        
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main application loop"""
        # Load or train model
        try:
            print("Loading medical AI model...")
            self.network.load_model("models/enhanced_medical_model.json")
        except:
            print("Training new enhanced model... This may take a few minutes...")
            self.network.train(cases_per_disease=100, verbose=True)
            self.network.save_model("models/enhanced_medical_model.json")
        
        while True:
            choice = self.display_main_menu()
            
            if choice == '1':  # New Diagnosis
                # Get patient ID
                self.patient_id = self.get_patient_id()
                self.current_session = self.history_manager.create_session(self.patient_id)
                
                # Collect symptoms by category
                symptom_responses = self.conduct_diagnosis_by_category()
                
                if not symptom_responses:
                    print("\nNo symptoms reported.")
                    input("Press Enter to continue...")
                    continue
                
                # Get diagnosis
                results = self.network.diagnose_with_reasoning(symptom_responses)
                
                # Display results
                self.display_diagnosis_results(results, symptom_responses)
                
                # Handle save/export options
                option = input("\nSelect option (1-4): ").strip()
                
                if option in ['1', '3']:  # Save to history
                    self.history_manager.save_diagnosis(
                        self.current_session,
                        symptom_responses,
                        results
                    )
                    print("✓ Saved to patient history")
                
                if option in ['2', '3']:  # Export PDF
                    patient_info = {"patient_id": self.patient_id or "Anonymous"}
                    filepath = self.pdf_exporter.export_to_text(
                        patient_info,
                        symptom_responses,
                        results
                    )
                    print(f"✓ Exported to: {filepath}")
                
                input("\nPress Enter to continue...")
            
            elif choice == '2':  # View History
                self.view_patient_history()
            
            elif choice == '3':  # Generate Report
                self.generate_patient_report()
            
            elif choice == '4':  # Recent Diagnoses
                self.view_recent_diagnoses()
            
            elif choice == '5':  # System Info
                self.show_system_info()
            
            elif choice == '6':  # Exit
                print("\nThank you for using the Enhanced Medical Diagnosis System.")
                print("Remember: Always consult healthcare professionals for medical advice.")
                break

# Run the enhanced system
if __name__ == "__main__":
    system = EnhancedMedicalSystem()
    system.run()
