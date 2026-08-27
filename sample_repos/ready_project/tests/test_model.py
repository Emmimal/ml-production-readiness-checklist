from train import train_and_validate

def test_model_beats_baseline():
    baseline, cv_mean, test_score = train_and_validate()
    assert test_score > baseline
