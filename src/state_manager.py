"""
Game Master Agent - State Management Module
Handles game state persistence, loading, and saving.
"""

import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class GameStateManager:
    """Manages game state persistence and loading."""
    
    def __init__(self, save_directory: str = "data/saves"):
        """
        Initialize the state manager.
        
        Args:
            save_directory: Directory to save game states
        """
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.current_state: Optional[Dict[str, Any]] = None
    
    def create_initial_state(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an initial game state from a character.
        
        Args:
            character: Character dictionary
        
        Returns:
            Initial game state dictionary
        """
        state = {
            "character": character,
            "current_location": "unknown",
            "story_context": "",
            "active_quests": [],
            "completed_quests": [],
            "npcs_met": {},
            "world_state": {},
            "combat_active": False,
            "session_history": [],
            "reputation": {},
            "achievements": {"achievements": [], "milestones": {}},
            "save_slot": None,
            "playtime_minutes": 0,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        self.current_state = state
        return state
    
    def save_state(self, state: Optional[Dict[str, Any]] = None, 
                   filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Save game state to a JSON file.
        
        Args:
            state: Game state dictionary (uses current_state if None)
            filename: Filename to save to (auto-generates if None)
        
        Returns:
            Dictionary with save status
        """
        try:
            state_to_save = state or self.current_state
            
            if state_to_save is None:
                return {
                    "error": "No game state to save",
                    "success": False
                }
            
            # Update timestamp
            state_to_save["last_updated"] = datetime.now().isoformat()
            
            # Generate filename if not provided
            if filename is None:
                char_name = state_to_save.get("character", {}).get("name", "unknown")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{char_name}_{timestamp}.json"
            
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = self.save_directory / filename
            
            # Save to file
            with open(filepath, 'w') as f:
                json.dump(state_to_save, f, indent=2)
            
            self.current_state = state_to_save
            
            return {
                "filename": filename,
                "filepath": str(filepath),
                "success": True,
                "message": f"Game saved successfully to {filepath}"
            }
            
        except Exception as e:
            return {
                "filename": filename or "unknown",
                "error": str(e),
                "success": False
            }
    
    def load_state(self, filename: str) -> Dict[str, Any]:
        """
        Load game state from a JSON file.
        
        Args:
            filename: Filename to load from
        
        Returns:
            Dictionary with loaded game state or error
        """
        try:
            # Ensure .json extension
            if not filename.endswith('.json'):
                filename += '.json'
            
            filepath = self.save_directory / filename
            
            if not filepath.exists():
                return {
                    "filename": filename,
                    "error": f"Save file not found: {filepath}",
                    "success": False
                }
            
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.current_state = state
            
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
    
    def update_state(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the current game state with new values.
        
        Args:
            updates: Dictionary of updates to apply
        
        Returns:
            Updated state dictionary
        """
        if self.current_state is None:
            return {
                "error": "No current game state to update",
                "success": False
            }
        
        # Deep merge updates
        def deep_update(base: Dict, updates: Dict):
            for key, value in updates.items():
                if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                    deep_update(base[key], value)
                else:
                    base[key] = value
        
        deep_update(self.current_state, updates)
        self.current_state["last_updated"] = datetime.now().isoformat()
        
        return {
            "state": self.current_state,
            "success": True
        }
    
    def add_to_history(self, entry: str) -> Dict[str, Any]:
        """
        Add an entry to the session history.
        
        Args:
            entry: History entry string
        
        Returns:
            Update result
        """
        if self.current_state is None:
            return {
                "error": "No current game state",
                "success": False
            }
        
        if "session_history" not in self.current_state:
            self.current_state["session_history"] = []
        
        timestamp = datetime.now().isoformat()
        self.current_state["session_history"].append({
            "timestamp": timestamp,
            "entry": entry
        })
        
        return {
            "success": True,
            "entry_added": entry
        }
    
    def list_saves(self, slot_filter: Optional[int] = None) -> Dict[str, Any]:
        """
        List all saved game files, optionally filtered by save slot.
        
        Args:
            slot_filter: Optional save slot number to filter by
        
        Returns:
            Dictionary with list of saved games
        """
        try:
            saves = []
            for filepath in self.save_directory.glob("*.json"):
                try:
                    with open(filepath, 'r') as f:
                        save_data = json.load(f)
                        char_name = save_data.get("character", {}).get("name", "Unknown")
                        last_updated = save_data.get("last_updated", "Unknown")
                        save_slot = save_data.get("save_slot", None)
                        
                        # Filter by slot if specified
                        if slot_filter is not None and save_slot != slot_filter:
                            continue
                        
                        saves.append({
                            "filename": filepath.name,
                            "character": char_name,
                            "last_updated": last_updated,
                            "location": save_data.get("current_location", "Unknown"),
                            "save_slot": save_slot,
                            "level": save_data.get("character", {}).get("level", 1),
                            "playtime": save_data.get("playtime_minutes", 0)
                        })
                except:
                    saves.append({
                        "filename": filepath.name,
                        "character": "Unknown",
                        "last_updated": "Unknown",
                        "location": "Unknown",
                        "save_slot": None
                    })
            
            # Sort by last updated (most recent first)
            saves.sort(key=lambda x: x.get("last_updated", ""), reverse=True)
            
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
    
    def save_to_slot(self, state: Optional[Dict[str, Any]] = None, 
                    slot_number: int = 1) -> Dict[str, Any]:
        """
        Save game state to a specific save slot (1-10).
        
        Args:
            state: Game state dictionary (uses current_state if None)
            slot_number: Save slot number (1-10)
        
        Returns:
            Dictionary with save status
        """
        if slot_number < 1 or slot_number > 10:
            return {
                "error": "Save slot must be between 1 and 10",
                "success": False
            }
        
        state_to_save = state or self.current_state
        if state_to_save is None:
            return {
                "error": "No game state to save",
                "success": False
            }
        
        # Add save slot info
        state_to_save["save_slot"] = slot_number
        state_to_save["last_updated"] = datetime.now().isoformat()
        
        # Generate filename with slot number
        char_name = state_to_save.get("character", {}).get("name", "unknown")
        filename = f"save_slot_{slot_number:02d}_{char_name}.json"
        
        return self.save_state(state_to_save, filename)
    
    def load_from_slot(self, slot_number: int) -> Dict[str, Any]:
        """
        Load game state from a specific save slot.
        
        Args:
            slot_number: Save slot number (1-10)
        
        Returns:
            Dictionary with loaded game state or error
        """
        result = self.list_saves(slot_filter=slot_number)
        
        if not result.get("success") or not result.get("saves"):
            return {
                "error": f"No save found in slot {slot_number}",
                "success": False
            }
        
        # Get the most recent save in this slot
        latest_save = result["saves"][0]
        return self.load_state(latest_save["filename"])
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        """Get the current game state."""
        return self.current_state
    
    def clear_state(self):
        """Clear the current game state."""
        self.current_state = None

