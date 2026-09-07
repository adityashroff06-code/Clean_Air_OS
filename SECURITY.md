# Security and responsible reporting

The maintained workflow runs locally and needs no credentials or network access
after dependency installation. Do not add API keys, cloud credentials, personal
Drive listings, or private datasets to source files or notebook outputs.

Use trusted input archives. Station CSVs are parsed in memory and large or malformed
inputs can exhaust resources; this is not a hardened upload service. ZIP members are
read directly rather than extracted, avoiding member-path writes to the filesystem.
Install dependencies in a dedicated environment and review updates before research
reruns where reproducibility matters.

For a security issue or exposed credential, use GitHub's private vulnerability
reporting feature if enabled, or an existing private maintainer contact. Do not put
the secret or sensitive reproduction data into a public issue. If no private channel
is available, open a minimal issue requesting one without disclosing the exploit.
Revoke exposed credentials at the provider; deleting the latest file alone does
not remove credentials from Git history.

No formal security support window, response SLA, or independent audit is claimed.
