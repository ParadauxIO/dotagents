---
name: create-pr
description: Create a GitHub pull request with Why, How, Diagram, and Screenshots sections, uploading diagram images and real application screenshots through the gh CLI.
---

# Create a pull request

Prepare a reviewer-facing explanation of the complete branch diff and publish it
with `gh`. A request to create a PR authorizes the necessary scoped commit, branch
push, PR creation, and relevant image attachments unless the user says otherwise.
A request to draft text or create this skill does not authorize publishing a PR.
Honor authorization already established in the session; do not add a confirmation
gate to an explicitly requested PR creation.

## Establish the change

Read repository instructions and PR templates. Identify the target repository,
base branch, head branch, worktree changes, and existing PRs for that head/base.
Use an existing PR's base or the user's target; otherwise determine the repository
default. Inspect the full merge-base diff and branch commits, including intended
uncommitted changes before committing. Do not infer scope from the latest commit
alone. Refresh relevant remote refs when necessary.

Keep unrelated changes out of the commit. Create a feature branch if needed, and
push to the intended remote without force-pushing. Ask only if ownership, scope,
or target is materially ambiguous. An existing matching PR should be reported
rather than duplicated; update it when the user's request covers doing so.

Check `gh --version`, authentication for the target host, and
`gh pr create --help` for `--attach` before collecting extensive visual evidence.
Read [attachment handling](references/attachments.md) when preparing images or
publishing. Missing upload support should not prevent preparing the description
and local artifacts; preserve them and report the publishing prerequisite.

## Write the description

Use [the body template](assets/pr-body.md) with these four sections in order.
Preserve required repository fields/checklists, adapting this structure into them
where necessary. Replace all template comments before publication.

- **Why?** Explain the concrete problem and who it affects. For a bug, describe
  the trigger and previous behavior. Link a verified issue when available; use a
  closing keyword only if the PR actually resolves it.
- **How?** Explain the resulting behavior and the important implementation choice.
  Include compatibility, rollout, or tradeoffs only when relevant. Add a concise
  verification statement with actual results and material gaps. Avoid file-by-file
  inventories, pasted logs, and narration of the agent's work.
- **Diagram:** Show the changed flow, state transition, or component relationship.
  Use a collapsible `<details open>` block labeled `Diagram`, expanded by default.
  Render a small source-based diagram to a PNG and attach it inside the block. Explain what
  the reviewer should notice in one sentence. For a trivial change with no useful
  flow or relationship to show, say briefly why a diagram is not applicable.
- **Screenshots:** Show real visual evidence of the affected product. Use a
  before/after table for existing UI and labeled after images for new UI. For a
  nonvisual change, state that screenshots are not applicable. If relevant images
  cannot be captured, state what is missing and why; do not present that as N/A.

Choose a short title describing the final behavior, following the repository's
title convention. Write for a reviewer who has not seen the conversation. Keep
small changes short even with the four-section structure.

## Produce visual evidence

Diagrams describe the actual final implementation, not an aspirational design.
Prefer a compact flowchart like the user's reference: simple rectangular boxes,
short verb-led labels in plain language, and directional arrows. Arrange each
flow top to bottom; place independent paths side by side when that makes their
relationship easier to compare. Show relevant branches and return loops, with
conditions on edges where needed. Do not invent a second path just for symmetry.
Focus on the behavior changed by the PR, not the entire system or a file inventory.
Use neutral, high-contrast styling and generous spacing; keep text readable at PR
body width. The reference's dark page background and viewer controls are not part
of the diagram. Avoid decorative icons, shadows, and unnecessary color coding.

Use Mermaid CLI or an available local diagram renderer; retain editable source
beside the image. For example, with `mmdc` available:

```bash
mmdc -i "$pr_artifacts/flow.mmd" -o "$pr_artifacts/flow.png" -b white
```

Use a task-specific temporary artifact directory outside the repository. Render
locally rather than sending private architecture to a public diagram service.
Open the resulting image to inspect labels, clipping, contrast, and accuracy.
Use rendered diagram images in the body, not only a Mermaid code block. If no
renderer is available, retain the source and report the missing dependency.

Capture screenshots with available Playwright tools or the project's browser
setup. Use the actual PR build for after images and an isolated base build for
before images; do not switch a dirty worktree or modify the DOM/CSS to fabricate
the result. Keep viewport, fixture data, theme, and framing comparable. Label the
page and relevant state, and record tested revisions. If a base build is
unavailable, provide honest after-only evidence and explain the limitation.
The `paradaux:verify-webapp` skill can help when available and verification is
needed, but is not required to use this skill.

Inspect every image before uploading. Prefer synthetic data; exclude credentials
and private customer information. Recapture safely when sensitive data is visible.
Do not commit incidental PR screenshots or diagrams into the application repo.

## Publish and check

Run relevant repository-required checks and report their actual status. Prepare
the final body in a file, with images positioned in the correct sections, then
follow the attachment reference to create the PR using `--body-file` and repeated
`--attach` arguments. Respect requested draft/ready status and repository policy;
otherwise create a ready PR when the work is complete, or a draft with clear gaps
when it is incomplete. Do not merge or enable auto-merge as part of creation.

Read back the PR title, body, base/head, and URL. Confirm local image references
were replaced with uploaded URLs. Inspect the rendered PR and images with an
authenticated browser when available; otherwise report that rendering was not
visually verified. Return the PR URL and any remaining validation or evidence
gaps. Preserve artifacts until uploads and body contents are confirmed.
