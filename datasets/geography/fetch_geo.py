import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

url = 'https://en.wikipedia.org/wiki/Local_government_areas_of_Nigeria'
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

tables = soup.find_all('table', {'class': 'wikitable'})
lga_table = None

for table in tables:
    df = pd.read_html(str(table))[0]
    if 'LGA' in df.columns and 'State' in df.columns:
        lga_table = df
        break

if lga_table is not None:
    base_dir = r'C:\Projects\MedSynth\datasets\geography'
    os.makedirs(base_dir, exist_ok=True)
    
    states = lga_table['State'].unique()
    pd.DataFrame({'state': states}).to_csv(os.path.join(base_dir, 'nigeria_states.csv'), index=False)
    
    lgas_df = lga_table[['State', 'LGA']].rename(columns={'State': 'state', 'LGA': 'lga'})
    lgas_df.to_csv(os.path.join(base_dir, 'nigeria_lgas.csv'), index=False)
    print(f'Successfully scraped {len(states)} states and {len(lgas_df)} LGAs from Wikipedia.')
else:
    print('Could not find the appropriate table.')

