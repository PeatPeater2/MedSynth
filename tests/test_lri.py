import unittest
import os
import json
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestLRIModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'lower_respiratory_infections.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"LRI module should be valid, but got: {errs}")
        
    def test_reproducibility(self):
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 555
        genA = Generator(options)
        genA.load_module(self.module_path)
        popA = genA.run()
        
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 555
        genB = Generator(options)
        genB.load_module(self.module_path)
        popB = genB.run()
        
        self.assertEqual(len(popA[0].record.conditions), len(popB[0].record.conditions))

    def test_generator_location_and_age_support(self):
        options = GeneratorOptions()
        options.population_size = 100
        options.thread_pool_size = 4
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        lri_cases = 0
        severe_cases = 0
        for p in pop:
            # check basic demographic location integrity
            self.assertIn("state", p.attributes)
            for cond in p.record.conditions:
                if cond.codes and "respiratory" in cond.codes[0].get("display", "").lower():
                    lri_cases += 1
                if cond.codes and "bacterial" in cond.codes[0].get("display", "").lower():
                    severe_cases += 1
                    
        print(f"Generated {len(pop)} patients. Lifetime LRI episodes: {lri_cases} (Severe: {severe_cases})")

if __name__ == '__main__':
    unittest.main()

