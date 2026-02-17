# Backlog: seed-increase-timeout-on-each-iteration-defau

| ID | Title | Score | Est. Hours | Depends On | Links |
|----|-------|-------|------------|------------|-------|
| pt-xwjw | Define timeout backoff semantics + configuration keys | 9 | 1-2 | - | pt-bcu8 |
| pt-bcu8 | Implement timeout backoff calculation helper | 4 | 1-2 | pt-xwjw | pt-xwjw,pt-9lri |
| pt-9lri | Add unit tests for timeout backoff calculation (including max cap) | 4 | 1-2 | pt-bcu8 | pt-bcu8,pt-w3ie |
| pt-w3ie | Wire timeout backoff into the retry/iteration timeout enforcement point | 3 | 1-2 | pt-9lri | pt-9lri,pt-7hzv |
| pt-7hzv | Add logging for effective timeout per iteration | 3 | 1-2 | pt-w3ie | pt-w3ie |