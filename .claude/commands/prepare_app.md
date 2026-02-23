# Prepare Application

Reset the database and start the backend server for testing. Follow the `Instructions` then `Report`.

## Instructions

- Run database migrations to ensure schema is up to date.
- Start the backend server if not already running.
- Verify the application is healthy.

## Steps

1. Run database migrations:
```bash
bash scripts/migrate.sh
```

2. Start the backend server (if not already running):
```bash
bash scripts/start.sh &
```

3. Wait for the server to be ready (check health endpoint or port availability).

4. Verify frontend builds cleanly:
```bash
cd frontend && npm run build
```

## Report
- Confirm each step completed successfully.
- Report any errors encountered.
- Confirm the application is ready for testing.
