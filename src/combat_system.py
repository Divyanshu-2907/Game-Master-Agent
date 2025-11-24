"""
Game Master Agent - Combat System Module
Handles combat encounters, initiative, and turn-based combat with conditions.
"""

import random
from typing import Dict, Any, List, Optional
from src.tools import roll_dice, perform_attack, update_character_stat


# Combat conditions
COMBAT_CONDITIONS = {
    "poisoned": {
        "name": "Poisoned",
        "description": "Takes damage at the start of each turn",
        "damage_per_turn": 1,
        "duration": 3,
        "affects": ["hp"]
    },
    "stunned": {
        "name": "Stunned",
        "description": "Cannot take actions, attacks have advantage against them",
        "can_act": False,
        "duration": 1,
        "affects": ["actions", "ac"]
    },
    "bleeding": {
        "name": "Bleeding",
        "description": "Takes damage at the end of each turn",
        "damage_per_turn": 2,
        "duration": 2,
        "affects": ["hp"]
    },
    "blessed": {
        "name": "Blessed",
        "description": "Gains advantage on attack rolls",
        "attack_bonus": 2,
        "duration": 3,
        "affects": ["attacks"]
    },
    "cursed": {
        "name": "Cursed",
        "description": "Suffers disadvantage on attack rolls",
        "attack_penalty": -2,
        "duration": 3,
        "affects": ["attacks"]
    }
}


class CombatManager:
    """Manages combat encounters."""
    
    def __init__(self):
        self.initiative_order = []
        self.current_turn = 0
        self.round = 1
        self.combatants = []
        self.combat_active = False
        self.conditions: Dict[str, List[Dict[str, Any]]] = {}  # character_name -> list of conditions
    
    def apply_condition(self, character_name: str, condition_name: str, 
                       duration: Optional[int] = None) -> Dict[str, Any]:
        """
        Apply a combat condition to a character.
        
        Args:
            character_name: Name of the character
            condition_name: Name of the condition
            duration: Optional custom duration
        
        Returns:
            Result dictionary
        """
        if condition_name not in COMBAT_CONDITIONS:
            return {"success": False, "error": f"Unknown condition: {condition_name}"}
        
        condition_template = COMBAT_CONDITIONS[condition_name]
        condition = {
            "name": condition_name,
            "description": condition_template["description"],
            "duration": duration or condition_template.get("duration", 1),
            "applied_at_round": self.round
        }
        
        if character_name not in self.conditions:
            self.conditions[character_name] = []
        
        # Check if already has this condition
        existing = [c for c in self.conditions[character_name] if c["name"] == condition_name]
        if existing:
            # Refresh duration
            existing[0]["duration"] = condition["duration"]
            return {"success": True, "refreshed": True, "condition": existing[0]}
        
        self.conditions[character_name].append(condition)
        return {"success": True, "condition": condition}
    
    def remove_condition(self, character_name: str, condition_name: str) -> Dict[str, Any]:
        """Remove a condition from a character."""
        if character_name in self.conditions:
            self.conditions[character_name] = [
                c for c in self.conditions[character_name] if c["name"] != condition_name
            ]
            return {"success": True}
        return {"success": False, "error": "Character not found"}
    
    def process_conditions(self, character_name: str, character: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process conditions for a character at the start/end of their turn.
        
        Returns:
            Dictionary with condition effects
        """
        if character_name not in self.conditions:
            return {"effects": [], "damage_taken": 0}
        
        effects = []
        total_damage = 0
        
        # Process each condition
        conditions_to_remove = []
        for condition in self.conditions[character_name]:
            condition_template = COMBAT_CONDITIONS[condition["name"]]
            
            # Reduce duration
            condition["duration"] -= 1
            
            # Apply effects
            if "damage_per_turn" in condition_template:
                damage = condition_template["damage_per_turn"]
                total_damage += damage
                effects.append(f"{condition['name']}: {damage} damage")
            
            # Check if expired
            if condition["duration"] <= 0:
                conditions_to_remove.append(condition["name"])
        
        # Remove expired conditions
        for cond_name in conditions_to_remove:
            self.remove_condition(character_name, cond_name)
            effects.append(f"{cond_name} expired")
        
        # Apply damage
        if total_damage > 0:
            current_hp = character.get("hp", {}).get("current", 0)
            new_hp = max(0, current_hp - total_damage)
            character["hp"]["current"] = new_hp
        
        return {
            "effects": effects,
            "damage_taken": total_damage,
            "conditions_removed": conditions_to_remove
        }
    
    def get_condition_modifiers(self, character_name: str) -> Dict[str, Any]:
        """Get attack/AC modifiers from conditions."""
        modifiers = {"attack_bonus": 0, "attack_penalty": 0, "ac_modifier": 0}
        
        if character_name not in self.conditions:
            return modifiers
        
        for condition in self.conditions[character_name]:
            condition_template = COMBAT_CONDITIONS[condition["name"]]
            
            if "attack_bonus" in condition_template:
                modifiers["attack_bonus"] += condition_template["attack_bonus"]
            if "attack_penalty" in condition_template:
                modifiers["attack_penalty"] += condition_template["attack_penalty"]
            if "affects" in condition_template and "ac" in condition_template["affects"]:
                modifiers["ac_modifier"] -= 2  # Stunned reduces AC
        
        return modifiers
    
    def start_combat(self, player: Dict[str, Any], enemies: List[Dict[str, Any]], 
                    difficulty: str = "medium") -> Dict[str, Any]:
        """
        Initialize a combat encounter.
        
        Args:
            player: Player character
            enemies: List of enemy dictionaries
            difficulty: Difficulty level ("easy", "medium", "hard")
        
        Returns:
            Combat initialization result
        """
        # Scale enemies based on player level and difficulty
        player_level = player.get("level", 1)
        difficulty_multipliers = {
            "easy": 0.8,
            "medium": 1.0,
            "hard": 1.3
        }
        multiplier = difficulty_multipliers.get(difficulty, 1.0)
        
        # Adjust enemy levels
        for enemy in enemies:
            base_level = enemy.get("level", 1)
            scaled_level = max(1, int(player_level * multiplier))
            enemy["level"] = scaled_level
            
            # Recalculate stats for scaled level
            stats = enemy.get("stats", {})
            for stat in stats:
                stats[stat] += (scaled_level - base_level) // 2
            
            # Recalculate HP
            con_mod = (stats.get("constitution", 10) - 10) // 2
            hp_die = enemy.get("hp_die", 8)
            max_hp = hp_die * scaled_level + con_mod
            enemy["hp"] = {"current": max_hp, "max": max_hp}
        
        # Reset conditions
        self.conditions = {}
        self.combatants = [{"type": "player", "character": player}] + [
            {"type": "enemy", "character": enemy} for enemy in enemies
        ]
        
        # Roll initiative for all combatants
        initiatives = []
        for combatant in self.combatants:
            char = combatant["character"]
            dex_mod = (char.get("stats", {}).get("dexterity", 10) - 10) // 2
            init_roll = roll_dice("1d20")
            init_total = init_roll["total"] + dex_mod
            initiatives.append({
                "combatant": combatant,
                "initiative": init_total,
                "roll": init_roll
            })
        
        # Sort by initiative (highest first)
        initiatives.sort(key=lambda x: x["initiative"], reverse=True)
        self.initiative_order = [item["combatant"] for item in initiatives]
        
        self.current_turn = 0
        self.round = 1
        self.combat_active = True
        
        return {
            "combat_started": True,
            "initiative_order": [
                {
                    "name": c["character"].get("name", "Unknown"),
                    "type": c["type"],
                    "initiative": init["initiative"]
                }
                for c, init in zip(self.initiative_order, initiatives)
            ],
            "round": self.round,
            "current_turn": self.initiative_order[0]["character"].get("name", "Unknown")
        }
    
    def get_current_combatant(self) -> Optional[Dict[str, Any]]:
        """Get the combatant whose turn it is."""
        if not self.combat_active or not self.initiative_order:
            return None
        return self.initiative_order[self.current_turn]
    
    def next_turn(self) -> Dict[str, Any]:
        """
        Advance to the next turn.
        
        Returns:
            Turn information
        """
        if not self.combat_active:
            return {"error": "No active combat", "success": False}
        
        self.current_turn += 1
        
        # Check if round is over
        if self.current_turn >= len(self.initiative_order):
            self.current_turn = 0
            self.round += 1
        
        current = self.get_current_combatant()
        
        return {
            "round": self.round,
            "turn": self.current_turn + 1,
            "current_combatant": current["character"].get("name", "Unknown") if current else None,
            "type": current["type"] if current else None
        }
    
    def player_attack(self, player: Dict[str, Any], target_name: str, 
                     weapon: Optional[str] = None) -> Dict[str, Any]:
        """
        Player attacks a target.
        
        Args:
            player: Player character
            target_name: Name of target to attack
            weapon: Optional weapon name
        
        Returns:
            Attack result
        """
        # Find target
        target = None
        for combatant in self.combatants:
            if combatant["type"] == "enemy" and combatant["character"].get("name") == target_name:
                target = combatant["character"]
                break
        
        if not target:
            return {"error": f"Target {target_name} not found", "success": False}
        
        # Perform attack
        result = perform_attack(player, target, weapon)
        
        if result.get("hit") and result.get("damage", 0) > 0:
            # Apply damage
            current_hp = target.get("hp", {}).get("current", 0)
            new_hp = max(0, current_hp - result["damage"])
            target["hp"]["current"] = new_hp
            
            # Check if defeated
            if new_hp == 0:
                result["target_defeated"] = True
                # Remove from combat
                self.combatants = [c for c in self.combatants if c["character"] != target]
                self.initiative_order = [c for c in self.initiative_order if c["character"] != target]
        
        return result
    
    def enemy_turn(self, enemy: Dict[str, Any], player: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an enemy's turn (AI-controlled).
        
        Args:
            enemy: Enemy character
            player: Player character
        
        Returns:
            Enemy action result
        """
        # Simple AI: attack player
        result = perform_attack(enemy, player)
        
        if result.get("hit") and result.get("damage", 0) > 0:
            # Apply damage to player
            current_hp = player.get("hp", {}).get("current", 0)
            new_hp = max(0, current_hp - result["damage"])
            player["hp"]["current"] = new_hp
            result["player_hp"] = new_hp
            
            if new_hp == 0:
                result["player_defeated"] = True
        
        return result
    
    def check_combat_status(self) -> Dict[str, Any]:
        """
        Check if combat is over.
        
        Returns:
            Combat status
        """
        players = [c for c in self.combatants if c["type"] == "player"]
        enemies = [c for c in self.combatants if c["type"] == "enemy"]
        
        if not players or all(p["character"].get("hp", {}).get("current", 0) <= 0 for p in players):
            self.combat_active = False
            return {
                "combat_active": False,
                "victory": False,
                "message": "All players defeated"
            }
        
        if not enemies or all(e["character"].get("hp", {}).get("current", 0) <= 0 for e in enemies):
            self.combat_active = False
            return {
                "combat_active": False,
                "victory": True,
                "message": "All enemies defeated"
            }
        
        return {
            "combat_active": True,
            "players_remaining": len(players),
            "enemies_remaining": len(enemies)
        }
    
    def end_combat(self) -> Dict[str, Any]:
        """End combat and reset state."""
        self.combat_active = False
        self.initiative_order = []
        self.current_turn = 0
        self.round = 1
        self.combatants = []
        
        return {"combat_ended": True, "success": True}


def create_enemy(name: str, enemy_type: str, level: int = 1, 
                difficulty: str = "medium") -> Dict[str, Any]:
    """
    Create an enemy NPC for combat with difficulty scaling.
    
    Args:
        name: Enemy name
        enemy_type: Type of enemy (e.g., "goblin", "skeleton", "orc")
        level: Base enemy level
        difficulty: Difficulty modifier ("easy", "medium", "hard")
    
    Returns:
        Enemy character dictionary
    """
    # Enemy templates
    templates = {
        "goblin": {
            "stats": {"strength": 8, "dexterity": 14, "constitution": 10, 
                     "intelligence": 10, "wisdom": 8, "charisma": 8},
            "hp_die": 7,
            "ac": 15
        },
        "skeleton": {
            "stats": {"strength": 10, "dexterity": 14, "constitution": 15,
                     "intelligence": 6, "wisdom": 8, "charisma": 5},
            "hp_die": 9,
            "ac": 13
        },
        "orc": {
            "stats": {"strength": 16, "dexterity": 12, "constitution": 16,
                     "intelligence": 7, "wisdom": 11, "charisma": 10},
            "hp_die": 15,
            "ac": 13
        },
        "animated_furniture": {
            "stats": {"strength": 14, "dexterity": 8, "constitution": 16,
                     "intelligence": 1, "wisdom": 3, "charisma": 1},
            "hp_die": 10,
            "ac": 12
        }
    }
    
    template = templates.get(enemy_type.lower(), templates["goblin"])
    stats = template["stats"].copy()
    
    # Apply difficulty scaling
    difficulty_multipliers = {
        "easy": 0.8,
        "medium": 1.0,
        "hard": 1.3
    }
    multiplier = difficulty_multipliers.get(difficulty, 1.0)
    scaled_level = max(1, int(level * multiplier))
    
    # Scale with level
    for stat in stats:
        stats[stat] += (scaled_level - 1) // 2
    
    con_mod = (stats["constitution"] - 10) // 2
    max_hp = int(template["hp_die"] * scaled_level * multiplier) + con_mod
    
    # Store original level and difficulty for reference
    enemy_level = scaled_level
    
    enemy = {
        "name": name,
        "type": enemy_type,
        "level": enemy_level,
        "base_level": level,
        "difficulty": difficulty,
        "hp": {"current": max_hp, "max": max_hp},
        "ac": template["ac"],
        "stats": stats,
        "inventory": [],
        "gold": random.randint(5, 15) * enemy_level,
        "conditions": []
    }
    
    return enemy

