# Auth boundary checklist

Use only the section matching the observed failure. Treat these as diagnostic
comparisons; exact settings and behavior depend on the project's library and
Keycloak version. Consult the installed version's documentation for changes.

| Failed stage | Evidence to compare |
| --- | --- |
| Login never reaches the expected realm | Browser redirect chain; configured issuer/realm; externally visible scheme and hostname; reverse-proxy routing. |
| Provider rejects the authorization request | Actual client ID and redirect URI versus that client's registered settings; requested flow and PKCE support. Compare exact scheme, host, port, and path before proposing changes. |
| Callback fails or loses the session | Application callback logs; state/nonce or PKCE mismatch; cookie domain, path, Secure and SameSite behavior; proxy scheme handling; consistency of session configuration across replicas. |
| Token exchange fails | Sanitized provider error; token endpoint and realm; public versus confidential client configuration; configured client authentication method; app configuration version. Do not assume every failure means the secret is wrong. |
| API rejects a token | Token type expected by the API; issuer, audience, expiry, not-before and server clock; signing key ID and the verifier's JWKS source/cache; actual verification error. An ID token is not interchangeable with an API access token. |
| Login succeeds but access is denied | Application permission rule; relevant realm/client roles, scopes or tenant membership; mapping into the issued token; whether the session predates a role change. A UI-hidden action is not proof the API enforces authorization. |
| Only one environment or replica fails | Runtime config source and deployment revision; secret reference/version metadata; issuer and callback URLs; proxy and cookie differences; which replica served the failing request. |

Capture only claims necessary for the comparison. Do not record raw tokens or
session cookies in screenshots, traces, command lines, reports, or checked-in
fixtures. Use synthetic credentials and claims for regression tests.
