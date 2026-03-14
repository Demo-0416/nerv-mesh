---
name: bootstrap
description: "Initialize SOUL.md and USER.md through an interactive conversation. Use when: first launch, user says 'bootstrap', 'initialize', 'set up memory', 'who am I', 'configure identity', or when SOUL.md/USER.md are empty or contain default placeholder text."
version: 0.1.0
tags: [memory, setup, identity]
---

# Bootstrap — Initialize Agent Identity & User Profile

This skill guides the agent through setting up SOUL.md and USER.md via a natural conversation. It should feel like a first meeting, not a form to fill out.

## When to Trigger

- First launch (SOUL.md or USER.md contain placeholder text like "unknown" or "to be discovered")
- User explicitly asks to set up identity or profile
- User says "bootstrap", "initialize", or "let's get to know each other"

## Process

### Phase 1: Read Current State

1. Use `memory_read` to check SOUL.md and USER.md
2. If both are already filled with real content, tell the user and ask if they want to update anything
3. If either contains placeholders, proceed to Phase 2

### Phase 2: Get to Know the User (USER.md)

Have a natural conversation. Do NOT dump all questions at once. Ask 1-2 questions, wait for answers, then follow up based on what they said.

**Round 1 — Who are you?**
- What's your name?
- What do you do? (role, profession, or however they want to describe themselves)

**Round 2 — How do you work?**
- What are you currently working on?
- What kind of tasks will you mainly use me for?

**Round 3 — Preferences**
- How do you like to communicate? (concise vs detailed, formal vs casual)
- Any specific things I should know about how you work?

Adapt based on their answers — if they're a developer, ask about tech stack. If they're a researcher, ask about their field. Be curious, not mechanical.

### Phase 3: Define the Agent (SOUL.md)

Based on what you learned about the user, propose an agent identity that fits them:

- **Identity**: What kind of assistant would be most useful to this specific user?
- **Tone**: Match the user's communication style
- **Principles**: What should the agent prioritize? (efficiency? thoroughness? creativity?)
- **Boundaries**: What should the agent avoid or be careful about?

Present the proposed SOUL.md to the user and ask for confirmation or adjustments.

### Phase 4: Write and Confirm

1. Use `memory_update` to write USER.md with the collected user profile
2. Use `memory_update` to write SOUL.md with the agreed identity
3. Show the user a summary of what was saved
4. Tell them they can update these anytime by saying "update my profile" or "update your identity"

## Writing Guidelines

**USER.md format** — Dense, telegraphic. No filler words. Bold section titles. Prioritize information density:

```markdown
# USER.md

**Who**: Name, role, one-line description.
**Goals**: What they're trying to accomplish.
**Preferences**: Communication style, language, work habits.
**Context**: Current projects, tech stack, domain expertise.
**Constraints**: Things to avoid, sensitivities.
```

**SOUL.md format** — Concise agent identity card:

```markdown
# SOUL.md

**Identity**: One-line role definition tailored to this user.
**Tone**: Communication style (direct/casual/formal/etc.).
**Principles**: 3-5 guiding rules for behavior.
**Growth**: How to improve over time with this user.
```

## Important

- Keep both files under 500 words each — they're loaded into every prompt
- Be warm and curious during the conversation, not robotic
- If the user gives short answers, that's fine — respect their style
- The goal is a useful profile, not an interrogation
