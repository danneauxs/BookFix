# Context Keywords Guide

## What are Context Keywords?

Context keywords are **strong indicator words** that appear near a heteronym and help determine its meaning. They are more specific and reliable than semantic tags.

## How They Work

When the AI encounters a heteronym like "close", it searches the surrounding context (100 chars before/after) for any context keywords. If found, it uses that keyword to determine pronunciation.

### Example: "close"

**Verb form (KLOHZ - to shut):**
- Keywords: door, hatch, window, gate, lid, eyes, mouth, curtain, shutter
- Example: "Please **close** the **door**" → AI finds "door" → chooses KLOHZ

**Adjective form (KLOHS - near):**
- Keywords: friend, proximity, relationship, distance, nearby, together, intimate
- Example: "They are **close** **friends**" → AI finds "friend" → chooses KLOHS

## Confidence Scoring

Base confidence depends on keyword specificity:
- Short keywords (3-4 chars): 0.70
- Medium keywords (5-6 chars): 0.74-0.78
- Long keywords (7+ chars): 0.80-0.90

Proximity boost adds up to +0.05:
- Very close (<20 chars): +0.05
- Moderately close (<50 chars): +0.03
- Far away (>50 chars): +0.00

**Maximum confidence: 0.92**

## Dictionary Format

In `choices_pos_dictionary.json`:

```json
{
  "words": {
    "close": {
      "klohz": {
        "pos_tags": ["VB", "VBD", "VBN", "VBG"],
        "description": "verb: to shut, to bring together",
        "examples": [
          "close the door",
          "eyes closed",
          "closing the window"
        ],
        "context_keywords": [
          "door", "hatch", "window", "gate", "lid",
          "eyes", "mouth", "curtain", "shutter", "valve",
          "book", "laptop", "file", "tab"
        ],
        "semantic_tags": ["shut", "seal", "fasten"]
      },
      "klohs": {
        "pos_tags": ["JJ", "RB"],
        "description": "adjective: near in space or time",
        "examples": [
          "close friend",
          "close proximity",
          "stay close"
        ],
        "context_keywords": [
          "friend", "relationship", "proximity", "distance",
          "nearby", "together", "intimate", "relative",
          "connection", "bond", "tie"
        ],
        "semantic_tags": ["near", "intimate", "tight"]
      }
    }
  }
}
```

## More Examples

### "lead" (LEED vs LED)

**Verb (LEED - to guide):**
```json
"context_keywords": [
  "team", "group", "army", "charge", "way", "path",
  "direction", "guide", "commander", "captain", "investigation"
]
```
Example: "She will **lead** the **team**"

**Noun (LED - the metal):**
```json
"context_keywords": [
  "pipe", "metal", "poisoning", "paint", "bullet",
  "weight", "sinker", "shield", "radiation", "toxic"
]
```
Example: "The **pipe** was made of **lead**"

### "read" (REED vs RED)

**Present (REED):**
```json
"context_keywords": [
  "book", "newspaper", "article", "story", "novel",
  "magazine", "email", "text", "label", "sign"
]
```
Example: "I **read** the **book** every day"

**Past (RED):**
```json
"context_keywords": [
  "yesterday", "ago", "last", "already", "finished",
  "previously", "once", "before", "earlier"
]
```
Example: "I **read** it **yesterday**"

### "wound" (WOOND vs WOWND)

**Noun (WOOND - injury):**
```json
"context_keywords": [
  "injury", "blood", "cut", "bandage", "bleeding",
  "heal", "infection", "doctor", "hospital", "pain"
]
```
Example: "The **wound** was **bleeding**"

**Verb (WOWND - past of wind):**
```json
"context_keywords": [
  "rope", "string", "cord", "wire", "thread",
  "clock", "watch", "coil", "spiral", "twisted"
]
```
Example: "He **wound** the **rope** around the post"

## Best Practices

### 1. Choose Highly Specific Keywords

**Good:** "door", "hatch", "window" (specific objects)
**Bad:** "the", "and", "it" (too common)

### 2. Include Multiple Forms

For "close the door":
- "door" ✓
- "doors" ✓
- "doorway" ✓
- "hatch" ✓
- "gate" ✓

### 3. Think About Real Usage

Ask: "What words would actually appear near this meaning?"

For "close" (verb):
- Physical objects that can be closed: door, window, eyes, mouth
- Actions: shut, open (opposite), seal

For "close" (adjective):
- Relationships: friend, relative, family
- Distance concepts: proximity, nearby, together

### 4. Avoid Ambiguous Keywords

**Bad example:** "open" as keyword for "close" (verb)
- "open" appears with both meanings: "open and close the door"
- Too ambiguous!

**Better:** "door", "window", "lid" (unambiguous objects)

### 5. Test with Real Sentences

Before adding keywords, test them:

```
"Please close the door" → finds "door" → KLOHZ ✓
"We are close friends" → finds "friend" → KLOHS ✓
"Close the window please" → finds "window" → KLOHZ ✓
```

## Priority in Decision Hierarchy

Context keywords rank **4th** in the decision hierarchy:

1. **REPLACE rules** (0.98) - User-defined phrases
2. **POS + Syntax** (0.95-0.98) - Grammar analysis
3. **Entity context** (0.92) - Named entities
4. **Context keywords** (0.72-0.92) ← **YOU ARE HERE**
5. **Semantic tags** (0.6-0.85) - Nearby words
6. **AI/LLM** (variable) - Contextual analysis

This means keywords beat semantic tags and AI, but lose to grammar analysis.

## When to Use Context Keywords vs Semantic Tags

### Use Context Keywords When:
- The word is strongly associated with specific objects/concepts
- Example: "close" + "door" → definitely verb
- Confidence: 0.72-0.92

### Use Semantic Tags When:
- The relationship is weaker or more general
- Example: "refuse" near "heap" (could be other words too)
- Confidence: 0.6-0.85

### Rule of Thumb:
- **Context keywords** = "This word MUST be nearby for this meaning"
- **Semantic tags** = "This word MIGHT be nearby for this meaning"

## Maintenance

### Adding New Keywords

1. Identify the heteronym meaning
2. List 5-15 specific words that appear with that meaning
3. Add to `context_keywords` array in dictionary
4. Test with real examples
5. Adjust confidence if needed

### Removing Keywords

Remove keywords if:
- They appear with multiple meanings (too ambiguous)
- They're too common (appear everywhere)
- They cause false positives

## Technical Details

### Search Window

The system searches **100 characters** before and after the target word by default. This captures:
- ~20 words before
- ~20 words after
- Typically 1-3 sentences of context

### Confidence Calculation

```python
base_confidence = min(0.90, 0.70 + (len(keyword) * 0.02))

if distance < 20:
    proximity_boost = 0.05  # Very close
elif distance < 50:
    proximity_boost = 0.03  # Moderately close
else:
    proximity_boost = 0.0   # Far away

final_confidence = min(0.92, base_confidence + proximity_boost)
```

### Performance

Context keyword matching is **fast**:
- Simple string search (no parsing)
- Cached in memory
- O(n*m) where n=keywords, m=context length
- Typical: <1ms per word

## Examples in Action

### Example 1: "close the door"

```
Context: "walked over and tried to close the heavy wooden door but"
         |----------------100 chars----------------|

Keyword search finds: "door" at position 52
Target word position: 35 (middle of context)
Distance: 17 chars (very close!)

Confidence calculation:
- Base: 0.70 + (4 * 0.02) = 0.78
- Proximity: +0.05 (distance < 20)
- Final: 0.83

Decision: KLOHZ (verb) with 0.83 confidence
```

### Example 2: "close friend"

```
Context: "has been a very close friend of mine for many years now"
         |----------------100 chars-------------------|

Keyword search finds: "friend" at position 31
Target word position: 25
Distance: 6 chars (very close!)

Confidence calculation:
- Base: 0.70 + (6 * 0.02) = 0.82
- Proximity: +0.05 (distance < 20)
- Final: 0.87

Decision: KLOHS (adjective) with 0.87 confidence
```

## Summary

Context keywords provide **high-confidence disambiguation** when strong indicator words are present. They bridge the gap between grammar-based analysis (POS tagging) and general semantic matching, giving you precise control over difficult heteronyms.

**Key benefits:**
- Higher confidence than semantic tags (0.72-0.92 vs 0.6-0.85)
- More reliable than AI/LLM (consistent, explainable)
- Easy to maintain (just add/remove words from list)
- Fast performance (simple string search)

Use them for any heteronym where you can identify 5+ specific words that strongly indicate a particular meaning!
