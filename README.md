# X Post Risk Reviewer

Review draft X posts as a decision gate before publishing. The Skill returns `PASS`, `REVISE`, `STOP`, or `NEEDS_CONTEXT` and shows the evidence, policy mapping, detector source, confidence, and actual execution trace behind the result.

## Install

Install directly from GitHub for Codex:

```bash
git clone https://github.com/CruiseSL/x-post-risk-reviewer.git ~/.codex/skills/x-post-risk-reviewer
```

Or install it for a project-level Agent skills directory:

```bash
mkdir -p .agents/skills
git clone https://github.com/CruiseSL/x-post-risk-reviewer.git .agents/skills/x-post-risk-reviewer
```

You can also copy this whole directory into your agent's skills directory.

Example paths:

```text
~/.codex/skills/x-post-risk-reviewer/
.agents/skills/x-post-risk-reviewer/
```

Then use a prompt like:

```text
Use $x-post-risk-reviewer to review these draft X posts before publishing.

Context:
- Account type:
- Region:
- Posting plan:
- Any media or links:

Posts:
1. ...
2. ...
3. ...
```

For batch review, include IDs if you have them:

```text
Use $x-post-risk-reviewer for this batch. Keep the IDs in your output and tell me the per-post risk plus batch-pattern risk.

post_001: ...
post_002: ...
post_003: ...
```

For an ordinary low-risk text post, the expected result is deliberately short: `PASS`, publish as written, no manufactured rewrite, and a trace showing what actually ran. Detailed findings appear only when there is a material issue.

This Skill helps reduce visible policy and enforcement risk. It does not guarantee reach, ranking, publication, or account safety, and it must not be used to disguise violating content.

## What It Reviews

- likely X Rules concerns in each draft
- privacy, harassment, hateful-conduct, violent-content, and authenticity risks
- batch patterns such as repeated copy, mass mentions, link-only runs, and coordinated posting signals
- whether context, media consent, legal review, or human review is still required
- compliant rewrites that remove the risky element instead of disguising it

## Optional Signal Runner

The default `rules` provider contains project-authored MIT-licensed heuristics. It is not an external open-source rule pack and it is not an official X rules engine. It needs no API key, network access, paid API, or model download.

For one post:

```bash
python3 scripts/moderate_posts.py --text "Draft post" --output moderation-signals.json
```

For local batch files:

```bash
python3 scripts/moderate_posts.py --input posts.json --output moderation-signals.json
```

Equivalent explicit form:

```bash
python3 scripts/moderate_posts.py --provider rules --input posts.json --output moderation-signals.json
```

The built-in provider evaluates 14 named rules covering duplicate copy, near-duplicates, link-only posts, heavy hashtags, mass mentions, possible private data, possible credentials, and selected English threat/scam/hate patterns. Every finding includes a stable `rule_id`, evidence, source type, version, and confidence. It does not inspect image pixels, final URL destinations, account history, or nuanced multilingual context.

Supported input formats: `.json`, `.jsonl`, `.csv`.

Default fields:

- `id`
- `text`
- optional `image_url`

The JSON output includes `policy_sources`, `detector_execution`, per-post `detector_trace`, and explicit lists of open-source, project-authored, and hosted components that actually ran. Paste or attach it to the Agent with the original drafts and ask it to continue with `$x-post-risk-reviewer`.

The full detector, source, version, license, language, and limitation registry is in [`references/detector-registry.json`](references/detector-registry.json).

Dry-run parsing check:

```bash
python3 scripts/moderate_posts.py --input examples/posts.sample.json --output /tmp/moderation-signals.sample.json --dry-run
```

### Optional Providers

OpenAI moderation signal:

```bash
python3 scripts/moderate_posts.py --provider openai --input posts.json --output moderation-signals.json
```

OpenAI's moderation endpoint is free to use according to OpenAI's docs, but it is not anonymous: the request still needs an OpenAI API key for authentication, quota, and abuse prevention. This is not an X API key. Only run this on drafts you are allowed to send to the moderation API.

Or keep the key in a temporary file outside the package:

```bash
python3 scripts/moderate_posts.py --provider openai --input posts.json --output moderation-signals.json --api-key-file /tmp/openai_api_key
```

Open-source model signals are optional and require local dependencies:

```bash
python3 scripts/moderate_posts.py --provider detoxify --input posts.json --output moderation-signals.json
python3 scripts/moderate_posts.py --provider cardiff-offensive --input posts.json --output moderation-signals.json
```

Detoxify is Apache-2.0 and primarily provides English toxicity signals. CardiffNLP is English-focused; TweetEval says task, dataset, and Twitter restrictions may apply, while the model card has no explicit license tag, so this project records it as `review_required`. Neither provider is an X policy engine. They may require Python packages, local model files, CPU/GPU time, and privacy/license review. The CardiffNLP adapter uses cached model files by default; pass `--allow-model-download` only if downloading model weights is acceptable.

Custom CSV fields:

```bash
python3 scripts/moderate_posts.py --provider rules --input posts.csv --output moderation-signals.json --text-field body --id-field post_id
```
