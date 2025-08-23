"""
Medical Training Data Generator
Generates neural network training data from symptom-disease mappings
"""

import random
from medical_symptom_schema import SYMPTOMS, interpret_severity
from medical_disease_schema import DISEASES, calculate_symptom_match_score

class MedicalDataGenerator:
    def __init__(self, num_symptoms=30, seed=None):
        """Initialize the medical data generator"""
        self.num_symptoms = num_symptoms
        self.num_diseases = len(DISEASES)
        if seed:
            random.seed(seed)
    
    def generate_patient_case(self, disease_id, variation=0.2):
        """
        Generate a patient case for a specific disease
        
        Args:
            disease_id: The disease to generate symptoms for
            variation: How much to vary from typical patterns (0-1)
        
        Returns:
            symptom_vector: Binary vector of symptom presence
            severity_vector: Normalized severity values (0-1)
            disease_label: The disease ID
        """
        disease = DISEASES[disease_id]
        symptom_vector = [0] * self.num_symptoms
        severity_vector = [0.0] * self.num_symptoms
        
        # Add expected symptoms based on frequency
        for symptom_id, pattern in disease['symptom_patterns'].items():
            if symptom_id >= self.num_symptoms:
                continue
                
            frequency = pattern['frequency']
            severity_range = pattern['severity_range']
            
            # Randomly decide if symptom is present based on frequency
            if random.random() < frequency:
                symptom_vector[symptom_id] = 1
                
                # Generate severity within the expected range
                min_sev, max_sev = severity_range
                severity = random.uniform(min_sev, max_sev)
                
                # Add variation
                severity += random.uniform(-variation, variation)
                severity = max(0, min(1, severity))  # Clamp to 0-1
                
                severity_vector[symptom_id] = severity
        
        # Occasionally add random symptoms (noise)
        if random.random() < variation:
            num_random = random.randint(1, 3)
            for _ in range(num_random):
                symptom_id = random.randint(0, self.num_symptoms - 1)
                if symptom_vector[symptom_id] == 0:  # Don't override existing
                    symptom_vector[symptom_id] = 1
                    severity_vector[symptom_id] = random.uniform(0.1, 0.3)  # Low severity
        
        return symptom_vector, severity_vector, disease_id
    
    def generate_mixed_case(self, disease_ids, weights=None):
        """
        Generate a case with multiple conditions (comorbidities)
        
        Args:
            disease_ids: List of disease IDs that are present
            weights: Weight for each disease (default equal)
        
        Returns:
            Combined symptom and severity vectors
        """
        if weights is None:
            weights = [1.0 / len(disease_ids)] * len(disease_ids)
        
        symptom_vector = [0] * self.num_symptoms
        severity_vector = [0.0] * self.num_symptoms
        
        for disease_id, weight in zip(disease_ids, weights):
            disease = DISEASES[disease_id]
            
            for symptom_id, pattern in disease['symptom_patterns'].items():
                if symptom_id >= self.num_symptoms:
                    continue
                
                frequency = pattern['frequency'] * weight
                severity_range = pattern['severity_range']
                
                if random.random() < frequency:
                    symptom_vector[symptom_id] = 1
                    
                    # Combine severities (take maximum)
                    min_sev, max_sev = severity_range
                    severity = random.uniform(min_sev, max_sev) * weight
                    severity_vector[symptom_id] = max(severity_vector[symptom_id], severity)
        
        # Primary diagnosis is the one with highest weight
        primary_disease = disease_ids[weights.index(max(weights))]
        
        return symptom_vector, severity_vector, primary_disease
    
    def generate_training_dataset(self, cases_per_disease=100, include_mixed=True):
        """
        Generate a complete training dataset
        
        Args:
            cases_per_disease: Number of cases to generate per disease
            include_mixed: Whether to include comorbidity cases
        
        Returns:
            training_data: List of (features, label) tuples
        """
        training_data = []
        
        # Generate pure disease cases
        for disease_id in DISEASES.keys():
            for _ in range(cases_per_disease):
                symptom_vec, severity_vec, label = self.generate_patient_case(disease_id)
                
                # Combine binary and severity for richer features
                features = symptom_vec + severity_vec
                training_data.append((features, label))
        
        # Generate mixed cases (comorbidities)
        if include_mixed:
            num_mixed = cases_per_disease * len(DISEASES) // 4  # 25% mixed cases
            
            for _ in range(num_mixed):
                # Randomly select 2-3 diseases
                num_diseases = random.randint(2, 3)
                disease_ids = random.sample(list(DISEASES.keys()), num_diseases)
                
                # Generate weights (primary disease gets higher weight)
                weights = [random.uniform(0.3, 0.7) for _ in range(num_diseases)]
                weights[0] = random.uniform(0.6, 0.9)  # Primary disease
                weights = [w / sum(weights) for w in weights]  # Normalize
                
                symptom_vec, severity_vec, label = self.generate_mixed_case(disease_ids, weights)
                features = symptom_vec + severity_vec
                training_data.append((features, label))
        
        # Shuffle the dataset
        random.shuffle(training_data)
        
        return training_data
    
    def generate_neural_network_format(self, cases_per_disease=100):
        """
        Generate data in the format expected by the neural network
        
        Returns:
            dataset: List where each row is features + [label]
        """
        training_data = self.generate_training_dataset(cases_per_disease)
        
        # Convert to neural network format
        dataset = []
        for features, label in training_data:
            row = features + [label]
            dataset.append(row)
        
        return dataset
    
    def generate_readable_case(self, disease_id=None):
        """Generate a human-readable patient case for testing"""
        if disease_id is None:
            disease_id = random.choice(list(DISEASES.keys()))
        
        symptom_vec, severity_vec, _ = self.generate_patient_case(disease_id)
        disease = DISEASES[disease_id]
        
        print(f"\nPatient Case - {disease['name']} ({disease['medical_name']})")
        print("=" * 60)
        print("Presenting Symptoms:")
        
        for i, (present, severity) in enumerate(zip(symptom_vec, severity_vec)):
            if present and i < len(SYMPTOMS):
                symptom = SYMPTOMS[i]
                severity_desc = self._get_severity_description(severity)
                print(f"  • {symptom['name']} ({symptom['medical_term']}): {severity_desc}")
        
        print(f"\nICD-10 Code: {disease['icd_10']}")
        print(f"Category: {disease['category']}")
        print(f"Typical Duration: {disease['typical_duration']}")
        print(f"\nDifferential Diagnosis: {', '.join(disease['differential_diagnosis'])}")
    
    def _get_severity_description(self, severity):
        """Convert severity value to human-readable description"""
        if severity < 0.2:
            return "Mild"
        elif severity < 0.4:
            return "Mild-Moderate"
        elif severity < 0.6:
            return "Moderate"
        elif severity < 0.8:
            return "Moderate-Severe"
        else:
            return "Severe"

# Example usage and testing
if __name__ == "__main__":
    generator = MedicalDataGenerator(seed=42)
    
    print("Medical Training Data Generator")
    print("=" * 60)
    
    # Generate a sample case for each disease
    print("\nSample Patient Cases:")
    for disease_id in list(DISEASES.keys())[:3]:  # Show first 3
        generator.generate_readable_case(disease_id)
    
    # Generate training dataset
    print("\n\nGenerating Training Dataset...")
    dataset = generator.generate_neural_network_format(cases_per_disease=50)
    
    print(f"Total training samples: {len(dataset)}")
    print(f"Features per sample: {len(dataset[0]) - 1}")
    print(f"Number of classes: {len(DISEASES)}")
    
    # Show data distribution
    print("\nClass Distribution:")
    class_counts = {}
    for row in dataset:
        label = row[-1]
        class_counts[label] = class_counts.get(label, 0) + 1
    
    for disease_id, count in sorted(class_counts.items()):
        disease_name = DISEASES[disease_id]['name']
        print(f"  {disease_name}: {count} samples")
    
    # Save sample dataset
    print("\nSaving sample dataset to 'medical_training_data.txt'...")
    with open('medical_training_data.txt', 'w') as f:
        f.write(f"# Medical Training Dataset\n")
        f.write(f"# Features: {len(dataset[0]) - 1} (30 binary symptoms + 30 severity values)\n")
        f.write(f"# Classes: {len(DISEASES)}\n")
        f.write(f"# Total samples: {len(dataset)}\n\n")
        
        # Save first 10 samples as example
        for i, row in enumerate(dataset[:10]):
            f.write(f"Sample {i}: {row}\n")
