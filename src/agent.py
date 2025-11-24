"""
Game Master Agent - Main Agent Module
Uses Google GenAI/ADK to create an intelligent Dungeon Master agent.
"""

import os
from typing import Dict, Any, Optional, List
from google import genai
from google.genai import types

from src.tools import (
    roll_dice, perform_attack, skill_check, update_character_stat,
    save_game, load_game, list_saved_games
)
from src.state_manager import GameStateManager
from src.content_generator import (
    generate_npc, create_quest, generate_location, 
    generate_combat_encounter, generate_puzzle
)
from src.combat_system import CombatManager, create_enemy
from src.reputation import ReputationSystem
from src.achievements import AchievementsSystem
from src.scenarios import get_scenario, list_scenarios


# System prompt for the Game Master agent
GM_SYSTEM_PROMPT = """You are an expert Dungeon Master running an immersive D&D-style RPG campaign.

CORE RESPONSIBILITIES:
- Create vivid, engaging narratives with rich descriptions
- Control all NPCs with distinct personalities and motivations
- Manage game mechanics fairly and transparently
- Respond to player actions with logical consequences
- Maintain story consistency and world coherence
- Balance challenge with player enjoyment

GAMEPLAY RULES:
- Always use the dice rolling tool for any random checks
- Follow D&D 5e rules loosely (or create simplified rules)
- Announce dice rolls and their results clearly
- Track HP, inventory, and stats accurately
- Give players meaningful choices
- Describe scenes with sensory details (sight, sound, smell)

TONE:
- Descriptive and atmospheric
- Encouraging but challenging
- Neutral narrator perspective
- Enthusiastic about player creativity

COMBAT:
- When combat starts, manage initiative, announce each round clearly
- Describe action cinematically
- Track HP and status effects accurately

DIALOGUE:
- When players talk to NPCs, roleplay the NPC with a distinct voice/personality
- Make NPCs memorable and engaging

EXPLORATION:
- When players search or investigate, call for appropriate skill checks
- Provide detailed descriptions of locations
- Reward creative problem-solving

STATE MANAGEMENT:
- When story beats happen, save the game state automatically
- Remember NPC interactions and player choices
- Maintain continuity across sessions

Be creative, fair, and make the adventure memorable!"""


class GameMasterAgent:
    """Main Game Master agent using Google GenAI/ADK."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        Initialize the Game Master agent.
        
        Args:
            api_key: Google GenAI API key (or set GOOGLE_GENAI_API_KEY env var)
            model: Model to use (default: gemini-2.0-flash-exp)
        """
        # Get API key
        if api_key is None:
            api_key = os.getenv("GOOGLE_GENAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "API key required. Set GOOGLE_GENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # Initialize client
        self.client = genai.Client(api_key=api_key)
        self.model = model
        
        # Initialize state manager
        self.state_manager = GameStateManager()
        
        # Initialize combat manager
        self.combat_manager = CombatManager()
        
        # Initialize reputation system
        self.reputation = ReputationSystem()
        
        # Initialize achievements system
        self.achievements = AchievementsSystem()
        
        # Initialize conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Create agent with tools
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the agent with tools and system prompt."""
        # Define tools for the agent
        self.tools = [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="roll_dice",
                        description="Roll dice using D&D notation (e.g., '1d20', '2d6+3'). Use this for all random checks, attacks, and skill checks.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "notation": types.Schema(
                                    type=types.Type.STRING,
                                    description="Dice notation (e.g., '1d20', '2d6+3', '1d8-1')"
                                )
                            },
                            required=["notation"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="perform_attack",
                        description="Perform an attack roll and calculate damage. Use during combat encounters.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "attacker": types.Schema(
                                    type=types.Type.OBJECT,
                                    description="Attacker character dictionary"
                                ),
                                "defender": types.Schema(
                                    type=types.Type.OBJECT,
                                    description="Defender character dictionary"
                                ),
                                "weapon": types.Schema(
                                    type=types.Type.STRING,
                                    description="Weapon name (optional)"
                                )
                            },
                            required=["attacker", "defender"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="skill_check",
                        description="Perform a skill check against a difficulty class (DC). Use for perception, stealth, persuasion, etc.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "skill": types.Schema(
                                    type=types.Type.STRING,
                                    description="Skill name (e.g., 'perception', 'stealth', 'persuasion')"
                                ),
                                "difficulty": types.Schema(
                                    type=types.Type.INTEGER,
                                    description="Difficulty class (DC) to beat"
                                ),
                                "modifiers": types.Schema(
                                    type=types.Type.OBJECT,
                                    description="Character stats and modifiers"
                                )
                            },
                            required=["skill", "difficulty", "modifiers"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="update_character_stat",
                        description="Update a character's stat (HP, stats, inventory, etc.). Use to track character changes.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "character": types.Schema(
                                    type=types.Type.OBJECT,
                                    description="Character dictionary"
                                ),
                                "stat": types.Schema(
                                    type=types.Type.STRING,
                                    description="Stat name (e.g., 'hp.current', 'stats.strength', 'inventory')"
                                ),
                                "value": types.Schema(
                                    type=types.Type.STRING,
                                    description="New value or operation (e.g., '50', '+10', '-5')"
                                )
                            },
                            required=["character", "stat", "value"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="save_game",
                        description="Save the current game state to a file. Use after important story beats.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "state": types.Schema(
                                    type=types.Type.OBJECT,
                                    description="Game state dictionary"
                                ),
                                "filename": types.Schema(
                                    type=types.Type.STRING,
                                    description="Filename to save to"
                                )
                            },
                            required=["state", "filename"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="load_game",
                        description="Load a game state from a file.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "filename": types.Schema(
                                    type=types.Type.STRING,
                                    description="Filename to load from"
                                )
                            },
                            required=["filename"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="generate_npc",
                        description="Generate an NPC with personality and dialogue. Use when introducing new characters.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "context": types.Schema(
                                    type=types.Type.STRING,
                                    description="Story context for the NPC"
                                ),
                                "role": types.Schema(
                                    type=types.Type.STRING,
                                    description="NPC role (e.g., 'tavern_owner', 'guard', 'merchant')"
                                )
                            },
                            required=["context", "role"]
                        )
                    ),
                    types.FunctionDeclaration(
                        name="create_quest",
                        description="Create a new quest. Use when the player receives a quest.",
                        parameters=types.Schema(
                            type=types.Type.OBJECT,
                            properties={
                                "difficulty": types.Schema(
                                    type=types.Type.STRING,
                                    description="Quest difficulty ('easy', 'medium', 'hard')"
                                ),
                                "theme": types.Schema(
                                    type=types.Type.STRING,
                                    description="Quest theme or template name"
                                )
                            },
                            required=["difficulty", "theme"]
                        )
                    )
                ]
            )
        ]
    
    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments for the tool
        
        Returns:
            Tool execution result
        """
        tool_functions = {
            "roll_dice": roll_dice,
            "perform_attack": perform_attack,
            "skill_check": skill_check,
            "update_character_stat": update_character_stat,
            "save_game": lambda state, filename: self.state_manager.save_state(state, filename),
            "load_game": lambda filename: self.state_manager.load_state(filename),
            "generate_npc": generate_npc,
            "create_quest": create_quest
        }
        
        if tool_name not in tool_functions:
            return {
                "error": f"Unknown tool: {tool_name}",
                "success": False
            }
        
        try:
            func = tool_functions[tool_name]
            result = func(**args)
            return result
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def start_session(self, character: Dict[str, Any], initial_prompt: str = ""):
        """
        Start a new game session.
        
        Args:
            character: Player character dictionary
            initial_prompt: Initial story prompt
        """
        # Create initial state
        state = self.state_manager.create_initial_state(character)
        
        # Add initial prompt to history
        if initial_prompt:
            self.conversation_history = [
                {
                    "role": "user",
                    "content": initial_prompt
                }
            ]
        else:
            self.conversation_history = []
    
    def process_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message and generate a response.
        
        Args:
            user_message: User's message/action
        
        Returns:
            Agent response dictionary
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get current state for context
        current_state = self.state_manager.get_current_state()
        state_context = ""
        if current_state:
            char = current_state.get("character", {})
            state_context = f"""
Current Character: {char.get('name', 'Unknown')} (Level {char.get('level', 1)})
HP: {char.get('hp', {}).get('current', 0)}/{char.get('hp', {}).get('max', 0)}
Location: {current_state.get('current_location', 'Unknown')}
Active Quests: {len(current_state.get('active_quests', []))}
"""
        
        # Prepare messages with system prompt
        messages = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(GM_SYSTEM_PROMPT + "\n\n" + state_context)]
            )
        ]
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Last 10 messages for context
            role = "user" if msg["role"] == "user" else "model"
            messages.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(msg["content"])]
                )
            )
        
        # Generate response with tool calling
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=messages,
                tools=self.tools,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95,
                    max_output_tokens=2048
                )
            )
            
            # Process response
            response_text = ""
            tool_calls = []
            
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
                    elif hasattr(part, 'function_call'):
                        tool_calls.append(part.function_call)
            
            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call.name
                tool_args = {}
                for arg_name, arg_value in tool_call.args.items():
                    tool_args[arg_name] = arg_value
                
                result = self._execute_tool(tool_name, tool_args)
                tool_results.append({
                    "tool": tool_name,
                    "result": result
                })
                
                # Update response text with tool result
                if result.get("success"):
                    response_text += f"\n\n[Used {tool_name}: {result.get('message', 'Success')}]"
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Update state history
            if current_state:
                self.state_manager.add_to_history(f"Player: {user_message}")
                self.state_manager.add_to_history(f"GM: {response_text[:100]}...")
            
            return {
                "response": response_text,
                "tool_calls": tool_results,
                "success": True
            }
            
        except Exception as e:
            error_msg = f"Error generating response: {str(e)}"
            return {
                "response": error_msg,
                "error": str(e),
                "success": False
            }
    
    def get_state(self) -> Optional[Dict[str, Any]]:
        """Get the current game state."""
        return self.state_manager.get_current_state()
    
    def save_current_game(self, filename: Optional[str] = None) -> Dict[str, Any]:
        """Save the current game state."""
        return self.state_manager.save_state(filename=filename)
    
    def load_game(self, filename: str) -> Dict[str, Any]:
        """Load a game state."""
        result = self.state_manager.load_state(filename)
        if result.get("success"):
            # Reset conversation history
            self.conversation_history = []
        return result

