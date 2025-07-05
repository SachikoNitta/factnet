"""
Complete Knowledge Graph Example: Neo4j + OpenAI + Visualization

This comprehensive example demonstrates:
- Neo4j persistent storage for production use
- OpenAI-powered automatic relationship detection
- Real-time visualization of the evolving knowledge graph
- Complete workflow from facts to visual insights

Prerequisites:
- Neo4j running on localhost:7687 (or update connection details)
- OpenAI API key (set as environment variable or hardcode)
- Visualization dependencies: pip install matplotlib networkx

Use this example to:
- See the complete FactNet workflow in action
- Test production-ready setup with all features
- Understand how AI detection affects graph structure
- Generate publication-ready knowledge graph visualizations
- Validate the entire pipeline with real data

Setup:
1. Start Neo4j: docker run -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
2. Set OPENAI_API_KEY environment variable
3. Install visualization: pip install matplotlib networkx
4. Run: python examples/example_complete.py

What this example does:
1. Connects to Neo4j database
2. Sets up OpenAI relationship detection
3. Adds facts about artificial intelligence
4. Waits for AI to detect relationships
5. Shows statistics and relationship details
6. Creates interactive visualization
7. Saves high-quality graph image
"""

import asyncio
import os
from factnet import KnowledgeGraph, Neo4jStorage, OpenAIRelationshipDetector, RelationshipType

async def main():
    print("🚀 Starting Complete FactNet Demo: Neo4j + OpenAI + Visualization")
    print("=" * 70)
    
    # Setup Neo4j storage
    print("📊 Connecting to Neo4j database...")
    storage = Neo4jStorage(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    )
    
    # Setup OpenAI detector
    print("🤖 Setting up OpenAI relationship detector...")
    ai_detector = OpenAIRelationshipDetector(
        api_key=os.getenv("OPENAI_API_KEY", "your_openai_key_here"),
        model="gpt-4o-mini"
    )
    
    # Create knowledge graph
    graph = KnowledgeGraph(storage, ai_detector)
    
    print("\\n📝 Adding facts about Artificial Intelligence...")
    print("-" * 50)
    
    # Add facts about AI - a topic with clear support/contradiction patterns
    facts = [
        "Artificial Intelligence can perform tasks that typically require human intelligence",
        "Machine learning algorithms improve automatically through experience",
        "AI systems can process and analyze large datasets faster than humans",
        "Artificial intelligence will replace all human jobs within 10 years",
        "Deep learning neural networks are inspired by the human brain structure",
        "AI systems are completely objective and free from bias",
        "Natural language processing enables computers to understand human language",
        "AI poses an existential threat to humanity",
        "Current AI systems lack true understanding and consciousness",
        "AI can help solve complex problems like climate change and disease"
    ]
    
    added_facts = []
    for i, fact_content in enumerate(facts, 1):
        fact = await graph.add_fact(fact_content)
        added_facts.append(fact)
        print(f"{i:2d}. Added: {fact_content[:60]}...")
    
    print(f"\\n✅ Added {len(added_facts)} facts to the knowledge graph")
    
    # Wait for AI processing to complete
    print("\\n🧠 AI is analyzing relationships between facts...")
    print("   This may take a moment depending on the number of facts...")
    await graph.wait_for_processing()
    print("✅ AI relationship detection completed!")
    
    # Add a few manual relationships for demonstration
    print("\\n➕ Adding some manual relationships for comparison...")
    await graph.add_manual_relationship(
        added_facts[0].id, added_facts[1].id, 
        RelationshipType.SUPPORTS, confidence=0.9
    )
    await graph.add_manual_relationship(
        added_facts[3].id, added_facts[0].id, 
        RelationshipType.CONTRADICTS, confidence=0.85
    )
    
    # Query and display results
    print("\\n📈 Knowledge Graph Analysis:")
    print("=" * 40)
    
    stats = await graph.get_network_stats()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    # Show relationship details
    print("\\n🔗 Detected Relationships:")
    print("-" * 40)
    relationships = await graph.get_relationships()
    
    for i, rel in enumerate(relationships, 1):
        source = await graph.get_fact(rel.source_id)
        target = await graph.get_fact(rel.target_id)
        print(f"{i:2d}. {rel.type.value.upper()} (confidence: {rel.confidence:.2f})")
        print(f"    Source: {source.content[:50]}...")
        print(f"    Target: {target.content[:50]}...")
        print()
    
    # Show supporting/contradicting relationships for first fact
    main_fact = added_facts[0]
    print(f"\\n🔍 Analysis for: '{main_fact.content}'")
    print("-" * 60)
    
    supporting = await graph.get_supporting_facts(main_fact.id)
    if supporting:
        print(f"\\n✅ Supporting facts ({len(supporting)}):")
        for fact in supporting:
            print(f"   • {fact.content}")
    
    contradicting = await graph.get_contradicting_facts(main_fact.id)
    if contradicting:
        print(f"\\n❌ Contradicting facts ({len(contradicting)}):")
        for fact in contradicting:
            print(f"   • {fact.content}")
    
    # Visualization
    print("\\n🎨 Creating Knowledge Graph Visualization...")
    print("-" * 50)
    
    try:
        from factnet import NetworkVisualizer
        
        # Create visualizer
        visualizer = NetworkVisualizer(graph)
        
        print("📊 Displaying interactive visualization...")
        print("   Close the plot window to continue to the next step...")
        
        # Show interactive visualization with full text
        await visualizer.visualize(
            figsize=(18, 14),
            show_labels=True,
            max_label_length=None  # Show full text
        )
        
        # Save high-quality visualization
        print("💾 Saving high-resolution visualization...")
        await visualizer.save_visualization(
            'ai_knowledge_graph.png',
            figsize=(20, 16),
            show_labels=True,
            max_label_length=None
        )
        
        print("✅ Visualization saved as 'ai_knowledge_graph.png'")
        
        # Save a compact version too
        await visualizer.save_visualization(
            'ai_knowledge_graph_compact.png',
            figsize=(14, 10),
            show_labels=True,
            max_label_length=50  # Shortened for compact view
        )
        
        print("✅ Compact visualization saved as 'ai_knowledge_graph_compact.png'")
        
    except ImportError:
        print("⚠️  Visualization not available.")
        print("   Install dependencies: pip install matplotlib networkx")
        print("   Then re-run this example for full visualization features.")
    
    # Final summary
    print("\\n🎉 Complete FactNet Demo Finished!")
    print("=" * 40)
    print("Summary of what happened:")
    print(f"• Connected to Neo4j database")
    print(f"• Added {len(added_facts)} facts about AI")
    print(f"• AI detected {len(relationships)} relationships")
    print(f"• Created interactive and saved visualizations")
    print(f"• Data persisted in Neo4j for future use")
    print("\\nYou can now:")
    print("• View the graph in Neo4j browser: http://localhost:7474")
    print("• Examine saved visualization images")
    print("• Add more facts and see relationships grow")
    
    # Close the graph
    await graph.close()
    print("\\n👋 Database connection closed. Demo complete!")

if __name__ == "__main__":
    asyncio.run(main())