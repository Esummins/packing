# A34 T2 — POP model generator for the lifted square-packing formulation.
# Spec: attempts/A34-sos-pilot/notes/formulation.md §1, §2(b), §3, §5.
#
# Variable order (global index):
#   for i = 1..n:  x_i, y_i, g_i (=cos θ_i), t_i (=sin θ_i)      -> 4n
#   for each pair (i<j) in lexicographic order: u1_ij, u2_ij     -> 2*C(n,2)
#   s                                                            -> 1
# so N = 4n + 2*binomial(n,2) + 1, and s is the LAST variable.

module A34Model

using DynamicPolynomials
using Combinatorics

export ModelSpec, build_pop, pair_list, var_index, corners_num, sat_direction, check_feasibility

struct ModelSpec
    n::Int
    cuts::Vector{String}      # subset of ["R1","R2","R3"]
    slb::Float64              # lower bound imposed on s (1.0 = uninformative)
    smax::Float64             # upper bound imposed on s (must exceed s(n))
    sqrt2ub::Float64          # rational-ish enclosure of sqrt(2) used in R3
end
ModelSpec(n; cuts=["R1","R2","R3"], slb=1.0, smax=4.0, sqrt2ub=1.4142136) =
    ModelSpec(n, cuts, slb, smax, sqrt2ub)

pair_list(n) = [(i,j) for i in 1:n for j in (i+1):n]

nvars(n) = 4n + 2*binomial(n,2) + 1

# index helpers (1-based global variable indices)
xi(i)      = 4*(i-1) + 1
yi(i)      = 4*(i-1) + 2
gi(i)      = 4*(i-1) + 3
ti(i)      = 4*(i-1) + 4
function ui(n, i, j)
    ps = pair_list(n)
    k = findfirst(==( (i,j) ), ps)
    base = 4n + 2*(k-1)
    (base+1, base+2)
end
si(n) = nvars(n)

var_index(n) = (xi=xi, yi=yi, gi=gi, ti=ti, ui=(i,j)->ui(n,i,j), si=si(n))

"""
    build_pop(spec) -> (pop, X, meta)

`pop[1]` is the objective (minimise s); `pop[2:end-numeq]` are the >= 0 rows,
the last `numeq` entries are the = 0 rows.  `meta` records row labels / counts /
clique definitions.
"""
function build_pop(spec::ModelSpec)
    n = spec.n
    N = nvars(n)
    @polyvar X[1:N]
    s = X[si(n)]

    x = [X[xi(i)] for i in 1:n]
    y = [X[yi(i)] for i in 1:n]
    g = [X[gi(i)] for i in 1:n]
    t = [X[ti(i)] for i in 1:n]

    ps = pair_list(n)
    uv(i,j) = (a = ui(n,i,j); (X[a[1]], X[a[2]]))

    PT = typeof(polynomial(1.0*X[1]*X[2] + 1.0))
    ineq = PT[]; ilab = String[]
    eq   = PT[]; elab = String[]

    push_i!(p, l) = (push!(ineq, polynomial(1.0*p)); push!(ilab, l))
    push_e!(p, l) = (push!(eq,   polynomial(1.0*p)); push!(elab, l))

    # ---- (C1) circle sign conditions + (C5) gamma,sigma in [0,1] -------------
    for i in 1:n
        push_i!(g[i],     "C1_g_nonneg_$i")
        push_i!(t[i],     "C1_t_nonneg_$i")
        push_i!(1 - g[i], "C5_g_ub_$i")
        push_i!(1 - t[i], "C5_t_ub_$i")
    end

    # ---- (C2) containment ---------------------------------------------------
    for i in 1:n
        push_i!(x[i] - (g[i]+t[i])/2,     "C2_xlo_$i")
        push_i!(s - x[i] - (g[i]+t[i])/2, "C2_xhi_$i")
        push_i!(y[i] - (g[i]+t[i])/2,     "C2_ylo_$i")
        push_i!(s - y[i] - (g[i]+t[i])/2, "C2_yhi_$i")
    end

    # ---- (C5) centre boxes (implied by C2+R3 but kept: Archimedean per clique)
    for i in 1:n
        push_i!(x[i] - 0.5,       "C5_xlo_$i")
        push_i!(s - 0.5 - x[i],   "C5_xhi_$i")
        push_i!(y[i] - 0.5,       "C5_ylo_$i")
        push_i!(s - 0.5 - y[i],   "C5_yhi_$i")
    end

    # ---- (C5) s box ---------------------------------------------------------
    push_i!(s - spec.slb,  "C5_slo")
    push_i!(spec.smax - s, "C5_shi")

    # ---- (C3) separation, 16 corner pairs / pair; (C4) ||u||^2 = 1 ----------
    for (i,j) in ps
        u1,u2 = uv(i,j)
        for s1 in (-1,1), s2 in (-1,1)          # corner of square i
            pax = x[i] + (s1/2)*g[i] - (s2/2)*t[i]
            pay = y[i] + (s1/2)*t[i] + (s2/2)*g[i]
            for r1 in (-1,1), r2 in (-1,1)      # corner of square j
                qbx = x[j] + (r1/2)*g[j] - (r2/2)*t[j]
                qby = y[j] + (r1/2)*t[j] + (r2/2)*g[j]
                push_i!(u1*(pax-qbx) + u2*(pay-qby),
                        "C3_$(i)_$(j)_$(s1)_$(s2)_$(r1)_$(r2)")
            end
        end
        # (C5) u components in [-1,1]
        push_i!(1 - u1, "C5_u1hi_$(i)_$(j)"); push_i!(1 + u1, "C5_u1lo_$(i)_$(j)")
        push_i!(1 - u2, "C5_u2hi_$(i)_$(j)"); push_i!(1 + u2, "C5_u2lo_$(i)_$(j)")
    end

    # ---- cuts ---------------------------------------------------------------
    if "R1" in spec.cuts
        for (i,j) in ps
            u1,u2 = uv(i,j)
            push_i!(u1*(x[i]-x[j]) + u2*(y[i]-y[j]) - 1, "R1_$(i)_$(j)")
        end
    end
    if "R2" in spec.cuts
        for (i,j) in ps
            push_i!((x[i]-x[j])^2 + (y[i]-y[j])^2 - 1, "R2_$(i)_$(j)")
        end
    end
    if "R3" in spec.cuts
        for i in 1:n
            push_i!(g[i] + t[i] - 1,            "R3lo_$i")
            push_i!(spec.sqrt2ub - g[i] - t[i], "R3hi_$i")
        end
    end

    # ---- equalities ---------------------------------------------------------
    for i in 1:n
        push_e!(g[i]^2 + t[i]^2 - 1, "C1_circle_$i")
    end
    for (i,j) in ps
        u1,u2 = uv(i,j)
        push_e!(u1^2 + u2^2 - 1, "C4_unit_$(i)_$(j)")
    end

    pop = vcat(PT[polynomial(1.0*s)], ineq, eq)
    meta = Dict{String,Any}(
        "n" => n, "N" => N, "numeq" => length(eq),
        "n_ineq" => length(ineq),
        "ineq_labels" => ilab, "eq_labels" => elab,
        "cuts" => spec.cuts, "slb" => spec.slb, "smax" => spec.smax,
    )
    return pop, X, meta
end

# ---- clique constructions ----------------------------------------------------

"Tier A: one clique per pair, K_ij = z_i ∪ z_j ∪ {u_ij} ∪ {s} (11 vars)."
function cliques_tierA(n)
    S = si(n)
    [sort(Int[xi(i),yi(i),gi(i),ti(i), xi(j),yi(j),gi(j),ti(j),
              ui(n,i,j)[1], ui(n,i,j)[2], S])
     for (i,j) in pair_list(n)]
end

"Tier B: Tier A + the configuration clique K_0 = {all z_i} ∪ {s} (4n+1 vars)."
function cliques_tierB(n)
    K0 = sort(Int[vcat([[xi(i),yi(i),gi(i),ti(i)] for i in 1:n]...); si(n)])
    vcat(Vector{Int}[K0], cliques_tierA(n))
end

"Dense: a single clique containing every variable."
cliques_dense(n) = Vector{Int}[collect(1:nvars(n))]

export cliques_tierA, cliques_tierB, cliques_dense

# ---- numeric side: known configurations, SAT directions, feasibility ---------

"Four corners of the unit square with centre (cx,cy) and orientation (g,t)."
function corners_num(cx, cy, g, t)
    [ (cx + (s1/2)*g - (s2/2)*t, cy + (s1/2)*t + (s2/2)*g)
      for s1 in (-1,1) for s2 in (-1,1) ]
end

"""
    sat_direction(ci, cj) -> (u1,u2, margin)

Separating Axis Theorem: for two convex polygons that are disjoint, some edge
normal of one of them separates.  `ci`,`cj` are `(cx,cy,g,t)` tuples.  Returns
the unit direction `u` maximising `min_a u·p_a - max_b u·q_b` over the 8
candidate axes, oriented so square i is on the `u·x >= β` side.
"""
function sat_direction(ci, cj)
    (cxi,cyi,gi_,ti_) = ci
    (cxj,cyj,gj_,tj_) = cj
    P = corners_num(cxi,cyi,gi_,ti_)
    Q = corners_num(cxj,cyj,gj_,tj_)
    cands = [(gi_,ti_), (-ti_,gi_), (gj_,tj_), (-tj_,gj_)]
    best = (0.0,0.0,-Inf)
    for (a,b) in cands, sgn in (1,-1)
        nrm = hypot(a,b); nrm < 1e-12 && continue
        u1 = sgn*a/nrm; u2 = sgn*b/nrm
        m = minimum(u1*p[1]+u2*p[2] for p in P) - maximum(u1*q[1]+u2*q[2] for q in Q)
        if m > best[3]; best = (u1,u2,m); end
    end
    return best
end

"""
    check_feasibility(spec, cfg) -> (point, worst_ineq, worst_eq, details)

`cfg` is a vector of `(cx,cy,θ)` triples plus the container side `s`.  Builds the
full lifted point (separating directions from SAT), evaluates every row of the
POP and returns the worst violations.
"""
function check_feasibility(spec::ModelSpec, cfg::Vector{<:Tuple}, sval::Float64)
    n = spec.n
    @assert length(cfg) == n
    N = nvars(n)
    v = zeros(N)
    for (i,(cx,cy,th)) in enumerate(cfg)
        v[xi(i)] = cx; v[yi(i)] = cy; v[gi(i)] = cos(th); v[ti(i)] = sin(th)
    end
    margins = Dict{String,Float64}()
    for (i,j) in pair_list(n)
        ci = (v[xi(i)],v[yi(i)],v[gi(i)],v[ti(i)])
        cj = (v[xi(j)],v[yi(j)],v[gi(j)],v[ti(j)])
        u1,u2,m = sat_direction(ci,cj)
        a,b = ui(n,i,j); v[a] = u1; v[b] = u2
        margins["sep_$(i)_$(j)"] = m
    end
    v[si(n)] = sval
    pop, X, meta = build_pop(spec)
    numeq = meta["numeq"]; nineq = meta["n_ineq"]
    ineqs = pop[2:1+nineq]; eqs = pop[2+nineq:end]
    ivals = [Float64(p(X => v)) for p in ineqs]
    evals = [Float64(p(X => v)) for p in eqs]
    wi = argmin(ivals); we = argmax(abs.(evals))
    return v, (meta["ineq_labels"][wi], ivals[wi]), (meta["eq_labels"][we], evals[we]), margins
end

end # module
