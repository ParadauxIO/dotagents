---
name: resolve-pr
description: Resolve failing CI checks or actionable review feedback on a GitHub pull request, then verify the affected checks and report remaining blockers.
---

# Resolve a pull request

Use available GitHub MCP tools or an authenticated GitHub CLI. Read the applicable
repository instructions and preserve existing user changes. Use the current tool
schemas rather than assuming names or capabilities. Missing log access is a
blocker to diagnose, not a reason to invent a failure cause.

## Establish the current state

Identify the repository, PR, target branch, head SHA, and local checkout revision.
Read the diff, current checks, failed job logs, and review threads, including later
replies. Fetch all relevant pages of results. Confirm feedback still applies to
the current diff before making changes. If the intended PR is ambiguous, ask.

Associate every check result with its commit. A green run on an older commit does
not validate the current head. Do not edit an unrelated branch to fix the PR;
use an appropriate isolated checkout when necessary.

## Resolve actionable findings

Classify findings as code defects, reproducible test failures, likely flaky tests,
environment/service failures, or obsolete feedback. Use the first meaningful
error and surrounding logs rather than the final cascading failure. A failure is
not flaky merely because rerunning might pass.

Make the smallest coherent fix supported by the evidence. Respect reviewer intent
without blindly applying suggestions that conflict with the code or requested
behavior. Explain unaddressed feedback with evidence. Do not silence failures by
weakening assertions, removing required checks, or changing branch protections.

Run the affected local checks and repository-required validation. Commit and push
when authorized by the user's task or existing session instructions; otherwise
prepare the local fix and report that remote validation awaits publication.
Posting replies, resolving review threads, merging, and enabling auto-merge are
separate external actions and require authorization covering those actions.

## Verify and bound retries

After an authorized push, inspect checks for the new head SHA. If the remote head
changes unexpectedly, reconcile the new diff before editing or publishing again.
Avoid force-pushing over another contributor's work.

When rerunning CI is authorized, retry a suspected transient failure once after
collecting evidence. If it repeats, investigate or report the blocker. Do not
repeatedly rerun deployment or other side-effecting jobs as a diagnostic shortcut.
Continue repair while each iteration produces new evidence; stop and summarize
when the same failure persists without a new hypothesis, access is missing, or
the needed fix exceeds the user's scope. Do not wait indefinitely for queued
checks or reviewers; report pending status honestly.

## Report

Summarize the defects fixed, feedback addressed or left open, local checks run,
and CI status with the corresponding head SHA and links. Distinguish passed,
failed, pending, and unavailable checks. Passing local tests does not mean CI has
passed, and passing CI alone does not mean the PR is approved or mergeable.
