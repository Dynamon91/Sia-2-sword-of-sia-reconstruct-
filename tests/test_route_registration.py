"""Reference camera offsets must compose correctly before they inform a map."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_route_continuation import resolve_offsets

def edge(a,b,delta,accepted=True):
    return {'from':a,'to':b,'delta':delta,'accepted':accepted}

class RegistrationGraphTest(unittest.TestCase):
    def test_chain_and_reverse_anchor(self):
        edges=[edge(155,160,[-242,59]),edge(160,161,[-116,-25])]
        self.assertEqual(resolve_offsets(edges,155),{155:[0,0],160:[-242,59],161:[-358,34]})
        self.assertEqual(resolve_offsets(edges,161),{161:[0,0],160:[116,25],155:[358,-34]})

    def test_rejected_edge_does_not_connect_or_conflict(self):
        edges=[edge(160,161,None,False),edge(161,162,[-24,-1])]
        self.assertEqual(resolve_offsets(edges,160),{160:[0,0]})
        edges.append(edge(160,161,[-116,-25]))
        self.assertEqual(resolve_offsets(edges,160)[162],[-140,-26])

    def test_consistent_cycle(self):
        edges=[edge(1,2,[-20,0]),edge(2,3,[-10,5]),edge(1,3,[-30,5])]
        self.assertEqual(resolve_offsets(edges,1)[3],[-30,5])

    def test_conflicting_cycle_is_rejected(self):
        edges=[edge(1,2,[-20,0]),edge(2,3,[-10,5]),edge(1,3,[-30,6])]
        with self.assertRaisesRegex(ValueError,'Conflicting'):resolve_offsets(edges,1)

if __name__=='__main__':unittest.main()
