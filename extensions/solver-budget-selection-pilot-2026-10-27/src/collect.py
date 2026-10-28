"""Primary collection + selection, under the frozen protocol.

Sequential, no competing jobs. Solver order rotates deterministically by
instance index. One collection per (instance, solver) through the LONGER
budget, with a snapshot retained at the shorter one.

Persistence follows PROTOCOL.md §3.1: collection is never capped, but the full
bank is written only when it holds <= BANK_PERSIST_MAX distinct solutions;
above that the record carries bank_persisted=false and the canonical bank hash
stands in its place. Selected sets are ALWAYS persisted in full.
"""
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pilotlib as P
import store

BANK_PERSIST_MAX = 5000
OUTDIR = os.path.join(P.EXT, 'data', 'collections')
PROTO_SHA = open(os.path.join(P.EXT, 'data', 'PROTOCOL_SHA.txt')).read().strip()


def budget_label(b):
    return f'b{int(b)}'


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    coh = P.cohort()
    print(f"protocol commit {PROTO_SHA}")
    print(f"{len(coh)} attempted instances; budgets {P.BUDGETS}; k={P.K_RETAIN}\n")
    print(f"{'instance':<16}{'order':>7}{'slv':>4}{'bank30':>8}{'bank5':>8}"
          f"{'dups':>9}{'att':>8}{'cpu':>7}{'elig5':>7}{'elig30':>7}")
    index = []
    t_all = time.perf_counter()
    for idx, (cl, meta) in enumerate(coh):
        order = (P.SOLVERS if idx % 2 == 0 else P.SOLVERS[::-1])   # rotation
        for lab in order:
            seed, mat = P.collection_seed(lab, meta['formula_hash'])
            fn = P.collect_walksat if lab == 'W' else P.collect_cdcl
            bank, info = fn(cl, meta['n'], max(P.BUDGETS), seed)
            rec = dict(protocol_commit=PROTO_SHA, **meta, solver=lab,
                       solver_order_position=order.index(lab) + 1,
                       collection_seed=seed, collection_seed_material=mat,
                       collection=info, budgets={}, bank_size=len(bank),
                       bank_hash=store.hash_A(bank.order),
                       bank_persisted=len(bank) <= BANK_PERSIST_MAX,
                       bank_persist_max=BANK_PERSIST_MAX)
            if rec['bank_persisted']:
                rec['bank'] = [list(x) for x in bank.order]
            rec['accepted_at'] = [round(t, 6) for t in bank.accepted_at]
            for b in P.BUDGETS:
                bl = budget_label(b)
                snap = bank.snapshot(b)
                entry = dict(budget=b, bank_size=len(snap),
                             bank_hash=store.hash_A(snap),
                             eligible=len(snap) >= P.K_RETAIN, sets={})
                pre = P.prefix_set(snap, P.K_RETAIN)
                if pre is not None:
                    entry['sets']['prefix'] = dict(
                        scheme='prefix', B=[list(x) for x in pre],
                        B_hash=store.hash_A(pre), k=P.K_RETAIN,
                        provenance=dict(rule='first k distinct validated '
                                             'discoveries, chronological'))
                for r in range(P.N_REPLICATES):
                    B, prov = P.uniform_set(snap, P.K_RETAIN,
                                            meta['formula_hash'], lab, bl, r)
                    if B is not None:
                        entry['sets'][f'uniform{r}'] = dict(
                            scheme=f'uniform{r}', B=[list(x) for x in B],
                            B_hash=prov['B_hash'], k=P.K_RETAIN,
                            provenance=prov)
                if not entry['eligible']:
                    entry['outcome'] = 'insufficient_sample'
                rec['budgets'][bl] = entry
            fn_out = os.path.join(OUTDIR, f"{meta['instance_id']}_{lab}.json")
            store.atomic_write_text(fn_out, json.dumps(rec))
            index.append(dict(instance_id=meta['instance_id'], solver=lab,
                              stratum=meta['stratum'], n=meta['n'],
                              alpha=meta['alpha'],
                              formula_hash=meta['formula_hash'],
                              bank_size=len(bank),
                              b5=rec['budgets']['b5']['bank_size'],
                              b30=rec['budgets']['b30']['bank_size'],
                              elig5=rec['budgets']['b5']['eligible'],
                              elig30=rec['budgets']['b30']['eligible'],
                              duplicates=info['duplicates'],
                              attempts=info.get('restarts') or info.get('runs'),
                              elapsed_s=round(info['elapsed_s'], 2),
                              cpu_s=round(info['cpu_s'], 2),
                              peak_rss_mb=info['peak_rss_mb'],
                              rejected_invalid=info['rejected_invalid'],
                              resource_limited=info['resource_limited'],
                              file=os.path.basename(fn_out)))
            r5 = rec['budgets']['b5']; r30 = rec['budgets']['b30']
            print(f"{meta['instance_id']:<16}{order.index(lab)+1:>7}{lab:>4}"
                  f"{r30['bank_size']:>8}{r5['bank_size']:>8}"
                  f"{info['duplicates']:>9}"
                  f"{(info.get('restarts') or info.get('runs')):>8}"
                  f"{info['cpu_s']:>7.1f}"
                  f"{('yes' if r5['eligible'] else 'NO'):>7}"
                  f"{('yes' if r30['eligible'] else 'NO'):>7}", flush=True)
    store.atomic_write_text(os.path.join(P.EXT, 'data', 'collection_index.json'),
                            json.dumps(dict(protocol_commit=PROTO_SHA,
                                            budgets=list(P.BUDGETS),
                                            k_retain=P.K_RETAIN,
                                            attempted=len(coh),
                                            rows=index), indent=2))
    el5 = sum(1 for r in index if r['elig5']); el30 = sum(1 for r in index if r['elig30'])
    print(f"\n  collection wall {time.perf_counter()-t_all:.0f}s")
    print(f"  eligible (solver,instance) cells: 5s {el5}/{len(index)}, 30s {el30}/{len(index)}")
    print(f"  wrote data/collections/ and data/collection_index.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
