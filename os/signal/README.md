# os/signal

Deferred SIGINT, SIGTERM and SIGHUP handling on Linux and macOS.

- `Block() Result<bool>` blocks the three signals for the calling thread and
  threads it creates later (`pthread_sigmask`). Call it in `main` before
  starting threads, or a thread that does not block them receives them.
- `Pending() int` consumes one blocked signal that has arrived, or returns 0.
- `Wait(nanoseconds) int` waits up to the duration for one (Linux uses
  `sigtimedwait`; macOS, which lacks it, polls `sigpending` every 10ms).
- `Unblock() Result<bool>` restores delivery; a pending signal then takes effect.
- `Hangup`, `Interrupt`, `Terminate` hold the numbers; `Name(n)` gives `SIGINT` etc.

Windows and Wasm have no POSIX signals: `Block`/`Unblock` return errors and
`Pending`/`Wait` return 0.

`ocean test os/signal` checks behavior without delivering signals (test bodies
run on worker threads). `OCEAN=/path/to/ocean python3 os/signal/tests/test_signal.py`
builds `tests/main.oc` and delivers real signals to it.
