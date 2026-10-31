# One-round k-set agreement: exact |V| thresholds

Largest |V| for which a one-round protocol with m-ary broadcast exists (solvable iff |V| <= entry). Exhaustive SAT over all protocols for every |V| in k+1..m+k. `m+k-1` is the general upper bound (lower-bound theorem).

Topologies: `complete`; `star` = hub 0 <-> leaves (both directions); `in_star` = leaves -> hub only; `out_star` = hub -> leaves only; `chain` = 0 -> 1 -> ... -> n-1; `ring` = directed cycle, i hears i-1.

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
