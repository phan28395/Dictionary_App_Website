-- Dictionary App Database Schema
-- Based on actual JSON structure from DictGenerativeRule_2
-- Supports all POS (Parts of Speech): Noun, Verb, Adjective, Adverb

-- ============================================
-- CORE TABLES (All POS share these)
-- ============================================

-- Main dictionary content table
CREATE TABLE dictionary_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lemma TEXT NOT NULL,
    pos TEXT NOT NULL CHECK(pos IN ('noun', 'verb', 'adjective', 'adverb')),
    
    -- Common fields for all POS (stored as JSON arrays)
    meanings JSON NOT NULL,              -- ["meaning 1", "meaning 2", ...]
    definitions JSON NOT NULL,           -- ["definition 1", "definition 2", ...]
    examples JSON NOT NULL,              -- [["example1a", "example1b"], ["example2a"], ...]
    frequency_meaning JSON NOT NULL,     -- [0.5, 0.3, 0.2] - decimal weights for each meaning
    
    -- Create compound index for fast lookups
    UNIQUE(lemma, pos)
);

-- Inflection lookup table (maps inflected forms to lemmas)
CREATE TABLE inflection_lookup (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inflected_form TEXT NOT NULL,        -- "went", "children", "better"
    lemma TEXT NOT NULL,                 -- "go", "child", "good"
    pos TEXT NOT NULL,
    
    FOREIGN KEY (lemma, pos) REFERENCES dictionary_entries(lemma, pos)
);

-- ============================================
-- NOUN-SPECIFIC FIELDS
-- ============================================

CREATE TABLE noun_properties (
    entry_id INTEGER PRIMARY KEY,
    
    domains JSON,                        -- ["STORAGE/CONTAINER", "WEAPONS/FIREARMS", ...]
    semantic_function JSON,              -- ["concrete_object", "measure", "person_role", ...]
    key_collocates JSON,                -- [["oak", "wine"], ["gun", "rifle"], ...]
    
    FOREIGN KEY (entry_id) REFERENCES dictionary_entries(id) ON DELETE CASCADE
);

-- ============================================
-- VERB-SPECIFIC FIELDS
-- ============================================

CREATE TABLE verb_properties (
    entry_id INTEGER PRIMARY KEY,
    
    grammatical_patterns JSON,           -- [["V", "V + prep + O"], ["V + O"], ...]
    semantic_roles JSON,                 -- ["agent_only", "agent_patient", ...]
    aspect_type JSON,                    -- ["activity", "achievement", "accomplishment", ...]
    key_collocates JSON,                -- [["cattle", "grass"], ["skin", "knee"], ...]
    
    FOREIGN KEY (entry_id) REFERENCES dictionary_entries(id) ON DELETE CASCADE
);

-- ============================================
-- ADJECTIVE-SPECIFIC FIELDS
-- ============================================

CREATE TABLE adjective_properties (
    entry_id INTEGER PRIMARY KEY,
    
    syntactic_position JSON,             -- ["both", "attributive_only", "predicative_only"]
    gradability JSON,                    -- ["gradable", "non_gradable"]
    semantic_type JSON,                  -- ["physical_property", "evaluative", "relational", ...]
    polarity JSON,                       -- ["positive", "negative", "neutral"]
    antonyms JSON,                       -- [["fertile", "fruitful"], ["open", "accessible"], ...]
    typical_modifiers JSON,              -- [["completely", "totally"], ["rather", "quite"], ...]
    key_collocates JSON,                -- [["woman", "couple"], ["land", "desert"], ...]
    
    FOREIGN KEY (entry_id) REFERENCES dictionary_entries(id) ON DELETE CASCADE
);

-- ============================================
-- ADVERB-SPECIFIC FIELDS
-- ============================================

-- Adverbs only use the common fields, no additional properties needed
-- They have: lemma, meanings, definitions, examples, frequency_meaning

-- ============================================
-- USER DATA TABLES (for licensing/favorites)
-- ============================================

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    hardware_id TEXT UNIQUE,
    license_status TEXT DEFAULT 'free' CHECK(license_status IN ('free', 'pro')),
    searches_remaining INTEGER DEFAULT 50,
    purchase_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    search_term TEXT NOT NULL,           -- What user typed
    lemma_found TEXT,                    -- What lemma was found
    pos_found TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    entry_id INTEGER,
    meaning_index INTEGER,                -- Which meaning they favorited (0-based)
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (entry_id) REFERENCES dictionary_entries(id),
    UNIQUE(user_id, entry_id, meaning_index)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

CREATE INDEX idx_lemma ON dictionary_entries(lemma);
CREATE INDEX idx_pos ON dictionary_entries(pos);
CREATE INDEX idx_lemma_pos ON dictionary_entries(lemma, pos);
CREATE INDEX idx_inflected ON inflection_lookup(inflected_form);
CREATE INDEX idx_user_searches ON search_history(user_id, timestamp DESC);
CREATE INDEX idx_user_favorites ON favorites(user_id);

-- ============================================
-- VIEWS FOR EASIER QUERYING
-- ============================================

-- Complete noun entries with all properties
CREATE VIEW noun_entries AS
SELECT 
    d.*,
    n.domains,
    n.semantic_function,
    n.key_collocates as noun_collocates
FROM dictionary_entries d
JOIN noun_properties n ON d.id = n.entry_id
WHERE d.pos = 'noun';

-- Complete verb entries with all properties
CREATE VIEW verb_entries AS
SELECT 
    d.*,
    v.grammatical_patterns,
    v.semantic_roles,
    v.aspect_type,
    v.key_collocates as verb_collocates
FROM dictionary_entries d
JOIN verb_properties v ON d.id = v.entry_id
WHERE d.pos = 'verb';

-- Complete adjective entries with all properties
CREATE VIEW adjective_entries AS
SELECT 
    d.*,
    a.syntactic_position,
    a.gradability,
    a.semantic_type,
    a.polarity,
    a.antonyms,
    a.typical_modifiers,
    a.key_collocates as adj_collocates
FROM dictionary_entries d
JOIN adjective_properties a ON d.id = a.entry_id
WHERE d.pos = 'adjective';

-- Simple view for adverbs (no additional properties)
CREATE VIEW adverb_entries AS
SELECT * FROM dictionary_entries WHERE pos = 'adverb';

-- ============================================
-- SAMPLE QUERIES
-- ============================================

/*
-- Search for inflected form:
SELECT 
    il.inflected_form,
    il.lemma,
    il.pos,
    de.meanings,
    de.definitions,
    de.examples
FROM inflection_lookup il
JOIN dictionary_entries de ON il.lemma = de.lemma AND il.pos = de.pos
WHERE il.inflected_form = 'went';

-- Get noun with all properties:
SELECT * FROM noun_entries WHERE lemma = 'barrel';

-- Get verb with patterns:
SELECT 
    lemma,
    json_extract(meanings, '$[0]') as primary_meaning,
    json_extract(grammatical_patterns, '$[0]') as primary_pattern
FROM verb_entries 
WHERE lemma = 'greet';

-- Get adjective with antonyms:
SELECT 
    lemma,
    json_extract(meanings, '$') as all_meanings,
    json_extract(antonyms, '$') as all_antonyms
FROM adjective_entries
WHERE lemma = 'barren';
*/