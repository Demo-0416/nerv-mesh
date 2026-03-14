---
name: summarize
description: Summarize long text, documents, or web pages into concise key points
version: 0.1.0
tags: [text, analysis, summary]
---

## Instructions

When asked to summarize content:

1. If given a URL, use `web_fetch` to retrieve the content
2. If given a file path, use `file_read` to load it
3. Identify the main topic and purpose of the content
4. Extract key points, organized by importance
5. Output a structured summary:

```
## Summary
One-sentence overview.

## Key Points
- Point 1
- Point 2
- ...

## Details
Expanded explanation of the most important points.

## Source
Where the content came from.
```

Keep summaries concise — aim for 20% of the original length.
