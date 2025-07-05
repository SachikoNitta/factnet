"""
Knowledge Graph Visualization Example

This example demonstrates:
- Creating a knowledge graph with facts and relationships
- Using the NetworkVisualizer to create visual representations
- Saving visualizations to files
- Different visualization styles and options

Prerequisites:
- matplotlib and networkx: pip install matplotlib networkx

Use this example to:
- Visualize your knowledge graph structure
- Debug relationship patterns
- Create presentation-ready network diagrams
- Export graphs for reports or analysis

Setup:
1. Install visualization dependencies: pip install matplotlib networkx
2. Run: python examples/example_visualization.py
"""

import asyncio
from factnet import KnowledgeGraph, InMemoryStorage, RelationshipType

async def main():
    # Create knowledge graph with sample data
    storage = InMemoryStorage()
    graph = KnowledgeGraph(storage)
    
    print("Creating sample knowledge graph...")
    
    # Add facts about climate change
    fact1 = await graph.add_fact("Human activities are the primary cause of climate change")
    fact2 = await graph.add_fact("CO2 emissions from fossil fuels drive global warming")
    fact3 = await graph.add_fact("Deforestation reduces carbon absorption capacity")
    fact4 = await graph.add_fact("Climate change is a natural phenomenon")
    fact5 = await graph.add_fact("IPCC reports show 95% confidence in human causation")
    fact6 = await graph.add_fact("Renewable energy can reduce carbon emissions")
    
    # Add relationships
    await graph.add_manual_relationship(fact2.id, fact1.id, RelationshipType.SUPPORTS, confidence=0.9)
    await graph.add_manual_relationship(fact3.id, fact1.id, RelationshipType.SUPPORTS, confidence=0.7)
    await graph.add_manual_relationship(fact5.id, fact1.id, RelationshipType.SUPPORTS, confidence=0.95)
    await graph.add_manual_relationship(fact4.id, fact1.id, RelationshipType.CONTRADICTS, confidence=0.8)
    await graph.add_manual_relationship(fact6.id, fact2.id, RelationshipType.SUPPORTS, confidence=0.6)
    
    print("Knowledge graph created with facts and relationships.")
    
    try:
        from factnet import NetworkVisualizer
        
        # Create visualizer
        visualizer = NetworkVisualizer(graph)
        
        print("\\nDisplaying interactive visualization...")
        print("Close the plot window to continue...")
        
        # Show interactive visualization
        await visualizer.visualize(
            figsize=(14, 10),
            show_labels=True,
            max_label_length=40
        )
        
        # Save visualization to file
        print("Saving visualization to 'knowledge_graph.png'...")
        await visualizer.save_visualization(
            'knowledge_graph.png',
            figsize=(16, 12),
            show_labels=True,
            max_label_length=35
        )
        
        print("Visualization saved successfully!")
        
        # Show network statistics
        stats = await graph.get_network_stats()
        print("\\nNetwork Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
    except ImportError:
        print("\\nVisualization not available.")
        print("Install dependencies: pip install matplotlib networkx")
        print("Then re-run this example.")
    
    await graph.close()

if __name__ == "__main__":
    asyncio.run(main())