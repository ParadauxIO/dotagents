---
name: dotagents-debug-auth
description: Diagnose failed login, session, or authorization behavior in applications using Keycloak, including mismatches in app configuration or Infisical-managed settings.
---

# Diagnose application authentication

Trace the reported failure from browser to application to identity provider.
Use the project's auth configuration and available Keycloak, Infisical, browser,
and log tools. Discover current tool capabilities; this skill does not assume
specific realms, clients, deployments, or secret names.

## Establish a concrete failure

Identify the affected environment, application, expected identity/role, failing
operation, timestamp, and observed response. Determine whether the failure is
login, callback/session creation, token validation, or application authorization.
Read the relevant project configuration and tests before querying remote systems.
Use a test account or sanitized reproduction where possible.

Collect the smallest evidence needed to distinguish hypotheses. Start with
configuration metadata and scoped reads. Do not dump environment variables,
secret stores, cookies, authorization codes, or raw tokens. If claim inspection is
needed, extract only relevant non-secret fields locally and redact identifying
values in reports; never submit tokens to public decoder sites. Decoding a token
does not validate its signature.

## Follow the failed boundary

Use [the symptom checklist](references/auth-boundaries.md) for the observed stage.
Compare the configuration actually used by the running app with the intended
configuration, not just a checked-in example. For Infisical-backed settings,
compare project/environment/path, key names, references, and version or deployment
timing before accessing values. An updated secret does not prove that a running
process reloaded it. Fetch secret values only when necessary and authorized,
without exposing them in tool output or artifacts.

For each hypothesis, name an observation that would confirm or reject it. Prefer
a targeted request, relevant log entry, or configuration comparison over broad
enumeration of users, realms, or secrets. Distinguish authentication failure from
a correctly authenticated user lacking application permissions.

## Fix and verify within scope

A diagnosis request permits investigation, not changing remote realms, user roles,
client settings, or secrets. Prepare the specific change and evidence first; apply
remote changes only when authorized. Do not bypass token validation, broaden
redirect patterns, disable protections, or grant elevated roles to make the test
pass. Preserve existing authorization and continue local fixes when requested.

Verify the original failing operation after the fix, including session refresh
or a fresh login when relevant. For authorization changes, verify both a permitted
identity and an identity that must remain denied. If access or unavailable
infrastructure prevents verification, state that limitation and the next useful
observation rather than cycling through speculative configuration changes.

Report the failed boundary, supporting sanitized evidence, cause versus remaining
hypotheses, proposed or applied change, and verification results. Keep any newly
confirmed project-specific gotchas in the project's existing documentation when
documentation updates are in scope.
