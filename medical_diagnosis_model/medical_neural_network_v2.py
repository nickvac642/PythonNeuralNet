"""
Enhanced Medical Neural Network V2
Implements clinical reasoning, syndrome-level diagnosis, and medical decision rules
"""

from NeuralNet import initialize_network, train_network, forward_user_input, predict
from medical_symptom_schema import SYMPTOMS, get_symptom_by_name
from medical_disease_schema_v2 import (
    DISEASES_V2, CLINICAL_RULES, DIAGNOSTIC_CERTAINTY,
    get_syndrome_from_symptoms, get_appropriate_differential,
    requires_testing, get_syndrome_diagnosis, assess_severity
)
from medical_training_generator import MedicalDataGenerator
import time
import json
import random

class ClinicalReasoningNetwork:
    def __init__(self, hidden_neurons=20, learning_rate=0.3, epochs=10000):
        """Initialize the clinical reasoning neural network"""
        self.num_symptoms = 30
        self.num_features = 60  # 30 binary + 30 severity
        self.num_diseases = len(DISEASES_V2)
        self.hidden_neurons = hidden_neurons
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.network = None
        self.clinical_network = None  # Secondary network for syndrome classification
        
    def train(self, cases_per_disease=100, verbose=True):
        """Train both specific and syndrome-level networks"""
        if verbose:
            print("Training Clinical Reasoning Neural Network...")
            print("This includes syndrome-level and specific diagnosis capabilities")
        
        # Generate enhanced training data
        training_data = self._generate_clinical_training_data(cases_per_disease)
        
        if verbose:
            print(f"\nGenerated {len(training_data)} training samples")
            print(f"Features: {self.num_features}")
            print(f"Disease categories: {self.num_diseases}")
        
        # Train primary network
        self.network = initialize_network(self.num_features, self.hidden_neurons, self.num_diseases)
        
        start_time = time.time()
        error_history = train_network(
            self.network, training_data, 
            self.learning_rate, self.epochs, 
            self.num_diseases, verbose
        )
        training_time = time.time() - start_time
        
        if verbose:
            print(f"\nTraining completed in {training_time:.2f} seconds")
            print(f"Final error: {error_history[-1]:.4f}")
        
        return error_history
    
    def _generate_clinical_training_data(self, cases_per_disease):
        """Generate training data with clinical reasoning patterns"""
        training_data = []
        
        for disease_id, disease in DISEASES_V2.items():
            # Generate standard cases
            for _ in range(cases_per_disease):
                symptom_vec, severity_vec = self._generate_disease_case(disease_id)
                features = symptom_vec + severity_vec + [disease_id]
                training_data.append(features)
            
            # Generate atypical presentations (10% of cases)
            for _ in range(cases_per_disease // 10):
                symptom_vec, severity_vec = self._generate_atypical_case(disease_id)
                features = symptom_vec + severity_vec + [disease_id]
                training_data.append(features)
            
            # Generate early/mild presentations
            for _ in range(cases_per_disease // 10):
                symptom_vec, severity_vec = self._generate_mild_case(disease_id)
                features = symptom_vec + severity_vec + [disease_id]
                training_data.append(features)
        
        # Shuffle data
        import random
        random.shuffle(training_data)
        
        return training_data
    
    def _generate_disease_case(self, disease_id):
        """Generate typical disease presentation"""
        disease = DISEASES_V2[disease_id]
        symptom_vector = [0] * self.num_symptoms
        severity_vector = [0.0] * self.num_symptoms
        
        for symptom_id, pattern in disease['symptom_patterns'].items():
            if symptom_id >= self.num_symptoms:
                continue
            
            import random
            if random.random() < pattern['frequency']:
                symptom_vector[symptom_id] = 1
                min_sev, max_sev = pattern['severity_range']
                severity_vector[symptom_id] = random.uniform(min_sev, max_sev)
        
        return symptom_vector, severity_vector
    
    def _generate_atypical_case(self, disease_id):
        """Generate atypical presentation"""
        symptom_vec, severity_vec = self._generate_disease_case(disease_id)
        
        import random
        # Remove 1-2 common symptoms
        disease = DISEASES_V2[disease_id]
        common_symptoms = [sid for sid, p in disease['symptom_patterns'].items() 
                          if p['frequency'] > 0.7 and symptom_vec[sid] == 1]
        
        if common_symptoms:
            to_remove = random.choice(common_symptoms)
            symptom_vec[to_remove] = 0
            severity_vec[to_remove] = 0
        
        return symptom_vec, severity_vec
    
    def _generate_mild_case(self, disease_id):
        """Generate mild/early presentation"""
        symptom_vec, severity_vec = self._generate_disease_case(disease_id)
        
        # Reduce all severities by 30-50%
        import random
        reduction = random.uniform(0.3, 0.5)
        for i in range(len(severity_vec)):
            severity_vec[i] *= (1 - reduction)
        
        return symptom_vec, severity_vec
    
    def diagnose_with_reasoning(self, symptoms_dict, has_test_results=None):
        """
        Diagnose with clinical reasoning
        
        Args:
            symptoms_dict: {symptom_name: severity}
            has_test_results: {test_name: result} if available
        
        Returns:
            Comprehensive diagnosis with clinical reasoning
        """
        # Create feature vectors
        symptom_vector = [0] * self.num_symptoms
        severity_vector = [0.0] * self.num_symptoms
        symptom_ids = []
        
        for symptom_name, severity in symptoms_dict.items():
            sid, symptom = get_symptom_by_name(symptom_name)
            if sid is not None and sid < self.num_symptoms:
                symptom_vector[sid] = 1
                severity_vector[sid] = severity / 10.0
                symptom_ids.append(sid)
        
        # Determine syndrome
        syndrome = get_syndrome_from_symptoms(symptom_ids)
        
        # Get neural network predictions
        features = symptom_vector + severity_vector
        nn_outputs = forward_user_input(self.network, features)
        
        # Apply clinical reasoning
        adjusted_outputs = self._apply_clinical_rules(
            nn_outputs, symptom_ids, severity_vector, has_test_results
        )
        
        # Get primary diagnosis
        predicted_idx = predict(adjusted_outputs)
        primary_disease = DISEASES_V2[predicted_idx]
        
        # Check if diagnosis requires testing
        if requires_testing(primary_disease['name']) and not has_test_results:
            # Downgrade to syndrome level
            syndrome_name = get_syndrome_diagnosis(primary_disease['name'])
            # Find syndrome in diseases
            for did, disease in DISEASES_V2.items():
                if disease['name'] == syndrome_name:
                    predicted_idx = did
                    primary_disease = disease
                    break
        
        # Generate appropriate differential
        differential_names = get_appropriate_differential(syndrome)
        
        # Build results
        results = {
            "syndrome": syndrome,
            "severity_assessment": assess_severity(symptom_ids, severity_vector),
            "primary_diagnosis": {
                "disease_id": predicted_idx,
                "name": primary_disease['name'],
                "medical_name": primary_disease['medical_name'],
                "icd_10": primary_disease['icd_10'],
                "confidence": adjusted_outputs[predicted_idx],
                "diagnostic_certainty": primary_disease['diagnostic_certainty'],
                "description": primary_disease['description']
            },
            "clinical_reasoning": self._generate_clinical_reasoning(
                symptom_ids, severity_vector, primary_disease, syndrome
            ),
            "differential_diagnosis": self._generate_differential(
                adjusted_outputs, differential_names, syndrome
            ),
            "required_tests": primary_disease.get('required_tests', []),
            "supportive_tests": primary_disease.get('supportive_tests', []),
            "clinical_pearls": primary_disease.get('clinical_pearls', []),
            "red_flags": self._check_red_flags(symptom_ids, severity_vector, primary_disease),
            "recommendations": self._generate_recommendations(
                primary_disease, symptom_ids, severity_vector, has_test_results
            )
        }
        
        return results
    
    def _apply_clinical_rules(self, nn_outputs, symptom_ids, severity_vector, has_test_results):
        """Apply clinical decision rules to adjust probabilities"""
        adjusted = nn_outputs.copy()
        
        # Example: Apply Centor criteria for strep
        strep_idx = None
        for did, disease in DISEASES_V2.items():
            if disease['name'] == "Streptococcal Pharyngitis":
                strep_idx = did
                break
        
        if strep_idx is not None:
            centor_score = 0
            
            # Check Centor criteria
            if 0 in symptom_ids and severity_vector[0] > 0.3:  # Fever
                centor_score += 1
            if 3 not in symptom_ids:  # Absence of cough
                centor_score += 1
            if 6 in symptom_ids and severity_vector[6] > 0.5:  # Sore throat
                centor_score += 1
            
            # Adjust strep probability based on Centor score
            if centor_score <= 1:
                adjusted[strep_idx] *= 0.1  # Very unlikely
            elif centor_score == 2:
                adjusted[strep_idx] *= 0.5  # Possible
            else:
                adjusted[strep_idx] *= 1.5  # Likely
        
        # Normalize probabilities
        total = sum(adjusted)
        if total > 0:
            adjusted = [p/total for p in adjusted]
        
        return adjusted
    
    def _generate_clinical_reasoning(self, symptom_ids, severity_vector, primary_disease, syndrome):
        """Generate clinical reasoning explanation"""
        reasoning = {
            "syndrome_identified": syndrome,
            "key_findings": [],
            "supporting_features": [],
            "inconsistent_features": []
        }
        
        # Identify key findings
        disease_symptoms = primary_disease['symptom_patterns']
        
        for sid in symptom_ids:
            if sid in disease_symptoms:
                pattern = disease_symptoms[sid]
                if pattern['frequency'] > 0.7:
                    reasoning["key_findings"].append({
                        "symptom": SYMPTOMS[sid]['name'],
                        "significance": "Common in this condition",
                        "frequency": f"{pattern['frequency']*100:.0f}% of cases"
                    })
                else:
                    reasoning["supporting_features"].append({
                        "symptom": SYMPTOMS[sid]['name'],
                        "significance": "Sometimes seen",
                        "frequency": f"{pattern['frequency']*100:.0f}% of cases"
                    })
            else:
                reasoning["inconsistent_features"].append({
                    "symptom": SYMPTOMS[sid]['name'],
                    "significance": "Not typical for this diagnosis"
                })
        
        # Note important absent symptoms
        for sid, pattern in disease_symptoms.items():
            if pattern['frequency'] > 0.8 and sid not in symptom_ids and sid < len(SYMPTOMS):
                reasoning["inconsistent_features"].append({
                    "symptom": SYMPTOMS[sid]['name'] + " (absent)",
                    "significance": f"Expected in {pattern['frequency']*100:.0f}% of cases"
                })
        
        return reasoning
    
    def _generate_differential(self, outputs, appropriate_diseases, syndrome):
        """Generate medically appropriate differential diagnosis"""
        differential = []
        
        # Get disease indices for appropriate differential
        disease_indices = []
        for disease_name in appropriate_diseases:
            for did, disease in DISEASES_V2.items():
                if disease['name'] == disease_name:
                    disease_indices.append((did, outputs[did]))
                    break
        
        # Sort by probability
        disease_indices.sort(key=lambda x: x[1], reverse=True)
        
        # Build differential list
        for did, prob in disease_indices[:5]:  # Top 5
            disease = DISEASES_V2[did]
            differential.append({
                "disease": disease['name'],
                "probability": prob,
                "icd_10": disease['icd_10'],
                "diagnostic_certainty": disease['diagnostic_certainty'],
                "key_discriminating_features": self._get_discriminating_features(did)
            })
        
        return differential
    
    def _get_discriminating_features(self, disease_id):
        """Get key features that distinguish this disease"""
        disease = DISEASES_V2[disease_id]
        features = []
        
        # Find highly specific symptoms (high frequency, less common in others)
        for sid, pattern in disease['symptom_patterns'].items():
            if pattern['frequency'] > 0.7 and sid < len(SYMPTOMS):
                features.append(SYMPTOMS[sid]['name'])
        
        return features[:3]  # Top 3 discriminating features
    
    def _check_red_flags(self, symptom_ids, severity_vector, primary_disease):
        """Check for red flag symptoms"""
        red_flags = []
        
        # Disease-specific red flags
        if 'red_flags' in primary_disease:
            for flag in primary_disease['red_flags']:
                # Check if symptom is present
                for sid, symptom in SYMPTOMS.items():
                    if symptom['name'].lower() in flag.lower() and sid in symptom_ids:
                        red_flags.append(flag)
        
        # General red flags
        if 4 in symptom_ids and severity_vector[4] > 0.5:  # Dyspnea
            red_flags.append("Significant shortness of breath - requires evaluation")
        
        if 18 in symptom_ids and severity_vector[18] > 0.6:  # Chest pain
            red_flags.append("Chest pain - cardiac evaluation needed")
        
        if 14 in symptom_ids:  # Confusion
            red_flags.append("Altered mental status - urgent evaluation")
        
        return red_flags
    
    def _generate_recommendations(self, disease, symptom_ids, severity_vector, has_test_results):
        """Generate clinical recommendations"""
        recommendations = []
        
        # Diagnostic certainty-based recommendations
        certainty = disease['diagnostic_certainty']
        
        if certainty == "CONFIRMATORY" and not has_test_results:
            recommendations.append(f"Confirmatory testing recommended: {', '.join(disease['required_tests'])}")
        elif certainty == "PRESUMPTIVE":
            recommendations.append(f"Consider testing to confirm: {', '.join(disease['required_tests'])}")
        
        # Severity-based recommendations
        severity = assess_severity(symptom_ids, severity_vector)
        if "SEVERE" in severity:
            recommendations.append("Immediate medical evaluation recommended")
        elif "MODERATE" in severity:
            recommendations.append("Medical evaluation within 24-48 hours")
        else:
            recommendations.append("Monitor symptoms, seek care if worsening")
        
        # Disease-specific recommendations
        if disease['name'] == "Viral Upper Respiratory Infection":
            recommendations.extend([
                "Supportive care: rest, fluids, symptom management",
                "Antibiotics not indicated for viral illness",
                "Return if symptoms worsen or persist >10 days"
            ])
        elif disease['name'] == "Influenza-like Illness":
            recommendations.extend([
                "Consider influenza testing if within 48 hours of onset",
                "Antiviral therapy most effective if started early",
                "Monitor for secondary bacterial pneumonia"
            ])
        
        # Add clinical pearls
        if disease.get('clinical_pearls'):
            recommendations.append(f"Clinical note: {disease['clinical_pearls'][0]}")
        
        return recommendations
    
    def explain_diagnosis(self, results):
        """Provide detailed explanation of diagnosis"""
        explanation = []
        
        explanation.append(f"Based on your symptoms, you appear to have a {results['syndrome']} syndrome.")
        explanation.append(f"Severity assessment: {results['severity_assessment']}")
        
        reasoning = results['clinical_reasoning']
        if reasoning['key_findings']:
            explanation.append("\nKey findings supporting the diagnosis:")
            for finding in reasoning['key_findings'][:3]:
                explanation.append(f"- {finding['symptom']}: {finding['significance']}")
        
        if reasoning['inconsistent_features']:
            explanation.append("\nFeatures that are less typical:")
            for feature in reasoning['inconsistent_features'][:2]:
                explanation.append(f"- {feature['symptom']}: {feature['significance']}")
        
        primary = results['primary_diagnosis']
        if primary['diagnostic_certainty'] == "CONFIRMATORY":
            explanation.append(f"\nNote: {primary['name']} requires laboratory confirmation.")
            explanation.append("Without testing, this is a presumptive diagnosis.")
        
        return "\n".join(explanation)

# Example usage
if __name__ == "__main__":
    print("Clinical Reasoning Neural Network V2")
    print("=" * 70)
    
    # Initialize network
    clinical_net = ClinicalReasoningNetwork(hidden_neurons=25, learning_rate=0.3, epochs=5000)
    
    # Train network
    print("\nTraining clinical reasoning network...")
    clinical_net.train(cases_per_disease=50, verbose=True)
    
    # Test case: Flu-like symptoms
    print("\n" + "=" * 70)
    print("TEST CASE: Patient with flu-like symptoms")
    print("=" * 70)
    
    test_symptoms = {
        "Fever": 8,
        "Fatigue": 9,
        "Cough": 6,
        "Headache": 7,
        "Muscle Pain": 8,
        "Sore Throat": 3
    }
    
    print("\nSymptoms reported:")
    for symptom, severity in test_symptoms.items():
        print(f"  • {symptom}: {severity}/10")
    
    # Get diagnosis
    results = clinical_net.diagnose_with_reasoning(test_symptoms)
    
    # Display results
    print(f"\n{'='*70}")
    print("CLINICAL DIAGNOSIS")
    print(f"{'='*70}")
    
    primary = results['primary_diagnosis']
    print(f"\nPrimary Diagnosis: {primary['name']}")
    print(f"Medical Name: {primary['medical_name']}")
    print(f"ICD-10: {primary['icd_10']}")
    print(f"Diagnostic Certainty: {primary['diagnostic_certainty']}")
    print(f"Confidence: {primary['confidence']*100:.1f}%")
    
    print(f"\nClinical Reasoning:")
    print(clinical_net.explain_diagnosis(results))
    
    print(f"\nDifferential Diagnosis:")
    for i, diff in enumerate(results['differential_diagnosis'][:3], 1):
        print(f"{i}. {diff['disease']} ({diff['diagnostic_certainty']}): {diff['probability']*100:.1f}%")
    
    if results['red_flags']:
        print(f"\n⚠️  RED FLAGS:")
        for flag in results['red_flags']:
            print(f"  • {flag}")
    
    print(f"\nRecommendations:")
    for rec in results['recommendations'][:5]:
        print(f"  • {rec}")
