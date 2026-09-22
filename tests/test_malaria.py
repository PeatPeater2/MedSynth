import unittest
import os
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestMalariaModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'malaria.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"Malaria module should be valid, but got: {errs}")
        
    def test_generator_100_patients(self):
        options = GeneratorOptions()
        options.population_size = 100
        options.thread_pool_size = 4
        gen = Generator(options)
        gen.load_module(self.module_path)
        
        pop = gen.run()
        malaria_cases = 0
        for p in pop:
            for cond in p.record.conditions:
                if cond.codes and cond.codes[0].get("display") == "Malaria":
                    malaria_cases += 1
                    
        print(f"Generated {len(pop)} patients. Lifetime Malaria episodes across population: {malaria_cases}")
        
if __name__ == '__main__':
    unittest.main()

