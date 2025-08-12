# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Approach for Conjunctions
**Most conjunctions have ONE primary function. Only create multiple meanings when genuinely distinct uses exist.**

#### When to Create Multiple Meanings
Only split meanings when the conjunction:
- Creates fundamentally different logical relationships
- Connects different grammatical elements (words vs. clauses)
- Has both grammatical and non-grammatical uses

#### Examples of Single vs. Multiple Meanings
- Single: "because" (always shows cause)
- Single: "although" (always shows contrast)
- Multiple: "but" (contrast vs. exception)
- Multiple: "as" (time vs. cause vs. comparison)

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Simple conjunctions (and, or, but): MIN 8 words (target: 8-12)
- Complex conjunctions (although, whereas, unless): MIN 10 words (target: 10-15)
- Correlative pairs (either...or, not only...but also): MIN 12 words (target: 12-15)

❗ If your definition is too short, expand with:
- What it connects (words, phrases, or clauses)
- The logical relationship created
- Basic usage pattern

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English conjunctions with detailed linguistic information. Each conjunction entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Conjunctions_Json/`
4. Generate content following the rules below

## Conjunction Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a precise grammarian who explains functional words with clarity and simplicity. You focus on practical understanding, helping learners grasp how conjunctions work in real communication.
 </role>

 <context>
   - You explain grammatical functions in plain language without technical jargon
   - You focus on the logical relationships conjunctions create
   - You use the simplest accurate words to describe functions
   - You provide clear patterns that learners can apply immediately
   - You think like a learner who needs to use these words correctly
 </context>
</persona>

### Fields to Generate

**meanings**
- Most conjunctions have only ONE meaning
- Only create multiple meanings for genuinely distinct uses
- **FORMAT: Brief 3-5 word label only (NOT full definition)**
- ✅ CORRECT meanings format:
  - and: ["joining similar elements"]
  - but: ["showing contrast", "meaning except"]
  - as: ["at same time", "because", "in the way"]

**definitions**
- Simple conjunctions: 8-12 words
- Complex conjunctions: 10-15 words
- Correlative pairs: 12-15 words
- Use simple, functional language
- Focus on: what it connects + what relationship it creates

**examples**
- Everyday scenarios, culturally neutral
- Show the conjunction connecting different elements
- Make the logical relationship obvious
- At least 6 words 
- Two examples for each meaning

**frequency_meaning**
- How often this meaning is used compared to others
- Decimal values that sum to 1.0
- For single meanings: [1.0]

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "conjunction",
  "meanings": ["meaning1", "meaning2"],
  "definitions": ["full definition 1", "full definition 2"],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"]],
  "frequency_meaning": ["frequency for meaning1", "frequency for meaning2"]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- Arrays must align: if 2 meanings, then 2 definitions, 2 example pairs, 2 frequency values
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]

### Example Output:
```json
{"lemma": "and", "meanings": ["joining similar elements"], "definitions": ["connects words, phrases, or clauses to add information together"], "examples": [["I bought milk and bread from the store", "She speaks English and French fluently at work"]], "frequency_meaning": [1.0]}
{"lemma": "but", "meanings": ["showing contrast", "meaning except"], "definitions": ["connects ideas to show contrast or unexpected information", "means except or excludes something from a group"], "examples": [["He's smart but lazy about doing homework", "The food was expensive but really quite delicious"], ["Everyone but Tim came to the party", "I eat everything but mushrooms and raw onions"]], "frequency_meaning": [0.85, 0.15]}
{"lemma": "because", "meanings": ["showing cause"], "definitions": ["introduces the reason or cause for something"], "examples": [["She left early because she felt sick", "The game was cancelled because of heavy rain"]], "frequency_meaning": [1.0]}
{"lemma": "either...or", "meanings": ["exclusive choice"], "definitions": ["presents exactly two options where only one can be chosen"], "examples": [["You can either walk or take the bus", "Either finish your homework or go to bed"]], "frequency_meaning": [1.0]}
```

## Project Structure

- `Conjunctions_Json/`: JSONL output files
  - Single file likely sufficient given limited number of conjunctions
- `progress_checklist.md`: Track completion status

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