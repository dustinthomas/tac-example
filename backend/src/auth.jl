module Auth

using SHA
using JWTs
using MbedTLS
using Random

"""
    hash_password(plain::String)::String

Hash a password with a random salt using SHA-256.
Returns "salt:hex_digest" format.
"""
function hash_password(plain::String)::String
    salt = bytes2hex(rand(UInt8, 16))
    digest = bytes2hex(sha256(salt * plain))
    return "$salt:$digest"
end

"""
    verify_password(plain::String, hash::String)::Bool

Verify a plaintext password against a "salt:hex_digest" hash.
"""
function verify_password(plain::String, hash::String)::Bool
    parts = split(hash, ":", limit=2)
    length(parts) != 2 && return false
    salt, stored_digest = parts
    computed_digest = bytes2hex(sha256(salt * plain))
    return computed_digest == stored_digest
end

"""
    _get_jwk()

Build the JWK symmetric key from JWT_SECRET env var.
"""
function _get_jwk()
    secret = get(ENV, "JWT_SECRET", "")
    isempty(secret) && error("JWT_SECRET environment variable not set")
    return JWKSymmetric(MbedTLS.MD_SHA256, Vector{UInt8}(secret))
end

"""
    create_token(user_id::Int, username::String, role::String)::String

Create a JWT with user_id, username, role, and expiry claims.
"""
function create_token(user_id::Int, username::String, role::String)::String
    expiry = get(ENV, "JWT_EXPIRY", "3600")
    exp_seconds = parse(Int, expiry)

    payload = Dict(
        "user_id" => user_id,
        "username" => username,
        "role" => role,
        "exp" => round(Int, time()) + exp_seconds
    )

    token = JWT(payload=payload)
    sign!(token, _get_jwk())
    return string(token)
end

"""
    validate_token(token_str::String)::Union{Dict, Nothing}

Decode and validate a JWT. Returns claims dict if valid, nothing if invalid/expired.
"""
function validate_token(token_str::AbstractString)::Union{Dict, Nothing}
    try
        token = JWT(jwt=token_str)
        validate!(token, _get_jwk())

        if !isverified(token)
            return nothing
        end

        c = claims(token)

        # Check expiry manually (JWTs.jl doesn't enforce it)
        if haskey(c, "exp")
            exp_time = c["exp"]
            if exp_time < time()
                return nothing
            end
        end

        return c
    catch
        return nothing
    end
end

end # module
