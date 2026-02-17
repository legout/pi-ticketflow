# Spec Audit Review — pt-7jzy

## Critical
- None.

## Major
- The acceptance criterion that idle sessions must receive a graceful EOF (`Ctrl+D`) before forced termination is not satisfied. In `tf/ralph_completion.py`, `graceful_terminate_dispatch` acknowledges that sending EOF is not possible and immediately proceeds to SIGTERM/SIGKILL. There is no attempt to close the dispatch session’s stdin, send a `SIGINT`, or otherwise deliver a `Ctrl+D` handshake, so the implementation never fulfills the “EOF before kill” requirement. Please add a concrete EOF delivery (e.g., close the session’s stdin or inject the control sequence via the dispatch subprocess/Pty) before escalating to SIGTERM/KILL.

## Minor
- None.

## Warnings
- None.

## Sections
- **Acceptance Criterion 1 (Completion detection from dispatch/session state):** Verified in `tf/ralph_completion.py` via `poll_dispatch_status` using `os.waitpid(os.WNOHANG)` and the polling loop in `wait_for_dispatch_completion` that stops when the PID exits.
- **Acceptance Criterion 2 (Graceful EOF before forced kill):** Not implemented; see Major comment above.
- **Acceptance Criterion 3 (Timeout and forced termination reporting):** Satisfied by `wait_for_dispatch_completion`, which logs timeout warnings and returns a `DispatchCompletionResult` recording `termination_method`, `duration_ms`, and any errors.