from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
import asyncio
import json
from .knowledge_network import Fact
from .relationship_types import RelationshipType

class AIRelationshipDetector(ABC):
    @abstractmethod
    async def detect_relationships(self, new_fact: Fact, existing_facts: List[Fact]) -> List[Tuple[str, RelationshipType, float]]:
        """
        Detect relationships between a new fact and existing facts.
        
        Args:
            new_fact: The newly added fact
            existing_facts: All existing facts in the knowledge base
            
        Returns:
            List of tuples: (target_fact_id, relationship_type, confidence_score)
        """
        pass

class OpenAIRelationshipDetector(AIRelationshipDetector):
    def __init__(self, api_key: str, model: str = "gpt-4", max_facts_per_request: int = 20):
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model
            self.max_facts_per_request = max_facts_per_request
        except ImportError:
            raise ImportError("OpenAI package required. Install with: pip install openai")
    
    async def detect_relationships(self, new_fact: Fact, existing_facts: List[Fact]) -> List[Tuple[str, RelationshipType, float]]:
        if not existing_facts:
            return []
        
        # Process facts in batches to avoid token limits
        relationships = []
        for i in range(0, len(existing_facts), self.max_facts_per_request):
            batch = existing_facts[i:i + self.max_facts_per_request]
            batch_relationships = await self._process_batch(new_fact, batch)
            relationships.extend(batch_relationships)
        
        return relationships
    
    async def _process_batch(self, new_fact: Fact, existing_facts: List[Fact]) -> List[Tuple[str, RelationshipType, float]]:
        prompt = self._create_prompt(new_fact, existing_facts)
        
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    max_tokens=1000
                )
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content, existing_facts)
        
        except Exception as e:
            print(f"Error in AI relationship detection: {e}")
            return []
    
    def _create_prompt(self, new_fact: Fact, existing_facts: List[Fact]) -> str:
        existing_facts_text = "\n".join([f"{i+1}. ID: {fact.id}, Content: {fact.content}" 
                                       for i, fact in enumerate(existing_facts)])
        
        prompt = f"""
Analyze the relationships between this NEW FACT and the EXISTING FACTS below.

NEW FACT: {new_fact.content}

EXISTING FACTS:
{existing_facts_text}

For each existing fact, determine if the new fact:
- SUPPORTS it (provides evidence for, confirms, reinforces)
- CONTRADICTS it (opposes, disproves, conflicts with)
- NEUTRAL (no clear relationship)

Respond with a JSON array of relationships. Each relationship should have:
- "fact_id": the ID of the existing fact
- "relationship": "supports", "contradicts", or "neutral"
- "confidence": a float between 0.0 and 1.0
- "reasoning": brief explanation

Only include relationships with confidence > 0.3. If no significant relationships exist, return an empty array.

Example format:
[
  {{
    "fact_id": "fact_123",
    "relationship": "supports",
    "confidence": 0.85,
    "reasoning": "Both facts discuss the same phenomenon with consistent evidence"
  }}
]
"""
        return prompt
    
    def _parse_response(self, response: str, existing_facts: List[Fact]) -> List[Tuple[str, RelationshipType, float]]:
        try:
            # Extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:-3]
            elif response.startswith("```"):
                response = response[3:-3]
            
            relationships_data = json.loads(response)
            relationships = []
            
            existing_fact_ids = {fact.id for fact in existing_facts}
            
            for rel_data in relationships_data:
                fact_id = rel_data.get("fact_id")
                relationship_str = rel_data.get("relationship", "").lower()
                confidence = float(rel_data.get("confidence", 0.0))
                
                if fact_id not in existing_fact_ids:
                    continue
                
                if relationship_str == "supports":
                    rel_type = RelationshipType.SUPPORTS
                elif relationship_str == "contradicts":
                    rel_type = RelationshipType.CONTRADICTS
                elif relationship_str == "neutral":
                    rel_type = RelationshipType.NEUTRAL
                else:
                    continue
                
                if confidence > 0.3:
                    relationships.append((fact_id, rel_type, confidence))
            
            return relationships
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error parsing AI response: {e}")
            return []

class CustomAIDetector(AIRelationshipDetector):
    def __init__(self, detect_function):
        """
        Custom AI detector that wraps a user-provided async function.
        
        Args:
            detect_function: async function that takes (new_fact, existing_facts) 
                           and returns List[Tuple[str, RelationshipType, float]]
        """
        self.detect_function = detect_function
    
    async def detect_relationships(self, new_fact: Fact, existing_facts: List[Fact]) -> List[Tuple[str, RelationshipType, float]]:
        return await self.detect_function(new_fact, existing_facts)