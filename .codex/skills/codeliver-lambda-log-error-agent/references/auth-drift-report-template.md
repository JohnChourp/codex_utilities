# Cross-Product Auth-Drift Report Template (CodeDeliver)

Use this structure when the run is product-wide auth audit, not single-incident triage.

## 1) Audit Summary
- Selected products
- Time window
- Mode used (`static-only` or `static + logs`)
- Data completeness status (`complete` / `partial`)
- One-line conclusion

## 2) Remediation Matrix
Include one row per product with:
- `product`
- `login_lambda`
- `renew_lambda`
- `authorizer`
- `frontend_auth_entry`
- `identity_source_table`
- `late_failure_signatures`
- `risk_level`
- `recommended_fix_wave`

## 3) Auth Surface Inventory
- Login issuance contract highlights
- Renew-token contract highlights
- Authorizer validation depth
- Frontend fail-close / fail-open notes

## 4) Suspected Fail-Open Paths
- Short causal chain per product
- Static evidence
- Live-log evidence if available

## 5) TTL Mismatches
- Actual TTL values found
- Intended/claimed behavior if mismatched
- Products affected

## 6) Late Identity Failure Signatures
- Exact signatures found
- Which lambdas emit them
- Which canonical identity table each signature points to

## 7) Ranked Product Verdicts
For each product:
- `confirmed systemic risk` / `likely risk` / `monitor-only`
- Confidence score (0.0-1.0)
- Why it received that classification

## 8) Recommended Remediation Waves
- Wave 1
- Wave 2
- Wave 3
- Why this order is preferred

## 9) Skill Integration Spec
- What changes are required in `codeliver-lambda-log-error-agent`
- What remains out of scope for this pass
- Required output sections for future auth-drift runs

## 10) Verification Plan
- Static checks
- Live log sweep checks
- What would upgrade `likely risk` to `confirmed systemic risk`

## 11) Final Conclusion
- `Where is the problem pattern?`
- `Why does it happen?`
- `What should be fixed next?`
