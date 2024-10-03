import os
import sys
import json
import glob
import pandas as pd
import networkx as nx
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('stopwords')
nltk.download('wordnet')

sys.path.append('..')

with open('../country_codes.json', 'r', encoding='utf-8') as f:
    country_codes = json.load(f)

def get_country_name(country_code):
    return country_codes.get(country_code, "Unavailable information")


def get_patents_citations(path):
    patents = []
    files = glob.glob(path + '/*/*.json')
    for file in files:
        if file.endswith('.json'):
            patent_number = os.path.splitext(os.path.basename(file))[0]
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                exchange_documents = data.get("exchange-documents", {}).get("exchange-document")
                if isinstance(exchange_documents, dict):
                    exchange_documents = [exchange_documents]
                for document in exchange_documents:
                    patent = {}
                    patent['patent_number'] = patent_number
                    abstract_data = document.get("abstract", "Unavailable information")
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
                    patent['abstract'] = abstract
                    references_data = document.get("bibliographic-data", {}).get("references-cited")
                    citations = set()
                    if references_data:
                        references = references_data.get("citation", [])
                        if isinstance(references, list):
                            for ref in references:
                                ref_doc_id = ref.get("patcit", {}).get("document-id")
                                if isinstance(ref_doc_id, list) and ref_doc_id:
                                    for doc in ref_doc_id:
                                        doc_number = doc.get('doc-number')
                                        country = doc.get('country')
                                        if doc_number:
                                            no_country_code_version = doc_number if not country else doc_number.replace(country, '').strip()
                                            if no_country_code_version in citations and country:
                                                citations.remove(no_country_code_version)
                                            if country:
                                                citations.add(country + doc_number)
                                            else:
                                                citations.add(doc_number)
                    patent['citations'] = list(citations)
                    bibliographic_data = document.get("bibliographic-data", {})
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
                    patent['invention_title'] = invention_title
                    inventors = bibliographic_data.get("parties", {}).get("inventors", {}).get("inventor", [])
                    inventor_names = []
                    if isinstance(inventors, list):
                        for inv in inventors:
                            name = inv.get("inventor-name", {}).get("name", "Unavailable information")
                            inventor_names.append(name)
                    elif isinstance(inventors, dict):
                        name = inventors.get("inventor-name", {}).get("name", "Unavailable information")
                        inventor_names.append(name)
                    patent['inventor_names'] = inventor_names
                    invention_titles = bibliographic_data.get("parties", {}).get("invention-title", "Unavailable information")
                    invention_title_names = []
                    if isinstance(invention_titles, list):
                        for inv_title in invention_titles:
                            title = inv_title.get("invention-title", "Unavailable information")
                            invention_title_names.append(title)
                    elif isinstance(invention_titles, dict):
                        title = invention_titles.get("invention-title", "Unavailable information")
                        invention_title_names.append(title)
                    patent['invention_title_names'] = invention_title_names
                    applicants = bibliographic_data.get("parties", {}).get("applicants", {}).get("applicant", [])
                    applicant_names = []
                    if isinstance(applicants, list):
                        for app in applicants:
                            name = app.get("applicant-name", {}).get("name", "Unavailable information")
                            applicant_names.append(name)
                    elif isinstance(applicants, dict):
                        name = applicants.get("applicant-name", {}).get("name", "Unavailable information")
                        applicant_names.append(name)
                    patent['applicant_names'] = applicant_names
                    publication_reference = bibliographic_data.get("publication-reference", {}).get("document-id", [])
                    year = publication_reference[0].get("date", "Unavailable information")[:4] if publication_reference else "Unavailable information"
                    country_code = publication_reference[0].get("country", "Unavailable information") if publication_reference else "Unavailable information"
                    country = get_country_name(country_code)
                    patent['year'] = year
                    patent['country'] = country
                    if patent.get('patent_number') and citations:
                        patents.append(patent)
    return patents


def convert_grafo_to_df(G):
    input_degree = dict(G.in_degree())
    output_degree = dict(G.out_degree())
    pagerank = nx.pagerank(G)
    patents_info = {}
    for patent in G.nodes():
        patents_info[patent] = {
            'input_degree': input_degree[patent],
            'output_degree': output_degree[patent],
            'pagerank': pagerank[patent],
        }
    patents_df = pd.DataFrame(patents_info).T
    return patents_df

def clean_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    tokens = text.split()
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
    return ' '.join(tokens)


def clean_and_deduplicate_names(names):
    if names == 'Unavailable information':
        return names
    name_list = eval(names)
    cleaned_names = [re.sub(r'\[[A-Z]{2}\]', '', name).replace(',', '').strip() for name in name_list]
    deduplicated_names = list(dict.fromkeys(cleaned_names))
    return deduplicated_names


def fill_country_from_patent_number(row):
    if row['country'] == 'Unavailable information':
        country_code = row['patent_number'][:2]
        return country_codes.get(country_code, 'Unknown')
    return row['country']


def normalize_text(text):
    stop_words = set([
    "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"
    ]) 
    words = re.split(r'\s+', text.strip().lower())
    normalized_words = [
        word.capitalize() + '.' if len(word) == 1 else word.capitalize() if word not in stop_words else word.lower()
        for word in words
    ]
    normalized_text = ' '.join(normalized_words)
    return normalized_text


def truncate_text(text, word_limit):
    words = text.split()
    if len(words) > word_limit:
        truncated = " ".join(words[:word_limit])
        return truncated + " <a href='#' onclick='toggleAbstract(event)'>...</a>"
    return text


expandable_script = """
<script>
function toggleAbstract(event) {
    event.preventDefault();
    const link = event.target;
    const fullText = link.getAttribute('data-fulltext');
    if (link.innerText === '...') {
        link.parentElement.innerHTML = fullText + " <a href='#' onclick='toggleAbstract(event)' data-fulltext='" + link.parentElement.getAttribute('data-truncated') + "'>Show less</a>";
    } else {
        link.parentElement.innerHTML = link.parentElement.getAttribute('data-truncated') + " <a href='#' onclick='toggleAbstract(event)' data-fulltext='" + fullText + "'>...</a>";
    }
}
</script>
"""