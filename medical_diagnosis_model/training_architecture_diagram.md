# Medical Neural Network Training Architecture

This diagram shows the complete training process for the enhanced medical diagnosis system.

```mermaid
graph TB
    subgraph "1. Data Generation Layer"
        A[Medical Knowledge Base] --> B[Disease Definitions<br/>DISEASES_V2]
        C[Symptom Schema<br/>30 symptoms] --> B
        B --> D[Training Data Generator]
        D --> E[Clinical Cases<br/>Typical/Atypical/Mild]
    end

    subgraph "2. Clinical Reasoning Layer"
        E --> F[Syndrome Detection]
        F --> G[Clinical Rules<br/>Centor, CURB-65]
        G --> H[Diagnostic Certainty<br/>Clinical/Presumptive/Confirmatory]
    end

    subgraph "3. Neural Network Layer"
        H --> I[Input Layer<br/>60 neurons<br/>30 symptoms + 30 severities]
        I --> J[Hidden Layer<br/>20-25 neurons<br/>Pattern detection]
        J --> K[Output Layer<br/>11 neurons<br/>Disease probabilities]
    end

    subgraph "4. Training Process"
        K --> L[Forward Propagation<br/>Calculate predictions]
        L --> M[Error Calculation<br/>Expected vs Actual]
        M --> N[Backpropagation<br/>Calculate gradients]
        N --> O[Weight Updates<br/>Gradient descent]
        O --> L
    end

    style A fill:#e1f5fe
    style B fill:#e1f5fe
    style C fill:#e1f5fe
    style F fill:#fff3e0
    style G fill:#fff3e0
    style H fill:#fff3e0
    style I fill:#f3e5f5
    style J fill:#f3e5f5
    style K fill:#f3e5f5
    style L fill:#e8f5e9
    style M fill:#e8f5e9
    style N fill:#e8f5e9
    style O fill:#e8f5e9
```

## Layer Descriptions

### 1. Data Generation Layer

- **Medical Knowledge Base**: Contains symptom definitions, disease patterns, and medical relationships
- **Disease Definitions (DISEASES_V2)**: 11 diseases with syndrome-level and specific diagnoses
- **Training Data Generator**: Creates realistic patient cases with typical (80%), atypical (10%), and mild (10%) presentations

### 2. Clinical Reasoning Layer

- **Syndrome Detection**: Groups symptoms into clinical syndromes (Respiratory Febrile, GI, etc.)
- **Clinical Rules**: Applies medical decision rules like Centor criteria for strep throat
- **Diagnostic Certainty**: Determines if diagnosis needs confirmatory testing

### 3. Neural Network Layer

- **Input Layer**: 60 features (30 binary symptom flags + 30 severity values)
- **Hidden Layer**: 20-25 neurons that learn medical patterns
- **Output Layer**: 11 neurons representing disease probabilities

### 4. Training Process

- **Forward Propagation**: Calculates predictions using current weights
- **Error Calculation**: Compares predictions to expected diagnosis (considers clinical rules)
- **Backpropagation**: Calculates how to adjust weights to reduce error
- **Weight Updates**: Applies gradient descent to improve predictions

## Key Innovations

1. **Syndrome-First Approach**: Diagnoses "Viral URI" instead of jumping to "Influenza"
2. **Test Requirements**: Knows when laboratory confirmation is needed
3. **Clinical Rules Integration**: Applies medical decision-making during training
4. **Realistic Data**: Generates medically accurate training cases

This architecture allows the network to think like a doctor, starting broad and narrowing down only when appropriate.
