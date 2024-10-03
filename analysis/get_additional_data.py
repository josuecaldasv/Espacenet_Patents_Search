import pandas as pd
import networkx as nx
import os
import sys
from dotenv import load_dotenv
import time
import json

sys.path.append( '..')

import extraction.utils as eu


load_dotenv()
CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

check_paths = ["../extraction/biblio_output/low_carbon_hydrogen", "../extraction/biblio_output/energy_hydrogen", "../extraction/biblio_output/additional_data"]
output_path = "../extraction/biblio_output/additional_data"
os.makedirs(output_path, exist_ok=True)

total_patents = pd.read_excel('total_patents_df.xlsx')
total_patents = total_patents.rename(columns={'Unnamed: 0': 'id'})
total_patents = total_patents.head(50)
id_list = total_patents['id'].tolist()

G_no_isolated = nx.read_edgelist("graphs/non_isolated_graph.edgelist", create_using=nx.DiGraph())
patent_numbers = list(G_no_isolated.nodes())

total_list = id_list + patent_numbers

access_token = eu.get_access_token(CLIENT_KEY, CLIENT_SECRET)

patents = []
for id in total_list:
    filename = f"{id}.json"
    if not eu.file_exists_in_any_subfolder(filename, check_paths):
        print(f"Guardando {filename}")
        time.sleep(5)
        response = eu.get_patent_biblio(id, access_token)
        if response:
            biblio_dict = eu.xml_to_dict(response)
            with open(os.path.join(output_path, filename), "w") as f:
                json.dump(biblio_dict, f, indent=4, ensure_ascii=False)
            print(f"Guardado {output_path}/{filename}")
    else:
        print(f"{output_path}/{filename} ya existe, omitiendo")

