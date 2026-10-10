# Movie Reservation System

## Tests

Install the test dependencies and run the API and service tests:

```powershell
uv sync --group test
uv run pytest
```

API tests use FastAPI's `TestClient` and an isolated SQLite database created for
each test. They do not connect to the configured PostgreSQL or Redis services.