import uuid
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from .relationship_types import RelationshipType

@dataclass
class Fact:
    id: str
    content: str
    metadata: Dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

@dataclass
class Relationship:
    source_id: str
    target_id: str
    type: RelationshipType
    confidence: float = 1.0
    metadata: Dict = field(default_factory=dict)

class KnowledgeNetwork:
    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.relationships: List[Relationship] = []
        self._relationship_detector: Optional[Callable] = None
    
    def add_fact(self, content: str, fact_id: str = None, metadata: Dict = None) -> Fact:
        fact = Fact(
            id=fact_id or str(uuid.uuid4()),
            content=content,
            metadata=metadata or {}
        )
        self.facts[fact.id] = fact
        
        if self._relationship_detector:
            self._detect_relationships_for_fact(fact)
        
        return fact
    
    def add_relationship(self, source_id: str, target_id: str, 
                        relationship_type: RelationshipType, 
                        confidence: float = 1.0, metadata: Dict = None) -> Relationship:
        if source_id not in self.facts or target_id not in self.facts:
            raise ValueError("Both source and target facts must exist")
        
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        self.relationships.append(relationship)
        return relationship
    
    def get_fact(self, fact_id: str) -> Optional[Fact]:
        return self.facts.get(fact_id)
    
    def get_relationships(self, fact_id: str = None, 
                         relationship_type: RelationshipType = None) -> List[Relationship]:
        results = self.relationships
        
        if fact_id:
            results = [r for r in results if r.source_id == fact_id or r.target_id == fact_id]
        
        if relationship_type:
            results = [r for r in results if r.type == relationship_type]
        
        return results
    
    def get_supporting_facts(self, fact_id: str) -> List[Fact]:
        relationships = self.get_relationships(fact_id, RelationshipType.SUPPORTS)
        return [self.facts[r.source_id] for r in relationships if r.target_id == fact_id]
    
    def get_contradicting_facts(self, fact_id: str) -> List[Fact]:
        relationships = self.get_relationships(fact_id, RelationshipType.CONTRADICTS)
        return [self.facts[r.source_id] for r in relationships if r.target_id == fact_id]
    
    def set_relationship_detector(self, detector: Callable[[Fact, List[Fact]], List[Tuple[str, RelationshipType, float]]]):
        self._relationship_detector = detector
    
    def _detect_relationships_for_fact(self, new_fact: Fact):
        if not self._relationship_detector:
            return
        
        existing_facts = [f for f in self.facts.values() if f.id != new_fact.id]
        if not existing_facts:
            return
        
        detected = self._relationship_detector(new_fact, existing_facts)
        
        for target_id, rel_type, confidence in detected:
            if target_id in self.facts:
                self.add_relationship(new_fact.id, target_id, rel_type, confidence)
    
    def get_network_stats(self) -> Dict:
        return {
            "total_facts": len(self.facts),
            "total_relationships": len(self.relationships),
            "support_relationships": len([r for r in self.relationships if r.type == RelationshipType.SUPPORTS]),
            "contradiction_relationships": len([r for r in self.relationships if r.type == RelationshipType.CONTRADICTS]),
            "neutral_relationships": len([r for r in self.relationships if r.type == RelationshipType.NEUTRAL])
        }