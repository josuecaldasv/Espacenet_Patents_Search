from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from community import community_louvain
import networkx as nx
from pyvis.network import Network
import os
import pandas as pd
import numpy as np
import textwrap
import random
from sklearn.cluster import KMeans

import utils

# 1. Load embeddings
# ------------------
input_path = 'embeddings/embeddings.npy'
embeddings = np.load(input_path)

# 2. Load data
# ------------

input_path = '../extraction/biblio_output/'
output_path = 'lda/'
os.makedirs(output_path, exist_ok=True)

patents = utils.get_patents_citations(input_path)
abstract_dict = {patent['patent_number']: patent.get('abstract', 'Unavailable information') for patent in patents}
title_dict = {patent['patent_number']: patent.get('invention_title', 'Unavailable information') for patent in patents}


# 3. Compute cosine similarity matrix
# -----------------------------------
similarity_matrix = cosine_similarity(embeddings)


# 4. Create a graph
# -----------------
G_09 = nx.Graph()

# Add nodes with attributes from both abstract_dict and title_dict
for i, patent_id in enumerate(abstract_dict.keys()):
    abstract = abstract_dict[patent_id]
    title = title_dict.get(patent_id, 'Unavailable information')
    G_09.add_node(patent_id, abstract=abstract, title=title)

# Add edges based on similarity_matrix
for i in range(len(abstract_dict)):
    for j in range(i + 1, len(abstract_dict)):
        if similarity_matrix[i][j] > 0.9:
            patent_id = list(abstract_dict.keys())[i]
            other_patent_id = list(abstract_dict.keys())[j]
            G_09.add_edge(patent_id, other_patent_id, weight=float(similarity_matrix[i][j]))

print(f'Number of nodes: {G_09.number_of_nodes()}')
print(f'Number of edges: {G_09.number_of_edges()}')


# 5. Detect communities
# ----------------------

G_09_community = G_09.copy()
partition = community_louvain.best_partition(G_09_community)
community_colors = {community: f'#{random.randint(0, 0xFFFFFF):06x}' for community in set(partition.values())}
for node, community in partition.items():
    G_09_community.nodes[node]['group'] = community


# 6. Visualize the graph for semantic connections
# -----------------------------------------------

net = Network(notebook=True, height="1000px", width="100%", bgcolor="#ffffff", font_color="black")
for node in G_09_community.nodes():
    title = "Title: " + G_09_community.nodes[node].get('title', 'Unavailable information')
    abstract = abstract_dict.get(node, 'Unavailable')
    wrapped_title = "\n".join(textwrap.wrap(title, width=80))
    truncated_abstract = utils.truncate_text("Abstract: " + abstract, 70)
    wrapped_abstract = "\n".join(textwrap.wrap(truncated_abstract, width=80))
    G_09_community.nodes[node]['size'] = len(list(G_09_community.neighbors(node))) * 3
    info_node = (
        f"{wrapped_title}\n"
        f"Community: {partition[node]}\n"
        f"{wrapped_abstract}"
    )
    net.add_node(node, label=node, title=info_node, color=community_colors[partition[node]], size=G_09_community.nodes[node]['size'])
net.from_nx(G_09_community)
net.toggle_physics(True)
net.set_options('''
var options = {
    "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.005,
            "springLength": 150,
            "springConstant": 0.08
        },
        "minVelocity": 0.75
    }
}
''')
net.show("interactive_plots/semantic_connections_communities.html")
with open("interactive_plots/semantic_connections_communities.html", "r") as f:
    html_content = f.read()
title_html = "<h1 style='text-align: center;'>Semantic Connections of Patents (Filtered: Similarity > 0.9, Grouped by Louvain Communities)</h1>\n"
html_content = html_content.replace("<body>", f"<body>\n{title_html}")
with open("interactive_plots/semantic_connections_communities.html", "w") as f:
    f.write(html_content)


# 7. Cluster analysis
# -------------------

G_09_cluster = G_09.copy()
n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
labels = kmeans.fit_predict(embeddings)
cluster_colors = {cluster: f'#{random.randint(0, 0xFFFFFF):06x}' for cluster in set(labels)}
cluster_labels = {cluster: f'Cluster: {cluster}' for cluster in set(labels)}
for node, label in zip(abstract_dict.keys(), labels):
    G_09_cluster.nodes[node]['group'] = label

# 8. Visualize the graph for clusters
# -----------------------------------

net = Network(notebook=True, height="1000px", width="100%", bgcolor="#ffffff", font_color="black")
for node, label in zip(G_09_cluster.nodes(), labels):
    title = "Title: " + G_09_cluster.nodes[node].get('title', 'Unavailable information') 
    abstract = abstract_dict.get(node, 'Unavailable')
    wrapped_title = "\n".join(textwrap.wrap(title, width=80))
    truncated_abstract = utils.truncate_text("Abstract: " + abstract, 70)
    wrapped_abstract = "\n".join(textwrap.wrap(truncated_abstract, width=80))
    G_09_cluster.nodes[node]['size'] = len(list(G_09_cluster.neighbors(node))) * 3
    info_node = (
        f"{wrapped_title}\n"
        f"{cluster_labels[label]}\n"
        f"{wrapped_abstract}"
    )
    net.add_node(node, label=node, title=info_node, color=cluster_colors[label], size=G_09_cluster.nodes[node]['size'])
net.from_nx(G_09_cluster)
net.toggle_physics(True)
net.set_options('''
var options = {
    "physics": {
        "forceAtlas2Based": {
            "gravitationalConstant": -50,
            "centralGravity": 0.005,
            "springLength": 150,
            "springConstant": 0.08
        },
        "minVelocity": 0.75
    }
}
''')
net.show("interactive_plots/semantic_connections_cluster.html")
with open("interactive_plots/semantic_connections_cluster.html", "r") as f:
    html_content = f.read()
title_html = "<h1 style='text-align: center;'>Semantic Connections of Patents (Filtered: Similarity > 0.9, Grouped by Clusters)</h1>\n"
html_content = html_content.replace("<body>", f"<body>\n{title_html}")
with open("interactive_plots/semantic_connections_cluster.html", "w") as f:
    f.write(html_content)