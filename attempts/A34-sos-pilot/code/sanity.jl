# A34 T2 — plug known optimal packings into the lifted POP and verify every row.
# Catches sign / corner-parametrisation bugs BEFORE any SDP is trusted.

include(joinpath(@__DIR__, "model.jl"))
using .A34Model
using JSON

function known_config(n)
    if n == 2
        s = 2.0
        return [(0.5,0.5,0.0), (1.5,0.5,0.0)], s
    elseif n == 3
        s = 2.0
        return [(0.5,0.5,0.0), (1.5,0.5,0.0), (0.5,1.5,0.0)], s
    elseif n == 4
        s = 2.0
        return [(0.5,0.5,0.0),(1.5,0.5,0.0),(0.5,1.5,0.0),(1.5,1.5,0.0)], s
    elseif n == 5
        s = 2 + 1/sqrt(2)
        h = s - 0.5
        return [(0.5,0.5,0.0),(h,0.5,0.0),(0.5,h,0.0),(h,h,0.0),
                (s/2,s/2,pi/4)], s
    else
        error("no known config for n=$n")
    end
end

results = Dict{String,Any}()
for n in (2,3,4,5)
    cfg, s = known_config(n)
    for cuts in ([String[]], [["R1","R2","R3"]])
        spec = ModelSpec(n; cuts=cuts[1], slb=1.0, smax=4.0)
        v, wi, we, margins = check_feasibility(spec, cfg, s)
        key = "n$(n)_cuts$(isempty(cuts[1]) ? "off" : "on")"
        results[key] = Dict(
            "s" => s,
            "worst_ineq_label" => wi[1], "worst_ineq_value" => wi[2],
            "worst_eq_label" => we[1], "worst_eq_value" => we[2],
            "min_sep_margin" => minimum(values(margins)),
            "ok" => (wi[2] >= -1e-9) && (abs(we[2]) <= 1e-9),
        )
        println(rpad(key,14), " worst_ineq=", rpad(string(round(wi[2],digits=12)),16),
                " (", wi[1], ")  worst_eq=", round(we[2],digits=14),
                "  minsep=", round(minimum(values(margins)),digits=12),
                "  OK=", results[key]["ok"])
    end
end

open(joinpath(@__DIR__, "..", "results", "sanity.json"), "w") do io
    JSON.print(io, results, 2)
end
println("wrote results/sanity.json")
