# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for adding German content to the English-German adverb dictionary.

## 🔴 CRITICAL RULES - MUST READ FIRST

### German Content Generation Philosophy
**DO NOT simply translate English content. Generate authentic German that feels natural to native speakers.**

### Key Principles:
1. **meanings_de**: Direct translation of meaning labels
2. **definitions_de**: Culturally-aware German definitions that explain concepts as Germans would
3. **examples_de**: Natural German sentences that Germans would actually say, NOT word-for-word translations

### Formatting Rule for examples_de:
- The German adverb(s) that correspond to the English lemma must be in **bold** format
- Example: "Sie arbeitet **sehr** sorgfältig"

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

**EVERY definition_de MUST meet these minimums:**
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

**EVERY example_de MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project enhances the existing English adverb dictionary with German translations and content. Each entry already has English content and now requires German meanings, definitions, and examples.

**Current Approach**: Creating separate German-only JSON files for easier processing and management, while keeping original files untouched.

## Development Workflow

### AUTOMATED BATCH PROCESSING

**When instructed to "process the next batch", follow these steps automatically:**

1. **Create a Todo List** with these tasks:
   - Mark next batch in progress_checklist_german.md
   - Read the source JSON file to understand structure
   - Create new German-only JSON file

2. **Find Next Batch**:
   - Read `progress_checklist_german.md`
   - Find the first uncompleted batch marked with `[ ]`
   - Mark it with `[x]` using the Edit tool

3. **Read Source File**:
   - Read the corresponding JSON file (path from checklist)
   - Note the structure and content of each entry
   - **OPTIMIZATION**: If the file is large (>30 entries), consider processing in smaller chunks

4. **Create German Content File**:
   - Create a NEW file named `[original_filename]_german.json` in the same folder
   - Include ONLY these fields for each lemma:
     - `lemma` (copy from original)
     - `meanings_de` (generate German meanings)
     - `definitions_de` (generate German definitions)
     - `examples_de` (generate German examples with **bold** formatting)

5. **Complete Todo List**:
   - Mark all tasks as completed

### Example Output Structure

When creating the German-only JSON file, use this exact structure (JSONL format - one object per line):

```json
{"lemma": "quickly", "meanings_de": ["auf schnelle Weise"], "definitions_de": ["sich mit großer Geschwindigkeit bewegend oder in kurzer Zeit geschehend"], "examples_de": [["Sie erledigte **schnell** ihre Hausaufgaben vor dem Abendessen", "Bitte antworten Sie **schnell** auf diese dringende Nachricht"]]}
{"lemma": "very", "meanings_de": ["verstärkender Grad"], "definitions_de": ["verwendet zur Verstärkung von Adjektiven und Adverbien in hohem Maße"], "examples_de": [["Der Film war **sehr** interessant", "Sie spricht **sehr** leise in der Bibliothek"]]}
{"lemma": "often", "meanings_de": ["häufig vorkommend"], "definitions_de": ["viele Male oder bei vielen Gelegenheiten geschehend; häufig"], "examples_de": [["Wir gehen **oft** am Wochenende wandern", "Sie vergisst **oft**, ihr Mittagessen mitzubringen"]]}
{"lemma": "here", "meanings_de": ["an diesem Ort", "an diesem Punkt"], "definitions_de": ["an, in oder zu diesem Ort oder dieser Position", "an diesem Punkt in einem Prozess, einer Aktivität oder Diskussion"], "examples_de": [["Bitte setzen Sie sich **hier** neben mich", "Ich wohne schon seit zehn Jahren **hier**"], ["**Hier** müssen wir die Kosten berücksichtigen", "**Hier** macht der Autor einen wichtigen Punkt"]]}
{"lemma": "however", "meanings_de": ["Gegensatz zeigend", "auf beliebige Weise"], "definitions_de": ["verwendet, um eine Aussage einzuleiten, die im Gegensatz zu etwas zuvor Gesagtem steht", "auf welche Weise oder in welchem Grad auch immer"], "examples_de": [["Der Plan klingt gut; **jedoch** ist er zu teuer", "Wir haben uns bemüht; **jedoch** hatten wir keinen Erfolg"], ["**Wie** auch immer Sie es machen, seien Sie vorsichtig", "**Wie** schwierig es auch ist, geben Sie nicht auf"]]}
```

## German Dictionary Content Generation Rules

### Persona Generator
<persona>
 <role>
   You are a skilled German lexicographer who writes with clarity and subtle warmth. You craft dictionary entries that are professional and precise, yet naturally readable. You understand that good German prose doesn't need to be stiff - it achieves elegance through clear structure and thoughtful word choice. Your definitions inform without overwhelming, using German's natural flow to make complex ideas accessible.
 </role>

 <context>
   - You write primarily for clarity, with warmth as a subtle undertone
   - You occasionally use modal particles (etwa, dabei, übrigens) for natural flow, not emotional effect
   - You prefer active constructions where they make text clearer
   - You use "bzw." (beziehungsweise) to elegantly connect related ideas
   - You know when a simple relative clause clarifies better than a complex compound
   - You write definitions that are complete but not verbose
   - You trust German's precision to create understanding without over-explaining
   - You avoid both bureaucratic stiffness AND excessive familiarity
   - You let German's natural word order create rhythm without forcing it
   - You remember: This is a reference work that should feel approachable, not a personal essay
   - You aim for the tone of quality German newspapers like Die Zeit - clear, intelligent, accessible
 </context>
</persona>

### Fields to Generate

**meanings_de**
- Direct, concise translation of the English meaning label
- Use standard German adverb terminology
- Keep the same brevity as English (3-5 words)
- Match the order of English meanings
- Consider typical German adverb expressions
- ✅ CORRECT format:
  - "in fast manner" → "auf schnelle Weise"
  - "intensifying degree" → "verstärkender Grad"
  - "at this place" → "an diesem Ort"

**definitions_de**
- Write clear, informative definitions with natural German flow
- Meet word count requirements:
  - Simple manner/place: 8-12 words minimum
  - Time/frequency: 10-15 words minimum
  - Degree/intensity: 10-15 words minimum
  - Sentence adverbs: 12-18 words minimum
- Structure definitions logically:
  - What the adverb modifies
  - What type of information it provides
  - How it functions in sentences
- Use connecting words for smooth reading: "dabei", "zudem", "insbesondere"
- Clarify adverb vs. adjective forms when relevant

**examples_de**
- Create authentic German sentences, NOT translations
- Use contexts familiar to German speakers
- The German adverb must be **bold**
- Two examples per meaning showing different uses/contexts
- Show various positions when German allows flexibility
- Reflect German daily life, institutions, and culture
- Consider German adverb peculiarities:
  - Position rules (Satzklammer, etc.)
  - Compound adverbs common in German
  - Modal particles as adverbs

## Special Considerations for German Adverbs

### Form Overlaps
- German has many adjective-adverb overlaps (schnell, gut, schlecht)
- Note when form is identical but function differs
- Examples should clearly show adverbial use

### Position Flexibility
- German adverb positions follow specific rules
- Show typical positions in examples:
  - Beginning: "**Leider** sind wir zu spät"
  - Middle position: "Wir sind **leider** zu spät"
  - End position: "Wir kommen **morgen**"

### German-Specific Adverb Types
- Modal particles (doch, mal, eben, halt)
- Pronominal adverbs (dafür, darauf, womit)
- Directional adverbs (hinauf, herein, dorthin)
- These require special attention to natural usage

### Degree Adverbs
- German has rich system: sehr, ziemlich, recht, äußerst
- Show appropriate collocations
- Note register differences

## JSON Structure Reference

### For Automated Batch Processing:
Use JSONL format (one object per line) with simplified structure:

```json
{"lemma": "quickly", "meanings_de": ["auf schnelle Weise"], "definitions_de": ["definition1"], "examples_de": [["example1", "example2"]]}
```

### For Understanding Complete Entry Structure:
When reading source files, you'll see entries with all these fields:

```json
{
  "lemma": "quickly",
  "meanings": ["in fast manner"],
  "definitions": ["moving or happening with great speed"],
  "examples": [["She quickly finished", "He quickly ran away"]],
  "frequency_meaning": [1.0]
}
```

### German Writing Guidelines:

1. **Authentic German Adverb Expression**
   - Consider German word order rules
   - Use appropriate register
   - Handle position flexibility correctly
   - Think: "How would Germans express this?"

**Examples of Natural vs. Rigid German:**

❌ RIGID (Direct translation):
- Definition: "geschehend mit Geschwindigkeit"
- Example: "Er lief schnell auf der Straße"

✅ PROFESSIONAL YET NATURAL:
- Definition: "sich mit großer Geschwindigkeit bewegend oder in kurzer Zeit geschehend"
- Example: "Er rannte **schnell** die Treppe hinauf, um den Bus zu erreichen"

2. **Cultural Adaptation**
   - English: "She answered very politely"
   - German: "Sie antwortete **äußerst** höflich" (using German intensifier preferences)

3. **Natural Adverb Collocations**
   - Use adverb combinations Germans actually use
   - "very much" → "sehr gern" (not "sehr viel" in many contexts)
   - "quite often" → "ziemlich oft" or "recht häufig"

4. **Adverb-Specific Considerations**
   - Position rules in German sentences
   - Modal particle usage
   - Register-appropriate choices
   - Compound adverb formations

## Quality Checklist

Before marking a batch complete, ensure:
- [ ] meanings_de provides clear, concise adverb translations
- [ ] definitions_de meet minimum word count requirements
- [ ] definitions_de read like authentic German explanations
- [ ] examples_de use **bold** for the German adverb
- [ ] examples_de reflect German culture and natural expression
- [ ] Adverb positions follow German rules
- [ ] No awkward direct translations
- [ ] Natural German word order and sentence structure

## Common Pitfalls to Avoid

❌ Word-for-word translation of adverb phrases
❌ Ignoring German position rules
❌ English sentence structure with German words
❌ Forgetting to bold the adverb in examples
❌ Using English adverb patterns that don't exist in German
❌ Definitions that are too short
❌ Confusing adjective and adverb forms
❌ Ignoring modal particles and their usage

## Progress Tracking
Check progress_checklist_german.md to see the next batch to do, mark the box with "x" before doing the task. Only do one batch at a time

## Important Reminders

- Think in German, don't translate from English
- Quality over speed: Ensure authentic German expression
- Meet all word count requirements
- When in doubt, ask: "Would a German speaker really say this?"
- Always bold the German adverb in examples_de
- Consider German-specific adverb types and positions
- Use the automated batch processing workflow to create separate German files
- One batch at a time - complete all steps for one batch only