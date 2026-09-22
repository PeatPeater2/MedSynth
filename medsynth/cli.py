import sys
import os
import argparse
import time
import csv

from medsynth.generator import Generator, GeneratorOptions
from medsynth.exporters import Exporter

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_geographic_data():
    base_dir = get_base_dir()
    states_file = os.path.join(base_dir, 'datasets', 'geography', 'nigeria_states.csv')
    lgas_file = os.path.join(base_dir, 'datasets', 'geography', 'nigeria_lgas.csv')
    
    valid_states = []
    if os.path.exists(states_file):
        with open(states_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                valid_states.append(row['state'])
                
    lgas_by_state = {}
    if os.path.exists(lgas_file):
        with open(lgas_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row['state']
                lga = row['lga']
                if state not in lgas_by_state:
                    lgas_by_state[state] = []
                lgas_by_state[state].append(lga)
                
    return valid_states, lgas_by_state

def get_available_diseases():
    base_dir = get_base_dir()
    modules_dir = os.path.join(base_dir, 'datasets', 'diseases')
    if not os.path.exists(modules_dir):
        modules_dir = os.path.join(base_dir, 'medsynth', 'data', 'modules')
        
    diseases = []
    if os.path.exists(modules_dir):
        for file in os.listdir(modules_dir):
            if file.endswith('.json'):
                diseases.append(file.replace('.json', ''))
    return diseases

def parse_age(age_str):
    if not age_str or age_str.lower() == 'all':
        return None, None
        
    age_groups = {
        'newborn': (0, 0),
        'child': (1, 14),
        'adolescent': (15, 19),
        'adult': (20, 64),
        'elderly': (65, 100)
    }
    
    if age_str.lower() in age_groups:
        return age_groups[age_str.lower()]
        
    if '-' in age_str:
        parts = age_str.split('-')
        try:
            min_age = int(parts[0])
            max_age = int(parts[1])
            if min_age < 0 or max_age < 0 or min_age > max_age:
                print(f"Error: Invalid age range '{age_str}'. Must be non-negative and min <= max.")
                sys.exit(1)
            return min_age, max_age
        except ValueError:
            print(f"Error: Invalid age range '{age_str}'.")
            sys.exit(1)
    else:
        try:
            age = int(age_str)
            if age < 0:
                print(f"Error: Invalid age '{age_str}'. Must be non-negative.")
                sys.exit(1)
            return age, age
        except ValueError:
            print(f"Error: Invalid age '{age_str}'.")
            sys.exit(1)

def build_options(count, state_str, lga, city, sex_str, age_str, disease_str, seed, valid_states, lgas_by_state, available_diseases):
    if count <= 0:
        print(f"Error: Invalid patient count '{count}'. Must be greater than 0.")
        sys.exit(1)
        
    options = GeneratorOptions()
    options.population_size = count
    
    # Sex
    if sex_str and sex_str.lower() != 'all':
        sexes = sex_str.lower().split(',')
        if len(sexes) == 1:
            if sexes[0] in ['m', 'male']:
                options.target_sex = 'M'
            elif sexes[0] in ['f', 'female']:
                options.target_sex = 'F'
            else:
                print(f"Error: Invalid sex '{sex_str}'. Use 'male' or 'female'.")
                sys.exit(1)
        # If multiple, leave target_sex None so demographic engine handles probabilistically
                
    # Age
    if age_str and age_str.lower() != 'all':
        min_age, max_age = parse_age(age_str)
        options.min_age = min_age
        options.max_age = max_age
        
    # State
    if state_str and state_str.lower() != 'all':
        states = state_str.split(',')
        validated_states = []
        valid_states_lower = {s.lower(): s for s in valid_states}
        for s in states:
            s_lower = s.lower().strip()
            if s_lower not in valid_states_lower:
                print(f"Error: Invalid state '{s}'.")
                sys.exit(1)
            validated_states.append(valid_states_lower[s_lower])
            
        if len(validated_states) == 1:
            options.target_state = validated_states[0]
        else:
            options.target_state = validated_states
            
    # LGA / City
    if lga:
        found = False
        lga_lower = lga.lower().strip()
        for s, llist in lgas_by_state.items():
            llist_lower = {l.lower(): l for l in llist}
            if lga_lower in llist_lower:
                found = True
                real_lga = llist_lower[lga_lower]
                if options.target_state and options.target_state != s:
                    print(f"Error: LGA '{real_lga}' belongs to '{s}', but state was restricted to '{options.target_state}'.")
                    sys.exit(1)
                options.target_lga = real_lga
                break
        if not found:
            print(f"Error: LGA '{lga}' not found in Nigerian geography dataset.")
            sys.exit(1)
        
    if city:
        # We don't have a cities.csv currently. But we should accept it and map it to LGA if we can, or just set it.
        # But instructions say: "Do not fabricate cities or LGAs. An invalid combination must produce an error".
        # Since we have no city list, we must error if they use --city.
        print(f"Error: --city is not currently supported as there is no city-level dataset available.")
        sys.exit(1)
        
    if seed is not None:
        options.seed = seed
        
    return options

def parse_group(group_str, valid_states, lgas_by_state):
    # format: sex:count:location:age
    parts = group_str.split(':')
    if len(parts) < 3:
        print(f"Error: Malformed group '{group_str}'. Expected 'sex:count:location' or 'sex:count:location:age'.")
        sys.exit(1)
        
    sex = parts[0]
    try:
        count = int(parts[1])
    except ValueError:
        print(f"Error: Group count '{parts[1]}' is not a valid integer.")
        sys.exit(1)
        
    location = parts[2]
    age = parts[3] if len(parts) > 3 else 'all'
    
    # Determine if location is a State or LGA
    target_state = None
    target_lga = None
    
    valid_states_lower = {s.lower(): s for s in valid_states}
    location_lower = location.lower().strip()
    
    if location_lower in valid_states_lower:
        target_state = valid_states_lower[location_lower]
    else:
        # Check if it's an LGA
        found = False
        for s, llist in lgas_by_state.items():
            llist_lower = {l.lower(): l for l in llist}
            if location_lower in llist_lower:
                found = True
                target_state = s
                target_lga = llist_lower[location_lower]
                break
        if not found:
            # Special case for "Ibadan" as requested in user examples. Ibadan is a city spanning LGAs in Oyo.
            # We map it to Oyo state directly if we don't have city support.
            if location_lower == 'ibadan':
                target_state = 'Oyo'
            else:
                print(f"Error: Location '{location}' not found in Nigerian geography dataset.")
                sys.exit(1)
    
    return count, target_state, target_lga, None, sex, age, 'all'

import json

def setup_generator(options, diseases_str, available_diseases):
    generator = Generator(options)
    
    base_dir = get_base_dir()
    modules_dir = os.path.join(base_dir, 'datasets', 'diseases')
    if not os.path.exists(modules_dir):
        modules_dir = os.path.join(base_dir, 'medsynth', 'data', 'modules')

    if os.path.exists(modules_dir):
        files_to_load = os.listdir(modules_dir)
        if diseases_str and diseases_str.lower() != 'all':
            allowed = [d.lower().strip() for d in diseases_str.split(',')]
            
            # Validate diseases
            for d in allowed:
                if d not in [x.lower() for x in available_diseases]:
                    print(f"Error: Invalid disease '{d}'. Available diseases: {', '.join(available_diseases)}")
                    sys.exit(1)
            
            files_to_load = [f for f in files_to_load if f.lower().replace('.json', '') in allowed]
            
        for file in files_to_load:
            if file.endswith('.json'):
                path = os.path.join(modules_dir, file)
                generator.load_module(path)
                
    return generator

def generate_cohort(options, diseases_str, available_diseases):
    gen = setup_generator(options, diseases_str, available_diseases)
    return gen.run()

def main():
    parser = argparse.ArgumentParser(description='MedSynth synthetic patient generator for Nigeria.', prog='medsynth')
    subparsers = parser.add_subparsers(dest='command')
    
    gen_parser = subparsers.add_parser('generate', help='Generate a synthetic population')
    
    gen_parser.add_argument('-p', '--patients', type=int, default=10, help='Number of patients (Default: 10)')
    gen_parser.add_argument('--state', type=str, default='Osun', help='Target state (Default: Osun)')
    gen_parser.add_argument('--lga', type=str, help='Target Local Government Area (LGA)')
    gen_parser.add_argument('--city', type=str, help='Target city (Not currently supported)')
    gen_parser.add_argument('--sex', type=str, default='all', help='Target sex: male, female, or all (Default: all)')
    gen_parser.add_argument('--age', type=str, default='all', help='Age or range e.g. 25, 20-40, child (Default: all)')
    gen_parser.add_argument('--disease', type=str, default='all', help='Specific diseases to include (Default: all)')
    gen_parser.add_argument('-f', '--format', type=str, default='csv,json,fhir', help='Output formats e.g. csv,fhir (Default: csv,json,fhir)')
    gen_parser.add_argument('-o', '--output', type=str, help='Custom output directory (Default: MedSynthOutput)')
    gen_parser.add_argument('--seed', type=int, help='Random seed for reproducibility (Default: random)')
    gen_parser.add_argument('--group', action='append', help='Group definition: sex:count:location[:age]')
    gen_parser.add_argument('--stream', action='store_true', help='Use streaming generation (removes RAM limits)')
    gen_parser.add_argument('-w', '--workers', type=int, default=1, help='Number of CPU processes for streaming generation (Default: 1)')
    gen_parser.add_argument('--resume', type=str, help='Resume from a checkpoint JSON file')
    gen_parser.add_argument('--checkpoint-every', type=int, default=10000, help='Checkpoint interval (Default: 10000)')
    
    args = parser.parse_args()
    
    if args.command != 'generate':
        parser.print_help()
        sys.exit(0)

    # Validate Formats
    formats = [f.lower().strip() for f in args.format.split(',')]
    if 'all' in formats:
        formats = ['csv', 'json', 'fhir']
    valid_formats = ['csv', 'json', 'fhir']
    for f in formats:
        if f not in valid_formats:
            print(f"Error: Invalid format '{f}'. Valid formats: csv, json, fhir, all")
            sys.exit(1)
            
    valid_states, lgas_by_state = load_geographic_data()
    available_diseases = get_available_diseases()
    
    base_dir = get_base_dir()
    output_dir = args.output if args.output else os.path.join(base_dir, 'MedSynthOutput')
    
    # Clean/create directories only for requested formats
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for fmt in valid_formats:
        fmt_dir = os.path.join(output_dir, fmt)
        if fmt in formats:
            if not os.path.exists(fmt_dir):
                os.makedirs(fmt_dir)
        else:
            pass

    if args.stream:
        start_index = 0
        if args.resume:
            if not os.path.exists(args.resume):
                print(f"Error: Checkpoint file '{args.resume}' not found.")
                sys.exit(1)
            try:
                with open(args.resume, 'r') as f:
                    ckpt = json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error: Checkpoint file '{args.resume}' is corrupted or invalid JSON. ({e})")
                sys.exit(1)
            if ckpt.get('seed') != args.seed:
                print(f"Error: Checkpoint seed {ckpt.get('seed')} does not match provided seed {args.seed}!")
                sys.exit(1)
            if ckpt.get('target_population') != args.patients:
                print(f"Error: Checkpoint population {ckpt.get('target_population')} does not match provided population {args.patients}!")
                sys.exit(1)
            if set(ckpt.get('output_formats', [])) != set(formats):
                print(f"Error: Checkpoint formats {ckpt.get('output_formats')} do not match provided formats {formats}!")
                sys.exit(1)
            start_index = ckpt.get('patients_completed', 0)
            print(f"Resuming from checkpoint... starting at patient index {start_index}")

        exporter = Exporter(output_dir, formats)
        exporter.begin(resume=bool(args.resume))
        patients_generated = start_index
        start_time = time.time()
        checkpoint_file = os.path.join(output_dir, 'checkpoint.json')

        def write_checkpoint(status, error=None):
            tmp_path = checkpoint_file + '.tmp'
            data = {
                'status': status,
                'seed': args.seed,
                'target_population': args.patients,
                'patients_completed': patients_generated,
                'output_formats': formats,
                'time_seconds': time.time() - start_time
            }
            if error: data['error'] = error
            with open(tmp_path, 'w') as f:
                json.dump(data, f, indent=2)
            os.replace(tmp_path, checkpoint_file)

        try:
            if args.group:
                print("Warning: Checkpoint/resume is currently only fully supported for standard (non-grouped) generation. Order constraints apply.")
                for g_str in args.group:
                    count, state_str, lga, city, sex_str, age_str, disease_str = parse_group(g_str, valid_states, lgas_by_state)
                    opts = build_options(count, state_str, lga, city, sex_str, age_str, disease_str, args.seed, valid_states, lgas_by_state, available_diseases)
                    generator = setup_generator(opts, disease_str, available_diseases)
                    for p in generator.generate_stream(workers=args.workers, start_index=start_index):
                        exporter.export_patient(p)
                        patients_generated += 1
                        if patients_generated % args.checkpoint_every == 0:
                            exporter.flush()
                            write_checkpoint("RUNNING")
                    if args.seed is not None:
                        args.seed += count
            else:
                opts = build_options(args.patients, args.state, args.lga, args.city, args.sex, args.age, args.disease, args.seed, valid_states, lgas_by_state, available_diseases)
                generator = setup_generator(opts, args.disease, available_diseases)
                for p in generator.generate_stream(workers=args.workers, start_index=start_index):
                    exporter.export_patient(p)
                    patients_generated += 1
                    if patients_generated % args.checkpoint_every == 0:
                        exporter.flush()
                        write_checkpoint("RUNNING")

            exporter.flush()
            write_checkpoint("COMPLETED")
            
        except (Exception, KeyboardInterrupt) as e:
            status = "FAILED" if not isinstance(e, KeyboardInterrupt) else "INTERRUPTED"
            exporter.flush()
            write_checkpoint(status, str(e))
            print(f"\n{status} during streaming generation: {e}")
            exporter.end()
            sys.exit(1)
            
        exporter.end()
        
        print(f" MedSynth Patient Generator Nigeria.")
        print(f"Total Patients Generated (Streamed): {patients_generated}")
        print(f"Output Directory: {output_dir}")
        print(f"Formats Generated: {', '.join(formats)}")
        
    else:
        # Legacy batch generation
        all_patients = []
        if args.group:
            for g_str in args.group:
                count, state_str, lga, city, sex_str, age_str, disease_str = parse_group(g_str, valid_states, lgas_by_state)
                opts = build_options(count, state_str, lga, city, sex_str, age_str, disease_str, args.seed, valid_states, lgas_by_state, available_diseases)
                cohort = generate_cohort(opts, disease_str, available_diseases)
                all_patients.extend(cohort)
                if args.seed is not None:
                    args.seed += count
        else:
            opts = build_options(args.patients, args.state, args.lga, args.city, args.sex, args.age, args.disease, args.seed, valid_states, lgas_by_state, available_diseases)
            cohort = generate_cohort(opts, args.disease, available_diseases)
            all_patients.extend(cohort)
            
        exporter = Exporter(output_dir, formats)
        exporter.export(all_patients)
        
        print(f" MedSynth Patient Generator Nigeria.")
        print(f"Total Patients Generated: {len(all_patients)}")
        print(f"Output Directory: {output_dir}")
        print(f"Formats Generated: {', '.join(formats)}")

if __name__ == '__main__':
    main()
