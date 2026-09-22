import os
import csv
import random
from typing import Dict, List, Tuple
from medsynth.patient import Patient

class Demographics:
    """
    Handles Nigerian demographics (Age, Gender, Ethnicity, Names) using
    real age pyramids and gender distributions. Geographic probabilistic mixing is modelled.
    """
    def __init__(self):
        self.genders = ["M", "F"]
        self.ethnicities = []
        self.names: Dict[str, Dict[str, List[str]]] = {}
        
        self.age_bins = []  # List of (min_age, max_age, male_weight, female_weight)
        self.total_male_weight = 0.0
        self.total_female_weight = 0.0

        self.zone_mapping = {
            'Lagos': 'SW', 'Ogun': 'SW', 'Oyo': 'SW', 'Osun': 'SW', 'Ondo': 'SW', 'Ekiti': 'SW',
            'Abia': 'SE', 'Anambra': 'SE', 'Ebonyi': 'SE', 'Enugu': 'SE', 'Imo': 'SE',
            'Akwa Ibom': 'SS', 'Bayelsa': 'SS', 'Cross River': 'SS', 'Delta': 'SS', 'Edo': 'SS', 'Rivers': 'SS',
            'Jigawa': 'NW', 'Kaduna': 'NW', 'Kano': 'NW', 'Katsina': 'NW', 'Kebbi': 'NW', 'Sokoto': 'NW', 'Zamfara': 'NW',
            'Adamawa': 'NE', 'Bauchi': 'NE', 'Borno': 'NE', 'Gombe': 'NE', 'Taraba': 'NE', 'Yobe': 'NE',
            'Benue': 'NC', 'Kogi': 'NC', 'Kwara': 'NC', 'Nasarawa': 'NC', 'Niger': 'NC', 'Plateau': 'NC', 'Federal Capital Territory': 'NC'
        }

        # Modelled probabilities for ethnicity given a geographical zone
        self.zone_ethnicity_weights = {
            'SW': {'Yoruba': 0.70, 'Igbo': 0.15, 'Hausa': 0.05, 'Other': 0.10},
            'SE': {'Igbo': 0.85, 'Yoruba': 0.05, 'Hausa': 0.05, 'Other': 0.05},
            'SS': {'Other': 0.60, 'Igbo': 0.25, 'Yoruba': 0.10, 'Hausa': 0.05},
            'NW': {'Hausa': 0.85, 'Yoruba': 0.05, 'Igbo': 0.05, 'Other': 0.05},
            'NE': {'Hausa': 0.60, 'Other': 0.30, 'Yoruba': 0.05, 'Igbo': 0.05},
            'NC': {'Other': 0.40, 'Hausa': 0.30, 'Yoruba': 0.15, 'Igbo': 0.15}
        }

        self._load_names()
        self._load_age_distribution()

    def _load_age_distribution(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        age_file = os.path.join(base_dir, 'datasets', 'demographics', 'age_sex_distribution.csv')
        
        if os.path.exists(age_file) and os.path.getsize(age_file) > 0:
            with open(age_file, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    min_a = int(row['min_age'])
                    max_a = int(row['max_age'])
                    m_w = float(row['male_pct'])
                    f_w = float(row['female_pct'])
                    self.age_bins.append((min_a, max_a, m_w, f_w))
                    self.total_male_weight += m_w
                    self.total_female_weight += f_w
        else:
            raise FileNotFoundError("age_sex_distribution.csv dataset is missing. Data foundation required.")

    def _load_names(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        names_dir = os.path.join(base_dir, 'datasets', 'names')
            
        files_map = {
            "Hausa": "hausa_names.csv",
            "Yoruba": "yoruba_names.csv",
            "Igbo": "igbo_names.csv",
            "Other": "other_ethnicities_names.csv"
        }
        
        for eth, filename in files_map.items():
            filepath = os.path.join(names_dir, filename)
            self.names[eth] = {"first_m": [], "first_f": [], "last": []}
            
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                with open(filepath, mode='r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row.get('first_m'): self.names[eth]["first_m"].append(row['first_m'].strip())
                        if row.get('first_f'): self.names[eth]["first_f"].append(row['first_f'].strip())
                        if row.get('last'): self.names[eth]["last"].append(row['last'].strip())
                
                # We sort them and then shuffle them based on a known seed string (the ethnicity name)
                # This ensures determinism across runs, but scatters the names so A-names don't all get 99% of zipf weight.
                for k in ["first_m", "first_f", "last"]:
                    self.names[eth][k].sort()
                    r = random.Random(eth + k)
                    r.shuffle(self.names[eth][k])

                self.ethnicities.append(eth)
            else:
                raise FileNotFoundError(f"Name dataset missing: {filepath}")

    def _get_zipf_weights(self, size: int) -> List[float]:
        # Zipfian distribution: weight = 1 / (rank ^ 0.8) for slightly softer curve than pure Zipf
        return [1.0 / ((i + 1) ** 0.8) for i in range(size)]

    def assign_demographics(self, patient: Patient, options):
        current_time_ms = options.reference_time
        # Determine overall gender based on total weights or options
        if options.target_sex:
            gender = options.target_sex.upper()
        else:
            gender = patient.rand_choices(["M", "F"], weights=[self.total_male_weight, self.total_female_weight], k=1)[0]
        
        if options.min_age is not None and options.max_age is not None:
            target_age = patient.rand_int(options.min_age, options.max_age)
        elif options.min_age is not None:
            target_age = patient.rand_int(options.min_age, 100)
        elif options.max_age is not None:
            target_age = patient.rand_int(0, options.max_age)
        else:
            # Determine age bin
            weights = [b[2] if gender == 'M' else b[3] for b in self.age_bins]
            selected_bin = patient.rand_choices(self.age_bins, weights=weights, k=1)[0]
            target_age = patient.rand_int(selected_bin[0], selected_bin[1])
        
        one_year_ms = int(365.25 * 24 * 60 * 60 * 1000)
        birthdate_ms = current_time_ms - (target_age * one_year_ms)
        jitter = patient.rand_int(0, one_year_ms - 1)
        patient.attributes["birthdate"] = birthdate_ms - jitter

        # Modelled Geographic mixing
        state = patient.attributes.get("state", "Federal Capital Territory")
        zone = self.zone_mapping.get(state, "NC")
        eth_probs = self.zone_ethnicity_weights[zone]
        
        eth_keys = list(eth_probs.keys())
        eth_wts = [eth_probs[k] for k in eth_keys]
        
        ethnicity = patient.rand_choices(eth_keys, weights=eth_wts, k=1)[0]
        
        first_name_list = self.names[ethnicity]["first_m"] if gender == "M" else self.names[ethnicity]["first_f"]
        
        if len(first_name_list) > 0:
            first_name = patient.rand_choices(first_name_list, weights=self._get_zipf_weights(len(first_name_list)), k=1)[0]
        else:
            first_name = "Unknown"
            
        last_name_list = self.names[ethnicity]["last"]
        if len(last_name_list) > 0:
            last_name = patient.rand_choices(last_name_list, weights=self._get_zipf_weights(len(last_name_list)), k=1)[0]
        else:
            last_name = "Unknown"
        
        patient.attributes["gender"] = gender
        patient.attributes["ethnicity"] = ethnicity
        patient.attributes["first_name"] = first_name
        patient.attributes["last_name"] = last_name



        # Genotype Assignment (approximating Nigerian population frequencies)
        # HbAA: ~68%, HbAS: ~25%, HbSS: ~2.5%, HbSC: ~0.5%, HbAC: ~4.0%
        genotypes = ['HbAA', 'HbAS', 'HbSS', 'HbSC', 'HbAC']
        g_weights = [68.0, 25.0, 2.5, 0.5, 4.0]
        patient.attributes["genotype"] = patient.rand_choices(genotypes, weights=g_weights, k=1)[0]
