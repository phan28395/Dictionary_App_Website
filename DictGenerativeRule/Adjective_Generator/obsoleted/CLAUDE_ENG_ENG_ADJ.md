# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Merging Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the word

#### Step 2: Calculate Similarity
Meanings are considered >40% similar if they share:
- Core quality or characteristic described
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
- Simple descriptive adjectives: MIN 8 words (target: 8-15)
- Complex/abstract adjectives: MIN 15 words (target: 15-25)  
- Technical/specialized adjectives: MIN 15 words (target: 20-25)

❗ If your definition is too short, expand with:
- What quality it describes
- What it typically modifies
- How it differs from similar adjectives
- Common contexts

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English adjectives with detailed linguistic information. Each adjective entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Adjectives_Json/`
4. Generate content following the rules below

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

**meanings**
- Could have multiple
- Merge related meanings (definitions must be 40%+ different to avoid many similar meanings) 
- Arrange the order of meanings based on frequency of usage. Most common meaning should be first
- **FORMAT: Brief 3-5 word label only (NOT full definition)**
- ✅ CORRECT meanings format:
- Quality + Context: State the core quality + where/how it applies (e.g., "high in temperature", "emotionally content", "large in size")
- Use Simple Opposites: When helpful, reference common opposites - "opposite of slow", "lacking moisture" to clarify the quality being described

**definitions**
- Simple descriptive adjectives: 8-15 words, do not make shorter than 8 words
- Complex/abstract adjectives: 15-25 words, do not make shorter than 15 words
- Technical/specialized adjectives: 20-25 words max, do not make shorter than 15 words
- Core Formula: [Describes what quality] + [in what way/to what degree] + [typical context/comparison] 
- Expand to Meet Word Count: If too short, add: what it causes/implies, how it's perceived, what it's compared to, or when this quality typically appears

**examples**
- Everyday scenarios, culturally neutral
- Each example showing different uses/contexts
- Shows what the adjective typically modifies
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
  "lemma": "adjective",
  "meanings": ["meaning1", "meaning2"],
  "definitions": ["full definition 1", "full definition 2"],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"]],
  "frequency_meaning": ["frequency for meaning1", "frequency for meaning2"],
  "pos": "",
  "pos_frequency": ""}

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
{"lemma": "bright", "meanings": ["emitting strong light", "intelligent and quick", "vivid in color"], "definitions": ["giving out or reflecting much light that illuminates surroundings", "showing intelligence and mental alertness with quick understanding of things", "having strong, intense, or vivid color that catches attention"], "examples": [["The bright sun made it hard to see", "We need bright lights for the photography studio"], ["She's a bright student who learns concepts quickly", "His bright ideas helped solve the company's problems"], ["The artist used bright yellows and oranges in painting", "Children often prefer bright colors to dull ones"]], "frequency_meaning": [0.45, 0.35, 0.2]}
{"lemma": "hard", "meanings": ["solid and firm", "difficult to do", "severe or harsh"], "definitions": ["solid, firm, and resistant to pressure or force", "requiring great effort, skill, or endurance to accomplish or understand", "showing no sympathy or affection; severe in manner or effect"], "examples": [["The ground was hard after weeks without rain", "This mattress is too hard for comfortable sleeping"], ["Learning a new language is hard but rewarding", "The test was so hard that many students failed"], ["She gave him a hard look of disapproval", "It's been a hard winter with record snowfall"]], "frequency_meaning": [0.4, 0.45, 0.15],"pos": "", "pos_frequency": ""} 
```

## Project Structure

- `Adjectives_Json/`: JSONL output files organized by ranges (50 adjectives per file)
  - `lemmas_1_to_500/`: Files for adjectives 1-500
  - `lemmas_501_to_1000/`: Files for adjectives 501-1000
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