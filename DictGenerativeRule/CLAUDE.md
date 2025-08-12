# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Merging Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the word, including:
- Technical/professional terms (medical, legal, computing, etc.)
- Named entities (games, brands, specific objects)
- Domain-specific uses (music, sports, trades)

#### Step 2: Calculate Similarity
Meanings are considered >40% similar if they share:
- Core conceptual features
- Usage contexts  
- Semantic relationships
- Functional purposes

**EXCEPTION - Never merge these even if conceptually similar:**
- Terms from different professional domains (dental bridge vs construction bridge)
- Named entities or proper nouns used as common nouns (Bridge the card game)
- Technical jargon that has specific meaning in a field (bridge in music, bridge in networking)
- When the same word refers to completely different physical objects

#### Step 3: Merge Similar Meanings
If meanings are >40% similar AND not exceptions above, create ONE unified meaning that encompasses these similarities

#### Step 4: Only Split When Truly Distinct
Keep meanings separate when they:
- Have different semantic categories
- Require different grammatical patterns
- Belong to completely different professional/technical domains
- Are specific games, activities, or named entities
- Would confuse learners if combined
- Refer to different concrete objects (even if functionally similar)

**Examples of meanings that MUST stay separate:**
- Bridge (structure) vs Bridge (dental prosthesis) vs Bridge (card game) - different entities
- Bank (financial) vs Bank (riverside) - unrelated origins
- Bat (animal) vs Bat (sports equipment) - different objects
- Spring (season) vs Spring (coil) vs Spring (water source) - distinct entities

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Simple concrete nouns: MIN 8 words (target: 8-15)
- Abstract concepts: MIN 15 words (target: 15-25)  
- Technical terms: MIN 15 words (target: 20-25)

❗ If your definition is too short, expand with:
- Purpose/function
- Distinguishing features
- Common contexts
- Related concepts

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of 2,635 English nouns with detailed linguistic information. Each noun entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Nouns_Json/`
4. Generate content following the rules below

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

**meanings**
- Could have multiple
- Check for common technical/professional uses (medical, dental, computing, music, etc.)
- Check for games or activities that share the word name
- Merge related meanings (definitions must be 40%+ different to avoid many similar meanings, BUT see exceptions in Step 2 above) 
- Arrange the order of meanings based on frequency of usage. Most common meaning should be first
- **FORMAT: Brief 3-5 word label only (NOT full definition)**
- ✅ CORRECT meanings format:
  - Thing + Core Purpose: State what it is + its main function/type (e.g., "furniture for sitting", "container for liquids", "tool for cutting")
  - For technical terms: Include the domain hint (e.g., "dental replacement device", "musical transition section")
  - For games/activities: Be explicit (e.g., "card game", "board game")
  - Keep It Concrete: Use physical descriptors when possible - "flat dining surface" not "horizontal plane", "leadership position" not "authoritative role"

**definitions**
- Simple concrete nouns: 8-15 words, do not make shorter than 8 words. 
- Abstract concepts: 15-25 words, do not make shorter than 15 words. 
- Technical terms: 20-25 words max, do not make shorter than 15 words.
- Core Formula: [What it is] + [key characteristic/purpose] + [distinguishing feature]
- Expand to Meet Word Count: If too short, add: what it's made of/from, where it's found/used, how it relates to similar things, or what makes it unique 

**examples**
- Everyday scenarios, culturally neutral when possible
- For technical/professional meanings: Use accessible professional contexts
- Each example showing different uses/contexts
- Shows common verb partners and prepositions naturally
- At least 6 words 
- Two examples for each meaning

**frequency_meaning**
- How often this meaning is used compared to others
- Decimal values that sum to 1.0
- Order matches the meanings order
- Consider professional/technical uses may be common in their domains

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "word",
  "meanings": ["meaning1", "meaning2",...],
  "definitions": ["full definition 1", "full definition 2",...],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"],...],
  "frequency_meaning": ["frequency for meaning1", "frequency for meaning2",...]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- Arrays must align: if 2 meanings, then 2 definitions, 2 example pairs, 2 frequency values
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]
- pos is always empty
- pos_frequency is always empty

### Example Output:
```json
{"lemma": "table", "meanings": ["flat dining surface", "data arrangement"], "definitions": ["flat surface with legs for putting things on", "organized arrangement of data in rows and columns"], "examples": [["We gathered around the kitchen table for dinner", "The wooden table needs to be polished regularly"], ["The data is displayed in a simple table format", "Check the table on page five for details"]], "frequency_meaning": [0.7, 0.3]}
{"lemma": "chair", "meanings": ["furniture for sitting", "leadership position"], "definitions": ["piece of furniture with back support designed for one person to sit on", "position of authority or leadership in an organization or committee"], "examples": [["Please take a chair and make yourself comfortable", "She bought four matching chairs for the dining room"], ["Professor Smith was appointed chair of the history department", "The committee chair called the meeting to order promptly"]], "frequency_meaning": [0.85, 0.15]}
```

## Project Structure

- `Nouns_Json/`: JSONL output files organized by ranges (50 nouns per file)
- `progress_checklist.md`: Track completion status of each batch

## Important Reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless they're absolutely necessary for achieving your goal
- ALWAYS prefer editing an existing file to creating a new one
- NEVER proactively create documentation files (*.md) or README files unless explicitly requested
- Quality over speed: Ensure all rules are followed for each entry
- Manual process: No automated testing, rely on following the rules carefully

## Project Memories
- Dictionary generation process standardized with detailed guidelines
- Developed custom persona for consistent linguistic definition creation