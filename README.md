# TaskWeave

**Concurrent Task Scheduling & Performance Laboratory**

TaskWeave is a local, single-machine laboratory for studying task scheduling,
bounded queues, worker pools, cancellation semantics, queueing theory, and
reproducible performance measurements.

The project uses Python for orchestration, experiments, tests, and reports.
C++20 is used for selected native concurrency components.

## Project status

**Current status ? Scheduler foundation implemented; performance research in progress.**

Implemented and tested:

- Task lifecycle state machine.
- Bounded worker-pool submission and overload rejection.
- FIFO scheduling with task cancellation and execution timeouts.
- Validated TOML runtime configuration.
- Graceful shutdown with a configurable caller wait period.
- Python unit and concurrency tests.
- Native C++20 bounded-queue demonstration.
- Environment diagnostics through the CLI.

Still in progress: scheduling metrics, open-loop benchmarking, statistical
comparisons, performance reports, and priority scheduling with starvation
mitigation. A shutdown grace period limits how long the caller waits; it does
not forcibly terminate a running Python thread.
## Design principles

- One task must not finish in multiple terminal states.
- Queue capacity and overload behavior must be explicit.
- Running Python threads cannot be safely force-killed.
- Correctness tests and performance experiments are separate.
- Benchmark conclusions must be based on sufficient measurements.
- Results must record their workload and environment.
- Never report fabricated performance improvements.

## Architecture

```text
TaskWeave
├── Python control plane
│   ├── Task lifecycle and configuration
│   ├── Scheduling policies
│   ├── Worker pool and bounded submission
│   ├── Metrics and latency distributions
│   ├── Workload generation
│   └── Reports and CLI
├── Native C++20 components
│   ├── Bounded thread-safe queue
│   └── Future native performance experiments
├── Validation
│   ├── Unit tests
│   ├── Concurrency tests
│   └── Property-based tests
└── Research
    ├── FIFO versus priority scheduling
    ├── Priority aging and starvation
    ├── Open-loop workload generation
    └── Queueing theory comparisons
```

## Prerequisites

- Python 3.11 or newer
- Git (recommended)
- CMake and a working C++20 compiler for the native component
- Windows PowerShell and VS Code

## Set up

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Validate the Python foundation

```powershell
python -m pytest
python -m taskweave doctor
```

## Build the native component

```powershell
cmake -S native -B native/build -DCMAKE_BUILD_TYPE=Release
cmake --build native/build --config Release
```

Run the resulting executable under `native/build` (the exact path depends
on the selected compiler and generator).

## Roadmap

1. ~~Establish and test the task state machine.~~
2. ~~Implement bounded submission and worker lifecycle semantics.~~
3. ~~Add FIFO scheduling, cancellation, timeouts, and graceful shutdown.~~
4. Add priority scheduling and starvation mitigation.
5. Add latency, throughput, rejection, and queue-wait metrics.
6. Build an open-loop load generator and reproducible experiments.
7. Expand statistical comparisons, reports, and CI validation.
8. Compare selected Python and C++ implementations.

See `docs/architecture.md` and `docs/failure-semantics.md`.
