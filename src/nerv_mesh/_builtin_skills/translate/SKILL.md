---
name: translate
description: Translate text between languages with context-aware accuracy
version: 0.1.0
tags: [language, translation]
---

## Instructions

When asked to translate:

1. Detect the source language if not specified
2. Translate the content to the target language
3. Preserve the original formatting (markdown, code blocks, etc.)
4. For technical terms, provide the translation with the original in parentheses on first occurrence
5. For ambiguous terms, choose the translation that best fits the context
6. Output format:

```
**Source language**: [detected language]
**Target language**: [target]

---

[translated content]
```

If translating a file, use `file_read` first, then output the translation.
