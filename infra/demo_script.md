# Close Call — three-minute demo and recording checklist

Status: script prepared; no video recorded. Planned script follows `shared/PLAN.md`.
Use verified examples and real results only. If only synthetic fixtures are available,
label the recording as a UI prototype and omit performance claims.

## 0:00–0:30 — Problem and headline

“Stale bots measure inactivity. They do not know whether maintainers still want a
contribution. Close Call checks evidence before recommending closure.”
Show [real wrongful count / eligible N], repository names, and “inferred from later
events.” If results are unavailable, say evaluation is pending and omit the number.

## 0:30–1:30 — Three audits

Use three preselected real PRs and show each source permalink and close timestamp:
- CONFIRMED: verified evidence of abandonment, rejection, or supersession.
- UNSUPPORTED: verified evidence that the work was wanted. Show an actually rejected
  model claim and its failed check only if one was observed; do not stage a failure
  and present it as measured behavior.
- ESCALATE: conflicting, insufficient, or security-sensitive evidence; human decides.

Explain that future outcome labels were not provided to the model. Do not expose
sensitive PR content or run code from any PR. If using recorded output rather than
live inference, state that clearly.

## 1:30–2:15 — Results

Show stale bot, metadata heuristic, and Close Call on the same evaluation subset.
Read recall, UNSUPPORTED precision, escalation rate, and claim rejection counts.
Show denominators and undefined values honestly. Mention 30 hand reviews only once
completed; otherwise state the actual completed count. Keep fixtures out of results.

## 2:15–2:45 — Local use and skill

Show Ollama and the exact tested model tag, then the AI owner's verified skill
installation command once available. No guessed command: if the skill has not
shipped, show the working entry point and call skill packaging pending. Say Apache
2.0 only after checking the exact model license. Code is MIT under root LICENSE.

## 2:45–3:00 — Limits

“Inferred outcomes, a small sample, and incomplete historical records limit our
conclusions. Matching a quote does not prove an interpretation. Close Call advises;
a maintainer decides. It never acts on a PR.”

## Recording and submission handoff

- Draft recording: Emmanuel shares screen and narrates after labeling with Nilesh.
- Final window in Allen's plan: 5:45–6:15 PM, submit by 6:15 PM. Confirm event
  date/timezone and official cutoff before scheduling; the email does not specify them.
- Before recording: use real data, hide credentials/notifications, check audio,
  readable text, and consistent demo state; keep a local backup of evaluated outputs.
- Record using the team's available screen recorder; capture narration and export
  a playable video within the event's duration/format requirements.
- Watch the entire export, verify audio and text, upload, and test signed-out access.
- Add the final video URL to `infra/devpost.md`; verify final metrics and track
  eligibility, submit in the authenticated Devpost session, and retain confirmation.

Pending handoff: real examples/results, tested skill command, recorder/operator,
public video URL, and submission confirmation. No recording or submission claimed.
