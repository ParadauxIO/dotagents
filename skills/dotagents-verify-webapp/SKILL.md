---
name: dotagents-verify-webapp
description: Verify a changed web application or reproduce a UI bug by exercising the affected user journey in a browser and checking observable state.
---

# Verify a web application

Use the available Playwright MCP tools or the project's existing browser test
runner. Discover the tools in the current session; do not assume provider-specific
tool names or install a second browser stack when one is already usable.

## Choose the journey

Read the relevant project instructions, startup scripts, and existing tests.
Identify the behavior being changed, the URL/environment, and the expected result.
Use project fixtures and test accounts. Ask for missing access or environment
details only when they block verification; do not guess credentials or production
targets. Keep project-specific setup in the project, not in this global skill.

Turn the request into a small set of observable assertions. Include the failing
path for a bug fix and relevant rejection or error behavior for permissions,
validation, or persistence changes. Avoid expanding a small change into a full
site audit.

## Exercise and inspect

- Reuse the project's documented server command and browser setup. Check whether
  the intended server is already running; record the tested revision and URL.
- Inspect the rendered page before choosing locators. Prefer accessible roles,
  labels, and existing test IDs. Wait for the expected element, response, or state;
  a delay or network-idle signal alone does not prove the app is ready.
- Perform the actual user actions. A successful HTTP response or a screenshot
  alone does not prove a journey completed. Assert the resulting UI state and,
  when relevant and accessible, the API or persisted state. For a save operation,
  reload or revisit the record to check persistence.
- Inspect console errors and failed requests relevant to the journey. Distinguish
  pre-existing background failures from regressions caused by the change.
- Capture useful evidence such as sanitized screenshots, assertion output, or
  traces. Avoid capturing tokens, account details, or sensitive form contents.
  Use disposable data for actions that send messages, create purchases, or alter
  accounts; a verification request does not authorize those actions on real data.

When fixing a bug is in scope, reproduce it before editing when practical, then
rerun the same assertions after the fix. Add a durable regression test when it
protects meaningful behavior using the project's existing test infrastructure.
If access, a missing service, or repeated infrastructure failures block progress,
report the blocker and partial evidence instead of claiming a pass. Clean up only
servers and disposable resources created for this verification.

## Report

State the environment and revision tested, actions exercised, assertions that
passed or failed, evidence locations, and any unverified part of the journey.
Separate observed results from inferences. Report material defects with a minimal
reproduction and expected versus actual behavior.
