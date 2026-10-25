# Human label summary

30 PRs; 35 submitted entries; **1 named human reviewer: Emmanuel**, per the user's
explicit attribution. Repeated slots: 3, 10, 17, 24, 30. Source: user-uploaded label
text, with label spelling normalized by permission and explanations preserved.
The AI-assisted tags were removed from submitted explanations as requested.

## Repeated-entry consistency

**2 of 5 agreed** (same person's repeated submissions, not inter-reviewer
agreement). Conflicting slots: 10, 17, 30. Both original labels
and explanations remain in the CSV. The prescribed conflict rule sets the final
human_label to UNCERTAIN; it does not replace either submitted label.

## Human label vs inferred outcome — counts only

| human_label | redone_later | no_evidence |
| --- | ---: | ---: |
| JUSTIFIED | 0 | 2 |
| NOT_JUSTIFIED | 2 | 3 |
| UNCERTAIN | 3 | 20 |

`no_evidence` means no later redo was found; it does not mean closure was justified.
The sample deliberately includes all 5 inferred redone_later cases plus 25 others
from 42 Jest PRs; it is not a population prevalence estimate.

## Human label vs AI suggestions — counts only

Columns below are **AI suggestions, not ground truth**.

| human_label | JUSTIFIED | NOT_JUSTIFIED | UNCERTAIN |
| --- | ---: | ---: | ---: |
| JUSTIFIED | 1 | 0 | 1 |
| NOT_JUSTIFIED | 0 | 4 | 1 |
| UNCERTAIN | 0 | 0 | 23 |

**28 of 30 matched** the AI suggestions.

## Final label distribution

| human_label | count |
| --- | ---: |
| JUSTIFIED | 2 |
| NOT_JUSTIFIED | 5 |
| UNCERTAIN | 23 |

## Limitations

Emmanuel saw AI-suggested labels as cross-references before submitting his labels.
All four source blocks were attributed to him by the user; there are no labels
attributed to Allen, Lio, or Nilesh and no independent four-reviewer agreement.
Review times were not supplied. Explanations are submitted judgments, not claims
that this task independently verified every statement. Some source entries say
"Key comment" without supplying a permalink; those placeholders are preserved.
