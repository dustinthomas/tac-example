module App

using Genie
using Genie.Router
using Genie.Renderer
using Genie.Renderer.Json
using Genie.Requests
using HTTP
using JSON3
using LibPQ

include("db.jl")
include("auth.jl")
include("equipment.jl")

using .DB
using .Auth
using .Equipment

const PUBLIC_DIR = joinpath(@__DIR__, "..", "public")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

"""Load .env file into ENV if it exists."""
function load_env!()
    env_path = joinpath(@__DIR__, "..", "..", ".env")
    isfile(env_path) || return
    # Read each KEY=VALUE pair from .env and populate ENV; skips blank lines and comments.
    for line in readlines(env_path)
        stripped = strip(line)
        (isempty(stripped) || startswith(stripped, "#")) && continue
        parts = split(stripped, "=", limit=2)
        length(parts) == 2 && (ENV[String(parts[1])] = String(parts[2]))
    end
end

"""Return a JSON error response with the given status code."""
function json_error(message::String, code::Int)
    # Build and return a JSON-encoded error response with the given HTTP status code
    return Genie.Renderer.respond(
        JSON3.write(Dict("error" => message)),
        :json,
        code
    )
end

"""Extract and validate JWT from Authorization header. Returns claims or nothing."""
function authenticate_request()
    try
        req = Genie.Requests.request()
        isnothing(req) && return nothing
        auth_header = HTTP.header(req, "Authorization", "")
        if isempty(auth_header) || !startswith(auth_header, "Bearer ")
            return nothing
        end
        token_str = String(strip(auth_header[8:end]))
        return Auth.validate_token(token_str)
    catch e
        @error "Auth error" exception=e
        return nothing
    end
end

# ---------------------------------------------------------------------------
# SPA fallback routes — serve index.html for client-side routes
# ---------------------------------------------------------------------------

function serve_index()
    index_path = joinpath(PUBLIC_DIR, "index.html")
    return Genie.Renderer.respond(read(index_path, String), :html)
end

route("/") do
    serve_index()
end

route("/login") do
    serve_index()
end

route("/dashboard") do
    serve_index()
end

route("/equipment") do
    serve_index()
end

# ---------------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------------

route("/api/auth/login", method=POST) do
    body = jsonpayload()
    if isnothing(body)
        return json_error("Invalid JSON body", 400)
    end

    username = get(body, "username", nothing)
    password = get(body, "password", nothing)

    if isnothing(username) || isnothing(password) || isempty(username) || isempty(password)
        return json_error("Username and password are required", 400)
    end

    user = DB.with_connection() do conn
        result = LibPQ.execute(conn,
            "SELECT id, username, password_hash, role FROM users WHERE username = \$1",
            [username]
        )
        rows = _result_to_dicts(result)
        isempty(rows) ? nothing : rows[1]
    end

    if isnothing(user) || !Auth.verify_password(password, user["password_hash"])
        return json_error("Invalid credentials", 401)
    end

    user_id = Int(user["id"])
    token = Auth.create_token(user_id, user["username"], user["role"])

    return Genie.Renderer.respond(
        JSON3.write(Dict(
            "token" => token,
            "user" => Dict(
                "id" => user_id,
                "username" => user["username"],
                "role" => user["role"]
            )
        )),
        :json
    )
end

# ---------------------------------------------------------------------------
# Equipment API (all require auth)
# ---------------------------------------------------------------------------

route("/api/equipment", method=GET) do
    claims = authenticate_request()
    if isnothing(claims)
        return json_error("Unauthorized", 401)
    end

    # Parse query params
    status_filter = getpayload(:status, nothing)
    area_filter = getpayload(:area, nothing)
    search_filter = getpayload(:search, nothing)

    equipment_list = DB.with_connection() do conn
        Equipment.list_equipment(conn;
            status=status_filter,
            area=area_filter,
            search=search_filter
        )
    end

    return Genie.Renderer.respond(JSON3.write(equipment_list), :json)
end

route("/api/equipment/:id::Int", method=GET) do
    claims = authenticate_request()
    if isnothing(claims)
        return json_error("Unauthorized", 401)
    end

    eq_id = params(:id)

    eq = DB.with_connection() do conn
        Equipment.get_equipment(conn, eq_id)
    end

    if isnothing(eq)
        return json_error("Equipment not found", 404)
    end

    return Genie.Renderer.respond(JSON3.write(eq), :json)
end

route("/api/equipment/:id::Int", method=PUT) do
    claims = authenticate_request()
    if isnothing(claims)
        return json_error("Unauthorized", 401)
    end

    eq_id = params(:id)
    body = jsonpayload()
    if isnothing(body)
        return json_error("Invalid JSON body", 400)
    end

    status = get(body, "status", nothing)
    comment = get(body, "comment", nothing)

    if isnothing(status) || isnothing(comment)
        return json_error("Status and comment are required", 400)
    end

    # Validate status value
    valid_statuses = ["UP", "UP WITH ISSUES", "MAINTENANCE", "DOWN"]
    if !(status in valid_statuses)
        return json_error("Invalid status. Must be one of: $(join(valid_statuses, ", "))", 400)
    end

    updated_by = get(claims, "username", "unknown")

    eq = DB.with_connection() do conn
        Equipment.update_equipment!(conn, eq_id, status, comment, updated_by)
    end

    if isnothing(eq)
        return json_error("Equipment not found", 404)
    end

    return Genie.Renderer.respond(JSON3.write(eq), :json)
end

# ---------------------------------------------------------------------------
# Utility: convert LibPQ Result to vector of Dicts (used in login route)
# ---------------------------------------------------------------------------

function _result_to_dicts(result)
    ct = LibPQ.columntable(result)
    cols = keys(ct)
    isempty(cols) && return Dict{String, Any}[]
    nrows = length(first(ct))
    rows = Dict{String, Any}[]
    for i in 1:nrows
        row = Dict{String, Any}()
        for col in cols
            val = ct[col][i]
            row[String(col)] = ismissing(val) ? nothing : val
        end
        push!(rows, row)
    end
    return rows
end

# ---------------------------------------------------------------------------
# Server startup
# ---------------------------------------------------------------------------

"""Entry point: loads environment config, starts the Genie.jl HTTP server, and blocks the main thread to keep the process alive."""
function main()
    load_env!()

    Genie.config.run_as_server = true
    Genie.config.server_host = "0.0.0.0"
    Genie.config.server_port = parse(Int, get(ENV, "BACKEND_PORT", "8000"))
    Genie.config.server_document_root = PUBLIC_DIR

    up()

    # up() starts the server in a background task and returns immediately.
    # Block the main thread so the process stays alive.
    try
        while true
            sleep(1)
        end
    catch e
        e isa InterruptException || rethrow()
    end
end

# Run if this file is the entry point
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

end # module
