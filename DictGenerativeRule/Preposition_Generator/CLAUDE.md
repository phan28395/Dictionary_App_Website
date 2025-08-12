# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for adding German content to the English-German preposition dictionary.

## 🔴 CRITICAL RULES - MUST READ FIRST

### German Content Generation Philosophy
**DO NOT simply translate English content. Generate authentic German that feels natural to native speakers.**

### Key Principles:
1. **meanings_de**: Direct translation of meaning labels
2. **definitions_de**: Culturally-aware German definitions that explain concepts as Germans would
3. **examples_de**: Natural German sentences that Germans would actually say, NOT word-for-word translations

### Formatting Rule for examples_de:
- The German preposition(s) that correspond to the English lemma must be in **bold** format
- Example: "Das Buch liegt **auf** dem Tisch"

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

**EVERY definition_de MUST meet these minimums:**
- Spatial/physical meanings: MIN 8 words (target: 8-12)
- Temporal meanings: MIN 10 words (target: 10-15)
- Abstract/metaphorical meanings: MIN 12 words (target: 12-18)
- Idiomatic uses: MIN 10 words (target: 10-15)

❗ If your definition is too short, expand with:
- The spatial relationship or position
- What types of nouns it typically combines with
- How it contrasts with similar prepositions
- Common contexts of use

**EVERY example_de MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project enhances the existing English preposition dictionary with German translations and content. Each entry already has English content and now requires German meanings, definitions, and examples.

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
{"lemma": "on", "meanings_de": ["eine Oberfläche berührend", "über Zeit/Datum", "in Betrieb", "über ein Thema"], "definitions_de": ["positioniert auf einer Oberfläche, diese berührend und von ihr gestützt", "verwendet zur Angabe spezifischer Tage und Daten, wann etwas geschieht", "funktionierend oder in Betrieb; nicht ausgeschaltet oder angehalten", "betreffend oder über ein bestimmtes Thema oder Subjekt"], "examples_de": [["Das Buch liegt **auf** dem Schreibtisch", "Sie stellte die Teller vorsichtig **auf** den Tisch"], ["Das Treffen ist **am** Montag um zehn Uhr", "Mein Geburtstag ist **am** fünften Juli"], ["Bitte lass das Licht **an**, wenn du gehst", "Der Computer war den ganzen Tag **an**"], ["Ich las einen Artikel **über** den Klimawandel", "Sie hielt eine Präsentation **über** Markttrends"]]}
{"lemma": "at", "meanings_de": ["spezifischer Ort", "spezifische Zeit", "gerichtet auf", "Fähigkeitsniveau"], "definitions_de": ["bezeichnet einen spezifischen Punkt oder Ort im Raum", "bezeichnet einen spezifischen Zeitpunkt oder Moment", "gerichtet auf oder zielend in Richtung von etwas", "bezeichnet das Niveau der Fähigkeit oder Fertigkeit bei einer Aktivität"], "examples_de": [["Triff mich **am** Café", "Sie wartet **an** der Bushaltestelle"], ["Der Unterricht beginnt **um** neun Uhr", "Ich sehe dich morgen **zur** Mittagszeit"], ["Zeige nicht **auf** andere Leute", "Sie warf den Ball **auf** das Ziel"], ["Er ist gut **in** Mathematik", "Sie ist schlecht **im** Kochen"]]}
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
- Use standard German preposition terminology
- Keep the same brevity as English (3-5 words)
- Match the order of English meanings
- Consider that English and German prepositions often don't map 1:1
- ✅ CORRECT format:
  - "touching a surface" → "eine Oberfläche berührend"
  - "about time/dates" → "über Zeit/Datum"
  - "specific location" → "spezifischer Ort"

**definitions_de**
- Write clear, informative definitions with natural German flow
- Meet word count requirements:
  - Spatial/physical: 8-12 words minimum
  - Temporal: 10-15 words minimum
  - Abstract/metaphorical: 12-18 words minimum
  - Idiomatic: 10-15 words minimum
- Structure definitions logically:
  - The spatial/temporal/abstract relationship
  - What it connects or relates
  - Common usage contexts
- Use connecting words for smooth reading: "dabei", "zudem", "insbesondere"
- Note case requirements (Akkusativ/Dativ) when relevant

**examples_de**
- Create authentic German sentences, NOT translations
- Use contexts familiar to German speakers
- The German preposition must be **bold**
- Two examples per meaning showing different uses/contexts
- Show natural German preposition usage
- Reflect German daily life, institutions, and culture
- Consider German preposition peculiarities:
  - Case governance (auf + Akk/Dat, in + Akk/Dat)
  - Contracted forms (am, im, zum, zur)
  - Different preposition choices than English

## Special Considerations for German Prepositions

### Case Governance
- German prepositions require specific cases
- Two-way prepositions (Wechselpräpositionen) change meaning with case
- Examples should demonstrate correct case usage naturally

### Preposition Mapping Challenges
- English "at" → German "an, bei, um, zu" depending on context
- English "on" → German "auf, an, am" depending on context
- English "in" → German "in, im, binnen" depending on context
- Choose the most natural German preposition for each context

### Contracted Forms
- Show contracted forms where natural:
  - an dem → am
  - in dem → im
  - zu dem → zum
  - zu der → zur

### Idiomatic Differences
- German often uses different prepositions in fixed expressions
- "good at" → "gut in" (not "gut bei")
- "depend on" → "abhängen von" (not "abhängen auf")

## JSON Structure Reference

### For Automated Batch Processing:
Use JSONL format (one object per line) with simplified structure:

```json
{"lemma": "on", "meanings_de": ["eine Oberfläche berührend", "über Zeit/Datum"], "definitions_de": ["definition1", "definition2"], "examples_de": [["example1", "example2"], ["example3", "example4"]]}
```

### For Understanding Complete Entry Structure:
When reading source files, you'll see entries with all these fields:

```json
{
  "lemma": "on",
  "meanings": ["touching a surface", "about time/dates"],
  "definitions": ["positioned touching and supported by a surface", "used to indicate days and dates"],
  "examples": [["The book is on the desk", "Put it on the table"], ["Meeting on Monday", "Birthday on July 5th"]],
  "frequency_meaning": [0.5, 0.3]
}
```

### German Writing Guidelines:

1. **Authentic German Preposition Usage**
   - Use natural German preposition choices
   - Show correct case governance
   - Include contracted forms where appropriate
   - Think: "Which preposition would Germans use here?"

**Examples of Natural vs. Rigid German:**

❌ RIGID (Direct translation):
- Definition: "positioniert berührend eine Oberfläche"
- Example: "Das Buch ist auf dem Tisch" (grammatically correct but can be more natural)

✅ PROFESSIONAL YET NATURAL:
- Definition: "auf einer Oberfläche liegend oder befindlich, diese berührend"
- Example: "Die Unterlagen liegen **auf** meinem Schreibtisch"

2. **Cultural Adaptation**
   - English: "at school" → German: "**in** der Schule"
   - English: "on the weekend" → German: "**am** Wochenende"
   - English: "in the street" → German: "**auf** der Straße"

3. **Natural Preposition Collocations**
   - Use preposition+noun combinations Germans actually use
   - "at work" → "bei der Arbeit" or "auf der Arbeit"
   - "on vacation" → "im Urlaub" or "in den Ferien"

4. **Preposition-Specific Considerations**
   - Case requirements (always correct)
   - Regional variations where relevant
   - Formal vs. informal usage
   - Fixed expressions and idioms

## Quality Checklist

Before marking a batch complete, ensure:
- [ ] meanings_de provides clear, concise preposition translations
- [ ] definitions_de meet minimum word count requirements
- [ ] definitions_de read like authentic German explanations
- [ ] examples_de use **bold** for the German preposition
- [ ] examples_de reflect German culture and natural expression
- [ ] Correct case usage throughout
- [ ] Natural German preposition choices (not forced translations)
- [ ] No awkward direct translations
- [ ] Contracted forms used where natural

## Common Pitfalls to Avoid

❌ Direct translation of English preposition usage
❌ Ignoring German case requirements
❌ Forgetting contracted forms (am, im, zum)
❌ Using wrong preposition in fixed expressions
❌ Forgetting to bold the preposition in examples
❌ Definitions that are too short
❌ Forcing English preposition logic onto German
❌ Missing regional or contextual variations

## Progress Tracking
Check progress_checklist_german.md to see the next batch to do, mark the box with "x" before doing the task. Only do one batch at a time

## Important Reminders

- Think in German, don't translate from English
- Quality over speed: Ensure authentic German expression
- Meet all word count requirements
- German prepositions often differ from English equivalents
- Always bold the German preposition in examples_de
- Show correct case governance naturally
- Use the automated batch processing workflow to create separate German files
- One batch at a time - complete all steps for one batch only