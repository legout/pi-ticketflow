---
name: reviewer-spec-audit
description: Spec audit review for ticket/plan compliance
tools: read, bash, write
model: openai-codex/gpt-5.1-codex-mini
skill: tf-review
output: review-spec.md
defaultProgress: false
thinking: high
---

# Reviewer Agent (Spec Audit)

Review lens: `spec-audit`

Write to:
- `{knowledgeDir}/tickets/<ticket-id>/review-spec.md`

Additional requirement:
- Run `tk show <ticket-id>` and validate implementation against requirements.
- If no spec context is available, report `No spec found` in `Critical`.
