from backend.selector.eig_selector import expected_information_gain


def test_eig_ranks_informative_symptom_higher():
    disease_probs = {"viral_uri": 0.5, "strep": 0.5}
    # symptom A splits posteriors strongly; symptom B is almost uninformative
    symptom_to_likelihood = {
        "fever": (0.9, 0.1),
        "rhinorrhea": (0.55, 0.45),
    }
    ranked = expected_information_gain(disease_probs, symptom_to_likelihood)
    assert ranked[0][0] == "fever"


