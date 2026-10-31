"""Task 2: exact one-round |V| thresholds for k-set agreement on directed graphs.

For every (topology, n, k, m) we decide solvability for EVERY |V| in
k+1 .. m+k by exhaustive SAT (|V| <= k is trivially solvable; |V| = m+k is
impossible by the lower-bound theorem, and is re-checked here).  The threshold
T is the largest solvable |V|; we also check that solvability is monotone
(solvable set = {1..T}), which it must be since restricting inputs preserves
solvability.

Writes results/thresholds_r1.csv, results/thresholds_r1.md and
results/thresholds_r1_raw.csv (one row per SAT call).
"""
import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kset_general import solvable, TOPOLOGIES, log10_protocols

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'results')


def main():
    os.makedirs(OUT, exist_ok=True)
    raw, table = [], []
    for n in (3, 4):
        for k in range(1, n):
            for m in (2, 3):
                for topo in TOPOLOGIES:
                    sol = {}
                    for V in range(k + 1, m + k + 1):
                        t0 = time.time()
                        r = solvable(n, V, m, k, topo, R=1)
                        dt = time.time() - t0
                        sol[V] = r
                        raw.append(dict(topology=topo, n=n, k=k, m=m, V=V,
                                        solvable=r, seconds=round(dt, 2),
                                        log10_protocols=round(log10_protocols(n, V, m, topo, 1), 1)))
                        print(f'{topo:9} n={n} k={k} m={m} |V|={V}: '
                              f'{"SOLVABLE" if r else "impossible"} ({dt:.1f}s)', flush=True)
                    T = max([k] + [V for V, r in sol.items() if r])
                    monotone = all(sol[V] == (V <= T) for V in sol)
                    assert monotone, (topo, n, k, m, sol)
                    assert not sol[m + k], 'lower bound theorem violated?!'
                    table.append(dict(topology=topo, n=n, k=k, m=m, threshold=T,
                                      upper_bound=m + k - 1,
                                      tight=(T == m + k - 1)))
    with open(os.path.join(OUT, 'thresholds_r1_raw.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(raw[0]))
        w.writeheader(); w.writerows(raw)
    with open(os.path.join(OUT, 'thresholds_r1.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(table[0]))
        w.writeheader(); w.writerows(table)

    # markdown: one row per (n,k,m), one column per topology
    lines = ['# One-round k-set agreement: exact |V| thresholds',
             '',
             'Largest |V| for which a one-round protocol with m-ary broadcast exists '
             '(solvable iff |V| <= entry). Exhaustive SAT over all protocols for every '
             '|V| in k+1..m+k. `m+k-1` is the general upper bound (lower-bound theorem).',
             '',
             'Topologies: `complete`; `star` = hub 0 <-> leaves (both directions); '
             '`in_star` = leaves -> hub only; `out_star` = hub -> leaves only; '
             '`chain` = 0 -> 1 -> ... -> n-1; `ring` = directed cycle, i hears i-1.',
             '',
             '| n | k | m | m+k-1 | ' + ' | '.join(TOPOLOGIES) + ' |',
             '|---|---|---|---|' + '---|' * len(TOPOLOGIES)]
    for n in (3, 4):
        for k in range(1, n):
            for m in (2, 3):
                row = {r['topology']: r['threshold'] for r in table
                       if (r['n'], r['k'], r['m']) == (n, k, m)}
                lines.append(f'| {n} | {k} | {m} | {m + k - 1} | ' +
                             ' | '.join(str(row[t]) for t in TOPOLOGIES) + ' |')
    open(os.path.join(OUT, 'thresholds_r1.md'), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
