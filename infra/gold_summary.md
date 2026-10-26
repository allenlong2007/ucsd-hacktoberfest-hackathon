# Human label summary

30 PRs and all 35 submitted entries remain in the CSV for audit. Nine entries from
Lio are AI-assisted and excluded from the answer key. This leaves **24 PRs with
26 human-source entries from Allen, Emmanuel and Nilesh**. Slots 7, 11, 15, 19,
23, 27 have no human-source label and are excluded. Source labels, reviewers and
explanations are unchanged; only derived final labels are recalculated after filtering.

## Human-human agreement

**1 of 2 agreed (too small to interpret).** The human-human pairs are slots 10
(disagreed) and 24 (agreed). Slots 3, 17 and 30 retain only their human-source entry
and do not count as double-human reviews. Slot 17's derived final label is now
JUSTIFIED, following Allen's unchanged label; Lio's conflicting label is excluded.

## Human label vs inferred outcome — counts only

| human_label | redone_later | no_evidence |
| --- | ---: | ---: |
| JUSTIFIED | 0 | 3 |
| NOT_JUSTIFIED | 2 | 2 |
| UNCERTAIN | 3 | 14 |

`no_evidence` means no later redo was found; it does not mean justified closure.
The original 30-PR sample included all 5 inferred redone_later cases plus 25 others
from 42 Jest PRs; excluding AI-assisted-only rows does not create a representative
population sample.

## Human label vs AI suggestions — counts only

Columns are **AI suggestions, not ground truth**.

| human_label | JUSTIFIED | NOT_JUSTIFIED | UNCERTAIN |
| --- | ---: | ---: | ---: |
| JUSTIFIED | 1 | 0 | 2 |
| NOT_JUSTIFIED | 0 | 4 | 0 |
| UNCERTAIN | 0 | 0 | 17 |

**22 of 24 matched** the AI suggestions.

## Final label distribution

| human_label | count |
| --- | ---: |
| JUSTIFIED | 3 |
| NOT_JUSTIFIED | 4 |
| UNCERTAIN | 17 |

## Limitations

Lio's 9 labels were AI-assisted and are excluded from the answer key; only Emmanuel saw AI suggestions before labeling.
These source/exposure classifications follow the team's report. Review times were
not supplied. Explanations were transcribed, not independently reverified in this
step. Missing source permalinks remain missing. Small, outcome-selected samples
and the two-pair agreement count do not support broad generalizations.
