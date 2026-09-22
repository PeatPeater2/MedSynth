import random

lgas = [ "Ife Central", "Ilesa East", "Osogbo", "Ede South"]

pickedLGA=random.choice(lgas)

print(pickedLGA)

lgass = ["Ife North", "Ife South", "Oke-Mesi", "Ede North"]

population_weights = [0.4, 0.3, 0.2, 0.1]

PICKED_LGA = random.choices(lgass, weights=population_weights, k=1)[0]
print(PICKED_LGA)



import random

# =========================================================
# 1. THE PATIENT (This is medsynth/patient.py)
# =========================================================
class Patient:
    def __init__(self, seed: int):
        self.seed = seed
        self.random = random.Random(seed)  # The patient's private dice!

    def pick_name(self):
        nigerian_names = ["Habib", "Sewa", "Obinna", "Amina", "Efe"]
        return self.random.choice(nigerian_names)


# =========================================================
# 2. THE GENERATOR (This is medsynth/generator.py)
# =========================================================
class Generator:
    def __init__(self, master_seed: int):
        self.master_dice = random.Random(master_seed)

    def make_patient(self):
        # Step A: Roll a unique baby seed
        baby_seed = self.master_dice.randint(1000, 9999)

        # Step B: Deliver it to Patient!
        new_patient = Patient(seed=baby_seed)
        return new_patient


# =========================================================
# 3. YOU / THE DASHBOARD (This is streamlit_app.py)
# =========================================================
# You type 42 on the keyboard:
user_input_seed = 42

# You give 42 to the Generator:
generator = Generator(master_seed=user_input_seed)

# You generate 3 patients:
for i in range(3):
    person = generator.make_patient()
    print(f"Patient #{i+1} | Seed: {person.seed} | Name: {person.pick_name()}")







class HealthRecord:
    def __init__(self, patient):
        self.patient = patient
        self.diagnoses = []


class Patient:
    def __init__(self, name: str):
        self.name = name
        # Object Composition happens right here:
        self.record = HealthRecord(self)


# 1. Create a patient
p = Patient("Amina")

# 2. The Patient uses its HealthRecord:
p.record.diagnoses.append("Malaria")
print("Diagnoses in record:", p.record.diagnoses)

# 3. The HealthRecord reaches back to the Patient:
print("Patient name from record:", p.record.patient.name)

# 4. Are they pointing to the exact same person?
print("Same object in memory?", p.record.patient is p)


class Patient2:
    def __init__(self, name: str):
        self.name = name

class VITALSMONITOR:
    def __init__(self, patient: Patient2):
        self.patient = patient
        self.vitals = {}
        
    def record_pulse(self, pulse: int):
         pass

class Engine:
        def __init__(self, horse_power: int):
            self.horse_power= horse_power

class Wheel:
        def __init__(self, size: int):
            self.size = size    

class Car:
        def __init__(self, make, model, horse_power, wheel_size):
            self.engine = Engine(horse_power)
            self.wheels = [Wheel(wheel_size) for wheel in range(4)]
            self.make = make
            self.model = model



import datetime

print("Current date and time:", datetime.datetime.now())
print("Current date:", datetime.date.today())