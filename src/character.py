"""
Game Master Agent - Character Management Module
Handles character creation, stats, and progression.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path


def create_character(name: str, race: str, character_class: str, 
                    stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """
    Create a new character with default stats based on class.
    
    Args:
        name: Character name
        race: Character race (e.g., "human", "elf", "dwarf")
        character_class: Character class (e.g., "fighter", "wizard")
        stats: Optional custom stats dictionary
    
    Returns:
        Complete character dictionary
    """
    # Load class templates
    templates_path = Path("data/templates/character_classes.json")
    if templates_path.exists():
        with open(templates_path, 'r') as f:
            classes = json.load(f)
    else:
        classes = {}
    
    class_info = classes.get(character_class.lower(), {})
    hit_die = class_info.get("hit_die", 8)
    
    # Default stats (point buy system - 27 points)
    if stats is None:
        stats = {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        }
        
        # Adjust based on primary stats
        primary_stats = class_info.get("primary_stats", [])
        for stat in primary_stats:
            if stat in stats:
                stats[stat] = max(stats[stat], 15)
    
    # Calculate HP
    con_modifier = (stats["constitution"] - 10) // 2
    max_hp = hit_die + con_modifier
    
    # Get starting skills
    starting_skills = class_info.get("starting_skills", [])
    
    # Get starting equipment
    starting_equipment = class_info.get("starting_equipment", [])
    
    character = {
        "name": name,
        "race": race,
        "class": character_class,
        "level": 1,
        "experience": 0,
        "hp": {
            "current": max_hp,
            "max": max_hp
        },
        "ac": 10 + (stats["dexterity"] - 10) // 2,  # Base AC
        "stats": stats,
        "skills": {
            "proficient": starting_skills,
            "expertise": []
        },
        "inventory": starting_equipment.copy(),
        "equipped": {
            "weapon": starting_equipment[0] if starting_equipment else "unarmed",
            "armor": starting_equipment[1] if len(starting_equipment) > 1 else "none"
        },
        "gold": 50,
        "background": f"A {race} {character_class} seeking adventure"
    }
    
    return character


def level_up_character(character: Dict[str, Any]) -> Dict[str, Any]:
    """
    Level up a character, increasing HP and potentially stats.
    
    Args:
        character: Character dictionary
    
    Returns:
        Updated character dictionary
    """
    character = character.copy()
    old_level = character["level"]
    new_level = old_level + 1
    
    # Calculate new HP
    class_info = character.get("class", "fighter")
    hit_die = 8  # Default
    if Path("data/templates/character_classes.json").exists():
        with open("data/templates/character_classes.json", 'r') as f:
            classes = json.load(f)
            hit_die = classes.get(class_info.lower(), {}).get("hit_die", 8)
    
    con_modifier = (character["stats"]["constitution"] - 10) // 2
    hp_gain = max(1, (hit_die // 2) + 1 + con_modifier)  # Average roll
    
    character["level"] = new_level
    character["hp"]["max"] += hp_gain
    character["hp"]["current"] += hp_gain  # Full heal on level up
    
    # Ability score improvement every 4 levels
    if new_level % 4 == 0:
        # Increase highest stat by 1
        stats = character["stats"]
        max_stat = max(stats.items(), key=lambda x: x[1])
        stats[max_stat[0]] += 1
    
    return character


def add_experience(character: Dict[str, Any], xp: int) -> Dict[str, Any]:
    """
    Add experience points and level up if threshold is met.
    
    Args:
        character: Character dictionary
        xp: Experience points to add
    
    Returns:
        Updated character dictionary and level up status
    """
    character = character.copy()
    character["experience"] += xp
    
    # Calculate level based on XP (simplified)
    xp_thresholds = [0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000]
    new_level = 1
    for i, threshold in enumerate(xp_thresholds):
        if character["experience"] >= threshold:
            new_level = i + 1
    
    leveled_up = new_level > character["level"]
    
    if leveled_up:
        while character["level"] < new_level:
            character = level_up_character(character)
    
    return {
        "character": character,
        "leveled_up": leveled_up,
        "new_level": character["level"] if leveled_up else None
    }


def get_character_summary(character: Dict[str, Any]) -> str:
    """
    Get a formatted summary of the character.
    
    Args:
        character: Character dictionary
    
    Returns:
        Formatted string summary
    """
    stats = character.get("stats", {})
    hp = character.get("hp", {})
    
    summary = f"""
=== {character.get('name', 'Unknown')} ===
Race: {character.get('race', 'Unknown')}
Class: {character.get('class', 'Unknown')}
Level: {character.get('level', 1)}
HP: {hp.get('current', 0)}/{hp.get('max', 0)}
AC: {character.get('ac', 10)}

Stats:
  STR: {stats.get('strength', 10)}  DEX: {stats.get('dexterity', 10)}
  CON: {stats.get('constitution', 10)}  INT: {stats.get('intelligence', 10)}
  WIS: {stats.get('wisdom', 10)}  CHA: {stats.get('charisma', 10)}

Experience: {character.get('experience', 0)}
Gold: {character.get('gold', 0)}

Equipment: {', '.join(character.get('inventory', []))}
"""
    return summary

