"""
Creature Creation Service - Simplified for D&D Creatures

This module provides creature creation for D&D beasts, monsters, animals, and NPCs.
It's a condensed and simplified version of the character creation system, 
focusing on the subset of features needed for creatures rather than full player characters.

Key differences from character creation:
- Simplified stat blocks (no complex character progression)
- Focus on basic creature attributes (AC, HP, abilities, attacks)
- Streamlined generation without backstory complexity
- Support for creature types (Beast, Monstrosity, Humanoid, etc.)
- Challenge Rating system instead of character levels

Dependencies: Core backend modules (simplified subset)
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Import only needed modules for creature creation
from llm_service_new import create_llm_service, LLMService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CREATURE CREATION CONFIGURATION
# ============================================================================

@dataclass
class CreatureConfig:
    """Configuration for creature creation process."""
    base_timeout: int = 15
    max_retries: int = 2
    include_tactics: bool = True
    include_lore: bool = False
    auto_calculate_cr: bool = True

@dataclass
class CreatureResult:
    """Result container for creature creation operations."""
    
    def __init__(self, success: bool = False, creature_data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.creature_data = creature_data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.creature_data)

# ============================================================================
# CREATURE MODELS
# ============================================================================

@dataclass
class CreatureStatBlock:
    """Basic creature stat block for D&D creatures."""
    name: str
    creature_type: str  # Beast, Monstrosity, Humanoid, etc.
    size: str  # Tiny, Small, Medium, Large, Huge, Gargantuan
    challenge_rating: float
    armor_class: int
    hit_points: int
    hit_dice: str
    speed: Dict[str, int]  # walk, fly, swim, burrow, climb
    ability_scores: Dict[str, int]  # STR, DEX, CON, INT, WIS, CHA
    skills: Dict[str, int] = None
    damage_resistances: List[str] = None
    damage_immunities: List[str] = None
    condition_immunities: List[str] = None
    senses: Dict[str, int] = None
    languages: List[str] = None
    proficiency_bonus: int = 2
    
    def __post_init__(self):
        self.skills = self.skills or {}
        self.damage_resistances = self.damage_resistances or []
        self.damage_immunities = self.damage_immunities or []
        self.condition_immunities = self.condition_immunities or []
        self.senses = self.senses or {"passive_perception": 10}
        self.languages = self.languages or []

@dataclass
class CreatureAction:
    """Represents a creature action (attack, spell, ability)."""
    name: str
    action_type: str  # "attack", "spell", "ability", "legendary"
    description: str
    damage_dice: str = None
    damage_type: str = None
    attack_bonus: int = None
    save_dc: int = None
    save_ability: str = None
    recharge: str = None  # "5-6", "6", etc.

# ============================================================================
# CREATURE CREATION SERVICE
# ============================================================================

class CreatureCreationService:
    """
    Main service for creating D&D creatures.
    Simplified version of character creation focused on creature stat blocks.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        self.llm_service = llm_service or create_llm_service()
        self.validator = CreatureValidator()
        self.generator = CreatureDataGenerator(self.llm_service)
        self.logger = logging.getLogger(__name__)
    
    # ========================================================================
    # MAIN CREATION METHODS
    # ========================================================================
    
    async def create_creature(self, creature_concept: Dict[str, Any], 
                            config: CreatureConfig = None) -> CreatureResult:
        """
        Create a complete creature from a concept.
        
        Args:
            creature_concept: Basic creature concept (name, type, CR, etc.)
            config: Creation configuration
            
        Returns:
            CreatureResult with complete stat block
        """
        # TODO: Implement creature creation workflow
        # 1. Validate concept
        # 2. Generate base stats
        # 3. Calculate derived stats (HP, AC, etc.)
        # 4. Generate actions and abilities
        # 5. Validate final creature
        pass
    
    async def create_creature_variant(self, base_creature: Dict[str, Any], 
                                    variant_concept: Dict[str, Any]) -> CreatureResult:
        """
        Create a variant of an existing creature.
        
        Args:
            base_creature: Existing creature to modify
            variant_concept: Variant modifications
            
        Returns:
            CreatureResult with variant creature
        """
        # TODO: Implement variant creation
        # 1. Copy base creature
        # 2. Apply variant modifications
        # 3. Recalculate stats as needed
        # 4. Validate variant
        pass
    
    async def bulk_create_creatures(self, creature_list: List[Dict[str, Any]]) -> List[CreatureResult]:
        """
        Create multiple creatures efficiently.
        
        Args:
            creature_list: List of creature concepts
            
        Returns:
            List of CreatureResults
        """
        # TODO: Implement bulk creation
        # 1. Process creatures in batches
        # 2. Handle parallel creation where possible
        # 3. Collect and return results
        pass
    
    # ========================================================================
    # CREATURE GENERATION HELPERS
    # ========================================================================
    
    def calculate_challenge_rating(self, stat_block: CreatureStatBlock) -> float:
        """
        Calculate appropriate challenge rating for a creature.
        
        Args:fin
            stat_block: Creature stat block
            
        Returns:
            Calculated challenge rating
        """
        # TODO: Implement CR calculation
        # 1. Calculate offensive CR (damage output)
        # 2. Calculate defensive CR (HP, AC, saves)
        # 3. Average and adjust for special abilities
        pass
    
    def generate_creature_actions(self, stat_block: CreatureStatBlock, 
                                num_actions: int = 2) -> List[CreatureAction]:
        """
        Generate appropriate actions for a creature.
        
        Args:
            stat_block: Creature stat block
            num_actions: Number of actions to generate
            
        Returns:
            List of creature actions
        """
        # TODO: Implement action generation
        # 1. Determine action types based on creature type
        # 2. Calculate attack bonuses and damage
        # 3. Generate special abilities if appropriate
        pass
    
    def balance_creature_stats(self, stat_block: CreatureStatBlock) -> CreatureStatBlock:
        """
        Balance creature stats for appropriate challenge level.
        
        Args:
            stat_block: Initial stat block
            
        Returns:
            Balanced stat block
        """
        # TODO: Implement stat balancing
        # 1. Check if stats are appropriate for CR
        # 2. Adjust HP, AC, damage to match target CR
        # 3. Ensure no stats are too high/low for creature type
        pass

# ============================================================================
# CREATURE VALIDATION
# ============================================================================

class CreatureValidator:
    """Validates creature stat blocks for correctness and balance."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_creature(self, stat_block: CreatureStatBlock) -> List[str]:
        """
        Validate a complete creature stat block.
        
        Args:
            stat_block: Creature to validate
            
        Returns:
            List of validation errors (empty if valid)
        """
        # TODO: Implement validation
        # 1. Check required fields are present
        # 2. Validate stat ranges for creature type
        # 3. Check CR matches actual power level
        # 4. Validate action mechanics
        pass
    
    def validate_creature_type(self, creature_type: str, size: str) -> bool:
        """
        Validate creature type and size combination.
        
        Args:
            creature_type: Type of creature
            size: Size category
            
        Returns:
            True if valid combination
        """
        # TODO: Implement type/size validation
        pass
    
    def validate_challenge_rating(self, stat_block: CreatureStatBlock) -> Dict[str, Any]:
        """
        Validate that creature stats match its challenge rating.
        
        Args:
            stat_block: Creature to validate
            
        Returns:
            Validation results with suggested CR if different
        """
        # TODO: Implement CR validation
        pass

# ============================================================================
# CREATURE DATA GENERATION
# ============================================================================

class CreatureDataGenerator:
    """Generates creature data using LLM services."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
        self.logger = logging.getLogger(__name__)
    
    async def generate_creature_description(self, stat_block: CreatureStatBlock) -> str:
        """
        Generate descriptive text for a creature.
        
        Args:
            stat_block: Creature stat block
            
        Returns:
            Generated description
        """
        # TODO: Implement description generation
        pass
    
    async def generate_creature_tactics(self, stat_block: CreatureStatBlock, 
                                      actions: List[CreatureAction]) -> str:
        """
        Generate tactical combat description.
        
        Args:
            stat_block: Creature stat block
            actions: Creature actions
            
        Returns:
            Tactical description
        """
        # TODO: Implement tactics generation
        pass
    
    async def generate_creature_lore(self, stat_block: CreatureStatBlock) -> Dict[str, str]:
        """
        Generate background lore for a creature.
        
        Args:
            stat_block: Creature stat block
            
        Returns:
            Dictionary with lore sections
        """
        # TODO: Implement lore generation
        pass
    
    def suggest_creature_variants(self, base_creature: CreatureStatBlock) -> List[Dict[str, Any]]:
        """
        Suggest interesting variants of a base creature.
        
        Args:
            base_creature: Base creature stat block
            
        Returns:
            List of variant suggestions
        """
        # TODO: Implement variant suggestions
        pass

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def quick_creature(name: str, creature_type: str, challenge_rating: float) -> CreatureResult:
    """
    Quickly create a basic creature with minimal input.
    
    Args:
        name: Creature name
        creature_type: Type of creature
        challenge_rating: Desired challenge rating
        
    Returns:
        CreatureResult with basic creature
    """
    # TODO: Implement quick creature creation
    pass

def creature_from_template(template_name: str, modifications: Dict[str, Any] = None) -> CreatureResult:
    """
    Create a creature from a predefined template.
    
    Args:
        template_name: Name of creature template
        modifications: Optional modifications to apply
        
    Returns:
        CreatureResult with template-based creature
    """
    # TODO: Implement template-based creation
    pass

def export_creature_statblock(creature: CreatureStatBlock, format: str = "json") -> str:
    """
    Export creature stat block in various formats.
    
    Args:
        creature: Creature stat block
        format: Export format ("json", "markdown", "dnd_beyond")
        
    Returns:
        Formatted creature data
    """
    # TODO: Implement export functionality
    pass

class JournalBasedEvolution:
    """Handles character evolution based on journal entries and play history."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze_play_patterns(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze journal entries to determine character play patterns."""
        if not journal_entries:
            return {"themes": [], "suggested_evolution": [], "confidence": 0.0}
        
        # Extract text from all journal entries
        journal_text = " ".join([entry.get("entry", "") for entry in journal_entries])
        
        # Enhanced keyword analysis
        analysis_patterns = {
            "stealth_assassin": {
                "keywords": ["sneak", "hide", "assassin", "shadow", "stealth", "backstab", "ambush", "poison", "silent", "dagger"],
                "weight": 1.0
            },
            "social_diplomat": {
                "keywords": ["persuade", "negotiate", "charm", "diplomat", "talk", "convince", "deception", "insight", "court"],
                "weight": 1.0
            },
            "combat_warrior": {
                "keywords": ["fight", "battle", "attack", "combat", "weapon", "armor", "charge", "defend", "warrior", "sword"],
                "weight": 1.0
            },
            "magic_scholar": {
                "keywords": ["spell", "magic", "cast", "ritual", "arcane", "divine", "study", "research", "tome", "scroll"],
                "weight": 1.0
            },
            "explorer_ranger": {
                "keywords": ["explore", "track", "wilderness", "forest", "survival", "nature", "animal", "guide", "scout"],
                "weight": 1.0
            },
            "healer_support": {
                "keywords": ["heal", "cure", "medicine", "help", "support", "protect", "save", "rescue", "tend", "care"],
                "weight": 1.0
            },
            "leader_commander": {
                "keywords": ["lead", "command", "order", "strategy", "tactics", "rally", "inspire", "organize", "direct"],
                "weight": 1.0
            }
        }
        
        text_lower = journal_text.lower()
        detected_themes = {}
        
        for pattern_name, pattern_data in analysis_patterns.items():
            score = sum(text_lower.count(keyword) for keyword in pattern_data["keywords"])
            if score > 0:
                detected_themes[pattern_name] = {
                    "score": score,
                    "confidence": min(score / 10.0, 1.0)  # Cap at 1.0
                }
        
        # Sort themes by score
        sorted_themes = sorted(detected_themes.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "themes": [{"name": theme, "score": data["score"], "confidence": data["confidence"]} 
                      for theme, data in sorted_themes],
            "total_entries": len(journal_entries),
            "analysis_confidence": min(len(journal_entries) / 20.0, 1.0)  # Higher confidence with more entries
        }
    
    def suggest_character_evolution(self, current_character: Dict[str, Any], 
                                  play_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest character evolution based on play patterns."""
        suggestions = {
            "multiclass_recommendations": [],
            "feat_suggestions": [],
            "skill_focus": [],
            "equipment_changes": [],
            "roleplay_evolution": "",
            "mechanical_changes": []
        }
        
        current_classes = current_character.get("classes", {})
        primary_class = max(current_classes.items(), key=lambda x: x[1])[0] if current_classes else "Fighter"
        
        themes = play_analysis.get("themes", [])
        if not themes:
            return suggestions
        
        top_theme = themes[0]["name"] if themes else None
        
        # Multiclass suggestions based on play patterns
        class_suggestions = {
            "stealth_assassin": ["Rogue", "Ranger", "Shadow Monk"],
            "social_diplomat": ["Bard", "Paladin", "Warlock"],
            "combat_warrior": ["Fighter", "Barbarian", "Paladin"],
            "magic_scholar": ["Wizard", "Sorcerer", "Warlock"],
            "explorer_ranger": ["Ranger", "Druid", "Scout Rogue"],
            "healer_support": ["Cleric", "Druid", "Divine Soul Sorcerer"],
            "leader_commander": ["Paladin", "Bard", "War Cleric"]
        }
        
        if top_theme in class_suggestions:
            for suggested_class in class_suggestions[top_theme]:
                if suggested_class not in current_classes:
                    suggestions["multiclass_recommendations"].append({
                        "class": suggested_class,
                        "reason": f"Journal shows strong {top_theme.replace('_', ' ')} tendencies",
                        "confidence": themes[0]["confidence"]
                    })
        
        # Feat suggestions
        feat_suggestions = {
            "stealth_assassin": ["Skulker", "Alert", "Assassinate", "Shadow Touched"],
            "social_diplomat": ["Actor", "Fey Touched", "Skill Expert", "Inspiring Leader"],
            "combat_warrior": ["Great Weapon Master", "Polearm Master", "Sentinel", "Tough"],
            "magic_scholar": ["Ritual Caster", "Magic Initiate", "Fey Touched", "Telekinetic"],
            "explorer_ranger": ["Sharpshooter", "Mobile", "Observant", "Nature Adept"],
            "healer_support": ["Healer", "Inspiring Leader", "Tough", "Fey Touched"],
            "leader_commander": ["Inspiring Leader", "Rally", "Tactical Mind", "Command"]
        }
        
        if top_theme in feat_suggestions:
            suggestions["feat_suggestions"] = feat_suggestions[top_theme]
        
        # Roleplay evolution
        evolution_descriptions = {
            "stealth_assassin": f"Character has evolved from {primary_class} into a shadow operative, using stealth and precision over brute force.",
            "social_diplomat": f"Character has grown beyond {primary_class} combat focus into a skilled negotiator and social manipulator.",
            "combat_warrior": f"Character has embraced their {primary_class} nature, becoming an exceptional warrior and tactician.",
            "magic_scholar": f"Character has discovered magical aptitude beyond their {primary_class} training, seeking arcane knowledge.",
            "explorer_ranger": f"Character has developed strong wilderness skills, moving beyond typical {primary_class} boundaries.",
            "healer_support": f"Character has found their calling in protecting and healing others, expanding beyond {primary_class} limitations.",
            "leader_commander": f"Character has naturally evolved into a leadership role, inspiring others beyond typical {primary_class} expectations."
        }
        
        if top_theme in evolution_descriptions:
            suggestions["roleplay_evolution"] = evolution_descriptions[top_theme]
        
        return suggestions
    
    def generate_evolved_backstory(self, current_backstory: str, journal_entries: List[Dict[str, Any]]) -> str:
        """Generate an evolved backstory incorporating journal entries."""
        if not journal_entries:
            return current_backstory
        
        # Summarize key journal moments
        key_moments = []
        for entry in journal_entries[-10:]:  # Last 10 entries for recent development
            entry_text = entry.get("entry", "")
            if len(entry_text) > 50:  # Only include substantial entries
                key_moments.append(entry_text)
        
        if not key_moments:
            return current_backstory
        
        prompt = f"""Evolve this character's backstory by incorporating their recent adventures:

ORIGINAL BACKSTORY:
{current_backstory}

RECENT ADVENTURES (from journal):
{chr(10).join(['- ' + moment for moment in key_moments[:5]])}

Create an evolved backstory that:
1. Keeps the core original elements
2. Shows character growth through these experiences
3. Explains how these adventures changed them
4. Maintains narrative consistency
5. Reflects their evolution as an adventurer

Return the evolved backstory as a single coherent narrative."""
        
        try:
            evolved_backstory = self.llm_service.generate(prompt, timeout_seconds=15)
            return evolved_backstory.strip()
        except Exception as e:
            logger.warning(f"Failed to generate evolved backstory: {e}")
            return current_backstory
    
    def create_character_arc_summary(self, character_name: str, journal_entries: List[Dict[str, Any]], 
                                   evolution_suggestions: Dict[str, Any]) -> str:
        """Create a summary of the character's development arc."""
        if not journal_entries:
            return f"{character_name} is just beginning their adventure."
        
        entry_count = len(journal_entries)
        themes = evolution_suggestions.get("themes", [])
        
        if not themes:
            return f"Through {entry_count} adventures, {character_name} has grown as a well-rounded adventurer."
        
        top_themes = [theme["name"].replace("_", " ") for theme in themes[:3]]
        
        arc_summary = f"""Character Arc for {character_name}:

Through {entry_count} documented adventures, {character_name} has shown remarkable growth and development. 

Primary Development Themes:
{chr(10).join(['• ' + theme.title() for theme in top_themes])}

Evolution Summary:
{evolution_suggestions.get('roleplay_evolution', 'Character continues to grow through their adventures.')}

This character has grown beyond their original conception, shaped by the challenges and choices they've faced in their journey."""
        
        return arc_summary

# ============================================================================
# CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Handles validation of character data."""
    
    @staticmethod
    def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
        """Validate basic character data structure."""
        result = CreationResult()
        
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        missing_fields = [field for field in required_fields if field not in character_data]
        
        if missing_fields:
            result.error = f"Missing required fields: {', '.join(missing_fields)}"
            return result
        
        # Validate ability scores
        abilities = character_data.get("ability_scores", {})
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in abilities:
                result.add_warning(f"Missing ability score: {ability}")
            else:
                score = abilities[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    result.add_warning(f"Invalid {ability} score: {score}")
        
        # Validate level
        level = character_data.get("level", 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            result.add_warning(f"Invalid character level: {level}")
        
        result.success = True
        result.data = character_data
        return result
    
    @staticmethod
    def validate_custom_content(character_data: Dict[str, Any], 
                              needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
        """Validate that custom content requirements are met."""
        result = CreationResult(success=True, data=character_data)
        
        # Check for custom species if needed
        if needs_custom_species:
            species = character_data.get("species", "").lower()
            standard_species = [
                "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
                "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
                "goliath", "tabaxi", "kenku", "lizardfolk", "tortle"
            ]
            
            if species in standard_species:
                result.add_warning(f"Used standard species '{species}' when custom was expected")
        
        # Check for custom class if needed
        if needs_custom_class:
            classes = character_data.get("classes", {})
            class_names = [name.lower() for name in classes.keys()]
            standard_classes = [
                "barbarian", "bard", "cleric", "druid", "fighter", "monk",
                "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
                "artificer", "blood hunter"
            ]
            
            for class_name in class_names:
                if class_name in standard_classes:
                    result.add_warning(f"Used standard class '{class_name}' when custom was expected")
                    break
        
        return result

# ============================================================================
# CHARACTER DATA GENERATION
# ============================================================================

class CharacterDataGenerator:
    """Handles core character data generation using LLM services."""
    
    def __init__(self, llm_service: LLMService, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    def generate_character_data(self, description: str, level: int) -> CreationResult:
        """Generate core character data with retry logic."""
        start_time = time.time()
        
        needs_custom_species = self._needs_custom_species(description)
        needs_custom_class = self._needs_custom_class(description)
        
        # Create targeted prompt
        prompt = self._create_character_prompt(description, level, needs_custom_species, needs_custom_class)
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Character generation attempt {attempt + 1}/{self.config.max_retries}")
                
                timeout = max(self.config.base_timeout - (attempt * 5), 10)
                response = self.llm_service.generate(prompt, timeout_seconds=timeout)
                
                # Clean and parse response
                cleaned_response = self._clean_json_response(response)
                character_data = json.loads(cleaned_response)
                character_data["level"] = level
                
                # Validate basic structure
                validation_result = self.validator.validate_basic_structure(character_data)
                if not validation_result.success:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(f"Validation failed: {validation_result.error}, retrying...")
                        continue
                    else:
                        character_data = self._apply_fixes(character_data, description, level)
                
                # Validate custom content requirements
                custom_validation = self.validator.validate_custom_content(
                    character_data, needs_custom_species, needs_custom_class
                )
                
                result = CreationResult(success=True, data=character_data)
                result.warnings.extend(validation_result.warnings + custom_validation.warnings)
                result.creation_time = time.time() - start_time
                
                logger.info("Character generation successful")
                return result
                
            except (TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    prompt = self._get_simplified_prompt(description, level)
                    continue
                else:
                    logger.error("All attempts failed, using fallback")
                    return self._get_fallback_result(description, level, start_time)
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    return self._get_fallback_result(description, level, start_time)
        
        return self._get_fallback_result(description, level, start_time)
    
    def _needs_custom_species(self, description: str) -> bool:
        """Determine if description requires custom species."""
        custom_keywords = ["unique", "custom", "new species", "homebrew", "original", "invented"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _needs_custom_class(self, description: str) -> bool:
        """Determine if description requires custom class."""
        custom_keywords = ["custom class", "homebrew class", "new class", "unique class"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _create_character_prompt(self, description: str, level: int, 
                               needs_custom_species: bool, needs_custom_class: bool) -> str:
        """Create optimized character generation prompt."""
        
        custom_instructions = ""
        if needs_custom_species:
            custom_instructions += "CREATE custom species name matching description. "
        if needs_custom_class:
            custom_instructions += "CREATE custom class name matching description. "
        
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}
{custom_instructions}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Skill1","Skill2"],"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":[{{"name":"Item","quantity":1}}],"backstory":"Brief backstory"}}

Match description exactly. Return complete JSON only."""
    
    def _get_simplified_prompt(self, description: str, level: int) -> str:
        """Get simplified prompt for retry attempts."""
        return f"""Character: {description}, Level {level}
JSON: {{"name":"Name","species":"Human","level":{level},"classes":{{"Fighter":{level}}},"background":"Folk Hero","alignment":["Neutral","Good"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Athletics"],"personality_traits":["Brave"],"ideals":["Justice"],"bonds":["Community"],"flaws":["Stubborn"],"armor":"Leather","weapons":[{{"name":"Sword","damage":"1d8","properties":["versatile"]}}],"equipment":[{{"name":"Pack","quantity":1}}],"backstory":"A brave {description} warrior."}}"""
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response."""
        if not response:
            raise ValueError("Empty response")
        
        # Remove markdown and find JSON boundaries
        response = response.replace('```json', '').replace('```', '').strip()
        
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[first_brace:last_brace + 1]
        
        # Basic JSON repair
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json_str
    
    def _apply_fixes(self, character_data: Dict[str, Any], description: str, level: int) -> Dict[str, Any]:
        """Apply fixes for common character data issues."""
        
        # Fix missing fields with defaults
        defaults = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "classes": {"Fighter": level},
            "ability_scores": {
                "strength": 13, "dexterity": 12, "constitution": 14,
                "intelligence": 11, "wisdom": 10, "charisma": 8
            },
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "skill_proficiencies": ["Athletics"],
            "personality_traits": ["Determined"],
            "ideals": ["Justice"],
            "bonds": ["Hometown"],
            "flaws": ["Stubborn"],
            "armor": "Leather",
            "weapons": [{"name": "Sword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
            "backstory": f"A {description} seeking adventure."
        }
        
        for key, value in defaults.items():
            if key not in character_data or not character_data[key]:
                character_data[key] = value
        
        return character_data
    
    def _generate_name_from_description(self, description: str) -> str:
        """Generate a simple name from description."""
        words = description.split()
        if words:
            return words[0].capitalize() + " " + ("Adventurer" if len(words) == 1 else words[-1].capitalize())
        return "Unknown Adventurer"
    
    def _get_fallback_result(self, description: str, level: int, start_time: float) -> CreationResult:
        """Create a fallback character when generation fails."""
        fallback_data = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "ability_scores": {
                "strength": 15, "dexterity": 13, "constitution": 14,
                "intelligence": 12, "wisdom": 10, "charisma": 8
            },
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "personality_traits": ["Brave and determined"],
            "ideals": ["Justice for all"],
            "bonds": ["Protecting my community"],
            "flaws": ["Too trusting of others"],
            "armor": "Chain Mail",
            "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
            "backstory": f"A fallback character based on: {description}"
        }
        
        result = CreationResult(success=True, data=fallback_data)
        result.add_warning("Used fallback character due to generation failures")
        result.creation_time = time.time() - start_time
        
        return result

# ============================================================================
# CHARACTER CREATOR
# ============================================================================

class CharacterCreator:
    """Main character creation service integrating all components with journal evolution."""
    
    def __init__(self, llm_service: LLMService = None, config: CreationConfig = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize components
        self.content_registry = ContentRegistry()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.custom_content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        
        # Initialize journal-based evolution
        self.journal_evolution = JournalBasedEvolution(self.llm_service)
        
        # Initialize managers
        self.feat_manager = FeatManager()
        
        logger.info("Character Creator initialized with journal evolution support")
    
    def create_character(self, description: str, level: int = 1, 
                        generate_backstory: bool = True,
                        include_custom_content: bool = False,
                        add_initial_journal: bool = True) -> CreationResult:
        """Create a complete D&D character from description."""
        
        start_time = time.time()
        
        try:
            # Generate core character data
            logger.info(f"Creating character: {description} (Level {level})")
            data_result = self.data_generator.generate_character_data(description, level)
            
            if not data_result.success:
                return data_result
            
            character_data = data_result.data
            
            # Create CharacterCore from the data
            character_core = self._build_character_core(character_data)
            
            # Create character sheet with journal initialization
            character_sheet = CharacterSheet(character_core.name)
            character_sheet.core = character_core
            character_sheet.state = CharacterState()
            character_sheet.stats = CharacterStats(character_core, character_sheet.state)
            
            # Add initial journal entry if requested
            if add_initial_journal:
                self._add_initial_journal_content(character_sheet, character_data, description)
            
            # Create managers for the character
            asi_manager = ASIManager()
            level_manager = CharacterLevelManager()
            ability_manager = AdvancedAbilityManager(character_core)
            
            # Generate backstory if requested
            backstory = None
            if generate_backstory:
                backstory_prompt = self._build_backstory_prompt(character_data)
                backstory = self.backstory_generator.generate_backstory(backstory_prompt)
                
                # Set backstory in character core
                if backstory:
                    character_core.backstory = backstory
            
            # Generate custom content if requested
            custom_content = {}
            if include_custom_content:
                custom_content = self._generate_custom_content(character_data, description)
            
            # Initialize character state with proper HP
            character_sheet.calculate_all_derived_stats()
            
            # Build final result
            result_data = {
                "core": character_core.to_dict(),
                "sheet": character_sheet.get_character_summary(),
                "backstory": backstory,
                "custom_content": custom_content,
                "journal": {
                    "entries": character_sheet.get_journal_entries(),
                    "summary": character_sheet.get_journal_summary()
                },
                "managers": {
                    "asi_info": asi_manager.calculate_available_asis(character_core.character_classes),
                    "level_summary": level_manager.get_level_progression_summary(character_core.character_classes),
                    "ability_summary": ability_manager.get_ability_summary()
                }
            }
            
            result = CreationResult(success=True, data=result_data)
            result.warnings.extend(data_result.warnings)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Character creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character creation failed: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def update_character_with_journal(self, character_sheet: CharacterSheet, 
                                    force_evolution: bool = False) -> CreationResult:
        """Update an existing character based on their journal entries."""
        
        start_time = time.time()
        
        try:
            journal_entries = character_sheet.get_journal_entries()
            
            if not journal_entries and not force_evolution:
                return CreationResult(
                    success=True, 
                    data={"message": "No journal entries to analyze"},
                    warnings=["Character has no journal entries for evolution analysis"]
                )
            
            # Analyze play patterns from journal
            play_analysis = self.journal_evolution.analyze_play_patterns(journal_entries)
            
            # Generate evolution suggestions
            current_character_data = character_sheet.get_character_summary()
            evolution_suggestions = self.journal_evolution.suggest_character_evolution(
                current_character_data, play_analysis
            )
            
            # Generate evolved backstory
            current_backstory = character_sheet.get_backstory()
            evolved_backstory = self.journal_evolution.generate_evolved_backstory(
                current_backstory, journal_entries
            )
            
            # Create character arc summary
            character_arc = self.journal_evolution.create_character_arc_summary(
                character_sheet.get_name(), journal_entries, play_analysis
            )
            
            # Update backstory if it evolved
            if evolved_backstory and evolved_backstory != current_backstory:
                character_sheet.core.backstory = evolved_backstory
                # Add journal entry about backstory evolution
                character_sheet.add_journal_entry(
                    "Character backstory has evolved based on recent adventures and experiences.",
                    tags=["character_development", "backstory_evolution"]
                )
            
            result_data = {
                "character_summary": character_sheet.get_character_summary(),
                "play_analysis": play_analysis,
                "evolution_suggestions": evolution_suggestions,
                "evolved_backstory": evolved_backstory,
                "character_arc": character_arc,
                "journal_summary": character_sheet.get_journal_summary()
            }
            
            result = CreationResult(success=True, data=result_data)
            result.creation_time = time.time() - start_time
            
            # Add suggestions as warnings for visibility
            if evolution_suggestions.get("multiclass_recommendations"):
                for rec in evolution_suggestions["multiclass_recommendations"][:2]  # Top 2
                    result.add_warning(f"Consider multiclassing: {rec['class']} - {rec['reason']}")
            
            logger.info(f"Character evolution analysis completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character journal analysis failed: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def apply_evolution_suggestions(self, character_sheet: CharacterSheet, 
                                  evolution_suggestions: Dict[str, Any],
                                  apply_multiclass: bool = False,
                                  apply_feats: bool = False) -> CreationResult:
        """Apply evolution suggestions to a character."""
        
        start_time = time.time()
        changes_made = []
        
        try:
            # Apply multiclass suggestions if requested
            if apply_multiclass and evolution_suggestions.get("multiclass_recommendations"):
                top_multiclass = evolution_suggestions["multiclass_recommendations"][0]
                new_class = top_multiclass["class"]
                
                # Add 1 level in the suggested class
                current_classes = character_sheet.core.character_classes.copy()
                current_classes[new_class] = current_classes.get(new_class, 0) + 1
                character_sheet.core.character_classes = current_classes
                
                # Add journal entry
                character_sheet.add_journal_entry(
                    f"Began training in {new_class} based on recent experiences and natural aptitude.",
                    tags=["multiclass", "character_development", new_class.lower()]
                )
                
                changes_made.append(f"Added 1 level in {new_class}")
            
            # Apply feat suggestions (simulation - would need actual feat system)
            if apply_feats and evolution_suggestions.get("feat_suggestions"):
                suggested_feats = evolution_suggestions["feat_suggestions"][:2]  # Top 2
                
                character_sheet.add_journal_entry(
                    f"Considering developing new abilities: {', '.join(suggested_feats)}",
                    tags=["feat_consideration", "character_development"]
                )
                
                changes_made.append(f"Noted feat considerations: {', '.join(suggested_feats)}")
            
            # Recalculate stats
            character_sheet.calculate_all_derived_stats()
            
            result_data = {
                "character_summary": character_sheet.get_character_summary(),
                "changes_applied": changes_made,
                "evolution_complete": True
            }
            
            result = CreationResult(success=True, data=result_data)
            result.creation_time = time.time() - start_time
            
            for change in changes_made:
                result.add_warning(f"Applied: {change}")
            
            logger.info(f"Evolution suggestions applied in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Failed to apply evolution suggestions: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def _add_initial_journal_content(self, character_sheet: CharacterSheet, 
                                   character_data: Dict[str, Any], description: str):
        """Add initial journal content for a new character."""
        
        # Add creation entry (already added by CharacterSheet constructor)
        
        # Add backstory-based initial entry
        background = character_data.get("background", "Folk Hero")
        personality = character_data.get("personality_traits", ["Brave"])
        
        initial_entry = f"Today I set out on my first real adventure. As a {background}, I've always {personality[0].lower() if personality else 'been determined'}, but now it's time to prove myself in the wider world. The road ahead is uncertain, but I'm ready for whatever challenges await."
        
        character_sheet.add_journal_entry(
            initial_entry,
            tags=["character_creation", "first_adventure", "backstory"]
        )
        
        # Add a hint about their potential based on description
        if "stealth" in description.lower() or "rogue" in description.lower():
            character_sheet.add_journal_entry(
                "I've always felt more comfortable in the shadows, watching and learning before acting.",
                tags=["character_creation", "personality", "stealth"]
            )
        elif "magic" in description.lower() or "wizard" in description.lower():
            character_sheet.add_journal_entry(
                "The arcane arts have always fascinated me. I sense there's more to magic than I currently understand.",
                tags=["character_creation", "personality", "magic"]
            )
        elif "social" in description.lower() or "bard" in description.lower():
            character_sheet.add_journal_entry(
                "I find myself naturally drawn to people and their stories. There's power in words and connections.",
                tags=["character_creation", "personality", "social"]
            )
    
    def _build_character_core(self, character_data: Dict[str, Any]) -> CharacterCore:
        """Build a CharacterCore from character data."""
        
        character_core = CharacterCore(character_data["name"])
        character_core.species = character_data.get("species", "Human")
        character_core.background = character_data.get("background", "Folk Hero")
        character_core.character_classes = character_data.get("classes", {"Fighter": 1})
        character_core.alignment = character_data.get("alignment", ["Neutral", "Good"])
        
        # Set personality traits
        character_core.personality_traits = character_data.get("personality_traits", ["Brave"])
        character_core.ideals = character_data.get("ideals", ["Justice"])
        character_core.bonds = character_data.get("bonds", ["Community"])
        character_core.flaws = character_data.get("flaws", ["Stubborn"])
        
        # Set proficiencies
        skill_profs = character_data.get("skill_proficiencies", [])
        for skill in skill_profs:
            character_core.skill_proficiencies[skill] = ProficiencyLevel.PROFICIENT
        
        # Set ability scores
        ability_scores = character_data.get("ability_scores", {})
        for ability_name, score in ability_scores.items():
            if hasattr(character_core, ability_name):
                setattr(character_core, ability_name, AbilityScore(score))
        
        return character_core
    
    def _build_backstory_prompt(self, character_data: Dict[str, Any]) -> str:
        """Build a backstory generation prompt from character data."""
        
        classes = character_data.get("classes", {})
        class_list = ", ".join([f"{cls} {level}" for cls, level in classes.items()])
        
        prompt = f"""Create a compelling backstory for this D&D character:

Name: {character_data.get('name', 'Unknown')}
Species: {character_data.get('species', 'Human')}
Classes: {class_list}
Background: {character_data.get('background', 'Folk Hero')}
Personality: {', '.join(character_data.get('personality_traits', ['Brave']))}
Ideals: {', '.join(character_data.get('ideals', ['Justice']))}
Bonds: {', '.join(character_data.get('bonds', ['Community']))}
Flaws: {', '.join(character_data.get('flaws', ['Stubborn']))}

Generate a rich, detailed backstory that explains their motivations, background, and how they became an adventurer."""
        
        return prompt
    
    def _generate_custom_content(self, character_data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Generate custom content based on character data."""
        
        custom_content = {}
        
        # Generate custom species if needed
        species = character_data.get("species", "")
        standard_species = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome"]
        
        if species.lower() not in standard_species:
            try:
                custom_species = self.custom_content_generator.generate_custom_species(
                    f"Create a custom species called '{species}' based on: {description}"
                )
                custom_content["species"] = custom_species.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom species: {e}")
        
        # Generate custom background if non-standard
        background = character_data.get("background", "")
        standard_backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
        
        if background.lower() not in standard_backgrounds:
            try:
                # Use content registry to create custom background
                background_id = self.content_registry.add_custom_background(
                    background,
                    f"Custom background: {background}",
                    character_data.get("skill_proficiencies", [])[:2],
                    character_data.get("equipment", [])[:3]
                )
                custom_background = self.content_registry.get_custom_background(background_id)
                if custom_background:
                    custom_content["background"] = custom_background.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom background: {e}")
        
        return custom_content

# ============================================================================
# CREATURE CREATOR
# ============================================================================

class CreatureCreator:
    """Service for creating and registering custom creatures for DM use, with CR support."""
    def __init__(self, db_session, created_by: Optional[str] = None):
        self.db = db_session
        self.created_by = created_by or "dungeon_master"

    def create_and_register_creature(self, name: str, creature_type: str, description: str = "", stat_block: Optional[Dict[str, Any]] = None, challenge_rating: Optional[float] = None, is_public: bool = False) -> Dict[str, Any]:
        """
        Create and register a custom creature in the database.
        creature_type: 'beast', 'monstrosity', 'undead', etc.
        stat_block: dict of creature stats (AC, HP, abilities, attacks, etc.)
        challenge_rating: D&D 5e CR (float or int)
        """
        from database_models_new import CustomContent
        from sqlalchemy.orm import Session
        from sqlalchemy.exc import SQLAlchemyError
        import traceback

        # Ensure CR is in stat_block
        if stat_block is None:
            stat_block = {}
        if challenge_rating is not None:
            stat_block["challenge_rating"] = challenge_rating

        creature_data = {
            "name": name,
            "creature_type": creature_type,
            "description": description,
            "stat_block": stat_block,
            "challenge_rating": stat_block.get("challenge_rating"),
        }
        try:
            db_creature = CustomContent(
                name=name,
                content_type="creature",
                content_data=creature_data,
                description=description,
                created_by=self.created_by,
                is_public=is_public,
            )
            self.db.add(db_creature)
            self.db.commit()
            self.db.refresh(db_creature)
            logger.info(f"Registered creature '{name}' as type '{creature_type}' (CR {creature_data['challenge_rating']}) in database.")
            return {"success": True, "creature": {
                "id": db_creature.id,
                "name": db_creature.name,
                "type": db_creature.content_type,
                "description": db_creature.description,
                "stat_block": db_creature.content_data.get("stat_block", {}),
                "challenge_rating": db_creature.content_data.get("challenge_rating"),
                "created_by": db_creature.created_by,
                "created_at": db_creature.created_at.isoformat(),
                "is_public": db_creature.is_public,
            }}
        except SQLAlchemyError as e:
            logger.error(f"Failed to register creature: {e}\n{traceback.format_exc()}")
            self.db.rollback()
            return {"success": False, "error": str(e)}

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED CHARACTER CREATION MODULE WITH JOURNAL EVOLUTION

This module provides comprehensive character creation and evolution based on play history:

CLASSES:
- CreationConfig: Configuration for character creation
- CreationResult: Result container with success/error/warning info
- JournalBasedEvolution: NEW - Analyzes journal entries for character evolution
- CharacterValidator: Validates character data structure and content
- CharacterDataGenerator: Generates character data using LLM services
- CharacterCreator: Main integration service with journal evolution support
- CharacterProgressionTracker: NEW - Manages character development snapshots and background evolution

KEY FEATURES:
- Journal-based character evolution analysis
- Play pattern detection from journal entries
- Automatic character progression suggestions
- Enhanced backstory generation incorporating journal entries
- Character arc tracking and development
- Multiclass and feat suggestions based on actual play
- Clean integration with all refactored modules
- Comprehensive error handling and validation
- Retry logic for LLM generation failures
- Support for custom content generation
- Backstory generation integration
- Fallback character creation when LLM fails

JOURNAL EVOLUTION FEATURES:
- Analyze play patterns (stealth, combat, social, magic, etc.)
- Suggest multiclass options based on journal themes
- Generate evolved backstories incorporating adventures
- Create character development arcs
- Apply evolution suggestions to characters
- Track character growth through documented experiences

DEPENDENCIES:
- character_models: CharacterCore, CharacterState, CharacterSheet (with journal)
- core_models: AbilityScore, ASIManager, etc.
- custom_content_models: ContentRegistry, managers
- ability_management: AdvancedAbilityManager
- llm_services: LLM integration
- generators: BackstoryGenerator, CustomContentGenerator

NEW METHODS:
- create_character(): Now includes initial journal content
- update_character_with_journal(): Analyze and evolve character from journal
- apply_evolution_suggestions(): Apply suggested changes to character
- analyze_character_evolution(): Get evolution analysis without changes

CONVENIENCE FUNCTIONS:
- create_character(): Enhanced with journal support
- update_character_from_journal(): New - Update character from play history
- analyze_character_evolution(): New - Analyze without updating
- quick_character(): Enhanced to return CharacterSheet with journal

REMOVED:
- Duplicate code and classes
- Legacy/example code
- Overly complex inheritance hierarchies
- Unused async functionality
- Dead code paths

The journal integration allows characters to truly evolve based on how they're actually played,
moving beyond initial conception to reflect the reality of their adventures and growth.
"""
