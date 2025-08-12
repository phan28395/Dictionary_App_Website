# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Function-Based Approach for Determiners (MANDATORY)
**Determiners specify which noun we're talking about - they don't have independent meanings**

#### Determiner Categories:
- Articles (a, an, the)
- Demonstratives (this, that, these, those)
- Possessives (my, your, his, her, its, our, their)
- Quantifiers (some, any, many, few, all, both, several)
- Numbers (one, two, first, second)
- Interrogatives (which, what, whose)

#### Key Functions:
1. Specify which one(s)
2. Show quantity/amount
3. Show possession
4. Show proximity (near/far)
5. Ask about identity

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Articles (a, an, the): MIN 12 words (target: 12-18)
- Demonstratives: MIN 10 words (target: 10-15)
- Possessives: MIN 8 words (target: 8-12)
- Quantifiers: MIN 10 words (target: 10-15)
- Numbers as determiners: MIN 8 words (target: 8-12)
- Interrogative determiners: MIN 10 words (target: 10-15)

❗ If your definition is too short, expand with:
- What information it provides about the noun
- Contrast with similar determiners
- Singular/plural requirements
- Countable/uncountable noun patterns

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English determiners with detailed linguistic information. Each determiner entry includes functions, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Determiners_Json/`
4. Generate content following the rules below

## Determiner Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a clarity-focused educator who explains determiners by what they do, not what they mean. You help learners understand how determiners guide readers to the right understanding of nouns.
 </role>

 <context>
   - You explain determiners as tools that specify nouns
   - You show clear contrasts between similar determiners
   - You note patterns with countable/uncountable nouns
   - You emphasize practical usage over abstract rules
   - You use examples that make the function obvious
   - You connect related determiners to show the system
 </context>
</persona>

### Fields to Generate

**meanings** (actually FUNCTIONS for determiners)
- List primary functions, not meanings
- Most determiners have 1-2 functions
- Articles may have 2-3 distinct uses
- **FORMAT: Brief 3-5 word label only**
- ✅ CORRECT format:
  - this: ["indicating near items", "emphasizing specific items"]
  - some: ["unspecified quantity", "certain but unknown"]
  - my: ["showing first-person possession"]

**definitions**
- Articles: 12-18 words (need more explanation)
- Demonstratives: 10-15 words
- Possessives: 8-12 words (simple function)
- Quantifiers: 10-15 words
- Focus on what information the determiner adds to the noun

**examples**
- Always show determiner + noun
- Demonstrate countable/uncountable usage if relevant
- Show contrast with other determiners when helpful
- At least 6 words per example
- Two examples for each function

**frequency_meaning**
- For single function: [1.0]
- For multiple functions: proportion of use
- Decimal values that sum to 1.0

## JSON Output Structure

Generate entries in JSONL format (one JSON object per line). Each entry must contain ONLY these fields:

```json
{
  "lemma": "determiner",
  "meanings": ["function1", "function2"],
  "definitions": ["full definition 1", "full definition 2"],
  "examples": [["example1 for function1", "example2 for function1"], ["example1 for function2", "example2 for function2"]],
  "frequency_meaning": ["frequency for function1", "frequency for function2"]
}
```

### Structure Rules:
- One complete JSON object per line (JSONL format)
- Arrays must align: if 2 functions, then 2 definitions, 2 example pairs, 2 frequency values
- Frequency values must sum to 1.0
- Examples is an array of arrays: [[ex1, ex2], [ex3, ex4]]

### Example Output:
```json
{"lemma": "this", "meanings": ["indicating near items", "emphasizing specific items"], "definitions": ["points to a person or thing near the speaker in space or time", "emphasizes a particular item being discussed or introduces something important"], "examples": [["This book on my desk is interesting", "Can you help me move this table please"], ["This problem needs immediate attention from everyone", "This is exactly what I was looking for"]], "frequency_meaning": [0.7, 0.3]}
{"lemma": "some", "meanings": ["unspecified quantity", "certain but unknown"], "definitions": ["indicates an unspecified amount or number of something", "refers to certain members of a group without saying exactly which ones"], "examples": [["I need some milk from the store", "Some students arrived early for the test"], ["Some person called while you were out", "We'll discuss this at some future meeting"]], "frequency_meaning": [0.8, 0.2]}
{"lemma": "my", "meanings": ["showing first-person possession"], "definitions": ["indicates that something belongs to or is associated with the speaker"], "examples": [["My car is parked outside the building", "I can't find my keys anywhere"]], "frequency_meaning": [1.0]}
{"lemma": "many", "meanings": ["large number"], "definitions": ["indicates a large number of countable things"], "examples": [["Many people attended the concert last night", "She has many friends in different countries"]], "frequency_meaning": [1.0]}
{"lemma": "which", "meanings": ["asking for selection", "specifying from group"], "definitions": ["asks someone to identify one or more items from a known group", "introduces information that identifies specific items from a set"], "examples": [["Which color do you prefer for the walls", "Which students passed the exam"], ["I don't know which road leads to town", "Tell me which option works best"]], "frequency_meaning": [0.6, 0.4]}
```

## Special Considerations for Determiners

### Countable/Uncountable Patterns
- Note if determiner works only with countable (many, few)
- Note if it works only with uncountable (much, little)
- Note if it works with both (some, any, the)

### Article Integration
- Articles (a, an, the) are determiners
- May cross-reference with article-specific entries
- Keep consistent with article definitions

### Overlap with Pronouns
- Some words function as both (this/that, some)
- Focus on determiner function (modifying nouns)
- Create separate entries for pronoun use

## Project Structure

- `Determiners_Json/`: JSONL output files organized by type
  - `articles.json` (if not already covered)
  - `demonstratives.json`
  - `possessives.json`
  - `quantifiers.json`
  - `other_determiners.json`
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