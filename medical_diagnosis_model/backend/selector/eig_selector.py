from __future__ import annotations

from typing import Dict, List, Tuple
import math


def _entropy(probabilities: List[float]) -> float:
    eps = 1e-12
    return -sum(p * math.log(max(p, eps)) for p in probabilities)


def expected_information_gain(
    disease_probs: Dict[str, float],
    symptom_to_likelihood: Dict[str, Tuple[float, float]],
) -> List[Tuple[str, float]]:
    """Rank symptoms by expected entropy reduction (yes/no).

    Inputs:
      - disease_probs: current posterior over diseases
      - symptom_to_likelihood: map symptom -> (P(yes|disease), P(no|disease)) approximations

    Returns: list of (symptom, EIG) sorted desc.
    Simplified toy math: assumes binary answers and naive Bayes update.
    """
    diseases = list(disease_probs.keys())
    p = [disease_probs[d] for d in diseases]
    h_before = _entropy(p)

    ranked: List[Tuple[str, float]] = []
    for symptom, (py, pn) in symptom_to_likelihood.items():
        # Approximate answer priors under current belief
        p_yes = sum(disease_probs[d] * py for d in diseases)
        p_no = 1.0 - p_yes

        # Posterior if answer is yes/no (naive Bayes style, normalized)
        def posterior(mult: float) -> List[float]:
            unnorm = [disease_probs[d] * mult for d in diseases]
            z = sum(unnorm) or 1e-12
            return [u / z for u in unnorm]

        p_post_yes = posterior(py)
        p_post_no = posterior(pn)

        h_yes = _entropy(p_post_yes)
        h_no = _entropy(p_post_no)
        eig = h_before - (p_yes * h_yes + p_no * h_no)
        ranked.append((symptom, eig))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked


