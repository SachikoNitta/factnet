"""
Neo4j + OpenAI Integration Example

This example demonstrates:
- Using Neo4j as persistent graph database storage
- AI-powered automatic relationship detection with OpenAI
- Background processing of relationship detection
- Querying the knowledge graph after AI processing
- Combining AI-detected and manual relationships

Prerequisites:
- Neo4j running on localhost:7687 (or update connection details)
- OpenAI API key (set as environment variable or hardcode)

Use this example to:
- Test production-ready storage with Neo4j
- See AI relationship detection in action
- Understand async processing workflow
- Validate AI-detected relationships vs manual ones
- Test with real scientific/factual content

Setup:
1. Start Neo4j: docker run -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
2. Set OPENAI_API_KEY environment variable
3. Run: python examples/example_neo4j.py
"""

import asyncio
import os
from factnet import KnowledgeGraph, Neo4jStorage, OpenAIRelationshipDetector, RelationshipType

async def main():
    # Setup Neo4j storage
    # Make sure Neo4j is running on localhost:7687
    storage = Neo4jStorage(
        uri="bolt://localhost:7687",
        username="neo4j",
        password="password"
    )
    
    # Setup OpenAI detector
    # Set your OpenAI API key in environment or replace with your key
    ai_detector = OpenAIRelationshipDetector(
        api_key=os.getenv("OPENAI_API_KEY", "your_openai_key_here"),
        model="gpt-4o-mini"  # or "gpt-3.5-turbo" for lower cost
    )
    
    # Create knowledge graph
    graph = KnowledgeGraph(storage, ai_detector)
    
    print("Adding facts to knowledge graph...")
    
    # Add facts - AI will automatically detect relationships
    fact1 = await graph.add_fact("The Earth is approximately 4.5 billion years old")
    fact2 = await graph.add_fact("Radiometric dating of meteorites shows the solar system formed 4.5 billion years ago")
    fact3 = await graph.add_fact("The Earth is only 6,000 years old according to biblical chronology")
    fact4 = await graph.add_fact("Fossil evidence shows complex life forms existed millions of years ago")
    
    print(f"Added facts: {fact1.id}, {fact2.id}, {fact3.id}, {fact4.id}")
    
    # Wait for AI processing to complete
    print("Waiting for AI relationship detection to complete...")
    await graph.wait_for_processing()
    
    # Query the knowledge graph
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
    
    print("\nAll detected relationships:")
    relationships = await graph.get_relationships()
    for rel in relationships:
        source = await graph.get_fact(rel.source_id)
        target = await graph.get_fact(rel.target_id)
        print(f"  {source.content[:50]}... --{rel.type.value}--> {target.content[:50]}... (confidence: {rel.confidence:.2f})")
    
    # Manual relationship addition
    print("\nAdding manual relationship...")
    await graph.add_manual_relationship(
        fact4.id, fact3.id, RelationshipType.CONTRADICTS, confidence=0.95
    )
    
    # Close the graph
    await graph.close()
    print("Knowledge graph closed.")

if __name__ == "__main__":
    asyncio.run(main())