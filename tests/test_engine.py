import unittest
import os
import tempfile
import json
import time

from medsynth.patient import Patient
from medsynth.health_record import HealthRecord
from medsynth.state_machine import Initial, Simple, Terminal, Delay, Guard, Encounter, EncounterEnd, ConditionOnset, ConditionEnd, SetAttribute, Counter
from medsynth.module import Module
from medsynth.logic import Logic
from medsynth.generator import Generator, GeneratorOptions
from medsynth.exporters import Exporter

class TestMedSynthEngine(unittest.TestCase):
    def test_logic(self):
        p = Patient(123)
        p.attributes["gender"] = "M"
        p.attributes["birthdate"] = 0 # 1970
        
        # Test True
        self.assertTrue(Logic({"condition_type": "True"}).test(p, 1000))
        
        # Test Gender
        self.assertTrue(Logic({"condition_type": "Gender", "gender": "M"}).test(p, 1000))
        self.assertFalse(Logic({"condition_type": "Gender", "gender": "F"}).test(p, 1000))
        
        # Test Age
        p.attributes["birthdate"] = 0
        current_time = 10 * 365.25 * 24 * 60 * 60 * 1000 # 10 years old
        self.assertTrue(Logic({"condition_type": "Age", "operator": "==", "quantity": 10, "unit": "years"}).test(p, current_time))
        self.assertTrue(Logic({"condition_type": "Age", "operator": ">=", "quantity": 5, "unit": "years"}).test(p, current_time))
        self.assertFalse(Logic({"condition_type": "Age", "operator": "<", "quantity": 10, "unit": "years"}).test(p, current_time))

    def test_state_machine_execution(self):
        # Build a small dummy module programmatically
        module_def = {
            "name": "TestModule",
            "states": {
                "Initial": {
                    "type": "Initial",
                    "direct_transition": "SetAttr"
                },
                "SetAttr": {
                    "type": "SetAttribute",
                    "attribute": "test_flag",
                    "value": True,
                    "direct_transition": "DelayState"
                },
                "DelayState": {
                    "type": "Delay",
                    "exact": {"quantity": 1, "unit": "days"},
                    "direct_transition": "EncounterState"
                },
                "EncounterState": {
                    "type": "Encounter",
                    "encounter_class": "ambulatory",
                    "direct_transition": "ConditionState"
                },
                "ConditionState": {
                    "type": "ConditionOnset",
                    "codes": [{"system": "SNOMED-CT", "code": "123", "display": "Test"}],
                    "direct_transition": "Terminal"
                },
                "Terminal": {
                    "type": "Terminal"
                }
            }
        }
        
        mod = Module(module_def)
        p = Patient(42)
        p.attributes["birthdate"] = 0
        
        # Execute timestep 0
        done = mod.process(p, 0)
        self.assertFalse(done) # Halted at DelayState
        self.assertTrue(p.attributes.get("test_flag"))
        
        # Advance time by half a day
        half_day = 12 * 60 * 60 * 1000
        done = mod.process(p, half_day)
        self.assertFalse(done) # Still halted
        
        # Advance time to > 1 day
        one_day = 24 * 60 * 60 * 1000
        done = mod.process(p, one_day + 1000)
        self.assertTrue(done) # Should reach terminal
        
        # Verify clinical record
        self.assertEqual(len(p.record.encounters), 1)
        self.assertEqual(len(p.record.conditions), 1)
        self.assertEqual(p.record.conditions[0].codes[0]["code"], "123")

    def test_generator_scaling(self):
        options = GeneratorOptions()
        options.population_size = 10
        generator = Generator(options)
        population = generator.run()
        self.assertEqual(len(population), 10)
        
        for p in population:
            self.assertIn("gender", p.attributes)
            self.assertIn("lga", p.attributes)

    def test_exporters(self):
        options = GeneratorOptions()
        options.population_size = 3
        generator = Generator(options)
        population = generator.run()
        
        with tempfile.TemporaryDirectory() as tmpdirname:
            exporter = Exporter(tmpdirname)
            exporter.export(population)
            
            # Check CSV
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, 'csv', 'patients.csv')))
            # Check JSON
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, 'json')))
            # Check FHIR
            self.assertTrue(os.path.exists(os.path.join(tmpdirname, 'fhir')))

if __name__ == '__main__':
    unittest.main()

