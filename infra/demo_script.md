# Close Call — final three-minute demo

Prepared script only; no video recorded by this agent. Emmanuel records, uploads
unlisted to YouTube and submits the Devpost entry with all four teammates and both
Open-Source AI and Best Use of Gemma 4 selected. Confirm final track requirements.

## 0:00–0:25 — Problem and headline

“Inactivity is not proof that a contribution is unwanted. In 25 stale-bot closures
in Jest with complete follow-up windows, 5 were later redone: 20%, under our inferred
label definition. Close Call checks evidence before recommending closure.”
Show jestjs/jest, the sample size, inferred-label caveat and 180-day eligibility.

## 0:25–1:20 — Live jest#15880

Lio fetches the PR; Nilesh runs Close Call via the Gemini API, using their working
authenticated terminals. From the repository root:

```bash
python3 backend/data/fetch_pr.py jestjs/jest 15880 > /tmp/close-call-demo-pr.jsonl
python3 ai/closecall/run.py /tmp/close-call-demo-pr.jsonl --backend gemini --output /tmp/close-call-demo-audit.jsonl
```

Show the source PR and the verified pre-close review request, then the result.
The saved runs both return ESCALATE: say “It refused to approve closure and sent
this case to a human.” Do not promise that a fresh stochastic run must match.
If rate limits or credentials block the live call, show the committed saved audit
and explicitly call it a saved run. Never show keys or execute PR code.

## 1:20–1:55 — jest#15877: interpretation still matters

Show saved hosted Gemma 4 26B UNSUPPORTED versus local Gemma 4 E2B CONFIRMED.
Both have verified quotations. Explain that the verifier checks quotation/source
matching, not whether the interpretation is sound. No cross-model adjudicator is
implemented. Human review is required; no_evidence does not prove justified closure.

## 1:55–2:35 — Results page

Stale bot let all 5 inferred wrongful closures through; Close Call approved 0 and
escalated all 5. Both models escalate 88% of the 25 eligible cases, so review burden
remains high. These escalations are not positive UNSUPPORTED detections.
The local model's verifier rejected 21 of 148 citations across all 42 audits;
these are citation failures, not proof of fabrication.

On 24 human-labeled PRs, hosted Close Call matched 15 labels. All 7 confident human
cases were escalated. Its 2 confident verdicts were on human-uncertain cases.
Describe agreement, never accuracy; show the confusion table if time permits.
Only 2 human-human pairs remain, with 1 agreement: too small to interpret.

## 2:35–3:00 — Limits and close

“One repository, small n, inferred later-event labels and substantial escalation
limit our conclusions. Lio's assisted labels are excluded from the answer key;
Emmanuel saw AI suggestions. Matching a quote does not settle interpretation.
Close Call advises, never acts.”

## Recording and submission

- Rehearse with Lio and Nilesh and check that the viewer displays the merged real data.
- Record screen and narration, hide credentials/notifications, and keep text readable.
- Watch the exported video all the way through; check audio, duration and legibility.
- Upload unlisted to YouTube and test the link signed out.
- Paste the video URL and write-up into Devpost; add Allen, Emmanuel, Lio and Nilesh.
- Select Open-Source AI and Best Use of Gemma 4. Verify source/video links and submit
  by the team's 6:15 PM target, then retain the submission confirmation.

The team's recording window is 5:45–6:10 PM. These are team target times, not a
verified event cutoff. No upload, teammate addition or submission is claimed here.
