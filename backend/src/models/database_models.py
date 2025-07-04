"""
Database models for the D&D Character Creator with Git-like versioning system.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import uuid
import logging
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.orm.attributes import flag_modified

# Configure logging
logger = logging.getLogger(__name__)


# Custom UUID type that works with SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32) storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

Base = declarative_base()

# ============================================================================
# CHARACTER VERSIONING SYSTEM (Git-like Branching)
# ============================================================================

class CharacterRepository(Base):
    """
    Represents a character's complete version history - like a Git repository.
    This is the root container for all versions/branches of a single character concept.
    """
    __tablename__ = "character_repositories"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Repository metadata
    name = Column(String(100), nullable=False, index=True)  # "Gandalf the Grey"
    description = Column(Text, nullable=True)  # "A wise wizard character with multiple storylines"
    player_name = Column(String(100), nullable=True)
    
    # Repository settings
    is_public = Column(Boolean, default=False)  # Can others see/fork this character?
    allow_forks = Column(Boolean, default=True)  # Can others create branches?
    
    # Initial character data (the "genesis" commit)
    initial_commit_hash = Column(String(64), nullable=True)  # Points to first CharacterCommit
    default_branch = Column(String(50), default="main")  # Default branch name
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branches = relationship("CharacterBranch", back_populates="repository", cascade="all, delete-orphan")
    commits = relationship("CharacterCommit", back_populates="repository", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "name": self.name,
            "description": self.description,
            "player_name": self.player_name,
            "is_public": self.is_public,
            "allow_forks": self.allow_forks,
            "initial_commit_hash": self.initial_commit_hash,
            "default_branch": self.default_branch,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "branch_count": len(self.branches) if self.branches else 0,
            "commit_count": len(self.commits) if self.commits else 0
        }


class CharacterBranch(Base):
    """
    Represents a branch of character development - like Git branches.
    Examples: "main", "multiclass-wizard", "evil-alternate", "level-20-path"
    """
    __tablename__ = "character_branches"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    
    # Branch metadata
    branch_name = Column(String(50), nullable=False, index=True)  # "main", "multiclass-path", etc.
    description = Column(Text, nullable=True)  # "Path where character becomes a wizard/fighter"
    branch_type = Column(String(20), default="development")  # "main", "development", "experimental", "alternate"
    
    # Branch pointers
    head_commit_hash = Column(String(64), nullable=True)  # Current HEAD of this branch
    parent_branch = Column(String(50), nullable=True)  # Branch this was created from
    branch_point_hash = Column(String(64), nullable=True)  # Commit where this branch started
    
    # Branch status
    is_active = Column(Boolean, default=True)
    is_merged = Column(Boolean, default=False)  # Has this branch been merged back?
    merged_into = Column(String(50), nullable=True)  # Which branch was this merged into?
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("CharacterRepository", back_populates="branches")
    commits = relationship("CharacterCommit", back_populates="branch", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "branch_name": self.branch_name,
            "description": self.description,
            "branch_type": self.branch_type,
            "head_commit_hash": self.head_commit_hash,
            "parent_branch": self.parent_branch,
            "branch_point_hash": self.branch_point_hash,
            "is_active": self.is_active,
            "is_merged": self.is_merged,
            "merged_into": self.merged_into,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "commit_count": len(self.commits) if self.commits else 0
        }


class CharacterCommit(Base):
    """
    Represents a single character state/version - like Git commits.
    Each level-up, major change, or story development creates a new commit.
    """
    __tablename__ = "character_commits"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("character_branches.id"), nullable=False)
    
    # Commit identification
    commit_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    short_hash = Column(String(8), nullable=False, index=True)  # First 8 chars for display
    
    # Commit metadata
    commit_message = Column(Text, nullable=False)  # "Level 2: Gained Action Surge"
    commit_type = Column(String(20), default="update")  # "initial", "level_up", "story", "equipment", "death", "resurrection"
    
    # Character level/progression info
    character_level = Column(Integer, nullable=False)
    experience_points = Column(Integer, default=0)
    milestone_name = Column(String(100), nullable=True)  # "Defeated the Dragon", "Learned Fireball"
    
    # Git-like relationship tracking
    parent_commit_hash = Column(String(64), nullable=True)  # Previous commit (null for initial)
    merge_parent_hash = Column(String(64), nullable=True)  # If this is a merge commit
    
    # Character data snapshot (complete character state at this point)
    character_data = Column(JSON, nullable=False)  # Full CharacterCore + CharacterState data
    
    # Change tracking
    changes_summary = Column(JSON, nullable=True)  # What changed from parent commit
    files_changed = Column(JSON, nullable=True)  # Which aspects changed (abilities, equipment, etc.)
    
    # Story/campaign context
    session_date = Column(DateTime, nullable=True)  # When this change happened in real life
    campaign_context = Column(Text, nullable=True)  # What was happening in the story
    dm_notes = Column(Text, nullable=True)  # DM notes about this character state
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)  # Who made this commit (player, DM, auto)
    
    # Relationships
    repository = relationship("CharacterRepository", back_populates="commits")
    branch = relationship("CharacterBranch", back_populates="commits")
    
    def generate_commit_hash(self) -> str:
        """Generate a unique commit hash based on character data and metadata."""
        # Create hash from character data, timestamp, and parent commit
        hash_input = f"{self.character_data}{self.commit_message}{self.created_at}{self.parent_commit_hash}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "branch_id": self.branch_id,
            "commit_hash": self.commit_hash,
            "short_hash": self.short_hash,
            "commit_message": self.commit_message,
            "commit_type": self.commit_type,
            "character_level": self.character_level,
            "experience_points": self.experience_points,
            "milestone_name": self.milestone_name,
            "parent_commit_hash": self.parent_commit_hash,
            "merge_parent_hash": self.merge_parent_hash,
            "character_data": self.character_data,
            "changes_summary": self.changes_summary,
            "files_changed": self.files_changed,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "campaign_context": self.campaign_context,
            "dm_notes": self.dm_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }


class CharacterTag(Base):
    """
    Tags for marking important commits - like Git tags.
    Examples: "v1.0-creation", "v2.0-multiclass", "v20.0-epic", "death", "resurrection"
    """
    __tablename__ = "character_tags"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    
    # Tag information
    tag_name = Column(String(50), nullable=False, index=True)  # "v1.0", "death-by-dragon", "epic-level"
    tag_type = Column(String(20), default="milestone")  # "milestone", "death", "resurrection", "retirement"
    description = Column(Text, nullable=True)
    
    # Points to specific commit
    commit_hash = Column(String(64), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "tag_name": self.tag_name,
            "tag_type": self.tag_type,
            "description": self.description,
            "commit_hash": self.commit_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }


# ============================================================================
# LEGACY CHARACTER MODEL (for backwards compatibility)
# ============================================================================

class Character(Base):
    """
    Database model for D&D characters with UUID support.
    Uses UUIDs for better scalability and security.
    Also supports the CharacterRepository versioning system.
    """
    __tablename__ = "characters"
    
    id = Column(String(36), primary_key=True, index=True)
    
    # Link to new versioning system (optional)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=True)
    commit_hash = Column(String(64), nullable=True)  # Which commit this represents
    
    # Original character fields
    name = Column(String(100), nullable=False, index=True)
    player_name = Column(String(100), nullable=True)
    
    # Character basics
    species = Column(String(50), nullable=False)
    background = Column(String(50), nullable=True)
    alignment = Column(String(20), nullable=True)
    level = Column(Integer, default=1)
    
    # Character classes (stored as JSON)
    character_classes = Column(JSON, nullable=False, default=dict)
    
    # Ability scores
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # Derived stats
    armor_class = Column(Integer, default=10)
    hit_points = Column(Integer, default=1)
    proficiency_bonus = Column(Integer, default=2)
    
    # Character data (stored as JSON for flexibility)
    equipment = Column(JSON, nullable=True, default=dict)
    features = Column(JSON, nullable=True, default=dict)
    spells = Column(JSON, nullable=True, default=dict)
    skills = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional character data
    backstory = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Approval state: 'pending', 'approved', 'rejected'
    approval_state = Column(String(20), default='pending', nullable=False)
    approval_notes = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "player_name": self.player_name,
            "species": self.species,
            "background": self.background,
            "alignment": self.alignment,
            "level": self.level,
            "character_classes": self.character_classes,
            "abilities": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "proficiency_bonus": self.proficiency_bonus,
            "equipment": self.equipment,
            "features": self.features,
            "spells": self.spells,
            "skills": self.skills,
            "backstory": self.backstory,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }
    
    # Relationships
    item_access = relationship("CharacterItemAccess", back_populates="character", cascade="all, delete-orphan")


class CharacterSession(Base):
    """Database model for character creation sessions."""
    __tablename__ = "character_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID
    character_id = Column(String(36), nullable=True)  # Links to Character if saved
    
    # Session data
    current_step = Column(String(50), default="basic_info")
    session_data = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class CustomContent(Base):
    """Database model for user-created custom content."""
    __tablename__ = "custom_content"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # "species", "class", "spell", etc.
    
    # Content data
    content_data = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # Future: user system
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

def register_custom_item(db: Session, name: str, item_type: str, description: str = "", properties: Optional[Dict[str, Any]] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom item in the CustomContent table.
    """
    item_data = {
        "name": name,
        "item_type": item_type,
        "description": description,
        "properties": properties or {},
    }
    db_item = CustomContent(
        name=name,
        content_type=item_type,
        content_data=item_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ============================================================================
# UNIFIED ITEM CATALOG SYSTEM - ALL ITEMS GET UUIDS
# ============================================================================

class UnifiedItem(Base):
    """
    Unified table for ALL items (spells, weapons, armor, equipment) - both traditional and custom.
    Every item gets a UUID for consistent tracking and relationships.
    """
    __tablename__ = "unified_items"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # 'spell', 'weapon', 'armor', 'item', 'tool', 'consumable'
    item_subtype = Column(String(50), nullable=True, index=True)  # 'simple_weapon', 'martial_weapon', 'light_armor', etc.
    source_type = Column(String(20), nullable=False, index=True)  # 'official', 'custom', or 'llm_generated'
    source_info = Column(String(500), nullable=True)  # Extra provenance or LLM prompt info
    llm_metadata = Column(JSON, nullable=True)  # LLM-specific metadata (model, prompt, etc.)
    
    # Content and properties
    content_data = Column(JSON, nullable=False)  # All item properties, stats, descriptions
    short_description = Column(String(500), nullable=True)  # Brief description for catalog views
    
    # D&D 5e specific metadata
    rarity = Column(String(20), nullable=True, index=True)  # 'common', 'uncommon', 'rare', 'very_rare', 'legendary', 'artifact'
    requires_attunement = Column(Boolean, default=False)
    spell_level = Column(Integer, nullable=True, index=True)  # For spells: 0 for cantrips, 1-9 for leveled spells
    spell_school = Column(String(30), nullable=True, index=True)  # For spells: 'evocation', 'conjuration', etc.
    class_restrictions = Column(JSON, nullable=True)  # Array of classes that can use this item ['wizard', 'sorcerer']
    
    # Economics and practical data
    value_gp = Column(Integer, nullable=True)  # Value in gold pieces
    weight_lbs = Column(String(10), nullable=True)  # Weight (can be fractional like "0.5")
    
    # Metadata and versioning
    created_by = Column(String(100), nullable=True)  # Creator (for custom items)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Most official items are public
    version = Column(Integer, default=1)  # For tracking updates to items
    
    # Source attribution
    source_book = Column(String(100), nullable=True)  # 'Player\'s Handbook 2024', 'Custom Creation', etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "item_type": self.item_type,
            "item_subtype": self.item_subtype,
            "source_type": self.source_type,
            "source_info": self.source_info,
            "llm_metadata": self.llm_metadata,
            "content_data": self.content_data,
            "short_description": self.short_description,
            "rarity": self.rarity,
            "requires_attunement": self.requires_attunement,
            "spell_level": self.spell_level,
            "spell_school": self.spell_school,
            "class_restrictions": self.class_restrictions,
            "value_gp": self.value_gp,
            "weight_lbs": self.weight_lbs,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "version": self.version,
            "source_book": self.source_book
        }


class CharacterItemAccess(Base):
    """
    Junction table tracking which items a character has access to (spells known, equipment owned, etc.).
    This replaces the old system of storing item lists directly in character data.
    """
    __tablename__ = "character_item_access"
    
    # Composite primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    item_id = Column(GUID(), ForeignKey("unified_items.id"), nullable=False, index=True)
    
    # Access type and status
    access_type = Column(String(30), nullable=False, index=True)  # 'spells_known', 'spells_prepared', 'inventory', 'equipped'
    access_subtype = Column(String(30), nullable=True)  # 'main_hand', 'off_hand', 'armor', 'attuned', etc.
    quantity = Column(Integer, default=1)  # For stackable items
    
    # Acquisition and management
    acquired_at = Column(DateTime, default=datetime.utcnow)
    acquired_method = Column(String(50), nullable=True)  # 'character_creation', 'level_up', 'purchase', 'loot', 'craft'
    is_active = Column(Boolean, default=True)  # Can be deactivated without deletion
    
    # Character-specific customization
    custom_properties = Column(JSON, nullable=True)  # Character-specific modifications to the item
    notes = Column(Text, nullable=True)  # Player notes about this specific item instance
    
    # Relationships
    character = relationship("Character", back_populates="item_access")
    item = relationship("UnifiedItem")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "character_id": str(self.character_id),
            "item_id": str(self.item_id),
            "access_type": self.access_type,
            "access_subtype": self.access_subtype,
            "quantity": self.quantity,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "acquired_method": self.acquired_method,
            "is_active": self.is_active,
            "custom_properties": self.custom_properties,
            "notes": self.notes,
            "item": self.item.to_dict() if self.item else None
        }

def register_custom_npc(db: Session, name: str, npc_type: str, description: str = "", stats: Optional[Dict[str, Any]] = None, challenge_rating: Optional[float] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom NPC in the CustomContent table, with CR support.
    """
    if stats is None:
        stats = {}
    if challenge_rating is not None:
        stats["challenge_rating"] = challenge_rating
    npc_data = {
        "name": name,
        "npc_type": npc_type,
        "description": description,
        "stats": stats,
        "challenge_rating": stats.get("challenge_rating"),
    }
    db_npc = CustomContent(
        name=name,
        content_type="npc",
        content_data=npc_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_npc)
    db.commit()
    db.refresh(db_npc)
    return db_npc

def register_custom_creature(db: Session, name: str, creature_type: str, description: str = "", stat_block: Optional[Dict[str, Any]] = None, challenge_rating: Optional[float] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom creature in the CustomContent table, with CR support.
    """
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
    db_creature = CustomContent(
        name=name,
        content_type="creature",
        content_data=creature_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_creature)
    db.commit()
    db.refresh(db_creature)
    return db_creature

# ============================================================================
# CONTENT CATALOG TABLES - FOR SPELL/EQUIPMENT MANAGEMENT
# ============================================================================

class SpellCatalog(Base):
    """
    Database model for all spells (traditional D&D and custom/generated).
    Provides a unified catalog for spell management and character assignment.
    """
    __tablename__ = "spell_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Spell properties
    level = Column(Integer, nullable=False, index=True)  # 0-9 (0 = cantrip)
    school = Column(String(50), nullable=False, index=True)  # evocation, illusion, etc.
    casting_time = Column(String(100), nullable=False)
    spell_range = Column(String(100), nullable=False)
    components = Column(String(200), nullable=False)  # V, S, M
    duration = Column(String(100), nullable=False)
    concentration = Column(Boolean, default=False)
    ritual = Column(Boolean, default=False)
    
    # Content
    description = Column(Text, nullable=False)
    higher_levels = Column(Text, nullable=True)  # At higher levels description
    
    # Class compatibility (JSON array of class names)
    compatible_classes = Column(JSON, nullable=False, default=list)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom spells
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Custom spell theme (for generated spells)
    spell_theme = Column(String(50), nullable=True)  # "void", "fire", "nature", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert spell to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "casting_time": self.casting_time,
            "range": self.spell_range,
            "components": self.components,
            "duration": self.duration,
            "concentration": self.concentration,
            "ritual": self.ritual,
            "description": self.description,
            "higher_levels": self.higher_levels,
            "compatible_classes": self.compatible_classes,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "spell_theme": self.spell_theme
        }


class WeaponCatalog(Base):
    """
    Database model for all weapons (traditional D&D and custom/generated).
    Provides a unified catalog for weapon management and character assignment.
    """
    __tablename__ = "weapon_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Weapon properties
    weapon_type = Column(String(50), nullable=False, index=True)  # "simple", "martial"
    weapon_category = Column(String(50), nullable=False, index=True)  # "melee", "ranged"
    damage_dice = Column(String(20), nullable=False)  # "1d8", "2d6", etc.
    damage_type = Column(String(20), nullable=False)  # "slashing", "piercing", "bludgeoning"
    
    # Optional properties (JSON array)
    properties = Column(JSON, nullable=False, default=list)  # ["finesse", "light", "versatile"]
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "15 gp", "2 sp", etc.
    
    # Range (for ranged weapons)
    range_normal = Column(Integer, nullable=True)  # normal range in feet
    range_long = Column(Integer, nullable=True)    # long range in feet
    
    # Versatile damage (for versatile weapons)
    versatile_damage = Column(String(20), nullable=True)  # "1d10" for longsword
    
    # Description and lore
    description = Column(Text, nullable=True)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom weapons
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weapon to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "weapon_type": self.weapon_type,
            "weapon_category": self.weapon_category,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type,
            "properties": self.properties,
            "weight": self.weight,
            "cost": self.cost,
            "range_normal": self.range_normal,
            "range_long": self.range_long,
            "versatile_damage": self.versatile_damage,
            "description": self.description,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


class ArmorCatalog(Base):
    """
    Database model for all armor (traditional D&D and custom/generated).
    Provides a unified catalog for armor management and character assignment.
    """
    __tablename__ = "armor_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Armor properties
    armor_type = Column(String(20), nullable=False, index=True)  # "light", "medium", "heavy", "shield"
    armor_class = Column(String(20), nullable=False)  # "11 + Dex mod", "18", etc.
    
    # Requirements and limitations
    strength_requirement = Column(Integer, nullable=True)  # Minimum Str for heavy armor
    stealth_disadvantage = Column(Boolean, default=False)
    max_dex_bonus = Column(Integer, nullable=True)  # For medium/heavy armor
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "1,500 gp", "10 gp", etc.
    
    # Description and lore
    description = Column(Text, nullable=True)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom armor
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "armor_type": self.armor_type,
            "armor_class": self.armor_class,
            "strength_requirement": self.strength_requirement,
            "stealth_disadvantage": self.stealth_disadvantage,
            "max_dex_bonus": self.max_dex_bonus,
            "weight": self.weight,
            "cost": self.cost,
            "description": self.description,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


class ItemCatalog(Base):
    """
    Database model for all other items (adventuring gear, tools, etc.).
    Provides a unified catalog for general item management and character assignment.
    """
    __tablename__ = "item_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Item properties
    item_type = Column(String(50), nullable=False, index=True)  # "tool", "consumable", "magic_item", etc.
    item_category = Column(String(50), nullable=True, index=True)  # "artisan_tools", "potion", etc.
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "25 gp", "2 sp", etc.
    
    # Usage and properties
    properties = Column(JSON, nullable=False, default=dict)  # Flexible properties storage
    uses_per_day = Column(Integer, nullable=True)  # For limited-use items
    charges = Column(Integer, nullable=True)  # For charged items
    
    # Description and mechanics
    description = Column(Text, nullable=True)
    mechanical_effect = Column(Text, nullable=True)  # Game mechanics description
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, DMG, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom items
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type,
            "item_category": self.item_category,
            "weight": self.weight,
            "cost": self.cost,
            "properties": self.properties,
            "uses_per_day": self.uses_per_day,
            "charges": self.charges,
            "description": self.description,
            "mechanical_effect": self.mechanical_effect,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


# ============================================================================
# CHARACTER-CONTENT RELATIONSHIP TABLES
# ============================================================================

class CharacterSpellAccess(Base):
    """
    Many-to-many relationship table for character spell access.
    Tracks which spells a character has access to and their status.
    """
    __tablename__ = "character_spell_access"
    
    id = Column(String(36), primary_key=True, index=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    spell_id = Column(String(36), ForeignKey("spell_catalog.id"), nullable=False, index=True)
    
    # Status tracking
    is_known = Column(Boolean, default=False)      # Spell is in character's known spells
    is_prepared = Column(Boolean, default=False)   # Spell is currently prepared
    is_favorite = Column(Boolean, default=False)   # Player-marked favorite
    
    # Learning information
    learned_at_level = Column(Integer, nullable=True)  # Level when spell was learned
    learned_from = Column(String(100), nullable=True)  # "level_up", "scroll", "tutor", etc.
    
    # Custom spell list assignment (for themed spellcasters)
    spell_list_category = Column(String(50), nullable=True)  # "known", "custom_void", "custom_fire", etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert spell access to dictionary format."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "spell_id": self.spell_id,
            "is_known": self.is_known,
            "is_prepared": self.is_prepared,
            "is_favorite": self.is_favorite,
            "learned_at_level": self.learned_at_level,
            "learned_from": self.learned_from,
            "spell_list_category": self.spell_list_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CharacterEquipmentAccess(Base):
    """
    Many-to-many relationship table for character equipment access.
    Tracks which equipment a character owns and their status.
    """
    __tablename__ = "character_equipment_access"
    
    id = Column(String(36), primary_key=True, index=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    
    # Equipment can be from any catalog
    weapon_id = Column(String(36), ForeignKey("weapon_catalog.id"), nullable=True, index=True)
    armor_id = Column(String(36), ForeignKey("armor_catalog.id"), nullable=True, index=True)
    item_id = Column(String(36), ForeignKey("item_catalog.id"), nullable=True, index=True)
    
    # Status tracking
    quantity = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    is_attuned = Column(Boolean, default=False)  # For magical items
    is_favorite = Column(Boolean, default=False)  # Player-marked favorite
    
    # Equipment slot (for equipped items)
    equipment_slot = Column(String(50), nullable=True)  # "main_hand", "armor", "boots", etc.
    
    # Acquisition information
    acquired_at_level = Column(Integer, nullable=True)  # Level when item was acquired
    acquired_from = Column(String(100), nullable=True)  # "starting_equipment", "loot", "purchase", etc.
    
    # Condition and notes
    condition = Column(String(20), default="normal")  # "normal", "damaged", "broken", etc.
    notes = Column(Text, nullable=True)  # Player notes about the item
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment access to dictionary format."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "weapon_id": self.weapon_id,
            "armor_id": self.armor_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "is_equipped": self.is_equipped,
            "is_attuned": self.is_attuned,
            "is_favorite": self.is_favorite,
            "equipment_slot": self.equipment_slot,
            "acquired_at_level": self.acquired_at_level,
            "acquired_from": self.acquired_from,
            "condition": self.condition,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

# ============================================================================
# DATABASE ACCESS LAYER - CRUD OPERATIONS
# ============================================================================
"""
This section addresses the comments about database access patterns:

ARCHITECTURE OVERVIEW:
- Database models (Character, CharacterSession, CustomContent) define the schema
- CharacterDB class provides all database operations with proper error handling
- Integration with character_models.py CharacterSheet class for gameplay
- Session management for character creation workflows

OPERATION FLOW:
1. CREATE NEW CHARACTER: CharacterSheet -> CharacterDB.save_character_sheet() -> Database
2. UPDATE EXISTING: Database -> CharacterDB.load_character_sheet() -> modify -> save back
3. IN-GAME PLAY: Load -> use getter/setter methods -> real-time updates -> save back

ACCESS PATTERNS:
- All database access goes through CharacterDB static methods
- Database sessions are properly managed with get_db() context manager
- Character data is converted between CharacterSheet objects and database models
- Supports both direct database operations and CharacterSheet integration
"""

# Database connection setup (to be configured in main app)
engine = None
SessionLocal = None

def init_database(database_url: str):
    """Initialize database connection."""
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# CHARACTER DATABASE OPERATIONS
# ============================================================================

class CharacterDB:
    """
    Database access layer for character operations.
    
    Order of operations:
    1) Create new character -> save to database
    2) Load existing character from database -> update -> save back
    3) Import for in-game play -> use getter/setter methods -> save back
    """
    
    @staticmethod
    def create_character(db: Session, character_data: Dict[str, Any]) -> Character:
        """Create a new character in the database."""
        db_character = Character(
            id=str(uuid.uuid4()),  # Generate UUID for new character
            name=character_data.get("name", ""),
            player_name=character_data.get("player_name"),
            species=character_data.get("species", ""),
            background=character_data.get("background"),
            alignment=character_data.get("alignment"),
            level=character_data.get("level", 1),
            character_classes=character_data.get("character_classes", {}),
            strength=character_data.get("abilities", {}).get("strength", 10),
            dexterity=character_data.get("abilities", {}).get("dexterity", 10),
            constitution=character_data.get("abilities", {}).get("constitution", 10),
            intelligence=character_data.get("abilities", {}).get("intelligence", 10),
            wisdom=character_data.get("abilities", {}).get("wisdom", 10),
            charisma=character_data.get("abilities", {}).get("charisma", 10),
            armor_class=character_data.get("armor_class", 10),
            hit_points=character_data.get("hit_points", 1),
            proficiency_bonus=character_data.get("proficiency_bonus", 2),
            equipment=character_data.get("equipment", {}),
            features=character_data.get("features", {}),
            spells=character_data.get("spells", {}),
            skills=character_data.get("skills", {}),
            backstory=character_data.get("backstory"),
            notes=character_data.get("notes")
        )
        
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def get_character(db: Session, character_id: str) -> Optional[Character]:
        """Retrieve a character from the database."""
        try:
            # character_id is now a string UUID, use it directly
            return db.query(Character).filter(Character.id == character_id, Character.is_active == True).first()
        except Exception:
            # Invalid UUID format or other error
            return None
    
    @staticmethod
    def get_character_by_name(db: Session, name: str, player_name: str = None) -> Optional[Character]:
        """Retrieve a character by name and optionally player name."""
        query = db.query(Character).filter(Character.name == name, Character.is_active == True)
        if player_name:
            query = query.filter(Character.player_name == player_name)
        return query.first()
    
    @staticmethod
    def update_character(db: Session, character_id: str, updates: Dict[str, Any]) -> Optional[Character]:
        """Update an existing character in the database."""
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return None
        
        # Update character fields with provided data
        for key, value in updates.items():
            if hasattr(db_character, key):
                setattr(db_character, key, value)
        
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def delete_character(db: Session, character_id: str) -> bool:
        """Soft delete a character (set is_active = False)."""
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return False
        
        db_character.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def list_characters(db: Session, player_name: str = None, limit: int = 50, offset: int = 0) -> List[Character]:
        """List characters with optional filtering."""
        query = db.query(Character).filter(Character.is_active == True)
        
        if player_name:
            query = query.filter(Character.player_name == player_name)
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def save_character_sheet(db: Session, character_sheet, character_id: str = None) -> Character:
        """
        Save a CharacterSheet object to the database.
        This bridges the gap between the new character models and database storage.
        """
        # Type check to prevent dict attribute errors
        if isinstance(character_sheet, dict):
            logger.error(f"save_character_sheet received a dict instead of CharacterSheet object: {character_sheet}")
            raise ValueError("Expected CharacterSheet object, got dict. Please pass a properly constructed CharacterSheet.")
        
        if not hasattr(character_sheet, 'core'):
            logger.error(f"save_character_sheet received object without 'core' attribute. Type: {type(character_sheet)}")
            raise ValueError("Object passed to save_character_sheet must have a 'core' attribute")
        
        # Convert CharacterSheet to flat database format
        character_data = {
            # Core character data
            "name": character_sheet.core.name,
            "species": character_sheet.core.species,
            "background": character_sheet.core.background,
            "alignment": " ".join(character_sheet.core.alignment) if isinstance(character_sheet.core.alignment, list) else character_sheet.core.alignment,
            "level": character_sheet.core.level,
            "character_classes": character_sheet.core.character_classes,
            "backstory": character_sheet.core.backstory,
            
            # Ability scores
            "strength": character_sheet.core.strength.total_score,
            "dexterity": character_sheet.core.dexterity.total_score,
            "constitution": character_sheet.core.constitution.total_score,
            "intelligence": character_sheet.core.intelligence.total_score,
            "wisdom": character_sheet.core.wisdom.total_score,
            "charisma": character_sheet.core.charisma.total_score,
            
            # Calculated stats
            "armor_class": character_sheet.stats.armor_class,
            "hit_points": character_sheet.stats.max_hit_points,
            "proficiency_bonus": character_sheet.stats.proficiency_bonus,
            "skills": character_sheet.stats.skills,
        }
        
        # Use provided character_id or try to get from character sheet
        char_id = character_id or getattr(character_sheet.core, 'id', None)
        
        if char_id:
            return CharacterDB.update_character(db, char_id, character_data)
        else:
            return CharacterDB.create_character(db, character_data)
    
    @staticmethod
    def load_character_sheet(db: Session, character_id: str):
        """
        Load a character from database and convert to CharacterSheet object with allocated items.
        Returns None if character not found.
        """
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return None
        
        # Import here to avoid circular imports
        from src.models.character_models import CharacterSheet, CharacterCore, CharacterState
        from src.services.unified_catalog_service import UnifiedCatalogService
        
        # Create a full CharacterSheet instead of just CharacterCore
        character_sheet = CharacterSheet(db_character.name)
        
        # Set core character data
        character_sheet.core.species = db_character.species
        character_sheet.core.background = db_character.background or ""
        character_sheet.core.alignment = db_character.alignment.split() if db_character.alignment else ["Neutral", "Neutral"]
        character_sheet.core.character_classes = db_character.character_classes or {}
        character_sheet.core.backstory = db_character.backstory or ""
        
        # Set ability scores
        character_sheet.core.strength.base_score = db_character.strength
        character_sheet.core.dexterity.base_score = db_character.dexterity
        character_sheet.core.constitution.base_score = db_character.constitution
        character_sheet.core.intelligence.base_score = db_character.intelligence
        character_sheet.core.wisdom.base_score = db_character.wisdom
        character_sheet.core.charisma.base_score = db_character.charisma
        
        # Store database ID for future saves
        character_sheet.core.id = db_character.id
        
        # Load allocated items from unified catalog
        try:
            catalog_service = UnifiedCatalogService(db)
            
            # Get spells
            character_spells = catalog_service.get_character_spells(character_id)
            character_sheet.state.allocated_spells = character_spells
            
            # Get equipment
            character_equipment = catalog_service.get_character_equipment(character_id)
            character_sheet.state.allocated_equipment = character_equipment
            
            # Get all allocations for comprehensive view
            all_allocations = catalog_service.get_character_allocations(character_id)
            character_sheet.state.all_allocated_items = all_allocations
            
        except Exception as e:
            # Log error but don't fail the entire load
            logger.error(f"Failed to load allocated items for character {character_id}: {e}")
            character_sheet.state.allocated_spells = {"spells_known": [], "spells_prepared": []}
            character_sheet.state.allocated_equipment = {"inventory": [], "equipped": []}
            character_sheet.state.all_allocated_items = []
        
        return character_sheet
    
    # ============================================================================
    # INVENTORY MANAGEMENT METHODS
    # ============================================================================
    
    @staticmethod
    def get_inventory(db: Session, character_id: str) -> List[Dict[str, Any]]:
        """Get character's inventory items."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return []
        
        # Extract inventory from equipment JSON field
        equipment_data = character.equipment or {}
        return equipment_data.get("inventory", [])
    
    @staticmethod
    def add_inventory_item(db: Session, character_id: str, item_data: Dict[str, Any]) -> bool:
        """Add an item to character's inventory."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return False
        
        # Initialize equipment if it doesn't exist
        if not character.equipment:
            character.equipment = {}
        
        # Initialize inventory list if it doesn't exist
        if "inventory" not in character.equipment:
            character.equipment["inventory"] = []
        
        # Add timestamp and unique ID to item
        item_data["added_at"] = datetime.utcnow().isoformat()
        item_data["item_id"] = str(uuid.uuid4())
        
        # Add item to inventory
        character.equipment["inventory"].append(item_data)
        
        # Mark the JSON field as modified (SQLAlchemy doesn't auto-detect JSON changes)
        flag_modified(character, "equipment")
        
        db.commit()
        db.refresh(character)
        return True
    
    @staticmethod
    def update_inventory_item(db: Session, character_id: str, item_name: str, updates: Dict[str, Any]) -> bool:
        """Update an existing inventory item."""
        character = CharacterDB.get_character(db, character_id)
        if not character or not character.equipment:
            return False
        
        inventory = character.equipment.get("inventory", [])
        
        # Find item by name
        for item in inventory:
            if item.get("name") == item_name:
                # Update item fields
                for key, value in updates.items():
                    if value is not None:  # Only update non-None values
                        item[key] = value
                
                item["updated_at"] = datetime.utcnow().isoformat()
                
                # Mark the JSON field as modified
                flag_modified(character, "equipment")
                
                db.commit()
                db.refresh(character)
                return True
        
        return False  # Item not found
    
    @staticmethod
    def remove_inventory_item(db: Session, character_id: str, item_name: str) -> bool:
        """Remove an item from character's inventory."""
        character = CharacterDB.get_character(db, character_id)
        if not character or not character.equipment:
            return False
        
        inventory = character.equipment.get("inventory", [])
        
        # Find and remove item by name
        for i, item in enumerate(inventory):
            if item.get("name") == item_name:
                inventory.pop(i)
                
                # Mark the JSON field as modified
                flag_modified(character, "equipment")
                
                db.commit()
                db.refresh(character)
                return True
        
        return False  # Item not found
    
    @staticmethod
    def get_equipped_items(db: Session, character_id: str) -> Dict[str, str]:
        """Get character's equipped items."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return {}
        
        equipment_data = character.equipment or {}
        return equipment_data.get("equipped_items", {})
    
    @staticmethod
    def equip_item(db: Session, character_id: str, item_name: str, slot: str) -> bool:
        """Equip an item to a specific slot."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return False
        
        # Initialize equipment if it doesn't exist
        if not character.equipment:
            character.equipment = {}
        
        # Initialize equipped_items if it doesn't exist
        if "equipped_items" not in character.equipment:
            character.equipment["equipped_items"] = {}
        
        # Equip the item
        character.equipment["equipped_items"][slot] = item_name
        
        # Mark the JSON field as modified
        flag_modified(character, "equipment")
        
        db.commit()
        db.refresh(character)
        return True
    
    @staticmethod
    def unequip_item(db: Session, character_id: str, slot: str) -> bool:
        """Unequip an item from a specific slot."""
        character = CharacterDB.get_character(db, character_id)
        if not character or not character.equipment:
            return False
        
        equipped_items = character.equipment.get("equipped_items", {})
        
        if slot in equipped_items:
            del equipped_items[slot]
            
            # Mark the JSON field as modified
            flag_modified(character, "equipment")
            
            db.commit()
            db.refresh(character)
            return True
        
        return False  # Slot not equipped
    
    @staticmethod
    def get_attuned_items(db: Session, character_id: str) -> List[str]:
        """Get character's attuned items."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return []
        
        equipment_data = character.equipment or {}
        return equipment_data.get("attuned_items", [])
    
    @staticmethod
    def add_attuned_item(db: Session, character_id: str, item_name: str) -> bool:
        """Add an item to attuned items (max 3). Only items that require attunement can be attuned."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return False
        
        # Initialize equipment if it doesn't exist
        if not character.equipment:
            character.equipment = {}
        
        # Initialize attuned_items if it doesn't exist
        if "attuned_items" not in character.equipment:
            character.equipment["attuned_items"] = []
        
        # Check if the item exists in inventory and requires attunement
        inventory = character.equipment.get("inventory", [])
        item_found = False
        requires_attunement = False
        
        for item in inventory:
            if item.get("name") == item_name:
                item_found = True
                requires_attunement = item.get("requires_attunement", False)
                break
        
        if not item_found:
            logger.warning(f"Item {item_name} not found in character's inventory")
            return False
        
        if not requires_attunement:
            logger.warning(f"Item {item_name} does not require attunement")
            return False
        
        attuned_items = character.equipment["attuned_items"]
        
        # Check attunement limit (D&D 5e limit is 3)
        if len(attuned_items) >= 3:
            return False
        
        # Check if already attuned
        if item_name in attuned_items:
            return False
        
        # Add to attuned items
        attuned_items.append(item_name)
        
        # Mark the JSON field as modified
        flag_modified(character, "equipment")
        
        db.commit()
        db.refresh(character)
        return True
    
    @staticmethod
    def remove_attuned_item(db: Session, character_id: str, item_name: str) -> bool:
        """Remove an item from attuned items."""
        character = CharacterDB.get_character(db, character_id)
        if not character or not character.equipment:
            return False
        
        attuned_items = character.equipment.get("attuned_items", [])
        
        if item_name in attuned_items:
            attuned_items.remove(item_name)
            
            # Mark the JSON field as modified
            flag_modified(character, "equipment")
            
            db.commit()
            db.refresh(character)
            return True
        
        return False
    
    @staticmethod
    def get_attunement_info(db: Session, character_id: str) -> Dict[str, Any]:
        """Get detailed attunement information for a character."""
        character = CharacterDB.get_character(db, character_id)
        if not character:
            return {"error": "Character not found"}
        
        equipment_data = character.equipment or {}
        attuned_items = equipment_data.get("attuned_items", [])
        inventory = equipment_data.get("inventory", [])
        
        # Categorize inventory items by attunement status
        attuned_item_details = []
        attuneable_items = []
        non_attuneable_items = []
        
        for item in inventory:
            item_name = item.get("name", "Unknown Item")
            requires_attunement = item.get("requires_attunement", False)
            is_attuned = item_name in attuned_items
            
            item_info = {
                "name": item_name,
                "rarity": item.get("rarity", "common"),
                "requires_attunement": requires_attunement,
                "is_attuned": is_attuned,
                "description": item.get("description", "")
            }
            
            if is_attuned:
                attuned_item_details.append(item_info)
            elif requires_attunement:
                attuneable_items.append(item_info)
            else:
                non_attuneable_items.append(item_info)
        
        return {
            "character_id": character_id,
            "attunement_slots_used": len(attuned_items),
            "attunement_slots_available": max(0, 3 - len(attuned_items)),
            "max_attunement_slots": 3,
            "attuned_items": attuned_item_details,
            "attuneable_items": attuneable_items,
            "non_attuneable_items": non_attuneable_items,
            "can_attune_more": len(attuned_items) < 3,
            "rules": {
                "attunement_limit": 3,
                "attunement_process": "Requires a short rest (1 hour) while focusing on the item",
                "breaking_attunement": "Can be done instantly at any time",
                "note": "Only magic items that specifically require attunement can be attuned to"
            }
        }
    
    # ============================================================================
    # UNIFIED ITEM CATALOG OPERATIONS
    # ============================================================================
    
    @staticmethod
    def create_unified_item(db: Session, item_data: Dict[str, Any]) -> UnifiedItem:
        """Create a new unified item (spell, weapon, armor, etc.) in the catalog."""
        db_item = UnifiedItem(
            name=item_data["name"],
            item_type=item_data["item_type"],
            item_subtype=item_data.get("item_subtype"),
            source_type=item_data.get("source_type", "custom"),
            content_data=item_data["content_data"],
            short_description=item_data.get("short_description"),
            rarity=item_data.get("rarity"),
            requires_attunement=item_data.get("requires_attunement", False),
            spell_level=item_data.get("spell_level"),
            spell_school=item_data.get("spell_school"),
            class_restrictions=item_data.get("class_restrictions"),
            value_gp=item_data.get("value_gp"),
            weight_lbs=item_data.get("weight_lbs"),
            created_by=item_data.get("created_by"),
            is_public=item_data.get("is_public", True),
            source_book=item_data.get("source_book")
        )
        
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    
    @staticmethod
    def get_unified_item(db: Session, item_id: str) -> Optional[UnifiedItem]:
        """Get a unified item by its UUID."""
        try:
            return db.query(UnifiedItem).filter(UnifiedItem.id == item_id, UnifiedItem.is_active == True).first()
        except Exception as e:
            logger.error(f"Failed to get unified item {item_id}: {e}")
            return None
    
    @staticmethod
    def search_unified_items(db: Session, 
                           item_type: Optional[str] = None,
                           source_type: Optional[str] = None,
                           spell_level: Optional[int] = None,
                           spell_school: Optional[str] = None,
                           rarity: Optional[str] = None,
                           class_restrictions: Optional[List[str]] = None,
                           search_text: Optional[str] = None,
                           limit: int = 100) -> List[UnifiedItem]:
        """Search unified items catalog with filters."""
        try:
            query = db.query(UnifiedItem).filter(UnifiedItem.is_active == True)
            
            # Apply filters
            if item_type:
                query = query.filter(UnifiedItem.item_type == item_type)
            if source_type:
                query = query.filter(UnifiedItem.source_type == source_type)
            if spell_level is not None:
                query = query.filter(UnifiedItem.spell_level == spell_level)
            if spell_school:
                query = query.filter(UnifiedItem.spell_school == spell_school)
            if rarity:
                query = query.filter(UnifiedItem.rarity == rarity)
            if search_text:
                query = query.filter(UnifiedItem.name.ilike(f"%{search_text}%"))
            
            # Class restrictions filter (if item has restrictions, check if any match)
            if class_restrictions:
                # This is a complex JSON query - for now, fetch all and filter in Python
                # In production, you'd want a proper JSON query
                pass
            
            return query.limit(limit).all()
        except Exception as e:
            logger.error(f"Failed to search unified items: {e}")
            return []
    
    @staticmethod
    def add_character_item_access(db: Session, character_id: str, item_id: str, 
                                access_type: str, access_subtype: Optional[str] = None,
                                quantity: int = 1, acquired_method: Optional[str] = None) -> CharacterItemAccess:
        """Add an item to a character's access list (spells known, inventory, etc.)."""
        db_access = CharacterItemAccess(
            character_id=character_id,
            item_id=item_id,
            access_type=access_type,
            access_subtype=access_subtype,
            quantity=quantity,
            acquired_method=acquired_method or "manual"
        )
        
        db.add(db_access)
        db.commit()
        db.refresh(db_access)
        return db_access
    
    @staticmethod
    def get_character_item_access(db: Session, character_id: str, 
                                access_type: Optional[str] = None) -> List[CharacterItemAccess]:
        """Get all items a character has access to, optionally filtered by access type."""
        try:
            query = db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.is_active == True
            )
            
            if access_type:
                query = query.filter(CharacterItemAccess.access_type == access_type)
            
            return query.all()
        except Exception as e:
            logger.error(f"Failed to get character item access for {character_id}: {e}")
            return []
    
    @staticmethod
    def remove_character_item_access(db: Session, character_id: str, item_id: str, 
                                   access_type: Optional[str] = None) -> bool:
        """Remove an item from a character's access list."""
        try:
            query = db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == item_id
            )
            
            if access_type:
                query = query.filter(CharacterItemAccess.access_type == access_type)
            
            access_records = query.all()
            for record in access_records:
                db.delete(record)
            
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to remove character item access: {e}")
            return False
    
    @staticmethod
    def update_character_item_access(db: Session, access_id: str, 
                                   update_data: Dict[str, Any]) -> Optional[CharacterItemAccess]:
        """Update a character's item access record."""
        try:
            access_record = db.query(CharacterItemAccess).filter(CharacterItemAccess.id == access_id).first()
            if not access_record:
                return None
            
            # Update allowed fields
            for field, value in update_data.items():
                if hasattr(access_record, field):
                    setattr(access_record, field, value)
            
            db.commit()
            db.refresh(access_record)
            return access_record
        except Exception as e:
            logger.error(f"Failed to update character item access {access_id}: {e}")
            return None
    
    # ============================================================================
# CHARACTER SESSION OPERATIONS
# ============================================================================

class CharacterSessionDB:
    """Database operations for character creation sessions."""
    
    @staticmethod
    def create_session(db: Session, session_id: str, initial_data: Dict[str, Any] = None) -> CharacterSession:
        """Create a new character creation session."""
        session = CharacterSession(
            session_id=session_id,
            session_data=initial_data or {},
            current_step="basic_info"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[CharacterSession]:
        """Get a character creation session."""
        return db.query(CharacterSession).filter(
            CharacterSession.session_id == session_id,
            CharacterSession.is_active == True
        ).first()
    
    @staticmethod
    def update_session(db: Session, session_id: str, updates: Dict[str, Any]) -> Optional[CharacterSession]:
        """Update a character creation session."""
        session = CharacterSessionDB.get_session(db, session_id)
        if not session:
            return None
        
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        db.commit()
        db.refresh(session)
        return session


# ============================================================================
# CHARACTER REPOSITORY MANAGER - GIT-LIKE OPERATIONS
# ============================================================================

class CharacterRepositoryManager:
    """
    High-level manager for Git-like character versioning operations.
    
    This class provides convenient methods for:
    - Creating and managing character repositories
    - Branch operations (create, merge, list)
    - Commit operations (create, retrieve, compare)
    - Character state management across versions
    """
    
    @staticmethod
    def create_repository(db: Session, name: str, description: str = None, 
                         player_name: str = None, initial_character_data: Dict[str, Any] = None) -> CharacterRepository:
        """
        Create a new character repository with initial commit.
        
        Args:
            db: Database session
            name: Repository name (character name)
            description: Repository description
            player_name: Player name
            initial_character_data: Initial character state
            
        Returns:
            CharacterRepository: Created repository
        """
        # Create repository
        repo = CharacterRepository(
            id=str(uuid.uuid4()),  # Generate UUID for new repository
            name=name,
            description=description,
            player_name=player_name
        )
        db.add(repo)
        db.flush()  # Get the ID
        
        # Create main branch
        main_branch = CharacterBranch(
            id=str(uuid.uuid4()),  # Generate UUID for main branch
            repository_id=repo.id,
            branch_name="main",
            description="Main character development branch",
            branch_type="main"
        )
        db.add(main_branch)
        db.flush()
        
        # Create initial commit if character data provided
        if initial_character_data:
            initial_commit = CharacterRepositoryManager.create_commit(
                db=db,
                repository_id=repo.id,
                branch_name="main",
                commit_message="Initial character creation",
                character_data=initial_character_data,
                character_level=initial_character_data.get("level", 1),
                commit_type="initial"
            )
            repo.initial_commit_hash = initial_commit.commit_hash
            main_branch.head_commit_hash = initial_commit.commit_hash
        
        db.commit()
        return repo
    
    @staticmethod
    def create_branch(db: Session, repository_id: str, branch_name: str, 
                     description: str = None, parent_branch: str = "main",
                     branch_point_hash: str = None) -> CharacterBranch:
        """
        Create a new development branch.
        
        Args:
            db: Database session
            repository_id: Repository ID
            branch_name: New branch name
            description: Branch description
            parent_branch: Branch to create from
            branch_point_hash: Specific commit to branch from
            
        Returns:
            CharacterBranch: Created branch
        """
        # character_id is now a string UUID, use it directly
        # Get parent branch info
        parent = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id,
            CharacterBranch.branch_name == parent_branch
        ).first()
        
        if not parent:
            raise ValueError(f"Parent branch '{parent_branch}' not found")
        
        # Use parent's head commit if no specific branch point
        if not branch_point_hash:
            branch_point_hash = parent.head_commit_hash
        
        # Create new branch
        branch = CharacterBranch(
            id=str(uuid.uuid4()),  # Generate UUID for new branch
            repository_id=repository_id,
            branch_name=branch_name,
            description=description,
            parent_branch=parent_branch,
            branch_point_hash=branch_point_hash,
            head_commit_hash=branch_point_hash  # Start at branch point
        )
        
        db.add(branch)
        db.commit()
        return branch
    
    @staticmethod
    def create_commit(db: Session, repository_id: str, branch_name: str,
                     commit_message: str, character_data: Dict[str, Any],
                     character_level: int, commit_type: str = "update",
                     milestone_name: str = None, session_date: datetime = None,
                     campaign_context: str = None, created_by: str = None) -> CharacterCommit:
        """
        Create a new character commit.
        
        Args:
            db: Database session
            repository_id: Repository ID
            branch_name: Target branch
            commit_message: Commit message
            character_data: Character state data
            character_level: Character level
            commit_type: Type of commit (initial, level_up, story, etc.)
            milestone_name: Milestone name
            session_date: Game session date
            campaign_context: Campaign context
            created_by: Creator name
            
        Returns:
            CharacterCommit: Created commit
        """
        # repository_id is now a string UUID, use it directly
        # Get branch
        branch = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id,
            CharacterBranch.branch_name == branch_name
        ).first()
        
        if not branch:
            raise ValueError(f"Branch '{branch_name}' not found")
        
        # Generate commit hash
        import time
        hash_input = f"{character_data}{commit_message}{time.time()}{branch.head_commit_hash}"
        commit_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        short_hash = commit_hash[:8]
        
        # Create commit
        commit = CharacterCommit(
            id=str(uuid.uuid4()),  # Generate UUID for new commit
            repository_id=repository_id,
            branch_id=branch.id,
            commit_hash=commit_hash,
            short_hash=short_hash,
            commit_message=commit_message,
            commit_type=commit_type,
            character_level=character_level,
            character_data=character_data,
            parent_commit_hash=branch.head_commit_hash,
            milestone_name=milestone_name,
            session_date=session_date,
            campaign_context=campaign_context,
            created_by=created_by
        )
        
        db.add(commit)
        
        # Update branch head
        branch.head_commit_hash = commit_hash
        branch.updated_at = datetime.utcnow()
        
        db.commit()
        return commit
    
    @staticmethod
    def get_commit_history(db: Session, repository_id: str, branch_name: str = None,
                          limit: int = 50) -> List[CharacterCommit]:
        """
        Get commit history for a repository or branch.
        
        Args:
            db: Database session
            repository_id: Repository ID
            branch_name: Branch name (optional)
            limit: Maximum commits to return
            
        Returns:
            List[CharacterCommit]: List of commits
        """
        query = db.query(CharacterCommit).filter(
            CharacterCommit.repository_id == repository_id
        )
        
        if branch_name:
            branch = db.query(CharacterBranch).filter(
                CharacterBranch.repository_id == repository_id,
                CharacterBranch.branch_name == branch_name
            ).first()
            if branch:
                query = query.filter(CharacterCommit.branch_id == branch.id)
        
        return query.order_by(CharacterCommit.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_character_at_commit(db: Session, commit_hash: str) -> Dict[str, Any]:
        """
        Get character data at a specific commit.
        
        Args:
            db: Database session
            commit_hash: Commit hash
            
        Returns:
            Dict: Character data at commit
        """
        commit = db.query(CharacterCommit).filter(
            CharacterCommit.commit_hash == commit_hash
        ).first()
        
        if not commit:
            raise ValueError(f"Commit '{commit_hash}' not found")
        
        return commit.character_data
    
    @staticmethod
    def create_tag(db: Session, repository_id: str, tag_name: str,
                   commit_hash: str, description: str = None,
                   tag_type: str = "milestone", created_by: str = None) -> CharacterTag:
        """
        Create a tag for a specific commit.
        
        Args:
            db: Database session
            repository_id: Repository ID
            tag_name: Tag name
            commit_hash: Target commit hash
            description: Tag description
            tag_type: Tag type
            created_by: Creator name
            
        Returns:
            CharacterTag: Created tag
        """
        tag = CharacterTag(
            id=str(uuid.uuid4()),  # Generate UUID for the tag
            repository_id=repository_id,
            tag_name=tag_name,
            commit_hash=commit_hash,
            description=description,
            tag_type=tag_type,
            created_by=created_by
        )
        
        db.add(tag)
        db.commit()
        return tag
    
    @staticmethod
    def get_repository_tree(db: Session, repository_id: str) -> Dict[str, Any]:
        """
        Get complete repository tree structure for visualization.
        
        Args:
            db: Database session
            repository_id: Repository ID
            
        Returns:
            Dict: Repository tree data
        """
        repo = db.query(CharacterRepository).filter(
            CharacterRepository.id == repository_id
        ).first()
        
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")
        
        branches = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id
        ).all()
        
        commits = db.query(CharacterCommit).filter(
            CharacterCommit.repository_id == repository_id
        ).order_by(CharacterCommit.created_at.desc()).all()
        
        tags = db.query(CharacterTag).filter(
            CharacterTag.repository_id == repository_id
        ).all()
        
        return {
            "repository": repo.to_dict(),
            "branches": [branch.to_dict() for branch in branches],
            "commits": [commit.to_dict() for commit in commits],
            "tags": [tag.to_dict() for tag in tags]
        }


# ============================================================================
# CHARACTER VERSIONING API - FRONTEND-FRIENDLY METHODS
# ============================================================================

class CharacterVersioningAPI:
    """
    Frontend-friendly API methods for character versioning.
    
    This class provides methods optimized for frontend consumption:
    - Timeline data for visualization components
    - Graph data for D3.js/vis.js integration
    - Simplified data structures for JavaScript consumption
    """
    
    @staticmethod
    def get_character_timeline_for_frontend(db: Session, repository_id: str) -> Dict[str, Any]:
        """
        Get timeline data optimized for frontend visualization.
        
        Args:
            db: Database session
            repository_id: Repository ID
            
        Returns:
            Dict: Timeline data for frontend
        """
        commits = db.query(CharacterCommit).filter(
            CharacterCommit.repository_id == repository_id
        ).order_by(CharacterCommit.created_at.asc()).all()
        
        branches = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id
        ).all()
        
        # Build timeline events
        events = []
        for commit in commits:
            branch_name = next((b.branch_name for b in branches if b.id == commit.branch_id), "main")
            
            events.append({
                "id": commit.commit_hash,
                "type": "commit",
                "timestamp": commit.created_at.isoformat(),
                "level": commit.character_level,
                "message": commit.commit_message,
                "branch": branch_name,
                "milestone": commit.milestone_name,
                "commit_type": commit.commit_type,
                "short_hash": commit.short_hash
            })
        
        # Add branch creation events
        for branch in branches:
            if branch.branch_name != "main":  # Skip main branch
                events.append({
                    "id": f"branch_{branch.id}",
                    "type": "branch_create",
                    "timestamp": branch.created_at.isoformat(),
                    "message": f"Created branch: {branch.branch_name}",
                    "branch": branch.branch_name,
                    "description": branch.description
                })
        
        # Sort by timestamp
        events.sort(key=lambda x: x["timestamp"])
        
        return {
            "repository_id": repository_id,
            "events": events,
            "branch_count": len(branches),
            "commit_count": len(commits)
        }
    
    @staticmethod
    def get_character_visualization_data(db: Session, repository_id: str) -> Dict[str, Any]:
        """
        Get graph visualization data for D3.js/vis.js.
        
        Args:
            db: Database session
            repository_id: Repository ID
            
        Returns:
            Dict: Graph data with nodes and edges
        """
        commits = db.query(CharacterCommit).filter(
            CharacterCommit.repository_id == repository_id
        ).all()
        
        branches = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id
        ).all()
        
        # Create branch color mapping
        branch_colors = {
            "main": "#2563eb",  # Blue
            "development": "#16a34a",  # Green
            "experimental": "#dc2626",  # Red
            "alternate": "#7c3aed"  # Purple
        }
        
        # Build nodes (commits)
        nodes = []
        for commit in commits:
            branch = next((b for b in branches if b.id == commit.branch_id), None)
            branch_name = branch.branch_name if branch else "main"
            
            nodes.append({
                "id": commit.commit_hash,
                "label": f"L{commit.character_level}: {commit.short_hash}",
                "title": commit.commit_message,
                "group": branch_name,
                "color": branch_colors.get(branch.branch_type if branch else "main", "#6b7280"),
                "level": commit.character_level,
                "timestamp": commit.created_at.isoformat(),
                "commit_type": commit.commit_type,
                "milestone": commit.milestone_name
            })
        
        # Build edges (commit relationships)
        edges = []
        for commit in commits:
            if commit.parent_commit_hash:
                edges.append({
                    "from": commit.parent_commit_hash,
                    "to": commit.commit_hash,
                    "arrows": "to"
                })
            
            # Handle merge commits
            if commit.merge_parent_hash:
                edges.append({
                    "from": commit.merge_parent_hash,
                    "to": commit.commit_hash,
                    "arrows": "to",
                    "dashes": True,
                    "color": {"color": "#f59e0b"}  # Orange for merge
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "branches": [
                {
                    "name": branch.branch_name,
                    "type": branch.branch_type,
                    "color": branch_colors.get(branch.branch_type, "#6b7280"),
                    "active": branch.is_active,
                    "merged": branch.is_merged
                }
                for branch in branches
            ]
        }
    
    @staticmethod
    def level_up_character(db: Session, repository_id: str, branch_name: str,
                          new_character_data: Dict[str, Any], level_up_choices: Dict[str, Any] = None) -> CharacterCommit:
        """
        Handle character level up with automatic commit creation.
        
        Args:
            db: Database session
            repository_id: Repository ID
            branch_name: Target branch
            new_character_data: Updated character data
            level_up_choices: Level up choices made
            
        Returns:
            CharacterCommit: Level up commit
        """
        current_level = new_character_data.get("level", 1)
        previous_level = current_level - 1
        
        # Build commit message
        class_info = new_character_data.get("character_classes", {})
        class_names = ", ".join([f"{cls} {lvl}" for cls, lvl in class_info.items()])
        commit_message = f"Level {current_level}: {class_names}"
        
        if level_up_choices:
            choices_summary = []
            if "new_spells" in level_up_choices:
                choices_summary.append(f"Learned {len(level_up_choices['new_spells'])} spells")
            if "ability_score_improvement" in level_up_choices:
                choices_summary.append("ASI applied")
            if "new_features" in level_up_choices:
                choices_summary.append(f"Gained {len(level_up_choices['new_features'])} features")
            
            if choices_summary:
                commit_message += f" - {', '.join(choices_summary)}"
        
        # Create level up commit
        return CharacterRepositoryManager.create_commit(
            db=db,
            repository_id=repository_id,
            branch_name=branch_name,
            commit_message=commit_message,
            character_data=new_character_data,
            character_level=current_level,
            commit_type="level_up",
            milestone_name=f"Level {current_level}"
        )


# ============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# ============================================================================

"""
CHARACTER VERSIONING SYSTEM USAGE EXAMPLES:

1. CREATE A NEW CHARACTER WITH VERSIONING:
   ```python
   # Create character data
   character_data = {
       "name": "Gandalf the Grey",
       "species": "Wizard (Maiar)",
       "level": 1,
       "character_classes": {"Wizard": 1},
       "abilities": {"strength": 10, "intelligence": 18, ...}
   }
   
   # Create repository with initial commit
   repo = CharacterRepositoryManager.create_repository(
       db=db,
       name="Gandalf the Grey",
       initial_character_data=character_data,
       player_name="Tolkien",
       description="The wise wizard of Middle-earth"
   )
   ```

2. LEVEL UP CHARACTER:
   ```python
   # Update character data for level 2
   level_2_data = character_data.copy()
   level_2_data["level"] = 2
   level_2_data["character_classes"] = {"Wizard": 2}
   
   # Commit the level up
   commit = CharacterRepositoryManager.commit_character_change(
       db=db,
       repository_id=repo.id,
       branch_name="main",
       character_data=level_2_data,
       commit_message="Level 2: Gained Arcane Recovery",
       commit_type="level_up",
       milestone_name="First Level Up"
   )
   ```

3. CREATE ALTERNATE CHARACTER PATH:
   ```python
   # Create branch for multiclass path at level 3
   multiclass_branch = CharacterRepositoryManager.create_branch(
       db=db,
       repository_id=repo.id,
       new_branch_name="multiclass-fighter",
       source_commit_hash=level_2_commit.commit_hash,
       description="Exploring multiclass with Fighter"
   )
   
   # Commit multiclass level 3
   multiclass_data = level_2_data.copy()
   multiclass_data["level"] = 3
   multiclass_data["character_classes"] = {"Wizard": 2, "Fighter": 1}
   
   multiclass_commit = CharacterRepositoryManager.commit_character_change(
       db=db,
       repository_id=repo.id,
       branch_name="multiclass-fighter",
       character_data=multiclass_data,
       commit_message="Level 3: Multiclassed into Fighter",
       commit_type="level_up"
   )
   ```

4. GET CHARACTER TIMELINE FOR FRONTEND:
   ```python
   timeline = CharacterVersioningAPI.get_character_timeline_for_frontend(
       db=db,
       repository_id=repo.id
   )
   # Returns formatted data for graph visualization
   ```

5. RETRIEVE CHARACTER AT SPECIFIC POINT:
   ```python
   # Get character data at level 2
   level_2_character = CharacterRepositoryManager.get_character_at_commit(
       db=db,
       commit_hash=level_2_commit.commit_hash
   )
   ```

FRONTEND INTEGRATION:
- Use CharacterVersioningAPI.get_character_timeline_for_frontend() for graph data
- Display branches as different colored lines
- Show commits as nodes with level/milestone information
- Allow users to click commits to view character state at that point
- Provide branch creation UI for "What if?" scenarios
- Show diff between commits to highlight changes

DATABASE SCHEMA:
- character_repositories: Main character containers
- character_branches: Different development paths
- character_commits: Individual character states/versions
- character_tags: Mark important milestones
- characters: Legacy table (kept for compatibility)

The system enables:
- Complete character development history
- "What if?" exploration with branches
- Visual timeline of character progression
- Rollback to previous character states
- Comparison between different development paths
- Story/campaign context tracking
- Collaborative character development
"""


# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
ENHANCED DATABASE MODELS WITH GIT-LIKE CHARACTER VERSIONING

This module provides a comprehensive database layer for D&D character management
with a revolutionary Git-like versioning system that allows players to explore
alternate character development paths.

KEY FEATURES:

1. CHARACTER REPOSITORIES (Git-like System):
   - CharacterRepository: Container for all versions of a character concept
   - CharacterBranch: Different development paths (main, multiclass, alternate stories)
   - CharacterCommit: Individual character states with full data snapshots
   - CharacterTag: Mark important milestones (deaths, resurrections, epic levels)

2. VERSION CONTROL OPERATIONS:
   - Create repositories with initial character commits
   - Branch from any commit to explore alternate paths
   - Commit character changes with detailed change tracking
   - Tag important milestones and story events
   - Retrieve character state at any point in history

3. VISUALIZATION SUPPORT:
   - Complete repository tree data for frontend graphs
   - Parent-child commit relationships for timeline display
   - Branch visualization with merge/split points
   - Diff calculation between character states

4. INTEGRATION SYSTEMS:
   - CharacterRepositoryManager: High-level Git-like operations
   - CharacterVersioningAPI: Frontend-friendly API methods
   - Integration with existing CharacterCore/CharacterState classes
   - Backwards compatibility with legacy Character model

5. USE CASES:
   - Track complete character development history
   - Explore "What if I multiclassed?" scenarios
   - Compare different character builds
   - Rollback to previous character states
   - Visualize character evolution over campaigns
   - Create alternate storyline branches
   - Collaborative character development

6. DATABASE OPERATIONS:
   - CharacterDB: CRUD operations for legacy characters
   - CharacterSessionDB: Character creation session management
   - Proper database session management with context managers
   - Integration with SQLAlchemy ORM

The system transforms character management from a simple database record into
a rich, explorable history that enhances storytelling and player engagement.
Players can see their character's journey visually, explore alternate paths,
and make informed decisions about character development.

FRONTEND VISUALIZATION:
The system is designed to support rich frontend visualizations showing:
- Character development timelines as interactive graphs
- Branch points where different paths diverged
- Commit nodes with level, XP, and milestone information
- Visual diffs between character states
- Tag markers for important story moments

This creates a "comic book multiverse" experience where players can explore
all the different paths their character might have taken.
"""

