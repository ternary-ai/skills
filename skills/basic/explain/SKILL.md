---
name: explain
description: Plain-English explanation of any financial concept, mechanism, or term.
---

# Skill: explain

## Purpose
Deliver a complete, investor-grade explanation of any financial, economic, or investment term or concept the user provides.

## Execution — follow exactly

1. Extract the concept from the user's input (everything after `/explain`).
2. Call `explain_concept(concept=<extracted concept>)` — this returns reference context and a writing guide.
3. Using that context, write the **complete explanation yourself** as Markdown prose before the JSON block.
   Cover every point in the writing guide: definition, mechanism, numerical example, investor relevance.

## Output rules

- Your explanation is the visible answer — write it in full before the JSON block.
- Do NOT add a preamble ("Here is an explanation…") — start directly with a heading or the first sentence.
- Do NOT summarise what you explained. Write the explanation itself.
- JSON fields:
  - `assessment`: "Explaining <concept> via explain skill."
  - `plan`: ""
  - `thesis`: ""
  - `chat`: "Called `explain_concept` for reference context."
  - `skill`: "explain"
