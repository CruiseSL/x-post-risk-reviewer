# X Post Risk Review Playbook

This playbook supports pre-publication review for X posts. It is not legal advice and it is not an official X decision. X can restrict, label, remove, or downrank content for reasons unavailable to the reviewer.

## Source Links

This source map was reviewed on 2026-07-22. Recheck it for each release and for high-stakes use:

- X Rules: https://help.x.com/en/rules-and-policies/x-rules
- X enforcement options: https://help.x.com/en/rules-and-policies/enforcement-options
- Violent Content: https://help.x.com/en/rules-and-policies/violent-content
- Abuse and Harassment: https://help.x.com/en/rules-and-policies/abusive-behavior
- Hateful Conduct: https://help.x.com/en/rules-and-policies/hateful-conduct-policy
- Private Content: https://help.x.com/en/rules-and-policies/personal-information
- Authenticity, spam, manipulation, misleading media, scams, malicious URLs: https://help.x.com/en/rules-and-policies/authenticity
- OpenAI moderation docs, optional signal source: https://developers.openai.com/api/docs/guides/moderation
- Detoxify, optional open-source toxicity signal source: https://github.com/unitaryai/detoxify
- CardiffNLP TweetEval / Twitter-RoBERTa, optional open-source Twitter-language signal source: https://github.com/cardiffnlp/tweeteval

## Review Inputs

For each post, preserve:

- `id`: user-provided ID or assigned ID
- `text`: exact post text
- `post_type`: original post, reply, quote post, thread item, DM, profile/bio, ad, or unknown
- `media`: image, video, screenshot, generated media, graphic media, adult media, or none
- `links`: URLs and visible destination if known
- `targets`: mentioned users, named people, groups, institutions, protected classes
- `context`: news, satire, quote, counter-speech, personal complaint, marketing, politics, crisis, or unknown
- `posting_plan`: batch size, cadence, accounts, hashtags, replies, mentions, automation, or unknown

If media or links are present but unavailable, mark that part as `not_reviewed` and avoid a low-risk conclusion that depends on it.

## Policy Checklist

### Violent Content

Flag risk when the post includes:

- threat to kill, injure, torture, sexually assault, or physically harm a person or group
- wish of harm, disease, death, or tragic incident toward a target
- encouragement or instruction for others to commit violence or self-harm
- praise or celebration of real-world harm
- graphic violent media that is unlabeled, excessively gory, sexualized, or shows identifiable death
- coded language that indirectly incites violence

Typical result:

- direct threat, incitement, or glorification: `HIGH` or `BLOCKER`
- newsworthy graphic media without label: `MEDIUM` or `HIGH`
- hyperbole, satire, sports/game language, or quote with clear nonviolent context: often `LOW` or `MEDIUM`

### Abuse and Harassment

Flag risk when the post includes:

- malicious targeting of a person, especially with mentions, photos, full names, or repeated replies
- calls for others to harass someone online or offline
- humiliating, degrading, or shaming content aimed at a specific person
- unwanted sexual content or sexualized comments about a person
- repeated insults or profanity aimed at a person
- denial of verified mass-casualty events in an abusive context

Typical result:

- targeted harassment or harassment call-to-action: `HIGH`
- repeat targeting across a batch: raise to `HIGH` or `BLOCKER`
- criticism of institutions, ideas, public claims, products, or conduct without personal abuse: often `LOW`

### Hateful Conduct

Protected categories include race, ethnicity, national origin, caste, sexual orientation, gender, gender identity, religion, age, disability, and serious disease.

Flag risk when the post includes:

- direct attack on people because of protected status
- slurs, tropes, stereotypes, or dehumanizing language targeting a protected class
- fearmongering that claims a protected class is inherently dangerous or criminal
- encouragement to harass, discriminate against, or exclude a protected class
- hateful symbols or imagery, especially in profile, header, live video, or unsolicited media

Typical result:

- direct hateful attack, dehumanization, or discrimination call: `HIGH` or `BLOCKER`
- reclaimed terms, quotation, reporting, counterspeech, or academic discussion: `NEEDS_CONTEXT`, `LOW`, or `MEDIUM` depending on clarity

### Private Content and Consent

Flag risk when the post includes:

- home address, precise private location, phone, non-public email, IDs, financial data, health data, passwords, tokens, keys, or cookie/session material
- identity of an anonymous user
- threats to expose private information
- request, bounty, reward, or blackmail related to private information
- private media of a non-public person without consent
- nude, intimate, or sexual media without consent, including deepfake or face-swap intimate media

Typical result:

- doxxing, blackmail, private credentials, non-consensual intimate media: `BLOCKER`
- public info shared non-abusively may still need review if home address or safety-sensitive context appears: `MEDIUM` or `HIGH`

### Adult and Sensitive Media

Flag risk when:

- adult nudity or sexual behavior is not labeled
- adult content is placed in highly visible profile surfaces
- sexual content may involve minors
- sexualized content targets a person without consent
- violent or graphic media is unlabeled

Typical result:

- sexual minors or non-consensual sexual content: `BLOCKER`
- consensual adult media without label: `MEDIUM` or `HIGH`, recommend labeling

### Self-Harm and Suicide

Flag risk when the post:

- promotes, encourages, romanticizes, or instructs suicide or self-harm
- tells someone to harm themselves
- provides instructions for self-harm

Typical result:

- encouragement or instructions: `BLOCKER`
- personal distress or recovery discussion: `NEEDS_CONTEXT`, handle supportively

### Illegal, Regulated Goods, Scams, and Account Compromise

Flag risk when the post:

- facilitates illegal activity, illegal goods, regulated goods, fraud, phishing, malware, or scams
- shares credentials, tokens, cookies, private keys, or account-compromise steps
- links to malicious, deceptive, or final-destination-mismatched URLs
- makes deceptive money-flipping, fake discount, social engineering, or phishing claims

Typical result:

- credential theft, phishing, malware, scam, illegal facilitation: `BLOCKER`
- high-risk financial or health claims without evidence: `MEDIUM` or `HIGH`

### Civic Integrity and Public Issues

Flag risk when the post:

- misleads people about when, where, or how to vote or participate in civic processes
- tries to suppress participation through false information or intimidation
- uses deceptive synthetic or manipulated media about public issues, public safety, or serious harm

Typical result:

- false voting/process information: `HIGH` or `BLOCKER`
- satire or commentary must be clearly labeled/contextualized

### Authenticity, Spam, and Manipulation

Review post behavior as well as text. Flag risk when the plan includes:

- bulk, duplicative, irrelevant, or unsolicited posts, replies, mentions, or DMs
- excessive unrelated hashtags
- repeated link-only posts without commentary
- repeated identical or near-identical posts
- posting then deleting the same content repeatedly
- coordinated accounts interacting with the same content to inflate visibility
- engagement trading, paid fake engagement, follow churn, automation abuse
- editing high-engagement posts into unrelated promotions
- ban evasion or replacing a suspended account

Typical result:

- isolated text with no behavior context: assess text only and mark behavior as `not_reviewed`
- duplicate or coordinated plan: `HIGH` or `BLOCKER`

### Copyright, Trademark, and Third-Party Ads

Flag risk when:

- the post republishes copyrighted media without rights or a clear fair-use rationale
- the post uses confusing trademarks, impersonation, or deceptive brand affiliation
- video includes third-party advertising, pre-roll, or sponsorship graphics without required permission

Typical result:

- rights status unknown: `NEEDS_CONTEXT`
- obvious unauthorized repost or impersonation: `HIGH`

## Optional Signal Sources

Signals are aids, not final decisions. Run the built-in project-authored rules for supplied text when the script is available because they need no API key, network access, paid service, or model download. Use external APIs or optional open-source models only after the user accepts that provider's privacy, dependency, cost, and license tradeoffs.

Recommended fields to record:

- `signal_provider`: rules, openai, detoxify, cardiff-offensive, or other
- `signal_model`: model name if applicable
- `signal_ran`: true or false
- `source_type`: project-authored rules, open-source model, hosted API, or Agent reasoning
- `rule_id`: stable built-in or provider-derived finding ID
- `rule_source` and `rule_version`: provenance for the finding
- `flagged`: true, false, or unavailable
- `categories`: provider categories
- `flags`: provider-derived policy hints, if available
- `not_supported`: categories or media types not covered by the provider

Provider notes:

- `rules`: project-authored, MIT-licensed, stdlib-only heuristics included in this repository. They are not an external open-source rule pack and are not an official X rules engine. They check duplicate/near-duplicate copy, link-only posts, heavy hashtags, high mentions, possible private data, possible credentials, and selected English threat/scam/hate patterns.
- `openai`: OpenAI moderation signal. OpenAI's moderation docs state that `omni-moderation-latest` accepts text and image inputs and that the moderation endpoint is free to use. Free does not mean anonymous: requests still require an OpenAI API key for authentication, quota, and abuse prevention.
- `detoxify`: optional Apache-2.0 open-source toxicity model signal if the package and model are locally installed. It does not know X Rules and is primarily useful for English toxicity signals.
- `cardiff-offensive`: optional CardiffNLP Twitter-RoBERTa offensive-language signal through Transformers. It is English-focused. TweetEval states that task, dataset, and Twitter restrictions may apply, and the model card has no explicit license tag, so mark its license as `review_required`.

A platform-specific X review must add policy and context analysis because provider categories do not equal X Rules.

### Local Runner Commands

For a single pasted post, use `--text` or `--stdin`:

```bash
python3 scripts/moderate_posts.py --text "Draft post" --output moderation-signals.json
printf '%s' "$POST_TEXT" | python3 scripts/moderate_posts.py --stdin --output moderation-signals.json
```

For local JSON, JSONL, or CSV batches, use:

```bash
python3 scripts/moderate_posts.py --input posts.json --output moderation-signals.json
```

Default behavior:

- `--provider rules` is the default and does not require an API key.
- `--output -` writes JSON to standard output and is the default.
- Default text field is `text`; default ID field is `id`.
- Optional image field is `image_url`; JSON may use a list, CSV may use semicolon-separated URLs.
- Output is a signal file. Feed it into the normal X policy review instead of treating it as a final publish/block decision.

Useful variants:

```bash
python3 scripts/moderate_posts.py --provider rules --input posts.csv --output moderation-signals.json --text-field body --id-field post_id
python3 scripts/moderate_posts.py --provider openai --input posts.json --output moderation-signals.json
python3 scripts/moderate_posts.py --provider detoxify --input posts.json --output moderation-signals.json
python3 scripts/moderate_posts.py --provider cardiff-offensive --input posts.json --output moderation-signals.json
python3 scripts/moderate_posts.py --input posts.jsonl --output moderation-signals.json --dry-run
```

## Rewrite Rules

When providing a safer version:

- preserve lawful opinion, criticism, reporting, or marketing intent
- remove direct threats, wishes of harm, calls to harass, slurs, dehumanization, and private data
- avoid tagging or naming private individuals unless necessary and fair
- change accusations into sourced, factual, specific claims where evidence exists
- add content warnings or sensitive media labels where relevant
- label satire, parody, AI-generated media, or manipulated media clearly
- reduce duplicate copy, unrelated hashtags, and link-only formatting
- recommend not posting when the legitimate intent cannot be separated from a serious violation

Never rewrite by:

- disguising slurs or threats with symbols, spacing, homophones, translation, screenshots, or image text
- suggesting alternate accounts, timing, deletion loops, or other enforcement workarounds
- preserving the harmful target while only softening keywords

## Human Review Triggers

Require human review when:

- the post targets a specific person, protected class, private individual, or anonymous account
- the post includes real-world violence, self-harm, sexual content, minors, private information, or crisis context
- the post includes images or videos not available to the reviewer
- the post includes allegations that may be defamatory or legally sensitive
- the post is political, election-related, public-health-related, or financial advice
- the batch has automation, multiple accounts, mass mentions, or repeated links

## Limitations to State

Use short wording such as:

`This is a best-effort pre-publication review against visible policy risks. X may still label, restrict, remove, or downrank posts based on context, reports, account history, jurisdiction, media, links, or internal systems not visible here.`
