# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for adding German content to the English-German verb dictionary.

## 🔴 CRITICAL RULES - MUST READ FIRST

### German Content Generation Philosophy
**DO NOT simply translate English content. Generate authentic German that feels natural to native speakers.**

### Key Principles:
1. **meanings_de**: Direct translation of meaning labels
2. **definitions_de**: Culturally-aware German definitions that explain concepts as Germans would
3. **examples_de**: Natural German sentences that Germans would actually say, NOT word-for-word translations

### Formatting Rule for examples_de:
- The German verb form(s) that correspond to the English lemma must be in **bold** format
- Example: "Sie **läuft** jeden Morgen im Park"

### Meaning Merging Process (MANDATORY)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the verb

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

**EVERY definition_de MUST meet these minimums:**
- Simple action verbs: MIN 10 words (target: 10-15)
- Complex/abstract verbs: MIN 15 words (target: 15-25)  
- Multi-faceted verbs: MIN 20 words (target: 20-25)

❗ If your definition is too short, expand with:
- What the action involves
- Who/what performs it
- What it affects/changes
- Common contexts

**EVERY example_de MUST meet this minimum:**
- Minimum 6 words

## Project Overview

This project enhances the existing English verb dictionary with German translations and content. Each entry already has English content and now requires German meanings, definitions, and examples.

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
{"lemma": "run", "meanings_de": ["schnell zu Fuß bewegen", "betreiben oder leiten", "kontinuierlich fließen"], "definitions_de": ["sich schneller als im Gehschritt fortbewegen, indem man abwechselnd mit den Füßen den Boden berührt", "eine Organisation, ein Geschäft oder ein System verantwortlich führen und dabei wichtige Entscheidungen treffen", "sich kontinuierlich in eine Richtung bewegen, besonders bei Flüssigkeiten oder fließenden Substanzen"], "examples_de": [["Sie **läuft** jeden Morgen fünf Kilometer durch den Park", "Die Kinder **rannten** lachend über den Spielplatz"], ["Mein Onkel **leitet** das Familienrestaurant seit zwanzig Jahren", "Wer wird das Unternehmen **führen**, wenn der Gründer in Rente geht"], ["Der Fluss **fließt** mitten durch unsere Stadt", "Tränen **liefen** ihr während der bewegenden Rede übers Gesicht"]]}
{"lemma": "break", "meanings_de": ["in Stücke zerteilen", "aufhören zu funktionieren", "Kontinuität unterbrechen"], "definitions_de": ["bewirken, dass etwas plötzlich oder gewaltsam in Teile oder Fragmente zerfällt", "nicht mehr ordnungsgemäß arbeiten oder die vorgesehene Funktion nicht mehr erfüllen können", "den kontinuierlichen Ablauf oder die Gleichmäßigkeit von etwas unterbrechen"], "examples_de": [["Pass auf, dass du das Glas beim Spülen nicht **zerbrichst**", "Der Ast **brach** unter dem Gewicht des schweren Schnees"], ["Mein Handy ist **kaputtgegangen**, als ich es auf Beton fallen ließ", "Der alte Drucker ist nach jahrelangem Gebrauch endlich **kaputtgegangen**"], ["Lass uns eine Mittagspause **machen** und das Meeting später fortsetzen", "**Unterbrich** deine Konzentration nicht während der Prüfungsvorbereitung"]]}
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
- Use standard German verb terminology
- Keep the same brevity as English (3-5 words)
- Match the order of English meanings
- Consider typical German verb expressions
- ✅ CORRECT format:
  - "move quickly on feet" → "schnell zu Fuß bewegen"
  - "operate or manage" → "betreiben oder leiten"

**definitions_de**
- Write clear, informative definitions with natural German flow
- Meet word count requirements:
  - Simple action verbs: 10-15 words minimum
  - Complex/abstract verbs: 15-25 words minimum
  - Multi-faceted verbs: 20-25 words minimum
- Structure definitions logically:
  - What the action is
  - How it's performed
  - What it affects or changes
  - When/where it typically occurs
- Use connecting words for smooth reading: "dabei", "zudem", "insbesondere"
- Include typical German verb patterns and constructions
- Explain reflexive verbs appropriately (sich + verb)

**examples_de**
- Create authentic German sentences, NOT translations
- Use contexts familiar to German speakers
- Include typical German verb conjugations and patterns
- The German verb form must be **bold** (including separable prefixes)
- Two examples per meaning showing different uses/contexts
- Show various tenses and forms naturally
- Reflect German daily life, institutions, and culture
- Consider German verb peculiarities:
  - Separable verbs: "Er **kommt** morgen **an**"
  - Reflexive verbs: "Sie **freut sich** auf den Urlaub"
  - Modal verb constructions when appropriate

## JSON Structure Reference

### For Automated Batch Processing:
Use JSONL format (one object per line) with simplified structure:

```json
{"lemma": "run", "meanings_de": ["schnell zu Fuß bewegen", "betreiben oder leiten"], "definitions_de": ["definition1", "definition2"], "examples_de": [["example1", "example2"], ["example3", "example4"]]}
```

### For Understanding Complete Entry Structure:
When reading source files, you'll see entries with all these fields:

```json
{
  "lemma": "run",
  "meanings": ["move quickly on feet", "operate or manage"],
  "definitions": ["move at a speed faster than walking", "be in charge of something"],
  "examples": [["She runs every morning", "They ran to catch the bus"], ["He runs a restaurant", "Who runs this company"]],
  "frequency_meaning": [0.6, 0.4],
  "pos": "",
  "pos_frequency": ""
}
```

### German Writing Guidelines:

1. **Authentic German Verb Expression**
   - Consider German verb patterns and constructions
   - Use appropriate reflexive forms where Germans would
   - Handle separable verbs correctly
   - Think: "How would Germans express this action?"

**Examples of Natural vs. Rigid German:**

❌ RIGID (Direct translation):
- Definition: "sich mit Geschwindigkeit fortbewegen durch Beinbewegung"
- Example: "Der Mann läuft auf der Straße"

✅ PROFESSIONAL YET NATURAL:
- Definition: "sich schneller als im Gehschritt fortbewegen, indem man abwechselnd mit den Füßen den Boden berührt"
- Example: "Er **läuft** jeden Morgen eine Stunde durch den Stadtpark"

2. **Cultural Adaptation**
   - English: "She runs the meeting efficiently"
   - German: "Sie **leitet** die Besprechung effizient" (using appropriate German business terminology)

3. **Natural Verb Collocations**
   - Use verb+noun combinations Germans actually use
   - "make a decision" → "eine Entscheidung treffen"
   - "take a break" → "eine Pause machen"
   - "run a business" → "ein Geschäft führen/leiten"

4. **Verb-Specific Considerations**
   - Separable verbs: Show both parts correctly
   - Reflexive verbs: Include "sich" appropriately
   - Modal constructions: Use when natural
   - Tense variety: Show different forms in examples

## Quality Checklist

Before marking a batch complete, ensure:
- [ ] meanings_de provides clear, concise verb translations
- [ ] definitions_de meet minimum word count requirements
- [ ] definitions_de read like authentic German explanations
- [ ] examples_de use **bold** for the German verb form(s)
- [ ] examples_de reflect German culture and natural expression
- [ ] Verb forms are grammatically correct
- [ ] Separable verbs handled properly
- [ ] No awkward direct translations
- [ ] Natural German word order and sentence structure

## Common Pitfalls to Avoid

❌ Word-for-word translation of verb phrases
❌ Ignoring German verb patterns (separable, reflexive)
❌ English sentence structure with German words
❌ Forgetting to bold the verb in examples
❌ Using English verb collocations that don't exist in German
❌ Definitions that are too short
❌ Missing reflexive pronouns where needed
❌ Incorrect handling of separable verb prefixes

## Progress Tracking
Check progress_checklist_german.md to see the next batch to do, mark the box with "x" before doing the task. Only do one batch at a time

## Important Reminders

- Think in German, don't translate from English
- Quality over speed: Ensure authentic German expression
- Meet all word count requirements
- When in doubt, ask: "Would a German speaker really say this?"
- Always bold the German verb form in examples_de
- Handle German verb complexities (separable, reflexive) correctly
- Use the automated batch processing workflow to create separate German files
- One batch at a time - complete all steps for one batch only