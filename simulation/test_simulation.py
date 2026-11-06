"""Scientific invariants and reproducibility checks for the demonstration."""
import unittest
from generate import score, las, simulate


class SimulationTests(unittest.TestCase):
    def test_unknown_is_not_incorrect_attribution(self):
        r=score([dict(status='unknown',answer=None,reference=1)])
        self.assertEqual(r['coverage'],0)
        self.assertEqual(r['effective'],0)
        self.assertIsNone(r['precision'])

    def test_unavailable_criterion_not_error(self):
        r=score([dict(status='attribution',answer=1,reference=None)])
        self.assertEqual(r['coverage'],1)
        self.assertIsNone(r['effective'])
        self.assertIsNone(r['precision'])

    def test_missing_and_refusal_not_zeros(self):
        r=score([dict(status=s,answer=None,reference=1) for s in ('missing','refused')])
        self.assertEqual(r['completeness'],0)
        self.assertIsNone(r['coverage'])

    def test_las_three_valued_logic(self):
        self.assertIsNone(las(1,None,'intersection'))
        self.assertEqual(las(0,None,'intersection'),0)
        self.assertEqual(las(1,None,'union'),1)
        self.assertIsNone(las(0,None,'union'))

    def test_reproducibility_and_different_seed(self):
        a=simulate(42,6)
        self.assertEqual(a,simulate(42,6))
        self.assertNotEqual(a['attributions'],simulate(43,6)['attributions'])

    def test_denominators_and_css_exclusion(self):
        a=simulate()
        for s in a['domain_scores'].values():
            self.assertLessEqual(s['correct'],s['valid'])
            self.assertLessEqual(s['valid'],s['comparable'])
            self.assertAlmostEqual(s['comparable_coverage']-s['effective'],s['uncorroborated'])
        for k,e in enumerate(a['css_evaluation']):
            expected=sum(a['css'][k][i][j] is not None and a['las_intersection'][i][j] is not None
                         for i in range(a['n']) for j in range(a['n']) if i!=j and k not in (i,j))
            self.assertEqual(e['n'],expected)

    def test_direction_and_no_self_ties(self):
        a=simulate()
        for j,node in enumerate(a['nodes']):
            self.assertEqual(node['advice_in'],sum(a['advice'][i][j] or 0 for i in range(a['n']) if i!=j))
            self.assertIsNone(a['advice'][j][j])


if __name__ == '__main__':
    unittest.main()
