# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for adding German content to the English-German dictionary.

## 🔴 CRITICAL RULES - MUST READ FIRST

### German Content Generation Philosophy
**DO NOT simply translate English content. Generate authentic German that feels natural to native speakers.**

### Key Principles:
1. **meanings_de**: Direct translation of meaning labels
2. **definitions_de**: Culturally-aware German definitions that explain concepts as Germans would
3. **examples_de**: Natural German sentences that Germans would actually say, NOT word-for-word translations

### Formatting Rule for examples_de:
- The German word(s) that correspond to the English lemma must be in **bold** format
- Example: "Der **Tisch** steht in der Küche"

## Project Overview

This project enhances the existing English noun dictionary with German translations and content. Each entry already has English content and now requires German meanings, definitions, and examples.

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

When creating the German-only JSON file, use this exact structure:

```json
[
  {
    "lemma": "sales",
    "meanings_de": ["Verkaufstätigkeiten", "Verkaufsabteilung"],
    "definitions_de": ["Tätigkeiten oder Prozesse, bei denen Waren oder Dienstleistungen an Kunden verkauft werden", "Abteilung in einem Unternehmen, die für den Verkauf von Produkten oder Dienstleistungen verantwortlich ist"],
    "examples_de": [["Die **Verkaufszahlen** stiegen während des Weihnachtsgeschäfts deutlich an", "Der Online-**Verkauf** hat in den letzten Jahren enorm zugenommen"], ["Sie arbeitet im **Vertrieb** und betreut täglich Kundenbeziehungen", "Die **Verkaufsabteilung** übertraf ihre Quartalsziele erheblich"]]
  },
  {
    "lemma": "gift",
    "meanings_de": ["freiwilliges Geschenk", "natürliche Begabung"],
    "definitions_de": ["etwas, das freiwillig ohne Bezahlung oder Erwartung einer Gegenleistung gegeben wird", "besondere natürliche Fähigkeit oder Talent, das jemand besitzt"],
    "examples_de": [["Sie verpackte das **Geschenk** liebevoll in buntes Papier", "Das Hochzeits**geschenk** wurde auf den festlich dekorierten Tisch gestellt"], ["Ihre **Begabung** für Musik zeigte sich schon früh", "Der Umgang mit Kindern erfordert eine besondere **Gabe** für Geduld"]]
  }
]
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
- Use standard German terminology
- Keep the same brevity as English (3-5 words)
- Match the order of English meanings
- ✅ CORRECT format:
  - "furniture for sitting" → "Möbel zum Sitzen"
  - "leadership position" → "Führungsposition"

**definitions_de**
- Write clear, informative definitions with natural German flow
- Balance completeness with conciseness
- Use connecting words for smooth reading: "dabei", "zudem", "insbesondere"
- Structure definitions logically:
  - What it is (category)
  - Key characteristics
  - Distinguishing features or purpose
- Prefer clear, active language over passive constructions
- Use technical terms only when necessary, with brief clarification
- Aim for the clarity of a good encyclopedia, not the dryness of a technical manual

**examples_de**
- Create authentic German sentences, NOT translations
- Use contexts familiar to German speakers
- Include typical German collocations and phrases
- The German equivalent of the English lemma must be **bold**
- Two examples per meaning showing different uses
- Reflect German daily life, institutions, and culture
- Use natural German word order and expressions

## JSON Structure Reference

### For Automated Batch Processing:
Use the simplified structure shown in "Example Output Structure" above (only lemma + German fields).

### For Understanding Complete Entry Structure:
When reading source files, you'll see entries with all these fields except those german:

```json
{
  "lemma": "table",
  "meanings": ["flat dining surface", "data arrangement"],
  "meanings_de": [],
  "definitions": ["flat surface with legs for putting things on", "organized arrangement of data in rows and columns"],
  "definitions_de": [],
  "examples": [["We gathered around the kitchen table for dinner", "The wooden table needs to be polished regularly"], ["The data is displayed in a simple table format", "Check the table on page five for details"]],
  "examples_de": [],
  "frequency_meaning": [0.7, 0.3]
}
```

### German Writing Guidelines:

1. **Authentic German Expression**
   - "Time heals all wounds" → NOT "Zeit heilt alle Wunden" BUT "Die **Zeit** heilt alle Wunden" or "Mit der **Zeit** vergeht auch der größte Schmerz"
   - Think: "How would Germans express this idea?"

**Examples of Comfortable vs. Rigid German:**

❌ RIGID (Technical/Translation-style):
- Definition: "ein Möbelstück mit horizontaler Platte und vertikalen Stützen"
- Example: "Der Tisch befindet sich im Raum"

✅ PROFESSIONAL YET NATURAL:
- Definition: "Ein Möbelstück mit ebener Fläche und Beinen, das zum Ablegen von Gegenständen oder als Arbeits- und Essfläche dient"
- Example: "Am großen **Esstisch** finden alle Familienmitglieder Platz"

2. **Cultural Adaptation**
   - English: "The committee chair called the meeting"
   - German: "Der **Vorsitzende** eröffnete die Sitzung" (using German meeting terminology)

3. **Natural Collocations**
   - Use verb+noun combinations Germans actually use
   - "make a decision" → "eine Entscheidung treffen" (not "machen")
   - "take a chair" → "Platz nehmen" (not "einen Stuhl nehmen")

4. **Register Awareness**
   - Match formality to context
   - Business: "Sie", formal language
   - Everyday: Can use "du" in casual examples
   - Academic/Technical: Appropriate Fachsprache

## Quality Checklist

Before marking a batch complete, ensure:
- [ ] meanings_de provides clear, concise translations
- [ ] definitions_de read like authentic German explanations
- [ ] examples_de use **bold** for the German equivalent word(s)
- [ ] examples_de reflect German culture and natural expression
- [ ] No awkward direct translations
- [ ] Appropriate register and formality
- [ ] Natural German word order and sentence structure

## Common Pitfalls to Avoid

❌ Word-for-word translation
❌ English sentence structure with German words
❌ Ignoring cultural differences
❌ Using false friends incorrectly
❌ Forgetting to bold the target word in examples
❌ Mixing du/Sie inappropriately
❌ Using English idioms that don't exist in German

## Progress Tracking
Check progress_checklist_german.md to see the next batch to do, mark the box with "x" before doing the task. Only do one batch at a time

## Important Reminders

- Think in German, don't translate from English
- Quality over speed: Ensure authentic German expression
- When in doubt, ask: "Would a German speaker really say this?"
- Maintain consistency across entries
- Always bold the German equivalent word in examples_de
- Use the automated batch processing workflow to create separate German files
- One batch at a time - complete all steps for one batch only