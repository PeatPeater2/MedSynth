import random
from typing import Dict, Any

class Physiology:
    @staticmethod
    def get_vital_sign(patient, time_ms: int, sign: str) -> float:
        age_y = patient.age_in_years(time_ms)
        age_m = patient.age_in_months(time_ms)
        is_male = patient.attributes.get("gender") == "M"

        # Do not calculate for unborn patients
        if age_y < 0 and age_m < 0:
            return 0.0

        if sign == "height":
            # Modelled WHO/CDC median height in cm
            if age_y < 5:
                # Roughly 50cm at birth, 100cm at 5
                base = 50 + (age_m * (50/60))
            elif age_y < 18:
                base = 100 + ((age_y - 5) * 6)
            else:
                base = 170 if is_male else 160
            
            # +/- 5% variation
            return round(base * (1 + (patient.rand() * 0.1 - 0.05)), 1)
            
        elif sign == "weight":
            # Modelled median weight in kg
            if age_y < 5:
                base = 3.5 + (age_m * (16.5/60))
            elif age_y < 18:
                base = 20 + ((age_y - 5) * 3)
            else:
                base = 70 if is_male else 65
            return round(base * (1 + (patient.rand() * 0.2 - 0.1)), 1)
            
        elif sign == "bmi":
            height_m = Physiology.get_vital_sign(patient, time_ms, "height") / 100.0
            weight = Physiology.get_vital_sign(patient, time_ms, "weight")
            if height_m > 0:
                return round(weight / (height_m * height_m), 1)
            return 0.0

        elif sign == "systolic_bp":
            if age_y < 18:
                base = 90 + (age_y * 2)
            else:
                # Nigerian hypertension prevalence is high (30-40%)
                base = 115 + (age_y * 0.4)
                if patient.rand() < 0.35: # Hypertension modeled probability
                    base += patient.rand_int(20, 40)
            return round(base)
            
        elif sign == "diastolic_bp":
            if age_y < 18:
                base = 60 + (age_y * 1)
            else:
                base = 75 + (age_y * 0.2)
                if patient.rand() < 0.35:
                    base += patient.rand_int(10, 20)
            return round(base)
            
        elif sign == "temperature":
            # Baseline
            base = 36.8 + (patient.rand() * 0.4)
            # Check active conditions for fever
            has_malaria = False
            for cond in patient.record.present_conditions:
                if cond.codes and cond.codes[0].get("code") == "61462000": # Malaria
                    has_malaria = True
                    break
            if has_malaria:
                base += patient.rand() * 2.5 + 1.0 # 38.0 to 40.5
            return round(base, 1)

        elif sign == "hemoglobin":
            # Baseline g/dL
            if age_y < 12:
                base = 12.0
            else:
                base = 14.5 if is_male else 13.0
            
            base += (patient.rand() * 2 - 1)
            
            # Disease effects: SCD
            genotype = patient.attributes.get("genotype", "HbAA")
            if genotype == "HbSS":
                base -= 5.0 # Chronic severe anemia
            elif genotype == "HbSC":
                base -= 2.5 # Mild/moderate anemia
                
            # Malaria acute effect
            for cond in patient.record.present_conditions:
                if cond.codes and cond.codes[0].get("code") == "61462000":
                    base -= patient.rand() * 2.0
                    break
                    
            return round(base, 1)
            
        return 0.0

