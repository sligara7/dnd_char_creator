# D&D Character Creator Backend - Engineering Requirements

## CORE MISSION
Create an AI-powered D&D 5e 2024 character creation system that enables users to bring ANY character concept to life through:
- **Creative Freedom**: Generate non-traditional characters beyond standard D&D constraints
- **Custom Content Creation**: Automatically create new classes, species, feats, spells, weapons, and armor
- **Deep Storytelling**: Generate compelling backstories aligned with character concepts
- **Iterative Development**: Collaborative character refinement through user feedback
- **Traditional Foundation**: Prioritize existing D&D content when appropriate, create custom when needed

## PRIMARY REQUIREMENTS

### 1. CHARACTER CREATION SYSTEM
**PRIORITY: CRITICAL**
- **Input**: User provides character concept description (text prompt)
- **Output**: Complete D&D 5e 2024 character sheet with full attributes
- **Process**: LLM translates concept → validates content → generates complete character
- **Flexibility**: Support ANY character concept, even if requiring completely custom content

**Required Character Components:**
- Core Attributes: Name, Species, Class(es), Level, Background, Alignment
- Ability Scores: STR, DEX, CON, INT, WIS, CHA (properly calculated)
- Skills & Proficiencies: Class/species/background appropriate selections
- Feats: Origin feat (level 1) + general feats (levels 4,8,12,16,19) + fighting styles + epic boons
- Equipment: Weapons, armor, tools, general equipment (class/background appropriate)
- Spells: For spellcasters, appropriate spell selection with spell slots
- Backstory: Deep, compelling narrative aligned with character concept
- Personality: Traits, ideals, bonds, flaws that bring character to life

### 2. CUSTOM CONTENT GENERATION
**PRIORITY: CRITICAL**
- **Custom Species**: New races with balanced traits, abilities, and lore
- **Custom Classes**: New classes with level progression, features, and spellcasting
- **Custom Feats**: Unique abilities that enhance character concepts
- **Custom Spells**: Thematic spells that fit character concepts
- **Custom Weapons**: Unique weapons with appropriate damage and properties
- **Custom Armor**: Armor types that fit character themes and protection needs
- **Balance Requirement**: All custom content must be balanced for D&D 5e play

### 3. ITERATIVE REFINEMENT SYSTEM
**PRIORITY: HIGH**
- User describes desired changes to generated character
- System updates character while maintaining consistency
- Process continues until user approves final character
- Track all iterations for version history

### 4. EXISTING CHARACTER ENHANCEMENT
**PRIORITY: HIGH**
- Import existing characters from database
- Level-up characters using journal entries as context for how character is actually played
- Multi-class characters based on play patterns and user preferences
- Maintain character consistency during advancement

### 5. CONTENT HIERARCHY & PRIORITIZATION
**PRIORITY: HIGH**
```
1. FIRST PRIORITY: Use existing D&D 5e 2024 official content when appropriate
2. SECOND PRIORITY: Adapt existing content to fit concept
3. THIRD PRIORITY: Create custom content when concept requires it
4. BALANCE REQUIREMENT: All content must be balanced for level-appropriate play
```

### 5.1. CAMPAIGN THEME-DRIVEN CONTENT CREATION
**PRIORITY: HIGH**
- **Theme Integration**: Support campaign themes (western, cyberpunk, steampunk, horror, etc.) as optional context for content creation
- **Flexible Application**: Theme provides creative direction but doesn't override player choice
- **Player Agency**: Users can still create traditional D&D content in themed campaigns (e.g., elf ranger in cyberpunk)
- **Content Adaptation**: All content types (characters, NPCs, monsters, items, spells) support theme-aware generation
- **Campaign Integration**: Campaign creators can suggest themes for character/content creation while preserving player freedom

**Theme Examples:**
- **Western**: Gunslingers, frontier towns, revolvers, cowboy gear, frontier magic
- **Cyberpunk**: Corporate agents, mega-cities, smart weapons, cyberware, data magic  
- **Steampunk**: Inventors, airships, mechanical gadgets, steam-powered devices, industrial magic
- **Horror**: Investigators, haunted locations, blessed weapons, protective charms, eldritch magic
- **Traditional**: Standard D&D fantasy with no thematic constraints

**Design Principles:**
- Theme is **suggestive, not mandatory** - guides content creation without forcing it
- **Backward compatible** - all existing functionality works unchanged
- **Optional integration** - can be used by campaign services or ignored entirely
- **Player choice preserved** - theme doesn't override specific player requests

## SECONDARY REQUIREMENTS

### 6. NPC & CREATURE CREATION
**PRIORITY: MEDIUM**
- Reuse character creation foundation for NPCs and creatures
- Generate appropriate challenge ratings for creatures
- Create roleplay-focused NPCs with motivations, secrets, and relationships
- Support various NPC types: major, minor, shopkeeper, quest-giver, etc.

### 7. STANDALONE ITEM CREATION
**PRIORITY: MEDIUM**
- Create individual spells, weapons, armor for DM use
- Generate items for in-game discovery and rewards
- Maintain thematic consistency with campaign setting

### 8. DATABASE & VERSION CONTROL
**PRIORITY: MEDIUM**
- UUID tracking for all created content
- Git-like branching for character evolution
- Character approval workflow (tentative → DM approved)
- Persistent storage of custom content for reuse

## TECHNICAL REQUIREMENTS

### 9. SYSTEM ARCHITECTURE
**PRIORITY: CRITICAL**
- **LLM Integration**: OpenAI/Ollama services for content generation
- **D&D 5e Compliance**: Full compatibility with 2024 rules; rules found at https://roll20.net/compendium/dnd5e/Rules:Free%20Basic%20Rules%20(2024)
- **Database Models**: Comprehensive character and content storage
- **API Structure**: RESTful endpoints for all creation operations
- **Error Handling**: Graceful fallbacks when generation fails

### 10. CONTENT VALIDATION
**PRIORITY: HIGH**
- Validate all generated content against D&D 5e rules
- Ensure mathematical correctness of character attributes
- Verify spell slot calculations, AC, HP, proficiency bonuses
- Balance check custom content against existing power levels

### 11. PERFORMANCE STANDARDS
**PRIORITY: MEDIUM**
- Character creation: < 30 seconds for complex characters
- Simple updates: < 5 seconds
- Database queries: < 1 second response time
- Concurrent user support: 10+ simultaneous creations

## IN-GAME PLAY REQUIREMENTS

### 12. CHARACTER SHEET MANAGEMENT
**PRIORITY: MEDIUM**
- Load complete character sheets for play
- Real-time attribute calculations based on conditions
- HP tracking, exhaustion levels, temporary effects
- Automatic updates when character state changes

### 13. JOURNAL & EXPERIENCE SYSTEM
**PRIORITY: LOW**
- Add journal entries to character sheets
- Track XP and prompt for level-up when appropriate
- Use journal data to inform character advancement decisions

## QUALITY STANDARDS

### 14. CONTENT QUALITY
- **Creativity**: Support unique, memorable character concepts
- **Balance**: All content appropriate for specified character level
- **Consistency**: Character elements work together thematically
- **Completeness**: Every character has full D&D 5e attribute set
- **Narrative Depth**: Rich backstories that enhance roleplay

### 15. USER EXPERIENCE
- **Intuitive**: Simple concept description creates complete character
- **Flexible**: Support iteration and refinement
- **Reliable**: Consistent quality across different character types
- **Feedback**: Clear communication of what was generated and why

## IMPLEMENTATION STATUS & ANALYSIS

### ✅ FULLY IMPLEMENTED REQUIREMENTS

#### 1. CHARACTER CREATION SYSTEM (CRITICAL) - ✅ EXCELLENT
- **Factory-based creation**: `/api/v2/factory/create` supports prompt-to-character generation
- **Complete character output**: Full character sheets with all D&D 5e components
- **LLM integration**: Uses creation_factory for AI-powered generation
- **ANY character concept**: Supports custom content generation when needed
- **All required components**: Core attributes, ability scores, skills, equipment, spells, backstory

#### 2. CUSTOM CONTENT GENERATION (CRITICAL) - ✅ EXCELLENT
- **Multiple content types**: Supports character, monster, npc, weapon, armor, spell, other_item
- **Factory pattern**: Unified creation system for all custom content
- **Balance integration**: Uses creation_validation.py for D&D 5e compliance
- **Content hierarchy**: Prioritizes existing D&D content when appropriate

#### 2.1. CAMPAIGN THEME-DRIVEN CONTENT CREATION (HIGH) - ✅ EXCELLENT
- **Theme parameter support**: `/api/v2/factory/create` and `/api/v2/factory/evolve` accept optional theme parameter
- **Backward compatibility**: All existing API calls work unchanged - theme is completely optional
- **All content types**: Characters, NPCs, monsters, weapons, armor, spells all support theme-aware generation
- **Campaign integration**: Campaign service can pass campaign themes to backend for thematic consistency
- **Player agency preserved**: Theme provides creative direction but doesn't override specific player requests
- **Response integration**: Theme included in factory responses for tracking and debugging
- **Foundation ready**: Infrastructure in place for theme-aware content generation logic

#### 3. ITERATIVE REFINEMENT SYSTEM (HIGH) - ✅ EXCELLENT
- **Character refinement**: `/api/v2/characters/{id}/refine` for iterative improvements
- **Structured feedback**: `/api/v2/characters/{id}/feedback` for targeted changes
- **Evolution support**: `/api/v2/factory/evolve` for existing object evolution
- **Version tracking**: Character snapshots and version management

#### 4. EXISTING CHARACTER ENHANCEMENT (HIGH) - ✅ EXCELLENT
- **Level-up with journal**: `/api/v2/characters/{id}/level-up` using journal entries
- **Enhancement system**: `/api/v2/characters/{id}/enhance` for story-driven changes
- **Character advancement**: Level-up suggestions based on play experience
- **Database integration**: Import/export existing characters

#### 9. SYSTEM ARCHITECTURE (CRITICAL) - ✅ EXCELLENT
- **LLM Integration**: Full OpenAI/Ollama support via creation_factory
- **Database Models**: Comprehensive character storage with CharacterDB
- **RESTful API**: Complete REST endpoints for all operations
- **Error Handling**: Proper exception handling and graceful fallbacks
- **Theme System**: Optional theme parameter support throughout factory system
- **Service Integration**: Campaign and backend services can optionally interface for enhanced functionality

#### 10. CONTENT VALIDATION (HIGH) - ✅ EXCELLENT
- **Character validation**: `/api/v2/validate/character` endpoint
- **External validation**: Uses creation_validation.py for consistency
- **D&D 5e compliance**: Mathematical correctness and rule validation

#### 12. CHARACTER SHEET MANAGEMENT (MEDIUM) - ✅ EXCELLENT
- **Complete sheets**: `/api/v2/characters/{id}/sheet` endpoint
- **Real-time updates**: Character state management for gameplay
- **Combat support**: HP tracking, conditions, temporary effects
- **Rest mechanics**: Short/long rest effects

### ✅ WELL SUPPORTED REQUIREMENTS

#### 6. NPC & CREATURE CREATION (MEDIUM) - ✅ GOOD
- **Factory support**: NPC and monster creation via factory endpoints
- **Challenge ratings**: Supports creature generation with appropriate CR
- **Roleplay focus**: Factory can generate NPCs with motivations and secrets

#### 7. STANDALONE ITEM CREATION (MEDIUM) - ✅ GOOD
- **Item factory**: `/api/v2/factory/create` supports weapon, armor, spell, other_item
- **Thematic consistency**: Items generated to match campaign themes
- **DM tools**: Standalone creation for DM use

#### 8. DATABASE & VERSION CONTROL (MEDIUM) - ✅ GOOD
- **Character persistence**: Full CRUD operations for characters
- **Version snapshots**: `/api/v2/characters/{id}/versions` endpoints
- **Character tracking**: Database storage with proper relationships

### ⚠️ PARTIALLY SUPPORTED REQUIREMENTS

#### 11. PERFORMANCE STANDARDS (MEDIUM) - ⚠️ PARTIAL
- **✅ Timing tracking**: Processing time included in responses
- **❌ Performance monitoring**: No explicit performance metrics endpoint
- **❌ Optimization features**: No caching or performance optimization visible

#### 13. JOURNAL & EXPERIENCE SYSTEM (LOW) - ⚠️ PARTIAL
- **✅ Journal-based leveling**: Uses journal entries for level-up decisions
- **✅ XP integration**: Level-up suggestions based on play experience
- **❌ Journal storage**: No endpoints for managing journal entries directly
- **❌ XP tracking**: No explicit experience point tracking system

### 🔧 ADDITIONAL REQUIREMENTS IDENTIFIED

#### 14. INVENTORY MANAGEMENT SYSTEM (NEW - MEDIUM)
- **Complete inventory system**: Add/remove/update character inventory items
- **Equipment slots**: Equip/unequip items to character slots
- **Attunement system**: D&D 5e attunement rules with 3-item limit
- **Item properties**: Rarity, weight, value, magical properties
- **Endpoints**: `/api/v2/characters/{id}/inventory/*` suite

#### 15. REAL-TIME GAMEPLAY SUPPORT (NEW - MEDIUM)
- **State management**: Real-time character state updates during play
- **Combat mechanics**: Apply damage, healing, conditions
- **Rest system**: Short/long rest effects and recovery
- **Live tracking**: HP, conditions, exhaustion, temporary effects
- **Endpoints**: `/api/v2/characters/{id}/state`, `/api/v2/characters/{id}/combat`, `/api/v2/characters/{id}/rest`

#### 16. COMPREHENSIVE VALIDATION SYSTEM (NEW - HIGH)
- **Character validation**: Validate character builds for D&D 5e compliance
- **Existing character checks**: Validate characters from database
- **Rule verification**: Mathematical correctness and balance checking
- **External integration**: Uses creation_validation.py for consistency
- **Endpoints**: `/api/v2/validate/character`, `/api/v2/characters/{id}/validate`

#### 17. FACTORY SYSTEM ARCHITECTURE (NEW - CRITICAL)
- **Unified creation**: Single factory pattern for all content types
- **Creation from scratch**: Generate entirely new objects
- **Evolution system**: Improve existing objects with new prompts
- **Type support**: Character, monster, NPC, weapon, armor, spell, other_item
- **Endpoints**: `/api/v2/factory/create`, `/api/v2/factory/evolve`, `/api/v2/factory/types`

#### 18. STANDALONE SERVICES ARCHITECTURE (NEW - CRITICAL)
**PRIORITY: CRITICAL**
- **Independent operation**: Backend service (`/backend`) and campaign service (`/backend_campaign`) work standalone
- **Optional integration**: When both services run, they interface for enhanced functionality
- **Service communication**: HTTP-based integration with health checks and graceful fallbacks
- **Theme propagation**: Campaign service can pass campaign themes to backend for content creation
- **No hard dependencies**: Either service can operate independently for core functionality
- **Resilient design**: Service failures don't break the other service
- **Content delegation**: Campaign service focuses on campaigns, backend service focuses on content creation

#### 19. UNIFIED CATALOG SYSTEM (NEW - HIGH)
**PRIORITY: HIGH**
- **Unified item tracking**: Centralized catalog for all items, spells, and equipment across characters
- **Smart recommendations**: Suggest appropriate items/spells based on character build and level
- **Cross-character sharing**: Allow characters to access shared catalog of available items
- **Rarity management**: Track item rarity and availability based on campaign settings
- **Custom content integration**: Seamlessly integrate custom items/spells into unified catalog

#### 20. ADVANCED SPELL MANAGEMENT (NEW - HIGH)
**PRIORITY: HIGH**
- **Spell swapping**: Allow characters to change prepared spells following D&D 5e rules
- **Spell slot tracking**: Real-time tracking of used/available spell slots by level
- **Spell progression**: Automatic spell availability as characters level up
- **Ritual tracking**: Separate tracking for ritual spells and components
- **Spell customization**: Support for custom spells with proper slot assignments
- **Known vs Prepared**: Distinguish between spells known and spells prepared for each class

#### 21. DYNAMIC EQUIPMENT MANAGEMENT (NEW - HIGH)
**PRIORITY: HIGH**
- **Equipment swapping**: Allow real-time swapping of equipped items between characters or inventory
- **Smart equipping**: Automatic optimization suggestions for equipment slots
- **Equipment synergy**: Track equipment combinations and their effects
- **Enchantment tracking**: Monitor magical item bonuses and their stacking rules
- **Equipment history**: Track when items were equipped/unequipped for session continuity
- **Slot validation**: Enforce D&D 5e equipment slot rules and restrictions

**Required Endpoints:**
- `/api/v2/catalog/*` - Unified catalog management
- `/api/v2/characters/{id}/spells/swap` - Spell swapping functionality
- `/api/v2/characters/{id}/spells/prepare` - Spell preparation management
- `/api/v2/characters/{id}/equipment/swap` - Equipment swapping
- `/api/v2/characters/{id}/equipment/optimize` - Equipment optimization suggestions

## MISSING FEATURES TO IMPLEMENT

### Performance Monitoring System
- **System metrics**: CPU, memory, database performance
- **Request tracking**: Endpoint usage, response times, error rates
- **Performance dashboard**: Real-time system health monitoring

### Journal Management System
- **Journal CRUD**: Create, read, update, delete journal entries
- **Session tracking**: Link journal entries to game sessions
- **Experience logging**: Track character development over time
- **Story integration**: Use journal data for character advancement

### Advanced Version Control
- **Git-like branching**: Character evolution trees
- **Merge conflicts**: Handle simultaneous character changes
- **Branch management**: Create, merge, delete character branches
- **Approval workflow**: DM approval for character changes

## IMPLEMENTATION PRIORITY ORDER

### ✅ COMPLETED (Phase 1)
1. **✅ Core character creation with existing D&D content**
2. **✅ Custom content generation (species, classes, items)**  
3. **✅ Iterative refinement system**
4. **✅ Character advancement and leveling**
5. **✅ NPC and creature creation**
6. **✅ Database persistence and versioning**
7. **✅ In-game play features**
8. **✅ Inventory management system**
9. **✅ Real-time gameplay support**
10. **✅ Comprehensive validation system**
11. **✅ Factory system architecture**
12. **✅ Campaign theme-driven content creation**
13. **✅ Standalone services architecture**

### 🔧 CURRENT IMPLEMENTATION (Phase 2)
14. **Performance monitoring system** (metrics endpoints, system health)
15. **Journal management system** (direct CRUD operations)  
16. **Advanced version control** (git-like branching, approval workflows)

### 📋 FUTURE ENHANCEMENTS (Phase 3)
17. **Campaign integration** (link characters to campaigns)
18. **Multi-user collaboration** (shared character editing)
19. **Export/import features** (PDF character sheets, Roll20 integration)
20. **AI-powered suggestions** (character optimization recommendations)

---

## CONTEXT FOR AI ASSISTANTS
When working on this system, remember:
- **Primary Goal**: Enable ANY character concept through creative D&D content generation
- **Balance First**: All content must be playable and balanced
- **User-Centric**: Prioritize ease of use and creative freedom
- **D&D Foundation**: Build on 5e 2024 rules while extending beyond traditional limits
- **Iterative Design**: Support collaborative character development process
- **Theme Integration**: Support campaign themes while preserving player choice
- **Service Independence**: Backend and campaign services work standalone but integrate when both available

## THEME SYSTEM USAGE EXAMPLES

### Campaign Creator Workflow
```bash
# Campaign creator specifies themes for their campaign
POST /api/v2/campaigns
{
  "title": "Wild West Adventures",
  "themes": ["western", "frontier"]
}

# When players create characters, campaign service suggests theme
POST /api/v2/factory/create
{
  "creation_type": "character",
  "prompt": "Create a gunslinger with a mysterious past",
  "theme": "western"  # Suggested by campaign, not mandatory
}
```

### Player Choice Examples
```bash
# Player accepts theme suggestion - creates western-themed character
POST /api/v2/factory/create
{
  "creation_type": "character",
  "prompt": "Create a gunslinger with a mysterious past",
  "theme": "western"
}

# Player overrides theme - creates traditional D&D character in western campaign
POST /api/v2/factory/create
{
  "creation_type": "character", 
  "prompt": "Create a traditional elven ranger with nature magic",
  "theme": "western"  # Theme present but player concept takes priority
}

# Player ignores theme entirely - still works (backward compatibility)
POST /api/v2/factory/create
{
  "creation_type": "character",
  "prompt": "Create a wizard specialist in divination magic"
  # No theme parameter - generates standard D&D content
}
```

## BACKEND How files work together:
app.py (FastAPI endpoints) 
  ↓ calls
creation_factory.py (orchestration) 
  ↓ uses
creation.py (character creation logic) ✓ WITH REFINEMENT METHODS
  ↓ depends on
- dnd_data.py (official D&D content)
- custom_content_models.py (custom content) ←→ ability_management.py
- character_models.py (data structures) ←→ ability_management.py
- core_models.py (D&D mechanics) ←→ ability_management.py (extends)
- creation_validation.py (balance checking) ←→ ability_management.py
- content_coordinator.py (complex workflows)

## CRITICAL IMPLEMENTATION STATUS

### ✅ COMPLETED: Character Refinement System
The **CharacterCreator** class now includes all required refinement methods:

1. **`refine_character()`** - Iteratively improve characters based on user feedback
2. **`level_up_character_with_journal()`** - Level up using play experiences 
3. **`enhance_existing_character()`** - Add story-driven improvements
4. **`apply_user_feedback()`** - Apply structured user feedback

**Import Status**: ✅ All backend imports fixed and working
**Architecture**: ✅ Proper module relationships established
**Core Features**: ✅ Character creation with custom content support

### 🔧 READY FOR INTEGRATION:
- **creation_factory.py** - Can now orchestrate refinement workflows
- **app.py** - Ready to expose refinement endpoints
- **Database integration** - Character versioning and iteration tracking
- **LLM integration** - Advanced prompt engineering for refinements

backend/ (Production Ready)
├── Core Application Files
│   ├── app.py (Main FastAPI app)
│   ├── main.py (Entry point)
│   └── src/ (Modular source code)
├── Container Files
│   ├── Dockerfile (Production container)
│   ├── .dockerignore (Comprehensive filtering)
│   └── requirements.txt (Production deps only)
├── Configuration
│   ├── .env (Template, no secrets)
│   └── .env.example (Documentation)
└── Documentation
    ├── README.md (Quick start)
    ├── CONTAINER_DEPLOYMENT.md (Detailed deployment)
    ├── SECURITY_AUDIT_COMPLETE.md (Security info)
    └── PRODUCTION_READY.md (Production guide)

# Build container
podman build -t dnd-char-creator .

# Run with environment variables
podman run -d \
  --name dnd-char-creator \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e SECRET_KEY="your-secret" \
  dnd-char-creator