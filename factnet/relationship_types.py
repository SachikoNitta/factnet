from enum import Enum

class RelationshipType(Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"
    
    def __str__(self):
        return self.value