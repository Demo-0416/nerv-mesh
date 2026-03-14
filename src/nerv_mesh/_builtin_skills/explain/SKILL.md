---
name: explain
description: Explain complex concepts, code, or errors in simple terms
version: 0.1.0
tags: [education, explanation]
---

## Instructions

When asked to explain something:

1. Assess the complexity of the topic
2. Start with a one-sentence summary (the "elevator pitch")
3. Then provide a layered explanation:
   - **Simple**: Explain like I'm 5 — use analogies and everyday language
   - **Technical**: Precise explanation with proper terminology
   - **Example**: Concrete example or code snippet demonstrating the concept
4. If explaining code:
   - Use `file_read` to load the code if a path is given
   - Walk through the logic step by step
   - Highlight non-obvious parts
5. If explaining an error:
   - Identify the root cause
   - Explain why it happened
   - Provide the fix
