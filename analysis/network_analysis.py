import pandas as pd
import networkx as nx

# Load data
df = pd.read_csv("data/transport_data.csv")

# Create directed graph
G = nx.DiGraph()

# Add edges with passenger flow as weight
for _, row in df.iterrows():
    source = row["source"]
    destination = row["destination"]
    passengers = row["passengers"]

    if G.has_edge(source, destination):
        G[source][destination]["weight"] += passengers
    else:
        G.add_edge(source, destination, weight=passengers)

print("===== TRANSPORT NETWORK =====")

print("\nStations:")
print(list(G.nodes()))

print("\nConnections:")
for source, destination, data in G.edges(data=True):
    print(source, "->", destination, "| Passengers:", data["weight"])

# Degree centrality
print("\n===== DEGREE CENTRALITY =====")
degree = nx.degree_centrality(G)

for station, value in degree.items():
    print(station, ":", round(value, 3))

# Betweenness centrality
print("\n===== BETWEENNESS CENTRALITY =====")
betweenness = nx.betweenness_centrality(G, weight="weight")

for station, value in betweenness.items():
    print(station, ":", round(value, 3))

# PageRank
print("\n===== PAGERANK =====")
pagerank = nx.pagerank(G, weight="weight")

for station, value in pagerank.items():
    print(station, ":", round(value, 3))