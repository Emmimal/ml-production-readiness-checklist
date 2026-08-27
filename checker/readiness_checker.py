"""
ML Production Readiness Checker
Article 15 companion tool. Statically scans a project directory for
20 of the 50 checklist items, four per section, that are actually
visible from files on disk. The other 30 items are judgment calls
a static tool cannot see (sign-off, on-call rotations, compliance
review, etc.) and are intentionally left out of this script. See
the article for the full 50-item list.

No third-party dependencies. Same ast + pathlib approach as the
Article 14 static auditor.
"""
import ast
import re
from pathlib import Path


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def find_files(root: Path, pattern: str):
    return list(root.rglob(pattern))


def any_file_contains(root: Path, glob_pattern: str, needles):
    for f in find_files(root, glob_pattern):
        text = read_text(f)
        if any(n in text for n in needles):
            return True
    return False


# ---------- Section 1: Data Quality and Pipeline Checks ----------

def check_schema_validation(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["pandera", "pydantic", "DataFrameSchema", "jsonschema"])


def check_fixed_seed(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["random_state=", "seed=", "np.random.default_rng", "torch.manual_seed"])


def check_data_versioning(root: Path) -> bool:
    return bool(find_files(root, "*.dvc")) or any_file_contains(root, "*", ["dvc add", "data_version"])


def check_data_quality_tests(root: Path) -> bool:
    return bool(find_files(root, "tests/test_data*.py")) or bool(find_files(root, "test_data*.py"))


# ---------- Section 2: Model Validation and Testing ----------

def check_baseline_comparison(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["DummyClassifier", "DummyRegressor", "baseline_score", "baseline ="])


def check_cross_validation(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["cross_val_score", "KFold", "StratifiedKFold", "cross_validate"])


def check_model_card(root: Path) -> bool:
    return bool(find_files(root, "model_card.md")) or bool(find_files(root, "MODEL_CARD.md"))


def check_model_tests(root: Path) -> bool:
    return bool(find_files(root, "tests/test_model*.py")) or bool(find_files(root, "test_model*.py"))


# ---------- Section 3: Deployment and Infrastructure ----------

def check_dockerfile_pinned(root: Path) -> bool:
    for f in find_files(root, "Dockerfile"):
        text = read_text(f)
        if re.search(r"^FROM\s+\S+:latest\s*$", text, re.MULTILINE):
            return False
        if re.search(r"^FROM\s+\S+:\S+", text, re.MULTILINE):
            return True
    return False


def check_requirements_pinned(root: Path) -> bool:
    for f in find_files(root, "requirements.txt"):
        lines = [l.strip() for l in read_text(f).splitlines() if l.strip() and not l.startswith("#")]
        if not lines:
            continue
        pinned = [l for l in lines if "==" in l]
        return len(pinned) == len(lines)
    return False


def check_health_endpoint(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["/health", "/healthz", "/ready"])


def check_ci_runs_tests(root: Path) -> bool:
    for f in find_files(root, "*.yml") + find_files(root, "*.yaml"):
        if ".github/workflows" in str(f) or "ci" in f.name.lower():
            text = read_text(f)
            if "pytest" in text or "test" in text.lower():
                return True
    return False


# ---------- Section 4: Monitoring, Alerting, Observability ----------

def check_prediction_logging(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["logging.info", "logger.info", "prediction_logged", "log_prediction"])


def check_drift_detection(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["ks_2samp", "evidently", "population_stability", "psi(", "check_drift"])


def check_retrain_trigger(root: Path) -> bool:
    return any_file_contains(root, "*.py", ["should_retrain", "retrain_trigger", "RETRAIN_THRESHOLD"])


def check_undeclared_consumers(root: Path) -> bool:
    """Reuses the Article 14 static auditor logic: an artifact string
    referenced directly by 2+ files fails this check."""
    artifact_pattern = re.compile(r"['\"]((?:data|models|archive|logs)/[\w\-./]+|[\w\-./]+\.(?:csv|json|pkl|parquet))['\"]")
    references = {}
    for f in find_files(root, "*.py"):
        text = read_text(f)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if artifact_pattern.search(f"'{node.value}'"):
                    references.setdefault(node.value, set()).add(str(f))
    undeclared = {k: v for k, v in references.items() if len(v) > 1}
    return len(undeclared) == 0


# ---------- Section 5: Documentation, Handoff, Team Readiness ----------

def check_readme_sections(root: Path) -> bool:
    for f in find_files(root, "README.md"):
        text = read_text(f).lower()
        if "setup" in text and "usage" in text:
            return True
    return False


def check_architecture_doc(root: Path) -> bool:
    return bool(find_files(root, "architecture.*")) or bool(find_files(root, "ARCHITECTURE.*"))


def check_rollback_runbook(root: Path) -> bool:
    return bool(find_files(root, "ROLLBACK.md")) or bool(find_files(root, "runbook*.md"))


def check_model_registry(root: Path) -> bool:
    return bool(find_files(root, "registry.yaml")) or bool(find_files(root, "registry.json")) or \
        bool(find_files(root, "model_registry.*"))


CHECKS = {
    "Section 1: Data Quality and Pipeline": [
        ("Schema validation defined (item 1)", check_schema_validation),
        ("Fixed random seed used (item 4)", check_fixed_seed),
        ("Data versioning present (item 6)", check_data_versioning),
        ("Data quality tests exist (item 10)", check_data_quality_tests),
    ],
    "Section 2: Model Validation and Testing": [
        ("Baseline comparison implemented (item 11)", check_baseline_comparison),
        ("Cross-validation used (item 12)", check_cross_validation),
        ("Model card present (item 15)", check_model_card),
        ("Model test suite exists (item 14)", check_model_tests),
    ],
    "Section 3: Deployment and Infrastructure": [
        ("Dockerfile pins a version, not latest (item 24)", check_dockerfile_pinned),
        ("requirements.txt fully pinned (item 25)", check_requirements_pinned),
        ("Health check endpoint present (item 23)", check_health_endpoint),
        ("CI runs tests before deploy (item 29)", check_ci_runs_tests),
    ],
    "Section 4: Monitoring, Alerting, Observability": [
        ("Prediction logging implemented (item 31)", check_prediction_logging),
        ("Drift detection code present (item 33)", check_drift_detection),
        ("Retraining trigger implemented (item 38)", check_retrain_trigger),
        ("No undeclared consumers (item 40, Article 14 auditor)", check_undeclared_consumers),
    ],
    "Section 5: Documentation, Handoff, Team Readiness": [
        ("README has Setup and Usage (item 41)", check_readme_sections),
        ("Architecture documented (item 42)", check_architecture_doc),
        ("Rollback runbook present (item 44)", check_rollback_runbook),
        ("Model registry entry present (item 43)", check_model_registry),
    ],
}


def run(root_str: str):
    root = Path(root_str)
    total = 0
    passed = 0
    section_results = {}
    for section, checks in CHECKS.items():
        results = []
        for label, fn in checks:
            ok = fn(root)
            results.append((label, ok))
            total += 1
            passed += int(ok)
        section_results[section] = results
    return section_results, passed, total


def print_report(root_str: str):
    section_results, passed, total = run(root_str)
    print(f"\n=== Readiness scan: {root_str} ===")
    for section, results in section_results.items():
        section_passed = sum(1 for _, ok in results if ok)
        print(f"\n{section} ({section_passed}/{len(results)})")
        for label, ok in results:
            mark = "PASS" if ok else "FAIL"
            print(f"  [{mark}] {label}")
    pct = round(100 * passed / total, 1)
    print(f"\nAutomated checks passed: {passed}/{total} ({pct}%)")
    print("Remaining 30 items are judgment calls: see the manual sign-off section.")
    return pct


if __name__ == "__main__":
    import sys
    print_report(sys.argv[1] if len(sys.argv) > 1 else ".")
