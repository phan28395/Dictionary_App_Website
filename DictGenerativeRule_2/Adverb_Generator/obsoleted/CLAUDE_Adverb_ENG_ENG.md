# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Meaning Organization for Adverbs (MANDATORY)
**Adverbs modify verbs, adjectives, other adverbs, or entire sentences. Organize by what they modify and type of information:**

#### Function Categories (in order):
1. Manner (how something happens)
2. Time/Frequency (when/how often)
3. Place/Direction (where)
4. Degree/Intensity (how much)
5. Sentence modification (speaker's comment)

#### When to Merge vs. Split Meanings
- Merge if modifying the same element type with similar information
- Split if modifying different elements (verb vs. adjective)
- Split if different categories (manner vs. degree)
- Common adverbs may have 2-4 distinct uses

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Simple manner/place adverbs: MIN 8 words (target: 8-12)
- Time/frequency adverbs: MIN 10 words (target: 10-15)
- Degree/intensity adverbs: MIN 10 words (target: 10-15)
- Sentence adverbs: MIN 12 words (target: 12-18)
- Multi-function adverbs: MIN 12 words (target: 12-18)

❗ If your definition is too short, expand with:
- What element it modifies (verb/adjective/adverb/sentence)
- What information it adds
- Common positions in sentences
- Similar adverbs for contrast

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English adverbs with detailed linguistic information. Each adverb entry includes meanings, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Adverbs_Json/`
4. Generate content following the rules below

## Adverb Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a precision-minded language coach who explains adverbs by showing what they modify and what information they add. You help learners see how adverbs fine-tune meaning in sentences.
 </role>

 <context>
   - You always specify what the adverb modifies
   - You group related uses while distinguishing different functions
   - You show position flexibility when it matters
   - You use clear examples that highlight the adverb's role
   - You note when forms overlap with adjectives
   - You explain degree adverbs by their intensifying or reducing effect
 </context>
</persona>

### Fields to Generate

**meanings**
- Most adverbs have 1-3 meanings
- Organize by function type and what they modify
- Manner adverbs often have single meaning
- Position/time adverbs may have multiple uses
- **FORMAT: Brief 3-5 word label only**
- ✅ CORRECT meanings format:
  - quickly: ["in fast manner"]
  - very: ["intensifying degree"]
  - here: ["at this place", "at this point"]
  - however: ["showing contrast", "in whatever way"]

**definitions**
- Simple manner/place: 8-12 words
- Time/frequency: 10-15 words
- Degree/intensity: 10-15 words
- Sentence adverbs: 12-18 words
- Specify what element is modified

**examples**
- Show the adverb modifying its typical target
- Vary positions when flexible
- Include common collocations
- Contrast with similar adverbs when helpful
- At least 6 words per example
- Two examples for each meaning

**frequency_meaning**
- Primary function usually most frequent
- Decimal values that sum to 1.0
- Order matches the meanings order

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "adverb",
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
{"lemma": "quickly", "meanings": ["in fast manner"], "definitions": ["moving or happening with great speed or in short time"], "examples": [["She quickly finished her homework before dinner", "Please respond quickly to this urgent message"]], "frequency_meaning": [1.0]}
{"lemma": "very", "meanings": ["intensifying degree"], "definitions": ["used to emphasize adjectives and adverbs to a high degree"], "examples": [["The movie was very interesting", "She speaks very quietly in the library"]], "frequency_meaning": [1.0]}
{"lemma": "often", "meanings": ["frequently occurring"], "definitions": ["happening many times or on many occasions; frequently"], "examples": [["We often go hiking on weekends", "She often forgets to bring her lunch"]], "frequency_meaning": [1.0]}
{"lemma": "here", "meanings": ["at this place", "at this point"], "definitions": ["in, at, or to this place or position", "at this point in a process, activity, or discussion"], "examples": [["Please sit here next to me", "I've lived here for ten years"], ["Here we need to consider the costs", "Here the author makes an important point"]], "frequency_meaning": [0.8, 0.2]}
{"lemma": "however", "meanings": ["showing contrast", "in whatever way"], "definitions": ["used to introduce a statement that contrasts with something previously said", "in whatever way or to whatever degree"], "examples": [["The plan sounds good; however, it's too expensive", "We tried hard; however, we didn't succeed"], ["However you do it, be careful", "However difficult it is, keep trying"]], "frequency_meaning": [0.85, 0.15]}
```

## Special Considerations for Adverbs

### Form Overlaps
- Note when adverb has same form as adjective (fast, hard, early)
- Clarify the adverb function in definition
- Examples should clearly show adverbial use

### Position Flexibility
- Show different positions in examples when relevant
- Beginning: "Unfortunately, we're late"
- Middle: "We unfortunately are late"
- End: "We're late, unfortunately"

### Degree Adverbs
- These primarily modify adjectives/adverbs
- Focus on intensifying or diminishing effect
- Common with gradable adjectives

### Sentence Adverbs
- Modify entire sentence, not just one element
- Express speaker's attitude or comment
- Usually set off by commas

## Project Structure

- `Adverbs_Json/`: JSONL output files organized by type or alphabetically
  - `manner_adverbs.json`
  - `time_frequency_adverbs.json`
  - `degree_adverbs.json`
  - `other_adverbs.json`
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