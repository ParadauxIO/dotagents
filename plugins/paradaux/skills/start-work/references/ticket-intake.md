# Ticket intake adapters

Use the tracker identified by the URL, user, or established project context.
Discover available tools and their schemas in the current agent session. Tool
prefixes vary between Claude Code, Codex, and their hosts. These adapters describe
capabilities rather than requiring one provider-specific tool namespace.

## Tasklie

The available Tasklie MCP exposes these operations:

| Input / need | Operation | Arguments |
| --- | --- | --- |
| Task reference, such as `PAR-123` | `tasklie_get_task` | `taskRef` |
| Ticket title or description | `tasklie_search_tasks` | `query`, optional `limit` |
| Discussion on the selected task | `tasklie_list_comments` | `taskRef` |

Search returns candidates, not a decision about which task the user meant. Once
resolved, fetch the full task and discussion. Task detail includes project,
status, subtasks, and development links such as branches, commits, and PRs.
Comments are returned oldest first: inspect later replies before acting on an
early suggestion. Follow relevant development links to check for existing work.
Use current tool schemas for any additional relationships; do not invent an API
or infer that missing fields mean there are no dependencies.

For a Tasklie URL, obtain the actual reference from the URL or accessible page;
do not manufacture it from a title slug. If a title is ambiguous across projects,
show a short candidate list with references and project names. If a result set
hits the search limit, narrow the search rather than treating it as exhaustive.

## GitHub issues

Use GitHub MCP or an authenticated `gh`. Prefer an explicit URL or repository and
issue number. Resolve `#123` against the established repository, not an arbitrary
remote. A URL pointing to a pull request is existing development context, not
automatically a new implementation ticket.

With task-specific variables holding the resolved repository and issue:

```bash
gh issue view "$intake_issue" --repo "$intake_repo" \
  --json number,title,body,url,state,assignees,labels
gh issue view "$intake_issue" --repo "$intake_repo" --comments
```

For a title search, include closed issues so already-completed work is visible:

```bash
gh issue list --repo "$intake_repo" --state all \
  --search "$intake_query" --limit 30 --json number,title,url,state
```

Check current CLI help or MCP schemas for parent/sub-issues, blockers, and linked
PRs. Retrieve those relationships when relevant. Check for truncation/pagination
and fetch the missing pages needed for the task; `--limit 30` is a bounded search,
not proof that no other match exists. Distinguish access failures from no matches.

## Named ticket without a provider

Use the user's established tracker or an unambiguous project association. A bare
title could also be a plain-text request: search only when the user identifies it
as a ticket or the context makes that clear. If the provider or project remains
ambiguous, ask one focused question rather than searching every connected account.

Keep intake read-only with respect to the tracker. Read access and ticket content
do not imply authorization to post comments, assign work, or transition status.
