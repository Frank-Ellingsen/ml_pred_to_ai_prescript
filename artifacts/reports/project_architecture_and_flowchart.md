# Project Architecture and Workflow Diagram

## Project Architecture Diagram

```mermaid
flowchart LR
    A[User / Analyst] --> B[finance_ai.cli]
    B --> C[FinancialAnalysisFlow]

    C --> D[Actuals Tool]
    C --> E[Budget Tool]
    C --> F[Forecast Tool]
    C --> G[Variance Tool]
    C --> H[Retrieval Tool]
    C --> I[Scenario Tool]

    D --> J[SQLite Repository]
    E --> J
    F --> J
    G --> J
    H --> J
    I --> J

    J --> K[(finance.db)]

    F --> L[ProjectCostForecaster]
    L --> M[ML artifacts / joblib]

    H --> N[Documents & Policies]
    C --> O[Analysis Report]
    O --> P[Findings Report]

    style A fill:#2b6cb0,color:#fff
    style B fill:#4a5568,color:#fff
    style C fill:#805ad5,color:#fff
    style J fill:#3182ce,color:#fff
    style K fill:#dd6b20,color:#fff
    style L fill:#38a169,color:#fff
    style O fill:#d69e2e,color:#fff
```

## Process Flowchart

```mermaid
flowchart TD
    A[Start: user asks a business question] --> B[finance_ai.cli command]
    B --> C[Load database schema and seed data]
    C --> D[Connect to SQLite finance.db]
    D --> E[Read Actuals, Budgets, Forecasts, Documents]
    E --> F[Run FinancialAnalysisFlow]
    F --> G[Compare actual vs budget]
    G --> H[Identify variance drivers]
    H --> I[Pull document evidence from retrieval tool]
    I --> J[Use forecast and scenario tools]
    J --> K[Produce executive summary, key findings, risks, recommendations]
    K --> L[Save findings report]
    L --> M[End]

    style A fill:#2b6cb0,color:#fff
    style B fill:#4a5568,color:#fff
    style C fill:#805ad5,color:#fff
    style D fill:#805ad5,color:#fff
    style E fill:#805ad5,color:#fff
    style F fill:#805ad5,color:#fff
    style K fill:#d69e2e,color:#fff
    style L fill:#38a169,color:#fff
```

## Summary

This project combines a deterministic SQLite financial data layer, a Python CLI, an analysis orchestration flow, supporting financial tools, and a document retrieval/forecasting pipeline. The architecture is designed to produce a report that explains variance, risks, and recommended next investigations.
