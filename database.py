import pandas as pd

df = pd.read_csv("database.csv")
diseases = []

base_symptom_list = set()

for index, row in df.iterrows():
    name = row['name']
    type = row['type']
    base_symptoms = row['base_symptoms'].split('\n')
    for sym in base_symptoms:
        base_symptom_list.add(sym)
    advance_symptoms = row['advance_symptoms'].split('\n')
    diseases.append({
        'name': name,
        'base_symptoms': base_symptoms,
        'advance_symptoms': advance_symptoms,
        'type': type
    })

base_symptom_list = list(base_symptom_list)
