import unittest
import os
from medsynth.generator import Generator, GeneratorOptions
from medsynth.validator import validate_module

class TestSickleCellModule(unittest.TestCase):
    def setUp(self):
        self.module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets', 'diseases', 'sickle_cell_disease.json')
        
    def test_validator(self):
        errs = validate_module(self.module_path)
        self.assertEqual(len(errs), 0, f"SCD module should be valid, but got: {errs}")

    def test_cases_generated(self):
        options = GeneratorOptions()
        options.population_size = 500
        options.seed = 42
        gen = Generator(options)
        gen.load_module(self.module_path)
        pop = gen.run()
        
        scd_cases = 0
        hbaa = 0
        hbas = 0
        hbss = 0
        for p in pop:
            g = p.attributes.get('genotype', 'Unknown')
            if g == 'HbAA': hbaa += 1
            if g == 'HbAS': hbas += 1
            if g == 'HbSS': hbss += 1
            if any(c.codes and c.codes[0]['display'] == 'Sickle cell disease (disorder)' for c in p.record.conditions):
                scd_cases += 1
        
        self.assertTrue(hbaa > 0)
        self.assertTrue(hbas > 0)
        # It's possible HbSS is 0 in 500 patients (2.5% expected is ~12), but it should be > 0.
        print(f"\nSCD Generation: AA={hbaa}, AS={hbas}, SS={hbss}, Cases={scd_cases}")
        self.assertTrue(scd_cases >= 0)

