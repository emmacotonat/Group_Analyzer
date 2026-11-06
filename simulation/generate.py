"""Reproducible synthetic example. No real participants and no fitted SRM.

Python 3.10+, standard library only. Run from any directory.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import random

DOMAINS = ['biografic', 'posicional', 'moral_normatiu']


def ratio(a, b):
    return a / b if b else None


def score(records):
    """Distinguish refusal/missing/unknown and unavailable target criterion."""
    usable = [r for r in records if r['status'] in ('attribution', 'unknown')]
    declared = [r for r in usable if r['status'] == 'attribution']
    comparable = [r for r in usable if r['reference'] is not None]
    valid = [r for r in comparable if r['status'] == 'attribution']
    correct = sum(r['answer'] == r['reference'] for r in valid)
    return dict(planned=len(records), usable=len(usable), declared=len(declared),
                comparable=len(comparable), valid=len(valid), correct=correct,
                completeness=ratio(len(usable), len(records)),
                coverage=ratio(len(declared), len(usable)),
                comparable_coverage=ratio(len(valid), len(comparable)),
                precision=ratio(correct, len(valid)),
                effective=ratio(correct, len(comparable)),
                uncorroborated=ratio(len(valid)-correct, len(comparable)))


def las(a, b, rule):
    """Three-valued logical intersection/union; unknown is never zero."""
    if rule == 'intersection':
        return 0 if 0 in (a, b) else 1 if a == b == 1 else None
    if rule == 'union':
        return 1 if 1 in (a, b) else 0 if a == b == 0 else None
    raise ValueError(rule)


def mean(values):
    v = [x for x in values if x is not None]
    return ratio(sum(v), len(v))


def corr(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    x, y = zip(*pairs)
    mx, my = mean(x), mean(y)
    den = math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))
    return sum((a-mx)*(b-my) for a, b in pairs)/den if den else None


def simulate(seed=20261106, n=12):
    rng = random.Random(seed)
    nodes = [dict(id=f'P{i+1:02}', team=i//4, tenure=1+rng.randrange(7),
                  role=['Logística', 'Activitats', 'Coordinació'][i % 3]) for i in range(n)]
    items = [dict(id=f'{d}_{q+1}', domain=d, options=[0, 1, 2],
                  description=desc) for d, descriptions in [
                      ('biografic', ['Antiguitat en tres franges', 'Àmbit de formació en tres categories']),
                      ('posicional', ['Comissió preferida entre tres opcions', 'Tasca preferida entre tres opcions']),
                      ('moral_normatiu', ['Criteri declarat en vinyeta educativa 1', 'Criteri declarat en vinyeta educativa 2'])]
             for q, desc in enumerate(descriptions)]
    truth = [[rng.randrange(3) for _ in items] for _ in nodes]
    # Every target has one unavailable criterion: test non-comparability explicitly.
    truth[4][3] = None
    advice = [[None if i == j else int(rng.random() < min(.85, .08 +
               .30*(nodes[i]['team'] == nodes[j]['team']) + .43*(j == 0)))
               for j in range(n)] for i in range(n)]
    attrs = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            same = nodes[i]['team'] == nodes[j]['team']
            for q, item in enumerate(items):
                d = DOMAINS.index(item['domain'])
                draw = rng.random()
                pknow = min(.95, [.72, .60, .48][d] + .10*same + .07*advice[i][j])
                status = ('refused' if draw < .015 else 'missing' if draw < .03 else
                          'attribution' if draw < .03+pknow*.97 else 'unknown')
                answer = None
                if status == 'attribution':
                    # Deliberately selective visibility: central P01 is less known biographically.
                    paccurate = min(.94, [.80, .61, .47][d] + .08*same + .10*advice[i][j])
                    if j == 0 and d == 0:
                        paccurate = .24
                    ref = truth[j][q]
                    if ref is None:
                        answer = rng.randrange(3)
                    elif rng.random() < paccurate:
                        answer = ref
                    else:
                        # Errors sometimes follow own response; can still coincide by projection.
                        answer = (truth[i][q] if rng.random() < .5 and truth[i][q] is not None
                                  else rng.choice([v for v in range(3) if v != ref]))
                attrs.append(dict(observer=i, target=j, item=q, domain=item['domain'],
                                  status=status, answer=answer, reference=truth[j][q]))
    css = []
    for k in range(n):
        m = []
        for i in range(n):
            row = []
            for j in range(n):
                if i == j:
                    row.append(None)
                    continue
                if k == i:
                    value = advice[i][j]
                elif k == j:
                    value = advice[i][j] if rng.random() < .91 else 1-advice[i][j]
                else:
                    value = advice[i][j] if rng.random() < .78 else 1-advice[i][j]
                    if rng.random() < .035:
                        value = None
                row.append(value)
            m.append(row)
        css.append(m)
    intersection = [[None if i == j else las(css[i][i][j], css[j][i][j], 'intersection')
                     for j in range(n)] for i in range(n)]
    union = [[None if i == j else las(css[i][i][j], css[j][i][j], 'union')
              for j in range(n)] for i in range(n)]
    consensus = [[None if i == j else mean([css[k][i][j] for k in range(n)])
                  for j in range(n)] for i in range(n)]
    by_domain = {d: score([r for r in attrs if r['domain'] == d]) for d in DOMAINS}
    pair = {d: [[None if i == j else score([r for r in attrs if r['observer'] == i and
               r['target'] == j and r['domain'] == d]) for j in range(n)] for i in range(n)]
            for d in DOMAINS}
    for j, node in enumerate(nodes):
        node['advice_in'] = sum(advice[i][j] or 0 for i in range(n) if i != j)
        node['advice_out'] = sum(advice[j][i] or 0 for i in range(n) if i != j)
        node['known'] = {d: score([r for r in attrs if r['target'] == j and r['domain'] == d])
                         for d in DOMAINS}
        node['knowing'] = {d: score([r for r in attrs if r['observer'] == j and r['domain'] == d])
                           for d in DOMAINS}
    benchmarks = {}
    for d in DOMAINS:
        sample = [r for r in attrs if r['domain'] == d and r['status'] == 'attribution'
                  and r['reference'] is not None]
        projection, majority = [], []
        for r in sample:
            q, j, i = r['item'], r['target'], r['observer']
            if truth[i][q] is not None:
                projection.append(int(truth[i][q] == r['reference']))
            values = [truth[t][q] for t in range(n) if t != j and truth[t][q] is not None]
            counts = {v: values.count(v) for v in (0, 1, 2)}
            # Deterministic tie breaking; not a population estimator.
            choice = max((0, 1, 2), key=lambda v: (counts[v], -v))
            majority.append(int(choice == r['reference']))
        benchmarks[d] = dict(projection=mean(projection), projection_n=len(projection),
                             majority_loo=mean(majority), majority_n=len(majority))
    css_evaluation = []
    for k in range(n):
        pairs = [(css[k][i][j], intersection[i][j]) for i in range(n) for j in range(n)
                 if i != j and k not in (i, j) and css[k][i][j] is not None
                 and intersection[i][j] is not None]
        pos = [a for a, ref in pairs if ref == 1]
        neg = [a for a, ref in pairs if ref == 0]
        css_evaluation.append(dict(observer=k, n=len(pairs), sensitivity=mean(pos),
                                   specificity=mean([1-a for a in neg])))
    # Descriptive least-squares additive decomposition, NOT SRM variance estimation.
    residuals = {}
    for d in DOMAINS:
        points = [(i, j, pair[d][i][j]['effective']) for i in range(n) for j in range(n)
                  if i != j and pair[d][i][j]['effective'] is not None]
        mu = mean([v for _, _, v in points])
        a, b = [0.]*n, [0.]*n
        for _ in range(200):
            for i in range(n):
                a[i] = mean([v-mu-b[j] for x, j, v in points if x == i]) or 0.
            for j in range(n):
                b[j] = mean([v-mu-a[i] for i, y, v in points if y == j]) or 0.
        residuals[d] = [[None]*n for _ in range(n)]
        for i, j, value in points:
            residuals[d][i][j] = value-mu-a[i]-b[j]
    return dict(synthetic=True, seed=seed, n=n, nodes=nodes, items=items,
                self_reports=truth, attributions=attrs, advice=advice, css=css,
                las_intersection=intersection, las_union=union, consensus=consensus,
                domain_scores=by_domain, pair_scores=pair, benchmarks=benchmarks,
                css_evaluation=css_evaluation, additive_residuals=residuals,
                correlations={d: corr([x['advice_in'] for x in nodes],
                                      [x['known'][d]['effective'] for x in nodes]) for d in DOMAINS})


def write_csv(path, rows):
    if not rows:
        return
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def build(seed=20261106, out=None):
    root = Path(__file__).resolve().parent
    out = Path(out) if out else root/'output'
    out.mkdir(parents=True, exist_ok=True)
    data = simulate(seed)
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    (out/'data.json').write_text(payload+'\n', encoding='utf-8')
    template = (root/'template.html').read_text(encoding='utf-8')
    (out/'index.html').write_text(template.replace('__DATA__', payload.replace('</', '<\\/')), encoding='utf-8')
    write_csv(out/'attributions.csv', data['attributions'])
    write_csv(out/'nodes.csv', [dict(id=x['id'],team=x['team'],tenure=x['tenure'],role=x['role'],
                                    advice_in=x['advice_in'],advice_out=x['advice_out']) for x in data['nodes']])
    write_csv(out/'self_reports.csv', [dict(target=i,item=q,value=v)
                                      for i,row in enumerate(data['self_reports']) for q,v in enumerate(row)])
    write_csv(out/'css.csv', [dict(observer=k,sender=i,receiver=j,value=v)
                             for k,m in enumerate(data['css']) for i,row in enumerate(m)
                             for j,v in enumerate(row) if i != j])
    summary = dict(synthetic=True,seed=seed,domain_scores=data['domain_scores'],
                   correlations=data['correlations'],benchmarks=data['benchmarks'],
                   warning='Paràmetres i patrons imposats pel generador; no són resultats de camp.')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed',type=int,default=20261106)
    parser.add_argument('--out')
    args = parser.parse_args()
    print(json.dumps(build(args.seed,args.out),ensure_ascii=False,indent=2))
