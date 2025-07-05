from typing import Optional
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

from .knowledge_graph import KnowledgeGraph
from .relationship_types import RelationshipType
import asyncio

class NetworkVisualizer:
    def __init__(self, knowledge_graph: KnowledgeGraph):
        if not HAS_VISUALIZATION:
            raise ImportError("Visualization requires matplotlib and networkx. Install with: pip install matplotlib networkx")
        
        self.knowledge_graph = knowledge_graph
    
    async def visualize(self, figsize: tuple = (12, 8), show_labels: bool = True, 
                       max_label_length: int = 30) -> None:
        G = nx.DiGraph()
        
        # Get all facts and relationships
        facts = await self.knowledge_graph.get_all_facts()
        relationships = await self.knowledge_graph.get_relationships()
        
        # Add nodes (facts)
        for fact in facts:
            label = fact.content[:max_label_length] + "..." if len(fact.content) > max_label_length else fact.content
            G.add_node(fact.id, label=label)
        
        # Add edges (relationships)
        edge_colors = []
        edge_styles = []
        
        for rel in relationships:
            G.add_edge(rel.source_id, rel.target_id, 
                      type=rel.type.value, confidence=rel.confidence)
            
            if rel.type == RelationshipType.SUPPORTS:
                edge_colors.append('green')
                edge_styles.append('-')
            elif rel.type == RelationshipType.CONTRADICTS:
                edge_colors.append('red')
                edge_styles.append('--')
            else:
                edge_colors.append('gray')
                edge_styles.append(':')
        
        # Create layout
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Draw the graph
        plt.figure(figsize=figsize)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=1500, alpha=0.7)
        
        # Draw edges with different colors for different relationship types
        for i, edge in enumerate(G.edges()):
            nx.draw_networkx_edges(G, pos, [edge], edge_color=edge_colors[i], 
                                  style=edge_styles[i], width=2, alpha=0.7,
                                  arrowsize=20, arrowstyle='->')
        
        # Draw labels
        if show_labels:
            labels = nx.get_node_attributes(G, 'label')
            nx.draw_networkx_labels(G, pos, labels, font_size=8, font_weight='bold')
        
        # Add legend
        legend_elements = [
            plt.Line2D([0], [0], color='green', lw=2, label='Supports'),
            plt.Line2D([0], [0], color='red', lw=2, linestyle='--', label='Contradicts'),
            plt.Line2D([0], [0], color='gray', lw=2, linestyle=':', label='Neutral')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.title("Knowledge Network Visualization")
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    async def save_visualization(self, filename: str, **kwargs) -> None:
        await self.visualize(show_labels=kwargs.get('show_labels', True),
                            figsize=kwargs.get('figsize', (12, 8)))
        plt.savefig(filename, bbox_inches='tight', dpi=300)
        plt.close()