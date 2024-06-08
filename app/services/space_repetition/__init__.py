# '''Steps to Create Graph Embeddings
# Define the Graph Structure:

# Nodes: Each node represents a LeetCode problem.
# Edges: Define edges based on certain relationships such as similar questions, same tags, or problems at similar problem_difficulty levels.
# Construct the Graph:

# Use a graph library like NetworkX to create the graph.
# Add nodes for each problem.
# Add edges based on defined relationships.
# Generate Graph Embeddings:

# Use graph embedding techniques like Node2Vec, GraphSAGE, or GCN (Graph Convolutional Networks) to generate embeddings for each node.
# Example Workflow'''

# import networkx as nx

# G = nx.Graph()

# # Example: Add nodes
# problems = [
#     {"id": 1, "level": "easy", "tags": ["array"], "similar_questions_id": [2, 3]},
#     {"id": 2, "level": "medium", "tags": ["dp"], "similar_questions_id": [1]},
#     {"id": 3, "level": "hard", "tags": ["array"], "similar_questions_id": [1]},
# ]

# for problem in problems:
#     G.add_node(problem["id"], level=problem["level"], tags=problem["tags"])

# # Example: Add edges
# for problem in problems:
#     for similar_id in problem["similar_questions_id"]:
#         G.add_edge(problem["id"], similar_id)


# from node2vec import Node2Vec

# # Precompute probabilities and generate walks
# node2vec = Node2Vec(G, dimensions=64, walk_length=30, num_walks=200, workers=4)

# # Embed nodes
# model = node2vec.fit(window=10, min_count=1, batch_words=4)

# # Get embeddings for nodes
# embeddings = {str(node): model.wv[str(node)] for node in G.nodes()}


# from torch_geometric.datasets import Planetoid
# import torch_geometric.transforms as T
# from torch_geometric.nn import SAGEConv
# import torch

# # Assuming you have the graph data in edge_index and x (features)
# edge_index = torch.tensor([
#     [0, 1],
#     [1, 0],
#     [1, 2],
#     [2, 1],
#     [0, 2],
#     [2, 0],
# ], dtype=torch.long).t().contiguous()

# x = torch.eye(3, dtype=torch.float)  # Example features

# class GraphSAGE(torch.nn.Module):
#     def __init__(self, in_channels, out_channels):
#         super(GraphSAGE, self).__init__()
#         self.conv1 = SAGEConv(in_channels, out_channels)
#         self.conv2 = SAGEConv(out_channels, out_channels)

#     def forward(self, x, edge_index):
#         x = self.conv1(x, edge_index)
#         x = torch.relu(x)
#         x = self.conv2(x, edge_index)
#         return x

# model = GraphSAGE(x.size(1), 64)
# optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
# criterion = torch.nn.MSELoss()

# def train():
#     model.train()
#     optimizer.zero_grad()
#     out = model(x, edge_index)
#     loss = criterion(out, x)  # Example loss
#     loss.backward()
#     optimizer.step()
#     return loss

# for epoch in range(100):
#     loss = train()
#     print(f'Epoch {epoch}, Loss: {loss.item()}')

# # Get the embeddings
# model.eval()
# embeddings = model(x, edge_index).detach().numpy()

# Integrating Graph Embeddings with Your Dataset
# Construct the Graph:

# Populate the graph with all LeetCode problems as nodes.
# Define edges based on similarity or other relationships.
# Generate Embeddings:

# Use a method like Node2Vec or GraphSAGE to generate embeddings for each problem.
# Utilize Embeddings:

# Use these embeddings for tasks like clustering, similarity search, or input to machine learning models.