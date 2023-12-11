import pandas as pd

df = pd.read_csv('database.csv')

print(df.columns)
print(df['advance_symtoms'].values)
