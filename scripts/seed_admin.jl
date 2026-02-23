# Seed or reset the admin user password
# Usage: julia --project=backend scripts/seed_admin.jl [password]
# Defaults to 'admin123' if no password given

# Load .env
env_path = joinpath(@__DIR__, "..", ".env")
if isfile(env_path)
    for line in readlines(env_path)
        stripped = strip(line)
        (isempty(stripped) || startswith(stripped, "#")) && continue
        parts = split(stripped, "=", limit=2)
        length(parts) == 2 && (ENV[String(parts[1])] = String(parts[2]))
    end
end

include(joinpath(@__DIR__, "..", "backend", "src", "auth.jl"))
include(joinpath(@__DIR__, "..", "backend", "src", "db.jl"))

using .Auth
using .DB
using LibPQ

password = length(ARGS) >= 1 ? ARGS[1] : "admin123"
hash = Auth.hash_password(password)

DB.with_connection() do conn
    LibPQ.execute(conn,
        "UPDATE users SET password_hash = \$1, updated_at = NOW() WHERE username = 'admin'",
        [hash]
    )
end

println("Admin password updated successfully.")
