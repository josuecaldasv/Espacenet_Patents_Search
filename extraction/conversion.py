import json
import glob
import os

def get_country_name(country_code):
    return country_codes.get(country_code, "Unavailable information")


def extract_patent_info_clean(patent_json):
    exchange_documents = patent_json.get("exchange-documents", {}).get("exchange-document", [])

    if not isinstance(exchange_documents, list):
        exchange_documents = [exchange_documents]
    if len(exchange_documents) > 1:
        exchange_documents.sort(key=lambda doc: doc.get("bibliographic-data", {}).get("publication-reference", {}).get("document-id", [])[0].get("date", ""), reverse=True)
    exchange_document = exchange_documents[0] if exchange_documents else {}
    bibliographic_data = exchange_document.get("bibliographic-data", {})
    abstract_data = exchange_document.get("abstract", "Unavailable information")
    abstract = "Unavailable information"
    if isinstance(abstract_data, dict):
        abstract = abstract_data.get("p", "Unavailable information")
    elif isinstance(abstract_data, list):
        for entry in abstract_data:
            if isinstance(entry, dict):
                text = entry.get("p", "")
                if text and (text.isascii() or all(ord(char) < 128 for char in text)):
                    abstract = text
                    break
        else:
            abstract = abstract_data[0].get("p", "Unavailable information")
    invention_title_data = bibliographic_data.get("invention-title", "Unavailable information")
    invention_title = "Unavailable information"
    if isinstance(invention_title_data, list):
        for title in invention_title_data:
            if title and (title.isascii() or all(ord(char) < 128 for char in title)):
                invention_title = title
                break
        else:
            invention_title = invention_title_data[0]
    elif isinstance(invention_title_data, str):
        invention_title = invention_title_data
    inventors = bibliographic_data.get("parties", {}).get("inventors", {}).get("inventor", [])
    inventor_names = []
    if isinstance(inventors, list):
        for inv in inventors:
            name = inv.get("inventor-name", {}).get("name", "Unavailable information")
            inventor_names.append(name)
    elif isinstance(inventors, dict):
        name = inventors.get("inventor-name", {}).get("name", "Unavailable information")
        inventor_names.append(name)
    applicants = bibliographic_data.get("parties", {}).get("applicants", {}).get("applicant", [])
    applicant_names = []
    if isinstance(applicants, list):
        for app in applicants:
            name = app.get("applicant-name", {}).get("name", "Unavailable information")
            applicant_names.append(name)
    elif isinstance(applicants, dict):
        name = applicants.get("applicant-name", {}).get("name", "Unavailable information")
        applicant_names.append(name)
    publication_reference = bibliographic_data.get("publication-reference", {}).get("document-id", [])
    year = publication_reference[0].get("date", "Unavailable information")[:4] if publication_reference else "Unavailable information"
    country_code = publication_reference[0].get("country", "Unavailable information") if publication_reference else "Unavailable information"
    country = get_country_name(country_code) 
    output = (
        f"Invention Title: {invention_title}\n"
        f"Inventors: {', '.join(inventor_names) if inventor_names else 'Unavailable information'}\n"
        f"Applicants: {', '.join(applicant_names) if applicant_names else 'Unavailable information'}\n"
        f"Year: {year}\n"
        f"Country: {country}\n"
        f"Abstract: {abstract}\n"
    )
    return output



with open('../country_codes.json', 'r', encoding='utf-8') as f:
    country_codes = json.load(f)

with open('dirs_mapping.json', 'r', encoding='utf-8') as f:
    dirs_mapping = json.load(f) 

dirs = ["biblio_output/energy_hydrogen/*.json", "biblio_output/low_carbon_hydrogen/*.json"]


for directory in dirs:
    for file_path in glob.glob(directory):
        try: 
            dir_name = os.path.basename(os.path.dirname(file_path))
            mapped_dir_name = dirs_mapping.get(dir_name, dir_name)
            file_name = os.path.basename(file_path)
            with open(file_path, "r") as file:
                patent_json = json.load(file)
            formatted_output = extract_patent_info_clean(patent_json)
            formatted_output += f"Keywords: {mapped_dir_name}\n"
            with open(f"biblio_output/txt_files/{file_name.replace('.json', '.txt')}", "w") as file:
                file.write(formatted_output)
            print(f"Archivo {file_name} procesado con éxito.")
        except Exception as e:
            print(f"Error en el archivo {file_name}: {str(e)}")
            continue