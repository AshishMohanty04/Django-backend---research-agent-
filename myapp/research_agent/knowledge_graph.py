# myapp/research_agent/knowledge_graph.py
import networkx as nx
# Simple in-memory knowledge graph stored in this module
_kg = nx.DiGraph()

def init_knowledge_graph():
    global _kg
    _kg = nx.DiGraph()

def extract_knowledge_triplets(text):
    # Placeholder - returns no triplets by default
    return []

def build_knowledge_graph(triplets):
    global _kg
    for head, relation, tail in triplets:
        _kg.add_node(head, type="entity"}
        _kg.add_node(tail, type="entity")
        _kg.add_edge(head, tail, relation=relation)

def get_graph_summary():
    return {"nodes": list(_kg.nodes)[:50], "edges": len(_kg.edges)}
