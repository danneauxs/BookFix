# Bookfix User Manual

# Purpose
This program exists to prepare text for TTS convresion.  English is a difficult language and TTS doesn't always turn text into speech as you might expect it to.
With some words phoenetic type spelling is required, numbers can be read incorrectly, the date 1982 can be pronouces a quantity not a date etc.  The  program
aims to fix as man of these issues as possible so the listener can stay immersed in the audio instead of noticing mistakes.

## 1. Main Application Window

The main window is the central hub for loading your ebook, selecting processing steps, and starting the text cleaning process.

 <!-- Placeholder for an image of the main GUI -->

### 1.1 File Selection & Main Buttons

*   **Browse...**: Opens a file dialog to select a text file (`.txt`) you want to process. Once a file is loaded, its name will appear to the left of this button.
*   **Start Processing**: Begins the text cleaning process using the currently selected checkboxes. This button is disabled until a file is loaded.
*   **Manage Heteronyms**: Opens a separate window to manually edit the dictionary of words with multiple pronunciations (heteronyms), suchas `close` (cloze/close).
*   **Save Output**: After processing is complete, this button becomes active. It allows you to save the cleaned-up text to a new file.
*   **Quit**: Closes the Bookfix application.

### 1.2 Processing Options (Checkboxes)

These checkboxes allow you to enable or disable specific cleaning steps. The steps are run in a fixed, logical order. You can right-click any checkbox to select only that single step.

#### Automatic Steps
These steps run automatically without user input.

*   **Automatic text replacements**: Performs a series of find-and-replace operations based on rules defined in your `.data.txt` file. This is useful for fixing common, repetitive errors.
      Heteronyms are words that are spelled the same but pronouced differently. Breath is one.  A deep Breath and I can't breath.  You can use deep breath -> deep breth so that every time the text has this phrase it is replaced with deep breth.  Mr. -> mister so TTS does not say Mr period or M R.  same with  Dr. or LT. etc.  98th -> ninety eighth instead of ninety-eight T H.  The * -> * format matches anything on the left and turns it to whatever you put on the right.
*   **Period processing**: Changes C.I.A. to CIA
*   **Roman numeral conversion**: Intelligently converts Roman numerals (e.g., "Chapter IV") to numbers ("Chapter 4") or words ("Chapter Four") based on context
*   **Blank line removal**: Reduces multiple consecutive blank lines down to a single blank line to improve text flow.  I don't suggest you use this if you plan on using DNXS Spokenword my Chatterbox TTS program.
*   **Convert to lowercase**: Converts the entire text to lowercase. This is generally not recommended unless needed for a specific purpose.
*   **Page number removal**: Detects and removes page numbers that may be scattered throughout the text. This only works when a number is on a line by itself with no other text.  It WILL remove chapters if they are alone so I suggest either don't use it unless your text has page number or you add Chapter before each chapter number.

#### Interactive Steps
These steps will pause the processing and require your input, either through a pop-up review window or a dedicated interactive panel.

*   **Interactive word choices (homograph disambiguation)**: This is the most powerful step. It finds words with multiple pronunciations (like `read`, `live`, `close`) and uses an AI and rule-based system to suggest the correct phonetic replacement for text-to-speech. The results are presented in the AI Review Window.
    *   **AI Mode**:
        *   `Hybrid (rules + AI)`: (Default) Uses local rules first. Only words that cannot be decided by rules are sent to the AI for analysis. This is the most efficient mode.
        *   `Verify ALL (AI checks all)`: Sends every single word to the AI, even if a local rule could decide it. Slower, but useful for debugging or verifying rules.
        *   `Rules ONLY (no AI)`: Disables the AI completely and only uses your local rules (keywords, etc.).
    *   **Show AI Reasoning (Debug)**: If checked, the AI's reasoning for its choice will be displayed in the review window. This is useful for debugging but makes the AI's response slightly slower.
    *   **Context**: Determines how much surrounding text (in characters) is sent to the AI for analysis. A larger context can lead to more accurate results but may be slightly slower. `250` is recommended.

*   **All-caps text processing**: Finds sequences of all-capitalized text and presents them in a review window for you to decide whether to convert them to lowercase (e.g., for shouting) or keep them as-is (e.g., for acronyms like "NASA"). Stings of words in all caps are automatically lowercase (THIS IS REALLY NEAT) as such thing cause TTS to freak out.

*   **Numbered line processing**: Finds numbers in the text and uses AI and rules to classify and format them correctly (e.g., as a `year`, `quantity`, or `military_time`). The results are presented in the AI Review Window.  So the date 1987 is rendered as nineteen eighty-seven, and 0800 is zero eight hundred etc. 

---

## 2. The AI Review Window

After you click "Start Processing", if any of the interactive steps are enabled, this window will appear. It allows you to review, accept, reject, or edit every change suggested by the system.

 <!-- Placeholder for an image of the review window -->

### 2.1 Main Layout

*   **Text with Changes Highlighted (Left Panel)**: Shows a snippet of the text with the current suggested change highlighted in yellow.
*   **Changes List (Top Right)**: A list of all changes to be reviewed. You can click on any item to jump directly to it.
    *   **Filter by source**: A dropdown that lets you filter the list to show all changes, only those made by the AI, or only those made by local rules.
*   **Current Change Panel (Middle Right)**: Displays detailed information about the currently selected change, including the original text, the suggested replacement, and the AI's confidence.
*   **Action Buttons (Bottom Right)**: A grid of buttons to act on the current change.

### 2.2 Action Buttons

#### Common Buttons
*   **✓ ACCEPT AI SUGGESTION**: Accepts the current suggestion.
*   **Accept**: Same as above.
*   **All**: Accepts the current suggestion for *all identical instances* of this word in the text.
*   **Edit**: Allows you to manually type a different replacement.
*   **Reject**: Rejects the suggestion and keeps the original text. This is done by clicking the "Edit" button and then saving the original text. (A dedicated "Reject" button may be added in the future).

#### Module-Specific Buttons & Controls

These controls only appear when you are reviewing a change from a specific module.

**For "Numbered" Changes:**

*   **Type (Dropdown Menu)**: This is the most important control for numbers. It shows the number's current classification (e.g., `quantity`). **When you change the type in this dropdown, the "Suggestion" text box will automatically update to the correct format.** For example, changing a `quantity` to a `date` will change "one thousand, nine hundred and ninety-seven" to "nineteen ninety-seven" instantly.
*   **Suggestion (Text Box)**: An editable text box showing the current suggested replacement. You can type in this box to make manual corrections.
*   **Type (Button)**: This button opens a separate dialog to create a "boosted" learning rule. Use this to teach the system that a number in a specific context (which you define with keywords) should always be a certain type. This is the most powerful way to teach the number processor.

**For "Choices" (Homograph) Changes:**

*   **Flip**: If a word has more than one alternative pronunciation, this button cycles to the next available option.
*   **Flip All**: Flips all identical instances of this word to the next available option.
*   **Keyword**: Opens the Keyword Management dialog. This lets you view or add keywords associated with a specific pronunciation of a word. For example, you could teach the system that when the word "door" appears near "close", it should always choose the `cloze` (verb) pronunciation.
*   **Add Skip**: Allows you to add a phrase to the `SKIP_CHOICE` list in your `.data.txt` file. For example, if you add "close to", the processor will ignore the word "close" whenever it is followed by "to".

**For "AllCaps" Changes:**

*   **Ignore**: Adds the current all-caps word to your `CAP_IGNORE` list in `.data.txt`, ensuring it will always be kept in uppercase in future runs.