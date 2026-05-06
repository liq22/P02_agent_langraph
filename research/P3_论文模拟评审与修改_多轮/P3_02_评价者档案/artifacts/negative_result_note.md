# P3_02 Negative And Blocked Evidence Note

generated_at: 2026-05-05

This node treats negative, blocked, rejected, and uncertain evidence as reviewer attack surfaces. The profiles do not interpret missing real-data rows, unresolved RM101 evidence, selected-backend uncertainty, Stage C/D incompleteness, low review scores, PHMGA dirty state, adapter-preflight gaps, or P1_03/P1_05 schema issues as support.

The interpretation is deliberately conservative: these failures and limitations define what the method, empirical, reproducibility, and adversarial reviewers should inspect next. They are not solved by persona design, prose calibration, or round planning.

Alternative explanation retained: the current positive synthetic/offline signal may reflect a narrow local sanity-check path rather than general performance. Downstream P3 critique must keep this limitation visible when mapping revision actions.
