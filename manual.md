# Bookfix User Manual

# Purpose
This program exists to prepare text for TTS conversion. English is a difficult language and TTS doesn't always turn text into speech as you might expect it to.
With some words phonetic-style spelling is required, numbers can be read incorrectly, and dates like 1982 can be pronounced as quantities instead of dates. The
program aims to fix as many of these issues as possible so the listener can stay immersed in the audio instead of noticing mistakes.

## 1. Main BookFix Window

The main window is the central hub for loading your ebook, selecting processing steps, and starting the text-cleaning process.

### 1.1 File Selection

**Section: “File Selection”**

- **File label**  
  Shows the name of the currently loaded file. Hovering usually shows the full path.
- **Browse…**  
  Opens a file dialog so you can choose the input file to process. Supported extensions include `.txt`, `.html`, `.xhtml`, and "All files". Once selected, the
  text is loaded and the file name appears in the label.

### 1.2 Processing Options (Checkboxes & Dropdowns)

The **Processing Options** section lets you enable or disable specific steps. All steps run in a fixed order; you cannot reorder them, only toggle them on/off.

You can **right‑click any checkbox** to select **only that step** (it turns that box on and all others off). Left‑click behaves like a normal checkbox.

#### 1.2.1 Processor checkboxes

Typical processor steps:

- **Replacements**  
  Applies user-defined find/replace rules (from `.data.txt` and related config). This is where you encode common TTS fixes, for example:
  - `deep breath -> deep breth` so a TTS engine pronounces "breath" correctly in that phrase.
  - `Mr. -> mister`, `Dr. -> doctor`, `Lt. -> lieutenant` so TTS doesn’t read the individual letters or say "M R".
  - `98th -> ninety eighth` so TTS doesn’t say "ninety-eight T H".
- **Periods**  
  Cleans up punctuation around periods and abbreviations, e.g. converting "C.I.A." → "CIA" and making spacing consistent.
- **Roman**  
  Converts Roman numerals into TTS‑friendly forms, using AI to correct mistakes (so "Chapter IV" → "Chapter four" while avoiding bogus conversions like "Mrs. C").
- **Blanklines**  
  Removes empty or whitespace‑only lines. This tightens the text but may not be ideal if another tool expects the original spacing.
- **Lowercase**  
  Uses a controlled list (UPPER_TO_LOWER) to convert specific all‑caps words into title case (e.g. SCUBA → Scuba, RADAR → Radar). Generally you don’t want to
  lowercase *everything*; this option focuses on known words.
- **Pagination**  
  Removes page numbers and pagination artifacts. For plain text, it removes lines that are only digits. Be careful: lines that contain just a chapter number may
  also be removed unless they include additional text like "Chapter 3".
- **Choices** (interactive / AI)  
  Handles words with multiple pronunciations/meanings (homographs) such as `lead`, `read`, `close`, `live`, etc. Uses rules + AI to choose the correct
  pronunciation/phonetic form for TTS. It runs as an interactive review step.
- **Allcaps** (interactive / AI)  
  Finds all‑caps sequences and decides whether they are **acronyms** (keep caps: NASA, FBI) or **emphasis/shouting** (convert to normal case). Long runs of
  ALL‑CAPS words are auto‑lowered because they often cause TTS to sound unnatural.
- **Numbered** (interactive / AI)  
  Detects numbers and classifies them (year, military time, quantity, currency, etc.), then formats them for natural speech. For example, 1987 → "nineteen
  eighty-seven", 0800 → "zero eight hundred".

The **choices**, **allcaps**, and **numbered** checkboxes are styled specially to indicate they are **interactive** steps.

#### 1.2.2 Choices AI sub‑options

Under the **Choices** processor, you will see extra controls that affect the homograph AI:

- **Show AI Reasoning (Debug)** [checkbox]  
  If enabled, the review window shows the AI’s reasoning/explanation for each decision. This is helpful for debugging or understanding decisions, but responses
  can be more verbose and slightly slower.

- **AI Mode:** [dropdown]
  - **Hybrid (rules + AI)** *(default)* – Rules handle obvious cases; AI is only asked when rules are uncertain. Good balance of speed and quality.
  - **Verify ALL (AI checks all)** – Every homograph occurrence is sent to the AI, even when rules are confident. Slowest but most thorough.
  - **Rules ONLY (no AI)** – Disables AI. All decisions rely purely on your rules and dictionaries.

- **Context:** [dropdown]  
  Controls how many characters of surrounding text the AI sees when deciding how to pronounce a word. Options are **50**, **100**, or **250** characters. Larger
  context usually gives better results; **250** is recommended.

Your preferences for these settings are saved in the configuration.

#### 1.2.3 Disabled phonetic option

At the bottom of the options, you may see:

- **Use Phonetic Analysis (DISABLED – unreliable)** [greyed‑out]

This is a legacy feature that’s intentionally disabled because it did not perform reliably. It is shown only for reference; you cannot enable it.

### 1.3 Text Content Area

The center‑left of the window is labeled **Text Content** and contains a read‑only text editor:

- After loading a file, it shows the original text.
- As automatic processors run, it updates to show the transformed text.
- After AI review steps (choices, allcaps, numbered), it shows the final approved version.

You do not edit text directly here; instead, all changes go through the processors and review windows.

### 1.4 Interactive Panel (Right Side)

The right‑hand **Interactive Processing** panel is used mainly for older/manual workflows, but it’s helpful to know what it contains:

- **Title:** usually "Interactive Processing" or "Interactive Word Choices".
- **Current item label:** a short description of the word/line currently under review.
- **Choice buttons area:** for legacy manual choices, a set of buttons representing options you can click.
- **Navigation buttons:**
  - **Previous** – go back to the previous item (disabled at the start).
  - **Skip** – skip the current item without changing it.
- **Roman numeral legend:** a small line explaining basic Roman numerals, used in some number workflows.

With the newer AI review windows, this panel is often hidden while AI‑based dialogs are in use.

### 1.5 Status & Progress

At the bottom, above the main buttons, you’ll see:

- **Status label** – messages like:
  - `Ready`
  - `Loaded file: my_book.txt`
  - `Running automatic processors…`
  - `Step 3/6: Roman numerals`
- **Progress bar** – appears while a background step (like replacements or roman) is running and shows percentage complete.

### 1.6 Action Buttons

At the very bottom are the main control buttons:

- **Start Processing**  
  Executes all **enabled** steps in the fixed order:
  1. Replacements  
  2. Periods  
  3. Roman  
  4. Blanklines  
  5. Lowercase  
  6. Pagination  
  7. Choices (AI review)  
  8. Allcaps (AI review)  
  9. Numbered (AI review)

  The button is disabled while processing is in progress.

- **Manage Heteronyms**  
  Opens the **Heteronym Dictionary Manager**, where you can edit the list of ambiguous words and their possible meanings/pronunciations.

- **Analyze Patterns**  
  Launches a separate analysis GUI that examines AI learning data and suggests new rules (e.g. REPLACE or SKIP patterns). This is an advanced feature for tuning
  the system over time.

- **Save Output**  
  Becomes enabled once all selected steps finish successfully. Lets you save the processed text to a new file of your choice.

- **Quit**  
  Closes the BookFix application.

---

## 2. AI Review Windows

Three modules rely on AI‑assisted **review windows** where you inspect and confirm proposed changes:

1. **Choices** – homographs / pronunciation decisions.
2. **Allcaps** – acronyms vs emphasis/shouting.
3. **Numbered** – number types and spoken formatting.

The general pattern is: **AI proposes → you review → BookFix applies only what you approve.**

### 2.1 Choices Review – Homographs

When the **Choices** step runs:

1. BookFix finds all occurrences of configured homograph words (lead, read, close, live, etc.).
2. For each occurrence, it uses a decision hierarchy:
   - High‑confidence phrase rules (REPLACE patterns).
   - POS tagging (noun vs. verb, phrasal verbs like "wound up").
   - Semantic clues from nearby words.
   - AI/LLM for ambiguous cases.
3. Every decision is stored in an internal **change tracker** with context and reasoning.
4. A **Choices review window** opens so you can confirm or adjust the decisions.

Depending on configuration, this review may appear as a generic AI review window or a specialized Choices Review Editor, but the ideas are the same.

#### 2.1.1 Layout (Choices Review)

Typical elements you’ll see:

- **Left panel: Text with highlight**  
  Shows a slice of the book’s text with the current word highlighted.

- **Right panel: Change list and details**
  - A list of all homograph decisions. Each entry looks like `lead → leed` or `lead → led` and may show confidence or rule/AI origin.
  - A detail area showing:
    - Original text.
    - Suggested replacement.
    - Optional reasoning (if "Show AI Reasoning" is enabled).

- **Navigation controls**
  - **Next / Previous** buttons.
  - Clicking a list item jumps directly to that change.
  - The window usually skips directly to the next unreviewed change.

#### 2.1.2 Actions (Choices Review)

Common actions include:

- **Accept / Accept AI Suggestion**  
  Approves the currently selected suggestion.

- **All / Accept All**  
  Approves the current suggestion for **all identical cases** in the document.

- **Edit**  
  Lets you type a custom replacement if you disagree with any option.

- **Undo / Reject**  
  Reverts a change back to the original text. (Depending on version, this may be a separate button or done via editing back to the original.)

Additional controls often visible for Choices:

- **Flip**  
  Cycles to the next available pronunciation/option for the current word.

- **Flip All**  
  Applies the flip to every identical instance of that word.

- **Keyword**  
  Opens a **Keyword Management** dialog, where you can add or adjust keywords that bias a word toward a particular pronunciation.

- **Add Skip**  
  Adds a phrase (e.g. "close to") to the `SKIP_CHOICE` list so that in that phrase, the word is ignored by the choices processor.

When you finish the review and confirm:

- The main text is updated with all approved changes.
- Learning data is updated so future runs can reuse your decisions.

If you cancel the review, BookFix asks whether to keep the AI changes or revert to the original text before continuing.

### 2.2 All‑Caps Review – Acronyms & Emphasis

The **Allcaps** step focuses on all‑uppercase words and sequences:

1. It learns document‑specific acronyms (e.g. "Federal Bureau of Investigation (FBI)").
2. It auto‑lowers obvious things like chapter headings and certain emphasis words.
3. It finds remaining isolated caps words and uses AI to decide:
   - Is this a **true acronym** (keep caps)?
   - Or just **emphasis/shouting** (lowercase or title‑case it)?
4. A **Caps Review Editor** window opens so you can review each unique caps word.

#### 2.2.1 Layout (Caps Review Editor)

- **Left list: Caps sequences**  
  A list of all caps words/phrases the system wants you to review.

- **Right panel: Context + options**  
  Shows the word in context and presents options for what to do with it.

#### 2.2.2 Actions (Caps Review)

Per‑word options typically include:

- **Keep (acronym)**  
  Leave the word in all caps and add it to the **CAP_IGNORE** list so future runs will also keep it.

- **Lowercase / Title‑case**  
  Convert the word to normal casing and update the **UPPER_TO_LOWER** list when appropriate.

- **This Document Only**  
  Apply the decision just for the current file, without changing global rules.

Bulk actions:

- **Accept All AI Suggestions**  
  Apply all keep/lower suggestions made by the AI.

- **Lowercase All**  
  Aggressively lower all remaining caps words.

When you click the final **Apply** or **Done** action:

- The main text is updated.
- CAP_IGNORE and UPPER_TO_LOWER lists are updated and saved back to configuration files.

### 2.3 Numbered Review – Number Types & Formatting

The **Numbered** step is responsible for how numbers are spoken by TTS:

1. BookFix scans the entire document for numbers (digits, commas, decimals, currency symbols, etc.).
2. For each number, it analyzes nearby context to classify it, for example:
   - **MILITARY TIME** – `0900`, `1600`.
   - **YEAR** – `1987`, `2024`.
   - **MEASUREMENT** – `10,000` with a unit.
   - **CURRENCY** – `$150`.
   - **GENERAL** – `42`.
3. It proposes spoken forms like:
   - `0900` → `zero nine hundred`.
   - `1600` → `sixteen hundred`.
   - `1987` → `nineteen eighty-seven`.
   - `$150` → `one hundred fifty dollars`.
4. All decisions are stored in a change tracker and presented in an AI review window for numbers.

#### 2.3.1 Layout (Numbers Review)

The numbers review uses the same AIChangesReviewWindow pattern as choices:

- **Left panel: Number changes list**  
  Each item summarizes a conversion, such as `42 → forty two (GENERAL)`.

- **Right panel: Context view**  
  Shows a slice of the original text with the number highlighted so you can see whether, for example, `1900` is a year or a quantity.

#### 2.3.2 Actions (Numbers Review)

Per‑change controls often include:

- **Type (Dropdown)**  
  Shows the current classification (`YEAR`, `CURRENCY`, `MEASUREMENT`, etc.). Changing this type automatically updates the suggested spoken form in the
  suggestion field. For example, switching from `quantity` to `date` changes the wording from "one thousand, nine hundred and ninety-seven" to "nineteen
  ninety-seven".

- **Suggestion (Text Box)**  
  A free‑text field where you can type your own spoken form if you don’t like the automatic one.

- **Boost / Type Rule button**  
  Opens a dialog to create a “boosted” learning rule associating a particular context (keywords around the number) with a specific type, so future occurrences
  are auto‑classified correctly.

Global actions mirror the choices review:

- **Accept All (Save & Learn)** – apply all suggestions and record them for future learning.
- **Accept All (Apply Only)** – apply them just in this document, without updating long‑term learning.

After confirming the review:

- All accepted conversions are written into the main text.
- When all enabled steps are done, **Save Output** becomes available so you can write the final, TTS‑ready text to disk.
