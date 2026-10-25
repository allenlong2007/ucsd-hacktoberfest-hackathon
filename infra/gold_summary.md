# Human label summary

30 PRs; 35 submitted entries; **4 human reviewers: Allen, Emmanuel, Lio, Nilesh**.
Reviewer names follow the team's corrected assignment and original label messages.
Label spellings were normalized by permission; labels and explanations are preserved.

## Inter-reviewer agreement

Inter-reviewer agreement: 2 of 5 double-labeled PRs (different reviewers, labeling independently). Small n, so indicative only.

Disagreed: slots 10, 17, 30. Both submitted labels and explanations remain in the
CSV. The prescribed conflict rule sets human_label to UNCERTAIN without replacing
either submitted label.

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

Only Emmanuel saw the AI suggestions before labeling.
Reviewer independence and exposure are reported by the team, not independently
verified by this transcription task. Review times were not supplied. Explanations
are submitted judgments, not claims that this task independently verified every
statement. Some source entries say "Key comment" without supplying a permalink;
those placeholders are preserved.
