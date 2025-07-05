"""
Basic Knowledge Graph Example with Manual Relationships

This example demonstrates:
- Creating a knowledge graph with in-memory storage
- Adding facts manually
- Creating explicit relationships between facts
- Querying supporting and contradicting facts
- Getting network statistics

Use this example to:
- Test basic library functionality
- Understand the core API
- Prototype without external dependencies (no Neo4j or OpenAI required)
- Learn how to manually define fact relationships
"""

import asyncio
from factnet import KnowledgeGraph, InMemoryStorage, RelationshipType

async def main():
    # Create knowledge graph with in-memory storage
    storage = InMemoryStorage()
    graph = KnowledgeGraph(storage)
    
    # Add facts
    fact1 = await graph.add_fact("The Earth is round")
    fact2 = await graph.add_fact("Satellites orbit around the Earth, confirming its spherical shape")
    fact3 = await graph.add_fact("The Earth is flat and not spherical")
    
    # Add manual relationships
    await graph.add_manual_relationship(fact1.id, fact3.id, RelationshipType.CONTRADICTS, confidence=0.9)
    await graph.add_manual_relationship(fact2.id, fact1.id, RelationshipType.SUPPORTS, confidence=0.8)
    
    # Query the network
    stats = await graph.get_network_stats()
    print("Network Stats:", stats)
    
    print(f"\nFacts supporting '{fact1.content}':")
    supporting_facts = await graph.get_supporting_facts(fact1.id)
    for fact in supporting_facts:
        print(f"- {fact.content}")
    
    print(f"\nFacts contradicting '{fact1.content}':")
    contradicting_facts = await graph.get_contradicting_facts(fact1.id)
    for fact in contradicting_facts:
        print(f"- {fact.content}")
    
    print("\nAll relationships:")
    relationships = await graph.get_relationships()
    for rel in relationships:
        source = await graph.get_fact(rel.source_id)
        target = await graph.get_fact(rel.target_id)
        print(f"{source.content} --{rel.type.value}--> {target.content} (confidence: {rel.confidence})")
    
    await graph.close()

if __name__ == "__main__":
    asyncio.run(main())