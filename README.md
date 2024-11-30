# Espacenet_Patents_Search

This repository provides access to patent information from Espacenet and enables text analysis of the extracted data.

## Instructions to Run the Repository

1. Install the required packages listed in `requirements.txt`.

2. Define a `.env` file with the following format to set your `CLIENT_KEY` and `CLIENT_SECRET` from Espacenet:

    ```plaintext
    CLIENT_KEY=YOUR_CLIENT_KEY
    CLIENT_SECRET=YOUR_CLIENT_SECRET
    ```

## Data Extraction
------------------------

1. Navigate to the `extraction` folder.

2. Run the `search_patents.py` script to extract patent information.

3. Monitor the amount of data extracted by your API key by executing `usage.py`.

4. Convert the extracted files and standardize the format to text files by running `conversion.py`.

## Data Analysis
-------------------------

1. Execute `citation_analysis.py` to perform a citation network analysis on the extracted patents.

2. Run `descriptive_analysis.py` for descriptive analysis and generate ranking graphs.

3. Execute `lda_analysis.py` to conduct Latent Dirichlet Allocation (LDA) analysis.

4. Run `semantic_analysis.py` for a semantic analysis of the patents.
