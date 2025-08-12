# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🔴 CRITICAL RULES - MUST READ FIRST

### Function-Based Approach for Pronouns (MANDATORY)
**Pronouns don't have "meanings" - they have grammatical functions and referential uses**

#### Instead of Multiple Meanings, Identify:
1. Grammatical roles (subject/object/possessive)
2. What/whom they refer to
3. Special usage contexts
4. Form variations if applicable

#### Pronoun Categories:
- Personal (I, you, he, she, it, we, they)
- Possessive (mine, yours, his, hers, its, ours, theirs)
- Reflexive (myself, yourself, himself, herself, itself, ourselves, themselves)
- Demonstrative (this, that, these, those)
- Relative (who, which, that, whom, whose)
- Interrogative (who, what, which, whose, whom)
- Indefinite (someone, anyone, nothing, everybody, etc.)

### Word Count Requirements (MANDATORY)

**EVERY definition MUST meet these minimums:**
- Personal/Possessive pronouns: MIN 8 words (target: 8-12)
- Reflexive/Demonstrative: MIN 10 words (target: 10-15)
- Relative/Interrogative: MIN 12 words (target: 12-18)
- Indefinite pronouns: MIN 10 words (target: 10-15)

❗ If your definition is too short, expand with:
- What/whom it refers to
- When to use it (not other forms)
- Grammatical position (subject/object)
- Any usage restrictions

**EVERY example MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project generates a comprehensive dictionary of English pronouns with detailed linguistic information. Each pronoun entry includes functions, definitions, examples, and frequency data in JSONL format.

## Development Workflow

### Content Generation Process
1. Check `progress_checklist.md` for next uncompleted batch (marked with `[ ]`)
2. Mark batch as complete in `progress_checklist.md` with `[x]`
3. Open the corresponding JSON file in `Pronouns_Json/`
4. Generate content following the rules below

## Pronoun Dictionary Entry Generation Rules

### Persona Generator
<persona>
 <role>
   You are a practical grammar guide who explains pronouns by their function, not abstract meaning. You focus on helping learners use pronouns correctly in real communication.
 </role>

 <context>
   - You explain what pronouns refer to and when to use them
   - You clarify differences between related forms (I/me/my/mine)
   - You note important usage contexts (formal/informal, subject/object)
   - You acknowledge evolving usage respectfully
   - You use clear examples to show correct placement and usage
   - You avoid technical grammar terms when simple explanations work
 </context>
</persona>

### Fields to Generate

**meanings** (actually FUNCTIONS for pronouns)
- List grammatical functions or uses, not "meanings"
- Most pronouns have 1-2 primary functions
- For pronouns with forms (I/me/my), treat base form only
- **FORMAT: Brief 3-5 word label only**
- ✅ CORRECT format:
  - I: ["first person subject"]
  - who: ["questioning about people", "relating clauses about people"]
  - someone: ["unknown or unspecified person"]

**definitions**
- Personal/Possessive: 8-12 words
- Reflexive/Demonstrative: 10-15 words
- Relative/Interrogative: 12-18 words
- Focus on: what it refers to + when to use it
- Note subject/object position if relevant

**examples**
- Show correct grammatical position
- Demonstrate typical usage patterns
- Include formal/informal contexts if relevant
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
  "lemma": "pronoun",
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
{"lemma": "I", "meanings": ["first person subject"], "definitions": ["pronoun used by a speaker to refer to himself or herself as the subject"], "examples": [["I want to go home now", "I think this is the right answer"]], "frequency_meaning": [1.0]}
{"lemma": "me", "meanings": ["first person object"], "definitions": ["pronoun used by a speaker to refer to himself or herself as the object"], "examples": [["Can you help me with this", "She gave me the book yesterday"]], "frequency_meaning": [1.0]}
{"lemma": "who", "meanings": ["questioning about people", "relating clauses about people"], "definitions": ["interrogative pronoun used to ask which person or people", "relative pronoun introducing clauses that give information about people"], "examples": [["Who is coming to the party tonight", "Who left this bag here"], ["The woman who lives next door is friendly", "Students who study hard usually do well"]], "frequency_meaning": [0.4, 0.6]}
{"lemma": "someone", "meanings": ["unknown or unspecified person"], "definitions": ["refers to an unspecified or unknown person"], "examples": [["Someone left their umbrella in the office", "I need someone to help me move tomorrow"]], "frequency_meaning": [1.0]}
{"lemma": "myself", "meanings": ["reflexive first person"], "definitions": ["reflexive pronoun used when the speaker is both subject and object of the action"], "examples": [["I taught myself how to play guitar", "I looked at myself in the mirror"]], "frequency_meaning": [1.0]}
```

## Special Considerations for Pronouns

### Form Variations
- For pronouns with multiple forms (I/me/my/mine), create separate entries
- Each form has its own grammatical function
- Cross-reference related forms in examples

### Usage Notes
- Note formal/informal distinctions where relevant
- Acknowledge singular "they" as accepted usage
- Be respectful about evolving pronoun usage

## Project Structure

- `Pronouns_Json/`: JSONL output files 

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