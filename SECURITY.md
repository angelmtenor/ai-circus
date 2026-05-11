# Security

## Deployment Hardening Checklist

Before deploying ai-circus services to production, verify every item below:

### Environment & Secrets

- [ ] `.env` file is NOT committed (verify `.gitignore` excludes `.env*`)
- [ ] All API keys use `SecretStr` (never logged in plaintext)
- [ ] `gitleaks` pre-commit hook is active (detects accidental secret commits)
- [ ] No hardcoded credentials in source code
- [ ] `.copilotignore` hides `.env*` from AI agent context

### Configuration

- [ ] `settings.yaml` ↔ `data_model.py` are in sync (run `uv run ai-env-check`)
- [ ] All mandatory fields have regex validation in `settings.yaml`
- [ ] `fail_on_missing: true` in global settings (app fails fast on missing vars)

### API & Network

- [ ] HTTP request timeouts configured for all external API calls
- [ ] Rate limiting / retry logic with exponential backoff enabled
- [ ] No debug logging of user queries in production (PII risk)
- [ ] Server host is NOT `0.0.0.0` unless behind a reverse proxy

### Subprocess Safety

- [ ] All subprocess calls use argument lists (never `shell=True`)
- [ ] Git command allow-list enforced (only `git diff`, `git ls-files`, `git commit`, `git add`)
- [ ] Executable paths validated with `shutil.which()` before execution

### Dependencies

- [ ] `uv.lock` reviewed for unexpected changes
- [ ] No known CVEs in dependency tree (`uv pip audit` or equivalent)
- [ ] Pre-commit hooks enforced in CI

### LLM-Specific

- [ ] LLM responses parsed with `json.loads()` (not regex alone)
- [ ] Output from LLM never executed as code without sandboxing
- [ ] Prompt injection mitigations in place for user-facing assistants
- [ ] Token/cost limits configured to prevent runaway spending

---

## Known Patterns & Mitigations

### Secret Logging Prevention

All secrets use Pydantic `SecretStr`. When displaying:
```python
val = "****" + secret.get_secret_value()[-4:] if secret else "None"
```

### Subprocess Hardening

Commands are allow-listed and passed as argument lists:
```python
ALLOWED_COMMANDS = {"git diff", "git ls-files", "git commit", "git add"}
subprocess.run(["git", "diff", "--staged"], check=True)  # Safe
```

### Env Drift Detection

Generated `data_model.py` contains a SHA-256 hash of the source YAML.
Run `uv run ai-env-check` to verify sync. CI should include this check.

---

## Reporting Vulnerabilities

If you discover a security issue, please report it responsibly via a private issue
or email rather than public disclosure. See [CONTRIBUTING.md](CONTRIBUTING.md).
