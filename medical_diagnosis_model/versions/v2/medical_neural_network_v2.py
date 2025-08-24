"""
Enhanced Medical Neural Network V2
Implements clinical reasoning, syndrome-level diagnosis, and medical decision rules
"""

try:
    # Prefer foundational implementation
    from foundational_brain.NeuralNet import initialize_network, predict
except Exception:
    # Fallback if PYTHONPATH not set
    from NeuralNet import initialize_network, predict
from medical_symptom_schema import SYMPTOMS, get_symptom_by_name
from .medical_disease_schema_v2 import (
    DISEASES_V2, CLINICAL_RULES, DIAGNOSTIC_CERTAINTY,
    get_syndrome_from_symptoms, get_appropriate_differential,
    requires_testing, get_syndrome_diagnosis, assess_severity
)
# Note: v2 generates its own synthetic training data; no dependency on v1 generator
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
        self.temperature = 1.0  # for probability calibration
        
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
        
        # Split into train/validation
        split = int(0.8 * len(training_data))
        train_set = training_data[:split]
        val_set = training_data[split:]

        # Initialize primary network
        self.network = initialize_network(self.num_features, self.hidden_neurons, self.num_diseases)

        start_time = time.time()
        history = self._train_softmax_cross_entropy(self.network, train_set, val_set, verbose=verbose)
        training_time = time.time() - start_time

        # Probability calibration (temperature scaling) on validation set
        self.temperature = self._calibrate_temperature(val_set)
        if verbose:
            print(f"\nCalibration: selected temperature T={self.temperature:.2f}")
            print(f"Training completed in {training_time:.2f} seconds")
        
        return history
    
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
                try:
                    sev_norm = float(severity) / 10.0
                except Exception:
                    sev_norm = 0.0
                # Treat zero (or negative) severity as absent
                if sev_norm > 0.0:
                    symptom_vector[sid] = 1
                    severity_vector[sid] = sev_norm
                    symptom_ids.append(sid)
        
        # Determine syndrome
        syndrome = get_syndrome_from_symptoms(symptom_ids)
        
        # Get neural network predictions (calibrated)
        features = symptom_vector + severity_vector
        nn_outputs = self._predict_proba(features)
        
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

    # ===== Optimization/Math helpers (softmax + cross-entropy) =====

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + (2.718281828459045 ** (-x)))

    def _softmax(self, logits):
        # Numerical stability: subtract max
        m = max(logits)
        exps = [pow(2.718281828459045, z - m) for z in logits]
        s = sum(exps)
        return [e / s for e in exps]

    def _cross_entropy(self, probs, expected_onehot):
        eps = 1e-12
        loss = 0.0
        for i in range(len(probs)):
            p = max(min(probs[i], 1.0 - eps), eps)
            loss += - expected_onehot[i] * (0 if p == 0 else (self._ln(p)))
        return loss

    def _ln(self, x: float) -> float:
        # Natural log via math if available; fallback to simple approximation
        import math
        return math.log(x)

    def _forward_logits_probs(self, network, inputs):
        # Forward through hidden (sigmoid)
        layer_inputs = inputs
        hidden_outputs = []
        for neuron in network[0]:
            # activation = w·x + b
            w = neuron['weights']
            activation = w[-1]
            for j in range(len(layer_inputs)):
                activation += w[j] * layer_inputs[j]
            out = self._sigmoid(activation)
            neuron['output'] = out
            hidden_outputs.append(out)

        # Output layer logits (linear)
        logits = []
        out_layer = network[1]
        for neuron in out_layer:
            w = neuron['weights']
            activation = w[-1]
            for j in range(len(hidden_outputs)):
                activation += w[j] * hidden_outputs[j]
            logits.append(activation)
        probs = self._softmax([z / self.temperature for z in logits])
        # store for potential reuse
        for idx, neuron in enumerate(out_layer):
            neuron['output'] = probs[idx]
        return hidden_outputs, logits, probs

    def _backward_softmax_ce(self, network, inputs, hidden_outputs, probs, expected_onehot):
        # Output layer delta: y_hat - y (for softmax + cross-entropy)
        output_layer = network[1]
        output_deltas = []
        for i in range(len(output_layer)):
            delta = probs[i] - expected_onehot[i]
            output_layer[i]['delta'] = delta
            output_deltas.append(delta)

        # Hidden layer deltas
        hidden_layer = network[0]
        hidden_deltas = []
        for j, neuron in enumerate(hidden_layer):
            error = 0.0
            for k, out_neuron in enumerate(output_layer):
                error += out_neuron['weights'][j] * output_deltas[k]
            # derivative of sigmoid using neuron['output'] already stored
            d = neuron['output'] * (1.0 - neuron['output'])
            neuron['delta'] = error * d
            hidden_deltas.append(neuron['delta'])

        # Update weights for output layer
        for i, neuron in enumerate(output_layer):
            for j in range(len(hidden_outputs)):
                neuron['weights'][j] += self.learning_rate * neuron['delta'] * hidden_outputs[j]
            neuron['weights'][-1] += self.learning_rate * neuron['delta']

        # Update weights for hidden layer
        for j, neuron in enumerate(hidden_layer):
            for k in range(len(inputs)):
                neuron['weights'][k] += self.learning_rate * neuron['delta'] * inputs[k]
            neuron['weights'][-1] += self.learning_rate * neuron['delta']

    def _train_softmax_cross_entropy(self, network, train_set, val_set, verbose=True):
        best_val_nll = float('inf')
        best_network = None
        patience = 20
        no_improve = 0
        history = []

        for epoch in range(self.epochs):
            # Shuffle
            random.shuffle(train_set)
            train_loss = 0.0
            train_correct = 0
            for row in train_set:
                features = row[:-1]
                label = int(row[-1])
                expected = [0] * self.num_diseases
                expected[label] = 1
                hidden_out, logits, probs = self._forward_logits_probs(network, features)
                # loss
                train_loss += self._cross_entropy(probs, expected)
                # accuracy
                pred = probs.index(max(probs))
                if pred == label:
                    train_correct += 1
                # backward/update
                self._backward_softmax_ce(network, features, hidden_out, probs, expected)

            # Validation
            val_loss, val_acc = self._evaluate(network, val_set)
            history.append({
                'epoch': epoch,
                'train_loss': train_loss / max(1, len(train_set)),
                'train_acc': train_correct / max(1, len(train_set)),
                'val_loss': val_loss,
                'val_acc': val_acc
            })

            if verbose and (epoch % 10 == 0 or epoch == self.epochs - 1):
                print(f"epoch={epoch:04d}  train_loss={history[-1]['train_loss']:.4f}  train_acc={history[-1]['train_acc']:.3f}  val_loss={val_loss:.4f}  val_acc={val_acc:.3f}")

            # Early stopping on validation loss
            if val_loss + 1e-6 < best_val_nll:
                best_val_nll = val_loss
                best_network = self._deepcopy_network(network)
                no_improve = 0
            else:
                no_improve += 1
                if no_improve >= patience:
                    if verbose:
                        print(f"Early stopping at epoch {epoch} (no val improvement for {patience} epochs)")
                    break

        if best_network is not None:
            self.network = best_network
        return history

    def _evaluate(self, network, dataset):
        if not dataset:
            return 0.0, 0.0
        total_nll = 0.0
        correct = 0
        for row in dataset:
            features = row[:-1]
            label = int(row[-1])
            _, logits, probs = self._forward_logits_probs(network, features)
            expected = [0] * self.num_diseases
            expected[label] = 1
            total_nll += self._cross_entropy(probs, expected)
            if probs.index(max(probs)) == label:
                correct += 1
        avg_nll = total_nll / len(dataset)
        acc = correct / len(dataset)
        return avg_nll, acc

    def _deepcopy_network(self, network):
        copied = []
        for layer in network:
            new_layer = []
            for neuron in layer:
                new_layer.append({'weights': list(neuron['weights'])})
            copied.append(new_layer)
        return copied

    def _calibrate_temperature(self, val_set):
        if not val_set:
            return 1.0
        candidates = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3.0]
        best_T = 1.0
        best_nll = float('inf')
        original_T = self.temperature
        for T in candidates:
            self.temperature = T
            nll, _ = self._evaluate(self.network, val_set)
            if nll < best_nll:
                best_nll = nll
                best_T = T
        self.temperature = best_T
        return best_T

    def _predict_proba(self, features):
        _, _, probs = self._forward_logits_probs(self.network, features)
        return probs

    # ===== Persistence =====

    def save_model(self, filename="models/enhanced_medical_model.json"):
        import json, os
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        model_data = {
            "config": {
                "num_symptoms": self.num_symptoms,
                "num_features": self.num_features,
                "num_diseases": self.num_diseases,
                "hidden_neurons": self.hidden_neurons,
                "learning_rate": self.learning_rate,
                "epochs": self.epochs,
                "temperature": self.temperature
            },
            "network": [
                [{"weights": n["weights"]} for n in self.network[0]],
                [{"weights": n["weights"]} for n in self.network[1]]
            ]
        }
        with open(filename, "w") as f:
            json.dump(model_data, f, indent=2)
        print(f"Model saved to {filename}")

    def load_model(self, filename="models/enhanced_medical_model.json"):
        import json
        with open(filename, "r") as f:
            model_data = json.load(f)
        cfg = model_data["config"]
        self.num_symptoms = cfg.get("num_symptoms", self.num_symptoms)
        self.num_features = cfg.get("num_features", self.num_features)
        self.num_diseases = cfg.get("num_diseases", self.num_diseases)
        self.hidden_neurons = cfg.get("hidden_neurons", self.hidden_neurons)
        self.learning_rate = cfg.get("learning_rate", self.learning_rate)
        self.epochs = cfg.get("epochs", self.epochs)
        self.temperature = cfg.get("temperature", 1.0)

        # Rebuild network structure
        self.network = []
        for layer in model_data["network"]:
            rebuilt = []
            for neuron in layer:
                rebuilt.append({"weights": list(neuron["weights"])})
            self.network.append(rebuilt)
        print(f"Model loaded from {filename}")
    
    # ===== Training from JSONL (v0.2) =====
    def train_from_jsonl(self, jsonl_path: str, seed: int = 42, verbose: bool = True):
        import random
        random.seed(seed)
        # Load data
        rows = []
        import json
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                rows.append(obj)
        # Build vectors
        dataset = []
        for obj in rows:
            sym = obj.get("symptoms", {})
            label_name = obj.get("label_name")
            # Map label to id
            label_id = None
            for did, d in DISEASES_V2.items():
                if d.get("name") == label_name:
                    label_id = did
                    break
            if label_id is None:
                continue
            symptom_vector = [0] * self.num_symptoms
            severity_vector = [0.0] * self.num_symptoms
            for name, sev in sym.items():
                sid, _ = get_symptom_by_name(name)
                if sid is None or sid >= self.num_symptoms:
                    continue
                try:
                    sevn = float(sev) / 10.0
                except Exception:
                    sevn = 0.0
                if sevn > 0.0:
                    symptom_vector[sid] = 1
                    severity_vector[sid] = sevn
            features = symptom_vector + severity_vector + [label_id]
            dataset.append(features)
        # Shuffle and split
        random.shuffle(dataset)
        split = int(0.8 * len(dataset))
        train_set = dataset[:split]
        val_set = dataset[split:]
        # Init and train
        self.network = initialize_network(self.num_features, self.hidden_neurons, self.num_diseases)
        history = self._train_softmax_cross_entropy(self.network, train_set, val_set, verbose=verbose)
        self.temperature = self._calibrate_temperature(val_set)
        if verbose:
            print(f"Calibration: selected T={self.temperature:.2f}")
        return history
    
    def _apply_clinical_rules(self, nn_outputs, symptom_ids, severity_vector, has_test_results):
        """Apply clinical decision rules to adjust probabilities"""
        adjusted = nn_outputs.copy()

        # Determine syndrome to guide appropriate weighting
        try:
            syndrome_ctx = get_syndrome_from_symptoms(symptom_ids)
            appropriate_names = set(get_appropriate_differential(syndrome_ctx))
        except Exception:
            syndrome_ctx = "Undifferentiated"
            appropriate_names = set()
        
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

        # Generic negative-evidence penalty: if highly expected symptoms are absent, downweight
        for did, disease in DISEASES_V2.items():
            patterns = disease.get('symptom_patterns', {})
            missing_high = 0
            for sid, pattern in patterns.items():
                freq = pattern.get('frequency', 0.0)
                if freq >= 0.85 and sid not in symptom_ids:
                    missing_high += 1
            if missing_high > 0:
                # Exponential penalty per missing key symptom
                adjusted[did] *= (0.6 ** missing_high)

        # Specific guard: UTI should not rank high without dysuria and frequency/urgency
        uti_idx = None
        for did, disease in DISEASES_V2.items():
            if disease['name'] == "Urinary Tract Infection":
                uti_idx = did
                break
        if uti_idx is not None:
            # 27: Dysuria, 26: Frequency/Urgency
            missing = int(26 not in symptom_ids) + int(27 not in symptom_ids)
            if missing == 2:
                # Very strong downweight when both GU keys absent
                adjusted[uti_idx] *= 0.03
            elif missing == 1:
                adjusted[uti_idx] *= 0.2

        # Soft-gate to diagnoses appropriate to inferred syndrome; allow general viral syndrome everywhere
        if appropriate_names:
            allowed = set(appropriate_names)
            allowed.add("Viral Syndrome")
            # Convert to log domain, apply additive biases, then re-softmax for stability
            eps = 1e-12
            logits = [self._ln(max(p, eps)) for p in adjusted]
            for did, disease in DISEASES_V2.items():
                if disease['name'] in allowed:
                    logits[did] += 2.5  # boost allowed
                else:
                    logits[did] -= 2.5  # penalize disallowed
            
            # Disease-specific discriminative boosts based on key features
            # Helper to find disease index by name
            def _idx(name: str):
                for _did, _dis in DISEASES_V2.items():
                    if _dis['name'] == name:
                        return _did
                return None
            
            uri_idx = _idx("Viral Upper Respiratory Infection")
            ili_idx = _idx("Influenza-like Illness")
            covid_idx = _idx("COVID-19-like Illness")
            pna_idx = _idx("Pneumonia Syndrome")
            
            # Symptom severities for readability
            fever = severity_vector[0] if len(severity_vector) > 0 else 0
            fatigue = severity_vector[1] if len(severity_vector) > 1 else 0
            cough = severity_vector[3] if len(severity_vector) > 3 else 0
            dyspnea = severity_vector[4] if len(severity_vector) > 4 else 0
            sore_throat = severity_vector[6] if len(severity_vector) > 6 else 0
            rhinorrhea = severity_vector[7] if len(severity_vector) > 7 else 0
            congestion = severity_vector[8] if len(severity_vector) > 8 else 0
            nausea = severity_vector[9] if len(severity_vector) > 9 else 0
            myalgia = severity_vector[16] if len(severity_vector) > 16 else 0
            chest_pain = severity_vector[18] if len(severity_vector) > 18 else 0
            anosmia = severity_vector[28] if len(severity_vector) > 28 else 0
            
            # URI: rhinorrhea + congestion + cough, not very high fever, limited myalgia
            if uri_idx is not None:
                if rhinorrhea > 0.3 and congestion > 0.3 and cough > 0.2:
                    logits[uri_idx] += 1.5
                if fever < 0.6 and myalgia < 0.6:
                    logits[uri_idx] += 0.5
                # Negative evidence: GU keys absent with strong URI pattern present
                if uti_idx is not None and (rhinorrhea > 0.3 or congestion > 0.3) and (26 not in symptom_ids) and (27 not in symptom_ids):
                    logits[uti_idx] -= 6.0
            
            # ILI: high fever + myalgia (+/- severe fatigue)
            if ili_idx is not None:
                if fever >= 0.6 and myalgia >= 0.6:
                    logits[ili_idx] += 2.5
                if fatigue >= 0.7:
                    logits[ili_idx] += 0.5
            
            # COVID-like: anosmia highly specific; GI + cough supportive; dyspnea moderate
            if covid_idx is not None:
                if anosmia >= 0.8:
                    logits[covid_idx] += 2.5
                if nausea >= 0.3 and cough > 0.2:
                    logits[covid_idx] += 0.5
                if dyspnea >= 0.4:
                    logits[covid_idx] += 0.3
            
            # Pneumonia: dyspnea + chest pain + strong cough
            if pna_idx is not None:
                if dyspnea >= 0.5 and chest_pain >= 0.4 and cough >= 0.5:
                    logits[pna_idx] += 2.0
            # Stronger UTI penalty if urinary keys absent; zero out if syndrome is respiratory
            if uti_idx is not None and (26 not in symptom_ids) and (27 not in symptom_ids):
                if syndrome_ctx and ("Respiratory" in syndrome_ctx or syndrome_ctx == "Undifferentiated"):
                    logits[uti_idx] -= 12.0
                else:
                    logits[uti_idx] -= 8.0
            # Recompute probabilities via softmax
            m = max(logits)
            exps = [pow(2.718281828459045, z - m) for z in logits]
            s = sum(exps)
            adjusted = [e / s for e in exps]
        
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
