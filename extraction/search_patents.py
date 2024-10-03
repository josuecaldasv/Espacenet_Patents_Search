import requests
import json
import time
import os
import xml.etree.ElementTree as ET
import utils
from dotenv import load_dotenv

load_dotenv()
CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
output_path = "search_patents"   
os.makedirs(output_path, exist_ok=True)

keywords = ['Low Carbon Hydrogen', 'Energy Hydrogen']
ranges = ['1-2000', '2001-4000', '4001-6000', '6001-8000', '8001-10000']


access_token = utils.get_access_token(CLIENT_KEY, CLIENT_SECRET)
if access_token:
    for keyword in keywords:
        search_results = utils.search_patents(access_token, keyword, 2001, 100, 4000)
        with open(os.path.join(output_path, f"{keyword}_2001_4000.json"), "w") as f:
            json.dump(search_results, f, indent=4, ensure_ascii=False)
