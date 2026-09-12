-- SQLite Persistence Layer for Project Finance AI
-- Strictly preserves authoritative financial records and immutable contracts

PRAGMA foreign_keys = ON;

-- 1. Historical Financial Actuals
CREATE TABLE IF NOT EXISTS actuals (
    entity_id TEXT NOT NULL,
    period TEXT NOT NULL,
    revenue REAL NOT NULL,
    cost REAL NOT NULL,
    customers INTEGER DEFAULT 0,
    units INTEGER DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'NOK',
    data_as_of TEXT NOT NULL,
    PRIMARY KEY (entity_id, period)
);

CREATE INDEX IF NOT EXISTS idx_actuals_entity_period ON actuals (entity_id, period);

-- 2. Approved Budgets
CREATE TABLE IF NOT EXISTS budgets (
    entity_id TEXT NOT NULL,
    period TEXT NOT NULL,
    metric TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'NOK',
    budget_version TEXT NOT NULL,
    PRIMARY KEY (entity_id, metric, period, budget_version)
);

CREATE INDEX IF NOT EXISTS idx_budgets_lookup ON budgets (entity_id, metric, period, budget_version);

-- 3. Authoritative Forecasts (ML Predictions & Intervals)
CREATE TABLE IF NOT EXISTS forecasts (
    forecast_id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    period TEXT NOT NULL,
    point_estimate REAL NOT NULL,
    lower REAL,
    upper REAL,
    confidence REAL DEFAULT 0.90,
    model_name TEXT NOT NULL,
    model_version TEXT NOT NULL,
    forecast_as_of TEXT NOT NULL,
    data_as_of TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_forecasts_lookup ON forecasts (entity_id, metric, period, model_version);

-- 4. Financial & Runbook Documents (RAG evidence store)
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL,
    period TEXT,
    version TEXT,
    source_uri TEXT,
    content TEXT NOT NULL
);

-- Full-Text Search (FTS5) for Evidence Retrieval
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    document_id,
    title,
    content,
    tokenize = 'porter unicode61'
);

-- 5. Human Decision & Feedback Store (Audit trail)
CREATE TABLE IF NOT EXISTS feedback (
    feedback_id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    actual_outcome TEXT,
    reviewer TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    comments TEXT
);

CREATE INDEX IF NOT EXISTS idx_feedback_analysis ON feedback (analysis_id);
