import networkx as nx
from pyvis.network import Network
import textwrap
import json
import utils
import pandas as pd

path = '../extraction/biblio_output/'
patents = utils.get_patents_citations(path)


# 1. Create a total graph and a DataFrame with all the patents
# ------------------------------------------------------------

# Load the additional data
path = '../extraction/biblio_output/'
patents = utils.get_patents_citations(path)
additional_data_dict = {
    patent['patent_number']: [
        patent.get('abstract', 'Unavailable information'),
        patent.get('year', 'Unavailable information'),
        patent.get('inventor_names', 'Unavailable information'),
        patent.get('applicant_names', 'Unavailable information'),
        patent.get('country', 'Unavailable information'),
        patent.get('invention_title', 'Unavailable information')
    ]
    for patent in patents
}

# Add the additional data to the patents
for patent in patents:
    patent_number = patent['patent_number']
    additional_data = additional_data_dict[patent_number]
    patent['abstract'] = additional_data[0]
    patent['year'] = additional_data[1]
    patent['inventor_names'] = additional_data[2]
    patent['applicant_names'] = additional_data[3]
    patent['country'] = additional_data[4]
    patent['invention_title'] = additional_data[5]

# Create the graph      
G = nx.DiGraph()
for patent in patents:
    patent_number = patent['patent_number']
    cites = patent['citations']
    G.add_node(
        patent_number,
        abstract=patent.get('abstract', 'Unavailable information'),
        year=patent.get('year', 'Unavailable information'),
        inventor_names=patent.get('inventor_names', 'Unavailable information'),
        applicant_names=patent.get('applicant_names', 'Unavailable information'),
        country=patent.get('country', 'Unavailable information'),
        invention_title=patent.get('invention_title', 'Unavailable information')
    )
    for cite in cites:
        G.add_edge(patent_number, cite)
nx.write_edgelist(G, "graphs/total_graph.edgelist")

node_data = []
for node, data in G.nodes(data=True):
    data['patent_number'] = node
    data['input_degree'] = G.in_degree(node)
    data['output_degree'] = G.out_degree(node)
    data['pagerank'] = nx.pagerank(G)[node]
    data['abstract'] = data.get('abstract', 'Unavailable information')
    data['year'] = data.get('year', 'Unavailable information')
    data['inventor_names'] = data.get('inventor_names', 'Unavailable information')
    data['applicant_names'] = data.get('applicant_names', 'Unavailable information')
    data['country'] = data.get('country', 'Unavailable information')
    node_data.append(data)
total_patents_df = pd.DataFrame(node_data)
total_patents_df = total_patents_df.sort_values(by='input_degree', ascending=False)
# total_patents_df = utils.convert_grafo_to_df(G)
# total_patents_df = total_patents_df.sort_values(by='input_degree', ascending=False)
total_patents_df.to_excel('graphs/total_patents_df.xlsx')
print(f'Total patents shape: {total_patents_df.shape}')




# 2. Create a filtered graph and a DataFrame with the patents with a input degree > 0
# -----------------------------------------------------------------------------------

degree_threshold = 0
filtered_nodes_degree = [node for node in G.nodes() if G.in_degree(node) > degree_threshold]
G_filtered_degree = G.subgraph(filtered_nodes_degree)
filtered_degree_df = utils.convert_grafo_to_df(G_filtered_degree)
filtered_degree_df = filtered_degree_df.sort_values(by='input_degree', ascending=False)
filtered_degree_df.to_excel('graphs/filtered_degree_df.xlsx')
nx.write_edgelist(G_filtered_degree, "graphs/filtered_degree_graph.edgelist")
print(f'Filtered degree patents shape: {filtered_degree_df.shape}')


# 3. Create a filtered graph and a DataFrame with the patents with a input degree > 0
# -----------------------------------------------------------------------------------

non_isolated_patents = [nodo for nodo in G_filtered_degree.nodes if G_filtered_degree.degree(nodo) > 0]
G_no_isolated = G_filtered_degree.subgraph(non_isolated_patents)
non_isolated_patents_df = utils.convert_grafo_to_df(G_no_isolated)
non_isolated_patents_df = non_isolated_patents_df.sort_values(by='input_degree', ascending=False)
non_isolated_patents_df.to_excel('graphs/non_isolated_patents_df.xlsx')
nx.write_edgelist(G_no_isolated, "graphs/non_isolated_graph.edgelist")
print(f'Non isolated patents shape: {non_isolated_patents_df.shape}')


# 4. Create an interactive plot
# -----------------------------

# Load the additional data
path = '../extraction/biblio_output/'
patents = utils.get_patents_citations(path)
abstract_dict = {patent['patent_number']: patent.get('abstract', 'Unavailable information') for patent in patents}

# Load the graph
G_to_plot = nx.read_edgelist("graphs/non_isolated_graph.edgelist", create_using=nx.DiGraph())

# Add the abstract to the nodes
for node in G_to_plot.nodes():
    if G_to_plot.nodes[node].get('abstract', 'Unavailable information') == 'Unavailable information':
        if node in abstract_dict:
            G_to_plot.nodes[node]['abstract'] = abstract_dict[node]

# Generate the interactive plot
net = Network(notebook=True, height="1000px", width="100%", directed=True)
for node, degree in G_to_plot.nodes(data=True):
    title = G_to_plot.nodes[node].get('invention_title', 'Unavailable information')
    abstract = G_to_plot.nodes[node].get('abstract', 'Unavailable information')
    wrapped_title = "\n".join(textwrap.wrap(title, width=80))
    truncated_abstract = utils.truncate_text(abstract, 100)
    info_node = (
        f"Title: {title}<br>"
        f"Cited by {G_to_plot.in_degree(node)} patents<br>"
        f"Citing {G_to_plot.out_degree(node)} patents<br>"
        f"Abstract: <span data-truncated='{truncated_abstract}' data-fulltext='{abstract}'>{truncated_abstract}</span>"
    )
    G_to_plot.nodes[node]['size'] = len(list(G_to_plot.neighbors(node))) * 3
    size = len(list(G_to_plot.neighbors(node))) * 3 if G_to_plot.out_degree(node) > 0 else 10
    net.add_node(node, label=node, title=info_node, size=size)
for source, target in G_to_plot.edges():
    net.add_edge(source, target)
net.repulsion(node_distance=200, central_gravity=0.3, spring_length=100, spring_strength=0.05)
net.show("interactive_plots/interactive_plot.html")
with open("interactive_plots/interactive_plot.html", "r") as f:
    html_content = f.read()
title_html = "<h1 style='text-align: center;'>Citation Network of Patents (Filtered: Non-Isolated)</h1>\n"
html_content = html_content.replace("<body>", f"<body>\n{title_html}\n{utils.expandable_script}")
with open("interactive_plots/interactive_plot.html", "w") as f:
    f.write(html_content)