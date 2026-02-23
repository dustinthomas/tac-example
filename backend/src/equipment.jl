module Equipment

using LibPQ

"""
    list_equipment(conn; status=nothing, area=nothing, search=nothing)

List equipment with optional filters. Returns a vector of Dicts.
"""
function list_equipment(conn::LibPQ.Connection;
                        status::Union{String, Nothing}=nothing,
                        area::Union{String, Nothing}=nothing,
                        search::Union{String, Nothing}=nothing)
    conditions = String[]
    params = Any[]
    idx = 1

    if !isnothing(status) && !isempty(status)
        push!(conditions, "status = \$$idx")
        push!(params, status)
        idx += 1
    end

    if !isnothing(area) && !isempty(area)
        push!(conditions, "area = \$$idx")
        push!(params, area)
        idx += 1
    end

    if !isnothing(search) && !isempty(search)
        push!(conditions, "(LOWER(name) LIKE \$$idx OR LOWER(description) LIKE \$$idx)")
        push!(params, "%" * lowercase(search) * "%")
        idx += 1
    end

    query = "SELECT id, name, description, area, bay, status, criticality, updated_by, last_comment, created_at, updated_at FROM equipment"
    if !isempty(conditions)
        query *= " WHERE " * join(conditions, " AND ")
    end
    query *= " ORDER BY id"

    result = LibPQ.execute(conn, query, params)
    return _result_to_dicts(result)
end

"""
    get_equipment(conn, id::Int)

Get a single equipment item by ID. Returns Dict or nothing.
"""
function get_equipment(conn::LibPQ.Connection, id::Int)
    result = LibPQ.execute(conn,
        "SELECT id, name, description, area, bay, status, criticality, updated_by, last_comment, created_at, updated_at FROM equipment WHERE id = \$1",
        [id]
    )
    rows = _result_to_dicts(result)
    return isempty(rows) ? nothing : rows[1]
end

"""
    update_equipment!(conn, id::Int, status::String, comment::String, updated_by::String)

Update equipment status and comment. Returns updated Dict or nothing if not found.
"""
function update_equipment!(conn::LibPQ.Connection, id::Int, status::String, comment::String, updated_by::String)
    result = LibPQ.execute(conn,
        """UPDATE equipment
           SET status = \$1, last_comment = \$2, updated_by = \$3, updated_at = NOW()
           WHERE id = \$4
           RETURNING id, name, description, area, bay, status, criticality, updated_by, last_comment, created_at, updated_at""",
        [status, comment, updated_by, id]
    )
    rows = _result_to_dicts(result)
    return isempty(rows) ? nothing : rows[1]
end

"""
Convert a LibPQ Result to a vector of Dicts.
"""
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

end # module
