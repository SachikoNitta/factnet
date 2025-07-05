"""
Simple In-Memory + OpenAI Example

This example demonstrates:
- Using in-memory storage (no Neo4j required)
- AI-powered relationship detection with OpenAI
- Quick testing and prototyping setup
- Health/medical domain fact relationships

Prerequisites:
- OpenAI API key (set as environment variable or hardcode)

Use this example to:
- Test AI relationship detection without Neo4j setup
- Quick prototyping and experimentation
- Validate OpenAI prompt effectiveness
- Test different fact domains (health, science, etc.)
- Debug AI relationship detection logic

Setup:
1. Set OPENAI_API_KEY environment variable (or hardcode in line 11)
2. Run: python examples/example_simple.py

Note: Data is not persisted - use example_neo4j.py for persistent storage
"""

import asyncio
import os
from factnet import KnowledgeGraph, InMemoryStorage, OpenAIRelationshipDetector, RelationshipType

async def main():
    # Setup in-memory storage (for testing without Neo4j)
    storage = InMemoryStorage()
    
    # Setup OpenAI detector
    ai_detector = OpenAIRelationshipDetector(
        api_key=os.getenv("OPENAI_API_KEY", "your_openai_key_here"),
        model="gpt-4o-mini"
    )
    
    # Create knowledge graph
    graph = KnowledgeGraph(storage, ai_detector)
    
    print("Adding facts to knowledge graph...")
    
    # Add facts - AI will automatically detect relationships
    fact1 = await graph.add_fact("Regular exercise improves cardiovascular health")
    fact2 = await graph.add_fact("Running 30 minutes daily reduces heart disease risk by 50%")
    fact3 = await graph.add_fact("Exercise has no impact on heart health")
    fact4 = await graph.add_fact("Sedentary lifestyle increases risk of heart disease")
    
    print("Waiting for AI relationship detection...")
    await graph.wait_for_processing()
    
    # Query results
    print("\nKnowledge Graph Statistics:")
    stats = await graph.get_network_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print(f"\nFacts supporting '{fact1.content}':")
    supporting = await graph.get_supporting_facts(fact1.id)
    for fact in supporting:
        print(f"  - {fact.content}")
    
    print(f"\nFacts contradicting '{fact1.content}':")
    contradicting = await graph.get_contradicting_facts(fact1.id)
    for fact in contradicting:
        print(f"  - {fact.content}")
    
    await graph.close()

if __name__ == "__main__":
    asyncio.run(main())