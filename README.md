# ml-production-readiness-checklist

Companion code for **[ML Production Readiness Checklist: 50 Things to Verify Before You Ship](https://emitechlogic.com/ml-production-readiness-checklist-50-things-to-verify-before-you-ship/)**
— Article 15 (final) of the [Production ML Engineering series](https://emitechlogic.com/machine-learning-production-pipeline/) on [EmiTechLogic](https://emitechlogic.com).

A dependency-free static scanner that checks 20 of the 50 checklist items directly
against a project's files. No API calls, no paid tooling, no third-party services.
Just `ast` and `pathlib` from the Python standard library, the same approach used
in the [Article 14 technical-debt auditor](https://emitechlogic.com/ml-technical-debt-how-to-identify-measure-and-pay-it-down/).

## What this checks

The scanner covers 4 of the 10 items in each of the checklist's 5 sections:

| Section | Automated items |
|---|---|
| 1. Data Quality and Pipeline | schema validation, fixed seed, data versioning, data-quality tests |
| 2. Model Validation and Testing | baseline comparison, cross-validation, model card, model test suite |
| 3. Deployment and Infrastructure | Dockerfile pinning, requirements.txt pinning, health endpoint, CI test gate |
| 4. Monitoring, Alerting, Observability | prediction logging, drift detection, retraining trigger, undeclared-consumer audit |
| 5. Documentation, Handoff, Team Readiness | README completeness, architecture doc, model registry entry, rollback runbook |

The other 30 items (stakeholder sign-off, on-call rotation, compliance review,
whether a runbook has actually been rehearsed) cannot be seen from a file scan.
The article covers all 50; this repo automates the 20 that a script can actually verify.

## Repo structure

```
.
├── checker/
│   └── readiness_checker.py
├── sample_repos/
│   ├── ready_project/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── schema.py
│   │   ├── train.py
│   │   ├── serve.py
│   │   ├── monitor.py
│   │   ├── retrain_trigger.py
│   │   ├── model_card.md
│   │   ├── registry.yaml
│   │   ├── architecture.md
│   │   ├── ROLLBACK.md
│   │   ├── README.md
│   │   ├── features.csv.dvc
│   │   ├── tests/
│   │   │   ├── test_data.py
│   │   │   └── test_model.py
│   │   └── .github/workflows/ci.yml
│   └── legacy_project/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── app.py
│       ├── train_model.py
│       └── README.md
├── LICENSE
└── README.md
```

## Quick start

```bash
git clone https://github.com/Emmimal/ml-production-readiness-checklist.git
cd ml-production-readiness-checklist

python checker/readiness_checker.py sample_repos/ready_project
python checker/readiness_checker.py sample_repos/legacy_project
```

Expected output:

```
=== Readiness scan: sample_repos/ready_project ===
...
Automated checks passed: 19/20 (95.0%)

=== Readiness scan: sample_repos/legacy_project ===
...
Automated checks passed: 1/20 (5.0%)
```

The `ready_project` fails exactly one check on purpose: an unpinned `requests`
dependency in its `requirements.txt`. An honest scanner should find something,
even in a fixture built to pass — the same principle the Article 14 auditor
demonstrated when its "after" refactor still surfaced 3 leftover magic numbers.

## Run it against your own project

```bash
python checker/readiness_checker.py /path/to/your/project
```

The scanner is read-only. It never modifies the target directory.

## Reproduce the article's model numbers

The `ready_project` sample includes a small trained model, a drift check, and a
test suite, so every number quoted in the article can be reproduced exactly:

```bash
cd sample_repos/ready_project
pip install -r requirements.txt
python train.py     # baseline=0.513 cv_mean=0.997 test=0.997
python monitor.py   # drift_detected=True p_value=0.0000
pytest tests -q     # 2 passed
```

Seed is fixed at 42 throughout. Nothing here needs a GPU, an API key, or paid
infrastructure.

**Note for Windows/PowerShell users:** if `pip install -r requirements.txt` hits
a dependency-resolution error, install the packages individually instead
(`pip install pandera==0.20.4 --no-deps`, then `scipy`, `pandas`, `flask` in that
order) — this resolves a solver quirk with pre-existing packages in a venv and
does not indicate a problem with the code itself.

## What this tool intentionally does not do

It cannot verify:
- Whether a rollback runbook has actually been rehearsed, only that the file exists
- Whether stakeholders have signed off on failure modes
- Whether an on-call rotation actually knows the model exists
- Compliance or privacy review status
- Anything that requires a human conversation rather than a file on disk

These 30 items are named explicitly in the article's checklist. A static scanner
that quietly dropped them because they're hard to automate would be less honest
than one that says so.

## License

MIT — see [LICENSE](LICENSE).

## Related

- [Article 15: ML Production Readiness Checklist](https://emitechlogic.com/ml-production-readiness-checklist-50-things-to-verify-before-you-ship/) (this repo's companion article)
- [Article 14: ML Technical Debt](https://emitechlogic.com/ml-technical-debt-how-to-identify-measure-and-pay-it-down/) (source of the undeclared-consumer auditor reused in item 40)
- [Article 11: Shadow Deployment and Canary Testing](https://emitechlogic.com/shadow-deployment-and-canary-testing-for-machine-learning-models-a-practical-guide/)
- [Article 12: Debugging ML Inference Latency](https://emitechlogic.com/debug-ml-inference-latency/)
- [Article 13: A/B Testing ML Models](https://emitechlogic.com/how-to-a-b-test-machine-learning-models-the-right-way/)
- [Production ML Engineering: the complete series](https://emitechlogic.com/machine-learning-production-pipeline/)
