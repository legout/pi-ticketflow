# seed-increase-timeout-on-each-iteration-defau

Introduce a progressive timeout increase on each iteration of a retry/loop mechanism, so longer-running attempts get more time before being aborted.

Default timeout increment should be **150000 ms** per iteration (with a sensible cap to avoid runaway runtimes).

## Keywords

- timeout
- backoff
- retries
- iteration
- watchdog
- robustness
