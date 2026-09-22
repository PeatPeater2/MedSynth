# MEDSYNTH PYTHON EXAMINATION (100 QUESTIONS)

## LEVEL 1 — FUNDAMENTALS
1. [EASY] What data structure is used to hold a patient's conditions?
2. [EASY] What is the difference between a list and a dictionary in the context of the JSON disease modules?
3. [EASY] How do you handle file paths across different operating systems in Python?
4. [EASY] What happens if import csv fails?
5. [EASY] How is the with open(...) context manager used when reading 
igeria_states.csv?
6. [EASY] What is the difference between == and is?
7. [EASY] How do you iterate over a dictionary of LGA populations?
8. [EASY] What is a Python tuple and where might it be used over a list?
9. [EASY] What does the pass statement do?
10. [EASY] How does exception handling (	ry/except) work in file loading?
11. [EASY] What is the purpose of __init__.py in the medsynth/ folder?
12. [EASY] How do you check if a key exists in a JSON dictionary?
13. [EASY] What is the difference between an integer and a float in Python?
14. [EASY] How are strings concatenated in the CSV exporter?
15. [EASY] What is a boolean flag?
16. [EASY] How do you define a function in Python?
17. [EASY] What is the return value of a function that has no 
eturn statement?
18. [EASY] How do you import a specific class from a module?
19. [EASY] What does sys.exit(1) do in cli.py?
20. [EASY] How do you add an item to a list?

## LEVEL 2 — INTERMEDIATE PYTHON
21. [MEDIUM] Why are classes used in MedSynth (e.g. Patient) rather than passing dictionaries around?
22. [MEDIUM] What does self represent in class Generator?
23. [MEDIUM] How does inheritance work? Does MedSynth use it?
24. [MEDIUM] What is a class method vs an instance method?
25. [MEDIUM] What is the @patch.object decorator used for in enchmark.py?
26. [MEDIUM] What is an iterator?
27. [MEDIUM] How do list comprehensions work, and where could they be used?
28. [MEDIUM] What is the purpose of type hints (e.g. patient: Patient)?
29. [MEDIUM] Why is pathlib often preferred over os.path?
30. [MEDIUM] How does Python's 
andom module generate numbers?
31. [MEDIUM] What happens when you set 
andom.seed()?
32. [MEDIUM] What is a dataclass and could it replace standard classes in MedSynth?
33. [MEDIUM] What are Python Enums?
34. [MEDIUM] How does rgparse work in cli.py?
35. [MEDIUM] What is a dictionary comprehension?
36. [MEDIUM] How does variable scope work in Python?
37. [MEDIUM] What is the difference between a shallow copy and a deep copy?
38. [MEDIUM] How does Python handle memory management (Garbage Collection)?
39. [MEDIUM] What are kwargs (**kwargs)?
40. [MEDIUM] What does if __name__ == '__main__': mean?

## LEVEL 3 — PYTHON USED IN MEDSYNTH
41. [HARD] Why does GeneratorOptions exist instead of just passing 10 arguments into the Generator class?
42. [HARD] Why is ssign_point a method of Geography rather than a standalone function?
43. [HARD] What does the lgas_by_state dictionary represent in geography.py?
44. [HARD] Why is it appropriate to use a dictionary mapping states to LGA lists?
45. [HARD] Why is the global random generator seeded in cli.py?
46. [HARD] What happens if the seed is completely removed?
47. [HARD] Why is sys imported in cli.py?
48. [HARD] What happens if csv.DictReader fails to parse a row?
49. [HARD] Why are Nigerian names loaded into memory once rather than reading the file for every patient?
50. [HARD] Why is os.path.join used instead of string concatenation with slashes?
51. [HARD] Why is the HealthRecord logic not inside main.py?
52. [HARD] What is the time complexity of looking up a state in a dictionary vs a list?
53. [HARD] Why is json.load() used over manual string parsing?
54. [HARD] What exception would be raised if a disease module JSON has a missing comma?
55. [HARD] Why does medsynth.bat pass execution to Python rather than doing it natively?
56. [HARD] Why do we shift the random seed by the patient count when processing multiple groups?
57. [HARD] What happens if two variables reference the same Patient object?
58. [HARD] Why is the Python ThreadPoolExecutor used (or not used) in generation?
59. [HARD] Why does cli.py lowercase the state strings before comparing them?
60. [HARD] What happens to the memory footprint if we append 1 million patients to ll_patients?

## LEVEL 4 — PYTHON CODE-READING QUESTIONS
61. [HARD] Explain the parse_group function in cli.py line by line. What are its inputs and outputs?
62. [HARD] What assumptions does the JSON loading logic in generator.py make?
63. [HARD] What happens in the state machine if an invalid transition name is provided?
64. [HARD] What is the time complexity of finding a patient's LGA in the lgas_by_state dictionary?
65. [HARD] What could cause the CSV Exporter to fail?
66. [HARD] How would you rewrite the demographics logic to use pandas? Why didn't we?
67. [HARD] Why was rgparse chosen over sys.argv?
68. [HARD] Explain the __init__ constructor of Patient.
69. [HARD] What happens if a patient reaches age 120? Where is that enforced?
70. [HARD] How does the state machine process a Delay state in code?
71. [HARD] Explain how FHIR UUIDs are generated in the exporter.
72. [HARD] What happens if a dataset CSV is completely empty?
73. [HARD] How does the codebase distinguish between male and female when assigning names?
74. [HARD] Why is ase_dir determined dynamically rather than hardcoded?
75. [HARD] Explain how the csv.writer is used to write patient records.
76. [HARD] What happens if 	arget_state is provided but is not in the dataset?
77. [HARD] How are multiple concurrent diseases tracked on a single patient object?
78. [HARD] What happens if a module attempts to add a duplicate condition?
79. [HARD] How does getattr or hasattr work in Python, and where might it be useful here?
80. [HARD] Explain how ll_patients.extend(cohort) differs from ppend.

## LEVEL 5 — PYTHON DEBUGGING QUESTIONS
81. [EXPERT] The generator produces identical patients. What would you inspect?
82. [EXPERT] The CSV exporter produces zero records. Where would you debug first?
83. [EXPERT] FHIR references between Conditions and Patients are broken. What part of the architecture is responsible?
84. [EXPERT] The JSON module loads but produces no conditions on the patient. How would you investigate?
85. [EXPERT] The random seed is identical, but results are different across runs. What could cause that in Python?
86. [EXPERT] An import works when running main.py but fails when using medsynth.bat. Why?
87. [EXPERT] A dataset path works on Windows but fails on Linux. Why?
88. [EXPERT] 100,000 patients cause memory exhaustion (OOM). What would you change in the Python code?
89. [EXPERT] A disease module gets stuck in an infinite loop. How do you find the offending state?
90. [EXPERT] The ge attribute is suddenly a string instead of an integer, breaking calculations. Where could this happen?
91. [EXPERT] The system throws a KeyError: 'Kano'. What is the underlying data issue?
92. [EXPERT] rgparse throws unrecognized arguments. How do you fix CLI argument parsing?
93. [EXPERT] The generator crashes halfway through with an IOError writing to a file. Why?
94. [EXPERT] A new module creates a condition, but it never shows up in FHIR. What mapping is missing?
95. [EXPERT] Patients are suddenly living to 300 years old. What logic broke?
96. [EXPERT] The ZIPF distribution is generating only one name for everyone. What is wrong with the parameters?
97. [EXPERT] You notice CPU utilization is at 12% during generation. Why isn't Python using all cores?
98. [EXPERT] How do you step through the GMF transition logic using pdb?
99. [EXPERT] The program hangs silently. What could cause a deadlock?
100. [EXPERT] You get a RecursionError in the state machine. What architectural flaw causes this?
