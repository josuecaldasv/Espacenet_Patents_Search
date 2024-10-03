import requests
import os
import utils
from dotenv import load_dotenv

load_dotenv()
CLIENT_KEY = os.getenv("CLIENT_KEY")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def get_patent_usage( token):
    url = F"https://ops.epo.org/3.2/developers/me/stats/usage?timeRange=22/09/2024~29/09/2024"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/exchange+xml',
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.text
    elif response.status_code == 404:
        print(f"Error 404: No se encontró usage")
        return None
    else:
        print(f"Error en la consulta de usage ({response.status_code})")
        return None
    

client_key = "auc2MieBZtPFyIvfHfUjpZnBi9DByAWVcHAVAbsYmnFTvPMA"
client_secret = "OUA0e0isLJsFyOePGOCDNM3P2MGHa5gqg6bGqgGCJh5Db13HLUjPJxJlc58Qv8QK"
access_token = utils.get_access_token(CLIENT_KEY, CLIENT_SECRET)
response = get_patent_usage(access_token)
if response:
    print(response)