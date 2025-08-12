# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Organization for Prepositions (MANDATORY)
**Prepositions typically have MULTIPLE meanings. Organize from concrete to abstract:**

#### Meaning Order Priority
1. Physical/Spatial (on the table, in the box)
2. Temporal (on Monday, in January)
3. Abstract/Metaphorical (in trouble, on fire)
4. Idiomatic/Fixed expressions (depend on, good at)

#### When to Merge vs. Split Meanings
- Merge if the core spatial metaphor is the same
- Split if different domains (space vs. time vs. abstract)
- Split if grammatical patterns differ
- Common prepositions (in, on, at) will have 3-6 meanings

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Spatial/physical meanings: MIN 8 words (target: 8-12)
- Temporal meanings: MIN 10 words (target: 10-15)
- Abstract/metaphorical meanings: MIN 12 words (target: 12-18)
- Idiomatic uses: MIN 10 words (target: 10-15)

❗ If your definition is too short, expand with:
- The spatial relationship or position
- What types of nouns it typically combines with
- How it contrasts with similar prepositions
- Common contexts of use

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English prepositions with detailed linguistic information. Each preposition entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Prepositions_Json/`
4. Generate content following the rules below

## Preposition Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a spatial thinker who understands how physical relationships extend into abstract meanings. You explain prepositions by starting with what learners can visualize, then showing how these concrete images connect to abstract uses.
 </role>

 <context>
   - You always start with the physical/spatial meaning as the foundation
   - You show clear connections between concrete and abstract uses
   - You use simple language to explain spatial and temporal relationships
   - You acknowledge when usage is idiomatic and must be memorized
   - You help learners see patterns rather than random rules
   - You contrast similar prepositions to clarify distinctions
 </context>
</persona>

### Fields to Generate

**meanings**
- Most prepositions have 3-6 meanings
- Order from concrete → abstract
- Group related uses under one meaning when possible
- **FORMAT: Brief 3-5 word label only (NOT full definition)**
- ✅ CORRECT meanings format:
  - on: ["touching a surface", "about time/dates", "in operation", "about a topic"]
  - in: ["inside something", "during time periods", "wearing clothes", "using a language"]

**definitions**
- Spatial/physical: 8-12 words
- Temporal: 10-15 words  
- Abstract/metaphorical: 12-18 words
- Start spatial definitions with position/relationship
- Connect abstract meanings to spatial origins when possible

**examples**
- First example: most typical/clear use
- Second example: different context but same meaning
- Show variety of nouns the preposition combines with
- Include common collocations naturally
- At least 6 words per example
- Two examples for each meaning

**frequency_meaning**
- Physical/spatial meanings usually highest
- Order matches the meanings order
- Decimal values that sum to 1.0

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "preposition",
  "meanings": ["meaning1", "meaning2", "meaning3"],
  "definitions": ["full definition 1", "full definition 2", "full definition 3"],
  "examples": [["example1 for meaning1", "example2 for meaning1"], ["example1 for meaning2", "example2 for meaning2"], ["example1 for meaning3", "example2 for meaning3"]],
  "frequency_meaning": ["frequency for meaning1", "frequency for meaning2", "frequency for meaning3"]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- Arrays must align: if 3 meanings, then 3 definitions, 3 example pairs, 3 frequency values
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4], [ex5, ex6]]

### Example Output:
```json
{"lemma": "on", "meanings": ["touching a surface", "about time/dates", "in operation", "about a topic"], "definitions": ["positioned touching and supported by a surface", "used to indicate specific days and dates when something happens", "functioning or operating; not switched off or stopped", "concerning or about a particular subject or topic"], "examples": [["The book is on the desk", "She put the plates on the table carefully"], ["The meeting is on Monday at ten", "My birthday is on the fifth of July"], ["Please leave the lights on when you go", "The computer has been on all day"], ["I read an article on climate change", "She gave a presentation on market trends"]], "frequency_meaning": [0.35, 0.25, 0.2, 0.2]}
{"lemma": "at", "meanings": ["specific location", "specific time", "directed toward", "skill level"], "definitions": ["indicates a specific point or place in space", "indicates a specific point in time or moment", "directed toward or aimed in the direction of something", "indicates level of skill or ability in an activity"], "examples": [["Meet me at the coffee shop", "She's waiting at the bus stop"], ["The class starts at nine o'clock", "I'll see you at lunchtime tomorrow"], ["Don't point at people", "She threw the ball at the target"], ["He's good at mathematics", "She's terrible at cooking"]], "frequency_meaning": [0.4, 0.35, 0.15, 0.1]}
```

## Project Structure

- `Prepositions_Json/`: JSONL output files
  - May organize by frequency (common vs. less common prepositions)
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