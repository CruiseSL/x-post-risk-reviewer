# Output Schema

Use this decision-oriented format. Keep obvious `PASS` results short; add detail only for material findings.

## Summary

```markdown
This is a best-effort pre-publication review, not an official X decision.

Decision: <PASS|REVISE|STOP|NEEDS_CONTEXT>
Action: <publish as written|make listed changes|do not post as written|provide material context>
Confidence: <high|medium|low>
Human review required: <yes|no>
Material findings: <number>
```

Decision mapping:

- `PASS`: no material issue found in the supplied content
- `REVISE`: a specific, removable issue exists
- `STOP`: serious or repeated risk makes the draft unsuitable as written
- `NEEDS_CONTEXT`: missing facts could change the decision

## Per-Post Results

```markdown
| id | decision | policy risk | evidence | action | confidence |
|---|---|---|---|---|---|
| post_001 | PASS | None found in supplied text | No material policy issue identified | Publish as written | high |
```

For `PASS`, do not manufacture writing advice, rewrites, or missing-context warnings. Mention absent media, links, or posting-plan data only when the draft or user says those elements exist or the omission could change the result.

## Material Findings

Add one block per finding for `REVISE`, `STOP`, or `NEEDS_CONTEXT`:

```markdown
### finding_001

- Post: post_001
- Evidence: "<short exact phrase or measurable pattern>"
- Policy mapping: <policy area and public policy source>
- Source: <rule_id and project_authored_rules | open_source_model | hosted_api | agent_reasoning>
- Confidence: <high|medium|low|provider_reported>
- Plausible consequence: <removal|reach restriction|interaction restriction|account challenge|suspension risk|context-dependent>
- Action: <specific corrective action>
```

Use source labels precisely:

- X policy pages are `public_policy`, not open-source detectors.
- `builtin.*` rules are `project_authored_rules` under this repository's MIT license.
- Detoxify and CardiffNLP are `open_source_model` signals only when they actually ran.
- OpenAI Moderation is a `hosted_api`, not open source.
- Contextual Agent conclusions are `agent_reasoning`, not deterministic rules.

Provide a compliant rewrite only when the decision is `REVISE` or `STOP` and a legitimate intent remains. Never add a rewrite to fill space.

## Detector Trace

Always include the actual execution trace:

```markdown
## Detector Trace

| component | source type | version/model | status | findings | limits |
|---|---|---|---|---|---|
| X policy map | public_policy | reviewed YYYY-MM-DD | referenced | n/a | Not an official X decision |
| Built-in heuristics | project_authored_rules | 2.0.0 | ran | 0 | Text and structural patterns only |
| Detoxify | open_source_model | original | not_run | n/a | Optional; primarily English |
| CardiffNLP offensive | open_source_model | model name | not_run | n/a | Optional; English; license review required |
| OpenAI Moderation | hosted_api | model name | not_run | n/a | Optional third-party service |
| Agent semantic review | agent_reasoning | runtime model | ran | 0 | Context-dependent and non-deterministic |
```

Then state explicitly:

```markdown
External open-source components used: <none|comma-separated detector IDs>
Project-authored components used: <none|comma-separated detector IDs>
Hosted APIs used: <none|comma-separated detector IDs>
```

Never say a provider was used when its status is `not_run`, `unavailable`, `error`, or `pending_agent_review`.

## Batch Pattern Risk

For more than one post, add exact and near-duplicate groups, link-only repetition, hashtag and mention concentration, multi-account or automation context, and cadence. State whether account-level behavior changes any per-post decision.

## Refusal

If the user requests evasion, explain that the Skill can remove the violating element but cannot disguise it or bypass enforcement. Offer a compliant version only when the legitimate message can be separated from the harmful content.
