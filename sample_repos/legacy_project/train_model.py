import pandas as pd
from sklearn.linear_model import LogisticRegression

def train():
    df = pd.read_csv("data/features.csv")
    X = df.drop(columns=["label"])
    y = df["label"]
    model = LogisticRegression()
    model.fit(X, y)
    return model.score(X, y)

if __name__ == "__main__":
    print(train())
