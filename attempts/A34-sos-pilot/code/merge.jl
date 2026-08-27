# Merge results/part_*.json into results/validation.json and print the table.
using JSON
R = joinpath(@__DIR__, "..", "results")
all = Any[]
for f in sort(readdir(R))
    startswith(f, "part_") && endswith(f, ".json") || continue
    try; append!(all, JSON.parsefile(joinpath(R,f))); catch e; @warn "skip $f" e; end
end
open(joinpath(R,"validation.json"),"w") do io; JSON.print(io, all, 2); end

hdr = ["n","tier","lvl","cuts","bound","maxblk","blocks","time_s","status"]
println(join(rpad.(hdr, [4,6,4,10,20,7,16,9,12]), " "))
for r in sort(all, by = x->(x["n"], x["tier"], x["level"], join(x["cuts"],"+")))
    b = r["bound"] === nothing ? "-" : string(round(Float64(r["bound"]), digits=8))
    println(join(rpad.([string(r["n"]), r["tier"], string(r["level"]),
        isempty(r["cuts"]) ? "none" : join(r["cuts"],"+"), b,
        string(get(r,"max_block","?")),
        string(get(r,"moment_block_sizes","?")),
        string(get(r,"time_s","?")), string(get(r,"status","?"))],
        [4,6,4,10,20,7,16,9,12]), " "))
end
println("\n", length(all), " records -> results/validation.json")
