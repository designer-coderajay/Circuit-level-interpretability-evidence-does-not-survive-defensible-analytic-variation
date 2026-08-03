# Pre-registration

Nothing here is written until the pipeline is built, unit-tested, and validated
on data that will not enter the confirmatory analysis.

The plan is committed with a timestamp BEFORE pooled results are looked at.
Record the commit hash and UTC timestamp in `RESEARCH_LOG.md` and in the paper's
reproducibility section. A commit hash on a public remote is verifiable by a
reviewer; a claim of pre-registration without one is not.

Locking:

```bash
git add preregistration/
git commit -m "prereg: lock analysis plan for <name>"
git rev-parse HEAD
date -u +"%Y-%m-%dT%H:%M:%SZ"
git tag -a prereg-<name> -m "locked <timestamp>"
git push origin prereg-<name>      # third-party attestation of the timestamp
```

`DEVIATIONS.md` is append-only. Every departure from the locked plan is recorded
with the date, what the plan said, what was done, why, and whether the decision
came before or after seeing the affected result. Reviewers forgive an owned
deviation and punish a hidden one.

**Blocked on:** design deltas D1, D2, D4 in `docs/DESIGN-DELTAS.md`, and on
reading arXiv:2606.06267 in full.
