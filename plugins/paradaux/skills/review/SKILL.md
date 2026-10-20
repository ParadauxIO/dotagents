---
name: review
description: Review a diff, branch, commit, or pull request for concrete defects, missing verification, and unnecessary complexity. Use when asked to review changes; use resolve-pr to repair existing review feedback or CI failures.
---

# Review changes

Produce an evidence-based review within the requested scope. A review request
authorizes investigation and relevant local checks, not edits or publication of
GitHub comments. Follow existing authorization if fixes or posting were also requested.

## Establish the target

Read repository instructions and inspect the working tree. Use the named files,
commit, staged changes, branch, or PR. For a branch or PR, establish the base and
head and compare against their merge base; include uncommitted work only when
requested. Without a named target, review uncommitted changes, including relevant
untracked files; if there are none, review the latest commit and state that choice.
Ask when the repository or comparison target remains materially ambiguous.

Read the change and connected code: affected callers, dependencies, tests, and
documented contracts. Trace inputs through state changes to outputs. Follow
signature, units, return-shape, and error-behavior changes beyond the diff. Use
deployment settings or documented usage to judge concurrency and input size;
state consequential assumptions rather than inventing production requirements.

## Investigate likely failures

Prioritize incorrect results, broken callers, security boundaries, data loss,
and failures under the expected workload. Check whether tests exercise changed
behavior and would detect the suspected regression. Run focused checks when
practical; distinguish executed evidence from reasoning and unavailable checks.

Flag complexity only when it has a concrete cost: duplicate logic that can drift,
an existing helper being bypassed, or speculative options that expand maintenance.
Name the reusable implementation or explain the simpler equivalent. Preserve
required behavior, project conventions, accessibility, and protective checks.
Do not turn the review into a repository-wide redesign or a list of style tastes.

Before reporting a defect, verify a reachable trigger, affected caller, and
observable consequence. Re-read surrounding guards and tests; reject suspicions
that the code already handles. A documented limitation is relevant when the
requested behavior or expected workload exceeds it, not merely because a more
general solution is possible. Report material test gaps separately from proven
bugs, identifying the behavior that lacks protection.

## Report findings

Lead with the material outcome. Order findings by impact and give each a stable
number, file/line reference, triggering situation, consequence, and smallest
plausible fix. Explain enough context for someone unfamiliar with the code.
Separate defects that block the requested behavior from optional improvements;
do not inflate severity to make a preference actionable.

Finish with relevant checks and unresolved limitations. If no actionable findings
remain, say so and summarize the coverage; absence of findings is not proof of
correctness. Avoid compulsory risk statements when there is no material gap.
