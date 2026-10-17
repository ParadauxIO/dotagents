# Attach diagrams and screenshots with gh

## Capability and prerequisites

GitHub introduced native `--attach` in gh 2.99.0. Check the installed command's
help for support rather than trusting the version alone. Creation and editing
must each support the flag if used. Uploads need repository write access and a
supported authentication method/host. The initial release supports GitHub.com and
Enterprise Cloud, not Enterprise Server; consult current official documentation
if the target differs. Never print tokens to diagnose authentication.

If unsupported, prepare the body and images and report the needed CLI upgrade or
access. Do not silently publish broken local links, substitute an unverified
upload extension/API, or commit images just to get public URLs. Upgrade tooling
when authorized by the task/environment; otherwise leave the concrete artifacts
ready for retry. A user can explicitly choose to publish with evidence gaps.

## Position images before uploading

Use ordinary Markdown images, including inside Markdown tables. Avoid HTML image
tags for path replacement. Use the same exact path string in each Markdown image
and its `--attach` argument. Prefer simple absolute filenames without spaces or
special Markdown characters in a unique temporary directory. Absolute paths are
local input only; they must not remain in the published body.

For example, when the task directory is `/tmp/pr-evidence-abc123`:

```markdown
<details open>
<summary><strong>Diagram</strong></summary>

The callback now establishes a session before navigating to the dashboard.

![Login callback flow](/tmp/pr-evidence-abc123/flow.png)

</details>

## Screenshots

| State | Before | After |
| --- | --- | --- |
| Login callback error | ![Callback before](/tmp/pr-evidence-abc123/before.png) | ![Callback after](/tmp/pr-evidence-abc123/after.png) |
```

Keep blank lines after `</summary>`
and before `</details>` so GitHub renders the Markdown within the collapsible
block. Keep the image reference as `![alt](path)` for attachment replacement.

Write the body using a file-writing tool or a quoted heredoc; do not interpolate
Markdown through shell command substitution. Store the actual repository, base,
head, title, body path, and artifact directory in task-specific variables. With
the intended branch already pushed, the publication command has this shape:

```bash
gh pr create --repo "$pr_repo" --base "$pr_base" --head "$pr_head" \
  --title "$pr_title" --body-file "$pr_body" \
  --attach "$pr_artifacts/flow.png" \
  --attach "$pr_artifacts/before.png" \
  --attach "$pr_artifacts/after.png"
```

Pass only files that exist and belong in this PR. Add `--draft` when appropriate.
Use shell arrays or a subprocess argument list for a variable number of files,
never `eval`. An unmatched attachment is appended to the body, so path matching
matters for keeping the requested layout. PNG is a convenient shared format for
diagrams and browser captures; keep individual images below the documented 10 MB
limit and inspect legibility after resizing.

For an authorized update, fetch the existing body first, preserve human content,
and use `gh pr edit "$pr_number" --repo "$pr_repo" --body-file "$pr_body"`
with attachment flags only for new local images. Retain existing remote image
URLs. Do not overwrite human edits made while preparing the update.

## Verify or recover

```bash
gh pr view "$pr_number" --repo "$pr_repo" \
  --json url,title,body,baseRefName,headRefName,headRefOid,isDraft
```

Check every intended image is in its section, no local paths remain, and the PR
targets the correct branches/revision. Reuse uploaded URLs on subsequent edits.
If a command times out or fails after an upload, inspect remote state before
retrying creation; the PR may already exist. Repair the existing PR when
authorized rather than creating duplicates. Do not repeatedly retry a persistent
authentication or capability error. `gh pr create --dry-run` is not a guaranteed
read-only preview: the CLI documents that it may push Git changes. Preview the
local body and images directly instead.

## Sources and design choices

Checked October 17, 2026. These are references, not additional instructions to load
for every PR:

- [GitHub attachment documentation](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)
  and [release announcement](https://github.blog/changelog/2026-09-01-github-cli-media-in-issues-pull-requests-and-comments/):
  native uploads and in-place Markdown path replacement.
- [GitHub PR creation manual](https://cli.github.com/manual/gh_pr_create): explicit
  base/head selection, body files, and dry-run behavior.
- [Sentry PR screenshots](https://github.com/getsentry/skills/blob/main/skills/pr-screenshots/SKILL.md):
  real product captures and comparable before/after framing.
- [Sentry PR writer](https://github.com/getsentry/skills/blob/main/skills/pr-writer/SKILL.md):
  explain the whole diff for reviewers. This skill uses the user's four-section
  format rather than Sentry's body structure or draft default.
- [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli): render editable diagram
  source into an attachable image.
