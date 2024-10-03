import networkx as nx
from pyvis.network import Network
import textwrap

import utils

# Load the additional data
# -------------------------

path = '../extraction/biblio_output/'
patents = utils.get_patents_citations(path)
abstract_dict = {patent['patent_number']: patent.get('abstract', 'Unavailable information') for patent in patents}



# Load the graph
# --------------

G_no_isolated = nx.read_edgelist("graphs/filtered_degree_graph.edgelist", create_using=nx.DiGraph())


# Add the abstract to the nodes
# ------------------------------

for node in G_no_isolated.nodes():
    if G_no_isolated.nodes[node].get('abstract', 'Unavailable information') == 'Unavailable information':
        if node in abstract_dict:
            G_no_isolated.nodes[node]['abstract'] = abstract_dict[node]

# Create an interactive plot
# --------------------------

net = Network(notebook=True, height="1000px", width="100%", directed=True)
for node, degree in G_no_isolated.nodes(data=True):
    abstract = G_no_isolated.nodes[node].get('abstract', 'Unavailable information')
    wrapped_abstract = "\n".join(textwrap.wrap(abstract, width=80))
    info_node = (
        f"Input Degree: {G_no_isolated.in_degree(node)}\n"
        f"Output Degree: {G_no_isolated.out_degree(node)}\n"
        f"Abstract: {wrapped_abstract}"
)
    G_no_isolated.nodes[node]['size'] = len(list(G_no_isolated.neighbors(node))) * 3
    net.add_node(node, label=node, title=info_node, size=G_no_isolated.nodes[node]['size'])
for source, target in G_no_isolated.edges():
    net.add_edge(source, target)
net.repulsion(node_distance=200, central_gravity=0.3, spring_length=100, spring_strength=0.05)
net.show("interactive_plot.html")

with open("interactive_plot.html", "r") as f:
    html_content = f.read()

title_html = "<h1 style='text-align: center;'>Citation Network of Patents (Filtered: Non-Isolated)</h1>\n"
html_content = html_content.replace("<body>", f"<body>\n{title_html}")

with open("interactive_plot.html", "w") as f:
    f.write(html_content)