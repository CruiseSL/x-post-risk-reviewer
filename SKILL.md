---
name: x-post-risk-reviewer
description: Review draft X posts for likely X Rules, visibility, and account-risk issues. Use for post preflight, batch review, compliant rewrites, and posting-plan risk. Never claim to guarantee reach, prevent suspension, bypass detection, or reverse-engineer X systems.
---

# X Post Risk Reviewer

Review draft X posts as a compliance preflight, not enforcement evasion.

## Modes

Single post, batch, compliant rewrite, or posting-plan audit.

## Workflow

1. Parse input into stable post IDs. If none exist, assign `post_001`, `post_002`, etc.
2. Identify available context: post type, targets, protected-class references, media, links, account count, schedule, geography, reply/quote status, and automation.
3. Read `references/review-playbook.md`.
4. For local batch files, prefer `scripts/moderate_posts.py --provider rules`; use `openai`, `detoxify`, or `cardiff-offensive` only after user approval. Provider flags are signals, not final decisions.
5. Review each post and batch patterns: duplicates, link-only runs, hashtag stuffing, mass mentions/replies, coordination, repeated deletes/edits.
6. Read `references/output-schema.md` and return the required format.

## Output Contract

Always include:

- a short best-effort disclaimer, not a guarantee from X
- a per-post table with `id`, `risk`, `policy_areas`, `why`, and `recommended_action`
- `human_review_required` flags for high-risk, ambiguous, legal, election, self-harm, privacy, or media-consent cases
- compliant rewrites when requested, without obfuscation or evasion tactics
- in batch mode, a `batch_pattern_risk` section
- a `signals_used` section naming policy, media, link, and signal-runner coverage

## Safety Boundaries

Do not help users evade enforcement. Refuse requests to:

- hide a violating message with misspellings, symbols, code words, image text, or translation tricks
- probe thresholds, classifiers, or ranking behavior
- plan ban evasion, coordinated amplification, fake engagement, or duplicate reporting
- preserve threats, harassment, doxxing, hateful attacks, non-consensual intimate content, scams, or illegal facilitation in disguised form

Offer compliant alternatives: remove the issue, add context, de-target individuals, remove private data, label media, cite sources, or do not post.

## Reference Map

- Read `references/review-playbook.md` for checks, links, and refusal rules.
- Read `references/output-schema.md` before producing user-facing reports.
- Use `scripts/moderate_posts.py` for local JSON, JSONL, or CSV drafts. Default to `--provider rules`; use API/model providers only with user approval.
- Use `evals/evals.json` for route checks before changing this skill.
