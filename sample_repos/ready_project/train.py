import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import cross_val_score, KFold, train_test_split

SEED = 42

def load_features():
    rng = np.random.default_rng(SEED)
    X = rng.normal(size=(2000, 5))
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y

def train_and_validate():
    X, y = load_features()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=SEED
    )
    baseline = DummyClassifier(strategy="most_frequent", random_state=SEED)
    baseline.fit(X_train, y_train)
    baseline_score = baseline.score(X_test, y_test)

    model = LogisticRegression(random_state=SEED)
    cv_scores = cross_val_score(model, X_train, y_train, cv=KFold(5, shuffle=True, random_state=SEED))
    model.fit(X_train, y_train)
    model_score = model.score(X_test, y_test)
    return baseline_score, cv_scores.mean(), model_score

if __name__ == "__main__":
    b, cv, m = train_and_validate()
    print(f"baseline={b:.3f} cv_mean={cv:.3f} test={m:.3f}")
