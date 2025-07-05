import asyncio
import uuid
from typing import List, Optional, Dict, Any
from .knowledge_network import Fact, Relationship
from .relationship_types import RelationshipType
from .backends import FactStorage, InMemoryStorage
from .ai_detectors import AIRelationshipDetector

class KnowledgeGraph:
    def __init__(self, storage: FactStorage, ai_detector: Optional[AIRelationshipDetector] = None):
        self.storage = storage
        self.ai_detector = ai_detector
        self._processing_queue = asyncio.Queue()
        self._processing_task = None
        self._start_processing()
    
    def _start_processing(self):
        """Start the background task for processing relationships"""
        if self._processing_task is None or self._processing_task.done():
            self._processing_task = asyncio.create_task(self._process_relationships())
    
    async def add_fact(self, content: str, fact_id: str = None, metadata: Dict = None) -> Fact:
        """
        Add a new fact to the knowledge graph.
        This will trigger AI relationship detection with existing facts.
        """
        fact = Fact(
            id=fact_id or str(uuid.uuid4()),
            content=content,
            metadata=metadata or {}
        )
        
        # Store the fact
        await self.storage.add_fact(fact)
        
        # Queue for relationship detection
        if self.ai_detector:
            await self._processing_queue.put(fact)
        
        return fact
    
    async def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Get a fact by ID"""
        return await self.storage.get_fact(fact_id)
    
    async def get_all_facts(self) -> List[Fact]:
        """Get all facts in the knowledge graph"""
        return await self.storage.get_all_facts()
    
    async def add_manual_relationship(self, source_id: str, target_id: str, 
                                    relationship_type: RelationshipType, 
                                    confidence: float = 1.0, metadata: Dict = None) -> Relationship:
        """Manually add a relationship between two facts"""
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            type=relationship_type,
            confidence=confidence,
            metadata=metadata or {}
        )
        
        await self.storage.add_relationship(relationship)
        return relationship
    
    async def get_relationships(self, fact_id: str = None, 
                              relationship_type: RelationshipType = None) -> List[Relationship]:
        """Get relationships, optionally filtered by fact_id and/or relationship type"""
        relationships = await self.storage.get_relationships(fact_id)
        
        if relationship_type:
            relationships = [r for r in relationships if r.type == relationship_type]
        
        return relationships
    
    async def get_supporting_facts(self, fact_id: str) -> List[Fact]:
        """Get all facts that support the given fact"""
        relationships = await self.get_relationships(fact_id, RelationshipType.SUPPORTS)
        supporting_facts = []
        
        for rel in relationships:
            if rel.target_id == fact_id:
                fact = await self.get_fact(rel.source_id)
                if fact:
                    supporting_facts.append(fact)
        
        return supporting_facts
    
    async def get_contradicting_facts(self, fact_id: str) -> List[Fact]:
        """Get all facts that contradict the given fact"""
        relationships = await self.get_relationships(fact_id, RelationshipType.CONTRADICTS)
        contradicting_facts = []
        
        for rel in relationships:
            if rel.target_id == fact_id:
                fact = await self.get_fact(rel.source_id)
                if fact:
                    contradicting_facts.append(fact)
        
        return contradicting_facts
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        facts = await self.get_all_facts()
        relationships = await self.get_relationships()
        
        return {
            "total_facts": len(facts),
            "total_relationships": len(relationships),
            "support_relationships": len([r for r in relationships if r.type == RelationshipType.SUPPORTS]),
            "contradiction_relationships": len([r for r in relationships if r.type == RelationshipType.CONTRADICTS]),
            "neutral_relationships": len([r for r in relationships if r.type == RelationshipType.NEUTRAL])
        }
    
    async def _process_relationships(self):
        """Background task to process relationship detection"""
        while True:
            try:
                # Get new fact from queue
                new_fact = await self._processing_queue.get()
                
                if self.ai_detector:
                    # Get all existing facts except the new one
                    all_facts = await self.get_all_facts()
                    existing_facts = [f for f in all_facts if f.id != new_fact.id]
                    
                    if existing_facts:
                        # Detect relationships
                        detected_relationships = await self.ai_detector.detect_relationships(
                            new_fact, existing_facts
                        )
                        
                        # Add detected relationships
                        for target_id, rel_type, confidence in detected_relationships:
                            await self.storage.update_relationship(
                                new_fact.id, target_id, rel_type, confidence
                            )
                        
                        print(f"Processed {len(detected_relationships)} relationships for fact: {new_fact.id}")
                
                # Mark task as done
                self._processing_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error processing relationships: {e}")
                self._processing_queue.task_done()
    
    async def wait_for_processing(self):
        """Wait for all queued relationship processing to complete"""
        await self._processing_queue.join()
    
    async def close(self):
        """Close the knowledge graph and cleanup resources"""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        
        if hasattr(self.storage, 'close'):
            self.storage.close()