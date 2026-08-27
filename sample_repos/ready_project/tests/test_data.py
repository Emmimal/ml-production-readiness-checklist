from schema import feature_schema
import pandas as pd

def test_schema_accepts_valid_data():
    df = pd.DataFrame({
        "user_age": [25, 40],
        "account_age_days": [10, 200],
        "avg_session_minutes": [5.0, 12.5],
    })
    feature_schema.validate(df)
