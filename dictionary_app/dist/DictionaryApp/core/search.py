"""
Search engine core for Dictionary App.
Handles dictionary searches, inflection lookups, and result formatting.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from .database import Database

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a single search result."""
    lemma: str
    pos: str
    meanings: List[Dict[str, Any]]
    inflection_note: Optional[str] = None
    frequency_rank: Optional[int] = None
    
    # POS-specific fields
    domains: Optional[List[str]] = None  # Noun
    semantic_function: Optional[str] = None  # Noun
    key_collocates: Optional[List[str]] = None  # Noun
    
    grammatical_patterns: Optional[List[str]] = None  # Verb
    semantic_roles: Optional[str] = None  # Verb
    aspect_type: Optional[str] = None  # Verb
    
    gradability: Optional[str] = None  # Adjective
    semantic_prosody: Optional[str] = None  # Adjective
    attributive_only: Optional[bool] = None  # Adjective
    predicative_only: Optional[bool] = None  # Adjective
    comparative_form: Optional[str] = None  # Adjective
    superlative_form: Optional[str] = None  # Adjective
    typical_modifiers: Optional[List[str]] = None  # Adjective
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            'lemma': self.lemma,
            'pos': self.pos,
            'meanings': self.meanings,
        }
        
        # Add optional fields if present
        if self.inflection_note:
            result['inflection_note'] = self.inflection_note
        if self.frequency_rank:
            result['frequency_rank'] = self.frequency_rank
            
        # Add POS-specific fields
        if self.pos == 'noun':
            if self.domains:
                result['domains'] = self.domains
            if self.semantic_function:
                result['semantic_function'] = self.semantic_function
            if self.key_collocates:
                result['key_collocates'] = self.key_collocates
                
        elif self.pos == 'verb':
            if self.grammatical_patterns:
                result['grammatical_patterns'] = self.grammatical_patterns
            if self.semantic_roles:
                result['semantic_roles'] = self.semantic_roles
            if self.aspect_type:
                result['aspect_type'] = self.aspect_type
                
        elif self.pos == 'adjective':
            if self.gradability:
                result['gradability'] = self.gradability
            if self.semantic_prosody:
                result['semantic_prosody'] = self.semantic_prosody
            if self.attributive_only is not None:
                result['attributive_only'] = self.attributive_only
            if self.predicative_only is not None:
                result['predicative_only'] = self.predicative_only
            if self.comparative_form:
                result['comparative_form'] = self.comparative_form
            if self.superlative_form:
                result['superlative_form'] = self.superlative_form
            if self.typical_modifiers:
                result['typical_modifiers'] = self.typical_modifiers
        
        return result


class SearchCache:
    """Simple in-memory cache for search results."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        """
        Initialize cache.
        
        Args:
            max_size: Maximum number of entries
            ttl: Time to live in seconds
        """
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.access_times[key] > self.ttl:
            del self.cache[key]
            del self.access_times[key]
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        return self.cache[key]
    
    def set(self, key: str, value: Any):
        """Set value in cache."""
        # Evict oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times, key=self.access_times.get)
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self):
        """Clear the cache."""
        self.cache.clear()
        self.access_times.clear()


class SearchEngine:
    """
    Main search engine for dictionary lookups.
    """
    
    def __init__(self, database: Database, config: Dict[str, Any]):
        """
        Initialize search engine.
        
        Args:
            database: Database instance
            config: Configuration dictionary
        """
        self.db = database
        self.config = config
        
        # Initialize cache
        cache_config = config.get('search', {}).get('cache', {})
        self.cache_enabled = cache_config.get('enabled', True)
        
        if self.cache_enabled:
            self.cache = SearchCache(
                max_size=cache_config.get('size_mb', 100) * 100,  # Rough estimate
                ttl=cache_config.get('ttl_seconds', 3600)
            )
        else:
            self.cache = None
        
        # Load inflection lookup
        self.inflection_map = {}
        self._load_inflection_lookup()
    
    def _load_inflection_lookup(self):
        """Load inflection lookup table into memory."""
        logger.info("Loading inflection lookup...")
        
        # Try to load from database first
        try:
            query = "SELECT inflected_form, lemma, pos FROM inflection_lookup"
            rows = self.db.execute(query)
            
            for inflected, lemma, pos in rows:
                if inflected not in self.inflection_map:
                    self.inflection_map[inflected] = []
                self.inflection_map[inflected].append((lemma, pos))
            
            logger.info(f"Loaded {len(self.inflection_map)} inflection mappings")
        except Exception as e:
            logger.warning(f"Could not load inflections from database: {e}")
            
            # Try to load from TSV file as fallback
            tsv_path = Path(__file__).parent.parent / 'data' / 'inflection_lookup.tsv'
            if tsv_path.exists():
                self._load_inflection_from_tsv(tsv_path)
    
    def _load_inflection_from_tsv(self, tsv_path: Path):
        """Load inflection lookup from TSV file."""
        try:
            with open(tsv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        inflected, lemma, pos = parts[0], parts[1], parts[2]
                        if inflected not in self.inflection_map:
                            self.inflection_map[inflected] = []
                        self.inflection_map[inflected].append((lemma, pos))
            
            logger.info(f"Loaded {len(self.inflection_map)} inflections from TSV")
        except Exception as e:
            logger.error(f"Failed to load inflection TSV: {e}")
    
    def search(self, term: str) -> List[SearchResult]:
        """
        Search for a term in the dictionary.
        
        Args:
            term: Search term (may be inflected form)
            
        Returns:
            List of search results
        """
        if not term:
            return []
        
        # Normalize input
        term = term.strip().lower()
        
        # Check cache
        if self.cache_enabled and self.cache:
            cached = self.cache.get(term)
            if cached is not None:
                logger.debug(f"Cache hit for: {term}")
                return cached
        
        results = []
        
        # Step 1: Check inflection lookup
        inflection_note = None
        if term in self.inflection_map:
            lemma_pos_pairs = self.inflection_map[term]
            inflection_note = f"{term} → "
            
            for lemma, pos in lemma_pos_pairs:
                result = self._fetch_entry(lemma, pos)
                if result:
                    result.inflection_note = f"{term} → {lemma}"
                    results.append(result)
        
        # Step 2: Try direct lemma search if no inflection results
        if not results:
            # Search all POS tables
            for pos in ['noun', 'verb', 'adjective', 'adverb']:
                result = self._fetch_entry(term, pos)
                if result:
                    results.append(result)
        
        # Sort results by frequency (if available)
        results.sort(key=lambda r: r.frequency_rank or 999999)
        
        # Cache results
        if self.cache_enabled and self.cache:
            self.cache.set(term, results)
        
        logger.info(f"Search for '{term}' returned {len(results)} results")
        return results
    
    def _fetch_entry(self, lemma: str, pos: str) -> Optional[SearchResult]:
        """
        Fetch dictionary entry from database.
        
        Args:
            lemma: Dictionary lemma
            pos: Part of speech
            
        Returns:
            SearchResult or None
        """
        # Query main entry
        query = """
            SELECT id, lemma, meanings, NULL as frequency_rank
            FROM dictionary_entries
            WHERE lemma = ? AND pos = ?
        """
        
        row = self.db.execute_one(query, (lemma, pos))
        
        if not row:
            return None
        
        entry_id, lemma, meanings_json, frequency_rank = row
        
        # Parse meanings
        try:
            meanings = json.loads(meanings_json) if meanings_json else []
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in meanings for {lemma}")
            meanings = []
        
        # Sort meanings by frequency
        meanings.sort(key=lambda m: m.get('frequency_meaning', 0), reverse=True)
        
        # Create result
        result = SearchResult(
            lemma=lemma,
            pos=pos,
            meanings=meanings,
            frequency_rank=frequency_rank
        )
        
        # Fetch POS-specific data
        if pos == 'noun':
            self._fetch_noun_data(entry_id, result)
        elif pos == 'verb':
            self._fetch_verb_data(entry_id, result)
        elif pos == 'adjective':
            self._fetch_adjective_data(entry_id, result)
        # Adverbs have no additional data
        
        return result
    
    def _fetch_noun_data(self, entry_id: int, result: SearchResult):
        """Fetch noun-specific data."""
        query = """
            SELECT domains, semantic_function, noun_collocates
            FROM noun_entries
            WHERE id = ?
        """
        
        row = self.db.execute_one(query, (entry_id,))
        
        if row:
            domains_json, semantic_function, collocates_json = row
            
            try:
                result.domains = json.loads(domains_json) if domains_json else None
            except json.JSONDecodeError:
                result.domains = None
            
            result.semantic_function = semantic_function
            
            try:
                result.key_collocates = json.loads(collocates_json) if collocates_json else None
            except json.JSONDecodeError:
                result.key_collocates = None
    
    def _fetch_verb_data(self, entry_id: int, result: SearchResult):
        """Fetch verb-specific data."""
        query = """
            SELECT grammatical_patterns, semantic_roles, aspect_type
            FROM verb_entries
            WHERE id = ?
        """
        
        row = self.db.execute_one(query, (entry_id,))
        
        if row:
            patterns_json, semantic_roles, aspect_type = row
            
            try:
                result.grammatical_patterns = json.loads(patterns_json) if patterns_json else None
            except json.JSONDecodeError:
                result.grammatical_patterns = None
            
            result.semantic_roles = semantic_roles
            result.aspect_type = aspect_type
    
    def _fetch_adjective_data(self, entry_id: int, result: SearchResult):
        """Fetch adjective-specific data."""
        query = """
            SELECT gradability, polarity as semantic_prosody, syntactic_position,
                   NULL as comparative_form, NULL as superlative_form, typical_modifiers
            FROM adjective_entries
            WHERE id = ?
        """
        
        row = self.db.execute_one(query, (entry_id,))
        
        if row:
            (gradability, semantic_prosody, syntactic_position,
             comparative_form, superlative_form, modifiers_json) = row
            
            result.gradability = gradability
            result.semantic_prosody = semantic_prosody
            # Parse syntactic_position to determine attributive/predicative
            if syntactic_position:
                result.attributive_only = syntactic_position == 'attributive'
                result.predicative_only = syntactic_position == 'predicative'
            result.comparative_form = comparative_form
            result.superlative_form = superlative_form
            
            try:
                result.typical_modifiers = json.loads(modifiers_json) if modifiers_json else None
            except json.JSONDecodeError:
                result.typical_modifiers = None
    
    def get_suggestions(self, prefix: str, limit: int = 10) -> List[str]:
        """
        Get autocomplete suggestions for a prefix.
        
        Args:
            prefix: Search prefix
            limit: Maximum number of suggestions
            
        Returns:
            List of suggested lemmas
        """
        query = """
            SELECT DISTINCT lemma
            FROM dictionary_entries
            WHERE lemma LIKE ?
            ORDER BY lemma ASC
            LIMIT ?
        """
        
        rows = self.db.execute(query, (f"{prefix}%", limit))
        return [row[0] for row in rows]
    
    def get_random_word(self, pos: Optional[str] = None) -> Optional[SearchResult]:
        """
        Get a random word from the dictionary.
        
        Args:
            pos: Optional part of speech filter
            
        Returns:
            Random search result or None
        """
        if pos:
            query = """
                SELECT lemma
                FROM dictionary_entries
                WHERE pos = ?
                ORDER BY RANDOM()
                LIMIT 1
            """
            row = self.db.execute_one(query, (pos,))
        else:
            query = """
                SELECT lemma
                FROM dictionary_entries
                ORDER BY RANDOM()
                LIMIT 1
            """
            row = self.db.execute_one(query)
        
        if row:
            results = self.search(row[0])
            return results[0] if results else None
        
        return None
    
    def get_word_of_day(self) -> Optional[SearchResult]:
        """
        Get word of the day (deterministic based on date).
        
        Returns:
            Word of the day or None
        """
        import hashlib
        from datetime import date
        
        # Use date as seed for consistency
        today = date.today().isoformat()
        seed = int(hashlib.md5(today.encode()).hexdigest()[:8], 16)
        
        # Get word at specific position based on seed
        query = """
            SELECT lemma
            FROM dictionary_entries
            ORDER BY lemma
            LIMIT 1 OFFSET ?
        """
        
        # Use modulo to keep offset reasonable
        offset = seed % 5000
        row = self.db.execute_one(query, (offset,))
        
        if row:
            results = self.search(row[0])
            return results[0] if results else None
        
        return None