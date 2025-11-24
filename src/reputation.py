"""
Game Master Agent - Reputation System
Tracks player reputation with different factions and NPCs.
"""

from typing import Dict, Any, Optional


class ReputationSystem:
    """Manages player reputation with factions and NPCs."""
    
    def __init__(self):
        """Initialize the reputation system."""
        self.faction_reputations: Dict[str, int] = {}  # faction_name -> reputation (-100 to 100)
        self.npc_reputations: Dict[str, int] = {}  # npc_name -> reputation (-100 to 100)
        self.reputation_history: list = []
    
    def get_faction_reputation(self, faction: str) -> int:
        """Get reputation with a faction."""
        return self.faction_reputations.get(faction, 0)
    
    def get_npc_reputation(self, npc_name: str) -> int:
        """Get reputation with an NPC."""
        return self.npc_reputations.get(npc_name, 0)
    
    def modify_reputation(self, faction: Optional[str] = None, 
                         npc_name: Optional[str] = None, 
                         amount: int = 0,
                         reason: str = "") -> Dict[str, Any]:
        """
        Modify reputation with a faction or NPC.
        
        Args:
            faction: Faction name (optional)
            npc_name: NPC name (optional)
            amount: Reputation change (-100 to 100)
            reason: Reason for the change
        
        Returns:
            Result dictionary
        """
        if faction:
            current = self.faction_reputations.get(faction, 0)
            new_reputation = max(-100, min(100, current + amount))
            self.faction_reputations[faction] = new_reputation
            
            self.reputation_history.append({
                "type": "faction",
                "target": faction,
                "change": amount,
                "new_reputation": new_reputation,
                "reason": reason
            })
            
            return {
                "success": True,
                "faction": faction,
                "old_reputation": current,
                "new_reputation": new_reputation,
                "change": amount
            }
        
        elif npc_name:
            current = self.npc_reputations.get(npc_name, 0)
            new_reputation = max(-100, min(100, current + amount))
            self.npc_reputations[npc_name] = new_reputation
            
            self.reputation_history.append({
                "type": "npc",
                "target": npc_name,
                "change": amount,
                "new_reputation": new_reputation,
                "reason": reason
            })
            
            return {
                "success": True,
                "npc": npc_name,
                "old_reputation": current,
                "new_reputation": new_reputation,
                "change": amount
            }
        
        return {"success": False, "error": "Must specify faction or npc_name"}
    
    def get_reputation_level(self, reputation: int) -> str:
        """Get reputation level description."""
        if reputation >= 80:
            return "Revered"
        elif reputation >= 50:
            return "Friendly"
        elif reputation >= 20:
            return "Neutral"
        elif reputation >= -20:
            return "Unfriendly"
        elif reputation >= -50:
            return "Hostile"
        else:
            return "Hated"
    
    def get_npc_reaction(self, npc_name: str) -> Dict[str, Any]:
        """
        Get NPC reaction based on reputation.
        
        Returns:
            Reaction dictionary with dialogue modifiers
        """
        reputation = self.get_npc_reputation(npc_name)
        level = self.get_reputation_level(reputation)
        
        reactions = {
            "Revered": {
                "dialogue_modifier": 10,
                "willingness_to_help": 1.0,
                "discount": 0.5,  # 50% discount
                "description": "They trust you completely and will go out of their way to help."
            },
            "Friendly": {
                "dialogue_modifier": 5,
                "willingness_to_help": 0.8,
                "discount": 0.2,  # 20% discount
                "description": "They like you and are generally helpful."
            },
            "Neutral": {
                "dialogue_modifier": 0,
                "willingness_to_help": 0.5,
                "discount": 0.0,
                "description": "They don't know you well, neutral attitude."
            },
            "Unfriendly": {
                "dialogue_modifier": -5,
                "willingness_to_help": 0.3,
                "discount": 0.0,
                "description": "They're wary of you and less helpful."
            },
            "Hostile": {
                "dialogue_modifier": -10,
                "willingness_to_help": 0.1,
                "discount": 0.0,
                "description": "They dislike you and may refuse to help."
            },
            "Hated": {
                "dialogue_modifier": -20,
                "willingness_to_help": 0.0,
                "discount": 0.0,
                "description": "They despise you and may attack on sight."
            }
        }
        
        reaction = reactions.get(level, reactions["Neutral"])
        reaction["reputation"] = reputation
        reaction["level"] = level
        
        return reaction
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reputation system to dictionary."""
        return {
            "faction_reputations": self.faction_reputations.copy(),
            "npc_reputations": self.npc_reputations.copy(),
            "reputation_history": self.reputation_history.copy()
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """Load reputation system from dictionary."""
        self.faction_reputations = data.get("faction_reputations", {})
        self.npc_reputations = data.get("npc_reputations", {})
        self.reputation_history = data.get("reputation_history", [])

