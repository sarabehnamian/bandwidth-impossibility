"""Independent SAT check: k-set agreement, complete graph, one round, m-valued messages.
Agent i sends s_i(x_i) in [m]; decides d_i(x_i, messages of others) in V.
Valid: each output is some agent's input. Agreement: at most k distinct outputs."""
import itertools, sys
from pysat.formula import IDPool, CNF
from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical153

def solvable(n, V, m, k):
    pool = IDPool(); cnf = CNF()
    s = lambda i, x, c: pool.id(('s', i, x, c))
    d = lambda i, x, cv, v: pool.id(('d', i, x, cv, v))
    o = lambda xv, v: pool.id(('o', xv, v))
    def exactly_one(lits):
        cnf.extend(CardEnc.equals(lits=lits, bound=1, vpool=pool, encoding=EncType.seqcounter).clauses)
    for i in range(n):
        for x in range(V):
            exactly_one([s(i, x, c) for c in range(m)])
            for cv in itertools.product(range(m), repeat=n - 1):
                exactly_one([d(i, x, cv, v) for v in range(V)])
    for xv in itertools.product(range(V), repeat=n):
        allowed = set(xv)
        for cvec in itertools.product(range(m), repeat=n):
            msg = [-s(j, xv[j], cvec[j]) for j in range(n)]  # if these messages are sent...
            for i in range(n):
                cv = tuple(cvec[j] for j in range(n) if j != i)
                for v in range(V):
                    # ...and agent i decides v, then v is "used" on input xv
                    if v in allowed:
                        cnf.append(msg + [-d(i, xv[i], cv, v), o(xv, v)])
                    else:
                        cnf.append(msg + [-d(i, xv[i], cv, v)])
        lits = [o(xv, v) for v in sorted(allowed)]
        if len(lits) > k:
            cnf.extend(CardEnc.atmost(lits=lits, bound=k, vpool=pool, encoding=EncType.seqcounter).clauses)
    with Cadical153(bootstrap_with=cnf.clauses) as S:
        return S.solve()

if __name__ == '__main__':
    rows = []
    for n in (3, 4):
        for k in range(1, n):
            for m in (2, 3):
                for V in range(2, m + k + 2):
                    if n == 4 and V ** n * m ** n > 2_000_000: continue
                    r = solvable(n, V, m, k)
                    pred = V <= m + k - 1
                    rows.append((n, k, m, V, r, pred))
                    print(f"n={n} k={k} m={m} |V|={V}: {'SOLVABLE ' if r else 'impossible'}  conj(|V|<=m+k-1)={pred}  {'OK' if r==pred else 'MISMATCH'}", flush=True)
