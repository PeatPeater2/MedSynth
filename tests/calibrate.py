import os
import collections
from medsynth.generator import Generator, GeneratorOptions

def calibrate_population():
    print("Running MedSynth Population Calibration (10,000 patients)...")
    options = GeneratorOptions()
    options.population_size = 1000
    options.seed = 42
    
    # Load all diseases
    import glob
    gen = Generator(options)
    for mod_path in glob.glob('datasets/diseases/*.json'):
        gen.load_module(mod_path)
        
    pop = gen.run()
    print(f"Generated {len(pop)} patients.\n")
    
    # Demographics
    males = 0
    females = 0
    age_bins = {'0-4':0, '5-14':0, '15-24':0, '25-44':0, '45-64':0, '65+':0}
    state_dist = collections.defaultdict(int)
    
    # Diseases
    disease_counts = collections.defaultdict(int)
    deaths = 0
    
    # Comorbidities
    comorbidity_counts = []
    
    for p in pop:
        # Sex
        g = p.attributes.get('gender')
        if g == 'M': males += 1
        elif g == 'F': females += 1
        
        # Age
        age = p.age_in_years(options.reference_time)
        if age <= 4: age_bins['0-4'] += 1
        elif age <= 14: age_bins['5-14'] += 1
        elif age <= 24: age_bins['15-24'] += 1
        elif age <= 44: age_bins['25-44'] += 1
        elif age <= 64: age_bins['45-64'] += 1
        else: age_bins['65+'] += 1
        
        # State
        state = p.attributes.get('state', 'Unknown')
        state_dist[state] += 1
        
        # Death
        if not p.is_alive(options.reference_time):
            deaths += 1
            
        # Conditions
        conds = set()
        for c in p.record.conditions:
            if c.codes:
                conds.add(c.codes[0]['display'])
                
        for c in conds:
            disease_counts[c] += 1
            
        comorbidity_counts.append(len(conds))
        
    print("=== SEX CALIBRATION ===")
    print(f"Male: {males/len(pop):.2%} | Female: {females/len(pop):.2%}")
    
    print("\n=== AGE CALIBRATION ===")
    for k, v in age_bins.items():
        print(f"{k}: {v/len(pop):.2%}")
        
    print("\n=== STATE DISTRIBUTION (Top 5) ===")
    top_states = sorted(state_dist.items(), key=lambda x: x[1], reverse=True)[:5]
    for k, v in top_states:
        print(f"{k}: {v/len(pop):.2%}")
        
    print("\n=== DISEASE PREVALENCE ===")
    for k, v in sorted(disease_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{k}: {v} cases ({v/len(pop):.2%})")
        
    print(f"\nTotal Deaths: {deaths} ({deaths/len(pop):.2%})")
    print(f"Average Conditions per Patient: {sum(comorbidity_counts)/len(pop):.2f}")
    
if __name__ == '__main__':
    calibrate_population()
