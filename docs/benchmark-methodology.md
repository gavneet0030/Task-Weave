# Benchmark methodology

Planned measurement rules:

1. Separate correctness tests from performance benchmarks.
2. Run warm-up iterations before recording samples.
3. Record workload parameters, Python/compiler versions, OS, and run identifiers.
4. Report throughput and latency percentiles; do not report only the mean.
5. Use enough independent repetitions to quantify variability.
6. Compare policies under equivalent workloads and randomized experiment order.
7. Record machine load and disclose limitations.
8. Never infer causation from a single run or a tiny sample.

Queueing theory comparisons will state their assumptions. Little's Law,
L = lambda * W, is meaningful only when the population, arrival rate, and
time interval use consistent boundaries and the system is sufficiently stable.