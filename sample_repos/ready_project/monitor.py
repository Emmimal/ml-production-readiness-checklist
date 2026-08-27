from scipy.stats import ks_2samp
import numpy as np

def check_drift(reference, current, alpha=0.05):
    stat, p_value = ks_2samp(reference, current)
    return p_value < alpha, p_value

if __name__ == "__main__":
    rng = np.random.default_rng(42)
    ref = rng.normal(size=1000)
    cur = rng.normal(loc=0.4, size=1000)
    drifted, p = check_drift(ref, cur)
    print(f"drift_detected={drifted} p_value={p:.4f}")
