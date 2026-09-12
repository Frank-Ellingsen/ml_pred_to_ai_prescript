# Runbook: Cost Variance and EAC Investigation

**Document ID**: RB-FIN-VAR-01  
**Target Audience**: Project Controllers, Financial Controllers, Engineering Project Managers  
**Sector Relevance**: Maritime, Defense, High-Tech Engineering Projects  

## 1. Trigger Conditions
This investigation process is automatically initiated when:
- Cumulative or period Actual Cost of Work Performed (ACWP) exceeds Budgeted Cost of Work Performed (BCWP) by $>5\%$.
- Model-predicted Estimate at Completion (EAC) exceeds the Budget at Completion (BAC).

## 2. Investigation Protocol
1. **Work Breakdown Structure (WBS) Isolation**:
   - Query the transaction-level actuals for the offending milestone or work package.
   - Separate direct labor, subcontractor milestones, and specialized materials/components.
2. **Subcontractor Milestone Verification**:
   - Check whether milestone progress was certified by quality assurance before invoice processing.
   - Verify indexation or currency adjustments (e.g. EUR/USD contracts converted to NOK).
3. **Productivity & Hours Evaluation**:
   - Reconcile booked engineering hours against planned earned hours.
   - Note whether rework or technical redesign contributed to labor surge.
4. **Schedule Slippage Impact**:
   - Determine if delay is extending project overhead and vessel drydock rental fees.

## 3. Recommended Actions
- **If Variance is Timing/Phasing Only**: Shift budget allocation across forward quarters with zero BAC impact.
- **If Structural Cost Overrun**: Update Estimate to Complete (ETC) and propose contingency drawdown to the Steering Committee.
