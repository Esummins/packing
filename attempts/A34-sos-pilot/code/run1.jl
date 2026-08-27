# Single-configuration driver with visible TSSOS/solver progress.
# usage: julia --project=code code/run1.jl <n> <tier> <level> <cuts:on|off> <solver> <tol> <timelimit>
include(joinpath(@__DIR__, "model.jl"))
using .A34Model
using JSON, JuMP, Dates, TSSOS
import Clarabel, COSMO, SCS

n     = parse(Int, ARGS[1])
tier  = ARGS[2]
level = parse(Int, ARGS[3])
cuts  = ARGS[4] == "on" ? ["R1","R2","R3"] : String[]
solver= ARGS[5]
tol   = parse(Float64, ARGS[6])
tl    = parse(Float64, ARGS[7])

spec = ModelSpec(n; cuts=cuts, slb=1.0, smax=4.0)
pop, X, meta = build_pop(spec)
cl = tier == "dense" ? cliques_dense(n) : tier == "A" ? cliques_tierA(n) : cliques_tierB(n)

jm = if solver == "SCS"
        m = Model(SCS.Optimizer)
        set_optimizer_attribute(m, "verbose", 1)
        set_optimizer_attribute(m, "eps_abs", tol); set_optimizer_attribute(m, "eps_rel", tol)
        set_optimizer_attribute(m, "max_iters", 100_000)
        set_optimizer_attribute(m, "time_limit_secs", tl); m
     elseif solver == "COSMO"
        m = Model(COSMO.Optimizer)
        set_optimizer_attribute(m, "verbose", true)
        set_optimizer_attribute(m, "eps_abs", tol); set_optimizer_attribute(m, "eps_rel", tol)
        set_optimizer_attribute(m, "max_iter", 100_000)
        set_optimizer_attribute(m, "time_limit", tl); m
     else
        m = Model(Clarabel.Optimizer)
        set_optimizer_attribute(m, "verbose", true)
        set_optimizer_attribute(m, "time_limit", tl); m
     end

cutstr = isempty(cuts) ? "none" : join(cuts,"+")
tag = string("n",n,"_tier",tier,"_lvl",level,"_cuts",cutstr,"_",solver)
println("=== ", tag, " ===  N=", meta["N"], " ineq=", meta["n_ineq"], " eq=", meta["numeq"],
        " cliques=", length(cl), " maxcliquesize=", maximum(length.(cl))); flush(stdout)

t0 = time()
opt, sol, data = cs_tssos(pop, X, level; numeq=meta["numeq"], cliques=cl, TS=false,
                          QUIET=false, model=jm)
el = time()-t0

bs = data.blocksize
allb = Int[]; for ci in bs, cj in ci, b in cj; push!(allb, b); end
rec = Dict{String,Any}("tag"=>tag, "n"=>n, "form"=>"min-s circle", "tier"=>tier, "level"=>level,
  "cuts"=>cuts, "solver"=>solver, "tol"=>tol, "TS"=>"false", "slb"=>1.0, "smax"=>4.0,
  "N_vars"=>meta["N"], "n_ineq"=>meta["n_ineq"], "n_eq"=>meta["numeq"],
  "n_cliques"=>length(cl), "max_clique_size"=>maximum(length.(cl)),
  "moment_block_sizes"=>sort(unique([maximum(bs[i][1]) for i in 1:length(bs)]), rev=true),
  "max_block"=>maximum(allb), "sum_block_sq"=>sum(b^2 for b in allb),
  "dropped_ineq"=>length(data.Iprime), "dropped_eq"=>length(data.Jprime),
  "bound"=>opt === nothing ? nothing : Float64(opt), "time_s"=>round(el,digits=2),
  "status"=>string(data.SDP_status), "timestamp"=>string(now()))
try
  rec["term_status"]=string(termination_status(jm)); rec["prim_status"]=string(primal_status(jm))
  rec["dual_status"]=string(dual_status(jm)); rec["solve_time_s"]=solve_time(jm)
  rec["primal_obj"]=objective_value(jm); rec["dual_obj"]=dual_objective_value(jm)
catch; end

out = joinpath(@__DIR__,"..","results","part_single.json")
prev = isfile(out) ? (try JSON.parsefile(out) catch; Any[] end) : Any[]
push!(prev, rec)
open(out,"w") do io; JSON.print(io, prev, 2); end
println("RESULT ", tag, "  bound=", rec["bound"], "  status=", rec["status"],
        "  t=", rec["time_s"], "s  maxblk=", rec["max_block"],
        "  dropped=", rec["dropped_ineq"], "/", rec["dropped_eq"]); flush(stdout)
