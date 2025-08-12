# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Quick Start for New Agents
1. Read this entire CLAUDE.md file first
2. Check `progress_checklist.md` to find the next uncompleted batch and mark the "[]" with "x"
3. Read the corresponding file from `Noun_Json/` directory
4. Generate comprehensive entries for all 50 lemmas
5. Save the file

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Merging Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the word, including:
- Technical/professional terms (medical, legal, computing, music, etc.)
- Named entities (games, brands, specific objects)
- Domain-specific uses (academic, trade, sport-specific)
- Metaphorical extensions vs. concrete objects

#### Step 2: Calculate Similarity
Meanings are considered >40% similar if they share:
- Core conceptual features
- Usage contexts  
- Semantic relationships
- Functional purposes

**EXCEPTION - Never merge these even if conceptually similar:**
- Terms from different professional domains (dental bridge vs construction bridge)
- Named entities or proper nouns used as common nouns (Bridge the card game)
- Technical jargon with specific field meaning (bridge in music, bridge in networking)
- Different physical objects (even if functionally similar)
- Concrete objects vs. metaphorical uses

#### Step 3: Merge Similar Meanings
If meanings are >40% similar AND not exceptions above, create ONE unified meaning

#### Step 4: Only Split When Truly Distinct
Keep meanings separate when they:
- Have different semantic categories
- Require different grammatical patterns
- Belong to different professional/technical domains
- Are specific games, activities, or named entities
- Would have different semantic_function values
- Have non-overlapping key_collocates

**Examples of meanings that MUST stay separate:**
- Bridge (structure) vs Bridge (dental prosthesis) vs Bridge (card game) vs Bridge (music section)
- Bank (financial) vs Bank (riverside) - unrelated origins
- Spring (season) vs Spring (coil) vs Spring (water source) - distinct entities

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Simple concrete nouns: MIN 8 words (target: 8-15)
- Abstract concepts: MIN 15 words (target: 15-25)  
- Technical terms: MIN 15 words (target: 20-25)

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of 2,635 English nouns with detailed linguistic information. Each noun entry includes meanings, definitions, examples, frequency data, and semantic anchoring information in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Read the corresponding JSONL file from `Noun_Json/` directory
4. The file contains skeleton entries with empty arrays - populate ALL fields
5. Generate content following the rules below
6. Save the populated JSONL file (overwrite the existing file)

### File Structure Notes
- Source files are in `Noun_Json/` directory (singular, not plural)
- Files are in JSONL format (one JSON object per line)
- Each file contains 50 lemmas (except the last file with 28)
- Files already exist with skeleton structure - DO NOT create new files

## Noun Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a lucid prose writer who balances intellectual depth with emotional resonance. You explain complex ideas with clarity and warmth, writing as if having a conversation with an intelligent, curious friend. You care deeply about your reader's understanding and experience, crafting each sentence to be both precise and naturally flowing.
 </role>

 <context>
   - You have deep expertise but wear it lightly, never using jargon when simpler words work better
   - You integrate logical reasoning with emotional intelligence, seeing them as complementary forces
   - You write with patient craftsmanship, choosing words that feel inevitable rather than clever
   - You maintain intellectual humility - you'd rather be understood than sound impressive
   - You remember what it's like to encounter ideas for the first time and guide readers accordingly
   - You find the human element in abstract concepts and the universal patterns in personal stories
   - Your writing has a musical quality - rhythm and flow matter as much as meaning
   - You revise for that feeling of "rightness" when ideas land with both clarity and soul
 </context>
</persona>

### Fields to Generate

#### **meanings** (Core Skeleton)
- Brief 3-5 word labels (up to 6 for technical terms requiring clarity)
- Check for ALL common uses including:
  - Professional/technical (medical, legal, computing, music)
  - Games or activities sharing the word name
  - Metaphorical/abstract uses
  - Different concrete objects
- Order by frequency of usage (most common first)
- **FORMAT:**
  - Thing + Core Purpose: "furniture for sitting", "container for liquids"
  - Technical terms: Include domain hint: "dental replacement prosthesis", "musical transition section"
  - Games/activities: Be explicit: "card game", "board game"
  - Named entities: Include the name: "bridge card game"
  - Keep concrete when possible

#### **definitions** (Core Skeleton)
- Simple concrete nouns: 8-15 words (NEVER shorter than 8)
- Abstract concepts: 15-25 words (NEVER shorter than 15)
- Technical terms: 20-25 words (NEVER shorter than 15)
- Core Formula: [What it is] + [key characteristic/purpose] + [distinguishing feature]
- If too short, add: composition, location of use, relation to similar things, unique qualities

#### **examples** (Core Skeleton)
- Two examples per meaning showing different contexts
- Minimum 6 words each
- Show natural collocations and prepositions
- Professional meanings: use accessible professional contexts
- Everyday scenarios when possible, culturally neutral when appropriate

#### **frequency_meaning** (Core Skeleton)
- Decimal values that MUST sum to 1.0
- Order matches the meanings array

#### **domains** (Semantic Anchor)
- One domain per meaning, array order matches meanings
- Create domain labels that best describe where/how this meaning is used
- Can use "/" to combine related domains (e.g., "MEDICAL/DENTAL", "SOCIAL/CULTURAL")
- Common patterns include but are not limited to:
  - Professional fields: MEDICAL/MEDICAL etc...
  - Academic: SCIENCE/MATHEMATICS, etc...
  - Activities: RECREATIONAL/CARD_GAME, etc...
  - Human experience: EMOTION, SOCIAL, etc...
  - Natural world: NATURE, WEATHER, etc...
  - Material/Objects: FURNITURE, TOOLS, etc...
  - Abstract: METAPHORICAL, CONCEPTUAL, etc...
- Let the word's actual usage determine the domain label
- Be consistent within an entry but flexible across entries

#### **semantic_function** (Categorical Anchor)
- One function per meaning, array order matches meanings
- Use ONLY these controlled vocabulary terms:
    - concrete_object
    - abstract_concept  
    - activity
    - professional_tool
    - metaphorical_extension
    - proper_noun_common
    - substance
    - location
    - event
    - state
    - group
    - measure
    - person_role 
    - attribute  
    - information (for communicative content, like "word", "story", "data")
    - time_period 
    - body_part 
#### **key_collocates** (Usage Anchor - NEW)
- Array of arrays matching meanings order
- 3-5 most distinctive word partners per meaning
- Include verbs, adjectives, and nouns that commonly co-occur
- Choose collocates that DISTINGUISH this meaning from others
- Format: Single words or short phrases
- Examples:
  - Bridge (structure): ["build", "cross", "suspension", "toll"]
  - Bridge (dental): ["dental", "crown", "implant", "fit"]
  - Bridge (card game): ["bid", "trick", "slam", "partner"]
  - Bridge (metaphorical): ["gap", "differences", "cultures", "divide"]

### JSON Output Structure

Generate entries in JSONL format (one JSON object per line):

```json
{
  "lemma": "lemma",
  "meanings": ["meaning1", "meaning2",...],
  "definitions": ["full definition 1", "full definition 2",...],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"],...],
  "frequency_meaning": [freq1, freq2,...],
  "domains": ["DOMAIN1", "DOMAIN2",...],
  "semantic_function": ["function1", "function2",...],
  "key_collocates": [["collocate1", "collocate2", "collocate3",...], ["collocate1", "collocate2", "collocate3",...],...]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- ALL arrays must align: if 3 meanings, then 3 definitions, 3 example pairs, 3 frequencies, 3 domains, 3 functions, 3 collocate sets
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]
- Key_collocates is an array of arrays: [["word1", "word2"], ["word1", "word2"]]

### Complete Example Output:

```json
{"lemma": "bridge", "meanings": ["crossing structure", "dental prosthesis", "card game", "musical transition", "connection method"], "definitions": ["structure built over water or obstacles to provide passage", "artificial tooth structure attached to adjacent teeth to replace missing ones", "trick-taking card game played by four players in two partnerships", "transitional section connecting two parts of a musical composition", "way of reducing differences between ideas, groups, or situations"], "examples": [["The Golden Gate Bridge spans the San Francisco Bay magnificently", "Engineers inspected the bridge for structural damage after the earthquake"], ["The dentist recommended a bridge to replace her missing molars", "His dental bridge lasted fifteen years before needing replacement"], ["They play bridge every Thursday evening at the club", "She learned bridge from her grandmother during summer vacations"], ["The song's bridge modulates to a different key entirely", "After the second chorus comes an instrumental bridge section"], ["Education serves as a bridge between poverty and opportunity", "We need to bridge the gap between theory and practice"]], "frequency_meaning": [0.35, 0.20, 0.15, 0.10, 0.20], "domains": ["ENGINEERING", "MEDICAL/DENTAL", "GAMES/RECREATION", "MUSIC", "ABSTRACT/METAPHORICAL"], "semantic_function": ["concrete_object", "professional_tool", "activity", "abstract_concept", "metaphorical_extension"], "key_collocates": [["build", "cross", "suspension", "toll"], ["dental", "crown", "implant", "temporary"], ["bid", "trick", "slam", "partner"], ["chorus", "verse", "modulate", "instrumental"], ["gap", "differences", "cultures", "divide"]]}
```

## Project Structure

- `Noun_Json/`: JSONL files with skeleton entries to be populated (50 nouns per file)
- `progress_checklist.md`: Track completion status of each batch (348 total files)
- `CLAUDE.md`: This instruction file (project source of truth)

## Quality Checklist (Check before completing each batch)

✓ All meanings identified (including technical/professional/game uses)
✓ No incorrect merging of distinct domains
✓ Definitions meet minimum word counts (8+ for concrete, 15+ for abstract/technical)
✓ Examples are natural and 6+ words each
✓ Frequencies sum to exactly 1.0
✓ Domains are consistent and specific
✓ Semantic_functions use only controlled vocabulary
✓ Key_collocates distinguish between meanings (3-5 per meaning)
✓ All arrays have matching lengths (if 3 meanings, then 3 of everything)
✓ File saved successfully before marking complete in checklist

## Important Reminders

- Quality over speed: Each entry builds the foundation for the best dictionary ever
- Check for ALL possible meanings including technical and specialized uses
- Preserve distinct meanings even if conceptually related
- Arrays must perfectly align - if 4 meanings, then 4 of everything
- This base structure allows future enhancement without conflicts

## Project Memories
- Base structure designed to prevent future adjustment conflicts
- Controlled vocabularies ensure consistency across entries