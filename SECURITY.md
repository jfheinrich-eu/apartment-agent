# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Apartment Agent, please use GitHub's private vulnerability reporting flow for this repository:

https://github.com/jfheinrich-eu/apartment-agent/security/advisories/new

**Please do not disclose security vulnerabilities publicly until we have had a chance to address them.**

### What to Include in Your Report

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact (severity, scope)
- Suggested fix (if available)

We take all security reports seriously and will acknowledge receipt of your report within 48 hours.

## Security Best Practices

When using Apartment Agent:

1. **Configuration Secrets**: Never commit sensitive data (API keys, passwords) to version control
   - Use environment variables or `.env` files (add to `.gitignore`)
   - Example: `bot_token` and `chat_id` for Telegram, SMTP credentials for email

2. **Dependencies**: Keep dependencies up to date
   - Run `pip install --upgrade -e ".[dev]"` regularly
   - Monitor Dependabot alerts on GitHub

3. **Database**: Protect your SQLite database
   - Store `apartments.sqlite3` securely
   - Restrict file permissions: `chmod 600 apartments.sqlite3`
   - Consider encrypting if storing sensitive personal data

4. **Network Requests**: All HTTP requests use:
   - TLS verification enabled by default
   - Configurable timeouts to prevent hanging connections
   - Proper SSL context for SMTP connections

## Supported Versions

| Version | Status | Support Until |
|---------|--------|---------------|
| 0.1.x   | Current | 2027-12-31   |
| 0.0.x   | Deprecated | 2026-12-31   |

## Dependency Security

We monitor dependencies for known vulnerabilities using:
- Dependabot (automatic dependency updates)
- `pip-audit` (vulnerability scanner)
- Regular security scans via GitHub Actions

## Reporting Other Issues

For non-security bugs or feature requests, please use [GitHub Issues](https://github.com/jfheinrich-eu/apartment-agent/issues).

---

Thank you for helping keep Apartment Agent secure!
