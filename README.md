# FactNet

A Python library for building AI-powered knowledge graphs with automatic relationship detection using graph databases.

## Features

- **Graph Database Integration**: Neo4j backend for scalable fact storage
- **AI-Powered Relationship Detection**: Automatic detection using OpenAI or custom AI models
- **Async Processing**: Background relationship detection without blocking fact addition
- **Flexible Storage**: Neo4j or in-memory storage backends
- **Rich Querying**: Find supporting/contradicting facts with confidence scores

## Installation

```bash
pip install -r requirements.txt
```

For Neo4j integration, install Neo4j Desktop or run via Docker:
```bash
docker run -p7474:7474 -p7687:7687 -e NEO4J_AUTH=neo4j/your_password neo4j:latest
```

## Quick Start

### With Neo4j and OpenAI

```python
import asyncio
from factnet import KnowledgeGraph, Neo4jStorage, OpenAIRelationshipDetector

async def main():
    # Setup Neo4j storage
    storage = Neo4jStorage(
        uri="bolt://localhost:7687",
        username="neo4j", 
        password="password"
    )
    
    # Setup AI detector
    ai_detector = OpenAIRelationshipDetector(
        api_key="your_openai_key",
        model="gpt-4o-mini"
    )
    
    # Create knowledge graph
    graph = KnowledgeGraph(storage, ai_detector)
    
    # Add facts - AI automatically detects relationships
    fact1 = await graph.add_fact("Regular exercise improves cardiovascular health")
    fact2 = await graph.add_fact("Running 30 minutes daily reduces heart disease risk by 50%")
    fact3 = await graph.add_fact("Exercise has no impact on heart health")
    
    # Wait for AI processing
    await graph.wait_for_processing()
    
    # Query relationships
    supporting = await graph.get_supporting_facts(fact1.id)
    contradicting = await graph.get_contradicting_facts(fact1.id)
    
    await graph.close()

asyncio.run(main())
```

### With In-Memory Storage (for testing)

```python
import asyncio
from factnet import KnowledgeGraph, InMemoryStorage, OpenAIRelationshipDetector

async def main():
    storage = InMemoryStorage()
    ai_detector = OpenAIRelationshipDetector(
        api_key="your_openai_key",
        model="gpt-4o-mini"
    )
    graph = KnowledgeGraph(storage, ai_detector)
    
    # Add facts and let AI detect relationships
    await graph.add_fact("The Earth is round")
    await graph.add_fact("Satellite imagery confirms Earth's spherical shape")
    await graph.add_fact("The Earth is flat")
    
    await graph.wait_for_processing()
    await graph.close()

asyncio.run(main())
```

## Core Components

### KnowledgeGraph
- `add_fact(content, fact_id=None, metadata=None)` - Add fact with AI relationship detection
- `get_supporting_facts(fact_id)` - Get facts that support a given fact
- `get_contradicting_facts(fact_id)` - Get facts that contradict a given fact
- `add_manual_relationship(source_id, target_id, type, confidence)` - Add explicit relationship
- `wait_for_processing()` - Wait for AI relationship detection to complete

### Storage Backends
- `Neo4jStorage(uri, username, password)` - Neo4j graph database storage
- `InMemoryStorage()` - In-memory storage for testing

### AI Detectors
- `OpenAIRelationshipDetector(api_key, model)` - Uses OpenAI for relationship detection
- `CustomAIDetector(detect_function)` - Wrap your own AI detection function

### Visualization
- `NetworkVisualizer(knowledge_graph)` - Create visual representations of the graph
- `await visualizer.visualize()` - Show interactive plot with matplotlib
- `await visualizer.save_visualization(filename)` - Save graph to image file

## Advanced Usage

### Custom AI Detector

```python
from factnet import CustomAIDetector, RelationshipType

async def my_ai_detector(new_fact, existing_facts):
    # Your AI logic here
    # Return [(target_fact_id, RelationshipType.SUPPORTS, confidence), ...]
    return [(existing_facts[0].id, RelationshipType.SUPPORTS, 0.8)]

detector = CustomAIDetector(my_ai_detector)
graph = KnowledgeGraph(storage, detector)
```

### Relationship Types and Confidence

```python
# Relationships are automatically detected with confidence scores
relationships = await graph.get_relationships()
for rel in relationships:
    print(f"{rel.type.value}: {rel.confidence:.2f}")
```

### Graph Visualization

```python
from factnet import NetworkVisualizer

# Create visualizer
visualizer = NetworkVisualizer(graph)

# Show interactive plot
await visualizer.visualize(figsize=(12, 8), max_label_length=30)

# Save to file
await visualizer.save_visualization('my_graph.png')
```

**Visualization Features:**
- **Green arrows**: Supporting relationships
- **Red dashed arrows**: Contradicting relationships  
- **Gray dotted arrows**: Neutral relationships
- **Interactive plots**: Zoom, pan, inspect nodes
- **Export formats**: PNG, PDF, SVG, etc.

## Common Use Cases

1. **News Fact Checking**: Store claims and automatically detect contradictions
2. **Research Knowledge Base**: Build interconnected research findings
3. **Legal Document Analysis**: Track supporting/contradicting evidence
4. **Scientific Literature**: Connect related studies and findings

## Examples

The `examples/` directory contains four demonstration scripts:

### 1. Basic Manual Relationships (`examples/example.py`)
```bash
python examples/example.py
```
- **Purpose**: Learn the core API without external dependencies
- **Features**: In-memory storage, manual relationship creation
- **Use for**: Testing basic functionality, understanding the API

### 2. Neo4j + OpenAI Integration (`examples/example_neo4j.py`)
```bash
python examples/example_neo4j.py
```
- **Purpose**: Production-ready setup with persistent storage and AI
- **Features**: Neo4j database, OpenAI relationship detection, async processing
- **Prerequisites**: Neo4j running, OpenAI API key
- **Use for**: Production testing, validating AI detection, persistent storage

### 3. Simple OpenAI Testing (`examples/example_simple.py`)
```bash
python examples/example_simple.py
```
- **Purpose**: Quick AI testing without database setup
- **Features**: In-memory storage, OpenAI relationship detection
- **Prerequisites**: OpenAI API key only
- **Use for**: Rapid prototyping, AI prompt validation, debugging

### 4. Graph Visualization (`examples/example_visualization.py`)
```bash
python examples/example_visualization.py
```
- **Purpose**: Visualize knowledge graph structure
- **Features**: Interactive plots, color-coded relationships, save to files
- **Prerequisites**: `pip install matplotlib networkx`
- **Use for**: Debugging relationships, creating diagrams, network analysis

## Architecture

The library uses an async architecture where:
1. Facts are immediately stored in the graph database
2. AI relationship detection runs in the background
3. Relationships are updated as they're discovered
4. Queries return current state with confidence scores

## File Structure

```
factnet/
├── factnet/
│   ├── __init__.py          # Main exports
│   ├── knowledge_graph.py   # Main KnowledgeGraph class
│   ├── backends.py          # Storage backends (Neo4j, InMemory)
│   ├── ai_detectors.py      # AI relationship detectors
│   ├── relationship_types.py # Relationship type enum
│   └── visualization.py     # Optional visualization
├── examples/
│   ├── example.py          # Basic manual relationships
│   ├── example_neo4j.py    # Neo4j + OpenAI integration
│   ├── example_simple.py   # In-memory + OpenAI testing
│   └── example_visualization.py # Graph visualization demo
└── README.md              # This file
```