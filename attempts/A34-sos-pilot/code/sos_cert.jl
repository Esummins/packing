# A34 T2b — extract ONE exact-rational SOS certificate for the n=2 min-s POP.
#
# Solves the DUAL (SOS) side of the dense level-2 relaxation directly in JuMP, so
# the Gram matrices are decision variables and can be read off verbatim:
#
#     s - lambda = sigma_0 + sum_k sigma_k * g_k + sum_l phi_l * h_l
#
# with sigma_0 = <B2, Q0 B2> (B2 = monomials of deg <= 2, |B2| = 78),
#      sigma_k = <B1, Qk B1> (B1 = monomials of deg <= 1, |B1| = 12),
#      phi_l   = free polynomial of deg <= 2.
#
# lambda is FIXED (below the relaxation optimum 1.70711104) so that the Gram
# cone has nonempty interior; we then push the Grams to have min eigenvalue >= t
# by writing Q = P + t*I with P PSD.  That makes the rational rounding safe.
#
# usage: julia --project=code code/sos_cert.jl <lambda> <mode> <tval> <solver>
#   mode = "maxt"  -> maximise t (with a trace cap); prints t*
#   mode = "fix"   -> fix t = tval, minimise total trace, and DUMP the certificate

include(joinpath(@__DIR__, "model.jl"))
using .A34Model
using DynamicPolynomials, MultivariatePolynomials
using JuMP, LinearAlgebra, JSON, Serialization
import Clarabel, SCS

const NV = 11
const VNAMES = ["x1","y1","g1","t1","x2","y2","g2","t2","u1","u2","s"]

# ---------------------------------------------------------------- monomials --
function monos_upto(d::Int)
    res = NTuple{NV,Int}[]
    cur = zeros(Int, NV)
    function rec(pos, rem)
        if pos > NV
            push!(res, NTuple{NV,Int}(cur)); return
        end
        for e in 0:rem
            cur[pos] = e
            rec(pos+1, rem-e)
        end
        cur[pos] = 0
    end
    rec(1, d)
    sort!(res, by = e -> (sum(e), e))
    return res
end

expvec(m, X) = ntuple(i -> Int(MultivariatePolynomials.degree(m, X[i])), NV)
addexp(a::NTuple{NV,Int}, b::NTuple{NV,Int}) = ntuple(i -> a[i]+b[i], NV)

const MP = MultivariatePolynomials
polyterms(p, X) = [(Float64(MP.coefficient(tm)), expvec(MP.monomial(tm), X)) for tm in MP.terms(p)]

function monostr(e::NTuple{NV,Int})
    parts = String[]
    for i in 1:NV
        e[i] == 0 && continue
        push!(parts, e[i] == 1 ? VNAMES[i] : string(VNAMES[i], "^", e[i]))
    end
    isempty(parts) ? "1" : join(parts, "*")
end

# ------------------------------------------------------------- rationalising --
const DEN = big(10)^12
ratq(v::Real) = Rational{BigInt}(round(BigInt, big(v) * DEN), DEN)
rstr(q::Rational{BigInt}) = string(numerator(q), "/", denominator(q))
# exact rationals for the model's structural coefficients (0.5, 1, 1.4142136, ...)
ratc(v::Real) = Rational{BigInt}(rationalize(BigInt, Float64(v), tol = 1e-11))

# ------------------------------------------------------------------ the POP --
const LAM    = length(ARGS) >= 1 ? parse(Float64, ARGS[1]) : 1.70
const MODE   = length(ARGS) >= 2 ? ARGS[2] : "maxt"
const TVAL   = length(ARGS) >= 3 ? parse(Float64, ARGS[3]) : 1e-3
const SOLVER = length(ARGS) >= 4 ? ARGS[4] : "Clarabel"
const TOL    = length(ARGS) >= 5 ? parse(Float64, ARGS[5]) : 1e-9

spec = ModelSpec(2; cuts = ["R1","R2","R3"], slb = 1.0, smax = 4.0)
pop, X, meta = build_pop(spec)
nineq = meta["n_ineq"]; numeq = meta["numeq"]
@assert length(X) == NV
ineqs = pop[2:1+nineq]
eqs   = pop[2+nineq:end]
ilab  = meta["ineq_labels"]; elab = meta["eq_labels"]
println("POP: N=$NV  ineq=$nineq  eq=$numeq  lambda=$LAM  mode=$MODE  t=$TVAL  solver=$SOLVER")

B2 = monos_upto(2); B1 = monos_upto(1)
n2 = length(B2); n1 = length(B1)
println("basis sizes: |B2|=$n2  |B1|=$n1")

gterms = [polyterms(p, X) for p in ineqs]
hterms = [polyterms(p, X) for p in eqs]

# ----------------------------------------------------------------- the SDP ---
function make_solver()
    if SOLVER == "Clarabel"
        m = Model(Clarabel.Optimizer)
        set_optimizer_attribute(m, "verbose", true)
        set_optimizer_attribute(m, "max_iter", 500)
        set_optimizer_attribute(m, "tol_gap_abs", TOL)
        set_optimizer_attribute(m, "tol_gap_rel", TOL)
        set_optimizer_attribute(m, "tol_feas", TOL)
        set_optimizer_attribute(m, "tol_ktratio", 1e-6)
        return m
    else
        m = Model(SCS.Optimizer)
        set_optimizer_attribute(m, "verbose", 1)
        set_optimizer_attribute(m, "max_iters", 400_000)
        set_optimizer_attribute(m, "eps_abs", TOL)
        set_optimizer_attribute(m, "eps_rel", TOL)
        return m
    end
end

const OUTTAG = length(ARGS) >= 7 ? ARGS[7] : ""
const FLOATDUMP = joinpath(@__DIR__, "..", "results", "floats$(OUTTAG).jls")

const ZERO = ntuple(_ -> 0, NV)
const SMON = ntuple(i -> (i == NV ? 1 : 0), NV)

function build_and_solve()
model = make_solver()
@variable(model, P0[1:n2, 1:n2], PSD)
Pk = [@variable(model, [1:n1, 1:n1], PSD, base_name = "P$k") for k in 1:nineq]
@variable(model, phi[1:numeq, 1:n2])
if MODE == "fix"
    tvar = TVAL
else
    @variable(model, tvar >= 0)
    @constraint(model, tvar <= 1.0)
end

acc = Dict{NTuple{NV,Int}, AffExpr}()
function bump!(key, ex)
    if haskey(acc, key)
        add_to_expression!(acc[key], ex)
    else
        acc[key] = AffExpr(0.0); add_to_expression!(acc[key], ex)
    end
end

# sigma_0 = <B2, Q0 B2>,  Q0 = P0 + tvar*I
for i in 1:n2, j in i:n2
    key = addexp(B2[i], B2[j])
    if i == j
        bump!(key, P0[i,i] + tvar)
    else
        bump!(key, 2.0 * P0[i,j])
    end
end
# sigma_k * g_k,  Qk = Pk + tvar*I
for k in 1:nineq
    Pkk = Pk[k]
    for i in 1:n1, j in i:n1
        base = addexp(B1[i], B1[j])
        ex = (i == j) ? (Pkk[i,i] + tvar) : (2.0 * Pkk[i,j])
        for (c, e) in gterms[k]
            bump!(addexp(base, e), c * ex)
        end
    end
end
# phi_l * h_l
for l in 1:numeq, i in 1:n2
    for (c, e) in hterms[l]
        bump!(addexp(B2[i], e), c * phi[l,i])
    end
end

# right-hand side: s - lambda
rhs = Dict{NTuple{NV,Int}, Float64}(SMON => 1.0, ZERO => -LAM)

allkeys = union(Set(keys(acc)), Set(keys(rhs)))
println("coefficient-matching equations: ", length(allkeys))
for key in allkeys
    ex = get(acc, key, AffExpr(0.0))
    @constraint(model, ex == get(rhs, key, 0.0))
end

trtot = tr(P0) + sum(tr(Pk[k]) for k in 1:nineq)
if MODE == "fix"
    # pure feasibility: an interior-point solver returns the analytic centre of the
    # feasible set, i.e. the MAXIMUM-rank Gram tuple -- exactly what we want before
    # rational rounding.  (A trace objective would push towards low rank: bad.)
    @objective(model, Min, 0.0 * trtot)
else
    @constraint(model, trtot <= 1e5)
    @objective(model, Max, tvar)
end

t0 = time()
optimize!(model)
el = round(time() - t0, digits = 2)
println("term_status=", termination_status(model), " prim=", primal_status(model),
        " dual=", dual_status(model), "  obj=", try objective_value(model) catch; NaN end,
        "  time=", el, "s")

tstar = MODE == "fix" ? TVAL : value(tvar)
println("t = ", tstar)

Q0v = Matrix(value.(P0)) + tstar * I
Qkv = [Matrix(value.(Pk[k])) + tstar * I for k in 1:nineq]
phiv = Matrix(value.(phi))
return (Q0v, Qkv, phiv, tstar, el, string(termination_status(model)), length(allkeys))
end # build_and_solve

if MODE == "round"
    Q0v, Qkv, phiv, tstar, el, termstat, nkeys = deserialize(FLOATDUMP)
    println("reloaded float point from ", FLOATDUMP)
else
    Q0v, Qkv, phiv, tstar, el, termstat, nkeys = build_and_solve()
    serialize(FLOATDUMP, (Q0v, Qkv, phiv, tstar, el, termstat, nkeys))
end

e0 = eigvals(Symmetric(Q0v))
mineigs = [minimum(eigvals(Symmetric(Qkv[k]))) for k in 1:nineq]
println("min eig sigma_0 Gram = ", minimum(e0), "   max = ", maximum(e0))
println("min over sigma_k Grams = ", minimum(mineigs))
println("max |Gram entry| = ", max(maximum(abs, Q0v), maximum(maximum(abs, Q) for Q in Qkv)),
        "   max |phi| = ", maximum(abs, phiv))

if MODE == "maxt"
    println("DONE (maxt probe)")
    exit(0)
end

# ---------------------------------------------------- rational certificate ---
# The Gram matrices are PROVABLY singular here (see notes): setting gamma=sigma=u=0
# in the degree-4 part of the identity leaves [sigma_0]_4 + [sigma_R2]_2*((dx)^2+(dy)^2) = 0
# with both summands >= 0, so sigma_0's top block must have a large kernel.  Hence the
# brief's "min eig >= 2e-7" precondition can never hold and a strictly positive shift is
# MANDATORY.  We take the smallest shift that survives rational rounding, and pay for it
# out of the verifier's residual margin.
const EPSFLOOR = length(ARGS) >= 6 ? parse(Float64, ARGS[6]) : 0.0
worstneg = max(0.0, -min(minimum(e0), minimum(mineigs)))
ADD_EPS = max(EPSFLOOR, 20 * worstneg, 1e-11)
# box bounds used in the certificate (must contain the feasible set)
cbox = Float64[4,4,1,1,4,4,1,1,1,1,4]
mbound(e) = prod(cbox[i]^e[i] for i in 1:NV)
costQ0 = sum(mbound(b)^2 for b in B2)
costQk = sum((sum(mbound(b)^2 for b in B1)) * sum(abs(c) * mbound(e) for (c, e) in gterms[k])
             for k in 1:nineq)
epscost = ADD_EPS * (costQ0 + costQk)
println("worst negative eigenvalue = ", -worstneg, "  -> eps = ", ADD_EPS,
        "   predicted residual cost of eps*I = ", epscost)
Q0v = Q0v + ADD_EPS * I
for k in 1:nineq; Qkv[k] = Qkv[k] + ADD_EPS * I; end

symq(M) = [ratq((M[i,j] + M[j,i]) / 2) for i in axes(M,1), j in axes(M,2)]
Q0r = symq(Q0v)
Qkr = [symq(Qkv[k]) for k in 1:nineq]
lamr = ratq(LAM)

# --- exact rational polynomial arithmetic, then normal-form reduction ---------
const RQ = Rational{BigInt}
const RPoly = Dict{NTuple{NV,Int}, RQ}
addto!(d::RPoly, e, v) = (w = get(d, e, zero(RQ)) + v; w == 0 ? delete!(d, e) : (d[e] = w); d)

function sos_rpoly(Q, B)
    d = RPoly(); n = length(B)
    for i in 1:n, j in 1:n
        addto!(d, addexp(B[i], B[j]), Q[i,j])
    end
    d
end

# D := (s - lambda) - sigma_0 - sum_k sigma_k g_k   (exact)
D = RPoly()
addto!(D, SMON, one(RQ)); addto!(D, ZERO, -lamr)
for (e, v) in sos_rpoly(Q0r, B2); addto!(D, e, -v); end
for k in 1:nineq
    sk = sos_rpoly(Qkr[k], B1)
    for (e, v) in sk, (c, eg) in gterms[k]
        addto!(D, addexp(e, eg), -v * ratc(c))
    end
end

# reduce D modulo h1 = g1^2+t1^2-1, h2 = g2^2+t2^2-1, h3 = u1^2+u2^2-1
# (leading monomials g1^2, g2^2, u1^2; quotients are the equality multipliers phi_l)
const RED = [(3, 4), (7, 8), (9, 10)]     # (leading var index, partner var index)
phiR = [RPoly() for _ in 1:numeq]
for (l, (lv, pv)) in enumerate(RED)
    while true
        tgt = nothing
        for (e, _) in D; if e[lv] >= 2; tgt = e; break; end; end
        tgt === nothing && break
        c = D[tgt]
        q = ntuple(i -> i == lv ? tgt[i] - 2 : tgt[i], NV)
        qt = ntuple(i -> i == pv ? q[i] + 2 : q[i], NV)
        addto!(phiR[l], q, c)
        addto!(D, tgt, -c)          # remove c*m
        addto!(D, q,  c)            # + c*q*(1 - partner^2)
        addto!(D, qt, -c)
    end
end
for l in 1:numeq
    dmax = maximum(sum(e) for e in keys(phiR[l]); init = 0)
    @assert dmax <= 2 "phi_$l has degree $dmax > 2"
end
const cboxI = BigInt[4,4,1,1,4,4,1,1,1,1,4]
mboundI(e) = prod(cboxI[i]^e[i] for i in 1:NV)
resid_bound = sum(abs(c) * RQ(mboundI(e)) for (e, c) in D; init = zero(RQ))
println("residual monomials: ", length(D), "   |r| <= ", Float64(resid_bound))
println("PREDICTED certified lambda' = ", Float64(lamr - resid_bound))

polyjson(tms) = Dict(monostr(e) => rstr(ratc(c)) for (c, e) in tms)

constraints = Any[]
for k in 1:nineq
    push!(constraints, Dict("name" => ilab[k], "type" => "ineq", "poly" => polyjson(gterms[k])))
end
for l in 1:numeq
    push!(constraints, Dict("name" => elab[l], "type" => "eq", "poly" => polyjson(hterms[l])))
end

sosblocks = Any[Dict("constraint" => -1,
                     "basis" => [monostr(e) for e in B2],
                     "gram" => [[rstr(Q0r[i,j]) for j in 1:n2] for i in 1:n2])]
for k in 1:nineq
    push!(sosblocks, Dict("constraint" => k - 1,   # 0-based index into "constraints"
                          "basis" => [monostr(e) for e in B1],
                          "gram" => [[rstr(Qkr[k][i,j]) for j in 1:n1] for i in 1:n1]))
end
eqmult = Any[]
for l in 1:numeq
    d = Dict{String,String}()
    for (e, q) in phiR[l]
        q == 0 && continue
        d[monostr(e)] = rstr(q)
    end
    isempty(d) && (d["1"] = "0/1")
    push!(eqmult, Dict("constraint" => nineq + l - 1, "poly" => d))
end

# box: valid OUTER box for the feasible set (s <= 4 => centres in [0.5, 3.5])
box = Dict{String,Any}()
for v in ("x1","y1","x2","y2"); box[v] = ["0/1", "4/1"]; end
for v in ("g1","t1","g2","t2"); box[v] = ["0/1", "1/1"]; end
for v in ("u1","u2");           box[v] = ["-1/1", "1/1"]; end
box["s"] = ["1/1", "4/1"]

cert = Dict(
    "lambda" => rstr(lamr),
    "vars" => VNAMES,
    "box" => box,
    "objective" => Dict("s" => "1/1"),
    "constraints" => constraints,
    "sos" => sosblocks,
    "eqmult" => eqmult,
)

outdir = joinpath(@__DIR__, "..", "certs")
mkpath(outdir)
outfile = joinpath(outdir, "n2_lvl2_cert$(OUTTAG).json")
open(outfile, "w") do io; JSON.print(io, cert); end
println("wrote ", outfile, "  (", round(filesize(outfile)/1e6, digits=2), " MB)")

meta_out = Dict(
    "lambda_fixed" => LAM, "t_margin" => tstar, "solver" => SOLVER, "tol" => TOL,
    "eps_added" => ADD_EPS, "eps_residual_cost_pred" => epscost,
    "worst_negative_eig_before_shift" => -worstneg,
    "min_eig_sigma0" => minimum(e0), "max_eig_sigma0" => maximum(e0),
    "min_eig_over_sigma_k" => minimum(mineigs),
    "max_abs_gram_entry" => max(maximum(abs, Q0v), maximum(maximum(abs, Q) for Q in Qkv)),
    "max_abs_phi_solver" => maximum(abs, phiv),
    "max_abs_phi_reduced" => Float64(maximum(abs(v) for l in 1:numeq for v in values(phiR[l]); init=zero(RQ))),
    "residual_terms" => length(D),
    "residual_bound" => Float64(resid_bound),
    "lambda_certified_pred" => Float64(lamr - resid_bound),
    "term_status" => termstat,
    "solve_time_s" => el, "n_ineq" => nineq, "n_eq" => numeq,
    "basis2" => n2, "basis1" => n1, "n_coef_eqs" => nkeys,
    "rational_denominator" => "10^12",
)
open(joinpath(@__DIR__, "..", "results", "cert_meta$(OUTTAG).json"), "w") do io
    JSON.print(io, meta_out, 2)
end
println(JSON.json(meta_out, 2))
