# Known Issues

Synthetic, made-up knowledge base for learning purposes. Each section is one known test-failure issue.

## KI-001: Test database not ready at startup
**Symptoms:** Tests fail during setup with "connection refused" on port 5432. Happens mostly on the first job of a pipeline run.
**Root cause:** The test database container starts slower than the test runner, so tests try to connect before the database accepts connections.
**Fix:** Add a health check or a wait-for-database step before the test stage starts.

## KI-002: Flaky timeouts in network integration tests
**Symptoms:** Intermittent TimeoutError after 30 seconds in the integration suite. The same test passes when re-run.
**Root cause:** The shared test environment is overloaded during peak hours, so responses are slow.
**Fix:** Raise the timeout for the integration suite only, add retries with backoff, and tag the test as flaky so it is tracked.

## KI-003: Expired TLS certificate on the test server
**Symptoms:** SSL errors such as CERTIFICATE_VERIFY_FAILED or "certificate has expired" when tests call the staging API.
**Root cause:** The self-signed certificate used by the test server reached its expiry date.
**Fix:** Regenerate the certificate and add an expiry check that warns 14 days in advance.

## KI-004: Mock server port already taken
**Symptoms:** OSError "address already in use" when a fixture starts the mock HTTP server.
**Root cause:** A previous test run crashed and left the mock server process running on the same fixed port.
**Fix:** Kill leftover processes in teardown and let fixtures pick a random free port.

## KI-005: Test runner runs out of memory
**Symptoms:** The test process is killed with exit code 137, or Python raises MemoryError while loading fixtures.
**Root cause:** A large test dataset is loaded fully into memory at once.
**Fix:** Stream or sample the dataset, and raise the runner's memory limit for the data suite.

## KI-006: Build agent disk is full
**Symptoms:** "No space left on device" while writing logs, reports, or build artifacts.
**Root cause:** Old build artifacts are never cleaned up on the shared build agent.
**Fix:** Add a cleanup job and an artifact retention policy (for example, keep 7 days).

## KI-007: Database schema out of date in tests
**Symptoms:** Errors like "column does not exist" or UndefinedColumn right after a pull that includes database changes.
**Root cause:** New migrations were not applied to the test database.
**Fix:** Run all migrations as part of test setup.

## KI-008: Auth token expires during long API suites
**Symptoms:** API tests start returning 401 Unauthorized part-way through a long run, while early tests passed.
**Root cause:** The access token lives for 1 hour, but the full suite runs longer than that.
**Fix:** Refresh the token in a fixture before it expires.

## KI-009: Race condition when tests run in parallel
**Symptoms:** Assertions fail only when tests run in parallel (for example pytest -n auto). Sequential runs pass.
**Root cause:** Tests share global state such as a module-level counter or the same temporary file.
**Fix:** Isolate state per test, for example with the tmp_path fixture, and remove shared globals.

## KI-010: Unpinned dependency broke the build
**Symptoms:** ImportError or "module has no attribute" after a fresh install, with no code changes on our side.
**Root cause:** A library released a new major version and our requirements did not pin versions.
**Fix:** Pin dependency versions and use a lock file.

## KI-011: Internal service hostname cannot be resolved
**Symptoms:** "Name or service not known" or "getaddrinfo failed" when tests call an internal service.
**Root cause:** The runner is not on the internal network, or uses the wrong DNS configuration.
**Fix:** Use the service name inside the container network, or mock the service for unit tests.

## KI-012: Date assertions depend on the timezone
**Symptoms:** A date test fails only near midnight, or only on runners set to UTC.
**Root cause:** The test compares local time with UTC time.
**Fix:** Freeze time in the test and use timezone-aware UTC datetimes everywhere.
