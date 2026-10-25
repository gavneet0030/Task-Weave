# Concurrency tests

Planned coverage:
- No task executes more than once.
- Every accepted task reaches exactly one terminal state.
- Worker exceptions do not kill unrelated work.
- Shutdown does not silently lose accepted work.
- Concurrent producers respect queue capacity.

These tests will be added with the worker-pool implementation.