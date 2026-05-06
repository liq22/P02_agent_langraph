# P1_09 Negative and Unclear Result Note

The current figure package does not contain a formal positive performance result.
It contains one draft figure for a bounded P1_04/P1_05 synthetic/offline keep signal.

Unsupported or unclear items remain visible:

- Real-data generalization is unsupported because the source ledger has no accepted real-data formal row.
- RM101 resolution is unsupported because the source run uses Ottawa synthetic data only.
- Variance stability is unclear because only one baseline row and one controlled attempt row are available.
- The perfect synthetic score is ambiguous and may reflect an easy synthetic fixture.
- The upstream `c1` claim map exists, but P1_08 was still at `stage: seed` when this node authored the figure package.

The safe use of `fig_main_synthetic_signal` is therefore limited to a preliminary synthetic/offline single-run signal. It must not be used as a formal main-result figure.
