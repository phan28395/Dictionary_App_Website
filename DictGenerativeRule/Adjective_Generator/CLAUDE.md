# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) for adding German content to the English-German adjective dictionary.

## 🔴 CRITICAL RULES - MUST READ FIRST

### German Content Generation Philosophy
**DO NOT simply translate English content. Generate authentic German that feels natural to native speakers.**

### Key Principles:
1. **meanings_de**: Direct translation of meaning labels
2. **definitions_de**: Culturally-aware German definitions that explain concepts as Germans would
3. **examples_de**: Natural German sentences that Germans would actually say, NOT word-for-word translations

### Formatting Rules for examples_de:
- The German adjective(s) that correspond to the English lemma must be in **bold** format
- Include appropriate gender agreement forms
- Example: "Das ist ein **schöner** Tag" (masculine), "Eine **schöne** Blume" (feminine)

### Adjective-Specific German Rules:
1. **Gender Agreement**: German adjectives change form based on:
   - Gender (masculine, feminine, neuter)
   - Case (nominative, accusative, dative, genitive)
   - Number (singular, plural)
   - Article type (definite, indefinite, no article)

2. **Usage Contexts**: Consider both:
   - Attributive use (before nouns): "ein **großer** Mann"
   - Predicative use (after verbs): "Der Mann ist **groß**"

3. **Comparative Forms**: When relevant, examples can show:
   - Positive: groß
   - Comparative: größer
   - Superlative: am größten / der größte

## Project Overview

This project enhances the existing English adjective dictionary with German translations and content. Each entry already has English content and now requires German meanings, definitions, and examples.

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
    "lemma": "bright",
    "meanings_de": ["stark leuchtend", "intelligent und schnell", "leuchtend in Farbe"],
    "definitions_de": ["Licht in hoher Intensität ausstrahlend oder reflektierend, sodass die Umgebung erhellt wird", "Intelligenz und geistige Aufmerksamkeit zeigend mit schnellem Verständnis für Sachverhalte und Zusammenhänge", "kräftige, intensive oder leuchtende Farben besitzend, die sofort ins Auge fallen"],
    "examples_de": [["Die **helle** Sonne blendete uns beim Autofahren", "Wir brauchen **helle** Lampen für das Fotostudio"], ["Sie ist eine **kluge** Schülerin, die neue Konzepte schnell versteht", "Seine **brillanten** Ideen halfen, die Probleme des Unternehmens zu lösen"], ["Der Künstler verwendete **leuchtende** Gelb- und Orangetöne im Gemälde", "Kinder bevorzugen oft **knallige** Farben gegenüber gedeckten Tönen"]]
  },
  {
    "lemma": "hard",
    "meanings_de": ["fest und hart", "schwierig zu tun", "streng oder hart"],
    "definitions_de": ["fest, solide und widerstandsfähig gegen Druck oder Krafteinwirkung", "große Anstrengung, Können oder Ausdauer erfordernd, um etwas zu bewältigen oder zu verstehen", "kein Mitgefühl oder keine Zuneigung zeigend; streng in Art und Wirkung"],
    "examples_de": [["Der Boden war nach wochenlanger Trockenheit **hart**", "Diese Matratze ist zu **hart** für bequemen Schlaf"], ["Eine neue Sprache zu lernen ist **schwer**, aber lohnend", "Die Prüfung war so **schwierig**, dass viele Studenten durchfielen"], ["Sie warf ihm einen **harten** Blick der Missbilligung zu", "Es war ein **harter** Winter mit Rekordschneefällen"]]
  }
]
```

## German Dictionary Content Generation Rules

### Meaning Merging Process (FROM ENGLISH RULES - APPLY TO GERMAN)
**BEFORE creating multiple meanings, ALWAYS check for overlap:**

#### Step 1: Identify All Possible Senses
List every potential meaning/usage of the adjective

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

### Word Count Requirements (ADAPTED FOR GERMAN)

**EVERY definition_de MUST meet these minimums:**
- Simple descriptive adjectives: MIN 10 words (target: 10-18) - German needs more words for clarity
- Complex/abstract adjectives: MIN 18 words (target: 18-28)  
- Technical/specialized adjectives: MIN 18 words (target: 23-30)

❗ If your definition is too short, expand with:
- What quality it describes (welche Eigenschaft)
- What it typically modifies (was es typischerweise beschreibt)
- How it differs from similar adjectives (Abgrenzung zu ähnlichen Adjektiven)
- Common contexts (typische Verwendungskontexte)

**EVERY example_de MUST meet this minimum:**
- Minimum 7 words (German sentences tend to be longer)

### Persona Generator
<persona>
 <role>
   You are a skilled German lexicographer specializing in adjectives who writes with clarity and subtle warmth. You craft dictionary entries that are professional and precise, yet naturally readable. You understand that good German prose doesn't need to be stiff - it achieves elegance through clear structure and thoughtful word choice. Your definitions inform without overwhelming, using German's natural flow to make complex ideas accessible. You pay special attention to the nuances of adjective usage in German, including declension patterns and contextual variations.
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
   - You understand adjective declension and show different forms naturally in examples
   - You know when to use attributive vs. predicative forms for clarity
 </context>
</persona>

### Fields to Generate

**meanings_de**
- Direct, concise translation of the English meaning label
- Use standard German terminology for adjective qualities
- Keep the same brevity as English (3-5 words)
- Match the order of English meanings
- ✅ CORRECT format:
  - "emitting strong light" → "stark leuchtend"
  - "difficult to do" → "schwierig zu tun"
  - "solid and firm" → "fest und hart"

**definitions_de**
- Write clear, informative definitions with natural German flow
- Balance completeness with conciseness
- Use connecting words for smooth reading: "dabei", "zudem", "insbesondere"
- Structure definitions logically:
  - What quality/characteristic it describes
  - In what way or to what degree
  - Typical contexts or comparisons
  - Distinguishing features from similar adjectives
- Prefer clear, active language over passive constructions
- Use technical terms only when necessary, with brief clarification
- Aim for the clarity of a good encyclopedia, not the dryness of a technical manual
- Consider mentioning if the adjective has special usage patterns (only attributive, only predicative, etc.)

**examples_de**
- Create authentic German sentences, NOT translations
- Use contexts familiar to German speakers
- Include typical German collocations and phrases
- The German adjective must be **bold** - show appropriate declension
- Two examples per meaning showing different uses
- Reflect German daily life, institutions, and culture
- Use natural German word order and expressions
- Show variety in adjective forms when relevant:
  - Different genders: "ein **großer** Mann", "eine **große** Frau"
  - Attributive vs predicative: "Das **schnelle** Auto" vs "Das Auto ist **schnell**"
  - Different cases when natural: "mit **großem** Erfolg" (dative)

## JSON Structure Reference

### For Automated Batch Processing:
Use the simplified structure shown in "Example Output Structure" above (only lemma + German fields).

### For Understanding Complete Entry Structure:
When reading source files, you'll see entries with all these fields (German fields will be empty):

```json
{
  "lemma": "bright",
  "meanings": ["emitting strong light", "intelligent and quick", "vivid in color"],
  "meanings_de": [],
  "definitions": ["giving out or reflecting much light that illuminates surroundings", "showing intelligence and mental alertness with quick understanding of things", "having strong, intense, or vivid color that catches attention"],
  "definitions_de": [],
  "examples": [["The bright sun made it hard to see", "We need bright lights for the photography studio"], ["She's a bright student who learns concepts quickly", "His bright ideas helped solve the company's problems"], ["The artist used bright yellows and oranges in painting", "Children often prefer bright colors to dull ones"]],
  "examples_de": [],
  "frequency_meaning": [0.45, 0.35, 0.2],
  "pos": "",
  "pos_frequency": ""
}
```

### German Writing Guidelines for Adjectives:

1. **Authentic German Expression**
   - "The tall building" → NOT "Das hohe Gebäude" (literal) BUT consider context: "Das **hohe** Gebäude überragt die Altstadt" or "Der **imposante** Wolkenkratzer"
   - Think: "How would Germans naturally describe this quality?"

2. **Adjective Declension Examples**
   ❌ WRONG (ignoring declension):
   - "Der gut Mann" 
   - "Eine schön Frau"
   
   ✅ CORRECT (proper declension):
   - "Der **gute** Mann half uns beim Umzug"
   - "Eine **schöne** Frau betrat das Restaurant"
   - "Mit **großem** Interesse verfolgten wir die Debatte"

3. **Natural Collocations**
   - Use adjective+noun combinations Germans actually use
   - "heavy rain" → "**starker** Regen" (not "schwerer")
   - "fast food" → "**schnelles** Essen" or "Fast Food"
   - "hard work" → "**harte** Arbeit"

4. **Register Awareness**
   - Match formality to context
   - Formal: "Eine **ausgezeichnete** Leistung"
   - Informal: "Das war echt **super**!"
   - Academic: "Eine **signifikante** Verbesserung"

5. **Comparative Usage (when relevant)**
   - Show natural use of comparative forms
   - "Diese Lösung ist **besser** als die vorherige"
   - "Das **schnellste** Auto im Test"

## Quality Checklist

Before marking a batch complete, ensure:
- [ ] meanings_de provides clear, concise translations of adjective meanings
- [ ] definitions_de read like authentic German explanations with proper word count
- [ ] examples_de use **bold** for the German adjective with correct declension
- [ ] examples_de show variety in adjective forms (gender, case, attributive/predicative)
- [ ] examples_de reflect German culture and natural expression
- [ ] No awkward direct translations
- [ ] Appropriate register and formality
- [ ] Natural German word order and sentence structure
- [ ] Adjective declensions are grammatically correct

## Common Pitfalls to Avoid

❌ Word-for-word translation of adjective phrases
❌ Incorrect adjective declension
❌ English sentence structure with German words
❌ Ignoring adjective-noun collocations unique to German
❌ Using false friends incorrectly (e.g., "sensible" ≠ "sensibel")
❌ Forgetting to bold the adjective in examples
❌ Not showing adjective agreement with gender/case
❌ Using English comparative patterns (e.g., "more beautiful" instead of "schöner")
❌ Ignoring adjectives that work differently in German (e.g., predicative-only adjectives)

## Adjective-Specific Considerations

1. **Adjectives with Limited Usage**
   - Some adjectives are only predicative: "Das Kind ist **quitt**" (never "das quitte Kind")
   - Some are only attributive: "der **hiesige** Brauch" (never "der Brauch ist hiesig")
   - Mention these restrictions in definitions when relevant

2. **Adjectives from Participles**
   - Present participles: "das **lachende** Kind" (the laughing child)
   - Past participles: "die **geöffnete** Tür" (the opened door)
   - These follow normal adjective declension rules

3. **Color Adjectives**
   - Often invariable in certain contexts: "Die Bluse ist **rosa**"
   - But decline normally as attributive adjectives: "eine **rosafarbene** Bluse"

4. **Adjectives with Prepositions**
   - Many German adjectives require specific prepositions
   - "stolz auf" (proud of), "zufrieden mit" (satisfied with)
   - Include these in examples when relevant

## Progress Tracking
Check progress_checklist_german.md to see the next batch to process, mark the box with "x" before doing the task. Only process one batch at a time.

## Important Reminders

- Think in German, don't translate from English
- Quality over speed: Ensure authentic German expression
- Pay special attention to adjective declension and agreement
- When in doubt, ask: "Would a German speaker really say this?"
- Maintain consistency across entries
- Always bold the German adjective in examples_de
- Show variety in adjective forms to help learners
- Use the automated batch processing workflow to create separate German files
- One batch at a time - complete all steps for one batch only
- Respect the word count minimums for German definitions