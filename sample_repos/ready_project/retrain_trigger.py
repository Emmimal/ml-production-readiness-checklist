"""Cron-scheduled retraining trigger. See Article 3 (retraining pipeline)."""

def should_retrain(days_since_last_train, drift_detected, accuracy_drop):
    return days_since_last_train > 30 or drift_detected or accuracy_drop > 0.03
