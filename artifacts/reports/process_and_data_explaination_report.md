# Process and Data Explanation Report

## 1. Project Overview

This repository implements a Project Finance AI workflow for explaining large project cost and revenue variances. It is designed around a deterministic set of data tables and a small set of reporting and analysis agents. The repository uses a local SQLite database as the authoritative data store, a typed Python analysis flow, and structured domain contracts for the final financial report.

The project focuses on one example entity:

- Entity ID: Project-Vessel-2026
- Currency: NOK
- Evaluation period: 2025-Q2

The test data included in this repository is intentionally mock but realistic enough to resemble a project controlling case in a maritime engineering environment.

## 2. Data Explains

The database schema defines five main tables:

1. actuals
   - Stores historical actuals for revenue, cost, customers, units, currency, and data-as-of timestamp.
   - Primary key is (entity_id, period).
   - Example actuals for Project-Vessel-2026 are recorded for 2024-Q3, 2024-Q4, 2025-Q1, and 2025-Q2.

2. budgets
   - Stores approved budget numbers by entity, period, metric, amount, currency, and budget version.
   - Example rows include revenue and cost budgets for 2024-Q3 through 2025-Q4.

3. forecasts
   - Stores machine learning forecast model outputs with point estimates, lower and upper bounds, confidence, model name, model version, and forecast timestamp.
   - Forecast rows exist for 2025-Q3 and 2025-Q4 and are separated for revenue and cost.

4. documents
   - Stores structured evidence in the form of technical memos, billing notices, and governance policies.
   - Example documents include the propulsion system memo and the customer milestone billing postponement notice.

5. feedback
   - Stores a later human review and decision record for decision traceability.

The full-text document index uses SQLite FTS5 so document title and content can be searched like a simple evidence retrieval layer.

## 3. Seeded Mock Data Description

The mock data is created by the repository seed routine in the seed data file. The dataset is intentionally limited to one project, one currency, and one analysis question.

The seeded data contains four actual rows, twelve budget rows, eight forecast rows, and three document records.

### Actuals rows

These rows describe historical, observed project financial performance:

- 2024-Q3: revenue 38,000,000 NOK, cost 31,000,000 NOK
- 2024-Q4: revenue 42,000,000 NOK, cost 34,500,000 NOK
- 2025-Q1: revenue 46,500,000 NOK, cost 37,200,000 NOK
- 2025-Q2: revenue 45,000,000 NOK, cost 42,000,000 NOK

These numbers reveal that the project is moving through a disruption in Q2 where revenue falls below the budget and cost moves above expected budget.

### Budgets rows

The budget table records approved budgets for 2024-Q3 through 2025-Q4. The most relevant budget comparison for the requested question is the 2025-Q2 budget:

- Revenue budget: 50,000,000 NOK
- Cost budget: 38,000,000 NOK

These compare directly with the actual Q2 numbers above.

### Forecast rows

The forecast table contains predictions for 2025-Q3 and 2025-Q4 with point estimates and intervals:

- Revenue forecasts for 2025-Q3 and 2025-Q4
- Cost forecasts for 2025-Q3 and 2025-Q4
- A shared ML model version: project_cost_forecaster / v2026.1

Forecast data is included to show how the workflow traces forecasts and compares them with the actuals and budgets.

### Document rows

Three documents are inserted as evidence:

- DOC-PROPULSION-01
  - A technical memo describing the propulsion waterjet and turbine integration cost overrun due to subcontractor price indexation.

- DOC-MILESTONE-REV-02
  - A billing notice explaining that milestone billing certificate acceptance was delayed and related revenue recognition shifted from Q2 into Q3.

- POL-FIN-2026-01
  - A governance or policy document explaining that any cost or revenue variance above five percent needs investigation, and that forecast numbers are treated as immutable evidence.

These documents are important because they ground the narrative in real evidence rather than just tables of numbers.

## 4. End-to-End Process

The process starts in the command-line interface in the CLI module. The CLI exposes commands to make the database and to seed it:

- init-database
- seed-database
- run-analysis
- train-models

The workflow command used for this test run is:

```text
python -m finance_ai.cli run-analysis
```

The analysis flow is implemented in the orchestration layer. It uses a typed workflow state and a two-step flow:

1. prepare_analysis
   - Validates the question, entity, period, and currency.
   - Creates the workflow context.

2. run_analysis
   - Builds a financial analysis crew from the project configuration.
   - Agent tools collect actuals, budgets, forecasts, retrieval evidence, and scenario information.

3. finalize
   - Converts the structured Pydantic output into the final financial report object in the state.

The actual detached fallback when CrewAI is missing is a deterministic mock crew that returns a report directly from the repository model definitions. This allows the project to run even when the external CrewAI dependency is unavailable.

## 5. Workflow Logic

The analysis flow begins with a business question:

> Why is revenue below budget and what should I investigate?

That question is answered by using the project’s cross-tool strategy:

- Actuals Tool reads actual project numbers.
- Budget Tool reads target budget numbers.
- Forecast Tool reads expected prediction numbers.
- Variance Tool compares observed and planned numbers.
- Retrieval Tool searches the document store for evidence.
- Scenario Tool captures known mitigation or performance scenarios.

The report is structured as a typed Pydantic financial report with four sections:

- Executive Summary
- Key Findings
- Risks and Uncertainty
- Recommended Investigations
- Evidence references

## 6. Result of the Workflow

The run produced the following result:

### Executive Summary

The workflow explains that Project-Vessel-2026 under-performed on revenue and over-ran on cost in Q2. It attributes the result to an indexation impact on the propulsion subcontractor cost and a delayed milestone certificate acceptance that delayed billing revenue into Q3.

### Key Findings

1. Actual revenue in Q2 was 45,000,000 NOK, compared with budget 50,000,000 NOK, a -10.0% variance.
2. Actual cost in Q2 was 42,000,000 NOK, compared with budget 38,000,000 NOK, a +10.5% variance.
3. The propulsion waterjet milestone passed factory acceptance on June 28.

### Risks and Uncertainty

1. Raw material and subcontractor price indexation volatility.
2. Customer quality assurance milestone verification timeline slippage.

### Recommended Investigations

1. Reconcile the customer QA certificate acceptance and delayed Q2 milestone billing in Q3.
2. Review the subcontractor clause 14.3 price indexation cap and charge mechanism.

### Evidence

The workflow also emits structured evidence references:

- EV-ACT-2025-Q2: actual source from actuals table
- EV-DOC-PROPULSION: evidence source from the propulsion memo in the documents table

## 7. Data Story in Plain Language

The data tells a consistent story. The project is profitable in the broad sense because cost and revenue numbers are real and there is a known project context. However, in the Q2 period, the project had a revenue shortfall because the milestone billing certificate was not accepted until after the close of the reporting quarter. At the same time, costs rose because the propulsion subcontractor applied a raw material indexation surcharge, which drove the project over budget on cost.

That is why the workflow concludes that the evidence points to two concrete causes:

- Customer-side QA evidence process delayed revenue recognition.
- Supplier contract indexation process increased costs.

## 8. Interpretation

This test data is not meant to represent a full enterprise operation. It is a self-contained mock dataset that demonstrates a simple but useful finance analysis workflow with realistic variance analysis and document evidence search. The important design feature is that the workflow is deterministic and repeatable. It uses source-of-truth data tables, a typed report model, and repository-backed evidence.

The project is useful as a demonstration because it turns structured data into a cross-checkable and reproducible narrative. It is suitable as a starting point for more advanced testing, data engineering, reporting automation, and ML forecast explanation.
