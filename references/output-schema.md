# Output Schema

Use this format for both single-post and batch reviews.

## Required Summary

```markdown
This is a best-effort pre-publication review, not a guarantee from X.

Overall: <LOW|MEDIUM|HIGH|BLOCKER|NEEDS_CONTEXT>
Human review required: <yes|no>
Main reason: <one sentence>
```

## Per-Post Table

```markdown
| id | risk | policy_areas | why | recommended_action |
|---|---|---|---|---|
| post_001 | MEDIUM | authenticity_spam, links_not_reviewed | Link-heavy post with limited context; destination not reviewed. | Add context, verify URL, avoid duplicate posting. |
```

Risk values:

- `LOW`
- `MEDIUM`
- `HIGH`
- `BLOCKER`
- `NEEDS_CONTEXT`

Policy area values may include:

- `violent_content`
- `abuse_harassment`
- `hateful_conduct`
- `private_content`
- `nonconsensual_intimate_content`
- `adult_sensitive_media`
- `self_harm`
- `illegal_regulated_goods`
- `scam_phishing_malware`
- `civic_integrity`
- `authenticity_spam`
- `misleading_media`
- `malicious_urls`
- `copyright_trademark`
- `third_party_video_ads`
- `account_behavior`
- `media_not_reviewed`
- `links_not_reviewed`
- `needs_context`

## Per-Post Detail

Use detail blocks for any item rated `MEDIUM` or above.

```markdown
### post_001

Risk: HIGH
Human review required: yes
Policy areas: abuse_harassment, violent_content
Evidence:
- Directly targets a named person.
- Includes a wish of physical harm.

Recommended action:
- Do not post as written.
- Remove the harm language and restate as criticism of the action or claim.

Compliant rewrite:
> <rewrite here>
```

Do not quote more of a risky post than necessary. Paraphrase when possible.

## Batch Pattern Risk

Include this section when reviewing more than one post.

```markdown
## Batch Pattern Risk

- Duplicate or near-duplicate copy: <none|low|medium|high>
- Link-only repetition: <none|low|medium|high|not_reviewed>
- Hashtag risk: <none|low|medium|high>
- Mention/reply targeting risk: <none|low|medium|high|not_reviewed>
- Multi-account or automation risk: <none|low|medium|high|not_reviewed>
- Schedule/cadence risk: <none|low|medium|high|not_reviewed>
```

Then add one sentence explaining whether account-level risk is higher than the per-post table suggests.

## Signals Used

Always include:

```markdown
## Signals Used

- X policy checklist: used
- Media review: <used|not_provided|not_reviewed>
- Link review: <used|not_provided|not_reviewed>
- Signal runner: <rules|openai/model|detoxify/model|cardiff-offensive/model|not_available|not_requested>
- Signal runner limits: <short note, e.g. local rules only; images not inspected; URLs not visited>
- Posting-plan review: <used|not_provided|not_reviewed>
```

## Refusal Format

If the user asks for evasion tactics:

```markdown
I can help make the post compliant, but I cannot help disguise violating content or bypass X enforcement. The safer path is to remove the violating element: <specific issue>. A compliant version would be:

> <rewrite>
```
