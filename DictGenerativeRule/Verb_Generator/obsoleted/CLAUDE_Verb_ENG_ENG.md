# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Merging Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the word

#### Step 2: Calculate Similarity
Meanings are considered >40% similar if they share:
- Core action or process
- Usage contexts
- Semantic relationships
- Functional purposes

#### Step 3: Merge Similar Meanings
If meanings are >40% similar, create ONE unified meaning that encompasses these similarities

#### Step 4: Only Split When Truly Distinct
Keep meanings separate ONLY when they:
- Have different semantic categories
- Require different grammatical patterns
- Belong to completely different domains
- Would confuse learners if combined

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Simple action verbs: MIN 10 words (target: 10-15)
- Complex/abstract verbs: MIN 15 words (target: 15-25)  
- Multi-faceted verbs: MIN 20 words (target: 20-25)

❗ If your definition is too short, expand with:
- What the action involves
- Who/what performs it
- What it affects/changes
- Common contexts

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English verbs with detailed linguistic information. Each verb entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Verbs_Json/`
4. Generate content following the rules below

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

**meanings**
- Could have multiple
- Merge related meanings (definitions must be 40%+ different to avoid many similar meanings) 
- Arrange the order of meanings based on frequency of usage. Most common meaning should be first
- ✅ CORRECT meanings format:
Action + Core Element: Start with a simple verb + what's affected/how it's done (e.g. "cut into pieces")
Avoid Abstract Words: Use everyday words a child would understand - "become hard" not "solidify", "look at carefully" not "scrutinize"
- FORMAT: Brief 3-5 word label only (NOT full definition)


**definitions**
- Simple action verbs: 10-15 words, do not make shorter than 10 words
- Complex/abstract verbs: 15-25 words, do not make shorter than 15 words
- Multi-faceted verbs: 20-25 words max, do not make shorter than 20 words
- Core Formula: [Action verb] + [who/what does it] + [what happens/changes] + [common context]
- Expand to Meet Word Count: If too short, add: how it's typically done, why it's done, what it affects, or when it commonly occurs 
**examples**
- Everyday scenarios, culturally neutral
- Each example showing different uses/contexts
- Shows common verb patterns naturally
- At least 6 words 
- Two examples for each meaning

**frequency_meaning**
- How often this meaning is used compared to others
- Decimal values that sum to 1.0
- Order matches the meanings order

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "verb",
  "meanings": ["meaning1", "meaning2"],
  "definitions": ["full definition 1", "full definition 2"],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"]],
  "frequency_meaning": ["frequency for meaning1", "frequency for meaning2"],
  "pos": "",
  "pos_frequency": ""
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- Arrays must align: if 2 meanings, then 2 definitions, 2 example pairs, 2 frequency values
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]

### Example Output:
```json
{"lemma": "run", "meanings": ["move quickly on feet", "operate or manage", "flow continuously"], "definitions": ["move at a speed faster than walking by taking quick steps with feet", "be in charge of and make decisions about how something operates or functions", "flow or move continuously in a steady stream like liquid"], "examples": [["She runs five miles every morning before work", "The children ran across the playground laughing joyfully"], ["My uncle has run the family restaurant for twenty years", "Who will run the company after the founder retires"], ["The river runs through the middle of our town", "Tears ran down her face during the emotional speech"]], "frequency_meaning": [0.5, 0.3, 0.2]}
{"lemma": "break", "meanings": ["separate into pieces", "stop functioning", "interrupt continuity"], "definitions": ["cause something to separate into parts or fragments suddenly or violently", "stop working properly or cease to function as intended", "interrupt the continuity or uniformity of something"], "examples": [["Be careful not to break the glass while washing it", "The branch broke under the weight of heavy snow"], ["My phone broke when I dropped it on concrete", "The old printer finally broke after years of use"], ["Let's break for lunch and continue the meeting later", "Don't break your concentration while studying for exams"]], "frequency_meaning": [0.45, 0.35, 0.2], "pos": "", "pos_frequency": ""} 
```

## Project Structure

- `Verbs_Json/`: JSONL output files organized by ranges (50 verbs per file)
  - `lemmas_1_to_500/`: Files for verbs 1-500
  - `lemmas_501_to_1000/`: Files for verbs 501-1000
  - [Additional folders as needed]
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