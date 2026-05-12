# af-debug Implementation Plan

A Rust CLI for fetching, parsing, indexing, and querying Airflow 3 / Composer task failures with structured Python traceback and pod-spec extraction. 0. Pre-flight (do these before writing code)

These are auth/access spikes. They're the things most likely to surprise you, and they're hard to estimate until you try. Spend at most a day on each.

    Confirm Airflow 3 REST API access from your dev machine.
        Find the Composer environment's Airflow web server URL (gcloud composer environments describe <env> --location <region> --format='value(config.airflowUri)').
        Composer 3 uses IAP. Confirm you can hit GET /api/v2/dags with gcloud auth print-identity-token as a bearer token, plus the IAP client ID as Authorization: Bearer <token> audience.
        Document the auth flow in docs/auth.md while it's fresh.
    Identify where task logs actually live.
        Composer dumps task logs to a GCS bucket. Find the bucket: gcloud composer environments describe <env> --format='value(config.dagGcsPrefix)' then look at sibling paths.
        Confirm the path layout: typically gs://<bucket>/logs/dag_id=X/run_id=Y/task_id=Z/attempt=N.log. The exact convention matters for the fetcher.
    Verify GAR access for image inspection.
        docker pull against the us-docker.pkg.dev/rental-ds/r15-ds/ranking_cf_training repo should work with gcloud auth configure-docker. Confirm this works from your dev machine.
    Pick the index backend. Default to SQLite via rusqlite. If you anticipate queries that scan millions of events, switch to DuckDB. Don't agonize — SQLite is fine for v1.

If any of these don't work cleanly, the tool's surface area changes. Don't start coding the fetch layer until 1–3 are resolved.

1. Project setup

af-debug/
├── Cargo.toml
├── README.md
├── docs/
│ ├── auth.md
│ └── architecture.md
├── examples/
│ └── sample_log.txt # one anonymized failure log for tests
└── src/
├── bin/af_debug.rs # CLI entry point
├── lib.rs
├── error.rs
├── config.rs # config file + env vars
├── fetch/
│ ├── mod.rs
│ ├── airflow_api.rs
│ ├── gcs.rs
│ └── cache.rs
├── parse/
│ ├── mod.rs
│ ├── log_line.rs
│ ├── traceback.rs
│ ├── pod_spec.rs
│ └── events.rs
├── index/
│ ├── mod.rs
│ ├── schema.rs
│ └── store.rs
├── query/
│ ├── mod.rs
│ ├── runs.rs
│ ├── errors.rs
│ └── images.rs
└── cli/
├── mod.rs
├── parse_cmd.rs
├── inspect_cmd.rs
├── index_cmd.rs
└── query_cmd.rs

Initial Cargo.toml deps (justify each — your userPreferences rule applies here too):
toml

[dependencies]

# CLI

clap = { version = "4", features = ["derive"] }

# async runtime — needed for concurrent GCS fetches

tokio = { version = "1", features = ["full"] }

# HTTP for Airflow + GCS REST

reqwest = { version = "0.12", features = ["json", "stream", "rustls-tls"], default-features = false }

# Serialization

serde = { version = "1", features = ["derive"] }
serde_json = "1"
serde_yaml = "0.9"

# Time

chrono = { version = "0.4", features = ["serde"] }

# Parsing — parser combinators for log lines and pod specs

winnow = "0.6"

# Errors

anyhow = "1" # binary
thiserror = "1" # library types

# Logging the tool itself

tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["env-filter"] }

# Index

rusqlite = { version = "0.32", features = ["bundled", "chrono"] }

# Parallelism for batch parse

rayon = "1"

# Progress UI

indicatif = "0.17"

[dev-dependencies]
insta = "1" # snapshot testing for parser output
pretty_assertions = "1"
tempfile = "3"

Set up CI on day one (.github/workflows/ci.yaml): cargo fmt --check, cargo clippy -- -D warnings, cargo test. Easier to maintain hygiene from the start than retrofit. 2. Milestone 1 — Standalone log parser (week 1)

Goal: cat failed_task.log | af-debug parse → JSON-lines of structured events. No network, no DB, no CLI subcommands yet. Just stdin → stdout.

Why this first: The parser is the riskiest piece in terms of getting the data model right. Everything downstream depends on what Event looks like. Building it standalone forces a clean separation, gives you something testable in isolation, and is already useful on its own.
Tasks

    Define Event enum and supporting types in parse/events.rs. Cover at minimum:
        LogLineEvent { ts, source_module, source_line, level, container, content } for the noise lines ({pod_manager.py:477} INFO - [base] ...)
        ApplicationLog { ts, level, module, function, message } for the application's own log lines (the inner INFO     run - <module>: ...)
        PythonTraceback { exception_type, exception_message, frames }
        PodSpecDump { raw: String, image: Option<ImageRef>, deployment_version: Option<String> } — start by capturing the raw block; structured parsing comes later
        TaskOutcome { status, exit_code, finished_at }
        AirflowOperator { operator, action } for lines like {baseoperator.py:423} WARNING ...
    Write parse/log_line.rs — a winnow parser for the outer log-line prefix. ~30–50 lines. Returns (timestamp, source_module, source_line, level, container_opt, remaining_content).
    Write parse/traceback.rs — state-machine parser. Triggered by "Traceback (most recent call last):", accumulates File "...", line N, in func + optional source lines, terminates on ExceptionType: message. Handles tracebacks embedded inside log line prefixes (the QA log has both: pod_manager's traceback dump and the inner application traceback).
    Write parse/pod_spec.rs — start dumb. Triggered by remote_pod: {, accumulates until the matching close brace at indent 0. Stores as a raw string. Extract just image: '...' and Deployment Version: ... via regex on the raw text. Don't try to parse the full Python pprint repr in v1.
    parse/mod.rs — the top-level LogParser state machine that drives the three sub-parsers.
    CLI binary minimal version — just af-debug parse [FILE], defaulting to stdin if no file given. Outputs JSON-lines to stdout.

Test data and exit criteria

    Save the QA failure log from this thread (anonymized) to examples/sample_log.txt.
    Snapshot test (insta) against expected JSON output.
    Hand-verify: every traceback in the source log appears as exactly one PythonTraceback event. The pod spec is captured once. Image digest is extracted.
    Run on the v0-7-0 failure log too (Python 3.8 / tensorboard / protobuf 3.20.3 from a few messages back) — different traceback shape, parser should handle both.

Done when: running af-debug parse examples/sample_log.txt | jq produces a structured stream where you can answer "what was the exception type and which file did it originate in" with one jq filter. 3. Milestone 2 — Index + local query (week 2)

Goal: af-debug parse --index db.sqlite examples/sample_log.txt ingests events. af-debug query errors returns structured results.
Tasks

    index/schema.rs — define the SQLite schema:

sql

CREATE TABLE log_files (
file_id INTEGER PRIMARY KEY,
dag_id TEXT NOT NULL,
run_id TEXT NOT NULL,
task_id TEXT NOT NULL,
attempt INTEGER NOT NULL,
source_path TEXT NOT NULL,
ingested_at TIMESTAMP NOT NULL,
start_ts TIMESTAMP,
end_ts TIMESTAMP,
image_digest TEXT,
deployment_version TEXT,
UNIQUE (dag_id, run_id, task_id, attempt)
);
CREATE TABLE tracebacks (
traceback_id INTEGER PRIMARY KEY,
file_id INTEGER NOT NULL REFERENCES log_files(file_id),
ts TIMESTAMP NOT NULL,
exception_type TEXT NOT NULL,
exception_message TEXT NOT NULL,
top_frame_file TEXT,
top_frame_func TEXT,
frame_count INTEGER NOT NULL
);
CREATE TABLE traceback_frames (
traceback_id INTEGER NOT NULL REFERENCES tracebacks(traceback_id),
frame_idx INTEGER NOT NULL,
file TEXT NOT NULL,
line INTEGER NOT NULL,
func TEXT NOT NULL,
source TEXT,
PRIMARY KEY (traceback_id, frame_idx)
);
CREATE INDEX idx_tracebacks_exc ON tracebacks(exception_type);
CREATE INDEX idx_tracebacks_ts ON tracebacks(ts);
CREATE INDEX idx_log_files_dag_run ON log_files(dag_id, run_id);

Use migrations from the start. rusqlite_migration crate handles this cleanly.

    index/store.rs — Index struct wrapping the connection. ingest_events() method that batches inserts in a transaction. Idempotent: re-ingesting the same (dag_id, run_id, task_id, attempt) is a no-op via the unique constraint.
    query/errors.rs — typed query functions, e.g.:

rust

pub fn group_errors_by_type(
index: &Index,
filter: ErrorFilter,
) -> Result<Vec<ErrorTypeSummary>>

Implement: errors-by-type, errors-by-top-frame, similar-tracebacks (matching on exception_type + first 3 frames' file+func).

    CLI additions:
        af-debug parse --index <path> — parse + ingest in one step
        af-debug query errors [--exc-type T] [--dag D] [--since 7d]
        af-debug query similar --to <traceback-id>

Exit criteria

    Ingest 10 sample logs (mix real + synthetic).
    af-debug query errors --exc-type TypeError returns the expected rows.
    Ingesting the same log twice doesn't duplicate rows.
    af-debug query similar --to <id> correctly groups the QA failures together if you ingest a few synthetic copies.

4. Milestone 3 — Live fetching (week 3)

Goal: af-debug inspect-run --dag X --run Y fetches logs from Composer's GCS bucket, parses, indexes, and prints a clean summary. No manual log copying.
Tasks

    config.rs — config file at ~/.config/af-debug/config.toml:

toml

[composer]
environment = "nu-ds-workloads-dev"
region = "us-east4"
project = "rental-ds-dev-e76d5d81"
airflow_url = "https://..."
iap_client_id = "..."

[storage]
logs_bucket = "us-east4-..."
cache_dir = "~/.cache/af-debug"

[index]
path = "~/.cache/af-debug/index.db"

    fetch/airflow_api.rs — minimal Airflow REST client. Two methods:
        get_dag_run(dag_id, run_id) -> DagRun (status, dates)
        list_task_instances(dag_id, run_id) -> Vec<TaskInstance>
    fetch/gcs.rs — GCS object fetch via REST API. Bearer token from gcloud auth print-access-token (cache for 50 minutes). Stream to local cache.
    fetch/cache.rs — local cache layer keyed by GCS path. Returns cached file if present; otherwise fetches.
    cli/inspect_cmd.rs — orchestrates: API call → identify failed tasks → fetch logs → parse → ingest → query → format output:

DAG: qa-rcf-warmstart-train
Task: ranking_cf_training
Run: manual\_\_2026-05-11T18:25:04
Status: failed (exit 1)
Image: ranking_cf_training@sha256:433906fac0... (dev-20260511.181021-aee2944)
Duration: 51m

Top traceback:
TypeError: run() got an unexpected keyword argument 'latent_users_file'
at run.py:302 in train_model
at run.py:390 in run
at run.py:512 in <module>

Exit criteria

    Run af-debug inspect-run --dag qa-rcf-warmstart-train --run manual__2026-05-11T18:25:04 and get the right summary back, with all logs cached locally for next time.
    Second invocation runs in <1 second (cache hit).
    Ingestion is automatic but skippable via --no-index flag.

5. Milestone 4 — Image inspection (week 3.5)

Goal: Given an image digest from a failure, get pip freeze and diff against requirements.txt.
Tasks

    fetch/docker.rs — shell out to docker pull and docker run --rm --entrypoint /bin/sh <image> -c "pip freeze". Capture stdout. Cache results by digest.
    fetch/git.rs — shell out to git show <commit>:<path> to read files from arbitrary commits. Used for fetching requirements.txt at the build's deployment-version commit.
    query/images.rs — diff_resolved_vs_requested(image_digest, repo_path):
        Pull image, capture pip freeze
        Extract deployment version from image labels or by running the container
        Read requirements.txt from the corresponding git commit
        Diff the two — show what's pinned vs what was resolved
    CLI:
        af-debug image pip-freeze <digest>
        af-debug image diff-requirements <digest> --repo <path>

Exit criteria

For the failure in this thread, running af-debug image diff-requirements ranking_cf_training@sha256:433906fac0... --repo ~/code/r15-ds-orchestration should print:

Pinned in requirements.txt Resolved in image
nurecs nurecs==0.1.dev196+g277df66
numpy>=1.26.0 numpy==2.4.4
protobuf==3.20.3 protobuf==3.20.3
...

That alone diagnoses the issue in seconds. 6. Milestone 5 — Batch indexing (week 4)

Goal: af-debug index-dag --dag X --since 30d builds the historical index. af-debug query becomes useful across many runs.
Tasks

    fetch/gcs.rs::list_dag_window — list objects under gs://<bucket>/logs/dag_id=<dag>/run_id=*/... filtered by date prefix. Bounded concurrency for fetches (buffered(16)).
    cli/index_cmd.rs — orchestrates: list → fetch (parallel, cached) → parse (parallel via rayon) → bulk-ingest. Show progress with indicatif.
    New queries in query/:
        failures-over-time --dag X — daily count by exception type
        images-summary --dag X --since 30d — which image digests appeared, fail rate per digest
        regression-window --dag X — finds the run where a new exception type first appeared

Exit criteria

    Index 60 days of failures for a DAG in <5 minutes.
    af-debug query failures-over-time --dag qa-rcf-warmstart-train --since 60d produces a clean tabular view.
    Memory usage stays under 500MB even on the largest DAG.

7. Cross-cutting concerns

Reproducibility / determinism. Parser tests must be deterministic. Pin a fixed timestamp in test fixtures rather than chrono::Utc::now(). Snapshot tests via insta.

Error handling. Library code returns Result<\_, AfDebugError> (your own thiserror enum). Binary code uses anyhow at the edges. Never unwrap() outside of tests or main()-level fatal paths.

Logging. Use tracing from day one. The tool itself logs at info; verbose mode (-v) bumps to debug. Never println! from library code.

Testing strategy:

    Unit tests for parsers (small fixtures, snapshot-based).
    Integration tests for the index (in-memory SQLite, tempfile for cache dirs).
    One end-to-end test against a fake GCS server (wiremock crate) for the fetch layer.
    Manual smoke test for live inspect-run against real Composer — gated behind an env var so CI doesn't try to run it.

Performance baseline. After Milestone 1, benchmark cargo bench or just time the parser on a 10MB log. Track this number — if a future change drops parser throughput from 100MB/s to 20MB/s, you want to know.

What I'd defer past v1:

    Real-time pod log tailing (kube crate watching pods).
    A web UI. Stay CLI-only.
    DuckDB migration. Only if SQLite genuinely becomes the bottleneck.
    Full Python-repr parser for pod specs. Regex extraction of key fields is enough for v1.
    Cross-DAG dashboards. The query commands are enough; let users pipe through jq or a notebook.

8. Hand-off notes for Claude Code

Things to be explicit about when you give this to Claude Code:

    Stack constraints. Rust 2024 edition, MSRV 1.80, cargo fmt + cargo clippy -- -D warnings must pass. unsafe requires a comment justifying it.
    Sequence. Build milestones in order. Don't let Claude jump ahead to fetching before the parser is solid. Each milestone has its own exit criteria; tick them off explicitly.
    Test discipline. Every parser change should land with a snapshot test or fixture update. Every query function should have an integration test against an in-memory index.
    Data model decisions are sticky. The Event enum and the SQLite schema will outlive everything else. Push back if Claude wants to "just add a field" without thinking about migration.
    Real fixtures. The examples/ dir should accumulate anonymized real log files from actual failures. Synthetic fixtures are fine but don't substitute for the real shape.
    The auth spike is a real blocker. If Composer/IAP auth doesn't work out cleanly, the whole inspect-run flow needs rethinking. Don't build past Milestone 2 until that's confirmed.
    Anonymization. Scrub real GCP project IDs, real user emails, internal repo names, and image digests from fixtures before committing. The example in this plan uses real names because you're internal; anything that lands in a public repo or shared tool needs scrubbing.
