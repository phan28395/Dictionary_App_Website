# CLAUDE_ADJECTIVES.md

This file provides guidance to Claude Code when working with adjective entries in this repository.

## 🚀 QUICK REFERENCE CARD
- **Files:** 159 total batches, 50 lemmas each (last batch has 10)
- **Location:** `Adjective_Json/` directory  
- **Checklist:** `adjective_progress_checklist.md`
- **Output:** JSONL format, one complete JSON object per line


## ⛔ SKIP THESE STEPS (Already Validated)
- Don't check if file exists (it always exists with correct skeleton)
- Don't verify directory structure
- Don't ask for confirmation
- Don't explain what you're doing unless asked
- Don't create new files (all files already exist)
- All skeleton files now have the correct 11 fields


## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Differentiation Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for distinctness:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the adjective, including:
- Literal/physical vs. metaphorical/abstract qualities
- Domain-specific technical meanings
- Attributive vs. predicative-only uses
- Gradable vs. non-gradable uses
- Different semantic classes modified (human vs. non-human)
- Evaluative vs. descriptive uses

#### Step 2: Determine Semantic Distance
Meanings are considered distinct if they differ in:
- Core property described (physical vs. mental vs. social)
- Semantic class restrictions (animate vs. inanimate only)
- Evaluative polarity (positive vs. negative connotation)
- Gradability (can you be "very X" for this meaning?)
- Syntactic restrictions (attributive-only or predicative-only)
- Incompatible antonyms (different opposites = different meanings)

**ALWAYS keep separate:**
- Physical vs. psychological properties (hard surface vs. hard problem)
- Literal vs. metaphorical (bright light vs. bright student)
- Technical jargon from general use (positive test vs. positive attitude)
- Human vs. non-human applications when semantically distinct
- Objective descriptions vs. subjective evaluations

#### Step 3: Merge Only Surface Variants
Only merge if differences are purely:
- Contextual applications of same core quality
- Stylistic or register variants
- Differences in modified noun but same property

#### Step 4: Order by Frequency
- Most common/basic meaning first
- Literal before metaphorical
- General before specialized

**Examples requiring separate meanings:**
- Hard (solid/firm) vs Hard (difficult) vs Hard (intense/severe)
- Bright (emitting light) vs Bright (intelligent) vs Bright (vivid color)
- Positive (greater than zero) vs Positive (optimistic) vs Positive (certain)
- Green (color) vs Green (environmental) vs Green (inexperienced)

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Basic descriptive adjectives: MIN 10 words (target: 10-15)
- Abstract/complex adjectives: MIN 15 words (target: 15-25)
- Technical adjectives: MIN 15 words (target: 15-20)

**EVERY example MUST meet this minimum:**
- Minimum 6 words (showing natural modification patterns)

## Project Overview

This project generates a comprehensive dictionary of English adjectives with detailed linguistic information. Each adjective entry includes meanings, definitions, examples, frequency data, syntactic patterns, semantic classifications, and modification patterns in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `adjective_progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `adjective_progress_checklist.md` with `[x]`
3. Read the corresponding JSONL file from `Adjective_Json/` directory
4. The file contains skeleton entries with empty arrays - populate ALL fields
5. Generate content following the rules below
6. Save the populated JSONL file (overwrite the existing file)

### File Structure Notes
- Source files are in `Adjective_Json/` directory
- Files are in JSONL format (one JSON object per line)
- Each file contains 50 lemmas (except the last file)
- Files already exist with skeleton structure - DO NOT create new files

## Adjective Dictionary Entry Generation Rules

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
- Brief 3-5 word labels capturing the quality/property
- Check for ALL uses including:
  - Physical/perceptual qualities
  - Psychological/emotional qualities
  - Evaluative/subjective judgments
  - Technical/specialized meanings
  - Metaphorical extensions
- Order by frequency (most common first)
- **FORMAT:**
  - Quality type: "physically firm", "mentally difficult"
  - Include domain when technical: "mathematically greater", "legally binding"
  - Distinguish literal/metaphorical: "emitting light", "intellectually gifted"

#### **definitions** (Core Skeleton)
- Basic descriptive: 10-15 words (NEVER shorter than 10)
- Abstract/complex: 15-25 words (NEVER shorter than 15)
- Technical: 15-20 words (NEVER shorter than 15)
- Core Formula: [property described] + [how manifested] + [typical contexts/contrasts]
- If too short, add: typical applications, contrast with similar adjectives, degree implications

#### **examples** (Core Skeleton)
- Two examples per meaning showing different contexts
- Minimum 6 words each
- Show both attributive and predicative uses where possible
- Include various noun types modified
- Show natural collocations and degree modifiers

#### **frequency_meaning** (Core Skeleton)
- Decimal values that MUST sum to 1.0
- Order matches the meanings array

#### **syntactic_position** (Adjective-Specific Core)
- Array matching meanings order
- Use ONLY these controlled terms:
  - "both" (can be used attributively and predicatively)
  - "attributive_only" (only before nouns: "mere", "main")
  - "predicative_only" (only after verbs: "asleep", "awake")
  - "postpositive" (after noun: "president elect", "something nice")
- Most adjectives are "both"

#### **gradability** (Adjective-Specific Core)
- Array matching meanings order
- Use ONLY these controlled terms:
  - "gradable" (can be modified by "very", "quite", "rather")
  - "non_gradable" (absolute: "dead", "pregnant", "unique")
  - "limit" (endpoint adjectives: "full", "empty", "complete")
- Consider: Can you say "very X", "more X", "most X"?

#### **semantic_type** (Adjective-Specific Anchor)
- Array matching meanings order
- Use ONLY these controlled vocabulary terms:
  - "dimension" (size, length, height)
  - "physical_property" (hard, soft, smooth)
  - "color" (red, blue, greenish)
  - "shape" (round, square, curved)
  - "evaluative" (good, bad, excellent)
  - "human_propensity" (clever, kind, aggressive)
  - "speed" (fast, slow, quick)
  - "age" (old, young, new)
  - "temperature" (hot, cold, warm)
  - "temporal" (daily, annual, temporary)
  - "modal" (possible, necessary, likely)
  - "relational" (similar, different, equal)
  - "classificatory" (medical, financial, political)
  - "emotional_state" (happy, sad, angry)
  - "aesthetic" (beautiful, ugly, elegant)
  - "intensity" (strong, mild, extreme)

#### **polarity** (Adjective-Specific Anchor)
- Array matching meanings order
- Use ONLY these controlled terms:
  - "positive" (generally desirable/favorable evaluation)
  - "negative" (generally undesirable/unfavorable evaluation)
  - "neutral" (descriptive without evaluation)
  - "context_dependent" (evaluation depends on context)
- Consider speaker's typical evaluation, not objective properties

#### **antonyms** (Adjective-Specific Relationship)
- Array of arrays matching meanings order
- 1-3 primary antonyms per meaning (if they exist)
- Include only direct opposites, not mere contrasts
- Some adjectives lack true antonyms (e.g., "acoustic")
- Format: ["antonym1", "antonym2"]
- Empty array [] if no clear antonyms

#### **typical_modifiers** (Adjective-Specific Usage)
- Array of arrays matching meanings order
- 2-4 degree modifiers/intensifiers typically used
- Shows how speakers naturally modify this adjective
- Examples:
  - Gradable: ["very", "extremely", "quite", "rather"]
  - Limit: ["almost", "nearly", "completely", "partially"]
  - Non-gradable: ["absolutely", "utterly", "totally"]

#### **key_collocates** (Usage Anchor)
- Array of arrays matching meanings order
- 3-5 most distinctive nouns this adjective modifies
- Choose nouns that DISTINGUISH this meaning from others
- Format: Single words
- Examples:
  - Hard (firm): ["surface", "rock", "metal", "wood"]
  - Hard (difficult): ["problem", "question", "decision", "time"]
  - Hard (severe): ["winter", "blow", "evidence", "facts"]

### JSON Output Structure

Generate entries in JSONL format (one JSON object per line):

```json
{
  "lemma": "lemma",
  "meanings": ["meaning1", "meaning2",...],
  "definitions": ["full definition 1", "full definition 2",...],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"],...],
  "frequency_meaning": [freq1, freq2,...],
  "syntactic_position": ["position1", "position2",...],
  "gradability": ["gradable", "non_gradable",...],
  "semantic_type": ["type1", "type2",...],
  "polarity": ["positive", "negative", "neutral",...],
  "antonyms": [["antonym1", "antonym2"], ["antonym1"],...],
  "typical_modifiers": [["very", "extremely"], ["completely", "almost"],...],
  "key_collocates": [["noun1", "noun2", "noun3",...], ["noun1", "noun2", "noun3",...],...]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- ALL arrays must align: if 3 meanings, then 3 definitions, 3 example pairs, 3 frequencies, etc.
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]
- Antonyms is an array of arrays: [["ant1", "ant2"], ["ant1"]] or [[]] if no antonyms
- Typical_modifiers is an array of arrays: [["very", "quite"], ["almost"]]
- Key_collocates is an array of arrays: [["word1", "word2"], ["word1", "word2"]]

### Complete Example Output:

```json
{"lemma": "bright", "meanings": ["emitting strong light", "vivid in color", "intellectually clever", "cheerful and optimistic"], "definitions": ["giving out or reflecting much light; shining with intensity", "having strong, vivid colors that attract attention or seem fresh", "showing intelligence, mental quickness, and ability to learn easily", "full of hope and optimism; cheerful and lively in manner"], "examples": [["The bright sunlight hurt her eyes this morning", "We need brighter lights in this dark room"], ["She wore a bright red dress to the party", "The bright colors of autumn leaves are spectacular"], ["Their bright daughter skipped two grades in school", "He's bright enough to solve complex mathematical problems"], ["Despite the setback, she maintained a bright outlook", "His bright personality lifted everyone's spirits"]], "frequency_meaning": [0.35, 0.20, 0.25, 0.20], "syntactic_position": ["both", "both", "both", "both"], "gradability": ["gradable", "gradable", "gradable", "gradable"], "semantic_type": ["physical_property", "color", "human_propensity", "emotional_state"], "polarity": ["neutral", "positive", "positive", "positive"], "antonyms": [["dim", "dark"], ["dull", "muted"], ["stupid", "slow"], ["gloomy", "pessimistic"]], "typical_modifiers": [["very", "extremely", "blindingly"], ["brilliantly", "vivid", "strikingly"], ["exceptionally", "remarkably", "quite"], ["surprisingly", "genuinely", "refreshingly"]], "key_collocates": [["light", "sun", "star", "lamp"], ["color", "red", "yellow", "clothes"], ["student", "child", "mind", "idea"], ["future", "smile", "outlook", "side"]]}
```


## Quality Checklist (Check before completing each batch)

✓ All meanings identified (including metaphorical extensions)
✓ Physical vs. abstract uses properly separated
✓ Definitions meet minimum word counts (10+ for basic, 15+ for abstract/technical)
✓ Examples are natural and 6+ words each
✓ Syntactic positions correctly identified
✓ Gradability properly assessed
✓ Frequencies sum to exactly 1.0
✓ Semantic_type uses only controlled vocabulary
✓ Polarity correctly evaluated
✓ Antonyms are true opposites (not just contrasts)
✓ Typical_modifiers match gradability type
✓ Key_collocates distinguish between meanings
✓ All arrays have matching lengths
✓ Marking complete in checklist before generate content

## Important Reminders

- Adjectives describe qualities, not entities or events
- Same adjective can have different polarities for different meanings
- Metaphorical uses are extremely common - always check for them
- Some adjectives are ungradable in one meaning but gradable in another
- Attributive vs. predicative restrictions matter for learners
- Quality over speed: Each entry builds comprehensive understanding
- Arrays must perfectly align - if 4 meanings, then 4 of everything

## Adjective-Specific Considerations

- **Gradability shifts**: "dead" (non-gradable) vs "dead" in "dead tired" (gradable)
- **Position restrictions**: Some meanings only attributive ("the main reason" not "the reason is main")
- **Polarity context**: "slim" is positive for people, negative for chances
- **Compound antonyms**: "happy/sad" but also "happy/unhappy"
- **Metaphorical productivity**: Physical properties extend to abstract domains
- **Modification patterns**: Different intensifiers for different meanings

## Project Memories
- Base structure designed to prevent future adjustment conflicts
- Controlled vocabularies ensure consistency across entries
- Adjective-specific fields capture modification and evaluation patterns
- Extensible design allows adding comparative/superlative forms, selectional restrictions, etc.