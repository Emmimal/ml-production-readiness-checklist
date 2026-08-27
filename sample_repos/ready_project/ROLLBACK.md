# Rollback Runbook

1. Set SERVE_MODEL_VERSION env var to the last known-good tag (see registry.yaml).
2. Redeploy the serving container.
3. Confirm /health returns 200 and prediction logs resume.
4. Notify #ml-oncall.
