# Behind the Scenes: How the Foundation Network Learns

This note explains the math and intuition behind the core neural network used across models in this repo. It’s a friendly refresher: symbol guide → big picture → exact equations.

---

## Symbols and notation (quick reference)

- Vectors / matrices
  - x ∈ R^d: input column vector (features)
  - W ∈ R^{m×n}: weight matrix mapping R^n → R^m
  - b ∈ R^m: bias vector
  - (·)^T: transpose
- Layer sizes
  - d: input dimension (e.g., 60 for 30 presence + 30 severity)
  - H: hidden units
  - C: number of classes
- Activations
  - Sigmoid: σ(t) = 1/(1+e^(−t)), with σ'(t) = σ(t)(1−σ(t))
  - Softmax: softmax_k(u) = e^{u_k} / Σ_j e^{u_j}
- Targets and predictions
  - One‑hot label y ∈ {0,1}^C
  - Predicted probs ŷ ∈ [0,1]^C with Σ_k ŷ_k = 1
- Loss
  - Cross‑entropy: L(y, ŷ) = −Σ_k y_k log(ŷ_k)
- Element‑wise product
  - u ⊙ v: multiply entries position‑wise

---

## High‑level intuition

1. Each training step has two halves: predict (forward pass) and learn (backprop + weight update).
2. Prediction is a sequence of linear maps (weighted sums) with non‑linear squashes that turn inputs into class scores and then probabilities.
3. Learning moves weights in the direction that reduces cross‑entropy; over many examples, the network discovers patterns that separate classes.

---

## Data interface (model‑agnostic)

- A training row is [x, label].
- In our projects, x often stacks presence flags (0/1) and severities ([0,1]); label is an integer class id converted to a one‑hot y.

---

## Forward pass (one hidden layer)

Given x ∈ R^d:

1. Hidden pre‑activation

- z1 = W1 x + b1 (W1 ∈ R^{H×d}, b1 ∈ R^H)

2. Hidden activation (sigmoid)

- a1 = σ(z1) ∈ (0,1)^H

3. Output logits and probabilities

- z2 = W2 a1 + b2 (W2 ∈ R^{C×H}, b2 ∈ R^C)
- ŷ = softmax(z2 / T) ∈ [0,1]^C

Temperature T:

- During training we typically use T = 1.
- After training we may pick a calibrated T* on the validation set (probability calibration) and use softmax(z2/T*) at inference.

---

## Loss (what we minimize)

Cross‑entropy (negative log‑likelihood) between y (one‑hot) and ŷ:

- L(y, ŷ) = − Σ_k y_k log(ŷ_k)
- Because y is one‑hot, L = −log(ŷ_true).

Why cross‑entropy?

- It directly rewards assigning high probability to the true class.
- Paired with softmax, it yields especially simple gradients (below).

(Mean Squared Error is OK for toy demos, but softmax + cross‑entropy is the standard for classification.)

---

## Gradients (how learning signals flow)

Key simplification with softmax + cross‑entropy:

- δ2 = ŷ − y ∈ R^C (output‑layer error signal)

Output‑layer gradients:

- ∂L/∂W2 = δ2 a1^T
- ∂L/∂b2 = δ2

Backpropagate to hidden:

- δ1 = (W2^T δ2) ⊙ σ'(z1) = (W2^T δ2) ⊙ a1 ⊙ (1 − a1)

Hidden‑layer gradients:

- ∂L/∂W1 = δ1 x^T
- ∂L/∂b1 = δ1

---

## Parameter update (gradient descent)

For learning rate η > 0:

- W ← W − η ∂L/∂W
- b ← b − η ∂L/∂b

Repeat over many examples/epochs.

---

## Validation, early stopping, calibration

- Validation split (~20%) to monitor generalization.
- Early stopping: keep best weights (lowest val loss); stop when no improvement.
- Temperature scaling: search a small set of T values that minimize validation NLL; use T\* at inference for calibrated confidence.

---

## Why presence + severity helps

With x = [p; s] (presence p and severity s):

- Presence (0/1) gates contribution in W1 x (absent → zero contribution).
- Severity (0–1) scales contribution strength when present.
- Hidden units learn co‑occurrence and severity interactions (e.g., severe sore throat + absence of cough vs. mild sore throat + cough).

---

## Pseudocode (single‑hidden‑layer training)

```
initialize W1 ∈ R^{H×d}, b1 ∈ R^H, W2 ∈ R^{C×H}, b2 ∈ R^C
for epoch in 1..E:
  shuffle(dataset)
  for (x, y_onehot) in dataset:
    # forward
    z1 = W1 x + b1
    a1 = sigmoid(z1)
    z2 = W2 a1 + b2
    yhat = softmax(z2)
    # loss
    L = - sum_k y_onehot[k] * log(yhat[k])
    # backward
    delta2 = yhat - y_onehot
    dW2 = delta2 a1^T;  db2 = delta2
    delta1 = (W2^T delta2) ⊙ a1 ⊙ (1 - a1)
    dW1 = delta1 x^T;    db1 = delta1
    # update
    W2 -= η dW2;  b2 -= η db2
    W1 -= η dW1;  b1 -= η db1
  evaluate val loss; save best; early stop if no improvement
(optional) choose temperature T* on validation for probability calibration)
```

---

## Extending the core

- Deeper nets: stack (affine → nonlinearity) blocks before softmax.
- Other nonlinearities: ReLU/tanh (often faster).
- Regularization: L2, dropout, batch norm.
- Optimizers: momentum, Adam.
- Class imbalance: weighted loss.

---

## Practical debug tips

- Check shapes (x, z1, a1, z2, ŷ).
- Compare train vs. validation losses.
- Inspect confidence; tune T if over‑confident.
- Try tiny synthetic cases where the answer is obvious.

This document lives in `foundational_brain/BEHIND_THE_SCENES.md` and explains the math that downstream models build on.

---

## Appendix A (v0.2 pipeline specifics)

### A1. JSONL → vector mapping
- Each record has a free‑text symptom map (Name → Severity 0–10) and a `label_name`.
- We map names to fixed symptom IDs; build x = [presence; severity], where presence_i = 1 if severity_i > 0 else 0 and severity_i ∈ [0,1].
- Label is mapped to a class index and then one‑hot y.

### A2. Class balance and explicit negatives
- Balanced per‑class counts (or class weights) suppress prior skew.
- Explicit negatives encode “absence of key symptoms” (e.g., dysuria=0, frequency=0 in respiratory cases), teaching strong negative evidence.

### A3. Training objective (softmax + cross‑entropy)
- Same equations as main text; we optimize NLL with SGD.
- Validation split for early stopping; select the best epoch by lowest val loss.

### A4. Probability calibration (temperature scaling)
- Pick T* on the validation set by minimizing NLL(softmax(z/T)).
- At inference, ŷ = softmax(z/T*). This improves reliability (confidence ≈ accuracy).

### A5. Expected Information Gain (EIG) in adaptive questioning
- Current posterior P(d) (after clinical rules).
- For a candidate symptom s, approximate P(yes|d) from disease symptom frequencies.
- P(yes) = Σ_d P(d) P(yes|d); P(no) = 1 − P(yes).
- Posteriors: P(d|yes) ∝ P(d) P(yes|d), P(d|no) ∝ P(d) (1−P(yes|d)).
- Entropy: H(P) = −Σ_d P(d) log P(d).
- EIG(s) = H(P) − [P(yes) H(P(d|yes)) + P(no) H(P(d|no))]. We ask the s with highest EIG.

### A6. Evidence‑aware stop and triage
- We stop only if (a) top‑1 probability ≥ threshold and (b) minimal supporting evidence exists (e.g., at least one GU key for UTI).
- First question is selected from a small triage set (respiratory vs GU vs GI discriminators) to reduce early ambiguity.

### A7. Quick metrics
- Confusion matrix and ECE bins provide a fast snapshot of class separation and calibration.
- ECE = Σ_bins (n_bin/N) |mean_conf − mean_acc|.

### A8. Where to look
- Data gen: `medical_diagnosis_model/data/generate_v02.py`
- Train from JSONL: `medical_diagnosis_model/versions/v2/medical_neural_network_v2.py`
- Pipeline + metrics: `medical_diagnosis_model/tools/train_pipeline.py`
