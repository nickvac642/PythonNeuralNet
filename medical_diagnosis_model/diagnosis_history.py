"""
Diagnosis History Management
Saves and retrieves patient diagnosis history
"""

import json
import os
from datetime import datetime
from pathlib import Path

class DiagnosisHistory:
    def __init__(self, history_dir="diagnosis_history"):
        """Initialize diagnosis history manager"""
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(exist_ok=True)
        self.current_session_file = None
        
    def create_session(self, patient_id=None):
        """Create a new diagnosis session"""
        timestamp = datetime.now()
        
        if patient_id is None:
            patient_id = f"patient_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            "patient_id": patient_id,
            "session_id": timestamp.strftime('%Y%m%d_%H%M%S'),
            "timestamp": timestamp.isoformat(),
            "diagnoses": []
        }
        
        filename = f"{patient_id}_{session['session_id']}.json"
        self.current_session_file = self.history_dir / filename
        
        return session
    
    def save_diagnosis(self, session, symptom_data, diagnosis_results):
        """Save a diagnosis to the current session"""
        diagnosis_entry = {
            "timestamp": datetime.now().isoformat(),
            "symptoms_reported": symptom_data,
            "primary_diagnosis": {
                "name": diagnosis_results['primary_diagnosis']['name'],
                "medical_name": diagnosis_results['primary_diagnosis']['medical_name'],
                "icd_10": diagnosis_results['primary_diagnosis']['icd_10'],
                "confidence": diagnosis_results['primary_diagnosis']['confidence']
            },
            "differential_diagnosis": diagnosis_results['all_probabilities'][:5],
            "symptom_analysis": {
                "expected_present": len(diagnosis_results['symptoms_analysis']['expected_symptoms_present']),
                "expected_absent": len(diagnosis_results['symptoms_analysis']['expected_symptoms_absent']),
                "unexpected": len(diagnosis_results['symptoms_analysis']['unexpected_symptoms'])
            },
            "recommendations": diagnosis_results['recommendations'][:3]
        }
        
        session['diagnoses'].append(diagnosis_entry)
        
        # Save to file
        if self.current_session_file:
            with open(self.current_session_file, 'w') as f:
                json.dump(session, f, indent=2)
        
        return diagnosis_entry
    
    def get_patient_history(self, patient_id):
        """Retrieve all diagnosis history for a patient"""
        history = []
        
        for file in self.history_dir.glob(f"{patient_id}_*.json"):
            with open(file, 'r') as f:
                session_data = json.load(f)
                history.append(session_data)
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        
        return history
    
    def get_all_patients(self):
        """Get list of all patients with history"""
        patients = set()
        
        for file in self.history_dir.glob("*.json"):
            with open(file, 'r') as f:
                session_data = json.load(f)
                patients.add(session_data['patient_id'])
        
        return sorted(list(patients))
    
    def get_recent_diagnoses(self, limit=10):
        """Get most recent diagnoses across all patients"""
        all_diagnoses = []
        
        for file in self.history_dir.glob("*.json"):
            with open(file, 'r') as f:
                session_data = json.load(f)
                for diagnosis in session_data['diagnoses']:
                    diagnosis['patient_id'] = session_data['patient_id']
                    all_diagnoses.append(diagnosis)
        
        # Sort by timestamp
        all_diagnoses.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return all_diagnoses[:limit]
    
    def generate_patient_report(self, patient_id):
        """Generate a summary report for a patient"""
        history = self.get_patient_history(patient_id)
        
        if not history:
            return None
        
        report = {
            "patient_id": patient_id,
            "total_sessions": len(history),
            "first_visit": history[0]['timestamp'],
            "last_visit": history[-1]['timestamp'],
            "diagnosis_frequency": {},
            "common_symptoms": {},
            "sessions": []
        }
        
        # Analyze all diagnoses
        for session in history:
            session_summary = {
                "date": session['timestamp'],
                "diagnoses_count": len(session['diagnoses']),
                "primary_diagnoses": []
            }
            
            for diagnosis in session['diagnoses']:
                # Track diagnosis frequency
                diag_name = diagnosis['primary_diagnosis']['name']
                report['diagnosis_frequency'][diag_name] = report['diagnosis_frequency'].get(diag_name, 0) + 1
                
                session_summary['primary_diagnoses'].append({
                    "name": diag_name,
                    "confidence": diagnosis['primary_diagnosis']['confidence']
                })
                
                # Track symptom frequency
                for symptom, severity in diagnosis['symptoms_reported'].items():
                    if symptom not in report['common_symptoms']:
                        report['common_symptoms'][symptom] = {
                            "count": 0,
                            "avg_severity": 0,
                            "severities": []
                        }
                    report['common_symptoms'][symptom]['count'] += 1
                    report['common_symptoms'][symptom]['severities'].append(severity)
            
            report['sessions'].append(session_summary)
        
        # Calculate average severities
        for symptom, data in report['common_symptoms'].items():
            if data['severities']:
                data['avg_severity'] = sum(data['severities']) / len(data['severities'])
                del data['severities']  # Remove raw data
        
        # Sort by frequency
        report['diagnosis_frequency'] = dict(sorted(
            report['diagnosis_frequency'].items(), 
            key=lambda x: x[1], 
            reverse=True
        ))
        
        report['common_symptoms'] = dict(sorted(
            report['common_symptoms'].items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        ))
        
        return report
    
    def export_session_summary(self, session):
        """Export session summary as formatted text"""
        summary = []
        summary.append("=" * 70)
        summary.append(f"DIAGNOSIS SESSION SUMMARY")
        summary.append(f"Patient ID: {session['patient_id']}")
        summary.append(f"Session Date: {datetime.fromisoformat(session['timestamp']).strftime('%B %d, %Y %I:%M %p')}")
        summary.append("=" * 70)
        
        for i, diagnosis in enumerate(session['diagnoses'], 1):
            summary.append(f"\nDiagnosis #{i}")
            summary.append("-" * 40)
            
            # Symptoms
            summary.append("\nSymptoms Reported:")
            for symptom, severity in diagnosis['symptoms_reported'].items():
                summary.append(f"  • {symptom}: {severity}/10")
            
            # Primary diagnosis
            primary = diagnosis['primary_diagnosis']
            summary.append(f"\nPrimary Diagnosis: {primary['name']} ({primary['medical_name']})")
            summary.append(f"ICD-10 Code: {primary['icd_10']}")
            summary.append(f"Confidence: {primary['confidence']*100:.1f}%")
            
            # Differential
            summary.append("\nDifferential Diagnosis:")
            for j, diff in enumerate(diagnosis['differential_diagnosis'][:3], 1):
                summary.append(f"  {j}. {diff['disease']}: {diff['probability']*100:.1f}%")
            
            # Recommendations
            summary.append("\nRecommendations:")
            for rec in diagnosis['recommendations']:
                summary.append(f"  • {rec}")
        
        summary.append("\n" + "=" * 70)
        
        return "\n".join(summary)

# Example usage
if __name__ == "__main__":
    history_manager = DiagnosisHistory()
    
    # Create a test session
    session = history_manager.create_session("test_patient_001")
    
    # Simulate a diagnosis
    test_symptoms = {"Fever": 7, "Cough": 5, "Fatigue": 8}
    test_results = {
        "primary_diagnosis": {
            "name": "Influenza",
            "medical_name": "Influenza",
            "icd_10": "J11",
            "confidence": 0.85
        },
        "all_probabilities": [
            {"disease": "Influenza", "probability": 0.85},
            {"disease": "COVID-19", "probability": 0.10},
            {"disease": "Common Cold", "probability": 0.05}
        ],
        "symptoms_analysis": {
            "expected_symptoms_present": ["Fever", "Cough", "Fatigue"],
            "expected_symptoms_absent": [],
            "unexpected_symptoms": []
        },
        "recommendations": [
            "Rest and fluids",
            "See doctor if symptoms worsen",
            "Consider flu test"
        ]
    }
    
    # Save diagnosis
    history_manager.save_diagnosis(session, test_symptoms, test_results)
    
    # Print summary
    print(history_manager.export_session_summary(session))
    
    # Get patient report
    report = history_manager.generate_patient_report("test_patient_001")
    if report:
        print(f"\nPatient Report Summary:")
        print(f"Total visits: {report['total_sessions']}")
        print(f"Most common diagnosis: {list(report['diagnosis_frequency'].keys())[0] if report['diagnosis_frequency'] else 'None'}")
