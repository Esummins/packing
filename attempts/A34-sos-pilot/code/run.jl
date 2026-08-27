# A34 T2 — driver: build the lifted POP, run CS-Lasserre relaxations via TSSOS,
# checkpoint every result to results/validation.json.
#
# usage: julia --project=code code/run.jl <plan>
#   <plan> = name of a plan defined in PLANS below (default "validation")

include(joinpath(@__DIR__, "model.jl"))
using .A34Model
using JSON, JuMP, Dates
using TSSOS
import Clarabel, COSMO, SCS

const RESULTS = joinpath(@__DIR__, "..", "results")
mkpath(RESULTS)

function make_model(solver::String; timelimit=3600.0, tol=1e-7)
    if solver == "Clarabel"
        m = Model(Clarabel.Optimizer)
        set_optimizer_attribute(m, "verbose", false)
        set_optimizer_attribute(m, "time_limit", timelimit)
        set_optimizer_attribute(m, "tol_gap_abs", tol)
        set_optimizer_attribute(m, "tol_gap_rel", tol)
        set_optimizer_attribute(m, "tol_feas", tol)
        return m
    elseif solver == "COSMO"
        m = Model(COSMO.Optimizer)
        set_optimizer_attribute(m, "verbose", false)
        set_optimizer_attribute(m, "time_limit", timelimit)
        set_optimizer_attribute(m, "max_iter", 100_000)
        set_optimizer_attribute(m, "eps_abs", 1e-6)
        set_optimizer_attribute(m, "eps_rel", 1e-6)
        return m
    elseif solver == "SCS"
        m = Model(SCS.Optimizer)
        set_optimizer_attribute(m, "verbose", 0)
        set_optimizer_attribute(m, "time_limit_secs", timelimit)
        set_optimizer_attribute(m, "max_iters", 100_000)
        set_optimizer_attribute(m, "eps_abs", tol)
        set_optimizer_attribute(m, "eps_rel", tol)
        return m
    else
        error("unknown solver $solver")
    end
end

cliques_for(tier, n) =
    tier == "dense" ? cliques_dense(n) :
    tier == "A"     ? cliques_tierA(n)  :
    tier == "B"     ? cliques_tierB(n)  : error("tier $tier")

function summarise_blocks(data)
    try
        bs = data.blocksize            # [clique][constraint][block]
        mom = [maximum(bs[i][1]) for i in 1:length(bs)]     # moment-matrix blocks
        allb = Int[]
        for ci in bs, cj in ci, b in cj; push!(allb, b); end
        return Dict("moment_block_sizes" => sort(unique(mom), rev=true),
                    "n_cliques" => length(bs),
                    "max_block" => maximum(allb),
                    "sum_block_sq" => sum(b^2 for b in allb))
    catch e
        return Dict("error" => string(e))
    end
end

function run_one(; n, tier, level, cuts, solver="Clarabel", TS=false,
                   slb=1.0, smax=4.0, timelimit=3600.0, MomentOne=false, tol=1e-6)
    spec = ModelSpec(n; cuts=cuts, slb=slb, smax=smax)
    pop, X, meta = build_pop(spec)
    cl = cliques_for(tier, n)
    cutstr = isempty(cuts) ? "none" : join(cuts, "+")
    tag = string("n", n, "_tier", tier, "_lvl", level, "_cuts", cutstr, "_", solver,
                 TS == false ? "" : "_TS")
    println("\n=== $tag ===  N=$(meta["N"]) ineq=$(meta["n_ineq"]) eq=$(meta["numeq"]) cliques=$(length(cl)) maxcliquesize=$(maximum(length.(cl)))")
    rec = Dict{String,Any}(
        "tag" => tag, "n" => n, "form" => "min-s circle", "tier" => tier,
        "level" => level, "cuts" => cuts, "solver" => solver, "TS" => string(TS),
        "slb" => slb, "smax" => smax,
        "N_vars" => meta["N"], "n_ineq" => meta["n_ineq"], "n_eq" => meta["numeq"],
        "n_cliques" => length(cl), "max_clique_size" => maximum(length.(cl)),
        "timestamp" => string(now()),
    )
    t0 = time()
    try
        jm = make_model(solver; timelimit=timelimit, tol=tol)
        opt, sol, data = cs_tssos(pop, X, level; numeq=meta["numeq"], cliques=cl,
                                  TS=TS, QUIET=true, solution=false, model=jm)
        rec["bound"] = opt === nothing ? nothing : Float64(opt)
        rec["time_s"] = round(time()-t0, digits=2)
        rec["status"] = string(data.SDP_status)
        merge!(rec, summarise_blocks(data))
        try   # constraints assigned to NO clique would be silently dropped
            rec["dropped_ineq"] = length(data.Iprime)
            rec["dropped_eq"]   = length(data.Jprime)
        catch
        end
        try
            rec["primal_obj"] = objective_value(jm)
            rec["dual_obj"]   = dual_objective_value(jm)
            rec["term_status"] = string(termination_status(jm))
            rec["prim_status"] = string(primal_status(jm))
            rec["dual_status"] = string(dual_status(jm))
            rec["solve_time_s"] = solve_time(jm)
        catch
        end
        println("   bound = ", rec["bound"], "   status = ", rec["status"],
                "   time = ", rec["time_s"], "s   maxblock = ", get(rec,"max_block","?"))
    catch e
        rec["bound"] = nothing
        rec["time_s"] = round(time()-t0, digits=2)
        rec["status"] = "ERROR"
        rec["error"] = first(string(e), 2000)
        println("   ERROR: ", first(string(e), 400))
    end
    return rec
end

# ---- checkpointing ----------------------------------------------------------
const PLANNAME = length(ARGS) >= 1 ? ARGS[1] : "smoke"
const OUT = joinpath(RESULTS, "part_$(PLANNAME).json")
function checkpoint!(all)
    open(OUT, "w") do io; JSON.print(io, all, 2); end
end
function load_prev()
    isfile(OUT) || return Any[]
    try; return JSON.parsefile(OUT); catch; return Any[]; end
end

# ---- plans ------------------------------------------------------------------
CUTS_ON  = ["R1","R2","R3"]
CUTS_OFF = String[]

function plan(name)
    P = []
    if name == "smoke"
        push!(P, (n=2, tier="dense", level=1, cuts=CUTS_ON,  solver="Clarabel"))
        push!(P, (n=2, tier="dense", level=1, cuts=CUTS_OFF, solver="Clarabel"))
    elseif name == "n2"
        for cuts in (CUTS_ON, CUTS_OFF), lvl in (1,2)
            push!(P, (n=2, tier="dense", level=lvl, cuts=cuts, solver="Clarabel"))
        end
    elseif name == "n3"
        for lvl in (1,2), tier in ("A","B"), cuts in (CUTS_ON, CUTS_OFF)
            push!(P, (n=3, tier=tier, level=lvl, cuts=cuts, solver="Clarabel"))
        end
    elseif name == "n3dense"
        for lvl in (1,2), cuts in (CUTS_ON, CUTS_OFF)
            push!(P, (n=3, tier="dense", level=lvl, cuts=cuts, solver="Clarabel"))
        end
    elseif name == "n5"
        for lvl in (1,2), tier in ("A","B"), cuts in (CUTS_ON, CUTS_OFF)
            push!(P, (n=5, tier=tier, level=lvl, cuts=cuts, solver="Clarabel"))
        end
    elseif name == "n3s"      # level-2 sweep with SCS (faster/leaner than Clarabel)
        for tier in ("B","A","dense"), cuts in (CUTS_ON, CUTS_OFF)
            push!(P, (n=3, tier=tier, level=2, cuts=cuts, solver="SCS", tol=1e-5))
        end
    elseif name == "n5s"
        for tier in ("A","B"), cuts in (CUTS_ON, CUTS_OFF)
            push!(P, (n=5, tier=tier, level=2, cuts=cuts, solver="SCS", tol=1e-5))
        end
    elseif name == "solvers"
        # calibrate the open solvers against Clarabel's 1.70711104 on n=2 lvl 2
        for slv in ("COSMO","SCS")
            push!(P, (n=2, tier="dense", level=2, cuts=CUTS_ON, solver=slv))
        end
    elseif name == "lvl3"
        push!(P, (n=2, tier="dense", level=3, cuts=CUTS_ON,  solver="SCS", tol=1e-5))
        push!(P, (n=2, tier="dense", level=3, cuts=CUTS_OFF, solver="SCS", tol=1e-5))
        push!(P, (n=3, tier="A",     level=3, cuts=CUTS_ON,  solver="SCS", tol=1e-5))
    elseif name == "lvl3c"
        push!(P, (n=2, tier="dense", level=3, cuts=CUTS_ON,  solver="COSMO", tol=1e-5))
    else
        error("unknown plan $name")
    end
    return P
end

pname = PLANNAME
tl = length(ARGS) >= 2 ? parse(Float64, ARGS[2]) : 3600.0
all = load_prev()
for cfg in plan(pname)
    rec = run_one(; cfg..., timelimit=tl)
    push!(all, rec)
    checkpoint!(all)
end
println("\nwrote ", OUT, " (", length(all), " records)")
