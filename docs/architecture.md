# Architecture

## Current foundation

- `core/task.py`: task states and guarded transitions.
- `core/queue.py`: bounded, thread-safe FIFO storage wrapper.
- `config.py`: validated runtime settings.
- `metrics/statistics.py`: percentile and throughput helpers.
- `workloads/open_loop.py`: exponential interarrival-time sampling.
- `native/`: a C++20 bounded queue demonstration.
- `tests/`: initial unit tests.

## Planned execution path

```text
Workload generator
       |
       v
Task submission API
       |
       v
Bounded task queue -----> overload/rejection metrics
       |
       v
Scheduling policy
   FIFO / Priority
       |
       v
Worker pool
       |
       v
Task result and lifecycle
       |
       v
Metrics -> Experiment storage -> Reports
```

This diagram describes the target architecture, not a claim that every
component has already been implemented.