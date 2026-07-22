---
name: x-post-risk-reviewer
description: Review draft X posts and posting plans as a pre-publication decision gate. Use for single posts, batches, replies, links or media context, policy and account-behavior risk, and compliant rewrites. Return PASS, REVISE, STOP, or NEEDS_CONTEXT with evidence and detector provenance. Do not use for generic copywriting or enforcement evasion.
---

# X Post Risk Reviewer

Provide a best-effort compliance preflight, not an official X decision.

## Workflow

1. Preserve post IDs or assign `post_001`, `post_002`, and so on.
2. When shell access exists, run `scripts/moderate_posts.py --provider rules` for supplied text. Use `--text` or `--stdin` for one post and `--input` for JSON, JSONL, or CSV.
3. Read `references/detector-registry.json`. Keep public X policies, project-authored rules, optional open-source models, hosted APIs, and Agent reasoning separately labeled.
4. Read `references/review-playbook.md`. Review only material context: targets, media, links, accounts, cadence, geography, reply or quote status, and automation.
5. Read `references/output-schema.md` and return its decision-oriented format. Provider signals are evidence, not final decisions.

## Decisions

- `PASS`: publish as written. Do not invent rewrites or style advice.
- `REVISE`: cite the removable issue and give the smallest compliant change.
- `STOP`: explain the serious issue that makes the draft unsuitable as written.
- `NEEDS_CONTEXT`: request only missing facts that could change the decision.

Every finding needs evidence, policy mapping, source, confidence, plausible consequence, and action. Do not use `needs_context` as a generic policy area.

## Provenance

Always show policy review date and each detector's source type, version or model, status, matched rule IDs, and limits. List an external open-source component as used only when it actually ran.

## Safety

Do not help hide violations, probe enforcement thresholds, evade suspensions, coordinate harassment or fake engagement, or disguise threats, hate, doxxing, scams, illegal facilitation, or non-consensual intimate content. Remove the harmful element, add truthful context, reduce manipulative behavior, or recommend not posting.

## Resources

- `references/detector-registry.json`: source and license registry
- `references/review-playbook.md`: policy checks
- `references/output-schema.md`: report contract
- `evals/evals.json`: behavior checks
