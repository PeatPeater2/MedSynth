import unittest
import os
import json
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestIHDModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'ischemic_heart_disease.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"IHD module should be valid, but got: {errs}")
        
    def test_reproducibility(self):
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 777
        genA = Generator(options)
        genA.load_module(self.module_path)
        popA = genA.run()
        
        options = GeneratorOptions()
        options.population_size = 1
        options.reference_time = 1700000000000
        options.end_time = 1700000000000
        options.seed = 777
        genB = Generator(options)
        genB.load_module(self.module_path)
        popB = genB.run()
        
        self.assertEqual(len(popA[0].record.conditions), len(popB[0].record.conditions))

    def test_generator_ihd(self):
        options = GeneratorOptions()
        options.population_size = 200
        options.thread_pool_size = 4
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        ihd_cases = 0
        mi_cases = 0
        ecgs = 0
        
        for p in pop:
            for cond in p.record.conditions:
                display = cond.codes[0].get("display", "").lower()
                if "ischemic heart disease" in display:
                    ihd_cases += 1
                if "myocardial infarction" in display:
                    mi_cases += 1
            for proc in p.record.procedures:
                if "electrocardiogram" in proc.codes[0].get("display", "").lower():
                    ecgs += 1
                    
        print(f"Generated {len(pop)} patients. IHD: {ihd_cases}, MI: {mi_cases}, ECGs: {ecgs}")

if __name__ == '__main__':
    unittest.main()

