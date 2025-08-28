# CLAUDE_VERBS.md

This file provides guidance to Claude Code when working with verb entries in this repository.

## Quick Start for New Agents
1. Read this entire CLAUDE_VERBS.md file first
2. Check `verb_progress_checklist.md` to find the next uncompleted batch and mark the "[]" with "x"
3. Read the corresponding file from `Verb_Json/` directory
4. Generate comprehensive entries for all 50 lemmas
5. Save the file

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Differentiation Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for distinctness:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the verb, including:
- Physical vs. mental actions
- Literal vs. metaphorical uses
- Transitive vs. intransitive patterns
- Domain-specific uses (legal, medical, computing, etc.)
- Phrasal verb meanings (but keep main verb separate)
- Causative vs. inchoative uses
- Different argument structures implying different meanings

#### Step 2: Determine Semantic Distance
Meanings are considered distinct if they differ in:
- Core semantic roles (who does what to whom)
- Selectional restrictions (animate vs. inanimate subjects/objects)
- Aspect profile (states vs. achievements vs. activities)
- Metaphorical mapping domains
- Syntactic frames required
- Professional/technical specificity

**ALWAYS keep separate:**
- Physical actions vs. abstract processes (break an object vs. break a promise)
- Different grammatical patterns (run intransitive vs. run transitive)
- Technical jargon from general use (compile code vs. compile a list)
- Actions with different intentionality (drop accidentally vs. drop deliberately)
- Different domains of metaphorical extension

#### Step 3: Merge Only True Variants
Only merge if differences are purely:
- Contextual variations of same core action
- Different objects but same semantic role
- Stylistic or register differences only

#### Step 4: Order by Frequency
- Most common/basic meaning first
- Physical before metaphorical
- General before specialized

**Examples requiring separate meanings:**
- Run (move quickly) vs Run (operate) vs Run (manage) vs Run (flow)
- Break (physically damage) vs Break (violate rules) vs Break (pause) vs Break (dawn)
- Set (place) vs Set (harden) vs Set (establish) vs Set (sun descending)

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Basic action verbs: MIN 10 words (target: 10-15)
- Complex/abstract verbs: MIN 15 words (target: 15-25)
- Technical/specialized verbs: MIN 15 words (target: 20-25)

**EVERY example MUST meet this minimum:**
- Minimum 7 words (verbs need more context than nouns)

## Project Overview

This project generates a comprehensive dictionary of English verbs with detailed linguistic information. Each verb entry includes meanings, definitions, examples, frequency data, grammatical patterns, and semantic anchoring information in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `verb_progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `verb_progress_checklist.md` with `[x]`
3. Read the corresponding JSONL file from `Verb_Json/` directory
4. The file contains skeleton entries with empty arrays - populate ALL fields
5. Generate content following the rules below
6. Save the populated JSONL file (overwrite the existing file)

### File Structure Notes
- Source files are in `Verb_Json/` directory
- Files are in JSONL format (one JSON object per line)
- Each file contains 50 lemmas (except the last file)
- Files already exist with skeleton structure - DO NOT create new files

## Verb Dictionary Entry Generation Rules

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
- Brief 3-6 word labels capturing the action essence
- Check for ALL uses including:
  - Physical vs. mental actions
  - Transitive vs. intransitive patterns
  - Professional/technical uses
  - Metaphorical extensions
  - Different grammatical constructions implying different meanings
- Order by frequency (most common first)
- **FORMAT:**
  - Core action + key distinction: "move rapidly forward", "operate a system"
  - Include particle for phrasal meanings: "break down mechanically"
  - Technical: Add domain hint: "compile computer code"
  - State vs. Action: Be explicit: "become solid", "make solid"

#### **definitions** (Core Skeleton)
- Basic action verbs: 10-15 words (NEVER shorter than 10)
- Complex/abstract verbs: 15-25 words (NEVER shorter than 15)
- Technical verbs: 20-25 words (NEVER shorter than 15)
- Core Formula: [action/state] + [agent/patient roles] + [manner/result] + [context/purpose]
- If too short, add: typical contexts, manner specifications, results/effects, contrast with similar verbs

#### **examples** (Core Skeleton)
- Two examples per meaning showing different contexts
- Minimum 7 words each 
- Show different tenses and aspects where relevant
- Include various grammatical patterns
- Professional meanings: use accessible professional contexts
- Show both animate and inanimate subjects where applicable

#### **frequency_meaning** (Core Skeleton)
- Decimal values that MUST sum to 1.0
- Order matches the meanings array
- Consider that basic physical meanings usually dominate

#### **grammatical_patterns** (Verb-Specific Core)
- Array of arrays matching meanings order
- 2-4 most common patterns per meaning
- Use standard notation:
  - "V" (intransitive): "She runs"
  - "V + O" (transitive): "He broke the window"
  - "V + O + O" (ditransitive): "She gave him a book"
  - "V + that-clause": "He believes that she left"
  - "V + to-inf": "She wants to leave"
  - "V + O + to-inf": "He told her to leave"
  - "V + prep + O": "She depends on him"
  - "V + O + prep + O": "He put the book on the table"
  - "V + adj": "She seems happy"
  - "V + O + adj": "Paint the wall blue"
  - Include prepositions where fixed: "look at", "depend on"

#### **semantic_roles** (Verb-Specific Anchor)
- One role configuration per meaning, array order matches meanings
- Use ONLY these controlled vocabulary terms:
  - agent_patient (someone does something to something)
  - agent_only (someone does something, no object)
  - agent_theme_goal (someone moves something somewhere)
  - agent_recipient_theme (someone gives someone something)
  - experiencer_stimulus (someone experiences something)
  - theme_only (something happens/exists)
  - agent_result (someone creates/produces something)
  - agent_instrument (someone uses something)
  - causative (someone causes something to happen)
  - inchoative (something becomes some state)
  - stative (something is in a state)
  - agent_patient_instrument (someone does something to something with something)

#### **aspect_type** (Verb-Specific Anchor)
- One aspect per meaning, array order matches meanings
- Use ONLY these controlled vocabulary terms:
  - activity (ongoing, no inherent endpoint: run, swim, work)
  - accomplishment (process with endpoint: build a house, write a letter)
  - achievement (instantaneous change: arrive, die, win)
  - state (no change: know, believe, own)
  - semelfactive (punctual, repeatable: knock, flash, cough)

#### **key_collocates** (Usage Anchor)
- Array of arrays matching meanings order
- 3-5 most distinctive word partners per meaning
- Include typical subjects, objects, prepositions, adverbs
- Choose collocates that DISTINGUISH this meaning from others
- Format: Single words or short phrases
- Examples:
  - Run (movement): ["quickly", "marathon", "miles", "athlete"]
  - Run (operate): ["business", "smoothly", "system", "program"]
  - Run (flow): ["water", "river", "tears", "blood"]

### JSON Output Structure

Generate entries in JSONL format (one JSON object per line):

```json
{
  "lemma": "lemma",
  "meanings": ["meaning1", "meaning2",...],
  "definitions": ["full definition 1", "full definition 2",...],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"],...],
  "frequency_meaning": [freq1, freq2,...],
  "grammatical_patterns": [["pattern1", "pattern2"], ["pattern1", "pattern2"],...],
  "semantic_roles": ["role1", "role2",...],
  "aspect_type": ["aspect1", "aspect2",...],
  "key_collocates": [["collocate1", "collocate2", "collocate3",...], ["collocate1", "collocate2", "collocate3",...],...]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- ALL arrays must align: if 4 meanings, then 4 definitions, 4 example pairs, 4 frequencies, 4 pattern sets, 4 roles, 4 aspects, 4 collocate sets
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]
- Grammatical_patterns is an array of arrays: [["V", "V + O"], ["V + that-clause"]]
- Key_collocates is an array of arrays: [["word1", "word2"], ["word1", "word2"]]


### Complete Example Output:

```json
{"lemma": "run", "meanings": ["move rapidly", "operate system", "manage organization", "flow continuously"], "definitions": ["move at a speed faster than walking by taking quick steps", "operate or cause a machine or system to function", "be in charge of and manage a business or organization", "flow or cause liquid to flow in a continuous stream"], "examples": [["She runs five miles every morning before breakfast", "The children ran across the playground laughing joyfully"], ["Can you run the dishwasher after dinner tonight?", "The new software runs much faster than before"], ["He successfully runs three restaurants in the city", "She has run the company for over ten years"], ["Water runs through these pipes into the tank", "Tears ran down her face during the movie"]], "frequency_meaning": [0.40, 0.25, 0.20, 0.15], "grammatical_patterns": [["V", "V + O"], ["V + O", "V"], ["V + O"], ["V", "V + prep"]], "semantic_roles": ["agent_only", "agent_patient", "agent_patient", "theme_only"], "aspect_type": ["activity", "activity", "activity", "activity"], "key_collocates": [["fast", "marathon", "athlete", "miles"], ["machine", "program", "smoothly", "system"], ["business", "company", "successfully", "organization"], ["water", "blood", "river", "stream"]]}
```

## Quality Checklist (Check before completing each batch)

✓ All meanings identified (including grammatical pattern variations)
✓ Physical vs. metaphorical uses properly separated
✓ Definitions meet minimum word counts (10+ for basic, 15+ for complex/technical)
✓ Examples are natural and 7+ words each
✓ Grammatical patterns correctly notated for each meaning
✓ Frequencies sum to exactly 1.0
✓ Semantic_roles use only controlled vocabulary
✓ Aspect_type uses only controlled vocabulary
✓ Key_collocates distinguish between meanings (3-5 per meaning)
✓ All arrays have matching lengths (if 4 meanings, then 4 of everything)
✓ Mark the checklist before continue to generate the content

## Important Reminders

- Different grammatical patterns often indicate different meanings
- Metaphorical uses of verbs are extremely common - check for them
- Aspect and semantic roles are crucial for understanding verb behavior
- Quality over speed: Each entry builds the foundation for comprehensive verb understanding
- Arrays must perfectly align - if 5 meanings, then 5 of everything
- This base structure allows future enhancement without conflicts

## Verb-Specific Considerations

- **Transitivity variations**: Same verb can be transitive/intransitive with different meanings
- **Causative/Inchoative pairs**: "break" (cause to break) vs "break" (become broken)
- **Aspect shifts**: Same verb can have different aspects in different uses
- **Metaphorical productivity**: Verbs extend metaphorically more than nouns
- **Argument structure**: Different arguments can signal different meanings

## Project Memories
- Base structure designed to prevent future adjustment conflicts
- Controlled vocabularies ensure consistency across entries
- Verb-specific fields capture grammatical and semantic complexity
- Extensible design allows adding features like tense forms, phrasal verb links, etc.