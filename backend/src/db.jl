module DB

using LibPQ

"""
    connection_string()

Build a PostgreSQL connection string from environment variables.
"""
function connection_string()
    host = get(ENV, "POSTGRES_HOST", "localhost")
    port = get(ENV, "POSTGRES_PORT", "5432")
    db   = get(ENV, "POSTGRES_DB", "fab_ui_dev")
    user = get(ENV, "POSTGRES_USER", "fab_ui")
    pass = get(ENV, "POSTGRES_PASSWORD", "")
    return "host=$host port=$port dbname=$db user=$user password=$pass"
end

"""
    get_connection()

Open and return a new database connection.
Caller is responsible for closing it.
"""
function get_connection()
    return LibPQ.Connection(connection_string())
end

"""
    with_connection(f)

Open a connection, pass it to `f`, and ensure it is closed afterward.

    with_connection() do conn
        execute(conn, "SELECT 1")
    end
"""
function with_connection(f)
    conn = get_connection()
    try
        return f(conn)
    finally
        close(conn)
    end
end

end # module
