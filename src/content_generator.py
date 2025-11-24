"""
Game Master Agent - Content Generation Module
Generates NPCs, quests, locations, and other game content.
"""

import json
import random
from typing import Dict, Any, Optional, List
from pathlib import Path


def generate_npc(context: str, role: str, 
                 templates_path: str = "data/templates/npc_templates.json") -> Dict[str, Any]:
    """
    Generate an NPC based on context and role.
    
    Args:
        context: Story context for the NPC
        role: NPC role (e.g., "tavern_owner", "guard", "merchant")
        templates_path: Path to NPC templates file
    
    Returns:
        Generated NPC dictionary
    """
    try:
        # Load templates
        templates_file = Path(templates_path)
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        # Get base template
        base_template = templates.get(role.lower(), {})
        
        # Generate NPC with variations
        npc = {
            "name": base_template.get("name", f"Unknown {role}"),
            "role": role,
            "personality": base_template.get("personality", "Neutral"),
            "description": base_template.get("description", "A mysterious figure"),
            "motivation": base_template.get("motivation", "Unknown"),
            "dialogue_style": base_template.get("dialogue_style", "Normal"),
            "context": context,
            "met": False,
            "interactions": []
        }
        
        # Add random variations
        if not base_template:
            # Generate from scratch
            names = ["Aldric", "Brenna", "Cedric", "Dara", "Ewan", "Fiona", 
                    "Gareth", "Helena", "Ivor", "Jenna", "Kael", "Luna"]
            npc["name"] = random.choice(names)
            npc["description"] = f"A {role.replace('_', ' ')} with a {random.choice(['kind', 'stern', 'mysterious', 'cheerful'])} demeanor"
        
        return {
            "npc": npc,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def create_quest(difficulty: str, theme: str,
                 templates_path: str = "data/templates/quest_templates.json") -> Dict[str, Any]:
    """
    Create a quest based on difficulty and theme.
    
    Args:
        difficulty: Quest difficulty ("easy", "medium", "hard")
        theme: Quest theme or template name
        templates_path: Path to quest templates file
    
    Returns:
        Generated quest dictionary
    """
    try:
        # Load templates
        templates_file = Path(templates_path)
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        # Get base template
        base_template = templates.get(theme.lower(), {})
        
        # Create quest
        quest = {
            "title": base_template.get("title", f"{theme.replace('_', ' ').title()} Quest"),
            "description": base_template.get("description", f"A {difficulty} quest"),
            "difficulty": difficulty,
            "status": "active",
            "objectives": base_template.get("objectives", []).copy(),
            "completed_objectives": [],
            "rewards": base_template.get("rewards", {
                "experience": 100,
                "gold": 50,
                "items": []
            }).copy(),
            "locations": base_template.get("locations", []).copy(),
            "started_at": None,
            "completed_at": None
        }
        
        # Adjust rewards based on difficulty
        difficulty_multipliers = {
            "easy": 0.7,
            "medium": 1.0,
            "hard": 1.5
        }
        multiplier = difficulty_multipliers.get(difficulty.lower(), 1.0)
        quest["rewards"]["experience"] = int(quest["rewards"]["experience"] * multiplier)
        quest["rewards"]["gold"] = int(quest["rewards"]["gold"] * multiplier)
        
        return {
            "quest": quest,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def generate_location(location_type: str, context: str = "") -> Dict[str, Any]:
    """
    Generate a location description.
    
    Args:
        location_type: Type of location (e.g., "tavern", "dungeon", "forest")
        context: Story context
    
    Returns:
        Location dictionary
    """
    location_templates = {
        "tavern": {
            "name": "The Rusty Tankard",
            "description": "A dimly lit tavern with wooden beams overhead. The air smells of ale and roasted meat. Patrons huddle around tables, speaking in hushed tones.",
            "features": ["bar", "tables", "fireplace", "stairs"],
            "atmosphere": "warm but tense"
        },
        "dungeon": {
            "name": "Ancient Dungeon",
            "description": "Cold stone walls covered in moss. Torches flicker, casting dancing shadows. The sound of dripping water echoes in the distance.",
            "features": ["corridors", "cells", "traps", "treasure_room"],
            "atmosphere": "ominous and foreboding"
        },
        "forest": {
            "name": "The Whispering Woods",
            "description": "Tall trees create a canopy overhead, filtering sunlight. Birds chirp in the distance. The path ahead is barely visible.",
            "features": ["trees", "path", "clearing", "stream"],
            "atmosphere": "mysterious and alive"
        },
        "town": {
            "name": "Small Town",
            "description": "A peaceful town with cobblestone streets. Shops line the main road, and townsfolk go about their daily business.",
            "features": ["shops", "inn", "temple", "market"],
            "atmosphere": "busy but friendly"
        }
    }
    
    template = location_templates.get(location_type.lower(), {
        "name": f"{location_type.title()}",
        "description": f"A {location_type}",
        "features": [],
        "atmosphere": "neutral"
    })
    
    location = {
        "type": location_type,
        "name": template["name"],
        "description": template["description"],
        "features": template["features"],
        "atmosphere": template["atmosphere"],
        "context": context,
        "explored": False,
        "npcs": [],
        "items": []
    }
    
    return {
        "location": location,
        "success": True
    }


def generate_combat_encounter(difficulty: str, location: str, 
                              player_level: int = 1) -> Dict[str, Any]:
    """
    Generate a combat encounter.
    
    Args:
        difficulty: Encounter difficulty ("easy", "medium", "hard")
        location: Location where encounter occurs
        player_level: Player's level
    
    Returns:
        Encounter dictionary with enemies
    """
    enemy_types = ["goblin", "skeleton", "orc", "animated_furniture", "bandit"]
    
    difficulty_enemy_counts = {
        "easy": (1, 2),
        "medium": (2, 3),
        "hard": (3, 5)
    }
    
    min_count, max_count = difficulty_enemy_counts.get(difficulty.lower(), (1, 2))
    enemy_count = random.randint(min_count, max_count)
    
    enemies = []
    for i in range(enemy_count):
        enemy_type = random.choice(enemy_types)
        enemy_name = f"{enemy_type.title()} {i+1}"
        enemies.append({
            "name": enemy_name,
            "type": enemy_type,
            "level": max(1, player_level + random.randint(-1, 1))
        })
    
    encounter = {
        "difficulty": difficulty,
        "location": location,
        "enemies": enemies,
        "status": "pending"
    }
    
    return {
        "encounter": encounter,
        "success": True
    }


def generate_puzzle(puzzle_type: str = "riddle") -> Dict[str, Any]:
    """
    Generate a puzzle or riddle.
    
    Args:
        puzzle_type: Type of puzzle ("riddle", "logic", "pattern")
    
    Returns:
        Puzzle dictionary
    """
    riddles = [
        {
            "question": "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?",
            "answer": "echo",
            "hints": ["It's a sound phenomenon", "It repeats what you say"]
        },
        {
            "question": "The more you take, the more you leave behind. What am I?",
            "answer": "footsteps",
            "hints": ["Think about walking", "They're left on the ground"]
        },
        {
            "question": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?",
            "answer": "map",
            "hints": ["It's something you use for navigation", "It shows geographical features"]
        }
    ]
    
    if puzzle_type.lower() == "riddle":
        puzzle = random.choice(riddles)
    else:
        puzzle = {
            "question": "Solve this logic puzzle: If all roses are flowers, and some flowers are red, are all roses red?",
            "answer": "no",
            "hints": ["Think about the logic", "Not all flowers are roses"]
        }
    
    return {
        "puzzle": {
            "type": puzzle_type,
            "question": puzzle["question"],
            "answer": puzzle["answer"].lower(),
            "hints": puzzle.get("hints", []),
            "solved": False
        },
        "success": True
    }

