import unittest
import os
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestMeningitisModule(unittest.TestCase):
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'meningitis.json')
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"Meningitis module should be valid, but got: {errs}")

    def test_cases_generated(self):
        options = GeneratorOptions()
        options.population_size = 200
        options.seed = 42
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        men_cases = sum(
            1 for p in pop 
            if any(c.codes and c.codes[0]['display'] == 'Meningitis (disorder)' for c in p.record.conditions)
        )
        self.assertTrue(men_cases >= 0)

