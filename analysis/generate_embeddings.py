from sentence_transformers import SentenceTransformer
import os
import numpy as np

import utils

# 1. Load data
# ------------
input_path = '../extraction/biblio_output/'
output_path = 'lda/'
os.makedirs(output_path, exist_ok=True)
patents = utils.get_patents_citations(input_path)
abstract_dict = {patent['patent_number']: patent.get('abstract', 'Unavailable information') for patent in patents}
n_patents = len(abstract_dict)


# 2. Generate embeddings
# ----------------------
model = SentenceTransformer('intfloat/multilingual-e5-large')
abstracts = list(abstract_dict.values())
embeddings = model.encode(abstracts)
embeddings_path = 'embeddings/embeddings.npy'
np.save(embeddings_path, embeddings)