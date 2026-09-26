import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("data/transport_data.csv")

# Create graph
G = nx.DiGraph()

for _, row in df.iterrows():
    source = row["source"]
    destination = row["destination"]
    passengers = row["passengers"]

    if G.has_edge(source, destination):
        G[source][destination]["weight"] += passengers
    else:
        G.add_edge(source, destination, weight=passengers)

# Create network layout
pos = nx.spring_layout(G, seed=42)

# Draw nodes
nx.draw_networkx_nodes(
    G,
    pos,
    node_size=2500
)

# Draw edges
nx.draw_networkx_edges(
    G,
    pos,
    arrows=True,
    arrowsize=20,
    width=2
)

# Station names
nx.draw_networkx_labels(
    G,
    pos,
    font_size=10,
    font_weight="bold"
)

# Passenger flow labels
edge_labels = nx.get_edge_attributes(G, "weight")

nx.draw_networkx_edge_labels(
    G,
    pos,
    edge_labels=edge_labels,
    font_size=9
)

plt.title("Public Transport Passenger Flow Network")
plt.axis("off")

# Save image
plt.savefig("analysis/transport_network.png", dpi=300, bbox_inches="tight")

plt.show()