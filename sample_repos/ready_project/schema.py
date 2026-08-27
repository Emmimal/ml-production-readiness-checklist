import pandera as pa

feature_schema = pa.DataFrameSchema({
    "user_age": pa.Column(int, pa.Check.in_range(18, 100)),
    "account_age_days": pa.Column(int, pa.Check.ge(0)),
    "avg_session_minutes": pa.Column(float, pa.Check.ge(0)),
})
