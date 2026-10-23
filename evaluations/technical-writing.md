# Technical-writing evaluation

## Method and limits

On 2026-10-23, the authoring Codex agent applied the candidate skill to the five
original inputs below, produced the retained outputs, and checked them against
explicit semantic criteria. This is a same-agent walkthrough, not an independent
model trial, clinical evaluation, or measured baseline comparison. No further
agents were launched. Model identifier, cost, latency, and human correction time
were not measured. No fixture commands were executed; the services are fictional.

For replication, give a fresh session only the candidate skill and one prompt/input
below. Keep the evaluator criteria hidden until output is complete. Compare with
no-skill output using the same model/settings and repeat across clients. Grade
meaning and reader task completion before style or length. A phrase match alone
is not a passing result. These small cases cannot establish broad effectiveness.

## 1. Operator procedure: preserve conditions and warnings

Prompt: Rewrite this for an on-call operator. Do not add commands.

Input:

> In order to seamlessly restore processing, restart `queue-worker` on `jobs-2`
> if the queue is paused. Before restarting, confirm that `active_jobs=0`;
> otherwise a restart can interrupt jobs. After restarting, inspect the status.
> Success is `state=running`. If the status is not running, escalate to the
> on-call lead. Do not delete the queue.

Candidate output:

> If the queue is paused, use these steps. A restart can interrupt jobs if
> `active_jobs` is not zero. Do not delete the queue.
>
> 1. Confirm that `active_jobs=0` before restarting.
> 2. Restart `queue-worker` on `jobs-2`.
> 3. Inspect the status. Success is `state=running`. If the status is not running,
>    escalate to the on-call lead.

Observed: PASS in author review. The pause condition precedes the procedure;
zero active jobs precedes restart; target, success criterion, escalation, and
prohibition survive. No executable syntax was invented. Failure probe: putting
the active-job check after restart fails even if the prose is shorter.

## 2. API reference: preserve requirements and uncertainty

Prompt: Make this API paragraph clearer for an integrator.

Input:

> A client should retry HTTP 503 responses. A client must not retry HTTP 400
> responses. A retry may succeed, but success is not guaranteed. The server may
> return `Retry-After`; when present, wait that many seconds before retrying.
> Reuse `Idempotency-Key` for a retry of the same request.

Candidate output:

> Clients should retry HTTP 503 responses and must not retry HTTP 400 responses.
> A retry may succeed; success is not guaranteed. If the server returns
> `Retry-After`, wait the specified number of seconds before retrying. Reuse
> `Idempotency-Key` when retrying the same request.

Observed: PASS in author review. Recommendation, prohibition, uncertain success,
optional header, units, and key reuse remain. Failure probe: replacing “should”
with “must” or “may” with “will” changes the contract and fails. No default retry
count or backoff algorithm was added.

## 3. Incident report: separate evidence from cause

Prompt: Rewrite for an engineering incident report. Use only these facts.

Input:

> Obviously the database caused the outage. Well, the logs show requests returned
> 503 from 09:12 to 09:18 UTC on 2026-10-20, and database CPU was high at 09:13.
> We suspect connection exhaustion but have not confirmed it. No impact count
> or recovery action has been established.

Candidate output:

> Requests returned HTTP 503 from 09:12 to 09:18 UTC on 2026-10-20. Database CPU
> was high at 09:13 UTC. Connection exhaustion is a suspected cause and remains
> unconfirmed. The impact count and recovery action are unknown.

Observed: PASS in author review. Times, date, observation, hypothesis, and missing
information remain distinct. The unsupported causal assertion is removed rather
than polished into apparent certainty. Failure probe: claiming that a restart
restored service or reporting a six-minute database failure fails.

## 4. Developer explanation: keep distinct concepts and exact literals

Prompt: Explain this to a new developer without changing its facts.

Input:

> Authentication verifies who you are; authorization checks what you can do.
> GET /reports requires `reports:read`. A valid login without that scope returns
> `403 Forbidden`. The `--dry-run` option reports changes without applying them.

Candidate output:

> Authentication establishes your identity. Authorization determines what you
> can do. `GET /reports` requires the `reports:read` scope. A valid login without
> that scope returns `403 Forbidden`. The `--dry-run` option reports changes
> without applying them.

Observed: PASS in author review. The two concepts remain distinct; endpoint,
scope, error, flag, and non-mutating behavior survive. Failure probe: replacing
both concepts with “verification” or changing 403 to 401 fails.

## 5. Review-only scope: find consequential omissions

Prompt: Review this runbook; do not rewrite it. The supplied reference is the
entire available evidence.

Reference: Export the archive before deletion. `purge --all` permanently deletes
all archives. No recovery method is documented.

Draft: Line 1: “Run `purge --all`.” Line 2: “Export your archive afterward.”
Line 3: “You can always recover deleted archives.”

Candidate output:

> Lines 1–2 put export after permanent deletion, so the reader can lose the archive.
> Move the export prerequisite before `purge --all` and state the permanent-loss risk.
>
> Line 3 promises recovery without supporting evidence. Remove that guarantee;
> the reference documents no recovery method.

Observed: PASS in author review. Reports locations, reader impact, and corrections;
does not execute the command, fabricate recovery, or replace the entire runbook.
Failure probe: cosmetic comments alone miss both consequential defects and fail.

## Outcome

Five of five retained outputs satisfy their semantic criteria in author review.
The failure probes demonstrate what the rubric rejects; they are counterexamples,
not executed mutation tests. No independent or blinded evaluation was performed.
Preserving modals, conditions, and literals takes priority over mechanically
removing every marker of AI prose. Follow-up reader tests should check whether
operators and new developers can actually complete their tasks using these texts.
