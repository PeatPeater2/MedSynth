import unittest
import os
import json
from medsynth.module import Module
from medsynth.patient import Patient
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestStrokeModule(unittest.TestCase):
    
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'stroke.json')
        self.mod = Module.load_from_file(self.module_path)
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"Stroke module should be valid, but got: {errs}")
        
    def test_reproducibility(self):
        options = GeneratorOptions()
        options.population_size = 1
        options.seed = 444
        genA = Generator(options)
        genA.load_module(self.module_path)
        popA = genA.run()
        
        options = GeneratorOptions()
        options.population_size = 1
        options.seed = 444
        genB = Generator(options)
        genB.load_module(self.module_path)
        popB = genB.run()
        
        self.assertEqual(len(popA[0].record.conditions), len(popB[0].record.conditions))

    def test_generator_age_and_subtype_support(self):
        options = GeneratorOptions()
        options.population_size = 200
        options.thread_pool_size = 4
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        stroke_cases = 0
        ischemic_cases = 0
        hemorrhagic_cases = 0
        ct_scans = 0
        
        for p in pop:
            for cond in p.record.conditions:
                display = cond.codes[0].get("display", "").lower()
                if "cerebrovascular" in display:
                    stroke_cases += 1
                if "ischemic" in display:
                    ischemic_cases += 1
                if "hemorrhagic" in display:
                    hemorrhagic_cases += 1
            for proc in p.record.procedures:
                if "tomography" in proc.codes[0].get("display", "").lower():
                    ct_scans += 1
                    
        print(f"Generated {len(pop)} patients. Lifetime Strokes: {stroke_cases} (Ischemic: {ischemic_cases}, Hemorrhagic: {hemorrhagic_cases})")
        print(f"Total CT Scans performed: {ct_scans}")

if __name__ == '__main__':
    unittest.main()

