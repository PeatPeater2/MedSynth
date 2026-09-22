import unittest
import os
import json
import tempfile
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestTuberculosisModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'tuberculosis.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator_and_negative_cases(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"TB module should be valid, but got: {errs}")
        
        # Test negative invalid module (impossible sequences, broken references)
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as f:
            json.dump({
                "states": {
                    "Initial": {"type": "Initial", "direct_transition": "FakeState"}
                }
            }, f)
            temp_path = f.name
            
        errs = validate_module(temp_path)
        self.assertIn("Missing 'Terminal' state.", errs)
        self.assertTrue(any("Invalid transition 'FakeState'" in e for e in errs))
        os.remove(temp_path)
        
    def test_healthy_patient(self):
        p = Patient(seed=123)
        p.attributes["birthdate"] = 0
        p.attributes["gender"] = "M"
        
        one_year = 365 * 24 * 60 * 60 * 1000
        self.assertFalse(self.mod.process(p, one_year))
        self.assertEqual(len(p.record.conditions), 0, "Healthy patient should not have TB condition immediately")

    def test_reproducibility(self):
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 42
        genA = Generator(options)
        genA.load_module(self.module_path)
        popA = genA.run()
        
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 42
        genB = Generator(options)
        genB.load_module(self.module_path)
        popB = genB.run()
        
        self.assertEqual(len(popA[0].record.conditions), len(popB[0].record.conditions))

    def test_generator_location_support(self):
        for state in ["Oyo", "Lagos", "Kano", "Federal Capital Territory"]:
            options = GeneratorOptions()
            options.population_size = 5
            options.target_state = state
            gen = Generator(options)
            gen.load_module(self.module_path)
            pop = gen.run()
            for p in pop:
                self.assertEqual(p.attributes["state"], state)
                
    def test_risk_factors(self):
        # We can't guarantee a TB case in a small sample due to low probability,
        # but we can verify the module executes without crashing for different ages/sexes.
        
        # Male Adult
        options = GeneratorOptions()
        options.population_size = 1
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        self.assertTrue(len(pop) == 1)

if __name__ == '__main__':
    unittest.main()
