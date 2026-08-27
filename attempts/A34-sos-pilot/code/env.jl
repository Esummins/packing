using Pkg, JSON, InteractiveUtils, JuMP
deps = Pkg.dependencies()
want = ["TSSOS","DynamicPolynomials","MultivariatePolynomials","JuMP","COSMO","Clarabel","SCS",
        "MosekTools","Mosek","SumOfSquares","SymbolicWedderburn","Graphs","JSON","Combinatorics"]
vers = Dict{String,Any}()
for (_,p) in deps
    if p.name in want
        vers[p.name] = p.version === nothing ? "unversioned/dev" : string(p.version)
    end
end
mosek_ok = false
mosek_msg = "no license file at " * joinpath(homedir(),"mosek","mosek.lic") *
            " and MOSEKLIC/MOSEKLM_LICENSE_FILE unset; MosekTools present only as a TSSOS dependency"
if isfile(joinpath(homedir(),"mosek","mosek.lic")) || haskey(ENV,"MOSEKLM_LICENSE_FILE")
    mosek_msg = "license file present but untested"
end
env = Dict(
  "julia_version" => string(VERSION),
  "cpu_threads" => Sys.CPU_THREADS,
  "total_memory_GB" => round(Sys.total_memory()/2^30, digits=1),
  "os" => string(Sys.KERNEL, " ", Sys.MACHINE),
  "packages" => vers,
  "mosek_license_works" => mosek_ok,
  "mosek_error" => mosek_msg,
  "solvers_used" => ["Clarabel","COSMO","SCS"],
  "project" => Base.active_project(),
)
open(joinpath(@__DIR__,"..","results","env.json"),"w") do io; JSON.print(io, env, 2); end
println(JSON.json(env,2))
