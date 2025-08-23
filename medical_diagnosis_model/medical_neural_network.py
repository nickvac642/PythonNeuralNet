"""
Enhanced Medical Diagnosis Neural Network
Built on the foundation of symptom-disease mappings with medical terminology
"""

from NeuralNet import initialize_network, train_network, forward_user_input, predict
from medical_symptom_schema import SYMPTOMS, get_symptom_by_name
from medical_disease_schema import DISEASES, get_differential_diagnosis
from medical_training_generator import MedicalDataGenerator
import time
import json

class MedicalDiagnosisNetwork:
    def __init__(self, hidden_neurons=10, learning_rate=0.3, epochs=10000):
        """Initialize the medical diagnosis neural network"""
        self.num_symptoms = 30
        self.num_features = 60  # 30 binary + 30 severity
        self.num_diseases = len(DISEASES)
        self.hidden_neurons = hidden_neurons
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.network = None
        self.generator = MedicalDataGenerator(self.num_symptoms)
        
    def train(self, cases_per_disease=100, verbose=True):
        """Train the network on generated medical data"""
        if verbose:
            print("Generating medical training data...")
        
        # Generate training dataset
        dataset = self.generator.generate_neural_network_format(cases_per_disease)
        
        if verbose:
            print(f"Generated {len(dataset)} training samples")
            print(f"Features: {self.num_features} (30 symptoms + 30 severities)")
            print(f"Classes: {self.num_diseases} diseases")
            print(f"\nInitializing network with {self.hidden_neurons} hidden neurons...")
        
        # Initialize network
        self.network = initialize_network(self.num_features, self.hidden_neurons, self.num_diseases)
        
        # Train network
        if verbose:
            print("\nTraining neural network...")
        
        start_time = time.time()
        error_history = train_network(self.network, dataset, self.learning_rate, self.epochs, self.num_diseases, verbose)
        training_time = time.time() - start_time
        
        if verbose:
            print(f"\nTraining completed in {training_time:.2f} seconds")
            print(f"Final error: {error_history[-1]:.4f}")
        
        return error_history
    
    def diagnose(self, symptoms_dict):
        """
        Diagnose based on symptom dictionary
        
        Args:
            symptoms_dict: Dict of {symptom_name: severity} where severity is 0-10
        
        Returns:
            diagnosis_results: Dict with predictions, probabilities, and recommendations
        """
        # Create feature vector
        symptom_vector = [0] * self.num_symptoms
        severity_vector = [0.0] * self.num_symptoms
        
        for symptom_name, severity in symptoms_dict.items():
            sid, symptom = get_symptom_by_name(symptom_name)
            if sid is not None and sid < self.num_symptoms:
                symptom_vector[sid] = 1
                severity_vector[sid] = severity / 10.0  # Normalize to 0-1
        
        # Combine features
        features = symptom_vector + severity_vector
        
        # Get neural network prediction
        nn_outputs = forward_user_input(self.network, features)
        predicted_disease_id = predict(nn_outputs)
        
        # Get traditional differential diagnosis for comparison
        present_symptoms = [i for i, v in enumerate(symptom_vector) if v == 1]
        differential = get_differential_diagnosis(present_symptoms)
        
        # Prepare results
        results = {
            "primary_diagnosis": {
                "disease_id": predicted_disease_id,
                "name": DISEASES[predicted_disease_id]['name'],
                "medical_name": DISEASES[predicted_disease_id]['medical_name'],
                "icd_10": DISEASES[predicted_disease_id]['icd_10'],
                "confidence": nn_outputs[predicted_disease_id],
                "description": DISEASES[predicted_disease_id]['description']
            },
            "all_probabilities": [],
            "differential_diagnosis": [],
            "symptoms_analysis": self._analyze_symptoms(symptom_vector, severity_vector, predicted_disease_id),
            "recommendations": self._get_recommendations(predicted_disease_id, nn_outputs[predicted_disease_id])
        }
        
        # Add all disease probabilities
        for did, disease in DISEASES.items():
            results["all_probabilities"].append({
                "disease": disease['name'],
                "probability": nn_outputs[did],
                "icd_10": disease['icd_10']
            })
        
        # Sort by probability
        results["all_probabilities"].sort(key=lambda x: x['probability'], reverse=True)
        
        # Add differential diagnosis from pattern matching
        for did, name, score in differential[:5]:
            results["differential_diagnosis"].append({
                "disease": name,
                "pattern_match_score": score
            })
        
        return results
    
    def _analyze_symptoms(self, symptom_vector, severity_vector, disease_id):
        """Analyze how symptoms relate to the diagnosis"""
        disease = DISEASES[disease_id]
        analysis = {
            "expected_symptoms_present": [],
            "expected_symptoms_absent": [],
            "unexpected_symptoms": [],
            "severity_assessment": []
        }
        
        # Check expected symptoms
        for symptom_id in disease['symptom_ids']:
            if symptom_id < self.num_symptoms:
                symptom = SYMPTOMS[symptom_id]
                pattern = disease['symptom_patterns'].get(symptom_id, {})
                
                if symptom_vector[symptom_id] == 1:
                    analysis["expected_symptoms_present"].append({
                        "symptom": symptom['name'],
                        "medical_term": symptom['medical_term'],
                        "typical_frequency": pattern.get('frequency', 0),
                        "severity": severity_vector[symptom_id]
                    })
                else:
                    if pattern.get('frequency', 0) > 0.7:  # High frequency symptom missing
                        analysis["expected_symptoms_absent"].append({
                            "symptom": symptom['name'],
                            "medical_term": symptom['medical_term'],
                            "typical_frequency": pattern.get('frequency', 0)
                        })
        
        # Check unexpected symptoms
        for sid, present in enumerate(symptom_vector):
            if present == 1 and sid not in disease['symptom_ids'] and sid < len(SYMPTOMS):
                symptom = SYMPTOMS[sid]
                analysis["unexpected_symptoms"].append({
                    "symptom": symptom['name'],
                    "medical_term": symptom['medical_term'],
                    "severity": severity_vector[sid]
                })
        
        # Severity assessment
        for item in analysis["expected_symptoms_present"]:
            sid, _ = get_symptom_by_name(item['symptom'])
            if sid is not None:
                pattern = disease['symptom_patterns'].get(sid, {})
                expected_range = pattern.get('severity_range', (0, 1))
                actual = item['severity']
                
                if actual < expected_range[0]:
                    assessment = "milder than typical"
                elif actual > expected_range[1]:
                    assessment = "more severe than typical"
                else:
                    assessment = "within typical range"
                
                analysis["severity_assessment"].append({
                    "symptom": item['symptom'],
                    "assessment": assessment
                })
        
        return analysis
    
    def _get_recommendations(self, disease_id, confidence):
        """Get recommendations based on diagnosis and confidence"""
        disease = DISEASES[disease_id]
        recommendations = []
        
        # Confidence-based recommendations
        if confidence > 0.8:
            recommendations.append("High confidence diagnosis - consider standard treatment protocols")
        elif confidence > 0.6:
            recommendations.append("Moderate confidence - consider additional testing to confirm")
        else:
            recommendations.append("Low confidence - comprehensive evaluation recommended")
        
        # Disease-specific recommendations
        if disease['category'] == "Infectious Disease":
            recommendations.append("Consider isolation precautions if contagious")
            recommendations.append("Monitor for complications")
        elif disease['category'] == "Chronic":
            recommendations.append("Develop long-term management plan")
            recommendations.append("Schedule regular follow-ups")
        
        # Duration-based recommendations
        if "days" in disease['typical_duration']:
            recommendations.append(f"Expected recovery: {disease['typical_duration']}")
        elif "Chronic" in disease['typical_duration']:
            recommendations.append("This is a chronic condition requiring ongoing management")
        
        # Differential diagnosis consideration
        if disease['differential_diagnosis']:
            recommendations.append(f"Rule out: {', '.join(disease['differential_diagnosis'][:3])}")
        
        # Etymology insight (for educational/research purposes)
        recommendations.append(f"Etymology insight: {disease['name']} derives from {disease['etymology']}")
        
        return recommendations
    
    def save_model(self, filename="medical_model.json"):
        """Save the trained model to a file"""
        if self.network is None:
            raise ValueError("No trained model to save")
        
        model_data = {
            "network": self.network,
            "config": {
                "num_symptoms": self.num_symptoms,
                "num_features": self.num_features,
                "num_diseases": self.num_diseases,
                "hidden_neurons": self.hidden_neurons
            },
            "training_params": {
                "learning_rate": self.learning_rate,
                "epochs": self.epochs
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(model_data, f, indent=2)
        
        print(f"Model saved to {filename}")
    
    def load_model(self, filename="medical_model.json"):
        """Load a trained model from a file"""
        with open(filename, 'r') as f:
            model_data = json.load(f)
        
        self.network = model_data["network"]
        config = model_data["config"]
        self.num_symptoms = config["num_symptoms"]
        self.num_features = config["num_features"]
        self.num_diseases = config["num_diseases"]
        self.hidden_neurons = config["hidden_neurons"]
        
        print(f"Model loaded from {filename}")

# Example usage
if __name__ == "__main__":
    print("Medical Diagnosis Neural Network")
    print("=" * 70)
    
    # Create and train the network
    med_network = MedicalDiagnosisNetwork(hidden_neurons=15, learning_rate=0.3, epochs=5000)
    med_network.train(cases_per_disease=50)
    
    # Test diagnosis
    print("\n" + "=" * 70)
    print("TEST DIAGNOSIS")
    print("=" * 70)
    
    # Example: Flu-like symptoms
    test_symptoms = {
        "Fever": 8,           # High fever
        "Fatigue": 7,         # Significant fatigue
        "Cough": 6,           # Moderate cough
        "Headache": 6,        # Moderate headache
        "Muscle Pain": 5,     # Some muscle pain
        "Sore Throat": 3      # Mild sore throat
    }
    
    print("\nPatient presents with:")
    for symptom, severity in test_symptoms.items():
        print(f"  • {symptom}: {severity}/10")
    
    # Get diagnosis
    results = med_network.diagnose(test_symptoms)
    
    print(f"\n{'='*70}")
    print("DIAGNOSIS RESULTS")
    print(f"{'='*70}")
    
    # Primary diagnosis
    primary = results['primary_diagnosis']
    print(f"\nPrimary Diagnosis: {primary['name']} ({primary['medical_name']})")
    print(f"ICD-10 Code: {primary['icd_10']}")
    print(f"Confidence: {primary['confidence']*100:.1f}%")
    print(f"Description: {primary['description']}")
    
    # Top 3 differential diagnoses
    print("\nDifferential Diagnosis (Neural Network):")
    for i, prob in enumerate(results['all_probabilities'][:3]):
        print(f"  {i+1}. {prob['disease']}: {prob['probability']*100:.1f}%")
    
    # Symptom analysis
    print("\nSymptom Analysis:")
    analysis = results['symptoms_analysis']
    print(f"  Expected symptoms present: {len(analysis['expected_symptoms_present'])}")
    print(f"  Key symptoms missing: {len(analysis['expected_symptoms_absent'])}")
    print(f"  Unexpected symptoms: {len(analysis['unexpected_symptoms'])}")
    
    # Recommendations
    print("\nRecommendations:")
    for rec in results['recommendations']:
        print(f"  • {rec}")
    
    # Save the model
    print("\n" + "=" * 70)
    med_network.save_model("trained_medical_model.json")
