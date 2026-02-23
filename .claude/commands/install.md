# Install & Prime

## Read
.env.sample (never read .env)

## Read and Execute
.claude/commands/prime.md

## Run
- Run `cp .env.sample .env` (skip if .env already exists)
- Install frontend dependencies: `cd frontend && npm install`
- Install backend dependencies: `cd backend && julia --project=. -e 'using Pkg; Pkg.instantiate()'`
- Download vendor libs: `bash scripts/download-vendor.sh`
- Run database migrations: `bash scripts/migrate.sh`
- Build frontend: `cd frontend && npm run build`

## Report
- Output the work you've just done in a concise bullet point list.
- Instruct the user to fill out `.env` based on `.env.sample` (POSTGRES_PASSWORD, JWT_SECRET are required).
- Remind the user to ensure PostgreSQL is running and the `fab_ui_dev` database exists before starting the server.
