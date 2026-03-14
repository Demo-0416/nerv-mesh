---
name: daily-report
description: Generate a daily work report from git history and file changes
version: 0.1.0
tags: [report, git, productivity]
---

## Instructions

When asked to generate a daily report:

1. Determine the date range (default: today)
2. Run `shell_exec` to get git log:
   ```bash
   git log --since="YYYY-MM-DD 00:00" --until="YYYY-MM-DD 23:59" --pretty=format:"%h | %an | %s" --date=short
   ```
3. Run `shell_exec` to get file change stats:
   ```bash
   git diff --stat HEAD~N..HEAD
   ```
4. Generate a structured report:

```
# Daily Report — YYYY-MM-DD

## Commits
- [hash] description

## File Changes
- X files changed, Y insertions, Z deletions

## Summary
Brief narrative of what was accomplished.
```

If no git repo is found, inform the user and offer to summarize based on other inputs.
