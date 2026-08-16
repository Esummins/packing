"""Synthetic 11-square certificate (container 4.0001) with big denominators, used only to
time `decide` vs `native_decide` before the real A03 data exists.  Not a bound on s(11)."""
import json
sq = []
for j in range(2):
    for i in range(4):
        x0 = f"{i*100002+1}/100000"; y0 = f"{j*100002+1}/100000"
        x1 = f"{i*100002+100001}/100000"; y1 = f"{j*100002+100001}/100000"
        sq.append({"corners": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]})
sq.append({"corners": [["300007/100000","200005/100000"],["400007/100000","200005/100000"],
                        ["400007/100000","300005/100000"],["300007/100000","300005/100000"]]})
t = "500000000001/1000000000000"
sq.append({"center": ["75/100", "3"], "t": t})
sq.append({"center": ["225/100", "3"], "t": t})
json.dump({"description": "synthetic timing test, NOT a bound", "container_side": "40001/10000",
           "squares": sq}, open("synthetic11.json", "w"), indent=1)
print("wrote synthetic11.json")
