"""Task 3: two-round thresholds on the complete graph, n = 3 (fully adaptive
round-2 messages).  Exhaustive SAT for every |V| in k+1 .. m^2+k (plus one more
for consensus as a margin check).

Writes results/thresholds_r2.csv and results/thresholds_r2.md.
Usage: python3 thresholds_r2.py            (all cells)
       python3 thresholds_r2.py m k        (one (m,k) pair)
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kset_general import solvable, log10_protocols

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')
CELLS = [(2, 1), (3, 1), (2, 2)]   # (m, k); consensus for m=2,3 + one 2-set cell
N, R, TOPO = 3, 2, 'complete'


def run(m, k):
    rows = []
    for V in range(k + 1, m ** R + k + 1):
        t0 = time.time()
        r = solvable(N, V, m, k, TOPO, R=R)
        dt = time.time() - t0
        rows.append(dict(topology=TOPO, n=N, R=R, k=k, m=m, V=V, solvable=r,
                         seconds=round(dt, 1),
                         log10_protocols=round(log10_protocols(N, V, m, TOPO, R), 1)))
        print(f'm={m} k={k} |V|={V}: {"SOLVABLE" if r else "impossible"} ({dt:.1f}s)',
              flush=True)
    return rows


def main():
    cells = [tuple(map(int, sys.argv[1:3]))] if len(sys.argv) > 2 else CELLS
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, 'thresholds_r2_raw.csv')
    old = []
    if os.path.exists(path):
        old = [r for r in csv.DictReader(open(path))
               if (int(r['m']), int(r['k'])) not in cells]
    new = []
    for m, k in cells:
        new += run(m, k)
    allrows = old + [{kk: str(v) for kk, v in r.items()} for r in new]
    allrows.sort(key=lambda r: (int(r['k']), int(r['m']), int(r['V'])))
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(allrows[0]))
        w.writeheader(); w.writerows(allrows)

    # summary table
    summ = []
    for (m, k) in sorted({(int(r['m']), int(r['k'])) for r in allrows}, key=lambda t: (t[1], t[0])):
        sol = {int(r['V']): r['solvable'] == 'True' for r in allrows
               if (int(r['m']), int(r['k'])) == (m, k)}
        T = max([k] + [V for V, s in sol.items() if s])
        assert all(sol[V] == (V <= T) for V in sol), sol
        summ.append(dict(topology=TOPO, n=N, R=R, k=k, m=m, threshold=T,
                         m_squared_plus_k_minus_1=m * m + k - 1,
                         checked_V=f'{min(sol)}..{max(sol)}'))
    with open(os.path.join(OUT, 'thresholds_r2.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(summ[0]))
        w.writeheader(); w.writerows(summ)
    lines = ['# Two-round thresholds, complete graph, n = 3',
             '',
             'Round-2 messages may depend on the agent\'s input and everything it received '
             'in round 1. Exhaustive SAT for every listed |V|.',
             '',
             '| task | m | threshold | m^2+k-1 | |V| checked |',
             '|---|---|---|---|---|']
    for s in summ:
        task = 'consensus' if s['k'] == 1 else f"{s['k']}-set"
        lines.append(f"| {task} | {s['m']} | {s['threshold']} | "
                     f"{s['m_squared_plus_k_minus_1']} | {s['checked_V']} |")
    open(os.path.join(OUT, 'thresholds_r2.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
