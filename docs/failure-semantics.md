# Failure and lifecycle semantics

The following rules will guide implementation and tests.

- Every task must have at most one terminal state.
- Queue overload must have a documented policy: reject, block, or timeout.
- Task exceptions must be captured and must not silently terminate unrelated workers.
- Graceful shutdown must define what happens to queued and running work.
- A timeout is not the same as forcibly stopping a running Python thread.
- Cancellation of queued work can be supported; cancellation of already-running
  code is cooperative unless that code provides its own cancellation mechanism.
- Metrics must distinguish queue wait, execution time, and end-to-end latency.

These are design requirements. They are not all implemented in Phase 1.