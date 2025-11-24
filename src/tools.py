"""
Game Master Agent - Tools Module
Contains all game mechanics tools that the agent can use.
"""

import random
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


def roll_dice(notation: str) -> Dict[str, Any]:
    """
    Roll dice based on D&D notation (e.g., "1d20", "2d6+3", "1d8-1").
    
    Args:
        notation: Dice notation string (e.g., "1d20", "2d6+3", "1d8-1")
    
    Returns:
        Dictionary with roll details including individual dice, total, and notation
    """
    try:
        # Parse notation: [count]d[sides][+/-modifier]
        parts = notation.lower().replace(' ', '').split('d')
        if len(parts) != 2:
            raise ValueError(f"Invalid dice notation: {notation}")
        
        count = int(parts[0]) if parts[0] else 1
        rest = parts[1]
        
        # Extract modifier
        modifier = 0
        if '+' in rest:
            sides, mod = rest.split('+')
            modifier = int(mod)
        elif '-' in rest:
            sides, mod = rest.split('-')
            modifier = -int(mod)
        else:
            sides = rest
        
        sides = int(sides)
        
        # Roll dice
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        
        result = {
            "notation": notation,
            "count": count,
            "sides": sides,
            "modifier": modifier,
            "rolls": rolls,
            "total": total,
            "success": True
        }
        
        return result
        
    except Exception as e:
        return {
            "notation": notation,
            "error": str(e),
            "success": False
        }


def perform_attack(attacker: Dict[str, Any], defender: Dict[str, Any], 
                   weapon: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform an attack roll and calculate damage.
    
    Args:
        attacker: Character dictionary with stats
        defender: Character dictionary with stats
        weapon: Optional weapon name (defaults to equipped weapon)
    
    Returns:
        Dictionary with attack roll, hit status, and damage
    """
    try:
        # Get attack bonus from strength or dexterity
        attack_stat = attacker.get("stats", {})
        str_mod = (attack_stat.get("strength", 10) - 10) // 2
        dex_mod = (attack_stat.get("dexterity", 10) - 10) // 2
        attack_bonus = max(str_mod, dex_mod) + attacker.get("level", 1)
        
        # Roll attack
        attack_roll = roll_dice("1d20")
        attack_total = attack_roll["total"] + attack_bonus
        
        # Get AC (Armor Class)
        defender_ac = defender.get("ac", 10)
        if "ac" not in defender:
            # Calculate AC from stats
            dex_mod_def = (defender.get("stats", {}).get("dexterity", 10) - 10) // 2
            defender_ac = 10 + dex_mod_def
        
        # Check if hit
        hit = attack_total >= defender_ac
        critical = attack_roll["rolls"][0] == 20
        
        # Calculate damage
        damage = 0
        if hit:
            # Base damage from weapon (1d8 for most weapons)
            damage_roll = roll_dice("1d8")
            damage = damage_roll["total"] + max(str_mod, dex_mod)
            
            if critical:
                damage = damage * 2
                damage_roll = roll_dice("2d8")
                damage = damage_roll["total"] + max(str_mod, dex_mod) * 2
        
        result = {
            "attacker": attacker.get("name", "Unknown"),
            "defender": defender.get("name", "Unknown"),
            "weapon": weapon or attacker.get("equipped", {}).get("weapon", "unarmed"),
            "attack_roll": attack_roll,
            "attack_bonus": attack_bonus,
            "attack_total": attack_total,
            "defender_ac": defender_ac,
            "hit": hit,
            "critical": critical,
            "damage": damage if hit else 0,
            "success": True
        }
        
        return result
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def skill_check(skill: str, difficulty: int, modifiers: Dict[str, Any]) -> Dict[str, Any]:
    """
    Perform a skill check against a difficulty class (DC).
    
    Args:
        skill: Skill name (e.g., "perception", "stealth", "persuasion")
        difficulty: Difficulty class (DC) to beat
        modifiers: Character stats and modifiers
    
    Returns:
        Dictionary with roll result, success status, and details
    """
    try:
        # Get relevant stat modifier
        stats = modifiers.get("stats", {})
        skill_to_stat = {
            "athletics": "strength",
            "acrobatics": "dexterity",
            "stealth": "dexterity",
            "perception": "wisdom",
            "investigation": "intelligence",
            "insight": "wisdom",
            "persuasion": "charisma",
            "intimidation": "charisma",
            "deception": "charisma",
            "arcana": "intelligence",
            "history": "intelligence",
            "nature": "intelligence",
            "religion": "intelligence",
            "medicine": "wisdom",
            "survival": "wisdom",
            "sleight_of_hand": "dexterity",
            "performance": "charisma"
        }
        
        stat_name = skill_to_stat.get(skill.lower(), "intelligence")
        stat_value = stats.get(stat_name, 10)
        stat_modifier = (stat_value - 10) // 2
        
        # Proficiency bonus (if applicable)
        proficiency = modifiers.get("level", 1) // 4 + 1
        skills = modifiers.get("skills", {})
        if skill.lower() in [s.lower() for s in skills.get("proficient", [])]:
            stat_modifier += proficiency
        
        # Roll d20
        roll = roll_dice("1d20")
        total = roll["total"] + stat_modifier
        
        # Check success
        success = total >= difficulty
        critical_success = roll["rolls"][0] == 20
        critical_failure = roll["rolls"][0] == 1
        
        result = {
            "skill": skill,
            "difficulty": difficulty,
            "roll": roll,
            "stat_modifier": stat_modifier,
            "total": total,
            "success": success,
            "critical_success": critical_success,
            "critical_failure": critical_failure,
            "success": True
        }
        
        return result
        
    except Exception as e:
        return {
            "skill": skill,
            "error": str(e),
            "success": False
        }


def update_character_stat(character: Dict[str, Any], stat: str, value: Any) -> Dict[str, Any]:
    """
    Update a character's stat (HP, stats, inventory, etc.).
    
    Args:
        character: Character dictionary
        stat: Stat name (e.g., "hp", "stats.strength", "inventory")
        value: New value or value to add/subtract
    
    Returns:
        Updated character dictionary
    """
    try:
        character = character.copy()
        
        # Handle nested stats (e.g., "stats.strength", "hp.current")
        if '.' in stat:
            parts = stat.split('.')
            current = character
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Handle operations
            if isinstance(value, str) and value.startswith(('+', '-')):
                op = value[0]
                val = int(value[1:])
                current[parts[-1]] = current.get(parts[-1], 0) + (val if op == '+' else -val)
            else:
                current[parts[-1]] = value
        else:
            # Handle top-level stats
            if isinstance(value, str) and value.startswith(('+', '-')):
                op = value[0]
                val = int(value[1:])
                character[stat] = character.get(stat, 0) + (val if op == '+' else -val)
            else:
                character[stat] = value
        
        return {
            "character": character,
            "updated_stat": stat,
            "new_value": value,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def save_game(state: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    Save game state to a JSON file.
    
    Args:
        state: Game state dictionary
        filename: Filename to save to (will be saved in data/saves/)
    
    Returns:
        Dictionary with save status
    """
    try:
        save_dir = Path("data/saves")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = save_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        return {
            "filename": filename,
            "filepath": str(filepath),
            "success": True,
            "message": f"Game saved successfully to {filepath}"
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "error": str(e),
            "success": False
        }


def load_game(filename: str) -> Dict[str, Any]:
    """
    Load game state from a JSON file.
    
    Args:
        filename: Filename to load from (in data/saves/)
    
    Returns:
        Dictionary with loaded game state or error
    """
    try:
        save_dir = Path("data/saves")
        
        # Ensure .json extension
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = save_dir / filename
        
        if not filepath.exists():
            return {
                "filename": filename,
                "error": f"Save file not found: {filepath}",
                "success": False
            }
        
        with open(filepath, 'r') as f:
            state = json.load(f)
        
        return {
            "filename": filename,
            "state": state,
            "success": True,
            "message": f"Game loaded successfully from {filepath}"
        }
        
    except Exception as e:
        return {
            "filename": filename,
            "error": str(e),
            "success": False
        }


def list_saved_games() -> Dict[str, Any]:
    """
    List all saved game files.
    
    Returns:
        Dictionary with list of saved games
    """
    try:
        save_dir = Path("data/saves")
        save_dir.mkdir(parents=True, exist_ok=True)
        
        saves = [f.name for f in save_dir.glob("*.json")]
        
        return {
            "saves": saves,
            "count": len(saves),
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }

