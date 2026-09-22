import unittest
import os
import csv
from medsynth.geography import Geography
from medsynth.demographics import Demographics

class TestDataFoundation(unittest.TestCase):
    
    def setUp(self):
        self.geo = Geography()
        self.demo = Demographics()
        
    def test_geography_completeness(self):
        # 36 states + FCT = 37
        self.assertEqual(len(self.geo.states), 37, "Must have exactly 37 states (36 + FCT)")
        
        total_lgas = sum(len(lgas) for lgas in self.geo.lgas_by_state.values())
        self.assertEqual(total_lgas, 774, "Must have exactly 774 LGAs")
        
        # No duplicates
        self.assertEqual(len(self.geo.states), len(set(self.geo.states)))
        
        all_lgas = []
        for lgas in self.geo.lgas_by_state.values():
            all_lgas.extend(lgas)
            
        # LGA names can technically overlap between states (e.g., Bassa in Plateau and Kogi),
        # but every LGA must map to a valid state, which is implicitly true since lgas_by_state keys are states.
        for state in self.geo.states:
            self.assertIn(state, self.geo.lgas_by_state)

    def test_demographics_structure(self):
        self.assertGreater(len(self.demo.age_bins), 0)
        self.assertGreater(self.demo.total_male_weight, 0)
        self.assertGreater(self.demo.total_female_weight, 0)
        
        # Test names diversity
        hausa = self.demo.names["Hausa"]
        self.assertGreater(len(hausa["first_m"]), 20)
        self.assertGreater(len(hausa["first_f"]), 20)
        self.assertGreater(len(hausa["last"]), 20)

if __name__ == '__main__':
    unittest.main()

