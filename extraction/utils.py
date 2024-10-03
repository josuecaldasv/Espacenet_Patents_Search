import requests
import base64
import json
import time
import os
import xml.etree.ElementTree as ET


def get_access_token(client_key, client_secret):
    credentials = f"{client_key}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    url = "https://ops.epo.org/3.2/auth/accesstoken"
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"Error obteniendo token: {response.status_code}")
        return None
    

def search_patents(access_token, keyword, start=1, batch_size=100, max_results=1000):
    url = "https://ops.epo.org/3.2/rest-services/published-data/search"
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    all_results = []
    while start <= max_results:
        end = start + batch_size - 1
        params = {
            "q": keyword,
            "range": f"{start}-{end}"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            search_result = data.get("ops:world-patent-data", {}).get("ops:biblio-search", {}).get("ops:search-result", {})
            publications = search_result.get("ops:publication-reference", [])
            all_results.extend(publications)
        else:
            response.raise_for_status()
        start += batch_size
        time.sleep(1) 
    return all_results


def xml_to_dict(element):
    if len(element) == 0:
        return element.text
    result = {}
    for child in element:
        child_result = xml_to_dict(child)
        tag = child.tag.split('}', 1)[-1]
        if tag in result:
            if not isinstance(result[tag], list):
                result[tag] = [result[tag]]
            result[tag].append(child_result)
        else:
            result[tag] = child_result
    return result


def file_exists_in_any_subfolder(filename, output_paths):
    for path in output_paths:
        if os.path.exists(os.path.join(path, filename)):
            return True
    return False


def get_patent_biblio(doc_number, token):
    url = f"http://ops.epo.org/rest-services/published-data/publication/epodoc/{doc_number}/biblio"
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/exchange+xml',
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            return root
        except ET.ParseError as e:
            print(f"Error al analizar el XML: {e}")
            return None
    elif response.status_code == 404:
        print(f"Error 404: No se encontró biblio para el documento {doc_number}")
        return None
    else:
        print(f"Error en la consulta de biblio ({response.status_code}) para el documento {doc_number}")
        return None