"""Exhaustive SAT check: k-set agreement on an arbitrary directed graph, R rounds,
m-valued messages (one broadcast symbol per agent per round).

Model
-----
* n agents, agent i holds x_i in V = {0..|V|-1}.
* In round r agent j broadcasts s^r_j(x_j, h_j^{<r}) in [m], where h_j^{<r} is the
  tuple of symbols j received from its in-neighbours in rounds 1..r-1.
  (Full adaptivity: a round-r message may depend on everything received before.)
* After R rounds agent i decides d_i(x_i, h_i^{<=R}) in V.
* k-set agreement: on every input vector every output is some agent's input
  (validity) and at most k distinct values are output (agreement).

The CNF is satisfiable iff such a protocol exists, so an UNSAT answer from the
(complete) solver is an exhaustive impossibility proof over the whole protocol space.
Every SAT answer is additionally re-checked by simulating the extracted protocol
on all |V|^n inputs.

Encoding
--------
s[r,j,x,h,c]   protocol: agent j, input x, history h sends c in round r  (exactly one c)
d[i,x,h,v]     protocol: agent i, input x, full history h decides v     (exactly one v)
t[r,xv,j,c]    "on input vector xv, agent j sends c in round r"  (implied, Horn-style)
o[xv,v]        "value v is output by someone on input xv"         (implied)
t and o only occur positively in the heads of their defining implications and
negatively elsewhere, so their least model is the true semantics; this makes the
encoding exactly equivalent to the existence of a protocol.
"""
import itertools
import sys
from pysat.formula import IDPool, CNF
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153


# ---------------------------------------------------------------- topologies
def in_neighbours(topology, n):
    """Return list N[i] = sorted in-neighbours of agent i."""
    if topology == 'complete':
        return [[j for j in range(n) if j != i] for i in range(n)]
    if topology == 'star':          # hub 0 <-> each leaf (both directions)
        return [list(range(1, n))] + [[0] for _ in range(1, n)]
    if topology == 'in_star':       # leaves -> hub only (hub hears all, leaves hear nobody)
        return [list(range(1, n))] + [[] for _ in range(1, n)]
    if topology == 'out_star':      # hub -> leaves only
        return [[]] + [[0] for _ in range(1, n)]
    if topology == 'chain':         # directed path 0 -> 1 -> ... -> n-1
        return [[]] + [[i - 1] for i in range(1, n)]
    if topology == 'ring':          # directed cycle, i hears i-1 only
        return [[(i - 1) % n] for i in range(n)]
    raise ValueError(topology)


TOPOLOGIES = ('complete', 'star', 'in_star', 'out_star', 'chain', 'ring')


def histories(N_i, m, rounds):
    """All possible receive-histories of an agent with in-neighbours N_i after
    `rounds` rounds, as tuples of length rounds*len(N_i) (round-major)."""
    return list(itertools.product(range(m), repeat=rounds * len(N_i)))


def log10_protocols(n, V, m, topology, R):
    """log10 of the number of distinct protocols (message tables + decision
    tables) that the SAT instance ranges over, before symmetry breaking."""
    import math
    N = in_neighbours(topology, n)
    tot = 0.0
    for j in range(n):
        deg = len(N[j])
        for r in range(1, R + 1):
            tot += V * m ** (deg * (r - 1)) * math.log10(m)
        tot += V * m ** (deg * R) * math.log10(V)
    return tot


# ---------------------------------------------------------------- encoder
def build(n, V, m, k, N, R, value_sym=False):
    pool = IDPool()
    cnf = CNF()

    def eq1(lits):
        cnf.extend(CardEnc.equals(lits=lits, bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    s = lambda r, j, x, h, c: pool.id(('s', r, j, x, h, c))
    d = lambda i, x, h, v: pool.id(('d', i, x, h, v))
    t = lambda r, xv, j, c: pool.id(('t', r, xv, j, c))
    o = lambda xv, v: pool.id(('o', xv, v))

    # protocol tables are total functions
    for j in range(n):
        for r in range(1, R + 1):
            for x in range(V):
                for h in histories(N[j], m, r - 1):
                    eq1([s(r, j, x, h, c) for c in range(m)])
        for x in range(V):
            for h in histories(N[j], m, R):
                eq1([d(j, x, h, v) for v in range(V)])

    # light symmetry breaking: per-agent relabelling of the round-1 alphabet
    # (receivers can relabel too) lets us fix s^1_j(0) = 0.  Sound and complete.
    for j in range(n):
        cnf.append([s(1, j, 0, (), 0)])
    # Optional: the task is invariant under permutations of V.  Permute V so
    # that agent 0's round-1 fibres are contiguous intervals, then relabel agent
    # 0's round-1 symbols in order of first appearance: s^1_0 becomes a
    # non-decreasing map with steps of 0 or 1.  (The other fixings above are
    # message relabellings applied afterwards, so they remain compatible.)
    if value_sym:
        for x in range(V - 1):
            for c in range(m):
                nxt = [s(1, 0, x + 1, (), c)] + ([s(1, 0, x + 1, (), c + 1)] if c + 1 < m else [])
                cnf.append([-s(1, 0, x, (), c)] + nxt)
    # Later rounds: agent j's round-r alphabet may be relabelled separately for
    # each history h, provided every out-neighbour i of j can reconstruct h
    # (every in-neighbour l of j is i itself or an in-neighbour of i).  Then we
    # may fix s^r_j(0, h) = 0.  On the complete graph this always applies.
    for j in range(n):
        outs = [i for i in range(n) if j in N[i]]
        if all(l == i or l in N[i] for i in outs for l in N[j]):
            for r in range(2, R + 1):
                for h in histories(N[j], m, r - 1):
                    cnf.append([s(r, j, 0, h, 0)])

    def hist_lits(xv, i, h, upto):
        """Negated t-literals asserting that agent i's history equals h."""
        lits = []
        deg = len(N[i])
        for r in range(1, upto + 1):
            for a, l in enumerate(N[i]):
                lits.append(-t(r, xv, l, h[(r - 1) * deg + a]))
        return lits

    for xv in itertools.product(range(V), repeat=n):
        # message semantics
        for r in range(1, R + 1):
            for j in range(n):
                for h in histories(N[j], m, r - 1):
                    pre = hist_lits(xv, j, h, r - 1)
                    for c in range(m):
                        cnf.append(pre + [-s(r, j, xv[j], h, c), t(r, xv, j, c)])
        # decisions, validity
        allowed = set(xv)
        for i in range(n):
            for h in histories(N[i], m, R):
                pre = hist_lits(xv, i, h, R)
                for v in range(V):
                    if v in allowed:
                        cnf.append(pre + [-d(i, xv[i], h, v), o(xv, v)])
                    else:
                        cnf.append(pre + [-d(i, xv[i], h, v)])
        # agreement
        lits = [o(xv, v) for v in sorted(allowed)]
        if len(lits) > k:
            cnf.extend(CardEnc.atmost(lits=lits, bound=k, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)
    return pool, cnf, s, d


# ---------------------------------------------------------------- verification
def extract_and_verify(model, n, V, m, k, N, R, s, d):
    true = set(l for l in model if l > 0)
    S = {}
    D = {}
    for j in range(n):
        for r in range(1, R + 1):
            for x in range(V):
                for h in histories(N[j], m, r - 1):
                    cs = [c for c in range(m) if s(r, j, x, h, c) in true]
                    assert len(cs) == 1
                    S[r, j, x, h] = cs[0]
        for x in range(V):
            for h in histories(N[j], m, R):
                vs = [v for v in range(V) if d(j, x, h, v) in true]
                assert len(vs) == 1
                D[j, x, h] = vs[0]
    for xv in itertools.product(range(V), repeat=n):
        hist = [() for _ in range(n)]
        for r in range(1, R + 1):
            sent = [S[r, j, xv[j], hist[j]] for j in range(n)]
            hist = [hist[i] + tuple(sent[l] for l in N[i]) for i in range(n)]
        outs = [D[i, xv[i], hist[i]] for i in range(n)]
        if not all(v in xv for v in outs) or len(set(outs)) > k:
            raise AssertionError(f'extracted protocol fails on {xv}: {outs}')
    return S, D


def solvable(n, V, m, k, topology='complete', R=1, verify=True, return_protocol=False,
             value_sym=False):
    if k >= n or V <= k:
        # trivial: everyone outputs own input (at most min(n,|V|) <= k values)
        return (True, None) if return_protocol else True
    N = in_neighbours(topology, n)
    pool, cnf, s, d = build(n, V, m, k, N, R, value_sym)
    with Cadical153(bootstrap_with=cnf.clauses) as S:
        res = S.solve()
        model = S.get_model() if res else None
    proto = None
    if res and verify:
        proto = extract_and_verify(model, n, V, m, k, N, R, s, d)
    return (res, proto) if return_protocol else res


if __name__ == '__main__':
    n, V, m, k = map(int, sys.argv[1:5])
    topo = sys.argv[5] if len(sys.argv) > 5 else 'complete'
    R = int(sys.argv[6]) if len(sys.argv) > 6 else 1
    vs = len(sys.argv) > 7 and sys.argv[7] == 'valuesym'
    print(solvable(n, V, m, k, topo, R, value_sym=vs))
