import unittest
import os
import json
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestDiarrheaModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'diarrheal_diseases.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"Diarrheal module should be valid, but got: {errs}")
        
    def test_reproducibility(self):
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 333
        genA = Generator(options)
        genA.load_module(self.module_path)
        popA = genA.run()
        
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 333
        genB = Generator(options)
        genB.load_module(self.module_path)
        popB = genB.run()
        
        self.assertEqual(len(popA[0].record.conditions), len(popB[0].record.conditions))

    def test_generator_age_and_severity_support(self):
        options = GeneratorOptions()
        options.population_size = 50
        options.thread_pool_size = 4
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        diarrhea_cases = 0
        dehydration_cases = 0
        cholera_cases = 0
        
        for p in pop:
            for cond in p.record.conditions:
                display = cond.codes[0].get("display", "").lower()
                if "diarrhea" in display:
                    diarrhea_cases += 1
                if "dehydration" in display:
                    dehydration_cases += 1
                if "cholera" in display:
                    cholera_cases += 1
                    
        print(f"Generated {len(pop)} patients. Lifetime Diarrhea: {diarrhea_cases} (Dehydration: {dehydration_cases}, Cholera: {cholera_cases})")

if __name__ == '__main__':
    unittest.main()

