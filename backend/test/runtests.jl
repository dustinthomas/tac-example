using Test

@testset "Backend Tests" begin
    @testset "Module loading" begin
        include(joinpath(@__DIR__, "..", "src", "App.jl"))
        @test isdefined(App, :main)
        @test isdefined(App, :authenticate_request)
        @test isdefined(App, :json_error)
        @test isdefined(App, :load_env!)
    end
end
