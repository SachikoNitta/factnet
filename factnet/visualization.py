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
                       max_label_length: int = None) -> None:
        G = nx.DiGraph()
        
        # Get all facts and relationships
        facts = await self.knowledge_graph.get_all_facts()
        relationships = await self.knowledge_graph.get_relationships()
        
        # Add nodes (facts)
        for fact in facts:
            if max_label_length is not None and len(fact.content) > max_label_length:
                label = fact.content[:max_label_length] + "..."
            else:
                label = fact.content
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
        
        # Create layout with more spacing for text
        if max_label_length is None:
            k = 3  # More spacing for full text
            node_size = 3000  # Larger nodes for full text
        else:
            k = 1
            node_size = 1500
            
        pos = nx.spring_layout(G, k=k, iterations=50)
        
        # Draw the graph
        plt.figure(figsize=figsize)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                              node_size=node_size, alpha=0.7)
        
        # Draw edges with different colors for different relationship types
        for i, edge in enumerate(G.edges()):
            nx.draw_networkx_edges(G, pos, [edge], edge_color=edge_colors[i], 
                                  style=edge_styles[i], width=2, alpha=0.7,
                                  arrowsize=20, arrowstyle='->')
        
        # Draw labels with text wrapping
        if show_labels:
            labels = nx.get_node_attributes(G, 'label')
            
            # Adjust font size based on label length
            if max_label_length is None:
                font_size = 6  # Smaller font for full text
            else:
                font_size = 8
            
            # Draw labels with better positioning for long text
            for node, label in labels.items():
                x, y = pos[node]
                
                # Wrap long text for better readability
                if len(label) > 50:
                    import textwrap
                    wrapped_label = '\\n'.join(textwrap.wrap(label, width=40))
                else:
                    wrapped_label = label
                
                plt.text(x, y, wrapped_label, fontsize=font_size, fontweight='bold',
                        ha='center', va='center', 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
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