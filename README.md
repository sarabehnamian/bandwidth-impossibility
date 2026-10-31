# Bandwidth impossibility: k-set agreement thresholds

Exhaustive computations for the "summarization barrier" paper. The model has
n agents with inputs in V. In each round every agent broadcasts one symbol
from an alphabet of size m to its out-neighbours. Ring and chain are directed:
agent i hears only agent i-1.

## Layout

| path | contents |
|---|---|
| `paper/kset_threshold.tex`, `.pdf` | threshold theorem, plus the new subsection *Other topologies and two rounds* |
| `sat/kset_sat.py` | original one-round, complete-graph SAT check (unchanged) |
| `sat/kset_general.py` | SAT encoder for **any digraph and any number of rounds R** (fully adaptive messages); every SAT model is re-verified by simulation |
| `sat/thresholds_r1.py` | task 2 sweep, writes `results/thresholds_r1*.{csv,md}` |
| `sat/thresholds_r2.py` | task 3 sweep, writes `results/thresholds_r2*.{csv,md}` |
| `results/report03/` | the student's run (notebook, `results.zip`, unpacked outputs) |
| `toolkit/` | **not present**: `mas-search-v3.zip` was not available |

Every search is exhaustive. CaDiCaL is a complete solver, so UNSAT means no
protocol exists anywhere in the protocol space. There is no sampling. Requires
`pip install python-sat`.

```bash
python3 sat/thresholds_r1.py
```

```bash
python3 sat/thresholds_r2.py
```

## Findings

### Task 2: one round, all topologies (`results/thresholds_r1.md`)

The table gives the threshold T: k-set agreement is solvable iff |V| <= T. It
covers 150 SAT instances, checking every |V| from k+1 to m+k. The largest
protocol space is about 10^516.

| n | k | m | m+k-1 | complete | star | in_star | out_star | chain | ring |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 1 |
| 3 | 1 | 3 | 3 | 3 | 3 | 1 | 3 | 1 | 1 |
| 3 | 2 | 2 | 3 | 3 | 3 | 2 | 2 | 2 | 3 |
| 3 | 2 | 3 | 4 | 4 | 4 | 3 | 3 | 3 | 4 |
| 4 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 1 | 1 |
| 4 | 1 | 3 | 3 | 3 | 3 | 1 | 3 | 1 | 1 |
| 4 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 |
| 4 | 2 | 3 | 4 | 4 | 3 | 2 | 3 | 3 | 3 |
| 4 | 3 | 2 | 4 | 4 | 4 | 3 | 3 | 3 | 4 |
| 4 | 3 | 3 | 5 | 5 | 5 | 4 | 3 | 4 | 5 |

The topologies are: `star` = hub and leaves with edges in both directions;
`in_star` = leaves send to the hub only; `out_star` = hub sends to the leaves
only.

* The complete graph always reaches m+k-1, which matches the theorem.
* **Proved (new):** one-round consensus on a digraph is solvable iff some
  agent is an in-neighbour of every other agent, and then exactly for |V| <= m.
  Otherwise only |V| = 1 is solvable. Deaf agents (in-degree 0) must output
  their own input, so k+1 deaf agents force the threshold down to k.
* **Conjectures** (stated as such in the paper):
  * for k = n-1 the bound m+n-2 is attained iff no agent is deaf;
  * the out-star threshold is max(m,k);
  * the chain threshold is m+k-2 for k >= 2.
* **Correction to the paper's remark.** Report 03's one-round "star" is really
  the in-star: its reachability data shows that leaves hear nothing. On the
  bidirectional star, n=3, k=2, m=2, |V|=3 is solvable. An explicit protocol,
  checked on all inputs, is given in the paper. The remark has been updated.
  With that reading, the new encoder agrees with all 46 consensus and k-set
  cells of report 03.

### Task 3: two rounds, complete graph, n = 3 (`results/thresholds_r2.md`)

| task | m | threshold | m^2+k-1 |
|---|---|---|---|
| consensus | 2 | 4 | 4 |
| consensus | 3 | M3T | 9 |
| 2-set | 2 | 5 | 5 |

**The consensus threshold equals m^2.** Adaptivity in round 2 does not help.
This is proved in the paper for all R, n and topologies. With |V| >= m^R+1, a
nested-fibre pigeonhole argument together with the product-fibre lemma gives a
contradiction. The leader protocol achieves m^R on the complete graph.

For k-set agreement, m^R+k-1 is achievable, by the one-round protocol over
alphabet m^R. The 2-set cell matches this exactly. Whether this is the exact
threshold for all k remains a **conjecture**.

### Task 4: not done

The toolkit (`mas-search-v3.zip`) was not provided, so the `counting_fires`
question was skipped, as instructed.
