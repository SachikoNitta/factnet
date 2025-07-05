from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from neo4j import GraphDatabase
import asyncio
from .knowledge_network import Fact, Relationship
from .relationship_types import RelationshipType

class FactStorage(ABC):
    @abstractmethod
    async def add_fact(self, fact: Fact) -> str:
        pass
    
    @abstractmethod
    async def get_fact(self, fact_id: str) -> Optional[Fact]:
        pass
    
    @abstractmethod
    async def get_all_facts(self) -> List[Fact]:
        pass
    
    @abstractmethod
    async def add_relationship(self, relationship: Relationship) -> None:
        pass
    
    @abstractmethod
    async def get_relationships(self, fact_id: str = None) -> List[Relationship]:
        pass
    
    @abstractmethod
    async def update_relationship(self, source_id: str, target_id: str, 
                                relationship_type: RelationshipType, confidence: float) -> None:
        pass

class Neo4jStorage(FactStorage):
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self._setup_constraints()
    
    def _setup_constraints(self):
        with self.driver.session() as session:
            session.run("CREATE CONSTRAINT fact_id IF NOT EXISTS FOR (f:Fact) REQUIRE f.id IS UNIQUE")
    
    async def add_fact(self, fact: Fact) -> str:
        def _add_fact_tx(tx, fact):
            # Neo4j doesn't accept empty dicts, so we convert to None if empty
            metadata = fact.metadata if fact.metadata else None
            query = """
            CREATE (f:Fact {id: $id, content: $content, metadata: $metadata, created_at: datetime()})
            RETURN f.id as id
            """
            result = tx.run(query, id=fact.id, content=fact.content, metadata=metadata)
            return result.single()["id"]
        
        with self.driver.session() as session:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.execute_write(_add_fact_tx, fact)
            )
    
    async def get_fact(self, fact_id: str) -> Optional[Fact]:
        def _get_fact_tx(tx, fact_id):
            query = "MATCH (f:Fact {id: $id}) RETURN f.id as id, f.content as content, f.metadata as metadata"
            result = tx.run(query, id=fact_id)
            record = result.single()
            if record:
                metadata = record["metadata"] or {}
                return Fact(id=record["id"], content=record["content"], metadata=metadata)
            return None
        
        with self.driver.session() as session:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.execute_read(_get_fact_tx, fact_id)
            )
    
    async def get_all_facts(self) -> List[Fact]:
        def _get_all_facts_tx(tx):
            query = "MATCH (f:Fact) RETURN f.id as id, f.content as content, f.metadata as metadata"
            result = tx.run(query)
            facts = []
            for record in result:
                metadata = record["metadata"] or {}
                facts.append(Fact(id=record["id"], content=record["content"], metadata=metadata))
            return facts
        
        with self.driver.session() as session:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.execute_read(_get_all_facts_tx)
            )
    
    async def add_relationship(self, relationship: Relationship) -> None:
        def _add_relationship_tx(tx, rel):
            # Neo4j doesn't accept empty dicts, so we convert to None if empty
            metadata = rel.metadata if rel.metadata else None
            query = """
            MATCH (source:Fact {id: $source_id}), (target:Fact {id: $target_id})
            MERGE (source)-[r:RELATES_TO {type: $type}]->(target)
            SET r.confidence = $confidence, r.metadata = $metadata, r.updated_at = datetime()
            """
            tx.run(query, source_id=rel.source_id, target_id=rel.target_id, 
                  type=rel.type.value, confidence=rel.confidence, metadata=metadata)
        
        with self.driver.session() as session:
            await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.execute_write(_add_relationship_tx, relationship)
            )
    
    async def get_relationships(self, fact_id: str = None) -> List[Relationship]:
        def _get_relationships_tx(tx, fact_id):
            if fact_id:
                query = """
                MATCH (source:Fact)-[r:RELATES_TO]->(target:Fact)
                WHERE source.id = $fact_id OR target.id = $fact_id
                RETURN source.id as source_id, target.id as target_id, 
                       r.type as type, r.confidence as confidence, r.metadata as metadata
                """
                result = tx.run(query, fact_id=fact_id)
            else:
                query = """
                MATCH (source:Fact)-[r:RELATES_TO]->(target:Fact)
                RETURN source.id as source_id, target.id as target_id, 
                       r.type as type, r.confidence as confidence, r.metadata as metadata
                """
                result = tx.run(query)
            
            relationships = []
            for record in result:
                rel_type = RelationshipType(record["type"])
                relationships.append(Relationship(
                    source_id=record["source_id"],
                    target_id=record["target_id"],
                    type=rel_type,
                    confidence=record["confidence"],
                    metadata=record["metadata"] or {}
                ))
            return relationships
        
        with self.driver.session() as session:
            return await asyncio.get_event_loop().run_in_executor(
                None, lambda: session.execute_read(_get_relationships_tx, fact_id)
            )
    
    async def update_relationship(self, source_id: str, target_id: str, 
                                relationship_type: RelationshipType, confidence: float) -> None:
        relationship = Relationship(source_id, target_id, relationship_type, confidence)
        await self.add_relationship(relationship)
    
    def close(self):
        self.driver.close()

class InMemoryStorage(FactStorage):
    def __init__(self):
        self.facts: Dict[str, Fact] = {}
        self.relationships: List[Relationship] = []
    
    async def add_fact(self, fact: Fact) -> str:
        self.facts[fact.id] = fact
        return fact.id
    
    async def get_fact(self, fact_id: str) -> Optional[Fact]:
        return self.facts.get(fact_id)
    
    async def get_all_facts(self) -> List[Fact]:
        return list(self.facts.values())
    
    async def add_relationship(self, relationship: Relationship) -> None:
        # Remove existing relationship between same facts
        self.relationships = [r for r in self.relationships 
                            if not (r.source_id == relationship.source_id and r.target_id == relationship.target_id)]
        self.relationships.append(relationship)
    
    async def get_relationships(self, fact_id: str = None) -> List[Relationship]:
        if fact_id:
            return [r for r in self.relationships if r.source_id == fact_id or r.target_id == fact_id]
        return self.relationships
    
    async def update_relationship(self, source_id: str, target_id: str, 
                                relationship_type: RelationshipType, confidence: float) -> None:
        relationship = Relationship(source_id, target_id, relationship_type, confidence)
        await self.add_relationship(relationship)