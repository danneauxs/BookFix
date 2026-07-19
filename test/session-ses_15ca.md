# Log file AI processing check: bookfix_ai_debug.log review

**Session ID:** ses_15cafd97effeJiZncrpIMoBnl1
**Created:** 6/7/2026, 2:19:59 PM
**Updated:** 6/7/2026, 6:27:52 PM

---

## User

file:///home/danno/MyApps/BookFix/bookfix_ai_debug.log   Look at this log. See if anything is sent to the AI for processing. If not, do you see a reason why it was not sent?

---

## Assistant (Plan · MiMo V2.5 Free · 3.7s)

_Thinking:_

The user wants me to examine a log file to see if anything is sent to the AI for processing, and if not, identify the reason why it wasn't sent.

Let me read the log file first.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix_ai_debug.log"
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix_ai_debug.log</path>
<type>file</type>
<content>
1: [2026-06-07 14:05:10] [INFO] File loaded: /home/danno/Calibre Library/David Beers/Warlord Born (The Great Insurrection Book 1) (224)/Warlord Born (The Great Insurrection Book - David Beers.txt
2: [2026-06-07 14:05:13] [INFO] Reloading POS dictionary...
3: [2026-06-07 14:05:13] [INFO] Starting AI-enhanced processing workflow with enabled_steps: {'replacements': False, 'choices': True, 'allcaps': False, 'numbered': False, 'periods': False, 'blanklines': False, 'lowercase': False, 'pagination': False}
4: [2026-06-07 14:05:13] [INFO] Pending interactive steps: ['interactive_choices']
5: [2026-06-07 14:05:13] [INFO] Starting interactive steps
6: [2026-06-07 14:05:13] [INFO] GUI: start_next_interactive_step called, pending steps: ['interactive_choices']
7: [2026-06-07 14:05:13] [INFO] GUI: Starting interactive step: interactive_choices
8: [2026-06-07 14:05:13] [INFO] GUI: Starting interactive choices
9: [2026-06-07 14:05:13] [INFO] GUI: Starting AI choices processing with new review workflow
10: [2026-06-07 14:05:13] [INFO] GUI: Loaded 23 homograph words from choices.json: ['recreation', 'bowed', 'jesus', 'lead', 'read', 'wound', 'live', 'object', 'close', 'record', 'records', 'present', 'sow', 'row', 'bass', 'resume', 'tear', 'refuse', 'polish', 'invalid', 'elaborate', 'estimate', 'wind']
11: [2026-06-07 14:05:13] [INFO] GUI: Populated ctx.choices with 23 words: ['recreation', 'bowed', 'jesus', 'lead', 'read', 'wound', 'live', 'object', 'close', 'record', 'records', 'present', 'sow', 'row', 'bass', 'resume', 'tear', 'refuse', 'polish', 'invalid', 'elaborate', 'estimate', 'wind']
12: [2026-06-07 14:05:13] [INFO] GUI: Loaded AI config from ai_config.json (provider=ollama)
13: [2026-06-07 14:05:13] [INFO] GUI: AI Mode set to HYBRID (AI only when rules unsure)
14: [2026-06-07 14:05:13] [INFO] GUI: Final AI config before init: ai_enabled=True, ai_verify_all=False
15: [2026-06-07 14:05:13] [INFO] GUI: Creating AIChoiceProcessor with context_size=250, show_reasoning=False
16: [2026-06-07 14:05:14] [INFO] GUI: Initializing AI with config: {'_available_models': ['mistral-small-latest', 'mistral-medium-latest', 'mistral-large-latest'], '_available_models_ollama': ['llama-3.3-70b-versatile', 'qwen/qwen3-32b', 'llama-3.1-8b-instant', 'llama-3.3-70b-versatile', 'openai/gpt-oss-20b'], '_provider_mistral': 'mistral', '_provider_ollama': 'ollama', '_provider_name': 'Change provider below to match your provider.', 'provider': 'ollama', '_model_mistral_small': 'mistral-small-latest', '_model_qwen_big': 'qwen-big:latest', '_model_mistral': 'mistral:latest', '_model_qwen_slim': 'qwen-slim:latest', '_model_qwen_coder_7b': 'qwen2.5-coder:7b-instruct', '_model': 'llama3.1:latest', '_model_name': 'This is where you change the model you want to use. Add it below', 'model': 'qwen-big:latest ', '_Store_Keys_below': 'You can store keys in The next entries and then just copy them into the actual API key when needed', '_api_key_mistral': '', '_api_key_groq': '', '_copy_key_into_next_line': 'paste your mistral api key below', 'api_key': '', 'rate_limit': 1.0, 'context_size': 250, 'show_ai_reasoning': False, 'max_retries': 3, 'confidence_threshold': 0.8, 'ai_enabled': True, 'ai_verify_all': False}
17: [2026-06-07 14:05:14] [DEBUG] Initializing ollama provider (model: qwen-big:latest )
18: [2026-06-07 14:05:14] [INFO] === AI Service Initialized (ollama) ===
19: [2026-06-07 14:05:14] [INFO] AI service initialized successfully: ollama provider configured (model: qwen-big:latest )
20: [2026-06-07 14:05:14] [INFO] GUI: initialize_ai returned: True
21: [2026-06-07 14:05:14] [INFO] Starting AI choices analysis for 23 words...
22: [2026-06-07 14:05:14] [DEBUG] DEBUG: Entering process_choices_ai_review_mode
23: [2026-06-07 14:05:16] [INFO] POS tagging services initialized (using spaCy)
24: [2026-06-07 14:05:16] [INFO] Reloading POS dictionary...
25: [2026-06-07 14:05:16] [INFO] POS dictionary reset and reloaded from file
26: [2026-06-07 14:05:16] [INFO] All logs cleared for new run: 2026-06-07 14:05:16
27: [2026-06-07 14:05:16] [DEBUG] DEBUG: Before len(ctx.choices) - type(ctx.choices): <class 'dict'>, ctx.choices is None: False
28: [2026-06-07 14:05:16] [INFO] Starting AI-first review mode with 23 choice rules (Batch Mode)
29: [2026-06-07 14:05:16] [DEBUG] DEBUG: Before set_text - type(ctx.text): <class 'str'>, len(ctx.text): 397543, change_tracker is None: False
30: [2026-06-07 14:05:16] [DEBUG] DEBUG: Total words to process: 23
31: [2026-06-07 14:05:16] [DEBUG] DEBUG: Processing word: 'bowed'
32: [2026-06-07 14:05:16] [DEBUG] DEBUG: Found 6 matches for 'bowed'
33: [2026-06-07 14:05:16] [DEBUG] DEBUG: Getting options for word: 'bowed'
34: [2026-06-07 14:05:16] [DEBUG] DEBUG: ─── 'bowed' occurrence 1/6 @ position 352564 ───
35: [2026-06-07 14:05:16] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 352564, end: 352569, context_size: 250, single_sentence: True
36: [2026-06-07 14:05:16] [DEBUG] DEBUG: Single sentence context: 'Their heads remained [bowed], neither of them glancing up to look their Ascendant in the eye.'
37: [2026-06-07 14:05:16] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
38: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules context_before: 'Their heads remained ', context_after: ', neither of them glancing up to look their Ascendant in the eye.'
39: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
40: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Their', 'heads', 'remained'], words_after: [',', 'neither', 'of', 'them', 'glancing', 'up', 'to', 'look', 'their', 'Ascendant', 'in', 'the', 'eye.']
41: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed , neither'
42: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'remained bowed ,'
43: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed ,'
44: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'remained bowed'
45: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['bowed , neither', 'remained bowed ,', 'bowed ,', 'remained bowed']
46: [2026-06-07 14:05:16] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
47: [2026-06-07 14:05:16] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
48: [2026-06-07 14:05:16] [DEBUG] DEBUG: Single sentence context: 'Their heads remained [bowed], neither of them glancing up to look their Ascendant in the eye.'
49: [2026-06-07 14:05:16] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
50: [2026-06-07 14:05:16] [DEBUG] DEBUG: _run_all_rules context_full: 'Their heads remained [bowed], neither of them glancing up to look their Ascendant in the eye.'
51: [2026-06-07 14:05:16] [DEBUG] DEBUG: _run_all_rules context_before: 'Their heads remained ', context_after: ', neither of them glancing up to look their Ascendant in the eye.'
52: [2026-06-07 14:05:16] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
53: [2026-06-07 14:05:16] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'JJ'
54: [2026-06-07 14:05:16] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
55: [2026-06-07 14:05:16] [DEBUG] connect_tcp.started host='huggingface.co' port=443 local_address=None timeout=10 socket_options=None
56: [2026-06-07 14:05:17] [DEBUG] connect_tcp.failed exception=ConnectError(gaierror(-2, 'Name or service not known'))
57: [2026-06-07 14:05:17] [DEBUG] connect_tcp.started host='huggingface.co' port=443 local_address=None timeout=None socket_options=None
58: [2026-06-07 14:05:17] [DEBUG] connect_tcp.failed exception=ConnectError(gaierror(-2, 'Name or service not known'))
59: [2026-06-07 14:05:17] [DEBUG] connect_tcp.started host='huggingface.co' port=443 local_address=None timeout=None socket_options=None
60: [2026-06-07 14:05:18] [DEBUG] connect_tcp.failed exception=ConnectError(gaierror(-2, 'Name or service not known'))
61: [2026-06-07 14:05:18] [INFO] RoBERTa-MNLI NLI model initialized for hybrid deciders
62: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.79))
63: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
64: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'boed'
65: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
66: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'boed'
67: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
68: [2026-06-07 14:05:18] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
69: [2026-06-07 14:05:20] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid', 'complex_pos', 'pos']
70: [2026-06-07 14:05:20] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 352564, match.end(): 352569, context_start_raw: 352314, match_start_in_full_text: 352564, match_end_in_full_text: 352569, context_end_raw: 352819
71: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Their heads remained [bowed], neither of them glancing up to look their Ascendant in the eye.'
72: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Their heads remained [bowed], neither of them glancing up to look their Ascendant in the eye.'
73: [2026-06-07 14:05:20] [DEBUG] DEBUG: ─── 'bowed' occurrence 2/6 @ position 353273 ───
74: [2026-06-07 14:05:20] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 353273, end: 353278, context_size: 250, single_sentence: True
75: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Ares remained silent, his head still [bowed].'
76: [2026-06-07 14:05:20] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
77: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules context_before: 'Ares remained silent, his head still ', context_after: '.'
78: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
79: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Ares', 'remained', 'silent,', 'his', 'head', 'still'], words_after: ['.']
80: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'still bowed .'
81: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed .'
82: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'still bowed'
83: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['still bowed .', 'bowed .', 'still bowed']
84: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
85: [2026-06-07 14:05:20] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
86: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Ares remained silent, his head still [bowed].'
87: [2026-06-07 14:05:20] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
88: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules context_full: 'Ares remained silent, his head still [bowed].'
89: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules context_before: 'Ares remained silent, his head still ', context_after: '.'
90: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
91: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'JJ'
92: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
93: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.65))
94: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
95: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'boed'
96: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
97: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'boed'
98: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
99: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
100: [2026-06-07 14:05:20] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid', 'complex_pos', 'pos']
101: [2026-06-07 14:05:20] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 353273, match.end(): 353278, context_start_raw: 353023, match_start_in_full_text: 353273, match_end_in_full_text: 353278, context_end_raw: 353528
102: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Ares remained silent, his head still [bowed].'
103: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Ares remained silent, his head still [bowed].'
104: [2026-06-07 14:05:20] [DEBUG] DEBUG: ─── 'bowed' occurrence 3/6 @ position 377331 ───
105: [2026-06-07 14:05:20] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 377331, end: 377336, context_size: 250, single_sentence: True
106: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Do you both understand?”
107:
108: The Primuses dropped to their knees and [bowed] their heads.'
109: [2026-06-07 14:05:20] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
110: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules context_before: 'Do you both understand?”
111:
112: The Primuses dropped to their knees and ', context_after: ' their heads.'
113: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
114: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Do', 'you', 'both', 'understand?”', 'The', 'Primuses', 'dropped', 'to', 'their', 'knees', 'and'], words_after: ['their', 'heads.']
115: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed their heads.'
116: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed their'
117: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed their'
118: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed'
119: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['bowed their heads.', 'and bowed their', 'bowed their', 'and bowed']
120: [2026-06-07 14:05:20] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
121: [2026-06-07 14:05:20] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
122: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Do you both understand?”
123:
124: The Primuses dropped to their knees and [bowed] their heads.'
125: [2026-06-07 14:05:20] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
126: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules context_full: 'Do you both understand?”
127:
128: The Primuses dropped to their knees and [bowed] their heads.'
129: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules context_before: 'Do you both understand?”
130:
131: The Primuses dropped to their knees and ', context_after: ' their heads.'
132: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
133: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'VBD'
134: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
135: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.89))
136: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
137: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
138: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
139: [2026-06-07 14:05:20] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
140: [2026-06-07 14:05:20] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid']
141: [2026-06-07 14:05:20] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 377331, match.end(): 377336, context_start_raw: 377081, match_start_in_full_text: 377331, match_end_in_full_text: 377336, context_end_raw: 377586
142: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Do you both understand?”
143:
144: The Primuses dropped to their knees and [bowed] their heads.'
145: [2026-06-07 14:05:20] [DEBUG] DEBUG: Single sentence context: 'Do you both understand?”
146:
147: The Primuses dropped to their knees and [bowed] their heads.'
148: [2026-06-07 14:05:20] [DEBUG] DEBUG: ─── 'bowed' occurrence 4/6 @ position 378765 ───
149: [2026-06-07 14:05:20] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 378765, end: 378770, context_size: 250, single_sentence: True
150: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and [bowed] her head.'
151: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
152: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules context_before: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and ', context_after: ' her head.'
153: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
154: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: words_before: ['“These', 'are', 'the', 'people', 'you', 'will', 'lead', 'back', 'to', 'Earth,', 'my', 'liege.”', 'Servia', 'knelt', 'at', 'Alistair’s', 'side', 'and'], words_after: ['her', 'head.']
155: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed her head.'
156: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed her'
157: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed her'
158: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed'
159: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['bowed her head.', 'and bowed her', 'bowed her', 'and bowed']
160: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
161: [2026-06-07 14:05:21] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
162: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and [bowed] her head.'
163: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
164: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_full: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and [bowed] her head.'
165: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_before: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and ', context_after: ' her head.'
166: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
167: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'VBD'
168: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
169: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.91))
170: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
171: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
172: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
173: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
174: [2026-06-07 14:05:21] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid']
175: [2026-06-07 14:05:21] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 378765, match.end(): 378770, context_start_raw: 378515, match_start_in_full_text: 378765, match_end_in_full_text: 378770, context_end_raw: 379020
176: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and [bowed] her head.'
177: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“These are the people you will lead back to Earth, my liege.” Servia knelt at Alistair’s side and [bowed] her head.'
178: [2026-06-07 14:05:21] [DEBUG] DEBUG: ─── 'bowed' occurrence 5/6 @ position 379088 ───
179: [2026-06-07 14:05:21] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 379088, end: 379093, context_size: 250, single_sentence: True
180: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“My liege, I present your people.”
181:
182: He took a knee on the other side and [bowed] his head.'
183: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
184: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules context_before: '“My liege, I present your people.”
185:
186: He took a knee on the other side and ', context_after: ' his head.'
187: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
188: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: words_before: ['“My', 'liege,', 'I', 'present', 'your', 'people.”', 'He', 'took', 'a', 'knee', 'on', 'the', 'other', 'side', 'and'], words_after: ['his', 'head.']
189: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed his head.'
190: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed his'
191: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed his'
192: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and bowed'
193: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['bowed his head.', 'and bowed his', 'bowed his', 'and bowed']
194: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
195: [2026-06-07 14:05:21] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
196: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“My liege, I present your people.”
197:
198: He took a knee on the other side and [bowed] his head.'
199: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
200: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_full: '“My liege, I present your people.”
201:
202: He took a knee on the other side and [bowed] his head.'
203: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_before: '“My liege, I present your people.”
204:
205: He took a knee on the other side and ', context_after: ' his head.'
206: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
207: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'VBD'
208: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
209: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.94))
210: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
211: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
212: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
213: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
214: [2026-06-07 14:05:21] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid']
215: [2026-06-07 14:05:21] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 379088, match.end(): 379093, context_start_raw: 378838, match_start_in_full_text: 379088, match_end_in_full_text: 379093, context_end_raw: 379343
216: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“My liege, I present your people.”
217:
218: He took a knee on the other side and [bowed] his head.'
219: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: '“My liege, I present your people.”
220:
221: He took a knee on the other side and [bowed] his head.'
222: [2026-06-07 14:05:21] [DEBUG] DEBUG: ─── 'bowed' occurrence 6/6 @ position 388748 ───
223: [2026-06-07 14:05:21] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 388748, end: 388753, context_size: 250, single_sentence: True
224: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: 'I [bowed] to Alistair Kane—Prometheus the Light Bringer.'
225: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'bowed'
226: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules context_before: 'I ', context_after: ' to Alistair Kane—Prometheus the Light Bringer.'
227: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking word 'bowed' with 378 rules
228: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: words_before: ['I'], words_after: ['to', 'Alistair', 'Kane—Prometheus', 'the', 'Light', 'Bringer.']
229: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed to Alistair'
230: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'I bowed to'
231: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'bowed to'
232: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'I bowed'
233: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['bowed to Alistair', 'I bowed to', 'bowed to', 'I bowed']
234: [2026-06-07 14:05:21] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
235: [2026-06-07 14:05:21] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
236: [2026-06-07 14:05:21] [DEBUG] DEBUG: Single sentence context: 'I [bowed] to Alistair Kane—Prometheus the Light Bringer.'
237: [2026-06-07 14:05:21] [DEBUG] DEBUG: Entering _run_all_rules for word: 'bowed'
238: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_full: 'I [bowed] to Alistair Kane—Prometheus the Light Bringer.'
239: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules context_before: 'I ', context_after: ' to Alistair Kane—Prometheus the Light Bringer.'
240: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'bowed'
241: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'bowed': 'NNP'
242: [2026-06-07 14:05:21] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'bowed'
243: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'bowed' → 'boughed' (nli=boughed(0.81))
244: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'bowed'
245: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'bowed'
246: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'bowed'
247: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'bowed'
248: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'bowed'. Found rules: ['hybrid']
249: [2026-06-07 14:05:22] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 388748, match.end(): 388753, context_start_raw: 388498, match_start_in_full_text: 388748, match_end_in_full_text: 388753, context_end_raw: 389003
250: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'I [bowed] to Alistair Kane—Prometheus the Light Bringer.'
251: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'I [bowed] to Alistair Kane—Prometheus the Light Bringer.'
252: [2026-06-07 14:05:22] [DEBUG] DEBUG: Processing word: 'close'
253: [2026-06-07 14:05:22] [DEBUG] DEBUG: Found 26 matches for 'close'
254: [2026-06-07 14:05:22] [DEBUG] DEBUG: Getting options for word: 'close'
255: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 1/26 @ position 7895 ───
256: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 7895 due to skip phrase match: 'close to'
257: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 2/26 @ position 34247 ───
258: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 34247 due to skip phrase match: 'close to'
259: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 3/26 @ position 36988 ───
260: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 36988 due to skip phrase match: 'close to'
261: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 4/26 @ position 46241 ───
262: [2026-06-07 14:05:22] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 46241, end: 46246, context_size: 250, single_sentence: True
263: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a [close]-range MechPulse while wearing the Clip.'
264: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'close'
265: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules context_before: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a ', context_after: '-range MechPulse while wearing the Clip.'
266: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking word 'close' with 378 rules
267: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Even', 'the', 'mutant', 'Alistair', 'had', 'once', 'seen,', "she'd", 'had', 'her', 'head', 'turned', 'into', 'powder', 'with', 'a'], words_after: ['-range', 'MechPulse', 'while', 'wearing', 'the', 'Clip.']
268: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close -range MechPulse'
269: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'a close -range'
270: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close -range'
271: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'a close'
272: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['close -range MechPulse', 'a close -range', 'close -range', 'a close']
273: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
274: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
275: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a [close]-range MechPulse while wearing the Clip.'
276: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _run_all_rules for word: 'close'
277: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_full: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a [close]-range MechPulse while wearing the Clip.'
278: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_before: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a ', context_after: '-range MechPulse while wearing the Clip.'
279: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'close'
280: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'close': 'JJ'
281: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'close'
282: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'close' → 'close' (pos-adj/adv)
283: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'close'
284: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'close'
285: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'close'
286: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'close'
287: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'close'
288: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'close'
289: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'close'. Found rules: ['hybrid', 'complex_pos', 'pos']
290: [2026-06-07 14:05:22] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 46241, match.end(): 46246, context_start_raw: 45991, match_start_in_full_text: 46241, match_end_in_full_text: 46246, context_end_raw: 46496
291: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a [close]-range MechPulse while wearing the Clip.'
292: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'Even the mutant Alistair had once seen, she'd had her head turned into powder with a [close]-range MechPulse while wearing the Clip.'
293: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 5/26 @ position 55789 ───
294: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 55789 due to skip phrase match: 'close the'
295: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 6/26 @ position 65680 ───
296: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 65680 due to skip phrase match: 'close enough'
297: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 7/26 @ position 94548 ───
298: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 94548 due to skip phrase match: 'as close'
299: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 8/26 @ position 104630 ───
300: [2026-06-07 14:05:22] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 104630, end: 104635, context_size: 250, single_sentence: True
301: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to [close] it.'
302: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'close'
303: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules context_before: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to ', context_after: ' it.'
304: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking word 'close' with 378 rules
305: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: words_before: ['The', 'chair', "wasn't", 'rocking', 'and', 'the', 'door', 'to', 'the', 'house', 'stood', 'open,', 'as', 'if', "she'd", 'just', 'forgotten', 'to'], words_after: ['it.']
306: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to close it.'
307: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close it.'
308: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to close'
309: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['to close it.', 'close it.', 'to close']
310: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
311: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
312: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to [close] it.'
313: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _run_all_rules for word: 'close'
314: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_full: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to [close] it.'
315: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_before: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to ', context_after: ' it.'
316: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'close'
317: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'close': 'VB'
318: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'close'
319: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'close' → 'cloze' (pos-verb)
320: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'close'
321: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'cloze'
322: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'close'
323: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'cloze'
324: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'close'
325: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'close'
326: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'close'. Found rules: ['hybrid', 'complex_pos', 'pos']
327: [2026-06-07 14:05:22] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 104630, match.end(): 104635, context_start_raw: 104380, match_start_in_full_text: 104630, match_end_in_full_text: 104635, context_end_raw: 104885
328: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to [close] it.'
329: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'The chair wasn't rocking and the door to the house stood open, as if she'd just forgotten to [close] it.'
330: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 9/26 @ position 107109 ───
331: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 107109 due to skip phrase match: 'close to'
332: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 10/26 @ position 153529 ───
333: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 153529 due to skip phrase match: 'close to'
334: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 11/26 @ position 158122 ───
335: [2026-06-07 14:05:22] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 158122, end: 158127, context_size: 250, single_sentence: True
336: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'If that is not good for you, then perhaps you should [close] my mouth so I don’t tell you any more names."'
337: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'close'
338: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules context_before: 'If that is not good for you, then perhaps you should ', context_after: ' my mouth so I don’t tell you any more names."'
339: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking word 'close' with 378 rules
340: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: words_before: ['If', 'that', 'is', 'not', 'good', 'for', 'you,', 'then', 'perhaps', 'you', 'should'], words_after: ['my', 'mouth', 'so', 'I', 'don’t', 'tell', 'you', 'any', 'more', 'names."']
341: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close my mouth'
342: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'should close my'
343: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close my'
344: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'should close'
345: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['close my mouth', 'should close my', 'close my', 'should close']
346: [2026-06-07 14:05:22] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
347: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
348: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'If that is not good for you, then perhaps you should [close] my mouth so I don’t tell you any more names."'
349: [2026-06-07 14:05:22] [DEBUG] DEBUG: Entering _run_all_rules for word: 'close'
350: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_full: 'If that is not good for you, then perhaps you should [close] my mouth so I don’t tell you any more names."'
351: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules context_before: 'If that is not good for you, then perhaps you should ', context_after: ' my mouth so I don’t tell you any more names."'
352: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'close'
353: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'close': 'VB'
354: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'close'
355: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'close' → 'cloze' (pos-verb)
356: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'close'
357: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'cloze'
358: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'close'
359: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'cloze'
360: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'close'
361: [2026-06-07 14:05:22] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'close'
362: [2026-06-07 14:05:22] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'close'. Found rules: ['hybrid', 'complex_pos', 'pos']
363: [2026-06-07 14:05:22] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 158122, match.end(): 158127, context_start_raw: 157872, match_start_in_full_text: 158122, match_end_in_full_text: 158127, context_end_raw: 158377
364: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'If that is not good for you, then perhaps you should [close] my mouth so I don’t tell you any more names."'
365: [2026-06-07 14:05:22] [DEBUG] DEBUG: Single sentence context: 'If that is not good for you, then perhaps you should [close] my mouth so I don’t tell you any more names."'
366: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 12/26 @ position 168463 ───
367: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 168463 due to skip phrase match: 'close to'
368: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 13/26 @ position 198384 ───
369: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 198384 due to skip phrase match: 'as close'
370: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 14/26 @ position 224015 ───
371: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 224015 due to skip phrase match: 'close to'
372: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 15/26 @ position 233925 ───
373: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 233925 due to skip phrase match: 'close to'
374: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 16/26 @ position 241320 ───
375: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 241320 due to skip phrase match: 'close enough'
376: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 17/26 @ position 243315 ───
377: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 243315 due to skip phrase match: 'close to'
378: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 18/26 @ position 261576 ───
379: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 261576 due to skip phrase match: 'how close'
380: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 19/26 @ position 268302 ───
381: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 268302 due to skip phrase match: 'how close'
382: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 20/26 @ position 271235 ───
383: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 271235 due to skip phrase match: 'close to'
384: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 21/26 @ position 278725 ───
385: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 278725 due to skip phrase match: 'close to'
386: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 22/26 @ position 300341 ───
387: [2026-06-07 14:05:22] [INFO] Skipping choice for 'close' at position 300341 due to skip phrase match: 'close to'
388: [2026-06-07 14:05:22] [DEBUG] DEBUG: ─── 'close' occurrence 23/26 @ position 300374 ───
389: [2026-06-07 14:05:22] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 300374, end: 300379, context_size: 250, single_sentence: True
390: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'They’d been so close to escaping, so impossibly [close].'
391: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'close'
392: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules context_before: 'They’d been so close to escaping, so impossibly ', context_after: '.'
393: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking word 'close' with 378 rules
394: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: words_before: ['They’d', 'been', 'so', 'close', 'to', 'escaping,', 'so', 'impossibly'], words_after: ['.']
395: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'impossibly close .'
396: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'close .'
397: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'impossibly close'
398: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['impossibly close .', 'close .', 'impossibly close']
399: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
400: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
401: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'They’d been so close to escaping, so impossibly [close].'
402: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _run_all_rules for word: 'close'
403: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_full: 'They’d been so close to escaping, so impossibly [close].'
404: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_before: 'They’d been so close to escaping, so impossibly ', context_after: '.'
405: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'close'
406: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'close': 'JJ'
407: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'close'
408: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'close' → 'close' (pos-adj/adv)
409: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'close'
410: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'close'
411: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'close'
412: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'close'
413: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'close'
414: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'close'
415: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'close'. Found rules: ['hybrid', 'complex_pos', 'pos']
416: [2026-06-07 14:05:23] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 300374, match.end(): 300379, context_start_raw: 300124, match_start_in_full_text: 300374, match_end_in_full_text: 300379, context_end_raw: 300629
417: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'They’d been so close to escaping, so impossibly [close].'
418: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'They’d been so close to escaping, so impossibly [close].'
419: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'close' occurrence 24/26 @ position 332528 ───
420: [2026-06-07 14:05:23] [INFO] Skipping choice for 'close' at position 332528 due to skip phrase match: 'how close'
421: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'close' occurrence 25/26 @ position 373608 ───
422: [2026-06-07 14:05:23] [INFO] Skipping choice for 'close' at position 373608 due to skip phrase match: 'close to'
423: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'close' occurrence 26/26 @ position 380859 ───
424: [2026-06-07 14:05:23] [INFO] Skipping choice for 'close' at position 380859 due to skip phrase match: 'close to'
425: [2026-06-07 14:05:23] [DEBUG] DEBUG: Processing word: 'recreation'
426: [2026-06-07 14:05:23] [DEBUG] DEBUG: Found 0 matches for 'recreation'
427: [2026-06-07 14:05:23] [DEBUG] DEBUG: Processing word: 'wound'
428: [2026-06-07 14:05:23] [DEBUG] DEBUG: Found 5 matches for 'wound'
429: [2026-06-07 14:05:23] [DEBUG] DEBUG: Getting options for word: 'wound'
430: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'wound' occurrence 1/5 @ position 70007 ───
431: [2026-06-07 14:05:23] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 70007, end: 70012, context_size: 250, single_sentence: True
432: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'The chair [wound] through the ship.'
433: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'wound'
434: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules context_before: 'The chair ', context_after: ' through the ship.'
435: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking word 'wound' with 378 rules
436: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: words_before: ['The', 'chair'], words_after: ['through', 'the', 'ship.']
437: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound through the'
438: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'chair wound through'
439: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound through'
440: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'chair wound'
441: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['wound through the', 'chair wound through', 'wound through', 'chair wound']
442: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
443: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
444: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'The chair [wound] through the ship.'
445: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _run_all_rules for word: 'wound'
446: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_full: 'The chair [wound] through the ship.'
447: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_before: 'The chair ', context_after: ' through the ship.'
448: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'wound'
449: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'wound': 'VBD'
450: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'wound'
451: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'wound' → 'wow'nd' (pos-verb-wind)
452: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'wound'
453: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'wound'
454: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'wow'nd'
455: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'wound'
456: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'wound'
457: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'wound'. Found rules: ['hybrid', 'pos']
458: [2026-06-07 14:05:23] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 70007, match.end(): 70012, context_start_raw: 69757, match_start_in_full_text: 70007, match_end_in_full_text: 70012, context_end_raw: 70262
459: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'The chair [wound] through the ship.'
460: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'The chair [wound] through the ship.'
461: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'wound' occurrence 2/5 @ position 127236 ───
462: [2026-06-07 14:05:23] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 127236, end: 127241, context_size: 250, single_sentence: True
463: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'A tube was attached to the mask and [wound] its way behind him so that he couldn't see what it was attached to.'
464: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'wound'

(Output capped at 50 KB. Showing lines 1-464. Use offset=465 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 3.7s)

_Thinking:_

Let me read more of the log file to see if there's any AI processing happening.

Let me read more of the log to see if AI is ever actually called:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix_ai_debug.log",
  "offset": 465
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix_ai_debug.log</path>
<type>file</type>
<content>
465: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules context_before: 'A tube was attached to the mask and ', context_after: ' its way behind him so that he couldn't see what it was attached to.'
466: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking word 'wound' with 378 rules
467: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: words_before: ['A', 'tube', 'was', 'attached', 'to', 'the', 'mask', 'and'], words_after: ['its', 'way', 'behind', 'him', 'so', 'that', 'he', "couldn't", 'see', 'what', 'it', 'was', 'attached', 'to.']
468: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound its way'
469: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and wound its'
470: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound its'
471: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and wound'
472: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['wound its way', 'and wound its', 'wound its', 'and wound']
473: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
474: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
475: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'A tube was attached to the mask and [wound] its way behind him so that he couldn't see what it was attached to.'
476: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _run_all_rules for word: 'wound'
477: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_full: 'A tube was attached to the mask and [wound] its way behind him so that he couldn't see what it was attached to.'
478: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_before: 'A tube was attached to the mask and ', context_after: ' its way behind him so that he couldn't see what it was attached to.'
479: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'wound'
480: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'wound': 'NNS'
481: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'wound'
482: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'wound' → 'wow'nd' (pos-verb-wind-its-way)
483: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'wound'
484: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'wound'
485: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'wound'
486: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'wound'
487: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'wound'. Found rules: ['hybrid']
488: [2026-06-07 14:05:23] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 127236, match.end(): 127241, context_start_raw: 126986, match_start_in_full_text: 127236, match_end_in_full_text: 127241, context_end_raw: 127491
489: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'A tube was attached to the mask and [wound] its way behind him so that he couldn't see what it was attached to.'
490: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'A tube was attached to the mask and [wound] its way behind him so that he couldn't see what it was attached to.'
491: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'wound' occurrence 3/5 @ position 229363 ───
492: [2026-06-07 14:05:23] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 229363, end: 229368, context_size: 250, single_sentence: True
493: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'He took the blade and cut a circular [wound] across his arm.'
494: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'wound'
495: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules context_before: 'He took the blade and cut a circular ', context_after: ' across his arm.'
496: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking word 'wound' with 378 rules
497: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: words_before: ['He', 'took', 'the', 'blade', 'and', 'cut', 'a', 'circular'], words_after: ['across', 'his', 'arm.']
498: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound across his'
499: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'circular wound across'
500: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound across'
501: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'circular wound'
502: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['wound across his', 'circular wound across', 'wound across', 'circular wound']
503: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
504: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
505: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'He took the blade and cut a circular [wound] across his arm.'
506: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _run_all_rules for word: 'wound'
507: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_full: 'He took the blade and cut a circular [wound] across his arm.'
508: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules context_before: 'He took the blade and cut a circular ', context_after: ' across his arm.'
509: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'wound'
510: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'wound': 'NN'
511: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'wound'
512: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'wound' → 'woond' (pos-noun)
513: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'wound'
514: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'woond'
515: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'wound'
516: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'woond'
517: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'wound'
518: [2026-06-07 14:05:23] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'wound'
519: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'wound'. Found rules: ['hybrid', 'complex_pos', 'pos']
520: [2026-06-07 14:05:23] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 229363, match.end(): 229368, context_start_raw: 229113, match_start_in_full_text: 229363, match_end_in_full_text: 229368, context_end_raw: 229618
521: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'He took the blade and cut a circular [wound] across his arm.'
522: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'He took the blade and cut a circular [wound] across his arm.'
523: [2026-06-07 14:05:23] [DEBUG] DEBUG: ─── 'wound' occurrence 4/5 @ position 229957 ───
524: [2026-06-07 14:05:23] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 229957, end: 229962, context_size: 250, single_sentence: True
525: [2026-06-07 14:05:23] [DEBUG] DEBUG: Single sentence context: 'Using his right hand, he wiped off half the [wound], then brought the blood up beneath his right eye and smeared a line.'
526: [2026-06-07 14:05:23] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'wound'
527: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules context_before: 'Using his right hand, he wiped off half the ', context_after: ', then brought the blood up beneath his right eye and smeared a line.'
528: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking word 'wound' with 378 rules
529: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Using', 'his', 'right', 'hand,', 'he', 'wiped', 'off', 'half', 'the'], words_after: [',', 'then', 'brought', 'the', 'blood', 'up', 'beneath', 'his', 'right', 'eye', 'and', 'smeared', 'a', 'line.']
530: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound , then'
531: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'the wound ,'
532: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound ,'
533: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'the wound'
534: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['wound , then', 'the wound ,', 'wound ,', 'the wound']
535: [2026-06-07 14:05:23] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
536: [2026-06-07 14:05:23] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
537: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'Using his right hand, he wiped off half the [wound], then brought the blood up beneath his right eye and smeared a line.'
538: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _run_all_rules for word: 'wound'
539: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_full: 'Using his right hand, he wiped off half the [wound], then brought the blood up beneath his right eye and smeared a line.'
540: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_before: 'Using his right hand, he wiped off half the ', context_after: ', then brought the blood up beneath his right eye and smeared a line.'
541: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'wound'
542: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'wound': 'NN'
543: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'wound'
544: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'wound' → 'woond' (pos-noun)
545: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'wound'
546: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'woond'
547: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'wound'
548: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'woond'
549: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'wound'
550: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'wound'
551: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'wound'. Found rules: ['hybrid', 'complex_pos', 'pos']
552: [2026-06-07 14:05:24] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 229957, match.end(): 229962, context_start_raw: 229707, match_start_in_full_text: 229957, match_end_in_full_text: 229962, context_end_raw: 230212
553: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'Using his right hand, he wiped off half the [wound], then brought the blood up beneath his right eye and smeared a line.'
554: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'Using his right hand, he wiped off half the [wound], then brought the blood up beneath his right eye and smeared a line.'
555: [2026-06-07 14:05:24] [DEBUG] DEBUG: ─── 'wound' occurrence 5/5 @ position 266412 ───
556: [2026-06-07 14:05:24] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 266412, end: 266417, context_size: 250, single_sentence: True
557: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'They reached the end of the hall, headed to the right, and [wound] through the underground lair.'
558: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'wound'
559: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules context_before: 'They reached the end of the hall, headed to the right, and ', context_after: ' through the underground lair.'
560: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking word 'wound' with 378 rules
561: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: words_before: ['They', 'reached', 'the', 'end', 'of', 'the', 'hall,', 'headed', 'to', 'the', 'right,', 'and'], words_after: ['through', 'the', 'underground', 'lair.']
562: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound through the'
563: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and wound through'
564: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'wound through'
565: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'and wound'
566: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['wound through the', 'and wound through', 'wound through', 'and wound']
567: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
568: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
569: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'They reached the end of the hall, headed to the right, and [wound] through the underground lair.'
570: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _run_all_rules for word: 'wound'
571: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_full: 'They reached the end of the hall, headed to the right, and [wound] through the underground lair.'
572: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_before: 'They reached the end of the hall, headed to the right, and ', context_after: ' through the underground lair.'
573: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'wound'
574: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'wound': 'VBD'
575: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'wound'
576: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'wound' → 'wow'nd' (pos-verb-wind)
577: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'wound'
578: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'wound'
579: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'wow'nd'
580: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'wound'
581: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'wound'
582: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'wound'. Found rules: ['hybrid', 'pos']
583: [2026-06-07 14:05:24] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 266412, match.end(): 266417, context_start_raw: 266162, match_start_in_full_text: 266412, match_end_in_full_text: 266417, context_end_raw: 266667
584: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'They reached the end of the hall, headed to the right, and [wound] through the underground lair.'
585: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'They reached the end of the hall, headed to the right, and [wound] through the underground lair.'
586: [2026-06-07 14:05:24] [DEBUG] DEBUG: Processing word: 'lead'
587: [2026-06-07 14:05:24] [DEBUG] DEBUG: Found 14 matches for 'lead'
588: [2026-06-07 14:05:24] [DEBUG] DEBUG: Getting options for word: 'lead'
589: [2026-06-07 14:05:24] [DEBUG] DEBUG: ─── 'lead' occurrence 1/14 @ position 108896 ───
590: [2026-06-07 14:05:24] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 108896, end: 108900, context_size: 250, single_sentence: True
591: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'That the AllMother should no longer [lead] us?"'
592: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
593: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules context_before: 'That the AllMother should no longer ', context_after: ' us?"'
594: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
595: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: words_before: ['That', 'the', 'AllMother', 'should', 'no', 'longer'], words_after: ['us?"']
596: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'longer lead us?"'
597: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead us?"'
598: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'longer lead'
599: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['longer lead us?"', 'lead us?"', 'longer lead']
600: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
601: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
602: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'That the AllMother should no longer [lead] us?"'
603: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
604: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_full: 'That the AllMother should no longer [lead] us?"'
605: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_before: 'That the AllMother should no longer ', context_after: ' us?"'
606: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
607: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
608: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
609: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
610: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
611: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
612: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
613: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
614: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
615: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
616: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
617: [2026-06-07 14:05:24] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 108896, match.end(): 108900, context_start_raw: 108646, match_start_in_full_text: 108896, match_end_in_full_text: 108900, context_end_raw: 109150
618: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'That the AllMother should no longer [lead] us?"'
619: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'That the AllMother should no longer [lead] us?"'
620: [2026-06-07 14:05:24] [DEBUG] DEBUG: ─── 'lead' occurrence 2/14 @ position 117758 ───
621: [2026-06-07 14:05:24] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 117758, end: 117762, context_size: 250, single_sentence: True
622: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'The other two Titans followed his [lead].'
623: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
624: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules context_before: 'The other two Titans followed his ', context_after: '.'
625: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
626: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: words_before: ['The', 'other', 'two', 'Titans', 'followed', 'his'], words_after: ['.']
627: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'his lead .'
628: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead .'
629: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'his lead'
630: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['his lead .', 'lead .', 'his lead']
631: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
632: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
633: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: 'The other two Titans followed his [lead].'
634: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
635: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_full: 'The other two Titans followed his [lead].'
636: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules context_before: 'The other two Titans followed his ', context_after: '.'
637: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
638: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'NN'
639: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
640: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (nli=leed(0.97))
641: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
642: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
643: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'led'
644: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
645: [2026-06-07 14:05:24] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
646: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'pos']
647: [2026-06-07 14:05:24] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)
648: [2026-06-07 14:05:24] [DEBUG] DEBUG: Queued item_id_counter: 1
649: [2026-06-07 14:05:24] [DEBUG] DEBUG: ─── 'lead' occurrence 3/14 @ position 178247 ───
650: [2026-06-07 14:05:24] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 178247, end: 178251, context_size: 250, single_sentence: True
651: [2026-06-07 14:05:24] [DEBUG] DEBUG: Single sentence context: '"Where does it [lead] to?"'
652: [2026-06-07 14:05:24] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
653: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules context_before: '"Where does it ', context_after: ' to?"'
654: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
655: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: words_before: ['"Where', 'does', 'it'], words_after: ['to?"']
656: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'it lead to?"'
657: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead to?"'
658: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'it lead'
659: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['it lead to?"', 'lead to?"', 'it lead']
660: [2026-06-07 14:05:24] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
661: [2026-06-07 14:05:24] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
662: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: '"Where does it [lead] to?"'
663: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
664: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_full: '"Where does it [lead] to?"'
665: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_before: '"Where does it ', context_after: ' to?"'
666: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
667: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
668: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
669: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
670: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
671: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
672: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
673: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
674: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
675: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
676: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
677: [2026-06-07 14:05:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 178247, match.end(): 178251, context_start_raw: 177997, match_start_in_full_text: 178247, match_end_in_full_text: 178251, context_end_raw: 178501
678: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: '"Where does it [lead] to?"'
679: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: '"Where does it [lead] to?"'
680: [2026-06-07 14:05:25] [DEBUG] DEBUG: ─── 'lead' occurrence 4/14 @ position 188472 ───
681: [2026-06-07 14:05:25] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 188472, end: 188476, context_size: 250, single_sentence: True
682: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: '"Just trying to follow your [lead], Titan."'
683: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
684: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules context_before: '"Just trying to follow your ', context_after: ', Titan."'
685: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
686: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: words_before: ['"Just', 'trying', 'to', 'follow', 'your'], words_after: [',', 'Titan."']
687: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead , Titan."'
688: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'your lead ,'
689: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead ,'
690: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'your lead'
691: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['lead , Titan."', 'your lead ,', 'lead ,', 'your lead']
692: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
693: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
694: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: '"Just trying to follow your [lead], Titan."'
695: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
696: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_full: '"Just trying to follow your [lead], Titan."'
697: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_before: '"Just trying to follow your ', context_after: ', Titan."'
698: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
699: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'NN'
700: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
701: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (nli=leed(0.97))
702: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
703: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
704: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'led'
705: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
706: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
707: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'pos']
708: [2026-06-07 14:05:25] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)
709: [2026-06-07 14:05:25] [DEBUG] DEBUG: Queued item_id_counter: 2
710: [2026-06-07 14:05:25] [DEBUG] DEBUG: ─── 'lead' occurrence 5/14 @ position 199148 ───
711: [2026-06-07 14:05:25] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 199148, end: 199152, context_size: 250, single_sentence: True
712: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'Maybe you'll [lead] us to glory.'
713: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
714: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules context_before: 'Maybe you'll ', context_after: ' us to glory.'
715: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
716: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Maybe', "you'll"], words_after: ['us', 'to', 'glory.']
717: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead us to'
718: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'you'll lead us'
719: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead us'
720: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'you'll lead'
721: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['lead us to', "you'll lead us", 'lead us', "you'll lead"]
722: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
723: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
724: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'Maybe you'll [lead] us to glory.'
725: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
726: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_full: 'Maybe you'll [lead] us to glory.'
727: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_before: 'Maybe you'll ', context_after: ' us to glory.'
728: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
729: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
730: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
731: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
732: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
733: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
734: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
735: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
736: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
737: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
738: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
739: [2026-06-07 14:05:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 199148, match.end(): 199152, context_start_raw: 198898, match_start_in_full_text: 199148, match_end_in_full_text: 199152, context_end_raw: 199402
740: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'Maybe you'll [lead] us to glory.'
741: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'Maybe you'll [lead] us to glory.'
742: [2026-06-07 14:05:25] [DEBUG] DEBUG: ─── 'lead' occurrence 6/14 @ position 280488 ───
743: [2026-06-07 14:05:25] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 280488, end: 280492, context_size: 250, single_sentence: True
744: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'You will not have a say in who I choose to serve or [lead]."'
745: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
746: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules context_before: 'You will not have a say in who I choose to serve or ', context_after: '."'
747: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
748: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: words_before: ['You', 'will', 'not', 'have', 'a', 'say', 'in', 'who', 'I', 'choose', 'to', 'serve', 'or'], words_after: ['."']
749: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'or lead ."'
750: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead ."'
751: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'or lead'
752: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['or lead ."', 'lead ."', 'or lead']
753: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
754: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
755: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'You will not have a say in who I choose to serve or [lead]."'
756: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
757: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_full: 'You will not have a say in who I choose to serve or [lead]."'
758: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_before: 'You will not have a say in who I choose to serve or ', context_after: '."'
759: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
760: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
761: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
762: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
763: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
764: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
765: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
766: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
767: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
768: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'pos']
769: [2026-06-07 14:05:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 280488, match.end(): 280492, context_start_raw: 280238, match_start_in_full_text: 280488, match_end_in_full_text: 280492, context_end_raw: 280742
770: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'You will not have a say in who I choose to serve or [lead]."'
771: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'You will not have a say in who I choose to serve or [lead]."'
772: [2026-06-07 14:05:25] [DEBUG] DEBUG: ─── 'lead' occurrence 7/14 @ position 281573 ───
773: [2026-06-07 14:05:25] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 281573, end: 281577, context_size: 250, single_sentence: True
774: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'This isn't my war to [lead].'
775: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
776: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules context_before: 'This isn't my war to ', context_after: '.'
777: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
778: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: words_before: ['This', "isn't", 'my', 'war', 'to'], words_after: ['.']
779: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead .'
780: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead .'
781: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead'
782: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['to lead .', 'lead .', 'to lead']
783: [2026-06-07 14:05:25] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
784: [2026-06-07 14:05:25] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
785: [2026-06-07 14:05:25] [DEBUG] DEBUG: Single sentence context: 'This isn't my war to [lead].'
786: [2026-06-07 14:05:25] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
787: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_full: 'This isn't my war to [lead].'
788: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules context_before: 'This isn't my war to ', context_after: '.'
789: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
790: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
791: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
792: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
793: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
794: [2026-06-07 14:05:25] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
795: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
796: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
797: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
798: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'pos']
799: [2026-06-07 14:05:26] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 281573, match.end(): 281577, context_start_raw: 281323, match_start_in_full_text: 281573, match_end_in_full_text: 281577, context_end_raw: 281827
800: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'This isn't my war to [lead].'
801: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'This isn't my war to [lead].'
802: [2026-06-07 14:05:26] [DEBUG] DEBUG: ─── 'lead' occurrence 8/14 @ position 296963 ───
803: [2026-06-07 14:05:26] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 296963, end: 296967, context_size: 250, single_sentence: True
804: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Obs barked and then rushed forward, passing both of them and taking the [lead].'
805: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
806: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules context_before: 'Obs barked and then rushed forward, passing both of them and taking the ', context_after: '.'
807: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
808: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Obs', 'barked', 'and', 'then', 'rushed', 'forward,', 'passing', 'both', 'of', 'them', 'and', 'taking', 'the'], words_after: ['.']
809: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'the lead .'
810: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead .'
811: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'the lead'
812: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['the lead .', 'lead .', 'the lead']
813: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
814: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
815: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Obs barked and then rushed forward, passing both of them and taking the [lead].'
816: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
817: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_full: 'Obs barked and then rushed forward, passing both of them and taking the [lead].'
818: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_before: 'Obs barked and then rushed forward, passing both of them and taking the ', context_after: '.'
819: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
820: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'NN'
821: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
822: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (nli=leed(0.87))
823: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
824: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
825: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'led'
826: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
827: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
828: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'pos']
829: [2026-06-07 14:05:26] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)
830: [2026-06-07 14:05:26] [DEBUG] DEBUG: Queued item_id_counter: 3
831: [2026-06-07 14:05:26] [DEBUG] DEBUG: ─── 'lead' occurrence 9/14 @ position 315633 ───
832: [2026-06-07 14:05:26] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 315633, end: 315637, context_size: 250, single_sentence: True
833: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to [lead].'
834: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
835: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules context_before: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to ', context_after: '.'
836: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
837: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: words_before: ['Soldiers', 'had', 'died', 'in', 'them,', 'though—his', 'troops,', 'the', 'ones', 'this', 'old', 'woman', 'wanted', 'him', 'to'], words_after: ['.']
838: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead .'
839: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead .'
840: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead'
841: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['to lead .', 'lead .', 'to lead']
842: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
843: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
844: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to [lead].'
845: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
846: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_full: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to [lead].'
847: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_before: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to ', context_after: '.'
848: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
849: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
850: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
851: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
852: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
853: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
854: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
855: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
856: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
857: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
858: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
859: [2026-06-07 14:05:26] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 315633, match.end(): 315637, context_start_raw: 315383, match_start_in_full_text: 315633, match_end_in_full_text: 315637, context_end_raw: 315887
860: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to [lead].'
861: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'Soldiers had died in them, though—his troops, the ones this old woman wanted him to [lead].'
862: [2026-06-07 14:05:26] [DEBUG] DEBUG: ─── 'lead' occurrence 10/14 @ position 315926 ───
863: [2026-06-07 14:05:26] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 315926, end: 315930, context_size: 250, single_sentence: True
864: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'The pen may [lead] to action, but that action is always the letting of blood.'
865: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
866: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules context_before: 'The pen may ', context_after: ' to action, but that action is always the letting of blood.'
867: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
868: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: words_before: ['The', 'pen', 'may'], words_after: ['to', 'action,', 'but', 'that', 'action', 'is', 'always', 'the', 'letting', 'of', 'blood.']
869: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead to action,'
870: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'may lead to'
871: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead to'
872: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'may lead'
873: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['lead to action,', 'may lead to', 'lead to', 'may lead']
874: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
875: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
876: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'The pen may [lead] to action, but that action is always the letting of blood.'
877: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
878: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_full: 'The pen may [lead] to action, but that action is always the letting of blood.'
879: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_before: 'The pen may ', context_after: ' to action, but that action is always the letting of blood.'
880: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
881: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
882: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
883: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
884: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
885: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
886: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
887: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
888: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
889: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
890: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
891: [2026-06-07 14:05:26] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 315926, match.end(): 315930, context_start_raw: 315676, match_start_in_full_text: 315926, match_end_in_full_text: 315930, context_end_raw: 316180
892: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'The pen may [lead] to action, but that action is always the letting of blood.'
893: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'The pen may [lead] to action, but that action is always the letting of blood.'
894: [2026-06-07 14:05:26] [DEBUG] DEBUG: ─── 'lead' occurrence 11/14 @ position 363375 ───
895: [2026-06-07 14:05:26] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 363375, end: 363379, context_size: 250, single_sentence: True
896: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'He didn’t understand this group, and now he, a warrior, was supposed to [lead] it?'
897: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'
898: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules context_before: 'He didn’t understand this group, and now he, a warrior, was supposed to ', context_after: ' it?'
899: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking word 'lead' with 378 rules
900: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: words_before: ['He', 'didn’t', 'understand', 'this', 'group,', 'and', 'now', 'he,', 'a', 'warrior,', 'was', 'supposed', 'to'], words_after: ['it?']
901: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead it?'
902: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'lead it?'
903: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'to lead'
904: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['to lead it?', 'lead it?', 'to lead']
905: [2026-06-07 14:05:26] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
906: [2026-06-07 14:05:26] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
907: [2026-06-07 14:05:26] [DEBUG] DEBUG: Single sentence context: 'He didn’t understand this group, and now he, a warrior, was supposed to [lead] it?'
908: [2026-06-07 14:05:26] [DEBUG] DEBUG: Entering _run_all_rules for word: 'lead'
909: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_full: 'He didn’t understand this group, and now he, a warrior, was supposed to [lead] it?'
910: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules context_before: 'He didn’t understand this group, and now he, a warrior, was supposed to ', context_after: ' it?'
911: [2026-06-07 14:05:26] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'lead'
912: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'lead': 'VB'
913: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'lead'
914: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'lead' → 'leed' (pos-verb)
915: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'lead'
916: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'leed'
917: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'lead'
918: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'leed'
919: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'lead'
920: [2026-06-07 14:05:27] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'lead'
921: [2026-06-07 14:05:27] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'lead'. Found rules: ['hybrid', 'complex_pos', 'pos']
922: [2026-06-07 14:05:27] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 363375, match.end(): 363379, context_start_raw: 363125, match_start_in_full_text: 363375, match_end_in_full_text: 363379, context_end_raw: 363629
923: [2026-06-07 14:05:27] [DEBUG] DEBUG: Single sentence context: 'He didn’t understand this group, and now he, a warrior, was supposed to [lead] it?'
924: [2026-06-07 14:05:27] [DEBUG] DEBUG: Single sentence context: 'He didn’t understand this group, and now he, a warrior, was supposed to [lead] it?'
925: [2026-06-07 14:05:27] [DEBUG] DEBUG: ─── 'lead' occurrence 12/14 @ position 368064 ───
926: [2026-06-07 14:05:27] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 368064, end: 368068, context_size: 250, single_sentence: True
927: [2026-06-07 14:05:27] [DEBUG] DEBUG: Single sentence context: 'He didn’t want to use this master race to kill others but to [lead] them.'
928: [2026-06-07 14:05:27] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'lead'

(Output capped at 50 KB. Showing lines 465-928. Use offset=929 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 8.1s)

_Thinking:_

Let me search for "AI" or "ollama" or "request" or "send" in the log to see if there's any actual AI call made. I need to read more of the log to find if AI was ever actually invoked after items were queued.

Let me search for the actual AI call and the end of the log:

**Tool: grep**

**Input:**
```json
{
  "pattern": "AI.*request|AI.*call|AI.*send|AI.*response|ollama.*request|process.*ai.*queue|ai_queue|batch|flush|finalize|Total AI|AI.*items|AI.*batch",
  "path": "/home/danno/MyApps/BookFix",
  "include": "bookfix_ai_debug.log"
}
```

**Output:**
```
Found 1 matches
/home/danno/MyApps/BookFix/bookfix_ai_debug.log:
  Line 3332: [2026-06-07 14:05:42] [DEBUG] Sending chunk 1 (7 items) to AI for batch analysis. Item IDs: [1, 2, 3, 4, 5, 6, 7]

```

**Tool: grep**

**Input:**
```json
{
  "pattern": "queuing for AI|queued for AI|AI.*prompt|AI.*query|_send_to_ai|_call_ai|_request_ai",
  "path": "/home/danno/MyApps/BookFix",
  "include": "bookfix_ai_debug.log"
}
```

**Output:**
```
Found 7 matches
/home/danno/MyApps/BookFix/bookfix_ai_debug.log:
  Line 647: [2026-06-07 14:05:24] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)

  Line 708: [2026-06-07 14:05:25] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)

  Line 829: [2026-06-07 14:05:26] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'lead' — queuing for AI. Rules fired: hybrid=leed(0.95), pos=led(0.80)

  Line 1208: [2026-06-07 14:05:28] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'tear' — queuing for AI. Rules fired: hybrid=teer(0.95), pos=tair(0.80)

  Line 1272: [2026-06-07 14:05:29] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'records' — queuing for AI. Rules fired: hybrid=rekords(0.95), pos=rekkurds(0.80)

  Line 2562: [2026-06-07 14:05:37] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'wind' — queuing for AI. Rules fired: hybrid=win'd(0.95), pos=why'nd(0.80)

  Line 2812: [2026-06-07 14:05:39] [DEBUG] DEBUG: disagreement (hybrid vs pos) for 'wind' — queuing for AI. Rules fired: hybrid=win'd(0.95), pos=why'nd(0.80)

```

---

## Assistant (Plan · MiMo V2.5 Free · 5.1s)

_Thinking:_

So items ARE being queued for AI (7 items). Let me see what happens after they are sent to AI at line 3332. Let me read from there.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix_ai_debug.log",
  "offset": 3320
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix_ai_debug.log</path>
<type>file</type>
<content>
3320: [2026-06-07 14:05:42] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'invalid'
3321: [2026-06-07 14:05:42] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'invalid'
3322: [2026-06-07 14:05:42] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'in-valid'
3323: [2026-06-07 14:05:42] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'invalid'
3324: [2026-06-07 14:05:42] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'invalid'
3325: [2026-06-07 14:05:42] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'invalid'. Found rules: ['hybrid', 'pos']
3326: [2026-06-07 14:05:42] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 340735, match.end(): 340742, context_start_raw: 340485, match_start_in_full_text: 340735, match_end_in_full_text: 340742, context_end_raw: 340992
3327: [2026-06-07 14:05:42] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].'
3328: [2026-06-07 14:05:42] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].'
3329: [2026-06-07 14:05:42] [DEBUG] DEBUG: Processing word: 'polish'
3330: [2026-06-07 14:05:42] [DEBUG] DEBUG: Found 0 matches for 'polish'
3331: [2026-06-07 14:05:42] [INFO] Processing 7 items in chunks of 10.
3332: [2026-06-07 14:05:42] [DEBUG] Sending chunk 1 (7 items) to AI for batch analysis. Item IDs: [1, 2, 3, 4, 5, 6, 7]
3333: [2026-06-07 14:05:42] [DEBUG]
3334: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3335: [2026-06-07 14:05:42] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3336: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3337:
3338: **REFERENCE EXAMPLES (correct usage for each word):**
3339:   lead → "leed": "The captain will lead the team to victory."
3340:   lead → "leed": "She will lead the orchestra tonight."
3341:   lead → "led": "he old pipes in the historic building were made of lead."
3342:   lead → "led": "Fishermen often use small lead weights."
3343:   lead → "led": "the room had lead shielding to block radiation."
3344:   records → "rekkurds": "She brought the records to the file cabinet."
3345:   records → "rekkurds": "His records of the meeting were detailed."
3346:   records → "rekords": "She records the meeting for those who can't attend."
3347:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3348:   tear → "tair": "Be careful not to tear the paper."
3349:   tear → "tair": "The dog tried to tear the toy apart."
3350:   tear → "teer": "A tear ran down her cheek."
3351:   tear → "teer": "The movie a tear to my eye."
3352:   wind → "win'd": "The wind howled through the trees all night."
3353:   wind → "win'd": "A cold wind blew in from the north."
3354:   wind → "win'd": "The trade wind carried the scent of the sea."
3355:   wind → "win'd": "She turned her face into the wind."
3356:   wind → "why'nd": "She began to wind the ribbon around the package."
3357:   wind → "why'nd": "The river wound its way through the valley."
3358:   wind → "why'nd": "He wound the clock before going to bed."
3359:   wind → "why'nd": "The road winds up through the mountains."
3360:
3361: === SENTENCE TO ANALYZE ===
3362: [
3363: {"id": 1, "word": "lead", "context": "The other two Titans followed his [lead].", "options": [{"spelling": "leed", "meaning": "leed"}, {"spelling": "led", "meaning": "led"}]}
3364: ]
3365:
3366: === INSTRUCTIONS ===
3367: 1. Read the sentence carefully
3368: 2. Study the examples provided for each option
3369: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3370: 4. Choose the spelling whose examples most closely align with the sentence
3371: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3372:
3373: === OUTPUT FORMAT ===
3374: Return ONLY a JSON array with this exact structure:
3375: [
3376:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3377: ]
3378:
3379: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3380:
3381: [2026-06-07 14:05:43] [DEBUG] Starting new HTTP connection (1): localhost:11434
3382: [2026-06-07 14:05:43] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3383: [2026-06-07 14:05:45] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3384: [2026-06-07 14:05:48] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3385: [2026-06-07 14:05:48] [DEBUG]
3386: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3387: [2026-06-07 14:05:48] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3388: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3389:
3390: **REFERENCE EXAMPLES (correct usage for each word):**
3391:   lead → "leed": "The captain will lead the team to victory."
3392:   lead → "leed": "She will lead the orchestra tonight."
3393:   lead → "led": "he old pipes in the historic building were made of lead."
3394:   lead → "led": "Fishermen often use small lead weights."
3395:   lead → "led": "the room had lead shielding to block radiation."
3396:   records → "rekkurds": "She brought the records to the file cabinet."
3397:   records → "rekkurds": "His records of the meeting were detailed."
3398:   records → "rekords": "She records the meeting for those who can't attend."
3399:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3400:   tear → "tair": "Be careful not to tear the paper."
3401:   tear → "tair": "The dog tried to tear the toy apart."
3402:   tear → "teer": "A tear ran down her cheek."
3403:   tear → "teer": "The movie a tear to my eye."
3404:   wind → "win'd": "The wind howled through the trees all night."
3405:   wind → "win'd": "A cold wind blew in from the north."
3406:   wind → "win'd": "The trade wind carried the scent of the sea."
3407:   wind → "win'd": "She turned her face into the wind."
3408:   wind → "why'nd": "She began to wind the ribbon around the package."
3409:   wind → "why'nd": "The river wound its way through the valley."
3410:   wind → "why'nd": "He wound the clock before going to bed."
3411:   wind → "why'nd": "The road winds up through the mountains."
3412:
3413: === SENTENCE TO ANALYZE ===
3414: [
3415: {"id": 1, "word": "lead", "context": "\"Just trying to follow your [lead], Titan.\"", "options": [{"spelling": "leed", "meaning": "leed"}, {"spelling": "led", "meaning": "led"}]}
3416: ]
3417:
3418: === INSTRUCTIONS ===
3419: 1. Read the sentence carefully
3420: 2. Study the examples provided for each option
3421: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3422: 4. Choose the spelling whose examples most closely align with the sentence
3423: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3424:
3425: === OUTPUT FORMAT ===
3426: Return ONLY a JSON array with this exact structure:
3427: [
3428:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3429: ]
3430:
3431: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3432:
3433: [2026-06-07 14:05:49] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3434: [2026-06-07 14:05:51] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3435: [2026-06-07 14:05:54] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3436: [2026-06-07 14:05:54] [DEBUG]
3437: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3438: [2026-06-07 14:05:54] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3439: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3440:
3441: **REFERENCE EXAMPLES (correct usage for each word):**
3442:   lead → "leed": "The captain will lead the team to victory."
3443:   lead → "leed": "She will lead the orchestra tonight."
3444:   lead → "led": "he old pipes in the historic building were made of lead."
3445:   lead → "led": "Fishermen often use small lead weights."
3446:   lead → "led": "the room had lead shielding to block radiation."
3447:   records → "rekkurds": "She brought the records to the file cabinet."
3448:   records → "rekkurds": "His records of the meeting were detailed."
3449:   records → "rekords": "She records the meeting for those who can't attend."
3450:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3451:   tear → "tair": "Be careful not to tear the paper."
3452:   tear → "tair": "The dog tried to tear the toy apart."
3453:   tear → "teer": "A tear ran down her cheek."
3454:   tear → "teer": "The movie a tear to my eye."
3455:   wind → "win'd": "The wind howled through the trees all night."
3456:   wind → "win'd": "A cold wind blew in from the north."
3457:   wind → "win'd": "The trade wind carried the scent of the sea."
3458:   wind → "win'd": "She turned her face into the wind."
3459:   wind → "why'nd": "She began to wind the ribbon around the package."
3460:   wind → "why'nd": "The river wound its way through the valley."
3461:   wind → "why'nd": "He wound the clock before going to bed."
3462:   wind → "why'nd": "The road winds up through the mountains."
3463:
3464: === SENTENCE TO ANALYZE ===
3465: [
3466: {"id": 1, "word": "lead", "context": "Obs barked and then rushed forward, passing both of them and taking the [lead].", "options": [{"spelling": "leed", "meaning": "leed"}, {"spelling": "led", "meaning": "led"}]}
3467: ]
3468:
3469: === INSTRUCTIONS ===
3470: 1. Read the sentence carefully
3471: 2. Study the examples provided for each option
3472: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3473: 4. Choose the spelling whose examples most closely align with the sentence
3474: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3475:
3476: === OUTPUT FORMAT ===
3477: Return ONLY a JSON array with this exact structure:
3478: [
3479:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3480: ]
3481:
3482: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3483:
3484: [2026-06-07 14:05:55] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3485: [2026-06-07 14:05:57] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3486: [2026-06-07 14:06:00] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3487: [2026-06-07 14:06:00] [DEBUG]
3488: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3489: [2026-06-07 14:06:00] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3490: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3491:
3492: **REFERENCE EXAMPLES (correct usage for each word):**
3493:   lead → "leed": "The captain will lead the team to victory."
3494:   lead → "leed": "She will lead the orchestra tonight."
3495:   lead → "led": "he old pipes in the historic building were made of lead."
3496:   lead → "led": "Fishermen often use small lead weights."
3497:   lead → "led": "the room had lead shielding to block radiation."
3498:   records → "rekkurds": "She brought the records to the file cabinet."
3499:   records → "rekkurds": "His records of the meeting were detailed."
3500:   records → "rekords": "She records the meeting for those who can't attend."
3501:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3502:   tear → "tair": "Be careful not to tear the paper."
3503:   tear → "tair": "The dog tried to tear the toy apart."
3504:   tear → "teer": "A tear ran down her cheek."
3505:   tear → "teer": "The movie a tear to my eye."
3506:   wind → "win'd": "The wind howled through the trees all night."
3507:   wind → "win'd": "A cold wind blew in from the north."
3508:   wind → "win'd": "The trade wind carried the scent of the sea."
3509:   wind → "win'd": "She turned her face into the wind."
3510:   wind → "why'nd": "She began to wind the ribbon around the package."
3511:   wind → "why'nd": "The river wound its way through the valley."
3512:   wind → "why'nd": "He wound the clock before going to bed."
3513:   wind → "why'nd": "The road winds up through the mountains."
3514:
3515: === SENTENCE TO ANALYZE ===
3516: [
3517: {"id": 1, "word": "tear", "context": "A [tear] dropped from her eye and rolled down her face.", "options": [{"spelling": "tair", "meaning": "tair"}, {"spelling": "teer", "meaning": "teer"}]}
3518: ]
3519:
3520: === INSTRUCTIONS ===
3521: 1. Read the sentence carefully
3522: 2. Study the examples provided for each option
3523: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3524: 4. Choose the spelling whose examples most closely align with the sentence
3525: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3526:
3527: === OUTPUT FORMAT ===
3528: Return ONLY a JSON array with this exact structure:
3529: [
3530:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3531: ]
3532:
3533: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3534:
3535: [2026-06-07 14:06:01] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3536: [2026-06-07 14:06:03] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3537: [2026-06-07 14:06:06] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3538: [2026-06-07 14:06:06] [DEBUG]
3539: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3540: [2026-06-07 14:06:06] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3541: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3542:
3543: **REFERENCE EXAMPLES (correct usage for each word):**
3544:   lead → "leed": "The captain will lead the team to victory."
3545:   lead → "leed": "She will lead the orchestra tonight."
3546:   lead → "led": "he old pipes in the historic building were made of lead."
3547:   lead → "led": "Fishermen often use small lead weights."
3548:   lead → "led": "the room had lead shielding to block radiation."
3549:   records → "rekkurds": "She brought the records to the file cabinet."
3550:   records → "rekkurds": "His records of the meeting were detailed."
3551:   records → "rekords": "She records the meeting for those who can't attend."
3552:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3553:   tear → "tair": "Be careful not to tear the paper."
3554:   tear → "tair": "The dog tried to tear the toy apart."
3555:   tear → "teer": "A tear ran down her cheek."
3556:   tear → "teer": "The movie a tear to my eye."
3557:   wind → "win'd": "The wind howled through the trees all night."
3558:   wind → "win'd": "A cold wind blew in from the north."
3559:   wind → "win'd": "The trade wind carried the scent of the sea."
3560:   wind → "win'd": "She turned her face into the wind."
3561:   wind → "why'nd": "She began to wind the ribbon around the package."
3562:   wind → "why'nd": "The river wound its way through the valley."
3563:   wind → "why'nd": "He wound the clock before going to bed."
3564:   wind → "why'nd": "The road winds up through the mountains."
3565:
3566: === SENTENCE TO ANALYZE ===
3567: [
3568: {"id": 1, "word": "records", "context": "Whatever name history [records], however it records his deeds, I will live or die with him.", "options": [{"spelling": "rekkurds", "meaning": "rekkurds"}, {"spelling": "rekords", "meaning": "rekords"}]}
3569: ]
3570:
3571: === INSTRUCTIONS ===
3572: 1. Read the sentence carefully
3573: 2. Study the examples provided for each option
3574: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3575: 4. Choose the spelling whose examples most closely align with the sentence
3576: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3577:
3578: === OUTPUT FORMAT ===
3579: Return ONLY a JSON array with this exact structure:
3580: [
3581:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3582: ]
3583:
3584: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3585:
3586: [2026-06-07 14:06:07] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3587: [2026-06-07 14:06:09] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3588: [2026-06-07 14:06:12] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3589: [2026-06-07 14:06:12] [DEBUG]
3590: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3591: [2026-06-07 14:06:12] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3592: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3593:
3594: **REFERENCE EXAMPLES (correct usage for each word):**
3595:   lead → "leed": "The captain will lead the team to victory."
3596:   lead → "leed": "She will lead the orchestra tonight."
3597:   lead → "led": "he old pipes in the historic building were made of lead."
3598:   lead → "led": "Fishermen often use small lead weights."
3599:   lead → "led": "the room had lead shielding to block radiation."
3600:   records → "rekkurds": "She brought the records to the file cabinet."
3601:   records → "rekkurds": "His records of the meeting were detailed."
3602:   records → "rekords": "She records the meeting for those who can't attend."
3603:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3604:   tear → "tair": "Be careful not to tear the paper."
3605:   tear → "tair": "The dog tried to tear the toy apart."
3606:   tear → "teer": "A tear ran down her cheek."
3607:   tear → "teer": "The movie a tear to my eye."
3608:   wind → "win'd": "The wind howled through the trees all night."
3609:   wind → "win'd": "A cold wind blew in from the north."
3610:   wind → "win'd": "The trade wind carried the scent of the sea."
3611:   wind → "win'd": "She turned her face into the wind."
3612:   wind → "why'nd": "She began to wind the ribbon around the package."
3613:   wind → "why'nd": "The river wound its way through the valley."
3614:   wind → "why'nd": "He wound the clock before going to bed."
3615:   wind → "why'nd": "The road winds up through the mountains."
3616:
3617: === SENTENCE TO ANALYZE ===
3618: [
3619: {"id": 1, "word": "wind", "context": "[Wind] ripped around Odin as blood leaked from his battered body.", "options": [{"spelling": "win'd", "meaning": "win'd"}, {"spelling": "why'nd", "meaning": "why'nd"}]}
3620: ]
3621:
3622: === INSTRUCTIONS ===
3623: 1. Read the sentence carefully
3624: 2. Study the examples provided for each option
3625: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3626: 4. Choose the spelling whose examples most closely align with the sentence
3627: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3628:
3629: === OUTPUT FORMAT ===
3630: Return ONLY a JSON array with this exact structure:
3631: [
3632:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3633: ]
3634:
3635: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3636:
3637: [2026-06-07 14:06:13] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3638: [2026-06-07 14:06:15] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3639: [2026-06-07 14:06:18] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3640: [2026-06-07 14:06:18] [DEBUG]
3641: === ANALYZING HOMOGRAPH BATCH (1 items) ===
3642: [2026-06-07 14:06:18] [DEBUG] Batch prompt sent to AI (Provider: ollama):
3643: You are a TTS pronunciation analyzer. Your job is to choose the correct pronunciation spelling for a homograph based on sentence context and examples.
3644:
3645: **REFERENCE EXAMPLES (correct usage for each word):**
3646:   lead → "leed": "The captain will lead the team to victory."
3647:   lead → "leed": "She will lead the orchestra tonight."
3648:   lead → "led": "he old pipes in the historic building were made of lead."
3649:   lead → "led": "Fishermen often use small lead weights."
3650:   lead → "led": "the room had lead shielding to block radiation."
3651:   records → "rekkurds": "She brought the records to the file cabinet."
3652:   records → "rekkurds": "His records of the meeting were detailed."
3653:   records → "rekords": "She records the meeting for those who can't attend."
3654:   records → "rekords": "hatever name history records, however it records his deeds, I will live or die with him."
3655:   tear → "tair": "Be careful not to tear the paper."
3656:   tear → "tair": "The dog tried to tear the toy apart."
3657:   tear → "teer": "A tear ran down her cheek."
3658:   tear → "teer": "The movie a tear to my eye."
3659:   wind → "win'd": "The wind howled through the trees all night."
3660:   wind → "win'd": "A cold wind blew in from the north."
3661:   wind → "win'd": "The trade wind carried the scent of the sea."
3662:   wind → "win'd": "She turned her face into the wind."
3663:   wind → "why'nd": "She began to wind the ribbon around the package."
3664:   wind → "why'nd": "The river wound its way through the valley."
3665:   wind → "why'nd": "He wound the clock before going to bed."
3666:   wind → "why'nd": "The road winds up through the mountains."
3667:
3668: === SENTENCE TO ANALYZE ===
3669: [
3670: {"id": 1, "word": "wind", "context": "He was fifty meters from the portal when the flames and [wind] started from above.", "options": [{"spelling": "win'd", "meaning": "win'd"}, {"spelling": "why'nd", "meaning": "why'nd"}]}
3671: ]
3672:
3673: === INSTRUCTIONS ===
3674: 1. Read the sentence carefully
3675: 2. Study the examples provided for each option
3676: 3. Match the sentence pattern against the examples — which set of examples best matches the current context?
3677: 4. Choose the spelling whose examples most closely align with the sentence
3678: 5. Your choice MUST be exactly one of the provided spelling codes — NOT the word as it appears in the sentence. These are TTS pronunciation codes, not standard spellings.
3679:
3680: === OUTPUT FORMAT ===
3681: Return ONLY a JSON array with this exact structure:
3682: [
3683:   {"id": N, "decision": {"choice": "exact_spelling_from_options", "reasoning": "why this matches the examples and context"}}
3684: ]
3685:
3686: Where N is the id from the input. CRITICAL: Do not deviate from this format. The "choice" must exactly match a spelling in the options array.
3687:
3688: [2026-06-07 14:06:19] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3689: [2026-06-07 14:06:21] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3690: [2026-06-07 14:06:24] [DEBUG] http://localhost:11434 "POST /api/generate HTTP/1.1" 404 46
3691: [2026-06-07 14:06:24] [DEBUG] DEBUG: Received chunk results. Item IDs: [1, 2, 3, 4, 5, 6, 7]
3692: [2026-06-07 14:06:24] [DEBUG] DEBUG: Processing item_id: 1
3693: [2026-06-07 14:06:24] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 117758, match.end(): 117762, context_start_raw: 117508, match_start_in_full_text: 117758, match_end_in_full_text: 117762, context_end_raw: 118012
3694: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'The other two Titans followed his [lead].'
3695: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'The other two Titans followed his [lead].'
3696: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 2
3697: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 188472, match.end(): 188476, context_start_raw: 188222, match_start_in_full_text: 188472, match_end_in_full_text: 188476, context_end_raw: 188726
3698: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: '"Just trying to follow your [lead], Titan."'
3699: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: '"Just trying to follow your [lead], Titan."'
3700: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 3
3701: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 296963, match.end(): 296967, context_start_raw: 296713, match_start_in_full_text: 296963, match_end_in_full_text: 296967, context_end_raw: 297217
3702: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'Obs barked and then rushed forward, passing both of them and taking the [lead].'
3703: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'Obs barked and then rushed forward, passing both of them and taking the [lead].'
3704: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 4
3705: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 104712, match.end(): 104716, context_start_raw: 104462, match_start_in_full_text: 104712, match_end_in_full_text: 104716, context_end_raw: 104966
3706: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'A [tear] dropped from her eye and rolled down her face.'
3707: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'A [tear] dropped from her eye and rolled down her face.'
3708: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 5
3709: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 3387, match.end(): 3394, context_start_raw: 3137, match_start_in_full_text: 3387, match_end_in_full_text: 3394, context_end_raw: 3644
3710: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'Whatever name history [records], however it records his deeds, I will live or die with him.'
3711: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'Whatever name history [records], however it records his deeds, I will live or die with him.'
3712: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 6
3713: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 25493, match.end(): 25497, context_start_raw: 25243, match_start_in_full_text: 25493, match_end_in_full_text: 25497, context_end_raw: 25747
3714: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: '[Wind] ripped around Odin as blood leaked from his battered body.'
3715: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: '[Wind] ripped around Odin as blood leaked from his battered body.'
3716: [2026-06-07 14:06:25] [DEBUG] DEBUG: Processing item_id: 7
3717: [2026-06-07 14:06:25] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 334503, match.end(): 334507, context_start_raw: 334253, match_start_in_full_text: 334503, match_end_in_full_text: 334507, context_end_raw: 334757
3718: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'He was fifty meters from the portal when the flames and [wind] started from above.'
3719: [2026-06-07 14:06:25] [DEBUG] DEBUG: Single sentence context: 'He was fifty meters from the portal when the flames and [wind] started from above.'
3720: [2026-06-07 14:06:25] [INFO] AI review mode complete: 92 decisions logged for review
3721: [2026-06-07 14:06:25] [INFO] AI review mode complete: 92 changes processed for review
3722: [2026-06-07 14:06:25] [DEBUG] DEBUG: Exiting process_choices_ai_review_mode
3723: [2026-06-07 14:06:25] [INFO] AI analysis complete. 92 decisions ready for review.
3724: [2026-06-07 14:06:25] [INFO] GUI: Got decision stats: Counter({'complex_pos': 48, 'hybrid': 37, 'disagreement': 7})
3725: [2026-06-07 14:17:49] [INFO] Application closing

(End of file - total 3725 lines)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 17.7s)

_Thinking:_

Now I have a clear picture. Let me analyze the log:

1. **Items ARE sent to AI for processing** - 7 items were queued (items with disagreements between hybrid and POS rules), and they were sent in chunks.

2. **The AI requests are failing** - Every single POST to `localhost:11434` (Ollama) returns **HTTP 404**. This is the critical issue.

The flow is:
- 7 items were queued for AI due to rule disagreements (lead ×3, tear ×1, records ×1, wind ×2)
- The system sent them one at a time (despite the chunk size being 10, it sent "chunk 1 (7 items)" but then processed each individually with a separate API call)
- Each POST to `http://localhost:11434/api/generate` returned **404 Not Found**
- The system retried each item 3 times (matching `max_retries: 3`), all 3 attempts returning 404
- After all retries failed, it still processed 7 items but with no actual AI response - the items were likely processed with fallback/default behavior
- Final stats show: `complex_pos: 48, hybrid: 37, disagreement: 7` - all 7 disagreements are still there

The root cause is clear: **Ollama is returning 404** for the `/api/generate` endpoint. This could mean:
1. The model `qwen-big:latest` is not pulled/available in Ollama
2. Ollama's API endpoint has changed (newer versions use `/api/chat` instead of `/api/generate`)
3. The Ollama server is running but the model isn't loaded

Actually, looking more carefully - the 404 response from `POST /api/generate` suggests the model name might not be valid or the endpoint doesn't recognize it. In newer Ollama versions, the generate endpoint still exists, but if the model isn't available, it would return a different error. A 404 typically means the route itself isn't found... wait, `/api/generate` is a standard Ollama endpoint.

Actually, looking at Ollama's behavior:
- 404 from `/api/generate` could mean the model doesn't exist/isn't pulled
- Or it could be an older Ollama version that doesn't support that endpoint

Let me also note another issue: the system sends 7 items but processes them ONE AT A TIME (each as a separate API call with only 1 item), despite saying "chunk 1 (7 items)". This is inefficient but the 404 is the real blocker.

Also important: after all the 404 failures, the system still reports "92 decisions logged for review" and "7 disagreement" decisions - meaning it fell back to default behavior when AI failed.

Here's my analysis:

## AI *Was* Sent to the AI, But Every Request Failed

**7 items were queued** for AI resolution (rule disagreements: lead ×3, tear ×1, records ×1, wind ×2). They **were sent** to Ollama — but every single request got an **HTTP 404**.

### The Problem: Ollama Returns 404 on `/api/generate`

Every POST to `http://localhost:11434/api/generate` returned **404 46** (line 3382 onward). Each item was retried 3 times (`max_retries: 3`), and all 21 attempts (7 items × 3 retries) failed identically.

### Likely Causes

1. **Model `qwen-big:latest` is not pulled/available** in your local Ollama — a 404 from `/api/generate` typically means the model doesn't exist on the server.
2. **Wrong API endpoint** — newer Ollama versions may use `/api/chat` instead of `/api/generate` for chat-capable models.

### Secondary Issue: No Batching

Despite saying "chunk 1 (7 items)", each item is sent as a **separate API call** with only 1 item in the payload. The chunking code isn't actually batching the items together — it's iterating one-by-one inside the chunk.

### What Happened to the 7 Disagreements

After all AI calls failed, the system fell back silently — the final stats show `disagreement: 7`, meaning those 7 items were **never resolved by AI** and presumably kept whatever default the fallback logic assigned.

### What to Check

1. Run `ollama list` — is `qwen-big:latest` listed?
2. Check your Ollama version — does it support `/api/generate` or does it need `/api/chat`?
3. The model name in `ai_config.json` has a trailing space: `'model': 'qwen-big:latest '` — that space could also cause issues.

---

## User

2026-06-07 14:44:53] [DEBUG] DEBUG: Processing word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Found 2 matches for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Getting options for word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: ─── 'invalid' occurrence 1/2 @ position 83507 ───
[2026-06-07 14:44:53] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 83507, end: 83514, context_size: 250, single_sentence: True
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: '"Then show me now, because I will not abide being an [invalid] any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules context_before: '"Then show me now, because I will not abide being an ', context_after: ' any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Checking word 'invalid' with 378 rules
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: words_before: ['"Then', 'show', 'me', 'now,', 'because', 'I', 'will', 'not', 'abide', 'being', 'an'], words_after: ['any', 'longer.']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'invalid any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'an invalid any'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'invalid any'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'an invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['invalid any longer.', 'an invalid any', 'invalid any', 'an invalid']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
[2026-06-07 14:44:53] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: '"Then show me now, because I will not abide being an [invalid] any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Entering _run_all_rules for word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules context_full: '"Then show me now, because I will not abide being an [invalid] any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules context_before: '"Then show me now, because I will not abide being an ', context_after: ' any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'invalid': 'JJ'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'invalid' → 'invalid' (jj-attr-noun)
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Complex POS rule matched: 'in-valid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'in-valid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'invalid'. Found rules: ['hybrid', 'complex_pos', 'pos']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 83507, match.end(): 83514, context_start_raw: 83257, match_start_in_full_text: 83507, match_end_in_full_text: 83514, context_end_raw: 83764
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: '"Then show me now, because I will not abide being an [invalid] any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: '"Then show me now, because I will not abide being an [invalid] any longer.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: ─── 'invalid' occurrence 2/2 @ position 340735 ───
[2026-06-07 14:44:53] [DEBUG] DEBUG: _extract_context - len(text): 397543, start: 340735, end: 340742, context_size: 250, single_sentence: True
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Entering _check_replace_rules for word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules context_before: 'That had changed, though, as he lay there unable to move, an ', context_after: '.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Checking word 'invalid' with 378 rules
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: words_before: ['That', 'had', 'changed,', 'though,', 'as', 'he', 'lay', 'there', 'unable', 'to', 'move,', 'an'], words_after: ['.']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'an invalid .'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'invalid .'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Adding phrase: 'an invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: Checking phrases: ['an invalid .', 'invalid .', 'an invalid']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _check_replace_rules: No REPLACE rule matches found
[2026-06-07 14:44:53] [DEBUG] DEBUG: Exiting _check_replace_rules (no match)
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Entering _run_all_rules for word: 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules context_full: 'That had changed, though, as he lay there unable to move, an [invalid].'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules context_before: 'That had changed, though, as he lay there unable to move, an ', context_after: '.'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Attempting POS tagging for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Detected POS tag for 'invalid': 'JJ'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Using hybrid decider for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Hybrid decider matched 'invalid' → 'in-valid' (pos-adj)
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking complex POS rules for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking simple POS rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Simple POS rule matched: 'in-valid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking semantic rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: _run_all_rules: Checking entity rule for 'invalid'
[2026-06-07 14:44:53] [DEBUG] DEBUG: Exiting _run_all_rules for word: 'invalid'. Found rules: ['hybrid', 'pos']
[2026-06-07 14:44:53] [DEBUG] DEBUG: _log_change - len(full_text): 397543, match.start(): 340735, match.end(): 340742, context_start_raw: 340485, match_start_in_full_text: 340735, match_end_in_full_text: 340742, context_end_raw: 340992
[2026-06-07 14:44:53] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].'
[2026-06-07 14:44:54] [DEBUG] DEBUG: Single sentence context: 'That had changed, though, as he lay there unable to move, an [invalid].' At the end it looks like it chose the correct spelling but the review window shows that it chose something else. It chose in-valid instead of invalid.  Why?

---

## Assistant (Plan · MiMo V2.5 Free · 35.8s)

_Thinking:_

The user is asking about the word "invalid" being chosen as "in-valid" instead of "invalid". Looking at the log:

Occurrence 2/2 for "invalid":
- Context: 'That had changed, though, as he lay there unable to move, an [invalid].'
- POS tag: JJ (adjective)
- Hybrid decider: 'in-valid' (pos-adj)
- Complex POS rule: 'in-valid'
- Simple POS rule: 'in-valid'
- Rules fired: ['hybrid', 'complex_pos', 'pos']

The user wants to know why it chose "in-valid" instead of "invalid". The word "invalid" as a noun (meaning a person made weak or disabled by illness or injury) is pronounced /ˈɪnvəlɪd/ with stress on the first syllable, while "invalid" as an adjective (meaning not valid) is pronounced /ɪnˈvælɪd/ with stress on the second syllable.

So the TTS pronunciation issue is:
- "invalid" (noun) = /ˈɪnvəlɪd/ - the person who is disabled
- "invalid" (adjective) = /ɪnˈvælɪd/ - not valid

The context "an [invalid]" is using "invalid" as a noun (a person), so the pronunciation should be "invalid" (the noun form, stressed first syllable).

But the rules are matching "in-valid" because the POS tag is JJ (adjective). Let me look at what "in-valid" means - it seems like this is the TTS pronunciation code for the adjective form (stressed second syllable: in-VALID).

The problem is:
1. The POS tagger tagged "invalid" as JJ (adjective)
2. The hybrid decider matched it to "in-valid" based on pos-adj
3. But in context, "an invalid" means a disabled person (noun), not "not valid" (adjective)

So the rules chose the wrong pronunciation because the POS tagger misidentified the word as an adjective when it's actually a noun in this context.

Now the user is asking why the review window shows "in-valid" instead of "invalid". This is because the rules all agreed on "in-valid" and there was no disagreement that would send it to AI for review. The rules fired were all consistent: hybrid=pos-adj, complex_pos=in-valid, simple POS=in-valid. Since there was no disagreement between rules, it wasn't queued for AI.

The real issue is: the TTS code "in-valid" is for the adjective form (in-VAL-id), but the context requires the noun form (IN-və-lid). The rules are wrong because they're using POS tagging which misidentified the word class.

Wait, let me re-read the user's question. They say "it chose in-valid instead of invalid". I think they mean the TTS pronunciation output was "in-valid" when it should have been "invalid" (the noun pronunciation).

Looking at the options for "invalid" in the choices.json... I don't see the actual options listed in the log. But typically "invalid" as a noun would have options like "in-valid" (adjective) vs "invalid" (noun).

Actually, looking at the log more carefully:
- The hybrid decider matched 'invalid' → 'invalid' (jj-attr-noun) for occurrence 1
- The hybrid decider matched 'invalid' → 'in-valid' (pos-adj) for occurrence 2

So for occurrence 1, the hybrid correctly identified it as the noun form. For occurrence 2, it chose the adjective form "in-valid".

The difference between the two occurrences:
- Occurrence 1: "being an [invalid] any longer" - hybrid: jj-attr-noun → 'invalid' (noun form)
- Occurrence 2: "an [invalid]." - hybrid: pos-adj → 'in-valid' (adjective form)

The user is saying occurrence 2 should also be the noun form (it's "an invalid" meaning a disabled person), but the rules chose the adjective pronunciation.

The reason is that the POS tagger tagged it as JJ (adjective) for both, but the hybrid decider has different sub-rules:
- For occurrence 1: "jj-attr-noun" pattern matched (being an invalid → noun after "an")
- For occurrence 2: "pos-adj" pattern matched instead

The issue is that occurrence 2 ends with just "an [invalid]." which is less context for the hybrid to determine it's a noun. The hybrid rule might need more context or the "pos-adj" rule is too broad.

But wait - the user says "the review window shows that it chose something else. It chose in-valid instead of invalid." They're looking at the UI and seeing the wrong choice. The rules are all agreeing on "in-valid" so there's no disagreement to trigger AI review, and the user is stuck with the wrong pronunciation.

Let me think about what the user is actually asking - they want to understand why the rules chose "in-valid" (adjective pronunciation) when the context clearly calls for "invalid" (noun pronunciation). The answer is:

1. The POS tagger tagged "invalid" as JJ (adjective)
2. The hybrid decider matched it to "in-valid" based on the adjective pattern
3. All other rules (complex_pos, simple POS) also matched "in-valid"
4. Since all rules agreed, there was no disagreement to send to AI
5. The result was "in-valid" even though the context requires the noun form

The fundamental problem is that the rules are relying on POS tagging which misidentified the word class. "An invalid" in this context is clearly a noun (a person), not an adjective.

Actually, I need to be more careful. Let me look at the first occurrence again:

Occurrence 1: "being an [invalid] any longer"
- POS tag: JJ (adjective)
- Hybrid: 'invalid' (jj-attr-noun)
- Complex POS: 'in-valid'
- Simple POS: 'in-valid'
- Rules fired: ['hybrid', 'complex_pos', 'pos']

Occurrence 2: "an [invalid]."
- POS tag: JJ (adjective)
- Hybrid: 'in-valid' (pos-adj)
- Complex POS: 'in-valid'
- Simple POS: 'in-valid'
- Rules fired: ['hybrid', 'complex_pos', 'pos']

So for occurrence 1, the hybrid correctly chose 'invalid' (noun) despite the JJ tag, using the "jj-attr-noun" sub-pattern. But for occurrence 2, the hybrid chose 'in-valid' (adjective) using the "pos-adj" sub-pattern.

The difference might be in the context - occurrence 1 has "being an [invalid] any longer" which might trigger a different hybrid sub-rule than occurrence 2's "an [invalid]."

The user wants to understand why this happens and presumably wants it fixed.

Looking at the log for occurrence 2 of "invalid":

```
Hybrid decider matched 'invalid' → 'in-valid' (pos-adj)
Complex POS rule matched: 'in-valid'
Simple POS rule matched: 'in-valid'
Rules fired: ['hybrid', 'complex_pos', 'pos']
```

All three rules **agreed** on `in-valid`, so there was no disagreement to trigger AI review. The result was accepted as-is.

### Why the Rules Chose Wrong

The POS tagger tagged "invalid" as **JJ (adjective)** in both occurrences. But the hybrid decider has different sub-patterns:

- **Occurrence 1** ("being an [invalid] any longer"): hybrid matched `jj-attr-noun` → correctly chose `invalid` (noun form)
- **Occurrence 2** ("an [invalid]."): hybrid matched `pos-adj` → chose `in-valid` (adjective form)

The difference is likely the sentence structure — occurrence 2 ends abruptly with just a period, giving the hybrid less context to determine it's being used as a noun. The `pos-adj` sub-pattern fired instead of `jj-attr-noun`.

### The Core Problem

"Invalid" as a **noun** (a disabled person, /ˈɪnvəlɪd/) and as an **adjective** (not valid, /ɪnˈvælɪd/) have different pronunciations. The rules chose the adjective pronunciation when the noun pronunciation was needed — and since all rules agreed, no AI review was triggered to catch the mistake.

### What Needs to Change

The hybrid decider's `pos-adj` sub-pattern is too broad — it fires on "an [word]." even when "an" strongly suggests a noun follows. The `jj-attr-noun` pattern should have fired instead.

Would you like me to investigate the hybrid decider logic to find where the `pos-adj` vs `jj-attr-noun` routing happens?





---

## User

file:///home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py file:///home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py  I'm not sure if the code is all in these two files, but they have something to do with it.  I need you to create a comprehensive flowchart in description of how the choices program works. So how are the hybrid choices made? What decides each homograph's choice? Basically what I need is a breakdown of the rules and how they work, not a technical description, just a basic description of how each word is processed and how it's decided, which version of the spelling of the homograph is used.  The Rules seem to be getting out of control, so I need to understand how they actually work.

---

## Assistant (Plan · MiMo V2.5 Free · 5.8s)

_Thinking:_

The user wants me to understand the flow of how homograph choices are made in the BookFix application. They want a comprehensive flowchart/description of the decision process, not technical code details. I need to read both files to understand the flow.

Let me read both files to understand the decision process.

Let me read both files to understand the full decision flow.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py"
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1: """
2: AI-Enhanced Choice Processor for Bookfix.
3:
4: Extends the InteractiveChoiceProcessor with AI analysis capabilities
5: for automatic homograph disambiguation.
6: """
7:
8: import re
9: import nltk
10: from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Any
11:
12: # Ensure NLTK data is available for sentence tokenization
13: try:
14:     nltk.data.find("tokenizers/punkt")
15: except LookupError:
16:     nltk.download("punkt", quiet=True)
17: try:
18:     nltk.data.find("tokenizers/punkt_tab")
19: except LookupError:
20:     nltk.download("punkt_tab", quiet=True)
21:
22: if TYPE_CHECKING:
23:     from ..context import BookfixContext
24:
25: from .choices import InteractiveChoiceProcessor
26: from ..ai.service import BookfixAIService
27: from ..ai.change_tracker import AIChangeTracker
28:
29: # Choices learning system retired — replaced by dep_rules (choices_pos_dictionary.json)
30: # and curated examples in choices.json. Files preserved at .ai_learning/ for reference.
31: from ..ai.pos_tagger import get_pos_tagger
32: from ..ai.pos_dictionary import get_pos_dictionary
33: from ..ai.hybrid_deciders import DECIDERS, NLI_WORDS
34: from ..lexicon_loader import LexiconLoader
35: from ..logging import log_message
36:
37:
38: class AIChoiceProcessor(InteractiveChoiceProcessor):
39:     """
40:     AI-enhanced choice processor that can automatically resolve homographs
41:     using context analysis, with fallback to manual processing.
42:     """
43:
44:     def __init__(
45:         self,
46:         change_tracker: Optional[AIChangeTracker] = None,
47:         context_size: int = 250,
48:         show_reasoning: bool = False,
49:     ):
50:         """Initializes a new instance of the BookfixAI class.
51:         Args:
52:         change_tracker (Optional[AIChangeTracker]): An optional tracker for changes.
53:         context_size (int): The size of the context to consider.
54:         show_reasoning (bool): Whether to display reasoning.
55:         Returns: None
56:         """
57:         super().__init__()
58:         from collections import Counter
59:
60:         self.ai_service: Optional[BookfixAIService] = None
61:         self.ai_enabled = False
62:         self.ai_verify_all = (
63:             False  # If True, AI verifies ALL decisions, not just uncertain ones
64:         )
65:         self.confidence_threshold = 0.8
66:         self.fallback_to_manual = True
67:         self.context_size = context_size  # Configurable context size for AI analysis
68:         self.rules_only_mode = False  # If True, disable AI and force rule application
69:         self.single_sentence_context = True  # Use single sentence context for rules
70:         self.show_reasoning = (
71:             show_reasoning  # Whether to request AI reasoning (verbose, slower)
72:         )
73:
74:         # Initialize spaCy and lexicon
75:         import spacy
76:
77:         try:
78:             self.nlp = spacy.load("en_core_web_md")
79:         except OSError:
80:             self.nlp = spacy.load("en_core_web_sm")
81:         self.lexicon_loader = LexiconLoader()
82:         self.word_choices = self.lexicon_loader.get_all_words()
83:
84:         # Hybrid deciders for improved accuracy on 22 known homographs
85:         self.nli = None  # Lazy load RoBERTa-MNLI when needed
86:
87:         # Load configuration
88:         self.config = self._load_config()
89:
90:         # Change tracking
91:         self.change_tracker = change_tracker
92:
93:         # Track AI decisions for review
94:         self.ai_decisions = []
95:         self.manual_decisions = []
96:
97:         # Decision statistics
98:         self.decision_stats = Counter()
99:
100:         # Log file for choices processing
101:         self.choices_log_path = None
102:
103:         # POS tagging system (lazy loaded)
104:         self.pos_tagger = None
105:         self.pos_dictionary = None
106:         self.use_pos_tagging = True  # Enable POS-based decisions
107:
108:     def initialize_ai(self, ai_config: Dict) -> bool:
109:         """
110:         Initialize AI service from configuration.
111:
112:         Args:
113:             ai_config: Dictionary with AI configuration
114:
115:         Returns:
116:             True if initialization was successful (AI enabled OR rules available)
117:         """
118:         try:
119:             self.ai_enabled = ai_config.get("ai_enabled", False)
120:             self.ai_verify_all = ai_config.get("ai_verify_all", False)
121:
122:             if not self.ai_enabled:
123:                 log_message(
124:                     "AI processing disabled - using rules-only mode (POS tagging, keywords, learned patterns)"
125:                 )
126:                 # CRITICAL: Set rules_only_mode flag for bypassing logic elsewhere
127:                 self.rules_only_mode = True
128:                 # Return True because review mode can still work with just rules
129:                 # POS tagging, keywords, and learned patterns don't require AI
130:                 return True
131:
132:             if self.ai_verify_all:
133:                 log_message(
134:                     "AI Verify ALL mode: AI will verify every decision, not just uncertain ones"
135:                 )
136:
137:             # Initialize AI service with full configuration
138:             # Supports both old (model_path) and new (provider/model/api_key) style configs
139:             self.ai_service = BookfixAIService(
140:                 model_path=ai_config.get("model_path"),
141:                 provider=ai_config.get("provider", "llama-cpp"),
142:                 model=ai_config.get("model"),
143:                 api_key=ai_config.get("api_key"),
144:                 confidence_threshold=ai_config.get("confidence_threshold", 0.8),
145:                 max_retries=ai_config.get("max_retries", 3),
146:                 rate_limit=ai_config.get("rate_limit", 0.5),
147:             )
148:
149:             # Test AI connection
150:             test_result = self.ai_service.test_connection()
151:             if not test_result.success:
152:                 log_message(
153:                     f"AI service connection failed: {test_result.error_message} — degrading to rules-only mode",
154:                     level="WARNING",
155:                 )
156:                 self.ai_enabled = False
157:                 self.rules_only_mode = True  # Review window still shows; no AI calls
158:                 return True  # Don't fall back to traditional picker
159:             else:
160:                 log_message(
161:                     f"AI service initialized successfully: {test_result.content}"
162:                 )
163:                 self.ai_enabled = True
164:                 return True
165:
166:         except Exception as e:
167:             import traceback
168:
169:             log_message(f"Failed to initialize AI service: {e}", level="ERROR")
170:             log_message(traceback.format_exc(), level="ERROR")
171:             self.ai_enabled = False
172:             return False
173:
174:     def _setup_choices_log(self, file_path: Optional[str]):
175:         """Setup choices.log in the same directory as the input file."""
176:         if file_path:
177:             import os
178:
179:             file_dir = os.path.dirname(file_path)
180:             self.choices_log_path = os.path.join(file_dir, "choices.log")
181:         else:
182:             self.choices_log_path = "choices.log"  # Fallback to current directory
183:
184:         # Create/overwrite the log file at the start of processing
185:         try:
186:             with open(self.choices_log_path, "w", encoding="utf-8") as f:
187:                 f.write("")  # Start with empty file
188:         except Exception as e:
189:             log_message(f"Failed to create choices.log: {e}", level="WARNING")
190:
191:     def _log_to_choices_log(self, message: str):
192:         """Log a message to choices.log."""
193:         if self.choices_log_path:
194:             try:
195:                 import datetime
196:
197:                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
198:                 with open(self.choices_log_path, "w", encoding="utf-8") as f:
199:                     f.write(f"[{timestamp}] {message}\n")
200:             except Exception as e:
201:                 log_message(f"Failed to write to choices.log: {e}", level="WARNING")
202:
203:     def _clear_all_logs(self, ctx: "BookfixContext"):
204:         """Delete all log files for a fresh start - NO archiving."""
205:         import os
206:         import datetime
207:
208:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
209:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
210:
211:         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
212:         mode = (
213:             "Rules-Only"
214:             if self.rules_only_mode
215:             else ("Hybrid" if self.ai_enabled else "Verify-All")
216:         )
217:         total_words = len(ctx.choices) if ctx and ctx.choices else 0
218:
219:         for filename in ["rules_choices.log", "rule_reasoning.log", "aiprompt.txt"]:
220:             filepath = os.path.join(log_dir, "logs", filename)
221:             if os.path.exists(filepath):
222:                 try:
223:                     os.unlink(filepath)
224:                     log_message(f"Deleted old log: {filename}")
225:                 except Exception as e:
226:                     log_message(f"Failed to delete {filename}: {e}", level="WARNING")
227:
228:         header = f"""=== NEW PROCESSING RUN STARTED: {timestamp} ===
229: Input file: {ctx.current_file_path if ctx and ctx.current_file_path else "unknown"}
230: Mode: {mode}
231: Total homographs configured: {total_words}
232: ================================================
233: """
234:
235:         rules_choices_path = os.path.join(log_dir, "logs", "rules_choices.log")
236:         with open(rules_choices_path, "w", encoding="utf-8") as f:
237:             f.write(header)
238:
239:         reason_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
240:         legend = """RULE TYPE EXPLANATIONS:
241:   complex_pos - Uses spaCy dependency parsing for special syntactic patterns (imperatives, auxiliaries)
242:   pos        - Basic POS tag match from spaCy (VB, NN, JJ, etc.)
243:   semantic   - Domain-aware keyword matching (audio, aquatic, social, physical categories)
244:   entity     - Named entity context (PERSON, ORG, GPE tags or entity patterns)
245:   definition - Dictionary/definition-based rule from choices_pos_dictionary.json
246:   keyword    - Direct keyword match from context_keywords lists
247:   consensus - All rules that fired agree on the same choice
248:   Priority order (highest to lowest): complex_pos > entity > pos > semantic > definition > keyword
249: ================================================================================
250: """
251:         with open(reason_path, "w", encoding="utf-8") as f:
252:             f.write(header)
253:             f.write(legend)
254:
255:         log_message(f"All logs cleared for new run: {timestamp}")
256:
257:     def _write_end_of_run_summary(self):
258:         """Write end-of-run summary to both log files."""
259:         import os
260:         import datetime
261:
262:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
263:         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
264:
265:         total_changes = (
266:             len(self.change_tracker.changes)
267:             if self.change_tracker and self.change_tracker.changes
268:             else 0
269:         )
270:         stats = dict(self.decision_stats)
271:
272:         summary = f"""
273: ================================================
274: PROCESSING COMPLETED: {timestamp}
275: Total changes processed: {total_changes}
276: Decision breakdown: {stats}
277: ================================================
278: """
279:
280:         rules_choices_path = os.path.join(log_dir, "logs", "rules_choices.log")
281:         with open(rules_choices_path, "a", encoding="utf-8") as f:
282:             f.write(summary)
283:
284:         reason_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
285:         with open(reason_path, "a", encoding="utf-8") as f:
286:             f.write(summary)
287:
288:     def _ensure_pos_services(self):
289:         """Lazy load POS tagger and dictionary (only once)."""
290:         if self.use_pos_tagging and self.pos_tagger is None:
291:             try:
292:                 self.pos_tagger = get_pos_tagger()
293:                 # Always get fresh reference to pos_dictionary from global singleton
294:                 # This ensures we get updates when reset_pos_dictionary() is called
295:                 self.pos_dictionary = get_pos_dictionary()
296:                 log_message("POS tagging services initialized (using spaCy)")
297:             except Exception as e:
298:                 log_message(f"Failed to initialize POS services: {e}", level="WARNING")
299:                 self.use_pos_tagging = False
300:
301:     def _ensure_nli_services(self):
302:         """Lazy load RoBERTa-MNLI NLI model (only when hybrid deciders need it)."""
303:         if self.nli is None:
304:             try:
305:                 from transformers import pipeline as hf_pipeline
306:                 import torch
307:
308:                 device = 0 if torch.cuda.is_available() else -1
309:                 self.nli = hf_pipeline(
310:                     "zero-shot-classification",
311:                     model="roberta-large-mnli",
312:                     device=device,
313:                 )
314:                 log_message("RoBERTa-MNLI NLI model initialized for hybrid deciders")
315:             except Exception as e:
316:                 log_message(f"Failed to initialize NLI model: {e}", level="WARNING")
317:                 self.nli = None
318:
319:     def _refresh_pos_dictionary(self):
320:         """Refresh the pos_dictionary reference to get latest instance from global singleton.
321:
322:         This ensures we get updates when reset_pos_dictionary() is called.
323:         """
324:         self.pos_dictionary = get_pos_dictionary()
325:
326:     def _load_config(self) -> Dict[str, Any]:
327:         """Load configuration from config.json."""
328:         import json
329:         from pathlib import Path
330:
331:         config_path = Path(__file__).parent.parent / "config" / "config.json"
332:         if config_path.exists():
333:             with open(config_path, "r") as f:
334:                 return json.load(f)
335:         return {}
336:
337:     def _check_replace_rules(
338:         self, word: str, context_before: str, context_after: str, ctx: "BookfixContext"
339:     ) -> Optional[Tuple[str, str]]:
340:         """
341:         Check if word is part of a phrase in REPLACE rules.
342:
343:         Args:
344:             word: The target word (e.g., "close")
345:             context_before: Text before the word
346:             context_after: Text after the word
347:             ctx: Context with replacements dict
348:
349:         Returns:
350:             Tuple of (pronunciation, explanation) or None if no match
351:         """
352:         log_message(
353:             f"DEBUG: Entering _check_replace_rules for word: '{word}'", level="DEBUG"
354:         )
355:         log_message(
356:             f"DEBUG: _check_replace_rules context_before: '{context_before}', context_after: '{context_after}'",
357:             level="DEBUG",
358:         )
359:
360:         if not hasattr(ctx, "replacements") or not ctx.replacements:
361:             log_message(
362:                 f"DEBUG: _check_replace_rules: No replacements dict available",
363:                 level="DEBUG",
364:             )
365:             log_message(
366:                 f"DEBUG: Exiting _check_replace_rules (no replacements)", level="DEBUG"
367:             )
368:             return None
369:
370:         log_message(
371:             f"DEBUG: _check_replace_rules: Checking word '{word}' with {len(ctx.replacements)} rules",
372:             level="DEBUG",
373:         )
374:
375:         # Get words before and after
376:         words_before = context_before.strip().split()
377:         words_after = context_after.strip().split()
378:         log_message(
379:             f"DEBUG: _check_replace_rules: words_before: {words_before}, words_after: {words_after}",
380:             level="DEBUG",
381:         )
382:
383:         # Build potential phrases (check longer phrases first for better matches):
384:         # 1. word + 2 next words (e.g., "close enough to")
385:         # 2. previous word + word + next word (e.g., "so close to")
386:         # 3. word + next word (e.g., "close to")
387:         # 4. previous word + word (e.g., "so close")
388:
389:         phrases_to_check = []
390:
391:         # word + 2 next words (longest first)
392:         if len(words_after) >= 2:
393:             phrase = f"{word} {words_after[0]} {words_after[1]}"
394:             phrases_to_check.append(phrase)
395:             log_message(
396:                 f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
397:             )
398:
399:         # 1 before + word + 1 after
400:         if words_before and words_after:
401:             phrase = f"{words_before[-1]} {word} {words_after[0]}"
402:             phrases_to_check.append(phrase)
403:             log_message(
404:                 f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
405:             )
406:
407:         # word + 1 next word
408:         if words_after:
409:             phrase = f"{word} {words_after[0]}"
410:             phrases_to_check.append(phrase)
411:             log_message(
412:                 f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
413:             )
414:
415:         # 1 before + word
416:         if words_before:
417:             phrase = f"{words_before[-1]} {word}"
418:             phrases_to_check.append(phrase)
419:             log_message(
420:                 f"DEBUG: _check_replace_rules: Adding phrase: '{phrase}'", level="DEBUG"
421:             )
422:
423:         # Check each phrase against REPLACE rules (ctx.replacements is a dict)
424:         # Need case-insensitive matching since keys might be any case
425:         log_message(
426:             f"DEBUG: _check_replace_rules: Checking phrases: {phrases_to_check}",
427:             level="DEBUG",
428:         )
429:
430:         for phrase in phrases_to_check:
431:             phrase_lower = phrase.lower()
432:
433:             # Check if this phrase exists as a key (case-insensitive)
434:             for original_key, replacement in ctx.replacements.items():
435:                 if original_key.lower() == phrase_lower:
436:                     # Found a match!
437:                     log_message(
438:                         f"DEBUG: _check_replace_rules: REPLACE MATCH FOUND! '{phrase}' matches rule '{original_key}' → '{replacement}'",
439:                         level="DEBUG",
440:                     )
441:                     replacement_words = replacement.split()
442:
443:                     # Find which word in replacement corresponds to our target word
444:                     original_words = phrase.split()
445:                     try:
446:                         # Ensure original_words is not empty before trying to find index
447:                         if not original_words:
448:                             log_message(
449:                                 f"DEBUG: _check_replace_rules: original_words is empty, skipping index lookup.",
450:                                 level="DEBUG",
451:                             )
452:                             continue
453:
454:                         word_index = [w.lower() for w in original_words].index(
455:                             word.lower()
456:                         )
457:                         log_message(
458:                             f"DEBUG: _check_replace_rules: word_index for '{word.lower()}' in original_words: {word_index}",
459:                             level="DEBUG",
460:                         )
461:
462:                         # --- CRITICAL LINE FOR ERROR ---
463:                         log_message(
464:                             f"DEBUG: _check_replace_rules: About to access replacement_words[{word_index}]",
465:                             level="DEBUG",
466:                         )
467:
468:                         # Ensure replacement_words is not empty and word_index is valid
469:                         if not replacement_words:
470:                             log_message(
471:                                 f"DEBUG: _check_replace_rules: replacement_words is empty, cannot access index {word_index}.",
472:                                 level="DEBUG",
473:                             )
474:                             continue
475:
476:                         # FIX: Handle cases where replacement has fewer words than original phrase
477:                         # Use the last word of replacement if word_index is out of bounds
478:                         if word_index >= len(replacement_words):
479:                             log_message(
480:                                 f"DEBUG: _check_replace_rules: Word index {word_index} is >= len(replacement_words) ({len(replacement_words)}). Using last word of replacement.",
481:                                 level="DEBUG",
482:                             )
483:                             pronunciation = replacement_words[-1]
484:                         else:
485:                             pronunciation = replacement_words[word_index]
486:                         # --- END CRITICAL LINE ---
487:
488:                         explanation = f"REPLACE rule: '{original_key}' → '{replacement}' (user-defined)"
489:                         log_message(
490:                             f"DEBUG: _check_replace_rules: Extracted pronunciation: '{pronunciation}' from position {word_index}",
491:                             level="DEBUG",
492:                         )
493:                         log_message(
494:                             f"DEBUG: Exiting _check_replace_rules (match found)",
495:                             level="DEBUG",
496:                         )
497:                         return (pronunciation, explanation)
498:                     except (ValueError, IndexError) as e:
499:                         log_message(
500:                             f"DEBUG: _check_replace_rules: Failed to extract pronunciation from match or word not found in original_words. Error: {e}",
501:                             level="DEBUG",
502:                         )
503:                         continue
504:
505:         log_message(
506:             f"DEBUG: _check_replace_rules: No REPLACE rule matches found", level="DEBUG"
507:         )
508:         log_message(f"DEBUG: Exiting _check_replace_rules (no match)", level="DEBUG")
509:         return None
510:
511:     def _get_pos_based_choice(
512:         self, word: str, context_before: str, context_after: str
513:     ) -> Optional[Tuple[str, float, str]]:
514:         """
515:         Get pronunciation choice based on POS tagging.
516:
517:         Args:
518:             word: The word to analyze
519:             context_before: Text before the word
520:             context_after: Text after the word
521:
522:         Returns:
523:             Tuple of (pronunciation, confidence, explanation) or None if no POS match
524:         """
525:         if not self.use_pos_tagging:
526:             return None
527:
528:         self._ensure_pos_services()
529:
530:         if self.pos_tagger is None or self.pos_dictionary is None:
531:             return None
532:
533:         # Check if word is in POS dictionary
534:         if not self.pos_dictionary.has_word(word):
535:             return None
536:
537:         try:
538:             # Get POS tag for word in context
539:             pos_tag = self.pos_tagger.tag_with_context(
540:                 context_before, word, context_after
541:             )
542:
543:             if not pos_tag:
544:                 return None
545:
546:             # Look up pronunciation based on POS tag
547:             pronunciation = self.pos_dictionary.get_pronunciation_by_pos(word, pos_tag)
548:
549:             if pronunciation:
550:                 explanation = self.pos_dictionary.explain_choice(word, pos_tag)
551:                 # Lower confidence for POS since it can be wrong (~5% error rate)
552:                 # This allows semantic/keyword rules to override when they have strong matches
553:                 base_confidence = 0.80
554:                 return (pronunciation, base_confidence, explanation)
555:
556:         except Exception as e:
557:             log_message(f"POS analysis error for '{word}': {e}", level="WARNING")
558:
559:         return None
560:
561:     def process_choices_ai_review_mode(
562:         self, ctx: "BookfixContext", force_all: bool = True
563:     ) -> Optional[AIChangeTracker]:
564:         """
565:         Process choices with AI, creating Change objects for later review.
566:         This version uses batching for AI calls to improve efficiency.
567:         """
568:         log_message("DEBUG: Entering process_choices_ai_review_mode", level="DEBUG")
569:
570:         # Clear logs at start of processing
571:         import os
572:
573:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
574:         log_files_to_clear = [
575:             "rule_reasoning.log",
576:             "rules_choices.log",
577:             "review_changes.log",
578:         ]
579:         for log_file in log_files_to_clear:
580:             log_path = os.path.join(log_dir, "logs", log_file)
581:             if os.path.exists(log_path):
582:                 os.remove(log_path)
583:
584:         if not self.change_tracker:
585:             log_message("Change tracker not set, cannot use review mode")
586:             log_message(
587:                 "DEBUG: Exiting process_choices_ai_review_mode (change tracker not set)",
588:                 level="DEBUG",
589:             )
590:             return None
591:
592:         if not self.ai_enabled and not self.use_pos_tagging:
593:             log_message("Neither AI nor POS tagging available, cannot use review mode")
594:             log_message(
595:                 "DEBUG: Exiting process_choices_ai_review_mode (AI/POS not available)",
596:                 level="DEBUG",
597:             )
598:             return None
599:
600:         if self.use_pos_tagging:
601:             self._ensure_pos_services()
602:             # Reload POS dictionary from disk to pick up manual edits
603:             from ..ai.pos_dictionary import reset_pos_dictionary
604:
605:             reset_pos_dictionary()
606:             self._refresh_pos_dictionary()
607:
608:         self._setup_choices_log(ctx.current_file_path)
609:         self._clear_all_logs(ctx)
610:         self._log_to_choices_log("=== AI CHOICES BATCH PROCESSING STARTED ===")
611:         log_message(
612:             f"DEBUG: Before len(ctx.choices) - type(ctx.choices): {type(ctx.choices)}, ctx.choices is None: {ctx.choices is None}",
613:             level="DEBUG",
614:         )
615:         log_message(
616:             f"Starting AI-first review mode with {len(ctx.choices)} choice rules (Batch Mode)"
617:         )
618:         log_message(
619:             f"DEBUG: Before set_text - type(ctx.text): {type(ctx.text)}, len(ctx.text): {len(ctx.text) if ctx.text is not None else 'None'}, change_tracker is None: {self.change_tracker is None}",
620:             level="DEBUG",
621:         )
622:         try:
623:             self.change_tracker.set_text(original=ctx.text, current=ctx.text)
624:         except IndexError as e:
625:             log_message(
626:                 f"FATAL ERROR: IndexError during set_text for file {ctx.current_file_path}: {e}",
627:                 level="ERROR",
628:             )
629:             log_message(
630:                 f"DEBUG: ctx.text type: {type(ctx.text)}, ctx.text length: {len(ctx.text) if ctx.text is not None else 'None'}",
631:                 level="ERROR",
632:             )
633:             log_message(
634:                 f"DEBUG: ctx.text (first 100 chars): {ctx.text[:100] if ctx.text else 'N/A'}",
635:                 level="ERROR",
636:             )
637:             log_message(
638:                 "DEBUG: Exiting process_choices_ai_review_mode (IndexError during set_text)",
639:                 level="DEBUG",
640:             )
641:             return None
642:
643:         items_for_ai_batch = []
644:         item_id_counter = 0
645:         match_map = {}
646:
647:         words_to_process = set(ctx.choices.keys())
648:         log_message(
649:             f"DEBUG: Total words to process: {len(words_to_process)}", level="DEBUG"
650:         )
651:         for word in words_to_process:
652:             log_message(f"DEBUG: Processing word: '{word}'", level="DEBUG")
653:             matches = self._find_matches(word, self.change_tracker.original_text)
654:             log_message(
655:                 f"DEBUG: Found {len(matches)} matches for '{word}'", level="DEBUG"
656:             )
657:             if not matches:
658:                 continue
659:
660:             log_message(f"DEBUG: Getting options for word: '{word}'", level="DEBUG")
661:             contextualized_options = ctx.contextualized_choices.get(word)
662:             regular_options = ctx.choices.get(word, [])
663:             options = regular_options or [
664:                 opt for opt, _ in (contextualized_options or [])
665:             ]
666:             if not options:
667:                 continue
668:
669:             for match_idx, match in enumerate(matches, 1):
670:                 detected_pos_tag = ""
671:                 log_message(
672:                     f"DEBUG: ─── '{word}' occurrence {match_idx}/{len(matches)} @ position {match.start()} ───",
673:                     level="DEBUG",
674:                 )
675:                 # Check if this match should be skipped based on context
676:                 if hasattr(ctx, "skip_choice") and ctx.skip_choice:
677:                     is_skipped = False
678:                     # Create a small window of text around the match, normalized for whitespace and case
679:                     window_start = max(0, match.start() - 30)
680:                     window_end = min(
681:                         len(self.change_tracker.original_text), match.end() + 30
682:                     )
683:                     text_window = self.change_tracker.original_text[
684:                         window_start:window_end
685:                     ]
686:                     normalized_window = " ".join(text_window.lower().split())
687:
688:                     for skip_phrase in ctx.skip_choice:
689:                         # Normalize the skip phrase as well
690:                         normalized_skip_phrase = " ".join(skip_phrase.lower().split())
691:                         if normalized_skip_phrase in normalized_window:
692:                             log_message(
693:                                 f"Skipping choice for '{word}' at position {match.start()} due to skip phrase match: '{skip_phrase}'"
694:                             )
695:                             is_skipped = True
696:                             break
697:
698:                     if is_skipped:
699:                         continue
700:
701:                 # --- Full Rule-Checking Logic ---
702:                 context_full = self._extract_context(
703:                     self.change_tracker.original_text,
704:                     match.start(),
705:                     match.end(),
706:                     self.context_size,
707:                     single_sentence=self.single_sentence_context,
708:                 )
709:
710:                 # --- Check for REPLACE rules first (highest priority) ---
711:                 # Split context to extract before/after, checking that split succeeds
712:                 context_parts = context_full.split(f"[{word}]")
713:                 if len(context_parts) == 2:
714:                     replace_rule_decision = self._check_replace_rules(
715:                         word, context_parts[0], context_parts[1], ctx
716:                     )
717:                     if replace_rule_decision:
718:                         pronunciation, explanation = replace_rule_decision
719:                         self.decision_stats["replace_rule"] += 1
720:
721:                         # Log REPLACE rule decision
722:                         short_ctx = self._extract_short_context(
723:                             self.change_tracker.original_text,
724:                             match.start(),
725:                             match.end(),
726:                             num_words=10,
727:                             replacement=pronunciation,
728:                         )
729:                         self._log_to_choices_log(
730:                             f"✓ DECISION: '{word}' → '{pronunciation}' | Rule: REPLACE (highest priority)"
731:                         )
732:                         self._log_to_choices_log(f"  Context: {short_ctx}")
733:                         self._log_to_choices_log(f"  Reason: {explanation}")
734:                         self._log_to_choices_log("")  # Blank line
735:
736:                         self._log_change(
737:                             match,
738:                             word,
739:                             options,
740:                             {
741:                                 "choice": pronunciation,
742:                                 "confidence": 1.0,
743:                                 "reason": explanation,
744:                             },
745:                             "replace_rule",
746:                             contextualized_options,
747:                             detected_pos_tag,
748:                         )
749:                         # Log comprehensive entry for REPLACE rule
750:                         replace_decision = {
751:                             "choice": pronunciation,
752:                             "confidence": 1.0,
753:                             "reason": explanation,
754:                         }
755:                         self._log_comprehensive_rule_entry(
756:                             word,
757:                             match,
758:                             {"replace_rule": replace_decision},
759:                             detected_pos_tag,
760:                             replace_decision,
761:                             "replace_rule",
762:                             options,
763:                         )
764:                         continue  # Skip all other rules and AI for this match
765:                 else:
766:                     log_message(
767:                         f"WARNING: context_full split failed for word '{word}'. Split returned {len(context_parts)} parts instead of 2.",
768:                         level="WARNING",
769:                     )
770:
771:                 # Store the single sentence for _log_rule_choice display
772:                 try:
773:                     _before, _w, _after = self._extract_sentence_context(
774:                         self.change_tracker.original_text, match.start(), match.end()
775:                     )
776:                     self._current_sentence = (_before + _w + _after).strip()
777:                 except Exception:
778:                     self._current_sentence = ""
779:
780:                 # Run all local rules
781:                 all_rules, detected_pos_tag = self._run_all_rules(
782:                     word, context_full, ctx
783:                 )
784:
785:                 # Initialize ai_decision and decision_source before conditional assignment
786:                 ai_decision = None
787:                 decision_source = None
788:
789:                 # Check for consensus
790:                 # Now returns 3-tuple to support disagreement gate: (decision, source, best_guess)
791:                 ai_decision, decision_source, best_guess = self._get_consensus_from_rules(
792:                     all_rules, context_full, word, options
793:                 )
794:
795:                 if ai_decision:
796:                     if self.ai_verify_all and self.ai_service:
797:                         # AI VERIFY ALL MODE: Rules produced a decision, but AI
798:                         # must verify EVERY decision per config. Queue the item
799:                         # for AI batch; store the rule decision as a safe fallback
800:                         # so we don't lose work if the AI call fails.
801:                         self._log_to_choices_log(
802:                             f"Queuing '{word}' for AI verification (Verify ALL mode)."
803:                         )
804:                         if all_rules:
805:                             _rules_summary = ", ".join(
806:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
807:                                 for r, v in all_rules.items()
808:                             )
809:                             _ai_reason = f"rule consensus ({decision_source}); verify all — rules fired: {_rules_summary}"
810:                         else:
811:                             _ai_reason = (
812:                                 f"rule consensus ({decision_source}); verify all"
813:                             )
814:                         self._log_rule_choice(
815:                             word, "→ AI verify", 0.0, f"queued [{_ai_reason}]"
816:                         )
817:                         item_id_counter += 1
818:                         log_message(
819:                             f"DEBUG: Queued (verify_all) item_id_counter: {item_id_counter}",
820:                             level="DEBUG",
821:                         )
822:
823:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
824:                         rich_options = [
825:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
826:                             for s in options
827:                         ]
828:                         batch_item = {
829:                             "id": item_id_counter,
830:                             "word": word,
831:                             "context": context_full,
832:                             "options": rich_options,
833:                         }
834:                         items_for_ai_batch.append(batch_item)
835:                         # IMPORTANT: store the *original rule decision and source*
836:                         # so that if AI batch fails, we can fall back cleanly
837:                         # without changing the reported source.
838:                         match_map[item_id_counter] = (
839:                             match,
840:                             word,
841:                             options,
842:                             contextualized_options,
843:                             detected_pos_tag,
844:                             ai_decision,  # rule decision fallback dict
845:                             decision_source,  # e.g. "complex_pos", "hybrid", etc.
846:                         )
847:                     else:
848:                         # Rule-based decision was made, log it directly
849:                         self.decision_stats[decision_source] += 1
850:
851:                         # Log the decision to the batch log with short context
852:                         short_ctx = self._extract_short_context(
853:                             self.change_tracker.original_text,
854:                             match.start(),
855:                             match.end(),
856:                             num_words=10,
857:                             replacement=ai_decision["choice"],
858:                         )
859:                         self._log_to_choices_log(
860:                             f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | Rule: {decision_source}"
861:                         )
862:                         self._log_to_choices_log(f"  Context: {short_ctx}")
863:                         self._log_to_choices_log(f"  Reason: {ai_decision['reason']}")
864:
865:                         # Log all rules that fired for transparency
866:                         if len(all_rules) > 1:
867:                             self._log_to_choices_log(f"  Other rules that fired:")
868:                             for rule_name, rule_data in all_rules.items():
869:                                 if rule_name != decision_source:
870:                                     self._log_to_choices_log(
871:                                         f"    - {rule_name}: '{rule_data['choice']}' | {rule_data['reason']}"
872:                                     )
873:                         self._log_to_choices_log("")  # Blank line for readability
874:
875:                         self._log_change(
876:                             match,
877:                             word,
878:                             options,
879:                             ai_decision,
880:                             decision_source,
881:                             contextualized_options,
882:                             detected_pos_tag,
883:                         )
884:                         # Log comprehensive entry for this word
885:                         self._log_comprehensive_rule_entry(
886:                             word,
887:                             match,
888:                             all_rules,
889:                             detected_pos_tag,
890:                             ai_decision,
891:                             decision_source,
892:                             options,
893:                         )
894:                 elif self.ai_enabled and self.ai_service:
895:                     # Disagreement gate (hybrid vs pos) uses the rich per-item prompt
896:                     # (definitions from choices.json + best_guess + GRAMMAR/KEYWORD CLUES)
897:                     # via _analyze_with_contextualized_ai + show_reasoning=True.
898:                     # All other "no consensus" cases still use efficient batch processing.
899:                     if decision_source == "disagreement" and best_guess is not None:
900:                         # --- DISAGREEMENT PATH: direct contextualized AI (rich prompt) ---
901:                         # This routes the exact ambiguous homograph cases to the verbose
902:                         # per-item analyzer so the model sees full dictionary meanings for
903:                         # the target word plus detected POS and context_keywords.
904:                         self._log_to_choices_log(
905:                             f"Disagreement (hybrid vs pos) for '{word}' — routing to contextualized AI (rich prompt + best_guess)."
906:                         )
907:                         self._log_rule_choice(word, "→ AI (contextualized)", 0.0, "disagreement→contextualized")
908:                         # best_guess is the hybrid dict from _get_consensus; extract the spelling string
909:                         bg = best_guess.get("choice") if isinstance(best_guess, dict) else best_guess
910:                         # Ensure list of (spelling, meaning) tuples for the call
911:                         ctx_opts = contextualized_options
912:                         if not ctx_opts:
913:                             meaning_map = {s: m for s, m in (contextualized_options or [])}
914:                             ctx_opts = [(s, meaning_map.get(s, s)) for s in options]
915:                         ai_decision = self._analyze_with_contextualized_ai(
916:                             word,
917:                             context_full,
918:                             ctx_opts,
919:                             show_reasoning=True,
920:                             best_guess=bg,
921:                             detected_pos_tag=detected_pos_tag,
922:                             context_keywords=None,  # auto-fetched inside from pos_dictionary
923:                         )
924:                         if ai_decision:
925:                             decision_source = "llm"
926:                             self.decision_stats[decision_source] += 1
927:                             short_ctx = self._extract_short_context(
928:                                 self.change_tracker.original_text,
929:                                 match.start(),
930:                                 match.end(),
931:                                 num_words=10,
932:                                 replacement=ai_decision["choice"],
933:                             )
934:                             self._log_to_choices_log(
935:                                 f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | AI: {decision_source} (contextualized)"
936:                             )
937:                             self._log_to_choices_log(f"  Context: {short_ctx}")
938:                             self._log_to_choices_log(f"  Reason: {ai_decision.get('reason', 'AI contextualized')}")
939:                             self._log_change(
940:                                 match,
941:                                 word,
942:                                 options,
943:                                 ai_decision,
944:                                 decision_source,
945:                                 contextualized_options,
946:                                 detected_pos_tag,
947:                             )
948:                             self._log_comprehensive_rule_entry(
949:                                 word,
950:                                 match,
951:                                 all_rules,
952:                                 detected_pos_tag,
953:                                 ai_decision,
954:                                 decision_source,
955:                                 options,
956:                             )
957:                         else:
958:                             # Contextualized AI failed — fall back to hybrid best_guess
959:                             # (this preserves the tuned hybrid decision for review)
960:                             fallback_choice = bg if bg else options[0]
961:                             ai_decision = {
962:                                 "choice": fallback_choice,
963:                                 "confidence": best_guess.get("confidence", 0.95) if isinstance(best_guess, dict) else 0.95,
964:                                 "reason": "hybrid best_guess fallback (contextualized AI failed)",
965:                             }
966:                             decision_source = "hybrid"
967:                             self.decision_stats[decision_source] += 1
968:                             self._log_rule_choice(
969:                                 word, ai_decision["choice"], ai_decision["confidence"], "disagreement→hybrid_fallback"
970:                             )
971:                             self._log_change(
972:                                 match,
973:                                 word,
974:                                 options,
975:                                 ai_decision,
976:                                 decision_source,
977:                                 contextualized_options,
978:                                 detected_pos_tag,
979:                             )
980:                             self._log_comprehensive_rule_entry(
981:                                 word,
982:                                 match,
983:                                 all_rules,
984:                                 detected_pos_tag,
985:                                 ai_decision,
986:                                 decision_source,
987:                                 options,
988:                             )
989:                     else:
990:                         # No rule consensus for non-disagreement cases → queue for AI batch
991:                         # (batch prompt uses REFERENCE EXAMPLES from choices.json for the word family)
992:                         self._log_to_choices_log(f"Queuing '{word}' for AI batch analysis.")
993:                         if all_rules:
994:                             _rules_summary = ", ".join(
995:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
996:                                 for r, v in all_rules.items()
997:                             )
998:                             _ai_reason = f"no consensus — rules fired: {_rules_summary}"
999:                         else:
1000:                             _ai_reason = (
1001:                                 f"no rules fired (POS: {detected_pos_tag or 'unknown'})"
1002:                             )
1003:                         self._log_rule_choice(word, "→ AI", 0.0, f"queued [{_ai_reason}]")
1004:                         item_id_counter += 1
1005:                         log_message(
1006:                             f"DEBUG: Queued item_id_counter: {item_id_counter}",
1007:                             level="DEBUG",
1008:                         )
1009:
1010:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
1011:                         rich_options = [
1012:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
1013:                             for s in options
1014:                         ]
1015:                         batch_item = {
1016:                             "id": item_id_counter,
1017:                             "word": word,
1018:                             "context": context_full,
1019:                             "options": rich_options,
1020:                         }
1021:                         items_for_ai_batch.append(batch_item)
1022:                         # Use best_guess (from disagreement) if present, else None
1023:                         fallback_decision = best_guess if best_guess is not None else None
1024:                         fallback_source = decision_source if decision_source else None
1025:                         match_map[item_id_counter] = (
1026:                             match,
1027:                             word,
1028:                             options,
1029:                             contextualized_options,
1030:                             detected_pos_tag,
1031:                             fallback_decision,  # rule fallback (hybrid on disagreement, else None)
1032:                             fallback_source,
1033:                         )
1034:                 else:
1035:                     # RULES-ONLY MODE: Force decision with zero confidence
1036:                     default_decision = None
1037:                     if self.rules_only_mode:
1038:                         # Use first option, force zero confidence
1039:                         forced_choice = options[0] if options else "UNKNOWN"
1040:                         forced_decision = {
1041:                             "choice": forced_choice,
1042:                             "confidence": 0.0,
1043:                             "reason": "Rules-only forced: using first option",
1044:                         }
1045:                         self.decision_stats["rules_only_forced"] += 1
1046:                         self._log_rule_choice(
1047:                             word, forced_choice, 0.0, "rules_only_main_loop"
1048:                         )
1049:                         self._log_change(
1050:                             match,
1051:                             word,
1052:                             options,
1053:                             forced_decision,
1054:                             "rules_only",
1055:                             contextualized_options,
1056:                             detected_pos_tag,
1057:                         )
1058:                         # Log comprehensive entry for this word
1059:                         self._log_comprehensive_rule_entry(
1060:                             word,
1061:                             match,
1062:                             all_rules,
1063:                             detected_pos_tag,
1064:                             forced_decision,
1065:                             "rules_only",
1066:                             options,
1067:                         )
1068:                     else:
1069:                         # No strong rules and no AI. Treat this as a low-confidence
1070:                         # default that explicitly requires human review in the
1071:                         # review window.
1072:                         self.decision_stats["review_needed"] += 1
1073:                         self._log_rule_choice(word, options[0], 0.5, "review_needed")
1074:                         default_decision = {
1075:                             "choice": options[0],
1076:                             "confidence": 0.5,
1077:                             "reason": "Review needed (no strong rules matched, AI disabled)",
1078:                         }
1079:
1080:                         # Log default decision
1081:                     short_ctx = self._extract_short_context(
1082:                         self.change_tracker.original_text,
1083:                         match.start(),
1084:                         match.end(),
1085:                         num_words=10,
1086:                         replacement=options[0],
1087:                     )
1088:                     self._log_to_choices_log(
1089:                         f"⚠️  DEFAULT: '{word}' → '{options[0]}' | No strong rules matched, using first option (Review Needed)"
1090:                     )
1091:                     self._log_to_choices_log(f"  Context: {short_ctx}")
1092:                     self._log_to_choices_log(
1093:                         f"  Available options: {', '.join(options)}"
1094:                     )
1095:                     self._log_to_choices_log("")  # Blank line
1096:
1097:                     # Use a special decision_source so the GUI can show
1098:                     # "Review Needed" instead of treating this as a strong rule.
1099:                     self._log_change(
1100:                         match,
1101:                         word,
1102:                         options,
1103:                         default_decision,
1104:                         "review_needed",
1105:                         contextualized_options,
1106:                         detected_pos_tag,
1107:                     )
1108:                     # Log comprehensive entry for this word
1109:                     self._log_comprehensive_rule_entry(
1110:                         word,
1111:                         match,
1112:                         all_rules,
1113:                         detected_pos_tag,
1114:                         default_decision,
1115:                         "review_needed",
1116:                         options,
1117:                     )
1118:
1119:         # Now, process the batch of items that need AI analysis
1120:         if items_for_ai_batch:
1121:             BATCH_SIZE = 10  # Process in chunks to avoid payload size limits
1122:             all_batch_results = {}
1123:             quota_exhausted = False
1124:
1125:             log_message(
1126:                 f"Processing {len(items_for_ai_batch)} items in chunks of {BATCH_SIZE}."
1127:             )
1128:
1129:             for i in range(0, len(items_for_ai_batch), BATCH_SIZE):
1130:                 chunk = items_for_ai_batch[i : i + BATCH_SIZE]
1131:
1132:                 if quota_exhausted:
1133:                     from ..ai.service import AIResponse
1134:
1135:                     for item in chunk:
1136:                         all_batch_results[item["id"]] = AIResponse(
1137:                             False,
1138:                             "",
1139:                             0.0,

(Output capped at 50 KB. Showing lines 1-1139. Use offset=1140 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py"
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
1: """
2: Hybrid homograph disambiguation engine.
3:
4: Uses spaCy transformer (en_core_web_trf) for POS/dependency, RoBERTa-large-MNLI NLI for
5: hard cases. 22 hand-tuned per-word deciders for accuracy on common homographs.
6:
7: Deciders return (pronunciation_spelling, route_explanation).
8: """
9:
10: import re
11: from typing import Optional, Tuple
12:
13: # POS tag categories for rules
14: VERB_PRESENT = {"VB", "VBP", "VBZ", "VBG", "VBN"}
15: VERB_PAST = {"VBD"}
16: ADJ_TAGS = {"JJ", "JJR", "JJS"}
17: ADV_TAGS = {"RB", "RBR", "RBS"}
18:
19:
20: def nli_decide(nli, sentence: str, word: str, q_a: str, label_a: str, q_b: str, label_b: str) -> Tuple[str, str]:
21:     """Run RoBERTa NLI to pick between two hypotheses.
22:
23:     Returns (pronunciation, route_string).
24:     """
25:     if not nli:
26:         return label_a, f"nli-disabled"
27:     try:
28:         result = nli(sentence, candidate_labels=[q_a, q_b], multi_label=False)
29:         scores = dict(zip(result["labels"], result["scores"]))
30:         if scores[q_a] > scores[q_b]:
31:             return label_a, f"nli={label_a}({scores[q_a]:.2f})"
32:         else:
33:             return label_b, f"nli={label_b}({scores[q_b]:.2f})"
34:     except Exception:
35:         return label_a, f"nli-error"
36:
37:
38: # ── 22 Word-Specific Deciders ────────────────────────────────────────────────────────
39:
40: def decide_record(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
41:     """record: verb → rekord; noun → rekkurd."""
42:     if tag in VERB_PRESENT or tag in VERB_PAST:
43:         return "rekord", "pos-verb"
44:     return "rekkurd", "pos-noun"
45:
46:
47: def decide_records(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
48:     """
49:     records (plural): verb → rekords; noun → rekkurds.
50:
51:     Includes special case for NNS mis-tags on verbs in clausal positions
52:     (e.g. spaCy tagging verb "records" as NNS in "history records").
53:     """
54:     # Strong context bias for known verb uses like "history records" even on NNS mistag.
55:     sent_lower = sentence.lower()
56:     if "history records" in sent_lower or re.search(r'\bit records\b', sent_lower):
57:         return "rekords", "pos-verb-context"
58:
59:     # Verb for plural: if verb tag, or NNS but in core verbal dep position (mis-tag case).
60:     if tag in VERB_PRESENT or tag in VERB_PAST or (tag == "NNS" and dep in ("ROOT", "xcomp", "ccomp", "advcl", "relcl", "nsubj", "dobj")):
61:         return "rekords", "pos-verb"
62:     return "rekkurds", "pos-noun"
63:
64:
65: def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
66:     """close: verb → cloze; adj/adv → close; noun → close."""
67:     if tag in VERB_PRESENT or tag in VERB_PAST:
68:         return "cloze", "pos-verb"
69:     if tag in ADJ_TAGS or tag in ADV_TAGS:
70:         return "close", "pos-adj/adv"
71:     return "close", "pos-default"
72:
73:
74: def decide_read(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
75:     """read: past/VBN → red; present → reed; default → red."""
76:     if tag in VERB_PAST or tag == "VBN":
77:         return "red", "pos-past"
78:     if tag in VERB_PRESENT:
79:         return "reed", "pos-verb"
80:     return "red", "pos-default"
81:
82:
83: def decide_live(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
84:     """
85:     live: verb → liv; adj/adv → lyve; noun → liv.
86:
87:     Uses dependency and simple phrase patterns to be robust to spaCy mis-tags
88:     (e.g. JJ for verb 'live' in "to live" or "live longer").
89:     Prioritizes verb-like dependency frames over fine POS tags for 'liv'.
90:     """
91:     # Normalize for bracketed target word in sentence (e.g. "go [live]").
92:     norm = re.sub(r'[\[\]]', '', sentence.lower())
93:
94:     # Verb cases in clausal positions: prefer 'liv' even if mis-tagged as JJ/RB.
95:     # Covers "to live in...", "live longer", "that live here", fronted infinitives, etc.
96:     # Uses expanded dep list matching complex_pos rules + common clausal roles.
97:     verb_clause_deps = {"ROOT", "xcomp", "ccomp", "advcl", "relcl", "acl"}
98:     if (tag in VERB_PRESENT or tag in VERB_PAST) or dep in verb_clause_deps:
99:         if not (head == "go" and "go live" in norm):
100:             return "liv", "pos-verb-clause"
101:
102:     # 'go live' idiom for launch/broadcast: 'lyve'.
103:     # Matches "go live.", "go live now", etc (robust to brackets). Explicitly exclude "go live in ..." (place) per user.
104:     if head == "go" and re.search(r'\bgo\s*live\b', norm, re.IGNORECASE) and not re.search(r'\bgo\s*live\s+in\b', norm, re.IGNORECASE):
105:         return "lyve", "pos-go-live-idiom"
106:
107:     # Adjective 'alive' or adverb 'live': 'lyve' (e.g. "a live person", "live specimens", "reported live").
108:     # Rely on dep_relation for adj/adv slots primarily (amod/advmod/compound).
109:     # Trust ADJ/ADV tag for lyve only when dep is consistent with predicative adjective (acomp/attr).
110:     # This avoids JJ mis-tags on verbs (with non-adjective deps) from stealing 'lyve'.
111:     if dep in ("amod", "compound", "advmod") or ((tag in ADJ_TAGS or tag in ADV_TAGS) and dep in ("acomp", "attr")):
112:         return "lyve", "pos-adj"
113:
114:     # Phrase-level bias for common "live person/people/body" as adjective (alive).
115:     if re.search(r'\blive (person|people|body|specimen)', norm, re.IGNORECASE):
116:         return "lyve", "pos-live-adj-phrase"
117:
118:     # Default to verb 'liv' for other noun-like defaults or mis-tags.
119:     return "liv", "pos-default"
120:
121:
122: def decide_object(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
123:     """object: verb → ubjekt; noun → objekt."""
124:     if tag in VERB_PRESENT or tag in VERB_PAST:
125:         return "ubjekt", "pos-verb"
126:     return "objekt", "pos-noun"
127:
128:
129: def decide_present(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
130:     """present: verb → prezent; noun/adj → present."""
131:     if tag in VERB_PRESENT or tag in VERB_PAST:
132:         return "prezent", "pos-verb"
133:     return "present", "pos-noun/adj"
134:
135:
136: def decide_sow(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
137:     """sow: verb → soh; noun → sow."""
138:     if tag in VERB_PRESENT or tag in VERB_PAST:
139:         return "soh", "pos-verb"
140:     return "sow", "pos-noun"
141:
142:
143: def decide_resume(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
144:     """resume: verb → rezoom; noun → resume."""
145:     if tag in VERB_PRESENT or tag in VERB_PAST:
146:         return "rezoom", "pos-verb"
147:     return "resume", "pos-noun"
148:
149:
150: def decide_refuse(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
151:     """refuse: verb → refuze; noun → refuse."""
152:     if tag in VERB_PRESENT or tag in VERB_PAST:
153:         return "refuze", "pos-verb"
154:     return "refuse", "pos-noun"
155:
156:
157: def decide_elaborate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
158:     """elaborate: verb → elaboreight; adj → elaborit."""
159:     if tag in VERB_PRESENT or tag in VERB_PAST:
160:         return "elaboreight", "pos-verb"
161:     return "elaborit", "pos-adj"
162:
163:
164: def decide_estimate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
165:     """estimate: verb → estimeight; noun → estimit."""
166:     if tag in VERB_PRESENT or tag in VERB_PAST:
167:         return "estimeight", "pos-verb"
168:     return "estimit", "pos-noun"
169:
170:
171: def decide_wind(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
172:     """
173:     Decide pronunciation for 'wind': verb sense 'why'nd' (to coil/twist) vs noun sense 'win'd' (moving air).
174:
175:     Args:
176:         tag: Fine-grained POS tag from spaCy (e.g. 'VBG', 'NN').
177:         dep: Dependency relation of the token (e.g. 'ROOT', 'advcl', 'nsubj').
178:         head: Lowercased head word text.
179:         has_det: True if the token has a determiner child (e.g. "the wind").
180:         nli: Optional zero-shot NLI pipeline (not used for wind).
181:         sentence: Full sentence context for additional checks.
182:
183:     Returns:
184:         Tuple of (pronunciation, route) where pronunciation is 'why'nd' or 'win'd',
185:         and route describes the decision path for logging.
186:     """
187:     # Core verb rule: only return the verb pronunciation ('why'nd') when the tag
188:     # indicates a verb form AND the dependency is a core verbal governor.
189:     # This aligns exactly with the tightened complex_pos dep_rules for why'nd
190:     # (only ROOT/xcomp/ccomp with match_mode "all"). It prevents spaCy mis-tags
191:     # of noun "wind" as VBG/VBN in reduced clauses (e.g. "wind flinging", "wind rushing",
192:     # "Wind ripped") which commonly attach with advcl/relcl/acl.
193:     if (tag in VERB_PRESENT or tag in VERB_PAST) and dep in ("ROOT", "xcomp", "ccomp"):
194:         return "why'nd", "pos-verb-core"
195:
196:     # Strong noun bias via determiner: phrases like "the wind", "a wind", or "this wind"
197:     # are almost always the noun sense. Prefer 'win'd' even if spaCy mis-tagged the POS.
198:     if has_det:
199:         return "win'd", "det-noun"
200:
201:     # Default to noun for everything else. This includes:
202:     # - Correct noun tags (NN/NNS)
203:     # - Mis-tagged verbs in non-core dependencies (the common failure mode for these cases)
204:     # - Any other ambiguous or non-verbal attachments
205:     # The goal is to never let a non-core verbal attachment force the verb spelling for 'wind'.
206:     return "win'd", "pos-noun"
207:
208:
209: def decide_lead(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
210:     """lead: VBD → led; verb → leed; adj/nn+nli → nli decision; noun → led."""
211:     if tag == "VBD":
212:         return "led", "pos-verb-past"
213:     if tag in VERB_PRESENT:
214:         return "leed", "pos-verb"
215:     if (tag in ADJ_TAGS or tag == "NN") and nli:
216:         return nli_decide(nli, sentence, "lead",
217:             "a person in a leading/supervising role",
218:             "leed",
219:             "the metal lead (Pb)",
220:             "led")
221:     return "led", "pos-noun"
222:
223:
224: def decide_invalid(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
225:     """
226:     invalid: special adj rules for 'in-valid'; noun 'invalid' for copular/predicative uses.
227:     """
228:     if tag in ADJ_TAGS:
229:         if dep == "pobj" and head == "of":
230:             return "invalid", "jj-pobj-of-noun"
231:         # Extended 'jj-but-noun' and attr checks to catch copular/predicative uses
232:         # like "being an invalid", "an invalid.", "as an invalid" (disabled person noun).
233:         # Broadened deps and removed strict has_det for attr-like complements.
234:         if has_det and dep in {"nsubj", "dobj", "pobj", "nsubjpass", "attr", "acomp", "appos"}:
235:             return "invalid", "jj-but-noun"
236:         if dep in {"attr", "acomp", "appos"}:
237:             return "invalid", "jj-attr-noun"
238:         return "in-valid", "pos-adj"
239:     return "invalid", "pos-noun"
240:
241:
242: _TEAR_EYES_AWAY = re.compile(
243:     r'\btear\b.{0,40}?\b(eyes?|gaze|attention|focus|sight)\b.{0,20}?\baway\b',
244:     re.IGNORECASE | re.DOTALL
245: )
246:
247:
248: def decide_tear(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
249:     """tear: verb+eyes-away → tair; verb+nli → nli; noun+through → tair; noun+nli → nli."""
250:     if tag in VERB_PRESENT or tag in VERB_PAST:
251:         if _TEAR_EYES_AWAY.search(sentence):
252:             return "tair", "pos-tear-eyes-away"
253:         return nli_decide(nli, sentence, "tear",
254:             "an action of ripping, shredding, or physically pulling something apart",
255:             "tair",
256:             "eyes watering, filling with tears, or about to cry",
257:             "teer")
258:     if dep == "pobj" and head == "through":
259:         return "tair", "pos-pobj-through"
260:     return nli_decide(nli, sentence, "tear",
261:         "a rip, hole, cut, wound, injury, or physical damage in material or flesh, or a rift, gap, tunnel, throughway, or transitional opening",
262:         "tair",
263:         "a teardrop, teardrop shape, liquid from the eye, or emotional response",
264:         "teer")
265:
266:
267: def decide_polish(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
268:     """polish: capitalized+NNP → pole-ish; verb → pollish; adj → pole-ish; default → pollish."""
269:     word_in_sent = next((w for w in sentence.split() if w.lower() == "polish"), None)
270:     if word_in_sent and word_in_sent[0].isupper() and tag == "NNP":
271:         return "pole-ish", "cap-proper"
272:     if tag in VERB_PRESENT or tag in VERB_PAST:
273:         return "pollish", "pos-verb"
274:     if tag in ADJ_TAGS:
275:         return "pole-ish", "pos-adj"
276:     return "pollish", "pos-default"
277:
278:
279: BASS_MUSIC_HEADS = {"case", "player", "guitar", "drum", "line", "clef", "man", "solo", "note"}
280: BASS_FISH_HEADS = {"boat", "fishing", "tournament", "lure", "angling", "farming"}
281: BASS_FISH_VERBS = {
282:     "caught", "catch", "fry", "frying", "fried", "cook", "cooking", "cooked",
283:     "ate", "eat", "eating", "hook", "hooked", "reel", "reeled", "land", "landed"
284: }
285:
286:
287: def decide_bass(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
288:     """bass: compound+music → base; compound+fish → bass; verb+fish → bass; else nli."""
289:     if dep == "compound":
290:         if head in BASS_MUSIC_HEADS:
291:             return "base", "pos-compound-music"
292:         if head in BASS_FISH_HEADS:
293:             return "bass", "pos-compound-fish"
294:     if head in BASS_FISH_VERBS:
295:         return "bass", "pos-verb-fish"
296:     if not nli:
297:         return "base", "nli-disabled"
298:     try:
299:         q_music = "low-pitched sound, bass tones in music, a bass instrument (guitar, drum, etc.), or a bass musician"
300:         q_fish = "a species of fish (largemouth bass, sea bass, striped bass, etc.) caught in fishing"
301:         result = nli(sentence, candidate_labels=[q_music, q_fish], multi_label=False)
302:         scores = dict(zip(result["labels"], result["scores"]))
303:         if scores[q_fish] > 0.70:
304:             return "bass", f"nli=bass({scores[q_fish]:.2f})"
305:         return "base", f"nli=base({scores[q_music]:.2f})"
306:     except Exception:
307:         return "base", "nli-error"
308:
309:
310: _POSITIONAL_ROW = re.compile(r'\b(front|back|first|last|middle)\s+row\b', re.IGNORECASE)
311: _ROW_OF = re.compile(r'\brow\s+of\b', re.IGNORECASE)
312:
313:
314: def decide_row(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
315:     """row: compound → ro; npadvmod → ro; verb → ro; positional → ro; row-of → ro; else nli."""
316:     if dep == "compound":
317:         return "ro", "pos-compound"
318:     if dep == "npadvmod":
319:         return "ro", "pos-npadvmod"
320:     if tag in VERB_PRESENT or tag in VERB_PAST:
321:         return "ro", "pos-verb"
322:     if _POSITIONAL_ROW.search(sentence):
323:         return "ro", "pos-positional"
324:     if _ROW_OF.search(sentence):
325:         return "ro", "pos-row-of"
326:     return nli_decide(nli, sentence, "row",
327:         "a line, sequence, or series of things arranged in order, or in a row meaning one after another consecutively",
328:         "ro",
329:         "a loud verbal argument, quarrel, or shouting match between people",
330:         "rau")
331:
332:
333: def decide_bowed(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
334:     """bowed: VBN+no-heads → boed; else nli."""
335:     if tag == "VBN" and not re.search(r'\bheads?\b', sentence, re.IGNORECASE):
336:         return "boed", "pos-vbn-deformation"
337:     return nli_decide(nli, sentence, "bowed",
338:         "a physical object or structure (shelf, fence, roof, wood, limb) has been bent or curved by weight or force",
339:         "boed",
340:         "a person deliberately lowered their head or body as a gesture of respect or greeting",
341:         "boughed")
342:
343:
344: def decide_wound(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
345:     """
346:     wound: noun/injury → woond; past of 'wind' (coil) → wow'nd; special case for 'wound its way'.
347:     """
348:     # Special case for the common verb idiom "wound its way" (past of 'wind').
349:     # This overrides even if spaCy mis-tags as NNS/NN (as seen in logs for "A tube ... wound its way").
350:     # User confirmed treating "wound the clock" / "wound its way" as past of 'wind' (wow'nd) is acceptable.
351:     if re.search(r'\bwound its way\b', sentence, re.IGNORECASE):
352:         return "wow'nd", "pos-verb-wind-its-way"
353:
354:     if tag not in VERB_PAST and tag not in VERB_PRESENT:
355:         return "woond", "pos-noun"
356:     if tag == "VB":
357:         return "woond", "pos-vb-injure"
358:     return "wow'nd", "pos-verb-wind"
359:
360:
361: def decide_recreation(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
362:     """recreation: compound → rek-reation; else nli."""
363:     if dep == "compound":
364:         return "rek-reation", "pos-compound-leisure"
365:     return nli_decide(nli, sentence, "recreation",
366:         "the act of recreating or rebuilding something that previously existed",
367:         "re-kreation",
368:         "a hobby, pastime, leisure activity, sport, or something done for enjoyment and relaxation",
369:         "rek-reation")
370:
371:
372: def decide_jesus(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
373:     """Jesus: biblical/exclamation vs Spanish name via nli."""
374:     return nli_decide(nli, sentence, "jesus",
375:         "the biblical Christian figure or used as a religious exclamation",
376:         "Jesus",
377:         "a Latin American or Spanish personal name (Jesús)",
378:         "heysous")
379:
380:
381: DECIDERS = {
382:     "record": decide_record,
383:     "records": decide_records,  # dedicated plural handler returning rekords/rekkurds + NNS-mistag gate
384:     "close": decide_close,
385:     "read": decide_read,
386:     "live": decide_live,
387:     "object": decide_object,
388:     "present": decide_present,
389:     "sow": decide_sow,
390:     "resume": decide_resume,
391:     "refuse": decide_refuse,
392:     "elaborate": decide_elaborate,
393:     "estimate": decide_estimate,
394:     "wind": decide_wind,
395:     "lead": decide_lead,
396:     "invalid": decide_invalid,
397:     "tear": decide_tear,
398:     "polish": decide_polish,
399:     "row": decide_row,
400:     "bass": decide_bass,
401:     "bowed": decide_bowed,
402:     "wound": decide_wound,
403:     "recreation": decide_recreation,
404:     "jesus": decide_jesus,
405: }
406:
407: NLI_WORDS = {"row", "bass", "bowed", "recreation", "jesus", "tear", "lead"}

(End of file - total 407 lines)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 5.2s)

_Thinking:_

Now let me read the rest of ai_choices.py to understand the full flow, particularly _run_all_rules and _get_consensus_from_rules.

Let me read the rest of ai_choices.py and also find the choices.py base class and the rules:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1140
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1140:                             "Quota exhausted — skipping remaining AI batches",
1141:                         )
1142:                     continue
1143:
1144:                 log_message(
1145:                     f"Sending chunk {i // BATCH_SIZE + 1} ({len(chunk)} items) to AI for batch analysis. Item IDs: {[item['id'] for item in chunk]}",
1146:                     level="DEBUG",
1147:                 )
1148:
1149:                 try:
1150:                     # Note: The AIResponse class is imported from ..ai.service
1151:                     from ..ai.service import AIResponse
1152:
1153:                     # Build example sentences for the unique words in this chunk
1154:                     chunk_words = set(item["word"].lower() for item in chunk)
1155:                     word_examples = {}
1156:                     for w in chunk_words:
1157:                         options = self.lexicon_loader.get_options(w)
1158:                         if options:
1159:                             word_examples[w] = {
1160:                                 opt["spelling"]: opt.get("examples", [])
1161:                                 for opt in options
1162:                                 if opt.get("examples")
1163:                             }
1164:
1165:                     chunk_results = self.ai_service.analyze_homographs_batch(
1166:                         chunk, word_examples=word_examples
1167:                     )
1168:                     log_message(
1169:                         f"DEBUG: Received chunk results. Item IDs: {list(chunk_results.keys())}",
1170:                         level="DEBUG",
1171:                     )
1172:                     # Check if quota was exhausted in this batch
1173:                     for resp in chunk_results.values():
1174:                         if not resp.success and "Quota exhausted" in (
1175:                             resp.error_message or ""
1176:                         ):
1177:                             quota_exhausted = True
1178:                             break
1179:                     all_batch_results.update(chunk_results)
1180:                 except Exception as e:
1181:                     log_message(
1182:                         f"Error processing chunk {i // BATCH_SIZE + 1}: {e}",
1183:                         level="ERROR",
1184:                     )
1185:                     # Create failure responses for items in this chunk
1186:                     for item in chunk:
1187:                         all_batch_results[item["id"]] = AIResponse(
1188:                             False, "", 0.0, f"Batch request failed: {e}"
1189:                         )
1190:
1191:             # Process the combined results from all chunks
1192:             for item_id, ai_response in all_batch_results.items():
1193:                 log_message(f"DEBUG: Processing item_id: {item_id}", level="DEBUG")
1194:                 (
1195:                     match,
1196:                     word,
1197:                     options,
1198:                     contextualized_options,
1199:                     detected_pos_tag,
1200:                     rule_decision,
1201:                     rule_source,
1202:                 ) = match_map[item_id]
1203:                 decision_source = "llm"
1204:                 ai_decision = None
1205:
1206:                 if ai_response.success:
1207:                     ai_decision = {
1208:                         "choice": ai_response.content,
1209:                         "confidence": ai_response.confidence,
1210:                         "reason": ai_response.reasoning,
1211:                     }
1212:                     self.decision_stats[decision_source] += 1
1213:                     self._log_rule_choice(
1214:                         word, ai_response.content, ai_response.confidence, "llm"
1215:                     )
1216:                 else:
1217:                     if rule_decision is not None and rule_source is not None:
1218:                         # VERIFY_ALL MODE fallback: rule had a consensus, use it
1219:                         # and preserve the original rule source tag.
1220:                         ai_decision = rule_decision
1221:                         decision_source = rule_source
1222:                         self.decision_stats[decision_source] += 1
1223:                         self._log_rule_choice(
1224:                             word,
1225:                             ai_decision["choice"],
1226:                             ai_decision.get("confidence", 0.0),
1227:                             f"ai_failed→{rule_source}",
1228:                         )
1229:                     else:
1230:                         # Old behavior: no prior rule consensus, fall back to first option
1231:                         decision_source = "default"
1232:                         ai_decision = {
1233:                             "choice": options[0],
1234:                             "confidence": 0.5,
1235:                             "reason": f"AI batch failed: {ai_response.error_message}",
1236:                         }
1237:                         self.decision_stats[decision_source] += 1
1238:                         self._log_rule_choice(
1239:                             word, options[0], 0.5, "ai_failed→default"
1240:                         )
1241:
1242:                 self._log_change(
1243:                     match,
1244:                     word,
1245:                     options,
1246:                     ai_decision,
1247:                     decision_source,
1248:                     contextualized_options,
1249:                     detected_pos_tag,
1250:                 )
1251:                 # Log comprehensive entry for this word
1252:                 self._log_comprehensive_rule_entry(
1253:                     word,
1254:                     match,
1255:                     {},
1256:                     detected_pos_tag,
1257:                     ai_decision,
1258:                     decision_source,
1259:                     options,
1260:                 )
1261:
1262:         log_message(
1263:             f"AI review mode complete: {len(self.change_tracker.changes)} decisions logged for review"
1264:         )
1265:         self._log_to_choices_log(f"\n=== AI CHOICES BATCH PROCESSING COMPLETED ===")
1266:         log_message(
1267:             f"AI review mode complete: {len(self.change_tracker.changes)} changes processed for review"
1268:         )
1269:         self._write_end_of_run_summary()
1270:         log_message("DEBUG: Exiting process_choices_ai_review_mode", level="DEBUG")
1271:         return self.change_tracker
1272:
1273:     def _run_all_rules(
1274:         self, word: str, context_full: str, ctx: "BookfixContext"
1275:     ) -> Tuple[Dict, str]:
1276:         """Helper to run all local rules and return their results and the detected POS tag."""
1277:         log_message(f"DEBUG: Entering _run_all_rules for word: '{word}'", level="DEBUG")
1278:         log_message(
1279:             f"DEBUG: _run_all_rules context_full: '{context_full}'", level="DEBUG"
1280:         )
1281:
1282:         all_rules = {}
1283:         detected_pos_tag = ""
1284:         pos_token = None
1285:         dep_info = None
1286:         doc = None
1287:
1288:         # Extract bracket context using case-insensitive match
1289:         import re
1290:
1291:         match = re.search(r"\[" + re.escape(word) + r"\]", context_full, re.IGNORECASE)
1292:         if not match:
1293:             log_message(
1294:                 f"DEBUG: _run_all_rules: bracket '[{word}]' not found in context_full",
1295:                 level="DEBUG",
1296:             )
1297:             return {}, ""
1298:         # Extract actual matched text to preserve original case (e.g., "Polish" not "polish")
1299:         actual_word_text = match.group()[1:-1]
1300:         bracket_start = match.start()
1301:         context_before = context_full[:bracket_start]
1302:         context_after = context_full[bracket_start + len(actual_word_text) + 2 :]
1303:         log_message(
1304:             f"DEBUG: _run_all_rules context_before: '{context_before}', context_after: '{context_after}'",
1305:             level="DEBUG",
1306:         )
1307:
1308:         if self.use_pos_tagging and self.pos_tagger:
1309:             log_message(
1310:                 f"DEBUG: _run_all_rules: Attempting POS tagging for '{word}'",
1311:                 level="DEBUG",
1312:             )
1313:             # Get rich spaCy context
1314:             try:
1315:                 pos_token, dep_info, doc = self.pos_tagger.get_token_and_dependency(
1316:                     context_before, word, context_after
1317:                 )
1318:                 if pos_token:
1319:                     detected_pos_tag = pos_token.pos_tag
1320:                     log_message(
1321:                         f"DEBUG: _run_all_rules: Detected POS tag for '{word}': '{detected_pos_tag}'",
1322:                         level="DEBUG",
1323:                     )
1324:                 else:
1325:                     log_message(
1326:                         f"DEBUG: _run_all_rules: No POS token found for '{word}'",
1327:                         level="DEBUG",
1328:                     )
1329:             except Exception as e:
1330:                 log_message(
1331:                     f"DEBUG: _run_all_rules: Error during POS tagging: {e}",
1332:                     level="DEBUG",
1333:                 )
1334:
1335:         # Hybrid decider check: if word has a specialized decider, use it
1336:         if word.lower() in DECIDERS and pos_token and dep_info and doc:
1337:             log_message(
1338:                 f"DEBUG: _run_all_rules: Using hybrid decider for '{word}'",
1339:                 level="DEBUG",
1340:             )
1341:             try:
1342:                 # Load NLI if needed for this word
1343:                 if word.lower() in NLI_WORDS:
1344:                     self._ensure_nli_services()
1345:
1346:                 # Extract sentence from context
1347:                 sentence = (
1348:                     context_before.rstrip()
1349:                     + " "
1350:                     + actual_word_text
1351:                     + " "
1352:                     + context_after.lstrip()
1353:                 )
1354:
1355:                 # Get parameters from spaCy structures
1356:                 tag = pos_token.pos_tag  # Fine-grained tag (VBN, NN, etc.)
1357:                 dep = dep_info.dep_relation  # Dependency relation (nsubj, dobj, etc.)
1358:                 head_text = dep_info.head_word.lower() if dep_info.head_word else ""
1359:
1360:                 # Check if word has a determiner child by checking the doc
1361:                 # Find the target token in the doc to check its children
1362:                 target_token_in_doc = None
1363:                 word_lower = word.lower()
1364:                 for token in doc:
1365:                     if token.text.lower() == word_lower and token.i == pos_token.index:
1366:                         target_token_in_doc = token
1367:                         break
1368:                 has_det = (
1369:                     any(c.dep_ == "det" for c in target_token_in_doc.children)
1370:                     if target_token_in_doc
1371:                     else False
1372:                 )
1373:
1374:                 # Call the hybrid decider
1375:                 decider_fn = DECIDERS[word.lower()]
1376:                 pronunciation, route = decider_fn(
1377:                     tag, dep, head_text, has_det, self.nli, sentence
1378:                 )
1379:
1380:                 all_rules["hybrid"] = {
1381:                     "choice": pronunciation,
1382:                     "confidence": 0.95,  # High confidence for hand-tuned deciders
1383:                     "reason": f"Hybrid decider ({route})",
1384:                 }
1385:                 log_message(
1386:                     f"DEBUG: _run_all_rules: Hybrid decider matched '{word}' → '{pronunciation}' ({route})",
1387:                     level="DEBUG",
1388:                 )
1389:                 self._log_rule_evaluation(
1390:                     word,
1391:                     "hybrid",
1392:                     f"Tag: {tag}, Dep: {dep}",
1393:                     f"Match: {pronunciation} ({route})",
1394:                 )
1395:
1396:             except Exception as e:
1397:                 log_message(
1398:                     f"DEBUG: _run_all_rules: Hybrid decider error for '{word}': {e}",
1399:                     level="DEBUG",
1400:                 )
1401:                 # Fall through to generic rules if hybrid fails
1402:
1403:         # Rule 1: Complex POS rules (e.g., imperative verbs)
1404:         if self.pos_dictionary and pos_token and dep_info and doc:
1405:             log_message(
1406:                 f"DEBUG: _run_all_rules: Checking complex POS rules for '{word}'",
1407:                 level="DEBUG",
1408:             )
1409:             try:
1410:                 complex_pos_result = (
1411:                     self.pos_dictionary.get_pronunciation_by_complex_pos_rules(
1412:                         actual_word_text, pos_token, dep_info, doc
1413:                     )
1414:                 )
1415:                 if complex_pos_result:
1416:                     all_rules["complex_pos"] = {
1417:                         "choice": complex_pos_result,
1418:                         "confidence": 0.98,
1419:                         "reason": f"Complex POS rule for '{word}'",
1420:                     }
1421:                     log_message(
1422:                         f"DEBUG: _run_all_rules: Complex POS rule matched: '{complex_pos_result}'",
1423:                         level="DEBUG",
1424:                     )
1425:                     self._log_rule_evaluation(
1426:                         word,
1427:                         "complex_pos",
1428:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1429:                         "Match" if complex_pos_result else "No match",
1430:                     )
1431:                 else:
1432:                     self._log_rule_evaluation(
1433:                         word,
1434:                         "complex_pos",
1435:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1436:                         "No match",
1437:                     )
1438:             except Exception as e:
1439:                 log_message(
1440:                     f"DEBUG: _run_all_rules: Error checking complex POS rules: {e}",
1441:                     level="DEBUG",
1442:                 )
1443:                 self._log_rule_evaluation(word, "complex_pos", "Error", str(e))
1444:
1445:         # Rule 2: Simple POS tagging (fallback if complex doesn't match)
1446:         log_message(
1447:             f"DEBUG: _run_all_rules: Checking simple POS rule for '{word}'",
1448:             level="DEBUG",
1449:         )
1450:         pos_result = self._get_pos_based_choice(word, context_before, context_after)
1451:         if pos_result:
1452:             pronunciation, confidence, explanation = pos_result
1453:             all_rules["pos"] = {
1454:                 "choice": pronunciation,
1455:                 "confidence": confidence,
1456:                 "reason": f"POS-based: {explanation} [Tag: {detected_pos_tag}]",
1457:             }
1458:             log_message(
1459:                 f"DEBUG: _run_all_rules: Simple POS rule matched: '{pronunciation}'",
1460:                 level="DEBUG",
1461:             )
1462:             self._log_rule_evaluation(
1463:                 word,
1464:                 "pos",
1465:                 f"POS: {detected_pos_tag}, Explanation: {explanation}",
1466:                 f"Match: {pronunciation}",
1467:             )
1468:         else:
1469:             self._log_rule_evaluation(
1470:                 word, "pos", f"POS: {detected_pos_tag}", "No match"
1471:             )
1472:
1473:         if self.pos_dictionary:
1474:             # Rule 3: Semantic matching
1475:             log_message(
1476:                 f"DEBUG: _run_all_rules: Checking semantic rule for '{word}'",
1477:                 level="DEBUG",
1478:             )
1479:             before_tokens = re.findall(r"\b\w+\b", context_before.lower())[-10:]
1480:             after_tokens = re.findall(r"\b\w+\b", context_after.lower())[:10]
1481:             try:
1482:                 semantic_result = self.pos_dictionary.get_pronunciation_by_semantic(
1483:                     word, before_tokens + after_tokens
1484:                 )
1485:                 if semantic_result:
1486:                     pronunciation, matched_tag, confidence = semantic_result
1487:                     all_rules["semantic"] = {
1488:                         "choice": pronunciation,
1489:                         "confidence": confidence,
1490:                         "reason": f"Semantic: nearby word '{matched_tag}'",
1491:                     }
1492:                     log_message(
1493:                         f"DEBUG: _run_all_rules: Semantic rule matched: '{pronunciation}'",
1494:                         level="DEBUG",
1495:                     )
1496:                     self._log_rule_evaluation(
1497:                         word,
1498:                         "semantic",
1499:                         f"Tokens: {before_tokens + after_tokens}",
1500:                         f"Match: {pronunciation} (tag: {matched_tag})",
1501:                     )
1502:                 else:
1503:                     self._log_rule_evaluation(
1504:                         word,
1505:                         "semantic",
1506:                         f"Tokens: {before_tokens + after_tokens}",
1507:                         "No match",
1508:                     )
1509:             except Exception as e:
1510:                 log_message(
1511:                     f"DEBUG: _run_all_rules: Error checking semantic rule: {e}",
1512:                     level="DEBUG",
1513:                 )
1514:                 self._log_rule_evaluation(word, "semantic", "Error", str(e))
1515:
1516:             # Rule 4: Named entity context
1517:             log_message(
1518:                 f"DEBUG: _run_all_rules: Checking entity rule for '{word}'",
1519:                 level="DEBUG",
1520:             )
1521:             try:
1522:                 entity_result = self.pos_dictionary.check_entity_context(
1523:                     word, context_before, context_after
1524:                 )
1525:                 if entity_result:
1526:                     all_rules["entity"] = {
1527:                         "choice": entity_result,
1528:                         "confidence": 0.85,
1529:                         "reason": f"Entity context: '{entity_result}'",
1530:                     }
1531:                     log_message(
1532:                         f"DEBUG: _run_all_rules: Entity rule matched: '{entity_result}'",
1533:                         level="DEBUG",
1534:                     )
1535:                     self._log_rule_evaluation(
1536:                         word,
1537:                         "entity",
1538:                         f"Context: {context_before} ... {context_after}",
1539:                         f"Match: {entity_result}",
1540:                     )
1541:                 else:
1542:                     self._log_rule_evaluation(
1543:                         word,
1544:                         "entity",
1545:                         f"Context: {context_before} ... {context_after}",
1546:                         "No match",
1547:                     )
1548:             except Exception as e:
1549:                 log_message(
1550:                     f"DEBUG: _run_all_rules: Error checking entity rule: {e}",
1551:                     level="DEBUG",
1552:                 )
1553:                 self._log_rule_evaluation(word, "entity", "Error", str(e))
1554:
1555:         log_message(
1556:             f"DEBUG: Exiting _run_all_rules for word: '{word}'. Found rules: {list(all_rules.keys())}",
1557:             level="DEBUG",
1558:         )
1559:         return all_rules, detected_pos_tag
1560:
1561:     def _log_comprehensive_rule_entry(
1562:         self,
1563:         word: str,
1564:         match,
1565:         all_rules: Dict,
1566:         detected_pos_tag: str,
1567:         decision: Dict,
1568:         decision_source: str,
1569:         options: List,
1570:     ):
1571:         """Log a comprehensive, readable entry for each word processed."""
1572:         import os
1573:         import datetime
1574:
1575:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1576:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1577:         log_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
1578:
1579:         # Get single sentence context
1580:         full_text = self.change_tracker.original_text
1581:         match_start = match.start()
1582:         match_end = match.end()
1583:         context_before, word_in_sent, context_after = self._extract_sentence_context(
1584:             full_text, match_start, match_end
1585:         )
1586:         sentence = f"{context_before}[{word_in_sent}]{context_after}"
1587:
1588:         timestamp = datetime.datetime.now().strftime("%H:%M:%S")
1589:         confidence = decision.get("confidence", 0.0) if decision else 0.0
1590:         chosen = decision.get("choice", "UNKNOWN") if decision else "UNKNOWN"
1591:         reason = decision.get("reason", "") if decision else ""
1592:
1593:         with open(log_path, "a", encoding="utf-8") as f:
1594:             f.write(f'=== ENTRY: "{word}" @ {timestamp} ===\n')
1595:             f.write(f"Sentence: {sentence}\n")
1596:             f.write(f"POS: {detected_pos_tag}\n")
1597:             f.write(f"\nRULE RESULTS:\n")
1598:
1599:             # Log each rule that fired
1600:             if all_rules:
1601:                 for rule_name, rule_data in all_rules.items():
1602:                     rule_choice = rule_data.get("choice", "none")
1603:                     rule_conf = rule_data.get("confidence", 0.0)
1604:                     rule_reason = rule_data.get("reason", "")
1605:                     f.write(
1606:                         f"  {rule_name}: {rule_choice} (conf: {rule_conf:.2f}) - {rule_reason}\n"
1607:                     )
1608:             else:
1609:                 f.write(f"  No rules fired\n")
1610:
1611:             f.write(
1612:                 f"\nFINAL DECISION: {chosen} (confidence: {confidence:.2f}, source: {decision_source})\n"
1613:             )
1614:             f.write(f"  Reason: {reason}\n")
1615:             f.write(f"  Available options: {options}\n")
1616:
1617:             # Consensus explanation: show why winner beat runner-up
1618:             if all_rules and len(all_rules) > 0:
1619:                 sorted_rules = sorted(
1620:                     all_rules.items(),
1621:                     key=lambda x: x[1].get("confidence", 0.0),
1622:                     reverse=True,
1623:                 )
1624:                 winner_name, winner_data = sorted_rules[0]
1625:                 if all(r.get("choice") == chosen for _, r in all_rules.items()):
1626:                     f.write(
1627:                         f"  Consensus: unanimous — all {len(all_rules)} rules chose {chosen}\n"
1628:                     )
1629:                 elif decision_source in ("complex_pos", "replace_rule"):
1630:                     f.write(
1631:                         f"  Consensus: {decision_source} override ({confidence:.2f}) — structural rule takes priority\n"
1632:                     )
1633:                 elif len(sorted_rules) > 1:
1634:                     runner_name, runner_data = sorted_rules[1]
1635:                     margin = sorted_rules[0][1].get("confidence", 0.0) - sorted_rules[
1636:                         1
1637:                     ][1].get("confidence", 0.0)
1638:                     winner_choice = winner_data.get("choice", "?")
1639:                     runner_choice = runner_data.get("choice", "?")
1640:                     if winner_choice != runner_choice:
1641:                         f.write(
1642:                             f"  Consensus: {decision_source}({confidence:.2f}) beat {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f} — DISAGREEMENT\n"
1643:                         )
1644:                     else:
1645:                         f.write(
1646:                             f"  Consensus: {decision_source}({confidence:.2f}) selected over {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f}\n"
1647:                         )
1648:                 else:
1649:                     f.write(
1650:                         f"  Consensus: only rule — {decision_source}({confidence:.2f})\n"
1651:                     )
1652:             f.write("---\n")
1653:
1654:     def _get_consensus_from_rules(
1655:         self, all_rules: Dict, context_full: str, word: str = "", options: List = None
1656:     ) -> Tuple[Optional[Dict], Optional[str], Optional[Dict]]:
1657:         """
1658:         Check for consensus among rule results.
1659:
1660:         Args:
1661:             all_rules: Dictionary of rule results
1662:             context_full: Full context around the word
1663:             word: The word being processed
1664:             options: List of available replacement options for this word
1665:
1666:         Returns:
1667:             Tuple of (decision_dict or None, source_str or None, best_guess_dict or None)
1668:             The third value carries a preferred rule decision (e.g. hybrid) to use
1669:             as best_guess when queuing to AI on disagreement.
1670:
1671:         Strategy:
1672:         1. If all rules agree on the same choice → consensus
1673:         2. If rules disagree:
1674:            - AI enabled → return None (send to AI)
1675:            - AI disabled → fall back to strict priority
1676:         3. If no rules matched → return None (or force in rules_only_mode)
1677:         4. NEW (hybrid mode): Disagreement gate — if complex_pos absent but
1678:            hybrid and pos both present and disagree on choice for a homograph
1679:            (word has hybrid decider), return None so caller queues to AI with
1680:            the hybrid choice as best_guess. This improves quality on ambiguous
1681:            spaCy parses without forcing verify_all globally.
1682:
1683:         NOTE: We intentionally avoid allowing a lower-priority rule (e.g. plain
1684:         'keyword') to win over higher-priority rules (complex_pos/entity/pos/
1685:         semantic) based solely on a slightly higher numeric confidence.
1686:         Additionally, **keyword-only** matches are treated as **no decision** so
1687:         they are always surfaced as low-confidence items for review (or sent to
1688:         AI), never as standalone rules.
1689:         """
1690:         # ===== RULES-ONLY MODE: Apply confidence floor, defer to review if below threshold =====
1691:         if self.rules_only_mode:
1692:             log_message(
1693:                 f"Rules-only mode: Checking decision for '{word}' (rules: {list(all_rules.keys()) if all_rules else 'none'})",
1694:                 level="DEBUG",
1695:             )
1696:             min_confidence = self.config.get("Thresholds", {}).get(
1697:                 "MIN_CONFIDENCE_THRESHOLD", 0.75
1698:             )
1699:             # Log to rule_choice log for tracking
1700:             if not all_rules:
1701:                 forced_choice = (
1702:                     options[0] if options and len(options) > 0 else "UNKNOWN"
1703:                 )
1704:                 self._log_rule_choice(word, forced_choice, 0.0, "rules_only_no_rules")
1705:                 return {
1706:                     "choice": forced_choice,
1707:                     "confidence": 0.0,
1708:                     "reason": "Rules-only: no rules",
1709:                 }, "rules_only", None
1710:             # Check if any rule meets confidence threshold
1711:             if all_rules:
1712:                 best_name = max(all_rules, key=lambda r: all_rules[r]["confidence"])
1713:                 best = all_rules[best_name]
1714:                 if best["confidence"] >= min_confidence:
1715:                     # Meets threshold - use with actual confidence
1716:                     best_copy = best.copy()
1717:                     best_copy["reason"] = f"Rules-only: {best['reason']}"
1718:                     self._log_rule_choice(
1719:                         word,
1720:                         best_copy["choice"],
1721:                         best_copy["confidence"],
1722:                         f"rules_only_{best_name}",
1723:                     )
1724:                     return best_copy, best_name, None
1725:                 else:
1726:                     # Below threshold - defer to review
1727:                     log_message(
1728:                         f"Rules-only mode: Confidence {best['confidence']:.2f} below threshold {min_confidence:.2f}, deferring to review",
1729:                         level="DEBUG",
1730:                     )
1731:                     return None, None, None
1732:             # Fallback
1733:             forced_choice = options[0] if options and len(options) > 0 else "UNKNOWN"
1734:             self._log_rule_choice(word, forced_choice, 0.0, "rules_only_fallback")
1735:             return {
1736:                 "choice": forced_choice,
1737:                 "confidence": 0.0,
1738:                 "reason": "Rules-only fallback",
1739:             }, "rules_only", None
1740:
1741:         # ===== HYBRID/VERIFY MODES: complex_pos > hybrid > pos; all others → AI =====
1742:         if not all_rules:
1743:             return None, None
1744:
1745:         # Rule 1: complex_pos (dep_rules) always wins — 0.98 confidence structural rule
1746:         if "complex_pos" in all_rules:
1747:             rule_decision = all_rules["complex_pos"]
1748:             self._log_rule_choice(
1749:                 word,
1750:                 rule_decision["choice"],
1751:                 rule_decision["confidence"],
1752:                 "complex_pos",
1753:             )
1754:             return rule_decision, "complex_pos", None
1755:
1756:         # Disagreement gate for hybrid/verify mode (only for the 23 homographs):
1757:         # If complex_pos is absent (no strong structural match) but both hybrid
1758:         # decider and simple POS produced choices that differ, do not auto-decide.
1759:         # Return None decision so the caller will queue to AI, passing the hybrid
1760:         # result as best_guess. This routes exactly the ambiguous cases (e.g. live
1761:         # tagged RB in relative clause, lead NN with possessive that NLI wants as
1762:         # guidance) to the LLM for better results while preserving fast rule path
1763:         # when the two agree.
1764:         # Controlled by config Thresholds.DISAGREEMENT_TO_AI (default True).
1765:         if (
1766:             "hybrid" in all_rules
1767:             and "pos" in all_rules
1768:         ):
1769:             hybrid_choice = all_rules["hybrid"]["choice"]
1770:             pos_choice = all_rules["pos"]["choice"]
1771:             if hybrid_choice != pos_choice:
1772:                 disagreement_flag = self.config.get("Thresholds", {}).get(
1773:                     "DISAGREEMENT_TO_AI", True
1774:                 )
1775:                 if disagreement_flag:
1776:                     fired = ", ".join(
1777:                         f"{k}={v['choice']}({v['confidence']:.2f})"
1778:                         for k, v in all_rules.items()
1779:                     )
1780:                     log_message(
1781:                         f"DEBUG: disagreement (hybrid vs pos) for '{word}' — queuing for AI. Rules fired: {fired}",
1782:                         level="DEBUG",
1783:                     )
1784:                     # Return None to force AI queue; attach hybrid as best_guess
1785:                     return None, "disagreement", all_rules["hybrid"]
1786:
1787:         # Rule 2: hybrid deciders — hand-tuned per-word logic, 0.95 confidence
1788:         if "hybrid" in all_rules:
1789:             rule_decision = all_rules["hybrid"]
1790:             self._log_rule_choice(
1791:                 word, rule_decision["choice"], rule_decision["confidence"], "hybrid"
1792:             )
1793:             return rule_decision, "hybrid", None
1794:
1795:         # Rule 3: POS tag — reliable only when pronunciations differ by part of speech
1796:         if "pos" in all_rules:
1797:             rule_decision = all_rules["pos"]
1798:             if rule_decision["confidence"] >= 0.80:
1799:                 self._log_rule_choice(
1800:                     word, rule_decision["choice"], rule_decision["confidence"], "pos"
1801:                 )
1802:                 return rule_decision, "pos", None
1803:
1804:         # Rules 4–7 (semantic, entity, definition, keyword) are not trusted to decide.
1805:         # Log which rules fired for diagnostics, then queue for AI.
1806:         fired = ", ".join(
1807:             f"{k}={v['choice']}({v['confidence']:.2f})" for k, v in all_rules.items()
1808:         )
1809:         log_message(
1810:             f"DEBUG: no autonomous decision — queuing for AI. Rules fired: {fired}",
1811:             level="DEBUG",
1812:         )
1813:         return None, None, None
1814:
1815:     def _log_rule_choice(
1816:         self, word: str, choice: str, confidence: float, rule_type: str
1817:     ):
1818:         """Log rule choices to separate file."""
1819:         import os, re
1820:
1821:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1822:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1823:         log_path = os.path.join(log_dir, "logs", "rules_choices.log")
1824:         sentence = getattr(self, "_current_sentence", "")
1825:         log_line = (
1826:             f"{word} -> {choice} (confidence {confidence:.2f}, rule: {rule_type})"
1827:         )
1828:         if sentence:
1829:             log_line += f" | {sentence}"
1830:         with open(log_path, "a", encoding="utf-8") as f:
1831:             f.write(log_line + "\n")
1832:
1833:     def _log_rule_evaluation(self, word: str, rule: str, details: str, result: str):
1834:         """Log each rule evaluation attempt."""
1835:         import os
1836:         import datetime
1837:
1838:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1839:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1840:         log_path = os.path.join(
1841:             log_dir, "logs", "rule_evaluation.log"
1842:         )  # Changed to separate file
1843:         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
1844:         with open(log_path, "a", encoding="utf-8") as f:
1845:             f.write(
1846:                 f"[{timestamp}] Word: '{word}' | Rule: {rule} | {details} | Result: {result}\n"
1847:             )
1848:
1849:     def _log_ai_choice(self, word: str, choice: str, confidence: float, reason: str):
1850:         """Log AI choices to separate file."""
1851:         import os
1852:
1853:         log_dir = os.path.dirname(os.path.abspath(__file__))
1854:         log_path = os.path.join(log_dir, "ai_choices.log")
1855:         with open(log_path, "w", encoding="utf-8") as f:
1856:             f.write(
1857:                 f"{word} -> {choice} (confidence {confidence:.2f}, reason: {reason})\n"
1858:             )
1859:             # AI disabled - use a simple majority if there is one, otherwise
1860:             # fall back to strict priority (no confidence-based tie-breaking).
1861:             from collections import Counter
1862:
1863:             vote_counts = Counter(choices)
1864:             most_common_choice, vote_count = vote_counts.most_common(1)[0]
1865:
1866:             total_votes = len(choices)
1867:             if vote_count > total_votes / 2:
1868:                 # Clear majority - find which rule suggested it (prefer higher priority)
1869:                 priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
1870:                 for rule_name in priority_order:
1871:                     if (
1872:                         rule_name in all_rules
1873:                         and all_rules[rule_name]["choice"] == most_common_choice
1874:                     ):
1875:                         consensus_decision = all_rules[rule_name].copy()
1876:                         consensus_decision["reason"] = (
1877:                             f"Consensus ({vote_count}/{total_votes} rules agree): {consensus_decision['reason']}"
1878:                         )
1879:                         return consensus_decision, f"consensus_{rule_name}"
1880:
1881:             # No clear majority (tie or even split) - fall back purely to
1882:             # strict priority order, ignoring confidence.
1883:             log_message(
1884:                 f"DEBUG: No clear consensus, using strict priority fallback",
1885:                 level="DEBUG",
1886:             )
1887:             priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
1888:             for rule_name in priority_order:
1889:                 if rule_name in all_rules:
1890:                     return all_rules[rule_name], rule_name
1891:
1892:         # Should never reach here, but safety fallback
1893:         return None, None
1894:
1895:     def _log_change(
1896:         self,
1897:         match,
1898:         word,
1899:         options,
1900:         decision,
1901:         decision_source,
1902:         contextualized_options,
1903:         detected_pos_tag: str,
1904:     ):
1905:         """Helper function to log a change to the change tracker."""
1906:         # This helper centralizes the logic for adding a change to the tracker
1907:         if decision is None:
1908:             log_message(
1909:                 f"WARNING: _log_change called with None decision for word '{word}'",
1910:                 level="WARNING",
1911:             )
1912:             return
1913:         replacement = decision["choice"]
1914:         confidence = decision["confidence"]
1915:         reason = decision.get("reason", "")
1916:
1917:         # Calculate context_before and context_after directly from original_text
1918:         # This avoids issues with splitting context_full if the bracketed word is not found or malformed
1919:         full_text = self.change_tracker.original_text
1920:         match_start_in_full_text = match.start()
1921:         match_end_in_full_text = match.end()
1922:
1923:         # Always extract 250-character context for review window display
1924:         context_start_raw = max(0, match_start_in_full_text - self.context_size)
1925:         context_end_raw = min(
1926:             len(full_text), match_end_in_full_text + self.context_size
1927:         )
1928:
1929:         log_message(
1930:             f"DEBUG: _log_change - len(full_text): {len(full_text)}, match.start(): {match.start()}, match.end(): {match.end()}, context_start_raw: {context_start_raw}, match_start_in_full_text: {match_start_in_full_text}, match_end_in_full_text: {match_end_in_full_text}, context_end_raw: {context_end_raw}",
1931:             level="DEBUG",
1932:         )
1933:         # The actual context_before and context_after for logging should be the raw text around the match
1934:         # up to the match boundaries, within the context_size window.
1935:         # This is the text *before* the matched word, within the context window
1936:         actual_context_before = full_text[context_start_raw:match_start_in_full_text]
1937:         # This is the text *after* the matched word, within the context window
1938:         actual_context_after = full_text[match_end_in_full_text:context_end_raw]
1939:
1940:         # Also extract single sentence context for learning storage
1941:         sentence_before, _, sentence_after = self._extract_sentence_context(
1942:             full_text, match_start_in_full_text, match_end_in_full_text
1943:         )
1944:         sentence_context = f"{sentence_before} {sentence_after}".strip()
1945:
1946:         self.change_tracker.add_change(
1947:             module_name="choices",
1948:             original=match.group(0),
1949:             replacement=replacement,
1950:             options=options,
1951:             start_pos=match.start(),
1952:             end_pos=match.end(),
1953:             context_before=actual_context_before,
1954:             context_after=actual_context_after,
1955:             confidence=confidence,
1956:             reasoning=reason,
1957:             pos_tag=detected_pos_tag,
1958:             decision_source=decision_source,
1959:             sentence_context=sentence_context,
1960:         )
1961:
1962:     def get_decision_statistics(self) -> Dict:
1963:         """Get statistics about decision sources."""
1964:         return self.decision_stats
1965:
1966:     def process_choices_ai(self, ctx: "BookfixContext") -> str:
1967:         """
1968:         Process choices using AI analysis with rules-only fallback (review mode).
1969:
1970:         Args:
1971:             ctx: BookfixContext with text and choices to process
1972:
1973:         Returns:
1974:             Processed text
1975:         """
1976:         if not self.ai_enabled or not self.ai_service:
1977:             log_message("AI not available, using rules-only mode (review window)")
1978:             log_message(
1979:                 f"DEBUG: ai_enabled={self.ai_enabled}, ai_service={self.ai_service is not None}"
1980:             )
1981:             # Use review mode with rules (POS tagging, keywords, etc.) instead of manual fallback
1982:             tracker = self.process_choices_ai_review_mode(ctx, force_all=False)
1983:             log_message(
1984:                 f"DEBUG: process_choices_ai_review_mode returned tracker={tracker is not None}"
1985:             )
1986:             if tracker:
1987:                 log_message(
1988:                     f"DEBUG: Returning text from tracker, changes={len(tracker.changes)}"
1989:                 )
1990:                 return (
1991:                     tracker.current_text
1992:                     if hasattr(tracker, "current_text")
1993:                     else ctx.text
1994:                 )
1995:             else:
1996:                 log_message("Review mode failed, falling back to manual processing")
1997:                 return self.process_choices(ctx)
1998:
1999:         # Initialize POS services BEFORE processing any words (needed for contextual analysis)
2000:         if self.use_pos_tagging:
2001:             self._ensure_pos_services()
2002:             # Refresh dictionary reference in case keywords were updated via keyword dialog
2003:             self._refresh_pos_dictionary()
2004:
2005:         log_message(
2006:             f"Starting AI choice processing with {len(ctx.choices)} choice rules"
2007:         )
2008:
2009:         # Reset tracking
2010:         self.ai_decisions = []
2011:         self.manual_decisions = []
2012:
2013:         # Process each choice rule - prioritize contextualized choices
2014:         words_to_process = set(ctx.choices.keys())
2015:
2016:         for word in words_to_process:
2017:             log_message(f"Processing word '{word}' with AI analysis")
2018:
2019:             # Find all matches of this word in the text
2020:             matches = self._find_matches(word, ctx.text)
2021:
2022:             if not matches:
2023:                 continue
2024:
2025:             # Get options (prioritize contextualized if available)
2026:             contextualized_options = ctx.contextualized_choices.get(word)
2027:             regular_options = ctx.choices.get(word, [])
2028:             # Build options list: prefer regular options, fall back to contextualized options
2029:             if regular_options:
2030:                 options = regular_options
2031:             elif contextualized_options:
2032:                 options = [opt for opt, _ in contextualized_options]
2033:             else:
2034:                 options = []
2035:
2036:             # Process matches in reverse order (rightmost first) to avoid position corruption
2037:             for match in reversed(matches):
2038:                 context = self._extract_context(
2039:                     ctx.text,
2040:                     match.start(),
2041:                     match.end(),
2042:                     self.context_size,
2043:                     single_sentence=self.single_sentence_context,
2044:                 )
2045:
2046:                 # Try AI analysis - use contextualized method if available
2047:                 if contextualized_options:
2048:                     ai_decision = self._analyze_with_contextualized_ai(
2049:                         word, context, contextualized_options
2050:                     )
2051:                 else:
2052:                     ai_decision = self._analyze_with_ai(word, context, regular_options)
2053:
2054:                 if (
2055:                     ai_decision
2056:                     and ai_decision["confidence"] >= self.confidence_threshold
2057:                 ):
2058:                     # Apply AI decision
2059:                     original_word = ctx.text[match.start() : match.end()]
2060:                     replacement = ai_decision["choice"]
2061:
2062:                     # Replace in text
2063:                     ctx.text = (
2064:                         ctx.text[: match.start()]
2065:                         + replacement
2066:                         + ctx.text[match.end() :]
2067:                     )
2068:
2069:                     log_message(
2070:                         f"AI replaced '{original_word}' with '{replacement}' (confidence: {ai_decision['confidence']:.2f})"
2071:                     )
2072:
2073:                     self.ai_decisions.append(
2074:                         {
2075:                             "word": word,
2076:                             "match": match,
2077:                             "context": context,
2078:                             "decision": ai_decision,
2079:                             "position": match.start(),
2080:                         }
2081:                     )
2082:                 else:
2083:                     # Queue for manual processing
2084:                     if self.fallback_to_manual:
2085:                         self.manual_decisions.append(
2086:                             {
2087:                                 "word": word,
2088:                                 "match": match,
2089:                                 "context": context,
2090:                                 "options": options,
2091:                                 "ai_reason": (
2092:                                     ai_decision.get("reason", "Low confidence")
2093:                                     if ai_decision
2094:                                     else "AI analysis failed"
2095:                                 ),
2096:                             }
2097:                         )
2098:                     else:
2099:                         log_message(
2100:                             f"Skipping '{word}' - AI confidence too low and manual fallback disabled"
2101:                         )
2102:
2103:         log_message(
2104:             f"AI processing complete: {len(self.ai_decisions)} automatic, {len(self.manual_decisions)} manual"
2105:         )
2106:
2107:         # If there are manual decisions to make, process them
2108:         if self.manual_decisions and self.fallback_to_manual:
2109:             self._process_manual_decisions(ctx)
2110:
2111:         # Update positions for any remaining changes after text modifications
2112:         self.change_tracker.update_positions_after_text_change(ctx.text)
2113:
2114:         return ctx.text
2115:
2116:     def _analyze_with_ai(
2117:         self,
2118:         word: str,
2119:         context: str,
2120:         options: List[str],
2121:         best_guess: Optional[str] = None,
2122:     ) -> Optional[Dict]:
2123:         """
2124:         Analyze a word choice using AI, enriched with definitions/POS/examples from choices.json when available.
2125:
2126:         Args:
2127:             word: The word to analyze
2128:             context: Context around the word
2129:             options: List of possible replacements
2130:             best_guess: A preliminary guess from local rules to be verified by the AI
2131:
2132:         Returns:
2133:             Dictionary with AI decision or None if failed
2134:         """
2135:         try:
2136:             # Enrich with definitions, POS, and examples from ctx.choice_definitions
2137:             definitions = []
2138:             if (
2139:                 hasattr(self, "ctx")
2140:                 and self.ctx
2141:                 and word.lower() in getattr(self.ctx, "choice_definitions", {})
2142:             ):
2143:                 entry = self.ctx.choice_definitions[word.lower()]
2144:                 for opt in entry.get("options", []):
2145:                     definitions.append(
2146:                         f"{opt['spelling']} ({opt.get('definition', '')}) [{opt.get('pos', 'UNKNOWN')}]"
2147:                     )
2148:
2149:             # Call AI service with enriched contextualized options
2150:             contextualized_options = []
2151:             for opt in options:
2152:                 desc = ""
2153:                 if definitions:
2154:                     # Find matching definition
2155:                     for d in definitions:
2156:                         if opt.lower() in d.lower():
2157:                             desc = d
2158:                             break
2159:                 contextualized_options.append((opt, desc))
2160:
2161:             response = self.ai_service.analyze_contextualized_homograph(
2162:                 word,
2163:                 context,
2164:                 contextualized_options,
2165:                 show_reasoning=True,
2166:                 best_guess=best_guess,
2167:             )
2168:
2169:             if response.success:
2170:                 # Log AI decision
2171:                 self._log_ai_choice(
2172:                     word,
2173:                     response.content,
2174:                     response.confidence,
2175:                     response.reasoning or "AI decision",
2176:                 )
2177:                 return {
2178:                     "choice": response.content,
2179:                     "confidence": response.confidence,
2180:                     "reason": response.reasoning
2181:                     or f"AI chose {response.content} using definition",
2182:                 }
2183:             else:
2184:                 log_message(
2185:                     f"AI analysis failed for '{word}': {response.error_message}"
2186:                 )
2187:                 return None
2188:
2189:         except Exception as e:
2190:             log_message(f"AI analysis error for '{word}': {e}", level="ERROR")
2191:             return None
2192:
2193:     def _analyze_with_contextualized_ai(
2194:         self,
2195:         word: str,
2196:         context: str,
2197:         contextualized_options: List[Tuple[str, str]],
2198:         show_reasoning: Optional[bool] = None,
2199:         best_guess: Optional[str] = None,
2200:         detected_pos_tag: Optional[str] = None,
2201:         context_keywords: Optional[Dict[str, List[str]]] = None,
2202:     ) -> Optional[Dict]:
2203:         """
2204:         Analyze a word choice using AI with context definitions.
2205:
2206:         Args:
2207:             word: The word to analyze
2208:             context: Context around the word
2209:             contextualized_options: List of (spelling, meaning) tuples
2210:             show_reasoning: Override for self.show_reasoning if provided
2211:             best_guess: A preliminary guess from local rules to be verified by the AI
2212:             detected_pos_tag: POS tag from spaCy (VB, NN, etc.) - optional clue for AI
2213:             context_keywords: Dict mapping spelling to keywords indicating that pronunciation - optional clues
2214:
2215:         Returns:
2216:             Dictionary with AI decision or None if failed
2217:         """
2218:         try:
2219:             # Determine whether to show reasoning for this specific call
2220:             use_reasoning = (
2221:                 self.show_reasoning if show_reasoning is None else show_reasoning
2222:             )
2223:
2224:             # If POS tag not provided, try to detect it
2225:             if detected_pos_tag is None and self.pos_tagger is not None:
2226:                 context_before = (
2227:                     context[: context.rfind(word)] if word in context else ""
2228:                 )
2229:                 context_after = (
2230:                     context[context.rfind(word) + len(word) :]
2231:                     if word in context
2232:                     else ""
2233:                 )
2234:                 detected_pos_tag = self.pos_tagger.tag_with_context(
2235:                     context_before, word, context_after
2236:                 )
2237:                 if detected_pos_tag:
2238:                     log_message(
2239:                         f"DEBUG: Extracted POS tag for '{word}': {detected_pos_tag}",
2240:                         level="DEBUG",
2241:                     )
2242:
2243:             # If keywords not provided, try to extract them from dictionary
2244:             if context_keywords is None and self.pos_dictionary is not None:
2245:                 context_keywords = {}
2246:                 for spelling, _ in contextualized_options:
2247:                     option_info = self.pos_dictionary.get_option_info(word, spelling)
2248:                     if option_info:
2249:                         keywords = option_info.get("context_keywords", [])
2250:                         context_keywords[spelling] = keywords
2251:                         if keywords:
2252:                             log_message(
2253:                                 f"DEBUG: Found keywords for '{word}' → '{spelling}': {keywords}",
2254:                                 level="DEBUG",
2255:                             )
2256:                     else:
2257:                         context_keywords[spelling] = []
2258:
2259:             # Call AI service
2260:             response = self.ai_service.analyze_contextualized_homograph(
2261:                 word,
2262:                 context,
2263:                 contextualized_options,
2264:                 use_reasoning,
2265:                 best_guess=best_guess,
2266:                 detected_pos_tag=detected_pos_tag,
2267:                 context_keywords=context_keywords,
2268:             )
2269:
2270:             if response.success:
2271:                 return {
2272:                     "choice": response.content,
2273:                     "confidence": response.confidence,
2274:                     "reason": response.reasoning
2275:                     or f"AI chose {response.content} based on context",
2276:                 }
2277:             else:
2278:                 log_message(
2279:                     f"Contextualized AI analysis failed for '{word}': {response.error_message}"
2280:                 )
2281:                 return None
2282:
2283:         except Exception as e:
2284:             log_message(
2285:                 f"Contextualized AI analysis error for '{word}': {e}", level="ERROR"
2286:             )
2287:             return None
2288:
2289:     def _apply_ai_decision(self, ctx: "BookfixContext", match, decision: Dict) -> None:
2290:         """Apply an AI decision to the text."""
2291:         original_word = ctx.text[match.start() : match.end()]
2292:         replacement = decision["choice"]
2293:
2294:         # Replace in text
2295:         ctx.text = ctx.text[: match.start()] + replacement + ctx.text[match.end() :]
2296:
2297:         log_message(
2298:             f"AI replaced '{original_word}' with '{replacement}' (confidence: {decision['confidence']:.2f})"
2299:         )
2300:
2301:     def _process_manual_decisions(self, ctx: "BookfixContext") -> None:
2302:         """Process remaining decisions manually using the interactive processor."""
2303:         log_message(f"Processing {len(self.manual_decisions)} manual decisions")
2304:
2305:         # Create a temporary context with only the manual decisions
2306:         manual_ctx = type(ctx)()  # Create new context of same type
2307:         manual_ctx.text = ctx.text
2308:         manual_ctx.choices = {}
2309:
2310:         # Group manual decisions by word
2311:         for decision in self.manual_decisions:
2312:             word = decision["word"]
2313:             if word not in manual_ctx.choices:
2314:                 manual_ctx.choices[word] = decision["options"]
2315:
2316:         # Process using parent class
2317:         manual_result = super().process_choices(manual_ctx)
2318:         ctx.text = manual_result.text
2319:
2320:     def _extract_sentence_context(
2321:         self, text: str, start: int, end: int
2322:     ) -> Tuple[str, str, str]:
2323:         """
2324:         Extract ONLY the sentence containing the match using NLTK sentence tokenization.
2325:
2326:         Args:
2327:             text: Full text
2328:             start: Start position of match
2329:             end: End position of match
2330:
2331:         Returns:

(Output capped at 50 KB. Showing lines 1140-2331. Use offset=2332 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/choices.py"
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/choices.py</path>
<type>file</type>
<content>
1: """
2: Interactive text choice processor for Bookfix.
3:
4: This module provides functionality for interactive word choice processing,
5: where users can select from predefined replacement options for specific words.
6: """
7:
8: import re
9: import datetime
10: from pathlib import Path
11: from typing import TYPE_CHECKING, List, Tuple, Optional, Callable, Any, Dict
12:
13: if TYPE_CHECKING:
14:     from ..context import BookfixContext
15:
16:
17: class InteractiveChoiceProcessor:
18:     """
19:     Handles interactive word choice processing with GUI callback support.
20:
21:     This class manages the state for processing interactive word choices,
22:     supporting both Tkinter and PyQt5 GUI frameworks through callbacks.
23:     """
24:
25:     def __init__(self):
26:         """Initializes a new instance of a class that tracks word processing state and GUI callbacks."""
27:         # Reset all state each time we process
28:         self.current_word: Optional[str] = None
29:         self.current_match: int = 0
30:         self.matches: List[Any] = []
31:         self.processed_words: int = 0
32:         self.total_words: int = 0
33:         self.current_text: str = ""
34:
35:         # GUI callbacks - set by the GUI framework
36:         self.progress_callback: Optional[Callable[[int, int, str], None]] = None
37:         self.choice_display_callback: Optional[Callable[[str, List[str]], None]] = None
38:         self.text_update_callback: Optional[Callable[[str, bool], None]] = None
39:         self.status_callback: Optional[Callable[[str], None]] = None
40:         self.completion_callback: Optional[Callable[[], None]] = (
41:             None  # Called when manual processing is complete
42:         )
43:         self.text_edit_widget: Optional[Any] = (
44:             None  # Direct access to text widget for highlighting
45:         )
46:
47:         # Phonetic processing - REMOVED (see phoneticreplacement.txt)
48:         # self.cmu_dict = None
49:         # self.g2p_model = None
50:         # self.phonetic_log: List[Dict] = []  # Log of automatic changes
51:
52:     def reset_state(self):
53:         """Reset all processing state - called before processing new text."""
54:         self.current_word = None
55:         self.current_match = 0
56:         self.matches = []
57:         self.processed_words = 0
58:         self.total_words = 0
59:         self.current_text = ""
60:         # self.phonetic_log = []  # Removed with phonetic analysis
61:
62:     def process_choices(
63:         self, ctx: "BookfixContext", use_spacy_auto: bool = False
64:     ) -> "BookfixContext":
65:         """
66:         Main entry point for interactive choice processing.
67:
68:         Args:
69:             ctx: BookfixContext containing text and choice definitions
70:             use_spacy_auto: Ignored (automatic processing removed)
71:
72:         Returns:
73:             Updated BookfixContext after processing
74:         """
75:         from ..logging import log_message
76:
77:         log_message("Starting interactive choice processing")
78:
79:         # CRITICAL: Reset all state and start fresh with current text
80:         self.reset_state()
81:         self.current_text = ctx.text
82:         log_message(f"Choice processor received text with length: {len(ctx.text)}")
83:
84:         # Clear matches and spacy log files in program directory
85:         try:
86:             import os
87:
88:             script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
89:             matches_path = os.path.join(script_dir, "matches.txt")
90:             spacy_path = os.path.join(script_dir, "spacy.txt")
91:
92:             open(matches_path, "w", encoding="utf-8").close()
93:             open(spacy_path, "w", encoding="utf-8").close()
94:             log_message(f"Cleared log files in program directory: {script_dir}")
95:         except Exception as e:
96:             log_message(f"Error clearing log files: {e}", level="ERROR")
97:
98:         self.total_words = len(ctx.choices)
99:         self.processed_words = 0
100:
101:         if self.total_words == 0:
102:             if self.status_callback:
103:                 self.status_callback("No words require interactive choices")
104:             return ctx
105:
106:         # Start interactive processing first word
107:         self._start_word_processing(ctx)
108:
109:         return ctx
110:
111:     def _start_word_processing(self, ctx: "BookfixContext"):
112:         """Start processing the next word in the choices dictionary."""
113:         if self.processed_words < self.total_words:
114:             words = list(ctx.choices.keys())
115:             self.current_word = words[self.processed_words]
116:             self.current_match = 0
117:
118:             # Find all matches for current word using our current text
119:             self.matches = list(
120:                 re.finditer(
121:                     r"\b" + re.escape(self.current_word) + r"\b",
122:                     self.current_text,
123:                     re.IGNORECASE,
124:                 )
125:             )
126:
127:             self._log_matches_state("start_word_processing")
128:
129:             if self.matches:
130:                 # Highlight first match before displaying choices
131:                 self._highlight_current_match(ctx)
132:
133:                 # Display choices for this word
134:                 options = ctx.choices[self.current_word]
135:                 if self.choice_display_callback:
136:                     self.choice_display_callback(self.current_word, options)
137:             else:
138:                 # No matches, move to next word
139:                 self._finish_current_word(ctx)
140:
141:     def _highlight_current_match(self, ctx: "BookfixContext"):
142:         """Highlight the current match and update status."""
143:         if self.matches and self.current_match < len(self.matches):
144:             match = self.matches[self.current_match]
145:             start, end = match.span()
146:
147:             # Handle our own highlighting directly
148:             self._apply_highlighting(start, end, self.current_word)
149:
150:             if self.status_callback:
151:                 status = f"Replacing {self.current_word}: {self.current_match + 1}/{len(self.matches)}"
152:                 self.status_callback(status)
153:         else:
154:             if self.status_callback:
155:                 self.status_callback(f"Finished {self.current_word}")
156:
157:     def _apply_highlighting(self, start: int, end: int, word: str):
158:         """Apply highlighting directly to our text widget."""
159:         from ..logging import log_message
160:
161:         if not self.text_edit_widget:
162:             log_message("No text widget available for highlighting")
163:             return
164:
165:         log_message(f"Highlighting text: '{word}' at position {start}-{end}")
166:
167:         # Clear previous highlighting
168:         self._clear_highlighting()
169:
170:         # Validate positions against current text
171:         widget_text = self.text_edit_widget.toPlainText()
172:         widget_length = len(widget_text)
173:         processor_length = len(self.current_text)
174:
175:         if widget_length != processor_length:
176:             log_message(
177:                 f"ERROR: Text widget has {widget_length} chars but processor has {processor_length} chars - OUT OF SYNC!"
178:             )
179:             log_message(f"Updating widget with current processor text...")
180:             self.text_edit_widget.setPlainText(self.current_text)
181:             widget_text = self.current_text
182:
183:         if start < 0 or end > len(widget_text) or start >= end:
184:             log_message(
185:                 f"Invalid highlight range: {start}-{end} (text length: {len(widget_text)})"
186:             )
187:             return
188:
189:         # Import Qt classes for highlighting
190:         try:
191:             from PyQt5.QtGui import QTextCursor, QTextCharFormat, QColor
192:
193:             # Get cursor and create highlight format
194:             cursor = self.text_edit_widget.textCursor()
195:             format_highlight = QTextCharFormat()
196:             format_highlight.setBackground(QColor("yellow"))
197:             format_highlight.setForeground(QColor("black"))
198:             format_highlight.setFontWeight(700)
199:
200:             # Apply highlight to the specific range
201:             cursor.setPosition(start)
202:             cursor.setPosition(end, QTextCursor.KeepAnchor)
203:             cursor.setCharFormat(format_highlight)
204:
205:             # Center the highlighted text in viewport after a small delay to ensure highlighting is applied
206:             from PyQt5.QtCore import QTimer
207:
208:             QTimer.singleShot(50, lambda: self._center_text_in_viewport(start))
209:
210:             log_message(f"Applied highlighting to range {start}-{end}")
211:
212:         except Exception as e:
213:             log_message(f"Error applying highlighting: {e}", level="ERROR")
214:
215:     def _center_text_in_viewport(self, position: int):
216:         """Position the highlighted text with context lines above it."""
217:         if not self.text_edit_widget:
218:             return
219:
220:         try:
221:             from PyQt5.QtGui import QTextCursor
222:             from ..logging import log_message
223:
224:             # Find the block (line) containing our position
225:             document = self.text_edit_widget.document()
226:             target_block = document.findBlock(position)
227:             target_line = target_block.blockNumber()
228:
229:             # Go back 3 lines to show context above the highlighted word
230:             context_line = max(0, target_line - 3)
231:             context_block = document.findBlockByNumber(context_line)
232:
233:             # Position cursor at the context line (3 lines above highlighted word)
234:             cursor = self.text_edit_widget.textCursor()
235:             cursor.setPosition(context_block.position())
236:             self.text_edit_widget.setTextCursor(cursor)
237:
238:             # Ensure this position is at the top of the viewport
239:             self.text_edit_widget.ensureCursorVisible()
240:
241:             # Now set cursor back to the highlighted position but don't scroll
242:             cursor.setPosition(position)
243:             self.text_edit_widget.setTextCursor(cursor)
244:
245:             log_message(
246:                 f"Positioned text at line {target_line}, showing context from line {context_line}"
247:             )
248:
249:         except Exception as e:
250:             from ..logging import log_message
251:
252:             log_message(f"Error positioning text: {e}", level="ERROR")
253:
254:     def _clear_highlighting(self):
255:         """Clear all highlighting from the text widget."""
256:         if not self.text_edit_widget:
257:             return
258:
259:         try:
260:             from PyQt5.QtGui import QTextCursor, QTextCharFormat
261:
262:             # Get the current document and clear all formatting
263:             document = self.text_edit_widget.document()
264:             cursor = QTextCursor(document)
265:             cursor.select(QTextCursor.Document)
266:             format_default = QTextCharFormat()
267:             cursor.setCharFormat(format_default)
268:             cursor.clearSelection()
269:             self.text_edit_widget.setTextCursor(cursor)
270:
271:         except Exception as e:
272:             from ..logging import log_message
273:
274:             log_message(f"Error clearing highlighting: {e}", level="ERROR")
275:
276:     def handle_choice(self, choice: str, ctx: "BookfixContext") -> bool:
277:         """
278:         Handle user's choice selection.
279:
280:         Args:
281:             choice: The selected replacement text
282:             ctx: BookfixContext to modify
283:
284:         Returns:
285:             True if more choices needed, False if word is complete
286:         """
287:         from ..logging import log_message
288:
289:         if not self.matches or self.current_match >= len(self.matches):
290:             return self._finish_current_word(ctx)
291:
292:         match = self.matches[self.current_match]
293:         start, end = match.span()
294:         matched_text = self.current_text[start:end]
295:
296:         # Check if no change needed
297:         if choice.lower() == matched_text.lower():
298:             # Skip this match, remove from list
299:             self.matches.pop(self.current_match)
300:
301:             if self.current_match < len(self.matches):
302:                 self._highlight_current_match(ctx)
303:                 return True
304:             else:
305:                 return self._finish_current_word(ctx)
306:
307:         # Apply replacement to both our current text and context
308:         self.current_text = self.current_text[:start] + choice + self.current_text[end:]
309:         ctx.text = self.current_text
310:
311:         # Update text display
312:         if self.text_update_callback:
313:             self.text_update_callback(ctx.text, preserve_highlighting=False)
314:
315:         # Log the replacement
316:         try:
317:             log_path = Path(__file__).parent.parent / "logs" / "debug.txt"
318:             log_path.parent.mkdir(exist_ok=True)
319:             with open(log_path, "a", encoding="utf-8") as debug_file:
320:                 debug_file.write(f"{self.current_word} -> {choice}\n")
321:         except Exception as e:
322:             log_message(f"Error writing to debug.txt: {e}", level="ERROR")
323:
324:         # CRITICAL: Re-find ALL matches in the NEW current text
325:         self.matches = list(
326:             re.finditer(
327:                 r"\b" + re.escape(self.current_word) + r"\b",
328:                 self.current_text,
329:                 re.IGNORECASE,
330:             )
331:         )
332:
333:         # Find next match position
334:         next_index = 0
335:         for i, m in enumerate(self.matches):
336:             if m.start() >= end:
337:                 next_index = i
338:                 break
339:         else:
340:             next_index = len(self.matches)
341:
342:         self.current_match = next_index
343:         self._log_matches_state("after_replacement")
344:
345:         if self.current_match < len(self.matches):
346:             self._highlight_current_match(ctx)
347:             return True
348:         else:
349:             return self._finish_current_word(ctx)
350:
351:     def _finish_current_word(self, ctx: "BookfixContext") -> bool:
352:         """Finish processing current word and move to next."""
353:         self.processed_words += 1
354:
355:         # Update progress
356:         if self.progress_callback:
357:             progress = int((self.processed_words / self.total_words) * 100)
358:             self.progress_callback(
359:                 self.processed_words, self.total_words, f"Progress: {progress}%"
360:             )
361:
362:         if self.processed_words < self.total_words:
363:             self._start_word_processing(ctx)
364:             return True
365:         else:
366:             # All manual words processed - now check if SpaCy processing should run
367:             ctx.log_change(
368:                 "interactive_choices",
369:                 f"Processed {self.total_words} words with interactive choices",
370:                 None,
371:                 None,
372:             )
373:
374:             if self.status_callback:
375:                 self.status_callback("Manual choices processing complete.")
376:
377:             # Automatically trigger completion without requiring user interaction
378:             if self.completion_callback:
379:                 self.completion_callback()
380:
381:             # Signal that manual processing is done
382:             return False
383:
384:     def _log_matches_state(self, location: str):
385:         """Log current matches state for debugging."""
386:         try:
387:             log_path = Path(__file__).parent.parent / "logs" / "matches.txt"
388:             log_path.parent.mkdir(exist_ok=True)
389:             with open(log_path, "a", encoding="utf-8") as f:
390:                 timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
391:                 f.write(f"--- Log Entry ({timestamp}) ---\n")
392:                 f.write(f"Location: {location}\n")
393:                 f.write(f"Current Word: '{self.current_word}'\n")
394:                 f.write(f"Current Match Index: {self.current_match}\n")
395:                 f.write(f"Total Matches Found: {len(self.matches)}\n")
396:                 f.write("Matches Details:\n")
397:
398:                 if self.matches:
399:                     for i, match in enumerate(self.matches):
400:                         try:
401:                             matched_text = match.group(0)
402:                         except IndexError:
403:                             matched_text = "[Error getting match text]"
404:                         f.write(
405:                             f"  Match {i}: Span=({match.start()}, {match.end()}), Text='{matched_text}'\n"
406:                         )
407:                 else:
408:                     f.write("  No matches found.\n")
409:                 f.write("---\n\n")
410:         except Exception as e:
411:             print(f"ERROR: Failed to write to matches.txt: {e}")
412:
413:     # PHONETIC ANALYSIS METHODS REMOVED - see phoneticreplacement.txt for details
414:     # These methods were unreliable and have been disabled
415:
416:     def process_choices_with_phonetic_analysis_DISABLED(
417:         self, ctx: "BookfixContext"
418:     ) -> "BookfixContext":
419:         """
420:         Process tagged choices automatically using phonetic analysis for disambiguation.
421:
422:         Args:
423:             ctx: BookfixContext containing text and tagged choice definitions
424:
425:         Returns:
426:             Updated BookfixContext with automatic processing applied
427:         """
428:         from ..logging import log_message
429:
430:         log_message("Starting phonetic automatic choice processing")
431:
432:         # CRITICAL: Reset processing state and use fresh text from context
433:         # Manual processing may have changed the text, so we need to start fresh
434:         self.current_text = ctx.text  # Get the updated text after manual processing
435:         self.phonetic_log = []  # Clear any previous log entries
436:
437:         log_message(
438:             f"Phonetic analysis received updated text with length: {len(self.current_text)}"
439:         )
440:
441:         # Test debug file creation in program directory and log text sample
442:         try:
443:             import os
444:
445:             script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
446:             phonetic_path = os.path.join(script_dir, "phonetic.txt")
447:             with open(phonetic_path, "a", encoding="utf-8") as f:
448:                 f.write("=== Phonetic Processing Started ===\n")
449:                 # Debug: Log first 500 chars of UPDATED text being processed
450:                 f.write(
451:                     f"UPDATED TEXT SAMPLE (first 500 chars): {self.current_text[:500]}\n"
452:                 )
453:                 f.write("=" * 80 + "\n")
454:         except Exception as e:
455:             log_message(f"ERROR: Cannot create phonetic.txt: {e}", level="ERROR")
456:
457:         # Load phonetic analysis models
458:         if not self._load_phonetic_models():
459:             # Fall back to interactive mode if phonetic analysis fails
460:             log_message(
461:                 "Phonetic analysis unavailable, falling back to interactive mode",
462:                 level="WARNING",
463:             )
464:             return ctx
465:
466:         if self.status_callback:
467:             self.status_callback(
468:                 "Processing tagged choices automatically with phonetic analysis..."
469:             )
470:
471:         # Process tagged choices only
472:         if not hasattr(ctx, "tagged_choices") or not ctx.tagged_choices:
473:             log_message("No tagged choices found for phonetic processing")
474:             return ctx
475:
476:         # Process each tagged word automatically with fresh text
477:         processed_text = self.current_text  # Use the fresh text from manual processing
478:         tagged_words = list(ctx.tagged_choices.keys())
479:
480:         log_message(f"Processing {len(tagged_words)} tagged words in fresh text")
481:
482:         for word_idx, word in enumerate(tagged_words):
483:             tagged_options = ctx.tagged_choices[word]
484:
485:             if self.progress_callback:
486:                 progress = int((word_idx / len(tagged_words)) * 100)
487:                 self.progress_callback(
488:                     word_idx + 1,
489:                     len(tagged_words),
490:                     f"Phonetic processing: {word} ({progress}%)",
491:                 )
492:
493:             # Find all matches for this word in the CURRENT processed text
494:             matches = list(
495:                 re.finditer(
496:                     r"\b" + re.escape(word) + r"\b", processed_text, re.IGNORECASE
497:                 )
498:             )
499:
500:             log_message(f"Processing tagged word '{word}' with {len(matches)} matches")
501:
502:             # Process each match in reverse order to maintain positions
503:             for match in reversed(matches):
504:                 start, end = match.span()
505:                 matched_text = processed_text[start:end]
506:
507:                 # Extract context from the CURRENT processed text (not old text)
508:                 context_before, context_after = self._extract_context(
509:                     processed_text, start, end, context_words=15
510:                 )
511:                 local_context = (
512:                     context_before + " " + matched_text + " " + context_after
513:                 )
514:
515:                 log_message(
516:                     f"Analyzing match at position {start}-{end}: '{matched_text}' in local context: '{local_context[:100]}...'"
517:                 )
518:
519:                 # Use phonetic analysis to determine best replacement with tagged options
520:                 best_choice = self._disambiguate_with_phonetics(
521:                     matched_text, tagged_options, local_context
522:                 )
523:
524:                 if best_choice and best_choice.lower() != matched_text.lower():
525:                     # Replace the text
526:                     processed_text = (
527:                         processed_text[:start] + best_choice + processed_text[end:]
528:                     )
529:
530:                     # Calculate length difference for position adjustment
531:                     length_diff = len(best_choice) - len(matched_text)
532:
533:                     # Log the change with final position (need to track this properly)
534:                     self.phonetic_log.append(
535:                         {
536:                             "original": matched_text,
537:                             "replacement": best_choice,
538:                             "context_before": context_before,
539:                             "context_after": context_after,
540:                             "position": start,  # This will be adjusted later
541:                             "length_diff": length_diff,
542:                             "options": [
543:                                 opt[0] for opt in tagged_options
544:                             ],  # Extract spellings for display
545:                         }
546:                     )
547:
548:                     log_message(
549:                         f"Replaced '{matched_text}' with '{best_choice}' at position {start}"
550:                     )
551:
552:         # Update context and display
553:         ctx.text = processed_text
554:         self.current_text = processed_text
555:
556:         if self.text_update_callback:
557:             self.text_update_callback(ctx.text, preserve_highlighting=False)
558:
559:         # Log completion
560:         ctx.log_change(
561:             "phonetic_auto_choices",
562:             f"Automatically processed {len(self.phonetic_log)} tagged word replacements using phonetic analysis",
563:             None,
564:             None,
565:         )
566:
567:         if self.status_callback:
568:             self.status_callback(
569:                 f"Phonetic processing complete. Made {len(self.phonetic_log)} automatic replacements."
570:             )
571:
572:         log_message(
573:             f"Phonetic automatic processing complete. Made {len(self.phonetic_log)} replacements."
574:         )
575:
576:         return ctx
577:
578:     def _load_phonetic_models_DISABLED(self) -> bool:
579:         """Load CMU dictionary and g2p-en model if not already loaded."""
580:         if self.cmu_dict is not None and self.g2p_model is not None:
581:             return True
582:
583:         try:
584:             import nltk
585:             from nltk.corpus import cmudict
586:             import g2p_en
587:
588:             # Download CMU dictionary if needed
589:             try:
590:                 nltk.data.find("corpora/cmudict")
591:             except LookupError:
592:                 nltk.download("cmudict")
593:
594:             self.cmu_dict = cmudict.dict()
595:             self.g2p_model = g2p_en.G2p()
596:             return True
597:
598:         except ImportError as e:
599:             from ..logging import log_message
600:
601:             log_message(
602:                 f"Phonetic libraries not yet installed, using built-in analysis: {e}",
603:                 level="WARNING",
604:             )
605:             # Use built-in analysis without external libraries
606:             self.cmu_dict = "builtin"  # Flag for built-in mode
607:             self.g2p_model = "builtin"
608:             return True
609:         except Exception as e:
610:             from ..logging import log_message
611:
612:             log_message(
613:                 f"Error loading phonetic models, using built-in analysis: {e}",
614:                 level="WARNING",
615:             )
616:             # Use built-in analysis as fallback
617:             self.cmu_dict = "builtin"
618:             self.g2p_model = "builtin"
619:             return True
620:
621:     def _extract_context(
622:         self, text: str, start: int, end: int, context_words: int = 10
623:     ) -> Tuple[str, str]:
624:         """Extract context words before and after a match."""
625:         import re
626:
627:         # Simple and reliable approach using regex word boundaries
628:         # Get text before the match
629:         text_before = text[:start]
630:         words_before = re.findall(r"\S+", text_before)  # All non-whitespace sequences
631:         context_before = " ".join(words_before[-context_words:]) if words_before else ""
632:
633:         # Get text after the match
634:         text_after = text[end:]
635:         words_after = re.findall(r"\S+", text_after)  # All non-whitespace sequences
636:         context_after = " ".join(words_after[:context_words]) if words_after else ""
637:
638:         return context_before, context_after
639:
640:     def _disambiguate_with_phonetics_DISABLED(
641:         self, word: str, tagged_options: List[Tuple[str, List[str]]], context: str
642:     ) -> Optional[str]:
643:         """Use CMU dictionary and g2p-en to disambiguate word based on phonetic context."""
644:         if not self.cmu_dict or not self.g2p_model:
645:             return None
646:
647:         try:
648:             from ..logging import log_message
649:
650:             log_message(
651:                 f"Phonetic analysis for '{word}' with context: '{context[:100]}...'"
652:             )
653:
654:             # Get pronunciations for each option
655:             option_pronunciations = {}
656:             for spelling, tags in tagged_options:
657:                 pronunciations = self._get_pronunciations(spelling)
658:                 option_pronunciations[spelling] = (pronunciations, tags)
659:                 log_message(f"Option '{spelling}': {pronunciations}")
660:
661:             # Analyze context for phonetic and semantic clues
662:             best_match = None
663:             best_score = 0
664:
665:             # Simple context analysis for common homographs
666:             context_lower = context.lower()
667:             word_lower = word.lower()
668:
669:             for spelling, (pronunciations, tags) in option_pronunciations.items():
670:                 score = 0
671:
672:                 log_message(f"Evaluating option '{spelling}' with tags {tags}")
673:
674:                 # Context-based scoring for common patterns
675:                 if word_lower == "read":
676:                     # Past tense indicators
677:                     past_indicators = [
678:                         "had",
679:                         "have",
680:                         "has",
681:                         "was",
682:                         "were",
683:                         "been",
684:                         "did",
685:                         "yesterday",
686:                         "ago",
687:                         "last",
688:                         "already",
689:                         "before",
690:                     ]
691:                     if any(indicator in context_lower for indicator in past_indicators):
692:                         if "past" in [tag.lower() for tag in tags]:
693:                             score += 15
694:                             log_message(f"  Past tense context match (+15)")
695:                     else:
696:                         # Present/infinitive indicators
697:                         present_indicators = [
698:                             "to",
699:                             "will",
700:                             "can",
701:                             "should",
702:                             "must",
703:                             "would",
704:                             "could",
705:                             "might",
706:                         ]
707:                         if any(
708:                             indicator in context_lower
709:                             for indicator in present_indicators
710:                         ) or "present" in [tag.lower() for tag in tags]:
711:                             if "present" in [
712:                                 tag.lower() for tag in tags
713:                             ] or "infinitive" in [tag.lower() for tag in tags]:
714:                                 score += 15
715:                                 log_message(f"  Present/infinitive context match (+15)")
716:
717:                 elif word_lower == "lead":
718:                     # Metal/noun indicators - expanded and improved
719:                     metal_indicators = [
720:                         "pipe",
721:                         "pipes",
722:                         "box",
723:                         "sheet",
724:                         "weight",
725:                         "bullet",
726:                         "paint",
727:                         "poisoning",
728:                         "heavy",
729:                         "metal",
730:                         "make-up",
731:                         "makeup",
732:                         "pencil",
733:                         "shot",
734:                         "ammunition",
735:                         "roof",
736:                         "plumbing",
737:                         "crystal",
738:                         "glass",
739:                         "gasoline",
740:                         "fuel",
741:                         "based",
742:                         "-based",
743:                         "free",
744:                         "content",
745:                         "level",
746:                     ]
747:                     # Verb indicators - more specific phrases
748:                     verb_indicators = [
749:                         "to lead",
750:                         "will lead",
751:                         "can lead",
752:                         "should lead",
753:                         "must lead",
754:                         "would lead",
755:                         "could lead",
756:                         "might lead",
757:                         "does lead",
758:                         "did lead",
759:                         "leading",
760:                         "leads to",
761:                         "lead the",
762:                         "lead a",
763:                         "lead an",
764:                     ]
765:
766:                     # Check for metal context first (higher priority)
767:                     metal_found = any(
768:                         indicator in context_lower for indicator in metal_indicators
769:                     )
770:                     verb_found = any(
771:                         indicator in context_lower for indicator in verb_indicators
772:                     )
773:
774:                     if metal_found:
775:                         if "metal" in [tag.lower() for tag in tags] or "noun" in [
776:                             tag.lower() for tag in tags
777:                         ]:
778:                             score += 20  # Higher score for metal context
779:                             log_message(f"  Metal/noun context match (+20)")
780:                     elif verb_found:
781:                         if "verb" in [tag.lower() for tag in tags]:
782:                             score += 15
783:                             log_message(f"  Verb context match (+15)")
784:                     else:
785:                         # Check if it's followed by typical metal-related words
786:                         lead_pattern = r"\blead\b\s*[-\s]*\w+"
787:                         import re
788:
789:                         match = re.search(lead_pattern, context_lower)
790:                         if match:
791:                             following_word = (
792:                                 match.group().split()[-1]
793:                                 if len(match.group().split()) > 1
794:                                 else ""
795:                             )
796:                             metal_suffixes = [
797:                                 "based",
798:                                 "free",
799:                                 "paint",
800:                                 "shot",
801:                                 "pipe",
802:                                 "content",
803:                                 "level",
804:                                 "poisoning",
805:                             ]
806:                             if any(
807:                                 suffix in following_word for suffix in metal_suffixes
808:                             ):
809:                                 if "metal" in [
810:                                     tag.lower() for tag in tags
811:                                 ] or "noun" in [tag.lower() for tag in tags]:
812:                                     score += 18
813:                                     log_message(
814:                                         f"  Metal pattern match: '{following_word}' (+18)"
815:                                     )
816:
817:                 elif word_lower == "tear":
818:                     # Crying indicators
819:                     cry_indicators = [
820:                         "eye",
821:                         "eyes",
822:                         "cry",
823:                         "crying",
824:                         "sad",
825:                         "weep",
826:                         "cheek",
827:                         "face",
828:                         "emotion",
829:                         "drop",
830:                         "roll",
831:                     ]
832:                     if any(indicator in context_lower for indicator in cry_indicators):
833:                         if "crying" in [tag.lower() for tag in tags] or "noun" in [
834:                             tag.lower() for tag in tags
835:                         ]:
836:                             score += 15
837:                             log_message(f"  Crying context match (+15)")
838:                     else:
839:                         # Ripping indicators
840:                         rip_indicators = [
841:                             "rip",
842:                             "torn",
843:                             "paper",
844:                             "fabric",
845:                             "cloth",
846:                             "apart",
847:                             "shred",
848:                         ]
849:                         if any(
850:                             indicator in context_lower for indicator in rip_indicators
851:                         ):
852:                             if "rip" in [tag.lower() for tag in tags] or "verb" in [
853:                                 tag.lower() for tag in tags
854:                             ]:
855:                                 score += 15
856:                                 log_message(f"  Ripping context match (+15)")
857:
858:                 elif word_lower == "wind":
859:                     # Air/weather indicators
860:                     air_indicators = [
861:                         "blow",
862:                         "blowing",
863:                         "breeze",
864:                         "storm",
865:                         "weather",
866:                         "air",
867:                         "gust",
868:                         "strong",
869:                         "feel",
870:                     ]
871:                     if any(indicator in context_lower for indicator in air_indicators):
872:                         if "air" in [tag.lower() for tag in tags] or "noun" in [
873:                             tag.lower() for tag in tags
874:                         ]:
875:                             score += 15
876:                             log_message(f"  Air/weather context match (+15)")
877:
878:                 elif word_lower == "live":
879:                     # Verb indicators (to live)
880:                     verb_indicators = [
881:                         "to",
882:                         "will",
883:                         "can",
884:                         "want",
885:                         "need",
886:                         "going",
887:                         "we",
888:                         "you",
889:                         "they",
890:                         "survive",
891:                         "exist",
892:                     ]
893:                     if any(indicator in context_lower for indicator in verb_indicators):
894:                         if "verb" in [tag.lower() for tag in tags] or "exist" in [
895:                             tag.lower() for tag in tags
896:                         ]:
897:                             score += 15
898:                             log_message(f"  Verb context match (+15)")
899:                     else:
900:                         # Adjective indicators (live broadcast)
901:                         adj_indicators = [
902:                             "broadcast",
903:                             "show",
904:                             "tv",
905:                             "radio",
906:                             "stream",
907:                             "recording",
908:                             "feed",
909:                         ]
910:                         if any(
911:                             indicator in context_lower for indicator in adj_indicators
912:                         ):
913:                             if "broadcast" in [
914:                                 tag.lower() for tag in tags
915:                             ] or "adj" in [tag.lower() for tag in tags]:
916:                                 score += 15
917:                                 log_message(f"  Broadcast context match (+15)")
918:
919:                 # Default scoring if no specific patterns found
920:                 if score == 0:
921:                     # Prefer first option as default
922:                     if spelling == tagged_options[0][0]:
923:                         score = 1
924:                         log_message(f"  Default first option (+1)")
925:
926:                 log_message(f"  Total score for '{spelling}': {score}")
927:
928:                 if score > best_score:
929:                     best_score = score
930:                     best_match = spelling
931:
932:             # If no scoring worked, fall back to first option
933:             if best_match is None and tagged_options:
934:                 best_match = tagged_options[0][0]
935:                 log_message(f"No context matches, using default: {best_match}")
936:
937:             log_message(f"Selected: {best_match} (score: {best_score})")
938:
939:             # Write detailed analysis to phonetic.txt debug file
940:             self._write_phonetic_debug(
941:                 word, context, tagged_options, best_match, best_score
942:             )
943:
944:             return best_match
945:
946:         except Exception as e:
947:             from ..logging import log_message
948:
949:             log_message(f"Error in phonetic disambiguation: {e}", level="ERROR")
950:             return tagged_options[0][0] if tagged_options else None
951:
952:     def _get_pronunciations(self, word: str) -> List[str]:
953:         """Get pronunciations for a word using CMU dictionary and g2p-en fallback."""
954:         pronunciations = []
955:
956:         try:
957:             # Built-in mode - return simple phonetic approximation
958:             if self.cmu_dict == "builtin":
959:                 return [f"[phonetic: {word.lower()}]"]
960:
961:             # Try CMU dictionary first
962:             if word.lower() in self.cmu_dict:
963:                 pronunciations = [
964:                     " ".join(pron) for pron in self.cmu_dict[word.lower()]
965:                 ]
966:
967:             # If not in CMU dict, use g2p-en for pronunciation generation
968:             if not pronunciations and self.g2p_model != "builtin":
969:                 g2p_result = self.g2p_model(word)
970:                 if g2p_result:
971:                     pronunciations = [" ".join(g2p_result)]
972:
973:         except Exception as e:
974:             from ..logging import log_message
975:
976:             log_message(
977:                 f"Error getting pronunciations for '{word}': {e}", level="ERROR"
978:             )
979:
980:         return pronunciations if pronunciations else ["[unknown]"]
981:
982:     def _write_phonetic_debug(
983:         self,
984:         word: str,
985:         context: str,
986:         tagged_options: List[Tuple[str, List[str]]],
987:         chosen: str,
988:         score: int,
989:     ):
990:         """Write detailed phonetic analysis to debug file."""
991:         try:
992:             import os
993:
994:             script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
995:             phonetic_path = os.path.join(script_dir, "phonetic.txt")
996:             with open(phonetic_path, "a", encoding="utf-8") as f:
997:                 f.write("=" * 80 + "\n")
998:                 f.write(f"WORD: {word}\n")
999:                 f.write(f"CHOSEN: {chosen} (score: {score})\n")
1000:                 f.write(f"CONTEXT: {context[:150]}...\n")
1001:                 f.write("\n")
1002:
1003:                 f.write(f"PHONETIC ANALYSIS:\n")
1004:                 for spelling, tags in tagged_options:
1005:                     pronunciations = self._get_pronunciations(spelling)
1006:                     f.write(
1007:                         f"  {spelling}: {pronunciations} (tags: {', '.join(tags)})\n"
1008:                     )
1009:                 f.write("\n")
1010:
1011:                 f.write(f"CONTEXT ANALYSIS:\n")
1012:                 context_lower = context.lower()
1013:                 word_lower = word.lower()
1014:
1015:                 if word_lower == "read":
1016:                     past_indicators = [
1017:                         "had",
1018:                         "have",
1019:                         "has",
1020:                         "was",
1021:                         "were",
1022:                         "been",
1023:                         "did",
1024:                         "yesterday",
1025:                         "ago",
1026:                         "last",
1027:                         "already",
1028:                         "before",
1029:                     ]
1030:                     present_indicators = [
1031:                         "to",
1032:                         "will",
1033:                         "can",
1034:                         "should",
1035:                         "must",
1036:                         "would",
1037:                         "could",
1038:                         "might",
1039:                     ]
1040:                     found_past = [
1041:                         ind for ind in past_indicators if ind in context_lower
1042:                     ]
1043:                     found_present = [
1044:                         ind for ind in present_indicators if ind in context_lower
1045:                     ]
1046:                     f.write(f"  Past indicators found: {found_past}\n")
1047:                     f.write(f"  Present indicators found: {found_present}\n")
1048:
1049:                 elif word_lower == "lead":
1050:                     metal_indicators = [
1051:                         "pipe",
1052:                         "pipes",
1053:                         "box",
1054:                         "sheet",
1055:                         "weight",
1056:                         "bullet",
1057:                         "paint",
1058:                         "poisoning",
1059:                         "heavy",
1060:                         "metal",
1061:                         "make-up",
1062:                         "makeup",
1063:                         "pencil",
1064:                         "shot",
1065:                         "ammunition",
1066:                         "roof",
1067:                         "plumbing",
1068:                         "crystal",
1069:                         "glass",
1070:                         "gasoline",
1071:                         "fuel",
1072:                         "based",
1073:                         "-based",
1074:                         "free",
1075:                         "content",
1076:                         "level",
1077:                     ]
1078:                     verb_indicators = [
1079:                         "to lead",
1080:                         "will lead",
1081:                         "can lead",
1082:                         "should lead",
1083:                         "must lead",
1084:                         "would lead",
1085:                         "could lead",
1086:                         "might lead",
1087:                         "does lead",
1088:                         "did lead",
1089:                         "leading",
1090:                         "leads to",
1091:                         "lead the",
1092:                         "lead a",
1093:                         "lead an",
1094:                     ]
1095:                     found_metal = [
1096:                         ind for ind in metal_indicators if ind in context_lower
1097:                     ]
1098:                     found_verb = [
1099:                         ind for ind in verb_indicators if ind in context_lower
1100:                     ]
1101:                     f.write(f"  Metal indicators found: {found_metal}\n")
1102:                     f.write(f"  Verb indicators found: {found_verb}\n")
1103:
1104:                     # Check for pattern matches
1105:                     import re
1106:
1107:                     lead_pattern = r"\blead\b\s*[-\s]*\w+"
1108:                     match = re.search(lead_pattern, context_lower)
1109:                     if match:
1110:                         following_word = (
1111:                             match.group().split()[-1]
1112:                             if len(match.group().split()) > 1
1113:                             else ""
1114:                         )
1115:                         f.write(
1116:                             f"  Pattern found: '{match.group()}' -> following word: '{following_word}'\n"
1117:                         )
1118:
1119:                 elif word_lower == "tear":
1120:                     cry_indicators = [
1121:                         "eye",
1122:                         "eyes",
1123:                         "cry",
1124:                         "crying",
1125:                         "sad",
1126:                         "weep",
1127:                         "cheek",
1128:                         "face",
1129:                         "emotion",
1130:                         "drop",
1131:                         "roll",
1132:                     ]
1133:                     rip_indicators = [
1134:                         "rip",
1135:                         "torn",
1136:                         "paper",
1137:                         "fabric",
1138:                         "cloth",
1139:                         "apart",
1140:                         "shred",
1141:                     ]
1142:                     found_cry = [ind for ind in cry_indicators if ind in context_lower]
1143:                     found_rip = [ind for ind in rip_indicators if ind in context_lower]
1144:                     f.write(f"  Crying indicators found: {found_cry}\n")
1145:                     f.write(f"  Ripping indicators found: {found_rip}\n")
1146:
1147:                 f.write("\n")
1148:
1149:         except Exception as e:
1150:             from ..logging import log_message
1151:
1152:             log_message(f"Error writing phonetic debug file: {e}", level="ERROR")
1153:
1154:     def get_phonetic_log_DISABLED(self) -> List[Dict]:
1155:         """Get the log of phonetic automatic changes - DISABLED."""
1156:         return []  # self.phonetic_log.copy()
1157:
1158:
1159: # Legacy function for backward compatibility
1160: def process_choices(ctx: "BookfixContext") -> "BookfixContext":
1161:     """
1162:     Legacy function for backward compatibility.
1163:
1164:     Note: This requires GUI callbacks to be set up properly.
1165:     """
1166:     processor = InteractiveChoiceProcessor()
1167:     return processor.process_choices(ctx)

(End of file - total 1167 lines)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 61.9s)

_Thinking:_

Now I have a comprehensive understanding of the system. Let me also check the pos_dictionary and dep_rules to understand the complex_pos rules better.

Now let me check the POS dictionary and dep_rules to understand complex_pos rules:

**Tool: task**

**Input:**
```json
{
  "subagent_type": "explore",
  "description": "Find dep_rules and pos_dictionary files",
  "prompt": "Search the BookFix project at /home/danno/MyApps/BookFix for files related to:\n1. dep_rules - complex POS dependency rules (likely in choices_pos_dictionary.json or a similar config)\n2. The pos_dictionary module (pos_dictionary.py) - especially the get_pronunciation_by_complex_pos_rules method and get_pronunciation_by_pos method\n3. choices.json - the homograph definitions file\n4. Any skip_choice or skip phrase configuration\n\nI need to understand:\n- What dep_rules look like (format and examples)\n- How complex_pos rules work vs simple POS rules\n- What skip phrases are configured\n- The structure of choices.json\n\nReturn the key findings: method signatures, rule formats, and any important logic."
}
```

**Output:**
```
<task id="ses_15bf32354ffe89o1v6AgZmqQMY" state="completed">
<task_result>
Now I have the complete picture. Here is a comprehensive summary of the findings:

---

## Key Findings

### 1. `dep_rules` Format and Examples

**File:** `/home/danno/MyApps/BookFix/.ai_learning/choices_pos_dictionary.json`

The `dep_rules` are an array of rule objects attached to each pronunciation option. Each rule object has a `type` and `values` (except `capitalized` which has no values).

**Rule types found in the codebase:**

| Type | Values | What it checks |
|------|--------|----------------|
| `dep_relation` | e.g. `["ROOT", "xcomp", "ccomp"]` | The token's dependency relation in the parse tree |
| `pos_category` | e.g. `["VERB"]`, `["NOUN"]`, `["ADJ"]` | The token's coarse POS category (UPOS) |
| `pos_tag` | e.g. `["VBD", "VBN"]` | The token's fine-grained POS tag |
| `prep_child` | e.g. `["of"]`, `["to", "before"]` | A child token with `dep_ == "prep"` whose text matches |
| `advmod_child` | e.g. `["respectfully", "humbly"]` | A child token with `dep_ == "advmod"` whose text matches |
| `cop_child` | (no values) | Any child token with `dep_ == "cop"` |
| `prev_token` | e.g. `["san", "don"]` | The immediately preceding token's text |
| `capitalized` | (no values) | Whether the word starts with uppercase |

**Concrete examples from the JSON:**

```json
// "bowed" → "boed" (bent by pressure) — match_mode: ANY
"dep_rules": [
  {"type": "pos_category", "values": ["ADJ"]},
  {"type": "dep_relation", "values": ["amod", "acomp", "advmod"]}
]

// "lead" → "leed" (to guide) — match_mode: ALL (both must match)
"dep_rules": [
  {"type": "pos_category", "values": ["VERB"]},
  {"type": "dep_relation", "values": ["ROOT", "xcomp", "ccomp", "advcl", "relcl"]}
]

// "recreation" → "re-kreation" (to create again) — no match_mode (defaults to "all")
"dep_rules": [
  {"type": "prep_child", "values": ["of"]}
]

// "polish" → "pole-ish" (relating to Poland) — checks capitalization
"dep_rules": [
  {"type": "capitalized"}
]

// "bass" → "bass" (fish) — uses prev_token
"dep_rules": [
  {"type": "prev_token", "values": ["striped", "largemouth", "smallmouth", "sea", "freshwater", "caught", "fishing"]}
]
```

**`match_mode`** controls how rules combine:
- `"all"` (default): ALL rules must match (logical AND)
- `"any"`: ANY rule matching is sufficient (logical OR)

---

### 2. `get_pronunciation_by_complex_pos_rules` vs `get_pronunciation_by_pos`

**File:** `/home/danno/MyApps/BookFix/bookfix/ai/pos_dictionary.py`

#### Simple POS: `get_pronunciation_by_pos(word, pos_tag) -> Optional[str]`

- Looks up the word in the dictionary, iterates over all pronunciation options, and finds which ones have the given `pos_tag` in their `pos_tags` array.
- Returns the pronunciation only if **exactly one** option matches. Returns `None` if zero or more than one match (ambiguous).
- This is the simple, non-structural disambiguation layer.

#### Complex POS: `get_pronunciation_by_complex_pos_rules(word, token, dep_info, doc) -> Optional[str]`

- A **data-driven** evaluator that reads `dep_rules` from the JSON and evaluates them against the spaCy parse tree.
- **First pass**: iterates over pronunciation options that have `dep_rules` defined (skips entries without them). For each, evaluates all rules and checks `match_mode` (`all` or `any`).
- If a match is found, returns that pronunciation immediately.
- If no `dep_rules` match, returns `None` — falling through to the simple `pos_tags` lookup.
- No hardcoded per-word logic; the rules are entirely declarative in the JSON.

#### Rule evaluation (`_evaluate_dep_rule`):

Each rule type is evaluated by the `_evaluate_dep_rule` method (lines 378-428 of `pos_dictionary.py`). Key logic:

- `capitalized`: checks `word[0].isupper()`
- `dep_relation`: checks `dep_info.dep_relation in values`
- `pos_category`: checks `token.pos_category in values`
- `pos_tag`: checks `token.pos_tag in values`
- `prep_child`: scans `doc` for children of the token with `dep_ == "prep"` whose text is in `values`
- `advmod_child`: scans `doc` for children with `dep_ == "advmod"` whose text is in `values`
- `cop_child`: scans `doc` for children with `dep_ == "cop"`
- `prev_token`: checks `doc[token.index - 1].text` is in `values`

---

### 3. Skip Choice Configuration

**File:** `/home/danno/MyApps/BookFix/data/skip_choice.txt`

The file contains context phrases (one per line) where the choice UI is skipped entirely — the user always picks the original spelling for these patterns.

**Format:** Plain text, one phrase per line, `#` for comments.

**Current skip phrases (107 lines, ~90 unique patterns):**

Most are adjective/adverb uses of **"close"** that should not trigger a verb choice:
- `close to`, `close enough`, `up-close`, `close proximity`, `close-up`, `close call`, `close attention`, `close range`, `close friend`, `close second`, `close-fitting`, `close-kit`, `close-cropped`, `close-trimmed`, etc.

Also includes:
- `present` phrases: `at present`, `the present`, `a present`, `be present`, `was present`, `present when`, `present state`, etc.
- `Jesus Christ` (always biblical)
- `refuse .` (punctuation context)
- `read a` (present tense context)
- A long sentence that was accidentally included: `"which results in a smaller review sample in shorter processing time."`

**Loading and usage:**
- Loaded in `bookfix/gui.py` (line 574) from `data/skip_choice.txt` into `ctx.skip_choice: List[str]`
- Checked in `bookfix/processors/ai_choices.py` (lines 676-699): for each homograph match, a 60-character window (30 chars before/after) is extracted, normalized, and tested against each skip phrase using substring matching. If any skip phrase appears in the window, the choice is skipped.
- Can be extended via the review window UI (`bookfix/ai/review_window.py`, `add_to_skip_choice` method).

---

### 4. Structure of `choices.json`

**File:** `/home/danno/MyApps/BookFix/data/choices.json`

This is the **single source of truth** for which words the homograph pipeline processes. It is a JSON **array** (not object) of 23 homograph entries.

**Schema per entry:**

```json
{
  "word": "close",                    // Surface form (case-insensitive)
  "options": [
    {
      "spelling": "close",            // Target replacement text
      "definition": "near or almost touching",
      "pos": "ADJECTIVE/ADVERB",      // Coarse POS (informational, not used for logic)
      "examples": ["The store is close to my house."],
      "context_keywords": ["hand", "very", "street", "finish", ...]
    },
    {
      "spelling": "cloze",
      "definition": "to shut something",
      "pos": "VERB",
      "examples": ["Please close the door."],
      "context_keywords": ["window", "shop", "room", ...]
    }
  ]
}
```

**Key fields per option:**
- `spelling` — the pronunciation hint / replacement text
- `definition` — human-readable meaning
- `pos` — coarse POS label (NOUN, VERB, ADJECTIVE, etc.) — informational
- `context_keywords` — words that signal this pronunciation in surrounding context
- `examples` — illustrative sentences

**Current homographs (23):** recreation, bowed, Jesus, lead, read, wound, live, object, close, record, records, present, sow, row, bass, resume, tear, refuse, polish, invalid, elaborate, estimate, wind.

**Adding a new homograph requires three steps** (documented in the JSON comments):
1. Add entry to `data/choices.json`
2. Add matching entry to `.ai_learning/choices_pos_dictionary.json` with `pos_tags`, `dep_rules`, `match_mode`
3. Add a `decide_<word>()` function in `bookfix/ai/hybrid_deciders.py` and register it in the `DECIDERS` dict

---

### 5. The Hybrid Decision Pipeline

**File:** `/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py`

Each of the 23 words has a dedicated `decide_<word>()` function that receives:
```python
def decide_word(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]
```

Returns `(pronunciation_spelling, route_explanation)`.

These are registered in the `DECIDERS` dict (line 381) and provide the **0.95 confidence hybrid path**. Words that need NLI (RoBERTa zero-shot) for hard cases are listed in `NLI_WORDS` (line 407): `row`, `bass`, `bowed`, `recreation`, `jesus`, `tear`, `lead`.

The decision layers are (in priority order):
1. **skip_choice** — context phrase match skips the word entirely
2. **REPLACE rules** — highest priority direct replacements
3. **Hybrid decider** (`decide_<word>`) — 0.95 confidence, POS + dependency + NLI
4. **Complex POS rules** (`get_pronunciation_by_complex_pos_rules`) — 0.98 confidence, data-driven dep_rules
5. **Simple POS** (`get_pronunciation_by_pos`) — basic tag-to-pronunciation mapping
6. **Context keywords** (`get_pronunciation_by_keywords`) — keyword matching in surrounding text (capped at 0.85 confidence)
7. **Semantic tags** (`get_pronunciation_by_semantic`) — semantic tag matching
8. **Entity detection** (`check_entity_context`) — spaCy NER-based
</task_result>
</task>
```

---

## Assistant (Plan · MiMo V2.5 Free · 20.4s)

_Thinking:_

Now I have all the information I need. Let me compress the earlier log file reading and create a comprehensive flowchart description for the user.

Now I have the full picture. Let me compress the earlier exploration and then deliver the flowchart.

**Tool: compress**

**Input:**
```json
{
  "topic": "Log file and code analysis",
  "content": [
    {
      "startId": "m0001",
      "endId": "m0011",
      "summary": "## Log File Analysis (m0001-m0005)\nRead `/home/danno/MyApps/BookFix/bookfix_ai_debug.log` (3725 lines). Key findings:\n- 23 homograph words loaded, only `choices` step enabled\n- AI provider: ollama, model: `qwen-big:latest ` (trailing space), mode: HYBRID\n- 7 items queued for AI due to hybrid-vs-pos disagreements: lead×3, tear×1, records×1, wind×2\n- **All AI requests failed**: every POST to `localhost:11434/api/generate` returned **HTTP 404** (21 attempts = 7 items × 3 retries)\n- After failure, system fell back silently — final stats: `complex_pos: 48, hybrid: 37, disagreement: 7`\n- Root cause: Ollama model not available or wrong endpoint\n\n## User's invalid Question (m0007)\nUser shared log for word 'invalid' — occurrence 2 of 2: `\"an [invalid].\"` \n- POS tag: JJ (adjective)\n- Hybrid decider: `in-valid` (pos-adj) — WRONG, should be noun form `invalid`\n- All 3 rules agreed on `in-valid`, no disagreement → no AI review triggered\n- The `decide_invalid` function's `pos-adj` fallback fires when `has_det` + dep not in `{nsubj, dobj, pobj, nsubjpass, attr, acomp, appos}` — for this case dep was likely something else, so it fell through to `pos-adj`\n\n## Code Files Read (m0009-m0011)\n### `bookfix/processors/ai_choices.py` (2331+ lines)\nMain class: `AIChoiceProcessor(InteractiveChoiceProcessor)`\n\n**`process_choices_ai_review_mode`** — main processing loop:\n1. For each word in `ctx.choices`, find all matches in text\n2. Check skip_phrase matches → skip if matched\n3. Extract single-sentence context\n4. Check REPLACE rules (highest priority, context phrase matching)\n5. Run `_run_all_rules()` → gets hybrid, complex_pos, pos, semantic, entity results\n6. `_get_consensus_from_rules()` determines outcome\n\n**`_run_all_rules`** runs in order:\n- Hybrid decider (0.95 conf) — if word in DECIDERS dict\n- Complex POS rules (0.98 conf) — data-driven dep_rules from choices_pos_dictionary.json\n- Simple POS (0.80 conf) — basic tag→pronunciation lookup\n- Semantic (variable conf) — keyword matching\n- Entity (0.85 conf) — NER context\n\n**`_get_consensus_from_rules`** decision logic:\n- Rules-only mode: confidence threshold check (0.75), defer if below\n- Hybrid/verify modes: `complex_pos` always wins (0.98)\n- **Disagreement gate**: if hybrid and pos disagree → queue for AI (returns None, \"disagreement\", hybrid as best_guess)\n- hybrid alone → use it (0.95)\n- pos alone with ≥0.80 conf → use it\n- Otherwise → queue for AI\n\n**AI batch processing**: items sent to Ollama in chunks of 10 via `analyze_homographs_batch`.\n\n### `bookfix/ai/hybrid_deciders.py` (407 lines)\n22 word-specific `decide_<word>()` functions registered in `DECIDERS` dict. NLI_WORDS (7 words need RoBERTa): row, bass, bowed, recreation, jesus, tear, lead.\n\n**`decide_invalid`** (the problem word):\n```python\ndef decide_invalid(tag, dep, head, has_det, nli, sentence):\n    if tag in ADJ_TAGS:\n        if dep == \"pobj\" and head == \"of\": return \"invalid\", \"jj-pobj-of-noun\"\n        if has_det and dep in {\"nsubj\", \"dobj\", \"pobj\", \"nsubjpass\", \"attr\", \"acomp\", \"appos\"}:\n            return \"invalid\", \"jj-but-noun\"\n        if dep in {\"attr\", \"acomp\", \"appos\"}: return \"invalid\", \"jj-attr-noun\"\n        return \"in-valid\", \"pos-adj\"  # ← FALLTHROUGH for unrecognized deps\n    return \"invalid\", \"pos-noun\"\n```\nThe bug: when POS=JJ but dep is not in the recognized sets (e.g. `ROOT`, `conj`, etc.), it falls through to `pos-adj` instead of `jj-attr-noun`.\n\n### `bookfix/processors/choices.py` (1167 lines)\nBase class `InteractiveChoiceProcessor` — handles GUI callbacks, highlighting, manual word-by-word processing. Largely legacy; AI processing overrides most of this."
    }
  ]
}
```

**Output:**
```
Compressed 11 messages into [Compressed conversation section].
```

---

## User

▣ DCP | -103.3K removed, +1.1K summary

│⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿████████│
▣ Compression #1 -103.3K removed, +1.1K summary
→ Topic: Log file and code analysis
→ Items: 11 messages and 9 tools compressed

---

## Assistant (Plan · MiMo V2.5 Free · 5.8s)

_Thinking:_

The user wants me to construct a flowchart of the `ai_choices.py` hybrid processing logic. I now have all the information I need from the compressed analysis. Let me also do a quick search to verify a few more details about the processing flow before presenting the comprehensive flowchart.

Let me read a few key methods to fill in any gaps in the flowchart.

Let me fill in a few more details from the actual code before presenting the full flowchart:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 640,
  "limit": 160
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
640:             )
641:             return None
642:
643:         items_for_ai_batch = []
644:         item_id_counter = 0
645:         match_map = {}
646:
647:         words_to_process = set(ctx.choices.keys())
648:         log_message(
649:             f"DEBUG: Total words to process: {len(words_to_process)}", level="DEBUG"
650:         )
651:         for word in words_to_process:
652:             log_message(f"DEBUG: Processing word: '{word}'", level="DEBUG")
653:             matches = self._find_matches(word, self.change_tracker.original_text)
654:             log_message(
655:                 f"DEBUG: Found {len(matches)} matches for '{word}'", level="DEBUG"
656:             )
657:             if not matches:
658:                 continue
659:
660:             log_message(f"DEBUG: Getting options for word: '{word}'", level="DEBUG")
661:             contextualized_options = ctx.contextualized_choices.get(word)
662:             regular_options = ctx.choices.get(word, [])
663:             options = regular_options or [
664:                 opt for opt, _ in (contextualized_options or [])
665:             ]
666:             if not options:
667:                 continue
668:
669:             for match_idx, match in enumerate(matches, 1):
670:                 detected_pos_tag = ""
671:                 log_message(
672:                     f"DEBUG: ─── '{word}' occurrence {match_idx}/{len(matches)} @ position {match.start()} ───",
673:                     level="DEBUG",
674:                 )
675:                 # Check if this match should be skipped based on context
676:                 if hasattr(ctx, "skip_choice") and ctx.skip_choice:
677:                     is_skipped = False
678:                     # Create a small window of text around the match, normalized for whitespace and case
679:                     window_start = max(0, match.start() - 30)
680:                     window_end = min(
681:                         len(self.change_tracker.original_text), match.end() + 30
682:                     )
683:                     text_window = self.change_tracker.original_text[
684:                         window_start:window_end
685:                     ]
686:                     normalized_window = " ".join(text_window.lower().split())
687:
688:                     for skip_phrase in ctx.skip_choice:
689:                         # Normalize the skip phrase as well
690:                         normalized_skip_phrase = " ".join(skip_phrase.lower().split())
691:                         if normalized_skip_phrase in normalized_window:
692:                             log_message(
693:                                 f"Skipping choice for '{word}' at position {match.start()} due to skip phrase match: '{skip_phrase}'"
694:                             )
695:                             is_skipped = True
696:                             break
697:
698:                     if is_skipped:
699:                         continue
700:
701:                 # --- Full Rule-Checking Logic ---
702:                 context_full = self._extract_context(
703:                     self.change_tracker.original_text,
704:                     match.start(),
705:                     match.end(),
706:                     self.context_size,
707:                     single_sentence=self.single_sentence_context,
708:                 )
709:
710:                 # --- Check for REPLACE rules first (highest priority) ---
711:                 # Split context to extract before/after, checking that split succeeds
712:                 context_parts = context_full.split(f"[{word}]")
713:                 if len(context_parts) == 2:
714:                     replace_rule_decision = self._check_replace_rules(
715:                         word, context_parts[0], context_parts[1], ctx
716:                     )
717:                     if replace_rule_decision:
718:                         pronunciation, explanation = replace_rule_decision
719:                         self.decision_stats["replace_rule"] += 1
720:
721:                         # Log REPLACE rule decision
722:                         short_ctx = self._extract_short_context(
723:                             self.change_tracker.original_text,
724:                             match.start(),
725:                             match.end(),
726:                             num_words=10,
727:                             replacement=pronunciation,
728:                         )
729:                         self._log_to_choices_log(
730:                             f"✓ DECISION: '{word}' → '{pronunciation}' | Rule: REPLACE (highest priority)"
731:                         )
732:                         self._log_to_choices_log(f"  Context: {short_ctx}")
733:                         self._log_to_choices_log(f"  Reason: {explanation}")
734:                         self._log_to_choices_log("")  # Blank line
735:
736:                         self._log_change(
737:                             match,
738:                             word,
739:                             options,
740:                             {
741:                                 "choice": pronunciation,
742:                                 "confidence": 1.0,
743:                                 "reason": explanation,
744:                             },
745:                             "replace_rule",
746:                             contextualized_options,
747:                             detected_pos_tag,
748:                         )
749:                         # Log comprehensive entry for REPLACE rule
750:                         replace_decision = {
751:                             "choice": pronunciation,
752:                             "confidence": 1.0,
753:                             "reason": explanation,
754:                         }
755:                         self._log_comprehensive_rule_entry(
756:                             word,
757:                             match,
758:                             {"replace_rule": replace_decision},
759:                             detected_pos_tag,
760:                             replace_decision,
761:                             "replace_rule",
762:                             options,
763:                         )
764:                         continue  # Skip all other rules and AI for this match
765:                 else:
766:                     log_message(
767:                         f"WARNING: context_full split failed for word '{word}'. Split returned {len(context_parts)} parts instead of 2.",
768:                         level="WARNING",
769:                     )
770:
771:                 # Store the single sentence for _log_rule_choice display
772:                 try:
773:                     _before, _w, _after = self._extract_sentence_context(
774:                         self.change_tracker.original_text, match.start(), match.end()
775:                     )
776:                     self._current_sentence = (_before + _w + _after).strip()
777:                 except Exception:
778:                     self._current_sentence = ""
779:
780:                 # Run all local rules
781:                 all_rules, detected_pos_tag = self._run_all_rules(
782:                     word, context_full, ctx
783:                 )
784:
785:                 # Initialize ai_decision and decision_source before conditional assignment
786:                 ai_decision = None
787:                 decision_source = None
788:
789:                 # Check for consensus
790:                 # Now returns 3-tuple to support disagreement gate: (decision, source, best_guess)
791:                 ai_decision, decision_source, best_guess = self._get_consensus_from_rules(
792:                     all_rules, context_full, word, options
793:                 )
794:
795:                 if ai_decision:
796:                     if self.ai_verify_all and self.ai_service:
797:                         # AI VERIFY ALL MODE: Rules produced a decision, but AI
798:                         # must verify EVERY decision per config. Queue the item
799:                         # for AI batch; store the rule decision as a safe fallback

(Showing lines 640-799 of 2594. Use offset=800 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 850,
  "limit": 200
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
850:
851:                         # Log the decision to the batch log with short context
852:                         short_ctx = self._extract_short_context(
853:                             self.change_tracker.original_text,
854:                             match.start(),
855:                             match.end(),
856:                             num_words=10,
857:                             replacement=ai_decision["choice"],
858:                         )
859:                         self._log_to_choices_log(
860:                             f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | Rule: {decision_source}"
861:                         )
862:                         self._log_to_choices_log(f"  Context: {short_ctx}")
863:                         self._log_to_choices_log(f"  Reason: {ai_decision['reason']}")
864:
865:                         # Log all rules that fired for transparency
866:                         if len(all_rules) > 1:
867:                             self._log_to_choices_log(f"  Other rules that fired:")
868:                             for rule_name, rule_data in all_rules.items():
869:                                 if rule_name != decision_source:
870:                                     self._log_to_choices_log(
871:                                         f"    - {rule_name}: '{rule_data['choice']}' | {rule_data['reason']}"
872:                                     )
873:                         self._log_to_choices_log("")  # Blank line for readability
874:
875:                         self._log_change(
876:                             match,
877:                             word,
878:                             options,
879:                             ai_decision,
880:                             decision_source,
881:                             contextualized_options,
882:                             detected_pos_tag,
883:                         )
884:                         # Log comprehensive entry for this word
885:                         self._log_comprehensive_rule_entry(
886:                             word,
887:                             match,
888:                             all_rules,
889:                             detected_pos_tag,
890:                             ai_decision,
891:                             decision_source,
892:                             options,
893:                         )
894:                 elif self.ai_enabled and self.ai_service:
895:                     # Disagreement gate (hybrid vs pos) uses the rich per-item prompt
896:                     # (definitions from choices.json + best_guess + GRAMMAR/KEYWORD CLUES)
897:                     # via _analyze_with_contextualized_ai + show_reasoning=True.
898:                     # All other "no consensus" cases still use efficient batch processing.
899:                     if decision_source == "disagreement" and best_guess is not None:
900:                         # --- DISAGREEMENT PATH: direct contextualized AI (rich prompt) ---
901:                         # This routes the exact ambiguous homograph cases to the verbose
902:                         # per-item analyzer so the model sees full dictionary meanings for
903:                         # the target word plus detected POS and context_keywords.
904:                         self._log_to_choices_log(
905:                             f"Disagreement (hybrid vs pos) for '{word}' — routing to contextualized AI (rich prompt + best_guess)."
906:                         )
907:                         self._log_rule_choice(word, "→ AI (contextualized)", 0.0, "disagreement→contextualized")
908:                         # best_guess is the hybrid dict from _get_consensus; extract the spelling string
909:                         bg = best_guess.get("choice") if isinstance(best_guess, dict) else best_guess
910:                         # Ensure list of (spelling, meaning) tuples for the call
911:                         ctx_opts = contextualized_options
912:                         if not ctx_opts:
913:                             meaning_map = {s: m for s, m in (contextualized_options or [])}
914:                             ctx_opts = [(s, meaning_map.get(s, s)) for s in options]
915:                         ai_decision = self._analyze_with_contextualized_ai(
916:                             word,
917:                             context_full,
918:                             ctx_opts,
919:                             show_reasoning=True,
920:                             best_guess=bg,
921:                             detected_pos_tag=detected_pos_tag,
922:                             context_keywords=None,  # auto-fetched inside from pos_dictionary
923:                         )
924:                         if ai_decision:
925:                             decision_source = "llm"
926:                             self.decision_stats[decision_source] += 1
927:                             short_ctx = self._extract_short_context(
928:                                 self.change_tracker.original_text,
929:                                 match.start(),
930:                                 match.end(),
931:                                 num_words=10,
932:                                 replacement=ai_decision["choice"],
933:                             )
934:                             self._log_to_choices_log(
935:                                 f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | AI: {decision_source} (contextualized)"
936:                             )
937:                             self._log_to_choices_log(f"  Context: {short_ctx}")
938:                             self._log_to_choices_log(f"  Reason: {ai_decision.get('reason', 'AI contextualized')}")
939:                             self._log_change(
940:                                 match,
941:                                 word,
942:                                 options,
943:                                 ai_decision,
944:                                 decision_source,
945:                                 contextualized_options,
946:                                 detected_pos_tag,
947:                             )
948:                             self._log_comprehensive_rule_entry(
949:                                 word,
950:                                 match,
951:                                 all_rules,
952:                                 detected_pos_tag,
953:                                 ai_decision,
954:                                 decision_source,
955:                                 options,
956:                             )
957:                         else:
958:                             # Contextualized AI failed — fall back to hybrid best_guess
959:                             # (this preserves the tuned hybrid decision for review)
960:                             fallback_choice = bg if bg else options[0]
961:                             ai_decision = {
962:                                 "choice": fallback_choice,
963:                                 "confidence": best_guess.get("confidence", 0.95) if isinstance(best_guess, dict) else 0.95,
964:                                 "reason": "hybrid best_guess fallback (contextualized AI failed)",
965:                             }
966:                             decision_source = "hybrid"
967:                             self.decision_stats[decision_source] += 1
968:                             self._log_rule_choice(
969:                                 word, ai_decision["choice"], ai_decision["confidence"], "disagreement→hybrid_fallback"
970:                             )
971:                             self._log_change(
972:                                 match,
973:                                 word,
974:                                 options,
975:                                 ai_decision,
976:                                 decision_source,
977:                                 contextualized_options,
978:                                 detected_pos_tag,
979:                             )
980:                             self._log_comprehensive_rule_entry(
981:                                 word,
982:                                 match,
983:                                 all_rules,
984:                                 detected_pos_tag,
985:                                 ai_decision,
986:                                 decision_source,
987:                                 options,
988:                             )
989:                     else:
990:                         # No rule consensus for non-disagreement cases → queue for AI batch
991:                         # (batch prompt uses REFERENCE EXAMPLES from choices.json for the word family)
992:                         self._log_to_choices_log(f"Queuing '{word}' for AI batch analysis.")
993:                         if all_rules:
994:                             _rules_summary = ", ".join(
995:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
996:                                 for r, v in all_rules.items()
997:                             )
998:                             _ai_reason = f"no consensus — rules fired: {_rules_summary}"
999:                         else:
1000:                             _ai_reason = (
1001:                                 f"no rules fired (POS: {detected_pos_tag or 'unknown'})"
1002:                             )
1003:                         self._log_rule_choice(word, "→ AI", 0.0, f"queued [{_ai_reason}]")
1004:                         item_id_counter += 1
1005:                         log_message(
1006:                             f"DEBUG: Queued item_id_counter: {item_id_counter}",
1007:                             level="DEBUG",
1008:                         )
1009:
1010:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
1011:                         rich_options = [
1012:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
1013:                             for s in options
1014:                         ]
1015:                         batch_item = {
1016:                             "id": item_id_counter,
1017:                             "word": word,
1018:                             "context": context_full,
1019:                             "options": rich_options,
1020:                         }
1021:                         items_for_ai_batch.append(batch_item)
1022:                         # Use best_guess (from disagreement) if present, else None
1023:                         fallback_decision = best_guess if best_guess is not None else None
1024:                         fallback_source = decision_source if decision_source else None
1025:                         match_map[item_id_counter] = (
1026:                             match,
1027:                             word,
1028:                             options,
1029:                             contextualized_options,
1030:                             detected_pos_tag,
1031:                             fallback_decision,  # rule fallback (hybrid on disagreement, else None)
1032:                             fallback_source,
1033:                         )
1034:                 else:
1035:                     # RULES-ONLY MODE: Force decision with zero confidence
1036:                     default_decision = None
1037:                     if self.rules_only_mode:
1038:                         # Use first option, force zero confidence
1039:                         forced_choice = options[0] if options else "UNKNOWN"
1040:                         forced_decision = {
1041:                             "choice": forced_choice,
1042:                             "confidence": 0.0,
1043:                             "reason": "Rules-only forced: using first option",
1044:                         }
1045:                         self.decision_stats["rules_only_forced"] += 1
1046:                         self._log_rule_choice(
1047:                             word, forced_choice, 0.0, "rules_only_main_loop"
1048:                         )
1049:                         self._log_change(

(Showing lines 850-1049 of 2594. Use offset=1050 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 3.3s)

_Thinking:_

Let me also read the `_run_all_rules` and `_get_consensus_from_rules` methods to make the flowchart accurate.

**Tool: grep**

**Input:**
```json
{
  "pattern": "def _run_all_rules|def _get_consensus_from_rules",
  "include": "*.py",
  "path": "/home/danno/MyApps/BookFix/bookfix/processors"
}
```

**Output:**
```
Found 2 matches
/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py:
  Line 1273:     def _run_all_rules(

  Line 1654:     def _get_consensus_from_rules(

```

---

## Assistant (Plan · MiMo V2.5 Free · 3.5s)

_Thinking:_

Let me read those two methods.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1273,
  "limit": 200
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1273:     def _run_all_rules(
1274:         self, word: str, context_full: str, ctx: "BookfixContext"
1275:     ) -> Tuple[Dict, str]:
1276:         """Helper to run all local rules and return their results and the detected POS tag."""
1277:         log_message(f"DEBUG: Entering _run_all_rules for word: '{word}'", level="DEBUG")
1278:         log_message(
1279:             f"DEBUG: _run_all_rules context_full: '{context_full}'", level="DEBUG"
1280:         )
1281:
1282:         all_rules = {}
1283:         detected_pos_tag = ""
1284:         pos_token = None
1285:         dep_info = None
1286:         doc = None
1287:
1288:         # Extract bracket context using case-insensitive match
1289:         import re
1290:
1291:         match = re.search(r"\[" + re.escape(word) + r"\]", context_full, re.IGNORECASE)
1292:         if not match:
1293:             log_message(
1294:                 f"DEBUG: _run_all_rules: bracket '[{word}]' not found in context_full",
1295:                 level="DEBUG",
1296:             )
1297:             return {}, ""
1298:         # Extract actual matched text to preserve original case (e.g., "Polish" not "polish")
1299:         actual_word_text = match.group()[1:-1]
1300:         bracket_start = match.start()
1301:         context_before = context_full[:bracket_start]
1302:         context_after = context_full[bracket_start + len(actual_word_text) + 2 :]
1303:         log_message(
1304:             f"DEBUG: _run_all_rules context_before: '{context_before}', context_after: '{context_after}'",
1305:             level="DEBUG",
1306:         )
1307:
1308:         if self.use_pos_tagging and self.pos_tagger:
1309:             log_message(
1310:                 f"DEBUG: _run_all_rules: Attempting POS tagging for '{word}'",
1311:                 level="DEBUG",
1312:             )
1313:             # Get rich spaCy context
1314:             try:
1315:                 pos_token, dep_info, doc = self.pos_tagger.get_token_and_dependency(
1316:                     context_before, word, context_after
1317:                 )
1318:                 if pos_token:
1319:                     detected_pos_tag = pos_token.pos_tag
1320:                     log_message(
1321:                         f"DEBUG: _run_all_rules: Detected POS tag for '{word}': '{detected_pos_tag}'",
1322:                         level="DEBUG",
1323:                     )
1324:                 else:
1325:                     log_message(
1326:                         f"DEBUG: _run_all_rules: No POS token found for '{word}'",
1327:                         level="DEBUG",
1328:                     )
1329:             except Exception as e:
1330:                 log_message(
1331:                     f"DEBUG: _run_all_rules: Error during POS tagging: {e}",
1332:                     level="DEBUG",
1333:                 )
1334:
1335:         # Hybrid decider check: if word has a specialized decider, use it
1336:         if word.lower() in DECIDERS and pos_token and dep_info and doc:
1337:             log_message(
1338:                 f"DEBUG: _run_all_rules: Using hybrid decider for '{word}'",
1339:                 level="DEBUG",
1340:             )
1341:             try:
1342:                 # Load NLI if needed for this word
1343:                 if word.lower() in NLI_WORDS:
1344:                     self._ensure_nli_services()
1345:
1346:                 # Extract sentence from context
1347:                 sentence = (
1348:                     context_before.rstrip()
1349:                     + " "
1350:                     + actual_word_text
1351:                     + " "
1352:                     + context_after.lstrip()
1353:                 )
1354:
1355:                 # Get parameters from spaCy structures
1356:                 tag = pos_token.pos_tag  # Fine-grained tag (VBN, NN, etc.)
1357:                 dep = dep_info.dep_relation  # Dependency relation (nsubj, dobj, etc.)
1358:                 head_text = dep_info.head_word.lower() if dep_info.head_word else ""
1359:
1360:                 # Check if word has a determiner child by checking the doc
1361:                 # Find the target token in the doc to check its children
1362:                 target_token_in_doc = None
1363:                 word_lower = word.lower()
1364:                 for token in doc:
1365:                     if token.text.lower() == word_lower and token.i == pos_token.index:
1366:                         target_token_in_doc = token
1367:                         break
1368:                 has_det = (
1369:                     any(c.dep_ == "det" for c in target_token_in_doc.children)
1370:                     if target_token_in_doc
1371:                     else False
1372:                 )
1373:
1374:                 # Call the hybrid decider
1375:                 decider_fn = DECIDERS[word.lower()]
1376:                 pronunciation, route = decider_fn(
1377:                     tag, dep, head_text, has_det, self.nli, sentence
1378:                 )
1379:
1380:                 all_rules["hybrid"] = {
1381:                     "choice": pronunciation,
1382:                     "confidence": 0.95,  # High confidence for hand-tuned deciders
1383:                     "reason": f"Hybrid decider ({route})",
1384:                 }
1385:                 log_message(
1386:                     f"DEBUG: _run_all_rules: Hybrid decider matched '{word}' → '{pronunciation}' ({route})",
1387:                     level="DEBUG",
1388:                 )
1389:                 self._log_rule_evaluation(
1390:                     word,
1391:                     "hybrid",
1392:                     f"Tag: {tag}, Dep: {dep}",
1393:                     f"Match: {pronunciation} ({route})",
1394:                 )
1395:
1396:             except Exception as e:
1397:                 log_message(
1398:                     f"DEBUG: _run_all_rules: Hybrid decider error for '{word}': {e}",
1399:                     level="DEBUG",
1400:                 )
1401:                 # Fall through to generic rules if hybrid fails
1402:
1403:         # Rule 1: Complex POS rules (e.g., imperative verbs)
1404:         if self.pos_dictionary and pos_token and dep_info and doc:
1405:             log_message(
1406:                 f"DEBUG: _run_all_rules: Checking complex POS rules for '{word}'",
1407:                 level="DEBUG",
1408:             )
1409:             try:
1410:                 complex_pos_result = (
1411:                     self.pos_dictionary.get_pronunciation_by_complex_pos_rules(
1412:                         actual_word_text, pos_token, dep_info, doc
1413:                     )
1414:                 )
1415:                 if complex_pos_result:
1416:                     all_rules["complex_pos"] = {
1417:                         "choice": complex_pos_result,
1418:                         "confidence": 0.98,
1419:                         "reason": f"Complex POS rule for '{word}'",
1420:                     }
1421:                     log_message(
1422:                         f"DEBUG: _run_all_rules: Complex POS rule matched: '{complex_pos_result}'",
1423:                         level="DEBUG",
1424:                     )
1425:                     self._log_rule_evaluation(
1426:                         word,
1427:                         "complex_pos",
1428:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1429:                         "Match" if complex_pos_result else "No match",
1430:                     )
1431:                 else:
1432:                     self._log_rule_evaluation(
1433:                         word,
1434:                         "complex_pos",
1435:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1436:                         "No match",
1437:                     )
1438:             except Exception as e:
1439:                 log_message(
1440:                     f"DEBUG: _run_all_rules: Error checking complex POS rules: {e}",
1441:                     level="DEBUG",
1442:                 )
1443:                 self._log_rule_evaluation(word, "complex_pos", "Error", str(e))
1444:
1445:         # Rule 2: Simple POS tagging (fallback if complex doesn't match)
1446:         log_message(
1447:             f"DEBUG: _run_all_rules: Checking simple POS rule for '{word}'",
1448:             level="DEBUG",
1449:         )
1450:         pos_result = self._get_pos_based_choice(word, context_before, context_after)
1451:         if pos_result:
1452:             pronunciation, confidence, explanation = pos_result
1453:             all_rules["pos"] = {
1454:                 "choice": pronunciation,
1455:                 "confidence": confidence,
1456:                 "reason": f"POS-based: {explanation} [Tag: {detected_pos_tag}]",
1457:             }
1458:             log_message(
1459:                 f"DEBUG: _run_all_rules: Simple POS rule matched: '{pronunciation}'",
1460:                 level="DEBUG",
1461:             )
1462:             self._log_rule_evaluation(
1463:                 word,
1464:                 "pos",
1465:                 f"POS: {detected_pos_tag}, Explanation: {explanation}",
1466:                 f"Match: {pronunciation}",
1467:             )
1468:         else:
1469:             self._log_rule_evaluation(
1470:                 word, "pos", f"POS: {detected_pos_tag}", "No match"
1471:             )
1472:

(Showing lines 1273-1472 of 2594. Use offset=1473 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1654,
  "limit": 250
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1654:     def _get_consensus_from_rules(
1655:         self, all_rules: Dict, context_full: str, word: str = "", options: List = None
1656:     ) -> Tuple[Optional[Dict], Optional[str], Optional[Dict]]:
1657:         """
1658:         Check for consensus among rule results.
1659:
1660:         Args:
1661:             all_rules: Dictionary of rule results
1662:             context_full: Full context around the word
1663:             word: The word being processed
1664:             options: List of available replacement options for this word
1665:
1666:         Returns:
1667:             Tuple of (decision_dict or None, source_str or None, best_guess_dict or None)
1668:             The third value carries a preferred rule decision (e.g. hybrid) to use
1669:             as best_guess when queuing to AI on disagreement.
1670:
1671:         Strategy:
1672:         1. If all rules agree on the same choice → consensus
1673:         2. If rules disagree:
1674:            - AI enabled → return None (send to AI)
1675:            - AI disabled → fall back to strict priority
1676:         3. If no rules matched → return None (or force in rules_only_mode)
1677:         4. NEW (hybrid mode): Disagreement gate — if complex_pos absent but
1678:            hybrid and pos both present and disagree on choice for a homograph
1679:            (word has hybrid decider), return None so caller queues to AI with
1680:            the hybrid choice as best_guess. This improves quality on ambiguous
1681:            spaCy parses without forcing verify_all globally.
1682:
1683:         NOTE: We intentionally avoid allowing a lower-priority rule (e.g. plain
1684:         'keyword') to win over higher-priority rules (complex_pos/entity/pos/
1685:         semantic) based solely on a slightly higher numeric confidence.
1686:         Additionally, **keyword-only** matches are treated as **no decision** so
1687:         they are always surfaced as low-confidence items for review (or sent to
1688:         AI), never as standalone rules.
1689:         """
1690:         # ===== RULES-ONLY MODE: Apply confidence floor, defer to review if below threshold =====
1691:         if self.rules_only_mode:
1692:             log_message(
1693:                 f"Rules-only mode: Checking decision for '{word}' (rules: {list(all_rules.keys()) if all_rules else 'none'})",
1694:                 level="DEBUG",
1695:             )
1696:             min_confidence = self.config.get("Thresholds", {}).get(
1697:                 "MIN_CONFIDENCE_THRESHOLD", 0.75
1698:             )
1699:             # Log to rule_choice log for tracking
1700:             if not all_rules:
1701:                 forced_choice = (
1702:                     options[0] if options and len(options) > 0 else "UNKNOWN"
1703:                 )
1704:                 self._log_rule_choice(word, forced_choice, 0.0, "rules_only_no_rules")
1705:                 return {
1706:                     "choice": forced_choice,
1707:                     "confidence": 0.0,
1708:                     "reason": "Rules-only: no rules",
1709:                 }, "rules_only", None
1710:             # Check if any rule meets confidence threshold
1711:             if all_rules:
1712:                 best_name = max(all_rules, key=lambda r: all_rules[r]["confidence"])
1713:                 best = all_rules[best_name]
1714:                 if best["confidence"] >= min_confidence:
1715:                     # Meets threshold - use with actual confidence
1716:                     best_copy = best.copy()
1717:                     best_copy["reason"] = f"Rules-only: {best['reason']}"
1718:                     self._log_rule_choice(
1719:                         word,
1720:                         best_copy["choice"],
1721:                         best_copy["confidence"],
1722:                         f"rules_only_{best_name}",
1723:                     )
1724:                     return best_copy, best_name, None
1725:                 else:
1726:                     # Below threshold - defer to review
1727:                     log_message(
1728:                         f"Rules-only mode: Confidence {best['confidence']:.2f} below threshold {min_confidence:.2f}, deferring to review",
1729:                         level="DEBUG",
1730:                     )
1731:                     return None, None, None
1732:             # Fallback
1733:             forced_choice = options[0] if options and len(options) > 0 else "UNKNOWN"
1734:             self._log_rule_choice(word, forced_choice, 0.0, "rules_only_fallback")
1735:             return {
1736:                 "choice": forced_choice,
1737:                 "confidence": 0.0,
1738:                 "reason": "Rules-only fallback",
1739:             }, "rules_only", None
1740:
1741:         # ===== HYBRID/VERIFY MODES: complex_pos > hybrid > pos; all others → AI =====
1742:         if not all_rules:
1743:             return None, None
1744:
1745:         # Rule 1: complex_pos (dep_rules) always wins — 0.98 confidence structural rule
1746:         if "complex_pos" in all_rules:
1747:             rule_decision = all_rules["complex_pos"]
1748:             self._log_rule_choice(
1749:                 word,
1750:                 rule_decision["choice"],
1751:                 rule_decision["confidence"],
1752:                 "complex_pos",
1753:             )
1754:             return rule_decision, "complex_pos", None
1755:
1756:         # Disagreement gate for hybrid/verify mode (only for the 23 homographs):
1757:         # If complex_pos is absent (no strong structural match) but both hybrid
1758:         # decider and simple POS produced choices that differ, do not auto-decide.
1759:         # Return None decision so the caller will queue to AI, passing the hybrid
1760:         # result as best_guess. This routes exactly the ambiguous cases (e.g. live
1761:         # tagged RB in relative clause, lead NN with possessive that NLI wants as
1762:         # guidance) to the LLM for better results while preserving fast rule path
1763:         # when the two agree.
1764:         # Controlled by config Thresholds.DISAGREEMENT_TO_AI (default True).
1765:         if (
1766:             "hybrid" in all_rules
1767:             and "pos" in all_rules
1768:         ):
1769:             hybrid_choice = all_rules["hybrid"]["choice"]
1770:             pos_choice = all_rules["pos"]["choice"]
1771:             if hybrid_choice != pos_choice:
1772:                 disagreement_flag = self.config.get("Thresholds", {}).get(
1773:                     "DISAGREEMENT_TO_AI", True
1774:                 )
1775:                 if disagreement_flag:
1776:                     fired = ", ".join(
1777:                         f"{k}={v['choice']}({v['confidence']:.2f})"
1778:                         for k, v in all_rules.items()
1779:                     )
1780:                     log_message(
1781:                         f"DEBUG: disagreement (hybrid vs pos) for '{word}' — queuing for AI. Rules fired: {fired}",
1782:                         level="DEBUG",
1783:                     )
1784:                     # Return None to force AI queue; attach hybrid as best_guess
1785:                     return None, "disagreement", all_rules["hybrid"]
1786:
1787:         # Rule 2: hybrid deciders — hand-tuned per-word logic, 0.95 confidence
1788:         if "hybrid" in all_rules:
1789:             rule_decision = all_rules["hybrid"]
1790:             self._log_rule_choice(
1791:                 word, rule_decision["choice"], rule_decision["confidence"], "hybrid"
1792:             )
1793:             return rule_decision, "hybrid", None
1794:
1795:         # Rule 3: POS tag — reliable only when pronunciations differ by part of speech
1796:         if "pos" in all_rules:
1797:             rule_decision = all_rules["pos"]
1798:             if rule_decision["confidence"] >= 0.80:
1799:                 self._log_rule_choice(
1800:                     word, rule_decision["choice"], rule_decision["confidence"], "pos"
1801:                 )
1802:                 return rule_decision, "pos", None
1803:
1804:         # Rules 4–7 (semantic, entity, definition, keyword) are not trusted to decide.
1805:         # Log which rules fired for diagnostics, then queue for AI.
1806:         fired = ", ".join(
1807:             f"{k}={v['choice']}({v['confidence']:.2f})" for k, v in all_rules.items()
1808:         )
1809:         log_message(
1810:             f"DEBUG: no autonomous decision — queuing for AI. Rules fired: {fired}",
1811:             level="DEBUG",
1812:         )
1813:         return None, None, None
1814:
1815:     def _log_rule_choice(
1816:         self, word: str, choice: str, confidence: float, rule_type: str
1817:     ):
1818:         """Log rule choices to separate file."""
1819:         import os, re
1820:
1821:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1822:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1823:         log_path = os.path.join(log_dir, "logs", "rules_choices.log")
1824:         sentence = getattr(self, "_current_sentence", "")
1825:         log_line = (
1826:             f"{word} -> {choice} (confidence {confidence:.2f}, rule: {rule_type})"
1827:         )
1828:         if sentence:
1829:             log_line += f" | {sentence}"
1830:         with open(log_path, "a", encoding="utf-8") as f:
1831:             f.write(log_line + "\n")
1832:
1833:     def _log_rule_evaluation(self, word: str, rule: str, details: str, result: str):
1834:         """Log each rule evaluation attempt."""
1835:         import os
1836:         import datetime
1837:
1838:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1839:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1840:         log_path = os.path.join(
1841:             log_dir, "logs", "rule_evaluation.log"
1842:         )  # Changed to separate file
1843:         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
1844:         with open(log_path, "a", encoding="utf-8") as f:
1845:             f.write(
1846:                 f"[{timestamp}] Word: '{word}' | Rule: {rule} | {details} | Result: {result}\n"
1847:             )
1848:
1849:     def _log_ai_choice(self, word: str, choice: str, confidence: float, reason: str):
1850:         """Log AI choices to separate file."""
1851:         import os
1852:
1853:         log_dir = os.path.dirname(os.path.abspath(__file__))
1854:         log_path = os.path.join(log_dir, "ai_choices.log")
1855:         with open(log_path, "w", encoding="utf-8") as f:
1856:             f.write(
1857:                 f"{word} -> {choice} (confidence {confidence:.2f}, reason: {reason})\n"
1858:             )
1859:             # AI disabled - use a simple majority if there is one, otherwise
1860:             # fall back to strict priority (no confidence-based tie-breaking).
1861:             from collections import Counter
1862:
1863:             vote_counts = Counter(choices)
1864:             most_common_choice, vote_count = vote_counts.most_common(1)[0]
1865:
1866:             total_votes = len(choices)
1867:             if vote_count > total_votes / 2:
1868:                 # Clear majority - find which rule suggested it (prefer higher priority)
1869:                 priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
1870:                 for rule_name in priority_order:
1871:                     if (
1872:                         rule_name in all_rules
1873:                         and all_rules[rule_name]["choice"] == most_common_choice
1874:                     ):
1875:                         consensus_decision = all_rules[rule_name].copy()
1876:                         consensus_decision["reason"] = (
1877:                             f"Consensus ({vote_count}/{total_votes} rules agree): {consensus_decision['reason']}"
1878:                         )
1879:                         return consensus_decision, f"consensus_{rule_name}"
1880:
1881:             # No clear majority (tie or even split) - fall back purely to
1882:             # strict priority order, ignoring confidence.
1883:             log_message(
1884:                 f"DEBUG: No clear consensus, using strict priority fallback",
1885:                 level="DEBUG",
1886:             )
1887:             priority_order = ["complex_pos", "entity", "pos", "semantic", "keyword"]
1888:             for rule_name in priority_order:
1889:                 if rule_name in all_rules:
1890:                     return all_rules[rule_name], rule_name
1891:
1892:         # Should never reach here, but safety fallback
1893:         return None, None
1894:
1895:     def _log_change(
1896:         self,
1897:         match,
1898:         word,
1899:         options,
1900:         decision,
1901:         decision_source,
1902:         contextualized_options,
1903:         detected_pos_tag: str,

(Showing lines 1654-1903 of 2594. Use offset=1904 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 3.1s)

_Thinking:_

Now let me also read the remaining rules (semantic, entity, keyword) to complete the flowchart.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1473,
  "limit": 180
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1473:         if self.pos_dictionary:
1474:             # Rule 3: Semantic matching
1475:             log_message(
1476:                 f"DEBUG: _run_all_rules: Checking semantic rule for '{word}'",
1477:                 level="DEBUG",
1478:             )
1479:             before_tokens = re.findall(r"\b\w+\b", context_before.lower())[-10:]
1480:             after_tokens = re.findall(r"\b\w+\b", context_after.lower())[:10]
1481:             try:
1482:                 semantic_result = self.pos_dictionary.get_pronunciation_by_semantic(
1483:                     word, before_tokens + after_tokens
1484:                 )
1485:                 if semantic_result:
1486:                     pronunciation, matched_tag, confidence = semantic_result
1487:                     all_rules["semantic"] = {
1488:                         "choice": pronunciation,
1489:                         "confidence": confidence,
1490:                         "reason": f"Semantic: nearby word '{matched_tag}'",
1491:                     }
1492:                     log_message(
1493:                         f"DEBUG: _run_all_rules: Semantic rule matched: '{pronunciation}'",
1494:                         level="DEBUG",
1495:                     )
1496:                     self._log_rule_evaluation(
1497:                         word,
1498:                         "semantic",
1499:                         f"Tokens: {before_tokens + after_tokens}",
1500:                         f"Match: {pronunciation} (tag: {matched_tag})",
1501:                     )
1502:                 else:
1503:                     self._log_rule_evaluation(
1504:                         word,
1505:                         "semantic",
1506:                         f"Tokens: {before_tokens + after_tokens}",
1507:                         "No match",
1508:                     )
1509:             except Exception as e:
1510:                 log_message(
1511:                     f"DEBUG: _run_all_rules: Error checking semantic rule: {e}",
1512:                     level="DEBUG",
1513:                 )
1514:                 self._log_rule_evaluation(word, "semantic", "Error", str(e))
1515:
1516:             # Rule 4: Named entity context
1517:             log_message(
1518:                 f"DEBUG: _run_all_rules: Checking entity rule for '{word}'",
1519:                 level="DEBUG",
1520:             )
1521:             try:
1522:                 entity_result = self.pos_dictionary.check_entity_context(
1523:                     word, context_before, context_after
1524:                 )
1525:                 if entity_result:
1526:                     all_rules["entity"] = {
1527:                         "choice": entity_result,
1528:                         "confidence": 0.85,
1529:                         "reason": f"Entity context: '{entity_result}'",
1530:                     }
1531:                     log_message(
1532:                         f"DEBUG: _run_all_rules: Entity rule matched: '{entity_result}'",
1533:                         level="DEBUG",
1534:                     )
1535:                     self._log_rule_evaluation(
1536:                         word,
1537:                         "entity",
1538:                         f"Context: {context_before} ... {context_after}",
1539:                         f"Match: {entity_result}",
1540:                     )
1541:                 else:
1542:                     self._log_rule_evaluation(
1543:                         word,
1544:                         "entity",
1545:                         f"Context: {context_before} ... {context_after}",
1546:                         "No match",
1547:                     )
1548:             except Exception as e:
1549:                 log_message(
1550:                     f"DEBUG: _run_all_rules: Error checking entity rule: {e}",
1551:                     level="DEBUG",
1552:                 )
1553:                 self._log_rule_evaluation(word, "entity", "Error", str(e))
1554:
1555:         log_message(
1556:             f"DEBUG: Exiting _run_all_rules for word: '{word}'. Found rules: {list(all_rules.keys())}",
1557:             level="DEBUG",
1558:         )
1559:         return all_rules, detected_pos_tag
1560:
1561:     def _log_comprehensive_rule_entry(
1562:         self,
1563:         word: str,
1564:         match,
1565:         all_rules: Dict,
1566:         detected_pos_tag: str,
1567:         decision: Dict,
1568:         decision_source: str,
1569:         options: List,
1570:     ):
1571:         """Log a comprehensive, readable entry for each word processed."""
1572:         import os
1573:         import datetime
1574:
1575:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1576:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1577:         log_path = os.path.join(log_dir, "logs", "rule_reasoning.log")
1578:
1579:         # Get single sentence context
1580:         full_text = self.change_tracker.original_text
1581:         match_start = match.start()
1582:         match_end = match.end()
1583:         context_before, word_in_sent, context_after = self._extract_sentence_context(
1584:             full_text, match_start, match_end
1585:         )
1586:         sentence = f"{context_before}[{word_in_sent}]{context_after}"
1587:
1588:         timestamp = datetime.datetime.now().strftime("%H:%M:%S")
1589:         confidence = decision.get("confidence", 0.0) if decision else 0.0
1590:         chosen = decision.get("choice", "UNKNOWN") if decision else "UNKNOWN"
1591:         reason = decision.get("reason", "") if decision else ""
1592:
1593:         with open(log_path, "a", encoding="utf-8") as f:
1594:             f.write(f'=== ENTRY: "{word}" @ {timestamp} ===\n')
1595:             f.write(f"Sentence: {sentence}\n")
1596:             f.write(f"POS: {detected_pos_tag}\n")
1597:             f.write(f"\nRULE RESULTS:\n")
1598:
1599:             # Log each rule that fired
1600:             if all_rules:
1601:                 for rule_name, rule_data in all_rules.items():
1602:                     rule_choice = rule_data.get("choice", "none")
1603:                     rule_conf = rule_data.get("confidence", 0.0)
1604:                     rule_reason = rule_data.get("reason", "")
1605:                     f.write(
1606:                         f"  {rule_name}: {rule_choice} (conf: {rule_conf:.2f}) - {rule_reason}\n"
1607:                     )
1608:             else:
1609:                 f.write(f"  No rules fired\n")
1610:
1611:             f.write(
1612:                 f"\nFINAL DECISION: {chosen} (confidence: {confidence:.2f}, source: {decision_source})\n"
1613:             )
1614:             f.write(f"  Reason: {reason}\n")
1615:             f.write(f"  Available options: {options}\n")
1616:
1617:             # Consensus explanation: show why winner beat runner-up
1618:             if all_rules and len(all_rules) > 0:
1619:                 sorted_rules = sorted(
1620:                     all_rules.items(),
1621:                     key=lambda x: x[1].get("confidence", 0.0),
1622:                     reverse=True,
1623:                 )
1624:                 winner_name, winner_data = sorted_rules[0]
1625:                 if all(r.get("choice") == chosen for _, r in all_rules.items()):
1626:                     f.write(
1627:                         f"  Consensus: unanimous — all {len(all_rules)} rules chose {chosen}\n"
1628:                     )
1629:                 elif decision_source in ("complex_pos", "replace_rule"):
1630:                     f.write(
1631:                         f"  Consensus: {decision_source} override ({confidence:.2f}) — structural rule takes priority\n"
1632:                     )
1633:                 elif len(sorted_rules) > 1:
1634:                     runner_name, runner_data = sorted_rules[1]
1635:                     margin = sorted_rules[0][1].get("confidence", 0.0) - sorted_rules[
1636:                         1
1637:                     ][1].get("confidence", 0.0)
1638:                     winner_choice = winner_data.get("choice", "?")
1639:                     runner_choice = runner_data.get("choice", "?")
1640:                     if winner_choice != runner_choice:
1641:                         f.write(
1642:                             f"  Consensus: {decision_source}({confidence:.2f}) beat {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f} — DISAGREEMENT\n"
1643:                         )
1644:                     else:
1645:                         f.write(
1646:                             f"  Consensus: {decision_source}({confidence:.2f}) selected over {runner_name}({runner_data.get('confidence', 0.0):.2f}) — margin: {margin:.2f}\n"
1647:                         )
1648:                 else:
1649:                     f.write(
1650:                         f"  Consensus: only rule — {decision_source}({confidence:.2f})\n"
1651:                     )
1652:             f.write("---\n")

(Showing lines 1473-1652 of 2594. Use offset=1653 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 3.2s)

_Thinking:_

Now let me also check the AI batch processing and the disagreement path to complete the flowchart.

Now let me read the AI batch processing and the contextualized AI path:

**Tool: grep**

**Input:**
```json
{
  "pattern": "def analyze_homographs_batch|def _analyze_with_contextualized_ai",
  "include": "*.py",
  "path": "/home/danno/MyApps/BookFix"
}
```

**Output:**
```
Found 4 matches
/home/danno/MyApps/BookFix/bookfix/ai/service.py:
  Line 685:     def analyze_homographs_batch(self, items: List[Dict], word_examples: Dict = None) -> Dict[int, AIResponse]:


/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py:
  Line 2193:     def _analyze_with_contextualized_ai(


/home/danno/MyApps/BookFix/export/bookfix/processors/ai_choices.py:
  Line 1753:     def _analyze_with_contextualized_ai(


/home/danno/MyApps/BookFix/export/bookfix/ai/service.py:
  Line 667:     def analyze_homographs_batch(self, items: List[Dict], word_examples: Dict = None) -> Dict[int, AIResponse]:

```

---

## Assistant (Plan · MiMo V2.5 Free · 5.2s)

_Thinking:_

Let me read the AI batch processing and the contextualized AI path to complete the flowchart.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/service.py",
  "offset": 685,
  "limit": 120
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/service.py</path>
<type>file</type>
<content>
685:     def analyze_homographs_batch(self, items: List[Dict], word_examples: Dict = None) -> Dict[int, AIResponse]:
686:         """
687:         Analyze a batch of homographs with a single AI call.
688:
689:         Args:
690:             items: A list of dictionaries, where each dict contains:
691:                    'id', 'word', 'context', 'options' (list of spellings)
692:             word_examples: Optional dict mapping word -> {spelling: [example sentences]}
693:
694:         Returns:
695:             A dictionary mapping each item's id to its AIResponse.
696:         """
697:         if not items:
698:             return {}
699:
700:         # Ollama can't reliably handle multi-item JSON batches — process one at a time
701:         if self.provider == "ollama" and len(items) > 1:
702:             all_decisions = {}
703:             for item in items:
704:                 original_id = item["id"]
705:                 # Remap to id=1 so AI always matches the prompt template example
706:                 remapped = dict(item)
707:                 remapped["id"] = 1
708:                 single_result = self.analyze_homographs_batch([remapped], word_examples)
709:                 if 1 in single_result:
710:                     all_decisions[original_id] = single_result[1]
711:             return all_decisions
712:
713:         log_message(
714:             f"\n=== ANALYZING HOMOGRAPH BATCH ({len(items)} items) ===", level="DEBUG"
715:         )
716:
717:         # Format the batch items for the prompt
718:         batch_items_text = []
719:         for item in items:
720:             # Use json.dumps to properly escape special characters
721:             item_dict = {
722:                 "id": item["id"],
723:                 "word": item["word"],
724:                 "context": item["context"],
725:                 "options": item["options"],  # Keep as a list, not a string
726:             }
727:             item_text = json.dumps(item_dict, ensure_ascii=False)
728:             batch_items_text.append(item_text)
729:
730:         # Build examples section from curated choices.json examples
731:         examples_section = ""
732:         if word_examples:
733:             lines = ["**REFERENCE EXAMPLES (correct usage for each word):**"]
734:             for word, spellings in sorted(word_examples.items()):
735:                 for spelling, examples in spellings.items():
736:                     for ex in examples:
737:                         lines.append(f'  {word} → "{spelling}": "{ex}"')
738:             examples_section = "\n".join(lines) + "\n"
739:
740:         batch_prompt = self._load_prompt("homograph_batch")
741:         if not batch_prompt:
742:             return {
743:                 item["id"]: AIResponse(False, "", 0.0, "Batch prompt not found.")
744:                 for item in items
745:             }
746:
747:         prompt = batch_prompt.replace("WORD_EXAMPLES", examples_section)
748:         prompt = prompt.replace("BATCH_ITEMS", "[\n" + ",\n".join(batch_items_text) + "\n]")
749:
750:         log_message(
751:             f"Batch prompt sent to AI (Provider: {self.provider}):\n{prompt}",
752:             level="DEBUG",
753:         )
754:
755:         # Build a map of item_id -> valid spellings for validation
756:         valid_spellings_by_id = {}
757:         for item in items:
758:             item_id = item["id"]
759:             valid_spellings = {opt["spelling"] for opt in item.get("options", [])}
760:             valid_spellings_by_id[item_id] = valid_spellings
761:
762:         response = self._make_request(prompt)
763:         decisions = {}
764:
765:         if response.success:
766:             try:
767:                 clean_response = response.content.strip()
768:                 if clean_response.startswith("```"):
769:                     lines = clean_response.split("\n")
770:                     if lines[0].startswith("```"):
771:                         lines = lines[1:]
772:                     if lines and lines[-1].strip() == "```":
773:                         lines = lines[:-1]
774:                     clean_response = "\n".join(lines).strip()
775:
776:                 # Fix invalid \' escape sequences Ollama emits for apostrophes in spellings
777:                 clean_response = clean_response.replace("\\'", "'")
778:
779:                 log_message(f"Raw AI batch response: {clean_response}", level="DEBUG")
780:                 batch_data = json.loads(clean_response)
781:
782:                 if not isinstance(batch_data, list):
783:                     raise ValueError("AI response is not a JSON array.")
784:
785:                 # Validate that list contains dicts
786:                 for idx, item in enumerate(batch_data):
787:                     if not isinstance(item, dict):
788:                         raise ValueError(
789:                             f"Item {idx} in batch response is not a dict: {type(item).__name__}"
790:                         )
791:
792:                 for result in batch_data:
793:                     item_id = result.get("id")
794:                     decision = result.get("decision", {})
795:                     choice = decision.get("choice")
796:                     reasoning = decision.get("reasoning", "")
797:
798:                     if item_id is not None and choice:
799:                         # Validate that the choice is one of the valid spellings
800:                         valid_spellings = valid_spellings_by_id.get(item_id, set())
801:                         if choice not in valid_spellings:
802:                             log_message(
803:                                 f"AI returned invalid choice '{choice}' for item {item_id}. Valid spellings: {valid_spellings}",
804:                                 level="WARNING",

(Showing lines 685-804 of 2050. Use offset=805 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 2193,
  "limit": 120
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
2193:     def _analyze_with_contextualized_ai(
2194:         self,
2195:         word: str,
2196:         context: str,
2197:         contextualized_options: List[Tuple[str, str]],
2198:         show_reasoning: Optional[bool] = None,
2199:         best_guess: Optional[str] = None,
2200:         detected_pos_tag: Optional[str] = None,
2201:         context_keywords: Optional[Dict[str, List[str]]] = None,
2202:     ) -> Optional[Dict]:
2203:         """
2204:         Analyze a word choice using AI with context definitions.
2205:
2206:         Args:
2207:             word: The word to analyze
2208:             context: Context around the word
2209:             contextualized_options: List of (spelling, meaning) tuples
2210:             show_reasoning: Override for self.show_reasoning if provided
2211:             best_guess: A preliminary guess from local rules to be verified by the AI
2212:             detected_pos_tag: POS tag from spaCy (VB, NN, etc.) - optional clue for AI
2213:             context_keywords: Dict mapping spelling to keywords indicating that pronunciation - optional clues
2214:
2215:         Returns:
2216:             Dictionary with AI decision or None if failed
2217:         """
2218:         try:
2219:             # Determine whether to show reasoning for this specific call
2220:             use_reasoning = (
2221:                 self.show_reasoning if show_reasoning is None else show_reasoning
2222:             )
2223:
2224:             # If POS tag not provided, try to detect it
2225:             if detected_pos_tag is None and self.pos_tagger is not None:
2226:                 context_before = (
2227:                     context[: context.rfind(word)] if word in context else ""
2228:                 )
2229:                 context_after = (
2230:                     context[context.rfind(word) + len(word) :]
2231:                     if word in context
2232:                     else ""
2233:                 )
2234:                 detected_pos_tag = self.pos_tagger.tag_with_context(
2235:                     context_before, word, context_after
2236:                 )
2237:                 if detected_pos_tag:
2238:                     log_message(
2239:                         f"DEBUG: Extracted POS tag for '{word}': {detected_pos_tag}",
2240:                         level="DEBUG",
2241:                     )
2242:
2243:             # If keywords not provided, try to extract them from dictionary
2244:             if context_keywords is None and self.pos_dictionary is not None:
2245:                 context_keywords = {}
2246:                 for spelling, _ in contextualized_options:
2247:                     option_info = self.pos_dictionary.get_option_info(word, spelling)
2248:                     if option_info:
2249:                         keywords = option_info.get("context_keywords", [])
2250:                         context_keywords[spelling] = keywords
2251:                         if keywords:
2252:                             log_message(
2253:                                 f"DEBUG: Found keywords for '{word}' → '{spelling}': {keywords}",
2254:                                 level="DEBUG",
2255:                             )
2256:                     else:
2257:                         context_keywords[spelling] = []
2258:
2259:             # Call AI service
2260:             response = self.ai_service.analyze_contextualized_homograph(
2261:                 word,
2262:                 context,
2263:                 contextualized_options,
2264:                 use_reasoning,
2265:                 best_guess=best_guess,
2266:                 detected_pos_tag=detected_pos_tag,
2267:                 context_keywords=context_keywords,
2268:             )
2269:
2270:             if response.success:
2271:                 return {
2272:                     "choice": response.content,
2273:                     "confidence": response.confidence,
2274:                     "reason": response.reasoning
2275:                     or f"AI chose {response.content} based on context",
2276:                 }
2277:             else:
2278:                 log_message(
2279:                     f"Contextualized AI analysis failed for '{word}': {response.error_message}"
2280:                 )
2281:                 return None
2282:
2283:         except Exception as e:
2284:             log_message(
2285:                 f"Contextualized AI analysis error for '{word}': {e}", level="ERROR"
2286:             )
2287:             return None
2288:
2289:     def _apply_ai_decision(self, ctx: "BookfixContext", match, decision: Dict) -> None:
2290:         """Apply an AI decision to the text."""
2291:         original_word = ctx.text[match.start() : match.end()]
2292:         replacement = decision["choice"]
2293:
2294:         # Replace in text
2295:         ctx.text = ctx.text[: match.start()] + replacement + ctx.text[match.end() :]
2296:
2297:         log_message(
2298:             f"AI replaced '{original_word}' with '{replacement}' (confidence: {decision['confidence']:.2f})"
2299:         )
2300:
2301:     def _process_manual_decisions(self, ctx: "BookfixContext") -> None:
2302:         """Process remaining decisions manually using the interactive processor."""
2303:         log_message(f"Processing {len(self.manual_decisions)} manual decisions")
2304:
2305:         # Create a temporary context with only the manual decisions
2306:         manual_ctx = type(ctx)()  # Create new context of same type
2307:         manual_ctx.text = ctx.text
2308:         manual_ctx.choices = {}
2309:
2310:         # Group manual decisions by word
2311:         for decision in self.manual_decisions:
2312:             word = decision["word"]

(Showing lines 2193-2312 of 2594. Use offset=2313 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 8.3s)

_Thinking:_

Now I have all the information I need to present the comprehensive flowchart. Let me also check the AI VERIFY ALL mode path to make sure I have the full picture.

Now let me check the AI VERIFY ALL path and the batch processing continuation:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 795,
  "limit": 55
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
795:                 if ai_decision:
796:                     if self.ai_verify_all and self.ai_service:
797:                         # AI VERIFY ALL MODE: Rules produced a decision, but AI
798:                         # must verify EVERY decision per config. Queue the item
799:                         # for AI batch; store the rule decision as a safe fallback
800:                         # so we don't lose work if the AI call fails.
801:                         self._log_to_choices_log(
802:                             f"Queuing '{word}' for AI verification (Verify ALL mode)."
803:                         )
804:                         if all_rules:
805:                             _rules_summary = ", ".join(
806:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
807:                                 for r, v in all_rules.items()
808:                             )
809:                             _ai_reason = f"rule consensus ({decision_source}); verify all — rules fired: {_rules_summary}"
810:                         else:
811:                             _ai_reason = (
812:                                 f"rule consensus ({decision_source}); verify all"
813:                             )
814:                         self._log_rule_choice(
815:                             word, "→ AI verify", 0.0, f"queued [{_ai_reason}]"
816:                         )
817:                         item_id_counter += 1
818:                         log_message(
819:                             f"DEBUG: Queued (verify_all) item_id_counter: {item_id_counter}",
820:                             level="DEBUG",
821:                         )
822:
823:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
824:                         rich_options = [
825:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
826:                             for s in options
827:                         ]
828:                         batch_item = {
829:                             "id": item_id_counter,
830:                             "word": word,
831:                             "context": context_full,
832:                             "options": rich_options,
833:                         }
834:                         items_for_ai_batch.append(batch_item)
835:                         # IMPORTANT: store the *original rule decision and source*
836:                         # so that if AI batch fails, we can fall back cleanly
837:                         # without changing the reported source.
838:                         match_map[item_id_counter] = (
839:                             match,
840:                             word,
841:                             options,
842:                             contextualized_options,
843:                             detected_pos_tag,
844:                             ai_decision,  # rule decision fallback dict
845:                             decision_source,  # e.g. "complex_pos", "hybrid", etc.
846:                         )
847:                     else:
848:                         # Rule-based decision was made, log it directly
849:                         self.decision_stats[decision_source] += 1

(Showing lines 795-849 of 2594. Use offset=850 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 30.2s)

_Thinking:_

Now I have all the information I need to present the comprehensive flowchart. Let me also check the batch processing continuation to see what happens after AI returns results.

Now I have all the pieces. Here is the **complete flowchart** of the `ai_choices.py` hybrid processing pipeline:

---

## AI Choices Processing Flowchart

### Main Loop: `process_choices_ai_review_mode`

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ For each word in ctx.choices             │
│   Find all regex matches in text        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ For each match occurrence               │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ SKIP CHECK   │ ← Extract 60-char window around match
        │ skip_choice  │   Normalize whitespace/case
        │ phrase match │   Compare against ~90 phrases
        └──────┬───────┘
               │
         Match? ──YES──→ SKIP (continue to next occurrence)
               │ NO
               ▼
        ┌──────────────┐
        │ Extract      │ ← context_full with [word] bracket
        │ context_full │
        └──────┬───────┘
               │
               ▼
        ┌──────────────────────────────────┐
        │ REPLACE RULE CHECK (highest prio)│ ← context.split("[word]")
        │ _check_replace_rules()           │   Check left/right context
        └──────┬───────────────────────────┘   against hardcoded phrases
               │
         Match? ──YES──→ APPLY (1.0 conf) → log + continue to next match
               │ NO
               ▼
        ┌──────────────────────────────────┐
        │ _run_all_rules()                 │
        │                                  │
        │  1. spaCy POS tagger             │ ← get_token_and_dependency()
        │     → pos_token, dep_info, doc   │
        │                                  │
        │  2. HYBRID DECIDER (if word in   │ ← decide_<word>(tag,dep,head,
        │     DECIDERS dict) → 0.95 conf   │   has_det, nli, sentence)
        │                                  │
        │  3. COMPLEX POS RULES            │ ← get_pronunciation_by_
        │     (dep_rules from JSON)→ 0.98  │   complex_pos_rules()
        │                                  │   Evaluates: dep_relation,
        │  4. SIMPLE POS TAG lookup        │   pos_category, pos_tag,
        │     (tag→pronunciation) → 0.80   │   prep_child, advmod_child,
        │                                  │   cop_child, prev_token,
        │  5. SEMANTIC MATCHING            │   capitalized
        │     (nearby keywords) → var conf │   match_mode: ALL or ANY
        │                                  │
        │  6. ENTITY CONTEXT               │
        │     (NER check) → 0.85 conf      │
        └──────┬───────────────────────────┘
               │
               ▼ all_rules dict populated
        ┌──────────────────────────────────┐
        │ _get_consensus_from_rules()      │
        └──────┬───────────────────────────┘
               │
    ┌──────────┴──────────────────────────┐
    │                                     │
    ▼ RULES-ONLY MODE                     ▼ HYBRID/VERIFY MODE
┌──────────────────┐               ┌──────────────────────────┐
│ Best rule conf   │               │ ① complex_pos present?   │
│ ≥ 0.75 threshold?│               │   YES → USE IT (0.98)    │
│                  │               │                           │
│ YES → use best   │               │ ② hybrid + pos BOTH       │
│ NO  → defer(→review)            │   present & DISAGREE?     │
│ None → force     │               │   YES → DISAGREEMENT GATE │
│  first option    │               │   (return None, "disagg", │
└──────────────────┘               │    hybrid as best_guess)  │
                                   │                           │
                                   │ ③ hybrid alone present?   │
                                   │   YES → USE IT (0.95)     │
                                   │                           │
                                   │ ④ pos alone, conf ≥ 0.80?│
                                   │   YES → USE IT            │
                                   │                           │
                                   │ ⑤ Otherwise → None        │
                                   │   (no decision)           │
                                   └──────────┬───────────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
                        ▼                     ▼                     ▼
                  ┌──────────┐         ┌──────────┐         ┌──────────┐
                  │ ai_decision │      │ decision_source  │  │ best_guess│
                  │ = dict    │         │ = "hybrid" etc  │  │ = hybrid │
                  │           │         │                  │  │  dict    │
                  └─────┬────┘         └──────────┘       └──────────┘
                        │
              ┌─────────┴─────────────────────────┐
              │                                   │
              ▼                                   ▼
    ┌──────────────────┐              ┌─────────────────────┐
    │ AI VERIFY ALL?   │              │ ai_decision = None  │
    │ (self.ai_verify  │              │ (no consensus)      │
    │  _all = True)    │              └─────────┬───────────┘
    └────────┬─────────┘                        │
             │                            ┌─────┴──────────┐
      YES    │    NO                      │                │
      ▼      ▼                           ▼                ▼
  ┌────────┐ ┌───────────────┐   ┌──────────────┐  ┌──────────────┐
  │ QUEUE  │ │ APPLY RULE    │   │ disagreement?│  │ Other no-    │
  │ for AI │ │ DECISION      │   │ source ==    │  │ consensus    │
  │ batch  │ │ directly      │   │ "disagg" &   │  │              │
  │ (store │ │ log + stats   │   │ best_guess?  │  └──────┬───────┘
  │ rule   │ └───────────────┘   └──────┬───────┘         │
  │ as     │                            │                 │
  │fallback│                     YES    │    NO           │
  └────────┘                     ▼      │    ▼            │
                               ┌────────┴──┐  ┌──────────┐
                               │CONTEXTUAL-│  │ QUEUE    │
                               │IZED AI    │  │ for AI   │
                               │(rich      │  │ BATCH    │
                               │ prompt)   │  │ (efficient│
                               │ per-item  │  │  batch   │
                               │ +defs +   │  │  prompt) │
                               │ POS +     │  └────┬─────┘
                               │ keywords  │       │
                               │ +best_    │       │
                               │ guess)    │       │
                               └─────┬─────┘       │
                                     │             │
                            ┌────────┴────────┐    │
                            │                 │    │
                     SUCCESS│          FAIL   │    │
                            ▼                 ▼    │
                   ┌────────────┐    ┌─────────┐   │
                   │ USE AI     │    │FALLBACK │   │
                   │ DECISION   │    │to hybrid│   │
                   │ (source=   │    │best_    │   │
                   │  "llm")    │    │guess    │   │
                   └────────────┘    └─────────┘   │
                                                   │
              ┌────────────────────────────────────┘
              │
              ▼
   ┌──────────────────────────┐
   │ AI BATCH PROCESSING      │
   │                          │
   │ Collect all queued items │
   │ (chunks of 10)           │
   │                          │
   │ analyze_homographs_batch │
   │ → Ollama: 1-at-a-time   │
   │ → Other: true batching   │
   │                          │
   │ For each item:           │
   │  • Send prompt with      │
   │    choices.json examples │
   │  • Parse JSON response   │
   │  • Validate spelling     │
   │    against valid options │
   └──────────┬───────────────┘
              │
        ┌─────┴─────┐
        │           │
   SUCCESS      FAIL
        │           │
        ▼           ▼
  ┌──────────┐ ┌──────────────┐
  │ USE AI   │ │ FALLBACK to  │
  │ decision │ │ stored rule  │
  │ (source= │ │ decision     │
  │  "llm")  │ │ (source=     │
  └──────────┘ │  original)   │
               └──────────────┘
```

### Summary of Rule Priority (Hybrid/Verify Mode)

| Priority | Rule | Confidence | When it wins |
|----------|------|-----------|-------------|
| 1 | REPLACE rules | 1.0 | Context phrase matches (checked first) |
| 2 | complex_pos (dep_rules) | 0.98 | Structural dep rules from JSON match |
| 3 | **Disagreement gate** | — | hybrid & pos disagree → AI queue |
| 4 | hybrid (decide_\<word\>) | 0.95 | Only hybrid fired, or hybrid+pos agree |
| 5 | pos (simple tag lookup) | 0.80 | Only pos fired, conf ≥ 0.80 |
| 6 | AI (contextualized) | var | Disagreement path — rich prompt |
| 7 | AI (batch) | var | No consensus — batch prompt |

### Key Data Flows

- **skip_choice.txt** → loaded into `ctx.skip_choice` → substring match in 60-char window
- **choices.json** → provides word definitions, examples, context_keywords → passed to AI prompts
- **choices_pos_dictionary.json** → dep_rules (dep_relation, pos_category, pos_tag, prep_child, etc.) → evaluated by complex_pos engine
- **hybrid_deciders.py** → 22 `decide_<word>()` functions → receive (tag, dep, head, has_det, nli, sentence) → return (pronunciation, route)
- **NLI_WORDS** (7 words: row, bass, bowed, recreation, jesus, tear, lead) → require RoBERTa zero-shot for hard cases




---

## User

the code updated. please update your output.

---

## Assistant (Plan · MiMo V2.5 Free · 6.7s)

_Thinking:_

The user is saying the code has been updated and wants me to re-read the relevant files to update the flowchart. Let me re-read the key files to see what changed.

Let me re-read the key files to see what changed.

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 640,
  "limit": 420
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
640:             )
641:             return None
642:
643:         items_for_ai_batch = []
644:         item_id_counter = 0
645:         match_map = {}
646:
647:         words_to_process = set(ctx.choices.keys())
648:         log_message(
649:             f"DEBUG: Total words to process: {len(words_to_process)}", level="DEBUG"
650:         )
651:         for word in words_to_process:
652:             log_message(f"DEBUG: Processing word: '{word}'", level="DEBUG")
653:             matches = self._find_matches(word, self.change_tracker.original_text)
654:             log_message(
655:                 f"DEBUG: Found {len(matches)} matches for '{word}'", level="DEBUG"
656:             )
657:             if not matches:
658:                 continue
659:
660:             log_message(f"DEBUG: Getting options for word: '{word}'", level="DEBUG")
661:             contextualized_options = ctx.contextualized_choices.get(word)
662:             regular_options = ctx.choices.get(word, [])
663:             options = regular_options or [
664:                 opt for opt, _ in (contextualized_options or [])
665:             ]
666:             if not options:
667:                 continue
668:
669:             for match_idx, match in enumerate(matches, 1):
670:                 detected_pos_tag = ""
671:                 log_message(
672:                     f"DEBUG: ─── '{word}' occurrence {match_idx}/{len(matches)} @ position {match.start()} ───",
673:                     level="DEBUG",
674:                 )
675:                 # Check if this match should be skipped based on context
676:                 if hasattr(ctx, "skip_choice") and ctx.skip_choice:
677:                     is_skipped = False
678:                     # Create a small window of text around the match, normalized for whitespace and case
679:                     window_start = max(0, match.start() - 30)
680:                     window_end = min(
681:                         len(self.change_tracker.original_text), match.end() + 30
682:                     )
683:                     text_window = self.change_tracker.original_text[
684:                         window_start:window_end
685:                     ]
686:                     normalized_window = " ".join(text_window.lower().split())
687:
688:                     for skip_phrase in ctx.skip_choice:
689:                         # Normalize the skip phrase as well
690:                         normalized_skip_phrase = " ".join(skip_phrase.lower().split())
691:                         if normalized_skip_phrase in normalized_window:
692:                             log_message(
693:                                 f"Skipping choice for '{word}' at position {match.start()} due to skip phrase match: '{skip_phrase}'"
694:                             )
695:                             is_skipped = True
696:                             break
697:
698:                     if is_skipped:
699:                         continue
700:
701:                 # --- Full Rule-Checking Logic ---
702:                 context_full = self._extract_context(
703:                     self.change_tracker.original_text,
704:                     match.start(),
705:                     match.end(),
706:                     self.context_size,
707:                     single_sentence=self.single_sentence_context,
708:                 )
709:
710:                 # --- Check for REPLACE rules first (highest priority) ---
711:                 # Split context to extract before/after, checking that split succeeds
712:                 context_parts = context_full.split(f"[{word}]")
713:                 if len(context_parts) == 2:
714:                     replace_rule_decision = self._check_replace_rules(
715:                         word, context_parts[0], context_parts[1], ctx
716:                     )
717:                     if replace_rule_decision:
718:                         pronunciation, explanation = replace_rule_decision
719:                         self.decision_stats["replace_rule"] += 1
720:
721:                         # Log REPLACE rule decision
722:                         short_ctx = self._extract_short_context(
723:                             self.change_tracker.original_text,
724:                             match.start(),
725:                             match.end(),
726:                             num_words=10,
727:                             replacement=pronunciation,
728:                         )
729:                         self._log_to_choices_log(
730:                             f"✓ DECISION: '{word}' → '{pronunciation}' | Rule: REPLACE (highest priority)"
731:                         )
732:                         self._log_to_choices_log(f"  Context: {short_ctx}")
733:                         self._log_to_choices_log(f"  Reason: {explanation}")
734:                         self._log_to_choices_log("")  # Blank line
735:
736:                         self._log_change(
737:                             match,
738:                             word,
739:                             options,
740:                             {
741:                                 "choice": pronunciation,
742:                                 "confidence": 1.0,
743:                                 "reason": explanation,
744:                             },
745:                             "replace_rule",
746:                             contextualized_options,
747:                             detected_pos_tag,
748:                         )
749:                         # Log comprehensive entry for REPLACE rule
750:                         replace_decision = {
751:                             "choice": pronunciation,
752:                             "confidence": 1.0,
753:                             "reason": explanation,
754:                         }
755:                         self._log_comprehensive_rule_entry(
756:                             word,
757:                             match,
758:                             {"replace_rule": replace_decision},
759:                             detected_pos_tag,
760:                             replace_decision,
761:                             "replace_rule",
762:                             options,
763:                         )
764:                         continue  # Skip all other rules and AI for this match
765:                 else:
766:                     log_message(
767:                         f"WARNING: context_full split failed for word '{word}'. Split returned {len(context_parts)} parts instead of 2.",
768:                         level="WARNING",
769:                     )
770:
771:                 # Store the single sentence for _log_rule_choice display
772:                 try:
773:                     _before, _w, _after = self._extract_sentence_context(
774:                         self.change_tracker.original_text, match.start(), match.end()
775:                     )
776:                     self._current_sentence = (_before + _w + _after).strip()
777:                 except Exception:
778:                     self._current_sentence = ""
779:
780:                 # Run all local rules
781:                 all_rules, detected_pos_tag = self._run_all_rules(
782:                     word, context_full, ctx
783:                 )
784:
785:                 # Initialize ai_decision and decision_source before conditional assignment
786:                 ai_decision = None
787:                 decision_source = None
788:
789:                 # Check for consensus
790:                 # Now returns 3-tuple to support disagreement gate: (decision, source, best_guess)
791:                 ai_decision, decision_source, best_guess = self._get_consensus_from_rules(
792:                     all_rules, context_full, word, options
793:                 )
794:
795:                 if ai_decision:
796:                     if self.ai_verify_all and self.ai_service:
797:                         # AI VERIFY ALL MODE: Rules produced a decision, but AI
798:                         # must verify EVERY decision per config. Queue the item
799:                         # for AI batch; store the rule decision as a safe fallback
800:                         # so we don't lose work if the AI call fails.
801:                         self._log_to_choices_log(
802:                             f"Queuing '{word}' for AI verification (Verify ALL mode)."
803:                         )
804:                         if all_rules:
805:                             _rules_summary = ", ".join(
806:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
807:                                 for r, v in all_rules.items()
808:                             )
809:                             _ai_reason = f"rule consensus ({decision_source}); verify all — rules fired: {_rules_summary}"
810:                         else:
811:                             _ai_reason = (
812:                                 f"rule consensus ({decision_source}); verify all"
813:                             )
814:                         self._log_rule_choice(
815:                             word, "→ AI verify", 0.0, f"queued [{_ai_reason}]"
816:                         )
817:                         item_id_counter += 1
818:                         log_message(
819:                             f"DEBUG: Queued (verify_all) item_id_counter: {item_id_counter}",
820:                             level="DEBUG",
821:                         )
822:
823:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
824:                         rich_options = [
825:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
826:                             for s in options
827:                         ]
828:                         batch_item = {
829:                             "id": item_id_counter,
830:                             "word": word,
831:                             "context": context_full,
832:                             "options": rich_options,
833:                         }
834:                         items_for_ai_batch.append(batch_item)
835:                         # IMPORTANT: store the *original rule decision and source*
836:                         # so that if AI batch fails, we can fall back cleanly
837:                         # without changing the reported source.
838:                         match_map[item_id_counter] = (
839:                             match,
840:                             word,
841:                             options,
842:                             contextualized_options,
843:                             detected_pos_tag,
844:                             ai_decision,  # rule decision fallback dict
845:                             decision_source,  # e.g. "complex_pos", "hybrid", etc.
846:                         )
847:                     else:
848:                         # Rule-based decision was made, log it directly
849:                         self.decision_stats[decision_source] += 1
850:
851:                         # Log the decision to the batch log with short context
852:                         short_ctx = self._extract_short_context(
853:                             self.change_tracker.original_text,
854:                             match.start(),
855:                             match.end(),
856:                             num_words=10,
857:                             replacement=ai_decision["choice"],
858:                         )
859:                         self._log_to_choices_log(
860:                             f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | Rule: {decision_source}"
861:                         )
862:                         self._log_to_choices_log(f"  Context: {short_ctx}")
863:                         self._log_to_choices_log(f"  Reason: {ai_decision['reason']}")
864:
865:                         # Log all rules that fired for transparency
866:                         if len(all_rules) > 1:
867:                             self._log_to_choices_log(f"  Other rules that fired:")
868:                             for rule_name, rule_data in all_rules.items():
869:                                 if rule_name != decision_source:
870:                                     self._log_to_choices_log(
871:                                         f"    - {rule_name}: '{rule_data['choice']}' | {rule_data['reason']}"
872:                                     )
873:                         self._log_to_choices_log("")  # Blank line for readability
874:
875:                         self._log_change(
876:                             match,
877:                             word,
878:                             options,
879:                             ai_decision,
880:                             decision_source,
881:                             contextualized_options,
882:                             detected_pos_tag,
883:                         )
884:                         # Log comprehensive entry for this word
885:                         self._log_comprehensive_rule_entry(
886:                             word,
887:                             match,
888:                             all_rules,
889:                             detected_pos_tag,
890:                             ai_decision,
891:                             decision_source,
892:                             options,
893:                         )
894:                 elif self.ai_enabled and self.ai_service:
895:                     # Disagreement gate (hybrid vs pos) uses the rich per-item prompt
896:                     # (definitions from choices.json + best_guess + GRAMMAR/KEYWORD CLUES)
897:                     # via _analyze_with_contextualized_ai + show_reasoning=True.
898:                     # All other "no consensus" cases still use efficient batch processing.
899:                     if decision_source == "disagreement" and best_guess is not None:
900:                         # --- DISAGREEMENT PATH: direct contextualized AI (rich prompt) ---
901:                         # This routes the exact ambiguous homograph cases to the verbose
902:                         # per-item analyzer so the model sees full dictionary meanings for
903:                         # the target word plus detected POS and context_keywords.
904:                         self._log_to_choices_log(
905:                             f"Disagreement (hybrid vs pos) for '{word}' — routing to contextualized AI (rich prompt + best_guess)."
906:                         )
907:                         self._log_rule_choice(word, "→ AI (contextualized)", 0.0, "disagreement→contextualized")
908:                         # best_guess is the hybrid dict from _get_consensus; extract the spelling string
909:                         bg = best_guess.get("choice") if isinstance(best_guess, dict) else best_guess
910:                         # Ensure list of (spelling, meaning) tuples for the call
911:                         ctx_opts = contextualized_options
912:                         if not ctx_opts:
913:                             meaning_map = {s: m for s, m in (contextualized_options or [])}
914:                             ctx_opts = [(s, meaning_map.get(s, s)) for s in options]
915:                         ai_decision = self._analyze_with_contextualized_ai(
916:                             word,
917:                             context_full,
918:                             ctx_opts,
919:                             show_reasoning=True,
920:                             best_guess=bg,
921:                             detected_pos_tag=detected_pos_tag,
922:                             context_keywords=None,  # auto-fetched inside from pos_dictionary
923:                         )
924:                         if ai_decision:
925:                             decision_source = "llm"
926:                             self.decision_stats[decision_source] += 1
927:                             short_ctx = self._extract_short_context(
928:                                 self.change_tracker.original_text,
929:                                 match.start(),
930:                                 match.end(),
931:                                 num_words=10,
932:                                 replacement=ai_decision["choice"],
933:                             )
934:                             self._log_to_choices_log(
935:                                 f"✓ DECISION: '{word}' → '{ai_decision['choice']}' | AI: {decision_source} (contextualized)"
936:                             )
937:                             self._log_to_choices_log(f"  Context: {short_ctx}")
938:                             self._log_to_choices_log(f"  Reason: {ai_decision.get('reason', 'AI contextualized')}")
939:                             self._log_change(
940:                                 match,
941:                                 word,
942:                                 options,
943:                                 ai_decision,
944:                                 decision_source,
945:                                 contextualized_options,
946:                                 detected_pos_tag,
947:                             )
948:                             self._log_comprehensive_rule_entry(
949:                                 word,
950:                                 match,
951:                                 all_rules,
952:                                 detected_pos_tag,
953:                                 ai_decision,
954:                                 decision_source,
955:                                 options,
956:                             )
957:                         else:
958:                             # Contextualized AI failed — fall back to hybrid best_guess
959:                             # (this preserves the tuned hybrid decision for review)
960:                             fallback_choice = bg if bg else options[0]
961:                             ai_decision = {
962:                                 "choice": fallback_choice,
963:                                 "confidence": best_guess.get("confidence", 0.95) if isinstance(best_guess, dict) else 0.95,
964:                                 "reason": "hybrid best_guess fallback (contextualized AI failed)",
965:                             }
966:                             decision_source = "hybrid"
967:                             self.decision_stats[decision_source] += 1
968:                             self._log_rule_choice(
969:                                 word, ai_decision["choice"], ai_decision["confidence"], "disagreement→hybrid_fallback"
970:                             )
971:                             self._log_change(
972:                                 match,
973:                                 word,
974:                                 options,
975:                                 ai_decision,
976:                                 decision_source,
977:                                 contextualized_options,
978:                                 detected_pos_tag,
979:                             )
980:                             self._log_comprehensive_rule_entry(
981:                                 word,
982:                                 match,
983:                                 all_rules,
984:                                 detected_pos_tag,
985:                                 ai_decision,
986:                                 decision_source,
987:                                 options,
988:                             )
989:                     else:
990:                         # No rule consensus for non-disagreement cases → queue for AI batch
991:                         # (batch prompt uses REFERENCE EXAMPLES from choices.json for the word family)
992:                         self._log_to_choices_log(f"Queuing '{word}' for AI batch analysis.")
993:                         if all_rules:
994:                             _rules_summary = ", ".join(
995:                                 f"{r}={v['choice']}({v['confidence']:.2f})"
996:                                 for r, v in all_rules.items()
997:                             )
998:                             _ai_reason = f"no consensus — rules fired: {_rules_summary}"
999:                         else:
1000:                             _ai_reason = (
1001:                                 f"no rules fired (POS: {detected_pos_tag or 'unknown'})"
1002:                             )
1003:                         self._log_rule_choice(word, "→ AI", 0.0, f"queued [{_ai_reason}]")
1004:                         item_id_counter += 1
1005:                         log_message(
1006:                             f"DEBUG: Queued item_id_counter: {item_id_counter}",
1007:                             level="DEBUG",
1008:                         )
1009:
1010:                         meaning_map = {s: m for s, m in (contextualized_options or [])}
1011:                         rich_options = [
1012:                             {"spelling": s, "meaning": meaning_map.get(s, s)}
1013:                             for s in options
1014:                         ]
1015:                         batch_item = {
1016:                             "id": item_id_counter,
1017:                             "word": word,
1018:                             "context": context_full,
1019:                             "options": rich_options,
1020:                         }
1021:                         items_for_ai_batch.append(batch_item)
1022:                         # Use best_guess (from disagreement) if present, else None
1023:                         fallback_decision = best_guess if best_guess is not None else None
1024:                         fallback_source = decision_source if decision_source else None
1025:                         match_map[item_id_counter] = (
1026:                             match,
1027:                             word,
1028:                             options,
1029:                             contextualized_options,
1030:                             detected_pos_tag,
1031:                             fallback_decision,  # rule fallback (hybrid on disagreement, else None)
1032:                             fallback_source,
1033:                         )
1034:                 else:
1035:                     # RULES-ONLY MODE: Force decision with zero confidence
1036:                     default_decision = None
1037:                     if self.rules_only_mode:
1038:                         # Use first option, force zero confidence
1039:                         forced_choice = options[0] if options else "UNKNOWN"
1040:                         forced_decision = {
1041:                             "choice": forced_choice,
1042:                             "confidence": 0.0,
1043:                             "reason": "Rules-only forced: using first option",
1044:                         }
1045:                         self.decision_stats["rules_only_forced"] += 1
1046:                         self._log_rule_choice(
1047:                             word, forced_choice, 0.0, "rules_only_main_loop"
1048:                         )
1049:                         self._log_change(
1050:                             match,
1051:                             word,
1052:                             options,
1053:                             forced_decision,
1054:                             "rules_only",
1055:                             contextualized_options,
1056:                             detected_pos_tag,
1057:                         )
1058:                         # Log comprehensive entry for this word
1059:                         self._log_comprehensive_rule_entry(

(Showing lines 640-1059 of 2594. Use offset=1060 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1273,
  "limit": 250
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1273:     def _run_all_rules(
1274:         self, word: str, context_full: str, ctx: "BookfixContext"
1275:     ) -> Tuple[Dict, str]:
1276:         """Helper to run all local rules and return their results and the detected POS tag."""
1277:         log_message(f"DEBUG: Entering _run_all_rules for word: '{word}'", level="DEBUG")
1278:         log_message(
1279:             f"DEBUG: _run_all_rules context_full: '{context_full}'", level="DEBUG"
1280:         )
1281:
1282:         all_rules = {}
1283:         detected_pos_tag = ""
1284:         pos_token = None
1285:         dep_info = None
1286:         doc = None
1287:
1288:         # Extract bracket context using case-insensitive match
1289:         import re
1290:
1291:         match = re.search(r"\[" + re.escape(word) + r"\]", context_full, re.IGNORECASE)
1292:         if not match:
1293:             log_message(
1294:                 f"DEBUG: _run_all_rules: bracket '[{word}]' not found in context_full",
1295:                 level="DEBUG",
1296:             )
1297:             return {}, ""
1298:         # Extract actual matched text to preserve original case (e.g., "Polish" not "polish")
1299:         actual_word_text = match.group()[1:-1]
1300:         bracket_start = match.start()
1301:         context_before = context_full[:bracket_start]
1302:         context_after = context_full[bracket_start + len(actual_word_text) + 2 :]
1303:         log_message(
1304:             f"DEBUG: _run_all_rules context_before: '{context_before}', context_after: '{context_after}'",
1305:             level="DEBUG",
1306:         )
1307:
1308:         if self.use_pos_tagging and self.pos_tagger:
1309:             log_message(
1310:                 f"DEBUG: _run_all_rules: Attempting POS tagging for '{word}'",
1311:                 level="DEBUG",
1312:             )
1313:             # Get rich spaCy context
1314:             try:
1315:                 pos_token, dep_info, doc = self.pos_tagger.get_token_and_dependency(
1316:                     context_before, word, context_after
1317:                 )
1318:                 if pos_token:
1319:                     detected_pos_tag = pos_token.pos_tag
1320:                     log_message(
1321:                         f"DEBUG: _run_all_rules: Detected POS tag for '{word}': '{detected_pos_tag}'",
1322:                         level="DEBUG",
1323:                     )
1324:                 else:
1325:                     log_message(
1326:                         f"DEBUG: _run_all_rules: No POS token found for '{word}'",
1327:                         level="DEBUG",
1328:                     )
1329:             except Exception as e:
1330:                 log_message(
1331:                     f"DEBUG: _run_all_rules: Error during POS tagging: {e}",
1332:                     level="DEBUG",
1333:                 )
1334:
1335:         # Hybrid decider check: if word has a specialized decider, use it
1336:         if word.lower() in DECIDERS and pos_token and dep_info and doc:
1337:             log_message(
1338:                 f"DEBUG: _run_all_rules: Using hybrid decider for '{word}'",
1339:                 level="DEBUG",
1340:             )
1341:             try:
1342:                 # Load NLI if needed for this word
1343:                 if word.lower() in NLI_WORDS:
1344:                     self._ensure_nli_services()
1345:
1346:                 # Extract sentence from context
1347:                 sentence = (
1348:                     context_before.rstrip()
1349:                     + " "
1350:                     + actual_word_text
1351:                     + " "
1352:                     + context_after.lstrip()
1353:                 )
1354:
1355:                 # Get parameters from spaCy structures
1356:                 tag = pos_token.pos_tag  # Fine-grained tag (VBN, NN, etc.)
1357:                 dep = dep_info.dep_relation  # Dependency relation (nsubj, dobj, etc.)
1358:                 head_text = dep_info.head_word.lower() if dep_info.head_word else ""
1359:
1360:                 # Check if word has a determiner child by checking the doc
1361:                 # Find the target token in the doc to check its children
1362:                 target_token_in_doc = None
1363:                 word_lower = word.lower()
1364:                 for token in doc:
1365:                     if token.text.lower() == word_lower and token.i == pos_token.index:
1366:                         target_token_in_doc = token
1367:                         break
1368:                 has_det = (
1369:                     any(c.dep_ == "det" for c in target_token_in_doc.children)
1370:                     if target_token_in_doc
1371:                     else False
1372:                 )
1373:
1374:                 # Call the hybrid decider
1375:                 decider_fn = DECIDERS[word.lower()]
1376:                 pronunciation, route = decider_fn(
1377:                     tag, dep, head_text, has_det, self.nli, sentence
1378:                 )
1379:
1380:                 all_rules["hybrid"] = {
1381:                     "choice": pronunciation,
1382:                     "confidence": 0.95,  # High confidence for hand-tuned deciders
1383:                     "reason": f"Hybrid decider ({route})",
1384:                 }
1385:                 log_message(
1386:                     f"DEBUG: _run_all_rules: Hybrid decider matched '{word}' → '{pronunciation}' ({route})",
1387:                     level="DEBUG",
1388:                 )
1389:                 self._log_rule_evaluation(
1390:                     word,
1391:                     "hybrid",
1392:                     f"Tag: {tag}, Dep: {dep}",
1393:                     f"Match: {pronunciation} ({route})",
1394:                 )
1395:
1396:             except Exception as e:
1397:                 log_message(
1398:                     f"DEBUG: _run_all_rules: Hybrid decider error for '{word}': {e}",
1399:                     level="DEBUG",
1400:                 )
1401:                 # Fall through to generic rules if hybrid fails
1402:
1403:         # Rule 1: Complex POS rules (e.g., imperative verbs)
1404:         if self.pos_dictionary and pos_token and dep_info and doc:
1405:             log_message(
1406:                 f"DEBUG: _run_all_rules: Checking complex POS rules for '{word}'",
1407:                 level="DEBUG",
1408:             )
1409:             try:
1410:                 complex_pos_result = (
1411:                     self.pos_dictionary.get_pronunciation_by_complex_pos_rules(
1412:                         actual_word_text, pos_token, dep_info, doc
1413:                     )
1414:                 )
1415:                 if complex_pos_result:
1416:                     all_rules["complex_pos"] = {
1417:                         "choice": complex_pos_result,
1418:                         "confidence": 0.98,
1419:                         "reason": f"Complex POS rule for '{word}'",
1420:                     }
1421:                     log_message(
1422:                         f"DEBUG: _run_all_rules: Complex POS rule matched: '{complex_pos_result}'",
1423:                         level="DEBUG",
1424:                     )
1425:                     self._log_rule_evaluation(
1426:                         word,
1427:                         "complex_pos",
1428:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1429:                         "Match" if complex_pos_result else "No match",
1430:                     )
1431:                 else:
1432:                     self._log_rule_evaluation(
1433:                         word,
1434:                         "complex_pos",
1435:                         f"POS: {detected_pos_tag}, Dep: {dep_info}",
1436:                         "No match",
1437:                     )
1438:             except Exception as e:
1439:                 log_message(
1440:                     f"DEBUG: _run_all_rules: Error checking complex POS rules: {e}",
1441:                     level="DEBUG",
1442:                 )
1443:                 self._log_rule_evaluation(word, "complex_pos", "Error", str(e))
1444:
1445:         # Rule 2: Simple POS tagging (fallback if complex doesn't match)
1446:         log_message(
1447:             f"DEBUG: _run_all_rules: Checking simple POS rule for '{word}'",
1448:             level="DEBUG",
1449:         )
1450:         pos_result = self._get_pos_based_choice(word, context_before, context_after)
1451:         if pos_result:
1452:             pronunciation, confidence, explanation = pos_result
1453:             all_rules["pos"] = {
1454:                 "choice": pronunciation,
1455:                 "confidence": confidence,
1456:                 "reason": f"POS-based: {explanation} [Tag: {detected_pos_tag}]",
1457:             }
1458:             log_message(
1459:                 f"DEBUG: _run_all_rules: Simple POS rule matched: '{pronunciation}'",
1460:                 level="DEBUG",
1461:             )
1462:             self._log_rule_evaluation(
1463:                 word,
1464:                 "pos",
1465:                 f"POS: {detected_pos_tag}, Explanation: {explanation}",
1466:                 f"Match: {pronunciation}",
1467:             )
1468:         else:
1469:             self._log_rule_evaluation(
1470:                 word, "pos", f"POS: {detected_pos_tag}", "No match"
1471:             )
1472:
1473:         if self.pos_dictionary:
1474:             # Rule 3: Semantic matching
1475:             log_message(
1476:                 f"DEBUG: _run_all_rules: Checking semantic rule for '{word}'",
1477:                 level="DEBUG",
1478:             )
1479:             before_tokens = re.findall(r"\b\w+\b", context_before.lower())[-10:]
1480:             after_tokens = re.findall(r"\b\w+\b", context_after.lower())[:10]
1481:             try:
1482:                 semantic_result = self.pos_dictionary.get_pronunciation_by_semantic(
1483:                     word, before_tokens + after_tokens
1484:                 )
1485:                 if semantic_result:
1486:                     pronunciation, matched_tag, confidence = semantic_result
1487:                     all_rules["semantic"] = {
1488:                         "choice": pronunciation,
1489:                         "confidence": confidence,
1490:                         "reason": f"Semantic: nearby word '{matched_tag}'",
1491:                     }
1492:                     log_message(
1493:                         f"DEBUG: _run_all_rules: Semantic rule matched: '{pronunciation}'",
1494:                         level="DEBUG",
1495:                     )
1496:                     self._log_rule_evaluation(
1497:                         word,
1498:                         "semantic",
1499:                         f"Tokens: {before_tokens + after_tokens}",
1500:                         f"Match: {pronunciation} (tag: {matched_tag})",
1501:                     )
1502:                 else:
1503:                     self._log_rule_evaluation(
1504:                         word,
1505:                         "semantic",
1506:                         f"Tokens: {before_tokens + after_tokens}",
1507:                         "No match",
1508:                     )
1509:             except Exception as e:
1510:                 log_message(
1511:                     f"DEBUG: _run_all_rules: Error checking semantic rule: {e}",
1512:                     level="DEBUG",
1513:                 )
1514:                 self._log_rule_evaluation(word, "semantic", "Error", str(e))
1515:
1516:             # Rule 4: Named entity context
1517:             log_message(
1518:                 f"DEBUG: _run_all_rules: Checking entity rule for '{word}'",
1519:                 level="DEBUG",
1520:             )
1521:             try:
1522:                 entity_result = self.pos_dictionary.check_entity_context(

(Showing lines 1273-1522 of 2594. Use offset=1523 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "offset": 1654,
  "limit": 200
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py</path>
<type>file</type>
<content>
1654:     def _get_consensus_from_rules(
1655:         self, all_rules: Dict, context_full: str, word: str = "", options: List = None
1656:     ) -> Tuple[Optional[Dict], Optional[str], Optional[Dict]]:
1657:         """
1658:         Check for consensus among rule results.
1659:
1660:         Args:
1661:             all_rules: Dictionary of rule results
1662:             context_full: Full context around the word
1663:             word: The word being processed
1664:             options: List of available replacement options for this word
1665:
1666:         Returns:
1667:             Tuple of (decision_dict or None, source_str or None, best_guess_dict or None)
1668:             The third value carries a preferred rule decision (e.g. hybrid) to use
1669:             as best_guess when queuing to AI on disagreement.
1670:
1671:         Strategy:
1672:         1. If all rules agree on the same choice → consensus
1673:         2. If rules disagree:
1674:            - AI enabled → return None (send to AI)
1675:            - AI disabled → fall back to strict priority
1676:         3. If no rules matched → return None (or force in rules_only_mode)
1677:         4. NEW (hybrid mode): Disagreement gate — if complex_pos absent but
1678:            hybrid and pos both present and disagree on choice for a homograph
1679:            (word has hybrid decider), return None so caller queues to AI with
1680:            the hybrid choice as best_guess. This improves quality on ambiguous
1681:            spaCy parses without forcing verify_all globally.
1682:
1683:         NOTE: We intentionally avoid allowing a lower-priority rule (e.g. plain
1684:         'keyword') to win over higher-priority rules (complex_pos/entity/pos/
1685:         semantic) based solely on a slightly higher numeric confidence.
1686:         Additionally, **keyword-only** matches are treated as **no decision** so
1687:         they are always surfaced as low-confidence items for review (or sent to
1688:         AI), never as standalone rules.
1689:         """
1690:         # ===== RULES-ONLY MODE: Apply confidence floor, defer to review if below threshold =====
1691:         if self.rules_only_mode:
1692:             log_message(
1693:                 f"Rules-only mode: Checking decision for '{word}' (rules: {list(all_rules.keys()) if all_rules else 'none'})",
1694:                 level="DEBUG",
1695:             )
1696:             min_confidence = self.config.get("Thresholds", {}).get(
1697:                 "MIN_CONFIDENCE_THRESHOLD", 0.75
1698:             )
1699:             # Log to rule_choice log for tracking
1700:             if not all_rules:
1701:                 forced_choice = (
1702:                     options[0] if options and len(options) > 0 else "UNKNOWN"
1703:                 )
1704:                 self._log_rule_choice(word, forced_choice, 0.0, "rules_only_no_rules")
1705:                 return {
1706:                     "choice": forced_choice,
1707:                     "confidence": 0.0,
1708:                     "reason": "Rules-only: no rules",
1709:                 }, "rules_only", None
1710:             # Check if any rule meets confidence threshold
1711:             if all_rules:
1712:                 best_name = max(all_rules, key=lambda r: all_rules[r]["confidence"])
1713:                 best = all_rules[best_name]
1714:                 if best["confidence"] >= min_confidence:
1715:                     # Meets threshold - use with actual confidence
1716:                     best_copy = best.copy()
1717:                     best_copy["reason"] = f"Rules-only: {best['reason']}"
1718:                     self._log_rule_choice(
1719:                         word,
1720:                         best_copy["choice"],
1721:                         best_copy["confidence"],
1722:                         f"rules_only_{best_name}",
1723:                     )
1724:                     return best_copy, best_name, None
1725:                 else:
1726:                     # Below threshold - defer to review
1727:                     log_message(
1728:                         f"Rules-only mode: Confidence {best['confidence']:.2f} below threshold {min_confidence:.2f}, deferring to review",
1729:                         level="DEBUG",
1730:                     )
1731:                     return None, None, None
1732:             # Fallback
1733:             forced_choice = options[0] if options and len(options) > 0 else "UNKNOWN"
1734:             self._log_rule_choice(word, forced_choice, 0.0, "rules_only_fallback")
1735:             return {
1736:                 "choice": forced_choice,
1737:                 "confidence": 0.0,
1738:                 "reason": "Rules-only fallback",
1739:             }, "rules_only", None
1740:
1741:         # ===== HYBRID/VERIFY MODES: complex_pos > hybrid > pos; all others → AI =====
1742:         if not all_rules:
1743:             return None, None
1744:
1745:         # Rule 1: complex_pos (dep_rules) always wins — 0.98 confidence structural rule
1746:         if "complex_pos" in all_rules:
1747:             rule_decision = all_rules["complex_pos"]
1748:             self._log_rule_choice(
1749:                 word,
1750:                 rule_decision["choice"],
1751:                 rule_decision["confidence"],
1752:                 "complex_pos",
1753:             )
1754:             return rule_decision, "complex_pos", None
1755:
1756:         # Disagreement gate for hybrid/verify mode (only for the 23 homographs):
1757:         # If complex_pos is absent (no strong structural match) but both hybrid
1758:         # decider and simple POS produced choices that differ, do not auto-decide.
1759:         # Return None decision so the caller will queue to AI, passing the hybrid
1760:         # result as best_guess. This routes exactly the ambiguous cases (e.g. live
1761:         # tagged RB in relative clause, lead NN with possessive that NLI wants as
1762:         # guidance) to the LLM for better results while preserving fast rule path
1763:         # when the two agree.
1764:         # Controlled by config Thresholds.DISAGREEMENT_TO_AI (default True).
1765:         if (
1766:             "hybrid" in all_rules
1767:             and "pos" in all_rules
1768:         ):
1769:             hybrid_choice = all_rules["hybrid"]["choice"]
1770:             pos_choice = all_rules["pos"]["choice"]
1771:             if hybrid_choice != pos_choice:
1772:                 disagreement_flag = self.config.get("Thresholds", {}).get(
1773:                     "DISAGREEMENT_TO_AI", True
1774:                 )
1775:                 if disagreement_flag:
1776:                     fired = ", ".join(
1777:                         f"{k}={v['choice']}({v['confidence']:.2f})"
1778:                         for k, v in all_rules.items()
1779:                     )
1780:                     log_message(
1781:                         f"DEBUG: disagreement (hybrid vs pos) for '{word}' — queuing for AI. Rules fired: {fired}",
1782:                         level="DEBUG",
1783:                     )
1784:                     # Return None to force AI queue; attach hybrid as best_guess
1785:                     return None, "disagreement", all_rules["hybrid"]
1786:
1787:         # Rule 2: hybrid deciders — hand-tuned per-word logic, 0.95 confidence
1788:         if "hybrid" in all_rules:
1789:             rule_decision = all_rules["hybrid"]
1790:             self._log_rule_choice(
1791:                 word, rule_decision["choice"], rule_decision["confidence"], "hybrid"
1792:             )
1793:             return rule_decision, "hybrid", None
1794:
1795:         # Rule 3: POS tag — reliable only when pronunciations differ by part of speech
1796:         if "pos" in all_rules:
1797:             rule_decision = all_rules["pos"]
1798:             if rule_decision["confidence"] >= 0.80:
1799:                 self._log_rule_choice(
1800:                     word, rule_decision["choice"], rule_decision["confidence"], "pos"
1801:                 )
1802:                 return rule_decision, "pos", None
1803:
1804:         # Rules 4–7 (semantic, entity, definition, keyword) are not trusted to decide.
1805:         # Log which rules fired for diagnostics, then queue for AI.
1806:         fired = ", ".join(
1807:             f"{k}={v['choice']}({v['confidence']:.2f})" for k, v in all_rules.items()
1808:         )
1809:         log_message(
1810:             f"DEBUG: no autonomous decision — queuing for AI. Rules fired: {fired}",
1811:             level="DEBUG",
1812:         )
1813:         return None, None, None
1814:
1815:     def _log_rule_choice(
1816:         self, word: str, choice: str, confidence: float, rule_type: str
1817:     ):
1818:         """Log rule choices to separate file."""
1819:         import os, re
1820:
1821:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1822:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1823:         log_path = os.path.join(log_dir, "logs", "rules_choices.log")
1824:         sentence = getattr(self, "_current_sentence", "")
1825:         log_line = (
1826:             f"{word} -> {choice} (confidence {confidence:.2f}, rule: {rule_type})"
1827:         )
1828:         if sentence:
1829:             log_line += f" | {sentence}"
1830:         with open(log_path, "a", encoding="utf-8") as f:
1831:             f.write(log_line + "\n")
1832:
1833:     def _log_rule_evaluation(self, word: str, rule: str, details: str, result: str):
1834:         """Log each rule evaluation attempt."""
1835:         import os
1836:         import datetime
1837:
1838:         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
1839:         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)
1840:         log_path = os.path.join(
1841:             log_dir, "logs", "rule_evaluation.log"
1842:         )  # Changed to separate file
1843:         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
1844:         with open(log_path, "a", encoding="utf-8") as f:
1845:             f.write(
1846:                 f"[{timestamp}] Word: '{word}' | Rule: {rule} | {details} | Result: {result}\n"
1847:             )
1848:
1849:     def _log_ai_choice(self, word: str, choice: str, confidence: float, reason: str):
1850:         """Log AI choices to separate file."""
1851:         import os
1852:
1853:         log_dir = os.path.dirname(os.path.abspath(__file__))

(Showing lines 1654-1853 of 2594. Use offset=1854 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 7.6s)

_Thinking:_

The code appears unchanged from what I read before. The user said "the code updated" — let me check if there are differences by looking at the line count and any new methods or changed signatures.

The code reads the same as before (2594 lines, same structure). Let me check if there were changes to the hybrid deciders or other files:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 50,
  "offset": 370
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
370:         head: Lowercased head word.
371:         has_det: Whether a determiner child is present.
372:         nli: Optional NLI pipeline (unused for sow).
373:         sentence: Full sentence context (unused here).
374:
375:     Returns:
376:         Tuple of (pronunciation, route) e.g. ("soh", "pos-verb")
377:     """
378:     # Verb tags indicate the verb pronunciation 'soh'.
379:     if tag in VERB_PRESENT or tag in VERB_PAST:
380:         return "soh", "pos-verb"
381:     # Default to noun pronunciation 'sow' for other tags.
382:     return "sow", "pos-noun"
383:
384:
385: def decide_resume(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
386:     """
387:     Decide pronunciation for 'resume': verb → 'rezoom'; noun → 'resume'.
388:
389:     Args:
390:         tag: Fine-grained POS tag from spaCy.
391:         dep: Dependency relation.
392:         head: Lowercased head word.
393:         has_det: Whether a determiner child is present.
394:         nli: Optional NLI pipeline (unused for resume).
395:         sentence: Full sentence context (unused here).
396:
397:     Returns:
398:         Tuple of (pronunciation, route) e.g. ("rezoom", "pos-verb")
399:     """
400:     # Verb tags indicate the verb pronunciation 'rezoom'.
401:     if tag in VERB_PRESENT or tag in VERB_PAST:
402:         return "rezoom", "pos-verb"
403:     # Default to noun pronunciation 'resume' for other tags.
404:     return "resume", "pos-noun"
405:
406:
407: def decide_refuse(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
408:     """
409:     Decide pronunciation for 'refuse': verb → 'refuze'; noun → 'refuse'.
410:
411:     Args:
412:         tag: Fine-grained POS tag from spaCy.
413:         dep: Dependency relation.
414:         head: Lowercased head word.
415:         has_det: Whether a determiner child is present.
416:         nli: Optional NLI pipeline (unused for refuse).
417:         sentence: Full sentence context (unused here).
418:
419:     Returns:

(Showing lines 370-419 of 876. Use offset=420 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 50,
  "offset": 190
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
190:     Args:
191:         tag: Fine-grained POS tag from spaCy.
192:         dep: Dependency relation.
193:         head: Lowercased head word.
194:         has_det: Whether a determiner child is present.
195:         nli: Optional NLI pipeline (unused for records).
196:         sentence: Full sentence context (used for special phrase check).
197:
198:     Returns:
199:         Tuple of (pronunciation, route) e.g. ("rekords", "pos-verb")
200:     """
201:     # Strong context bias for known verb uses like "history records" even on NNS mistag.
202:     sent_lower = sentence.lower()
203:     if "history records" in sent_lower or re.search(r'\bit records\b', sent_lower):
204:         return "rekords", "pos-verb-context"
205:
206:     # Verb for plural: if verb tag, or NNS but in core verbal dep position (mis-tag case).
207:     if tag in VERB_PRESENT or tag in VERB_PAST or (tag == "NNS" and dep in ("ROOT", "xcomp", "ccomp", "advcl", "relcl", "nsubj", "dobj")):
208:         return "rekords", "pos-verb"
209:     # Default to noun plural.
210:     return "rekkurds", "pos-noun"
211:
212:
213: def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
214:     """
215:     Decide pronunciation for 'close': verb → 'cloze'; adj/adv → 'close'; noun → 'close'.
216:
217:     Args:
218:         tag: Fine-grained POS tag from spaCy.
219:         dep: Dependency relation.
220:         head: Lowercased head word.
221:         has_det: Whether a determiner child is present.
222:         nli: Optional NLI pipeline (unused for close).
223:         sentence: Full sentence context (unused here).
224:
225:     Returns:
226:         Tuple of (pronunciation, route) e.g. ("cloze", "pos-verb")
227:     """
228:     # Verb tags indicate the 'cloze' pronunciation.
229:     if tag in VERB_PRESENT or tag in VERB_PAST:
230:         return "cloze", "pos-verb"
231:     # Adjective or adverb tags get the 'close' pronunciation.
232:     if tag in ADJ_TAGS or tag in ADV_TAGS:
233:         return "close", "pos-adj/adv"
234:     # Default (including noun and other tags) to 'close'.
235:     return "close", "pos-default"
236:
237:
238: def decide_read(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
239:     """

(Showing lines 190-239 of 876. Use offset=240 to continue.)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 5.1s)

_Thinking:_

The hybrid_deciders.py file grew from 407 lines to 876 lines. That's a significant change. Let me check the full file to understand what was added.

The file grew from 407 to 876 lines. Let me read the full file to see the changes:

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 200,
  "offset": 1
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
1: """
2: Hybrid homograph disambiguation engine.
3:
4: Uses spaCy transformer (en_core_web_trf) for POS/dependency, RoBERTa-large-MNLI NLI for
5: hard cases. 22 hand-tuned per-word deciders for accuracy on common homographs.
6:
7: Deciders return (pronunciation_spelling, route_explanation).
8: """
9:
10: import re
11: from typing import Optional, Tuple
12:
13: # POS tag categories for rules
14: VERB_PRESENT = {"VB", "VBP", "VBZ", "VBG", "VBN"}
15: VERB_PAST = {"VBD"}
16: ADJ_TAGS = {"JJ", "JJR", "JJS"}
17: ADV_TAGS = {"RB", "RBR", "RBS"}
18:
19:
20: def is_verb_context(tag: str, dep: str, head: str, sentence: str) -> bool:
21:     """Return True if the token is likely the verb sense of 'live' (to liv).
22:
23:     Supplements spaCy's often-wrong tag (frequently JJ) and dep (frequently amod)
24:     by using verb-like dependency frames plus sentence-level look-ahead/look-behind
25:     cues for common verb frames: "that live here", "live longer than", "do somehow live",
26:     "people that live", etc.
27:
28:     This is the core of the requested heuristic that scans context beyond pure
29:     whitespace or spaCy POS.
30:
31:     Args:
32:         tag: Fine-grained POS tag from spaCy.
33:         dep: Dependency relation.
34:         head: Lowercased head word.
35:         sentence: Context sentence (may contain [live] brackets).
36:
37:     Returns:
38:         True if 'liv' (verb) should be chosen.
39:     """
40:     # Normalize sentence for reliable pattern matching (strip target brackets).
41:     norm = re.sub(r'[\[\]]', '', sentence.lower())
42:
43:     # 1. Verb-clause dependency frames are strong signals for verb, even under JJ mis-tag.
44:     # Covers "to live", "live longer", relative clauses "that live", "advcl" infinitives, etc.
45:     verb_clause_deps = {"ROOT", "xcomp", "ccomp", "advcl", "relcl", "acl"}
46:     if dep in verb_clause_deps:
47:         # Non-obvious branch: we trust the dep over the tag here because the parser
48:         # often mis-tags the verb as JJ but still assigns a correct clausal dep.
49:         return True
50:
51:     # 2. If the syntactic head is a clear verbal auxiliary or infinitive marker,
52:     # treat as verb. E.g. heads like "do", "had", "to" in "had to live", "do live".
53:     verb_heads = {"do", "does", "did", "can", "could", "will", "would", "must",
54:                   "have", "has", "had", "be", "is", "are", "was", "were", "to"}
55:     if head in verb_heads:
56:         return True
57:
58:     # 3. Sentence-level heuristic: scan for common verb complement/relative patterns
59:     # around the target word. This provides the "look ahead/behind" the user requested.
60:     # These patterns catch the exact failing cases even when dep == "amod".
61:     verb_patterns = [
62:         r'\bthat\s+live\b',                    # relative: "people that live here"
63:         r'\blive\s+(here|there|longer|long|in|on|with|for|to|as)\b',  # "live here", "live longer"
64:         r'\blive\s+than\b',                    # "live longer than me"
65:         r'\bdo\s+.*?\blive\b',                 # "if you do somehow live"
66:         r'\bpeople\s+.*?\blive\b',             # "fifty thousand people ... live"
67:         r'\byou\s+.*?\blive\b',                # "if you ... live longer"
68:         r'\bsomehow\s+live\b',
69:         r'\blive\s+longer\b',
70:     ]
71:     for pat in verb_patterns:
72:         if re.search(pat, norm):
73:             # Non-obvious: we return True for verb even if the immediate dep looks adjectival.
74:             return True
75:
76:     # 4. Fall back to the tag only if nothing else matched (original simple behavior).
77:     if tag in VERB_PRESENT or tag in VERB_PAST:
78:         return True
79:
80:     return False
81:
82:
83: def is_noun_context(tag: str, dep: str, head: str, has_det: bool, sentence: str) -> bool:
84:     """Return True if the token is likely the noun sense of 'invalid' (a disabled person).
85:
86:     Provides sentence-scanning heuristic for bare/copular noun uses such as
87:     "an invalid.", "being an invalid", "as an invalid" that spaCy often tags JJ+amod.
88:
89:     This complements the dep_rules in the JSON (which cannot see full sentence context).
90:
91:     Args:
92:         tag: Fine-grained POS tag.
93:         dep: Dependency relation.
94:         head: Head word (lowercased).
95:         has_det: Whether a determiner child is present.
96:         sentence: Context sentence (may contain [invalid]).
97:
98:     Returns:
99:         True if noun pronunciation 'invalid' should be chosen.
100:     """
101:     norm = re.sub(r'[\[\]]', '', sentence.lower())
102:
103:     # Strong noun cues via surface pattern (the requested heuristic scanning).
104:     # "an invalid" or "a invalid" (with or without following period) almost always
105:     # means the disabled-person noun, regardless of what spaCy tagged the token.
106:     if re.search(r'\ban? invalid\b', norm):
107:         return True
108:     if re.search(r'\binvalid\s*\.\s*$', norm) or re.search(r'\binvalid\s*\.', norm):
109:         return True
110:     if re.search(r'\b(being an invalid|as an invalid)\b', norm):
111:         return True
112:
113:     # Dep-based noun positions (extended from prior fixes). These still help when
114:     # the parse is correct.
115:     noun_deps = {"nsubj", "dobj", "pobj", "attr", "appos", "conj", "nsubjpass", "ROOT"}
116:     if dep in noun_deps:
117:         return True
118:     if has_det and dep in {"nsubj", "dobj", "pobj", "attr", "acomp", "appos"}:
119:         return True
120:
121:     return False
122:
123:
124: def nli_decide(nli, sentence: str, word: str, q_a: str, label_a: str, q_b: str, label_b: str) -> Tuple[str, str]:
125:     """
126:     Run RoBERTa NLI (zero-shot) to pick between two pronunciation hypotheses for a homograph.
127:
128:     Used by several deciders as fallback when POS rules are insufficient.
129:
130:     Args:
131:         nli: The zero-shot classification pipeline (or None if disabled).
132:         sentence: The full context sentence containing the target word.
133:         word: The homograph word being decided (for logging in route).
134:         q_a: First hypothesis/question string for NLI.
135:         label_a: Pronunciation to return if q_a wins.
136:         q_b: Second hypothesis/question string for NLI.
137:         label_b: Pronunciation to return if q_b wins.
138:
139:     Returns:
140:         Tuple (chosen_pronunciation, route_string) e.g. ("tair", "nli=tair(0.92)")
141:     """
142:     # If NLI pipeline not available, default to first hypothesis (label_a).
143:     if not nli:
144:         return label_a, f"nli-disabled"
145:     try:
146:         result = nli(sentence, candidate_labels=[q_a, q_b], multi_label=False)
147:         scores = dict(zip(result["labels"], result["scores"]))
148:         if scores[q_a] > scores[q_b]:
149:             return label_a, f"nli={label_a}({scores[q_a]:.2f})"
150:         else:
151:             return label_b, f"nli={label_b}({scores[q_b]:.2f})"
152:     except Exception:
153:         # On any error (model issues, etc.) safely default to label_a.
154:         return label_a, f"nli-error"
155:
156:
157: # ── 22 Word-Specific Deciders ────────────────────────────────────────────────────────
158:
159: def decide_record(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
160:     """
161:     Decide pronunciation for 'record': verb sense 'rekord' vs noun sense 'rekkurd'.
162:
163:     Uses simple POS tag check; verb forms get 'rekord', everything else 'rekkurd'.
164:
165:     Args:
166:         tag: Fine-grained POS tag from spaCy.
167:         dep: Dependency relation.
168:         head: Lowercased head word.
169:         has_det: Whether a determiner child is present.
170:         nli: Optional NLI pipeline (unused for record).
171:         sentence: Full sentence context (unused here).
172:
173:     Returns:
174:         Tuple of (pronunciation, route) e.g. ("rekord", "pos-verb")
175:     """
176:     # Verb tags indicate action sense.
177:     if tag in VERB_PRESENT or tag in VERB_PAST:
178:         return "rekord", "pos-verb"
179:     # Default to noun sense for all other tags (including mis-tags).
180:     return "rekkurd", "pos-noun"
181:
182:
183: def decide_records(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
184:     """
185:     Decide pronunciation for 'records' (plural): verb → 'rekords'; noun → 'rekkurds'.
186:
187:     Includes special case for NNS mis-tags on verbs in clausal positions
188:     (e.g. spaCy tagging verb "records" as NNS in "history records").
189:
190:     Args:
191:         tag: Fine-grained POS tag from spaCy.
192:         dep: Dependency relation.
193:         head: Lowercased head word.
194:         has_det: Whether a determiner child is present.
195:         nli: Optional NLI pipeline (unused for records).
196:         sentence: Full sentence context (used for special phrase check).
197:
198:     Returns:
199:         Tuple of (pronunciation, route) e.g. ("rekords", "pos-verb")
200:     """

(Showing lines 1-200 of 876. Use offset=201 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 200,
  "offset": 200
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
200:     """
201:     # Strong context bias for known verb uses like "history records" even on NNS mistag.
202:     sent_lower = sentence.lower()
203:     if "history records" in sent_lower or re.search(r'\bit records\b', sent_lower):
204:         return "rekords", "pos-verb-context"
205:
206:     # Verb for plural: if verb tag, or NNS but in core verbal dep position (mis-tag case).
207:     if tag in VERB_PRESENT or tag in VERB_PAST or (tag == "NNS" and dep in ("ROOT", "xcomp", "ccomp", "advcl", "relcl", "nsubj", "dobj")):
208:         return "rekords", "pos-verb"
209:     # Default to noun plural.
210:     return "rekkurds", "pos-noun"
211:
212:
213: def decide_close(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
214:     """
215:     Decide pronunciation for 'close': verb → 'cloze'; adj/adv → 'close'; noun → 'close'.
216:
217:     Args:
218:         tag: Fine-grained POS tag from spaCy.
219:         dep: Dependency relation.
220:         head: Lowercased head word.
221:         has_det: Whether a determiner child is present.
222:         nli: Optional NLI pipeline (unused for close).
223:         sentence: Full sentence context (unused here).
224:
225:     Returns:
226:         Tuple of (pronunciation, route) e.g. ("cloze", "pos-verb")
227:     """
228:     # Verb tags indicate the 'cloze' pronunciation.
229:     if tag in VERB_PRESENT or tag in VERB_PAST:
230:         return "cloze", "pos-verb"
231:     # Adjective or adverb tags get the 'close' pronunciation.
232:     if tag in ADJ_TAGS or tag in ADV_TAGS:
233:         return "close", "pos-adj/adv"
234:     # Default (including noun and other tags) to 'close'.
235:     return "close", "pos-default"
236:
237:
238: def decide_read(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
239:     """
240:     Decide pronunciation for 'read': past/VBN → 'red'; present → 'reed'; default → 'red'.
241:
242:     Args:
243:         tag: Fine-grained POS tag from spaCy.
244:         dep: Dependency relation.
245:         head: Lowercased head word.
246:         has_det: Whether a determiner child is present.
247:         nli: Optional NLI pipeline (unused for read).
248:         sentence: Full sentence context (unused here).
249:
250:     Returns:
251:         Tuple of (pronunciation, route) e.g. ("red", "pos-past")
252:     """
253:     # Past tense or VBN participle uses the 'red' pronunciation.
254:     if tag in VERB_PAST or tag == "VBN":
255:         return "red", "pos-past"
256:     # Present tense verb forms use 'reed'.
257:     if tag in VERB_PRESENT:
258:         return "reed", "pos-verb"
259:     # Default for nouns, adjectives, etc. to 'red'.
260:     return "red", "pos-default"
261:
262:
263: def decide_live(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
264:     """
265:     live: verb → liv; adj/adv → lyve; noun → liv.
266:
267:     Uses a robust context-aware heuristic (is_verb_context) that performs
268:     dependency checks plus sentence scanning (look-ahead/look-behind) for
269:     verb cues. This protects against spaCy's frequent JJ + amod mis-tags on
270:     true verbs like "people that live here" and "live longer than me".
271:
272:     The heuristic is the primary decision path; adjective branch is guarded
273:     to never override a detected verb context.
274:
275:     Args:
276:         tag: Fine-grained POS tag.
277:         dep: Dependency relation.
278:         head: Head word (lowercased).
279:         has_det: Has determiner child.
280:         nli: NLI pipeline (unused for live).
281:         sentence: Context sentence for heuristics.
282:
283:     Returns:
284:         (pronunciation, route)
285:     """
286:     # Normalize once for all pattern checks (removes [live] brackets).
287:     norm = re.sub(r'[\[\]]', '', sentence.lower())
288:
289:     # Primary decision: use the new sentence-scanning heuristic.
290:     # This is deliberately first and comprehensive so that even when dep=="amod"
291:     # and tag=="JJ" the verb cases are caught via patterns like "live here" or "that live".
292:     if is_verb_context(tag, dep, head, sentence):
293:         # Guard the one idiom that looks like a verb frame but is actually adj: "go live".
294:         if not (head == "go" and "go live" in norm):
295:             return "liv", "pos-verb-heuristic"
296:
297:     # 'go live' idiom for launch/broadcast: 'lyve'.
298:     # Explicitly checked after the verb heuristic so "go live in ..." (place) stays verb.
299:     if head == "go" and re.search(r'\bgo\s*live\b', norm, re.IGNORECASE) and not re.search(r'\bgo\s*live\s+in\b', norm, re.IGNORECASE):
300:         return "lyve", "pos-go-live-idiom"
301:
302:     # Adjective/adverb 'lyve': only when the heuristic did NOT claim verb,
303:     # and the attachment is consistent with modification (amod/advmod/compound)
304:     # or a clear predicative adjective slot (with matching tag).
305:     # The extra "not is_verb_context" guard is redundant after the early return
306:     # above but kept for clarity and future maintenance.
307:     if dep in ("amod", "compound", "advmod") or ((tag in ADJ_TAGS or tag in ADV_TAGS) and dep in ("acomp", "attr")):
308:         if not is_verb_context(tag, dep, head, sentence):
309:             return "lyve", "pos-adj"
310:
311:     # Phrase-level bias for common "live person/people/body/specimen" as the alive sense.
312:     if re.search(r'\blive (person|people|body|specimen)', norm, re.IGNORECASE):
313:         return "lyve", "pos-live-adj-phrase"
314:
315:     # Default to the verb sense for everything else (including most mis-tags).
316:     return "liv", "pos-default"
317:
318:
319: def decide_object(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
320:     """
321:     Decide pronunciation for 'object': verb → 'ubjekt'; noun → 'objekt'.
322:
323:     Args:
324:         tag: Fine-grained POS tag from spaCy.
325:         dep: Dependency relation.
326:         head: Lowercased head word.
327:         has_det: Whether a determiner child is present.
328:         nli: Optional NLI pipeline (unused for object).
329:         sentence: Full sentence context (unused here).
330:
331:     Returns:
332:         Tuple of (pronunciation, route) e.g. ("ubjekt", "pos-verb")
333:     """
334:     # Verb tags indicate the stressed-first-syllable verb pronunciation.
335:     if tag in VERB_PRESENT or tag in VERB_PAST:
336:         return "ubjekt", "pos-verb"
337:     # Default to noun pronunciation for other tags.
338:     return "objekt", "pos-noun"
339:
340:
341: def decide_present(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
342:     """
343:     Decide pronunciation for 'present': verb → 'prezent'; noun/adj → 'present'.
344:
345:     Args:
346:         tag: Fine-grained POS tag from spaCy.
347:         dep: Dependency relation.
348:         head: Lowercased head word.
349:         has_det: Whether a determiner child is present.
350:         nli: Optional NLI pipeline (unused for present).
351:         sentence: Full sentence context (unused here).
352:
353:     Returns:
354:         Tuple of (pronunciation, route) e.g. ("prezent", "pos-verb")
355:     """
356:     # Verb tags indicate the verb pronunciation 'prezent'.
357:     if tag in VERB_PRESENT or tag in VERB_PAST:
358:         return "prezent", "pos-verb"
359:     # Default to noun/adj pronunciation 'present' for other tags.
360:     return "present", "pos-noun/adj"
361:
362:
363: def decide_sow(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
364:     """
365:     Decide pronunciation for 'sow': verb → 'soh'; noun → 'sow'.
366:
367:     Args:
368:         tag: Fine-grained POS tag from spaCy.
369:         dep: Dependency relation.
370:         head: Lowercased head word.
371:         has_det: Whether a determiner child is present.
372:         nli: Optional NLI pipeline (unused for sow).
373:         sentence: Full sentence context (unused here).
374:
375:     Returns:
376:         Tuple of (pronunciation, route) e.g. ("soh", "pos-verb")
377:     """
378:     # Verb tags indicate the verb pronunciation 'soh'.
379:     if tag in VERB_PRESENT or tag in VERB_PAST:
380:         return "soh", "pos-verb"
381:     # Default to noun pronunciation 'sow' for other tags.
382:     return "sow", "pos-noun"
383:
384:
385: def decide_resume(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
386:     """
387:     Decide pronunciation for 'resume': verb → 'rezoom'; noun → 'resume'.
388:
389:     Args:
390:         tag: Fine-grained POS tag from spaCy.
391:         dep: Dependency relation.
392:         head: Lowercased head word.
393:         has_det: Whether a determiner child is present.
394:         nli: Optional NLI pipeline (unused for resume).
395:         sentence: Full sentence context (unused here).
396:
397:     Returns:
398:         Tuple of (pronunciation, route) e.g. ("rezoom", "pos-verb")
399:     """

(Showing lines 200-399 of 876. Use offset=400 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 200,
  "offset": 420
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
420:         Tuple of (pronunciation, route) e.g. ("refuze", "pos-verb")
421:     """
422:     # Verb tags indicate the verb pronunciation 'refuze'.
423:     if tag in VERB_PRESENT or tag in VERB_PAST:
424:         return "refuze", "pos-verb"
425:     # Default to noun pronunciation 'refuse' for other tags.
426:     return "refuse", "pos-noun"
427:
428:
429: def decide_elaborate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
430:     """
431:     Decide pronunciation for 'elaborate': verb → 'elaboreight'; adj → 'elaborit'.
432:
433:     Args:
434:         tag: Fine-grained POS tag from spaCy.
435:         dep: Dependency relation.
436:         head: Lowercased head word.
437:         has_det: Whether a determiner child is present.
438:         nli: Optional NLI pipeline (unused for elaborate).
439:         sentence: Full sentence context (unused here).
440:
441:     Returns:
442:         Tuple of (pronunciation, route) e.g. ("elaboreight", "pos-verb")
443:     """
444:     # Verb tags indicate the verb pronunciation 'elaboreight'.
445:     if tag in VERB_PRESENT or tag in VERB_PAST:
446:         return "elaboreight", "pos-verb"
447:     # Default (adj and others) to 'elaborit'.
448:     return "elaborit", "pos-adj"
449:
450:
451: def decide_estimate(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
452:     """
453:     Decide pronunciation for 'estimate': verb → 'estimeight'; noun → 'estimit'.
454:
455:     Args:
456:         tag: Fine-grained POS tag from spaCy.
457:         dep: Dependency relation.
458:         head: Lowercased head word.
459:         has_det: Whether a determiner child is present.
460:         nli: Optional NLI pipeline (unused for estimate).
461:         sentence: Full sentence context (unused here).
462:
463:     Returns:
464:         Tuple of (pronunciation, route) e.g. ("estimeight", "pos-verb")
465:     """
466:     # Verb tags indicate the verb pronunciation 'estimeight'.
467:     if tag in VERB_PRESENT or tag in VERB_PAST:
468:         return "estimeight", "pos-verb"
469:     # Default to noun pronunciation 'estimit' for other tags.
470:     return "estimit", "pos-noun"
471:
472:
473: def decide_wind(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
474:     """
475:     Decide pronunciation for 'wind': verb sense 'why'nd' (to coil/twist) vs noun sense 'win'd' (moving air).
476:
477:     Args:
478:         tag: Fine-grained POS tag from spaCy (e.g. 'VBG', 'NN').
479:         dep: Dependency relation of the token (e.g. 'ROOT', 'advcl', 'nsubj').
480:         head: Lowercased head word text.
481:         has_det: True if the token has a determiner child (e.g. "the wind").
482:         nli: Optional zero-shot NLI pipeline (not used for wind).
483:         sentence: Full sentence context for additional checks.
484:
485:     Returns:
486:         Tuple of (pronunciation, route) where pronunciation is 'why'nd' or 'win'd',
487:         and route describes the decision path for logging.
488:     """
489:     # Core verb rule: only return the verb pronunciation ('why'nd') when the tag
490:     # indicates a verb form AND the dependency is a core verbal governor.
491:     # This aligns exactly with the tightened complex_pos dep_rules for why'nd
492:     # (only ROOT/xcomp/ccomp with match_mode "all"). It prevents spaCy mis-tags
493:     # of noun "wind" as VBG/VBN in reduced clauses (e.g. "wind flinging", "wind rushing",
494:     # "Wind ripped") which commonly attach with advcl/relcl/acl.
495:     if (tag in VERB_PRESENT or tag in VERB_PAST) and dep in ("ROOT", "xcomp", "ccomp"):
496:         return "why'nd", "pos-verb-core"
497:
498:     # Strong noun bias via determiner: phrases like "the wind", "a wind", or "this wind"
499:     # are almost always the noun sense. Prefer 'win'd' even if spaCy mis-tagged the POS.
500:     if has_det:
501:         return "win'd", "det-noun"
502:
503:     # Default to noun for everything else. This includes:
504:     # - Correct noun tags (NN/NNS)
505:     # - Mis-tagged verbs in non-core dependencies (the common failure mode for these cases)
506:     # - Any other ambiguous or non-verbal attachments
507:     # The goal is to never let a non-core verbal attachment force the verb spelling for 'wind'.
508:     return "win'd", "pos-noun"
509:
510:
511: def decide_lead(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
512:     """
513:     Decide pronunciation for 'lead': VBD → 'led'; verb → 'leed'; adj/nn + nli → nli decision; noun → 'led'.
514:
515:     Args:
516:         tag: Fine-grained POS tag from spaCy.
517:         dep: Dependency relation.
518:         head: Lowercased head word.
519:         has_det: Whether a determiner child is present.
520:         nli: Optional NLI pipeline (used for adj/NN cases).
521:         sentence: Full sentence context (passed to nli_decide).
522:
523:     Returns:
524:         Tuple of (pronunciation, route) e.g. ("led", "pos-verb-past") or nli result.
525:     """
526:     # Explicit past tense tag gets 'led'.
527:     if tag == "VBD":
528:         return "led", "pos-verb-past"
529:     # Present verb tags get 'leed'.
530:     if tag in VERB_PRESENT:
531:         return "leed", "pos-verb"
532:     # For adjectives or nouns, fall back to NLI if available to disambiguate.
533:     if (tag in ADJ_TAGS or tag == "NN") and nli:
534:         return nli_decide(nli, sentence, "lead",
535:             "a person in a leading/supervising role",
536:             "leed",
537:             "the metal lead (Pb)",
538:             "led")
539:     # Default to noun sense 'led'.
540:     return "led", "pos-noun"
541:
542:
543: def decide_invalid(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
544:     """
545:     invalid: noun 'invalid' (disabled person) vs adj 'in-valid' (not valid).
546:
547:     The primary path is now the sentence-scanning is_noun_context heuristic
548:     which detects "an invalid.", "being an invalid" etc. even when spaCy
549:     assigns JJ + amod. This is the context heuristic requested to go beyond
550:     pure spaCy tag/dep (and the limited dep_rules in the JSON).
551:
552:     Args:
553:         tag, dep, head, has_det, nli, sentence: standard decider parameters.
554:
555:     Returns:
556:         (pronunciation, route)
557:     """
558:     # Run the noun heuristic first. It looks for surface patterns ("an invalid")
559:     # and common noun deps. This catches the bare-NP cases that previously
560:     # fell through to the adj branch because of amod mis-parses.
561:     if is_noun_context(tag, dep, head, has_det, sentence):
562:         return "invalid", "noun-heuristic"
563:
564:     if tag in ADJ_TAGS:
565:         # "of" prepositional object is a special noun case even under JJ tag.
566:         if dep == "pobj" and head == "of":
567:             return "invalid", "jj-pobj-of-noun"
568:
569:         # The remaining JJ cases that also have certain deps + det are treated
570:         # as the noun sense (copular/predicative "being an invalid" etc.).
571:         # These are kept for when the heuristic above didn't trigger but the
572:         # structural signals are still strong.
573:         if has_det and dep in {"nsubj", "dobj", "pobj", "nsubjpass", "attr", "acomp", "appos"}:
574:             return "invalid", "jj-but-noun"
575:         if dep in {"attr", "acomp", "appos"}:
576:             return "invalid", "jj-attr-noun"
577:
578:         # True adjective use (or any JJ that didn't match the noun patterns above).
579:         return "in-valid", "pos-adj"
580:
581:     # Default non-adjective tag → noun sense.
582:     return "invalid", "pos-noun"
583:
584:
585: _TEAR_EYES_AWAY = re.compile(
586:     r'\btear\b.{0,40}?\b(eyes?|gaze|attention|focus|sight)\b.{0,20}?\baway\b',
587:     re.IGNORECASE | re.DOTALL
588: )
589:
590:
591: def decide_tear(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
592:     """
593:     Decide pronunciation for 'tear': verb+eyes-away → 'tair'; verb+nli → nli; noun+through → 'tair'; noun+nli → nli.
594:
595:     Args:
596:         tag: Fine-grained POS tag from spaCy.
597:         dep: Dependency relation.
598:         head: Lowercased head word.
599:         has_det: Whether a determiner child is present.
600:         nli: NLI pipeline (used for most cases).
601:         sentence: Full sentence context (for special pattern and nli_decide).
602:
603:     Returns:
604:         Tuple of (pronunciation, route) e.g. ("tair", "pos-tear-eyes-away")
605:     """
606:     # Verb forms: special "tear ... eyes away" pattern takes 'tair'; else NLI.
607:     if tag in VERB_PRESENT or tag in VERB_PAST:
608:         if _TEAR_EYES_AWAY.search(sentence):
609:             return "tair", "pos-tear-eyes-away"
610:         return nli_decide(nli, sentence, "tear",
611:             "an action of ripping, shredding, or physically pulling something apart",
612:             "tair",
613:             "eyes watering, filling with tears, or about to cry",
614:             "teer")
615:     # Noun "through" object gets 'tair'.
616:     if dep == "pobj" and head == "through":
617:         return "tair", "pos-pobj-through"
618:     # Otherwise NLI for noun sense disambiguation.
619:     return nli_decide(nli, sentence, "tear",

(Showing lines 420-619 of 876. Use offset=620 to continue.)
</content>
```

**Tool: read**

**Input:**
```json
{
  "filePath": "/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py",
  "limit": 260,
  "offset": 620
}
```

**Output:**
```
<path>/home/danno/MyApps/BookFix/bookfix/ai/hybrid_deciders.py</path>
<type>file</type>
<content>
620:         "a rip, hole, cut, wound, injury, or physical damage in material or flesh, or a rift, gap, tunnel, throughway, or transitional opening",
621:         "tair",
622:         "a teardrop, teardrop shape, liquid from the eye, or emotional response",
623:         "teer")
624:
625:
626: def decide_polish(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
627:     """
628:     Decide pronunciation for 'polish': capitalized+NNP → 'pole-ish'; verb → 'pollish'; adj → 'pole-ish'; default → 'pollish'.
629:
630:     Args:
631:         tag: Fine-grained POS tag from spaCy.
632:         dep: Dependency relation.
633:         head: Lowercased head word.
634:         has_det: Whether a determiner child is present.
635:         nli: Optional NLI pipeline (unused for polish).
636:         sentence: Full sentence context (used for capitalization check).
637:
638:     Returns:
639:         Tuple of (pronunciation, route) e.g. ("pole-ish", "cap-proper")
640:     """
641:     # Detect capitalized proper-noun usage of "Polish" (the nationality/language).
642:     word_in_sent = next((w for w in sentence.split() if w.lower() == "polish"), None)
643:     if word_in_sent and word_in_sent[0].isupper() and tag == "NNP":
644:         return "pole-ish", "cap-proper"
645:     # Verb tags get 'pollish'.
646:     if tag in VERB_PRESENT or tag in VERB_PAST:
647:         return "pollish", "pos-verb"
648:     # Adjective tags get 'pole-ish'.
649:     if tag in ADJ_TAGS:
650:         return "pole-ish", "pos-adj"
651:     # Default to 'pollish' for nouns etc.
652:     return "pollish", "pos-default"
653:
654:
655: BASS_MUSIC_HEADS = {"case", "player", "guitar", "drum", "line", "clef", "man", "solo", "note"}
656: BASS_FISH_HEADS = {"boat", "fishing", "tournament", "lure", "angling", "farming"}
657: BASS_FISH_VERBS = {
658:     "caught", "catch", "fry", "frying", "fried", "cook", "cooking", "cooked",
659:     "ate", "eat", "eating", "hook", "hooked", "reel", "reeled", "land", "landed"
660: }
661:
662:
663: def decide_bass(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
664:     """
665:     Decide pronunciation for 'bass': compound+music → 'base'; compound+fish → 'bass'; verb+fish → 'bass'; else nli.
666:
667:     Args:
668:         tag: Fine-grained POS tag from spaCy.
669:         dep: Dependency relation.
670:         head: Lowercased head word (used for compound/verb heads).
671:         has_det: Whether a determiner child is present.
672:         nli: NLI pipeline (used for fallback disambiguation).
673:         sentence: Full sentence context (passed to nli).
674:
675:     Returns:
676:         Tuple of (pronunciation, route) e.g. ("base", "pos-compound-music") or nli result.
677:     """
678:     # Compound modifier: check head word lists for music vs fish.
679:     if dep == "compound":
680:         if head in BASS_MUSIC_HEADS:
681:             return "base", "pos-compound-music"
682:         if head in BASS_FISH_HEADS:
683:             return "bass", "pos-compound-fish"
684:     # Head verb related to fish activity → 'bass'.
685:     if head in BASS_FISH_VERBS:
686:         return "bass", "pos-verb-fish"
687:     # Fallback to NLI if no nli available.
688:     if not nli:
689:         return "base", "nli-disabled"
690:     try:
691:         q_music = "low-pitched sound, bass tones in music, a bass instrument (guitar, drum, etc.), or a bass musician"
692:         q_fish = "a species of fish (largemouth bass, sea bass, striped bass, etc.) caught in fishing"
693:         result = nli(sentence, candidate_labels=[q_music, q_fish], multi_label=False)
694:         scores = dict(zip(result["labels"], result["scores"]))
695:         if scores[q_fish] > 0.70:
696:             return "bass", f"nli=bass({scores[q_fish]:.2f})"
697:         return "base", f"nli=base({scores[q_music]:.2f})"
698:     except Exception:
699:         return "base", "nli-error"
700:
701:
702: _POSITIONAL_ROW = re.compile(r'\b(front|back|first|last|middle)\s+row\b', re.IGNORECASE)
703: _ROW_OF = re.compile(r'\brow\s+of\b', re.IGNORECASE)
704:
705:
706: def decide_row(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
707:     """
708:     Decide pronunciation for 'row': compound → 'ro'; npadvmod → 'ro'; verb → 'ro'; positional → 'ro'; row-of → 'ro'; else nli.
709:
710:     Args:
711:         tag: Fine-grained POS tag from spaCy.
712:         dep: Dependency relation.
713:         head: Lowercased head word.
714:         has_det: Whether a determiner child is present.
715:         nli: NLI pipeline (used for fallback).
716:         sentence: Full sentence context (for patterns and nli).
717:
718:     Returns:
719:         Tuple of (pronunciation, route) e.g. ("ro", "pos-compound") or nli result.
720:     """
721:     # Compound attachment → 'ro' (as in "row house").
722:     if dep == "compound":
723:         return "ro", "pos-compound"
724:     # npadvmod (e.g. "row after row") → 'ro'.
725:     if dep == "npadvmod":
726:         return "ro", "pos-npadvmod"
727:     # Verb tags → 'ro'.
728:     if tag in VERB_PRESENT or tag in VERB_PAST:
729:         return "ro", "pos-verb"
730:     # Positional phrases like "front row" → 'ro'.
731:     if _POSITIONAL_ROW.search(sentence):
732:         return "ro", "pos-positional"
733:     # "row of" construction → 'ro'.
734:     if _ROW_OF.search(sentence):
735:         return "ro", "pos-row-of"
736:     # Fallback NLI for "row" (argument) vs "ro" (line).
737:     return nli_decide(nli, sentence, "row",
738:         "a line, sequence, or series of things arranged in order, or in a row meaning one after another consecutively",
739:         "ro",
740:         "a loud verbal argument, quarrel, or shouting match between people",
741:         "rau")
742:
743:
744: def decide_bowed(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
745:     """
746:     Decide pronunciation for 'bowed': VBN+no-heads → 'boed'; else nli.
747:
748:     Args:
749:         tag: Fine-grained POS tag from spaCy.
750:         dep: Dependency relation.
751:         head: Lowercased head word.
752:         has_det: Whether a determiner child is present.
753:         nli: NLI pipeline (used for fallback).
754:         sentence: Full sentence context (for heads check and nli).
755:
756:     Returns:
757:         Tuple of (pronunciation, route) e.g. ("boed", "pos-vbn-deformation") or nli result.
758:     """
759:     # VBN without "head(s)" in sentence → deformation sense 'boed'.
760:     if tag == "VBN" and not re.search(r'\bheads?\b', sentence, re.IGNORECASE):
761:         return "boed", "pos-vbn-deformation"
762:     # Otherwise use NLI to choose between bent vs bowed (greeting).
763:     return nli_decide(nli, sentence, "bowed",
764:         "a physical object or structure (shelf, fence, roof, wood, limb) has been bent or curved by weight or force",
765:         "boed",
766:         "a person deliberately lowered their head or body as a gesture of respect or greeting",
767:         "boughed")
768:
769:
770: def decide_wound(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
771:     """
772:     Decide pronunciation for 'wound': noun/injury → 'woond'; past of 'wind' (coil) → 'wow'nd'; special case for 'wound its way'.
773:
774:     Args:
775:         tag: Fine-grained POS tag from spaCy.
776:         dep: Dependency relation.
777:         head: Lowercased head word.
778:         has_det: Whether a determiner child is present.
779:         nli: Optional NLI pipeline (unused for wound).
780:         sentence: Full sentence context (used for special idiom check).
781:
782:     Returns:
783:         Tuple of (pronunciation, route) e.g. ("woond", "pos-noun")
784:     """
785:     # Special case for the common verb idiom "wound its way" (past of 'wind').
786:     # This overrides even if spaCy mis-tags as NNS/NN (as seen in logs for "A tube ... wound its way").
787:     # User confirmed treating "wound the clock" / "wound its way" as past of 'wind' (wow'nd) is acceptable.
788:     if re.search(r'\bwound its way\b', sentence, re.IGNORECASE):
789:         return "wow'nd", "pos-verb-wind-its-way"
790:
791:     # Non-verb tags default to noun/injury sense 'woond'.
792:     if tag not in VERB_PAST and tag not in VERB_PRESENT:
793:         return "woond", "pos-noun"
794:     # Bare "VB" (base form) in this context treated as injure sense 'woond'.
795:     if tag == "VB":
796:         return "woond", "pos-vb-injure"
797:     # Otherwise (VBD etc.) treat as past of 'wind' → 'wow'nd'.
798:     return "wow'nd", "pos-verb-wind"
799:
800:
801: def decide_recreation(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
802:     """
803:     Decide pronunciation for 'recreation': compound → 'rek-reation'; else nli.
804:
805:     Args:
806:         tag: Fine-grained POS tag from spaCy.
807:         dep: Dependency relation.
808:         head: Lowercased head word.
809:         has_det: Whether a determiner child is present.
810:         nli: NLI pipeline (used for non-compound cases).
811:         sentence: Full sentence context (passed to nli).
812:
813:     Returns:
814:         Tuple of (pronunciation, route) e.g. ("rek-reation", "pos-compound-leisure") or nli result.
815:     """
816:     # Compound (e.g. "recreation room" meaning leisure) uses 'rek-reation'.
817:     if dep == "compound":
818:         return "rek-reation", "pos-compound-leisure"
819:     # Otherwise NLI between "re-kreation" (rebuilding) and "rek-reation" (leisure).
820:     return nli_decide(nli, sentence, "recreation",
821:         "the act of recreating or rebuilding something that previously existed",
822:         "re-kreation",
823:         "a hobby, pastime, leisure activity, sport, or something done for enjoyment and relaxation",
824:         "rek-reation")
825:
826:
827: def decide_jesus(tag: str, dep: str, head: str, has_det: bool, nli, sentence: str) -> Tuple[str, str]:
828:     """
829:     Decide pronunciation for 'Jesus': biblical/exclamation vs Spanish name via nli.
830:
831:     Args:
832:         tag: Fine-grained POS tag from spaCy.
833:         dep: Dependency relation.
834:         head: Lowercased head word.
835:         has_det: Whether a determiner child is present.
836:         nli: NLI pipeline (required for this decider).
837:         sentence: Full sentence context (passed to nli).
838:
839:     Returns:
840:         Tuple of (pronunciation, route) from nli_decide.
841:     """
842:     # Always delegate to NLI for biblical vs personal name disambiguation.
843:     return nli_decide(nli, sentence, "jesus",
844:         "the biblical Christian figure or used as a religious exclamation",
845:         "Jesus",
846:         "a Latin American or Spanish personal name (Jesús)",
847:         "heysous")
848:
849:
850: DECIDERS = {
851:     "record": decide_record,
852:     "records": decide_records,  # dedicated plural handler returning rekords/rekkurds + NNS-mistag gate
853:     "close": decide_close,
854:     "read": decide_read,
855:     "live": decide_live,
856:     "object": decide_object,
857:     "present": decide_present,
858:     "sow": decide_sow,
859:     "resume": decide_resume,
860:     "refuse": decide_refuse,
861:     "elaborate": decide_elaborate,
862:     "estimate": decide_estimate,
863:     "wind": decide_wind,
864:     "lead": decide_lead,
865:     "invalid": decide_invalid,
866:     "tear": decide_tear,
867:     "polish": decide_polish,
868:     "row": decide_row,
869:     "bass": decide_bass,
870:     "bowed": decide_bowed,
871:     "wound": decide_wound,
872:     "recreation": decide_recreation,
873:     "jesus": decide_jesus,
874: }
875:
876: NLI_WORDS = {"row", "bass", "bowed", "recreation", "jesus", "tear", "lead"}

(End of file - total 876 lines)
</content>
```

---

## Assistant (Plan · MiMo V2.5 Free · 18.7s)

_Thinking:_

The key change in hybrid_deciders.py is:

1. **`is_verb_context()` helper** (lines 20-80) — NEW. A comprehensive sentence-scanning heuristic for "live" verb detection. Checks:
   - Verb-clause deps (ROOT, xcomp, ccomp, advcl, relcl, acl)
   - Verb heads (do, does, did, can, could, will, would, must, have, has, had, be, is, are, was, were, to)
   - 8 sentence-level patterns (that live, live here, live longer, etc.)
   - Falls back to tag check

2. **`is_noun_context()` helper** (lines 83-121) — NEW. Sentence-scanning heuristic for "invalid" noun detection. Checks:
   - Surface patterns: "an invalid", "being an invalid", "as an invalid", "invalid." (sentence-final)
   - Extended noun deps: added `conj` and `ROOT` to the set
   - Determiner check

3. **`decide_invalid` updated** (lines 543-582) — Now calls `is_noun_context()` FIRST before the JJ checks. The old fallthrough bug (pos-adj for unrecognized deps) is still there but the heuristic catches the "an invalid" case before it reaches that branch.

4. **`decide_live` completely rewritten** (lines 263-316) — Now uses `is_verb_context()` as the primary decision path. Has special handling for "go live" idiom. Falls back to adj/adv only when the heuristic didn't claim verb.

5. **`decide_wind` rewritten** (lines 473-508) — Much tighter logic:
   - Only returns verb ('why'nd') when tag is verb AND dep is ROOT/xcomp/ccomp
   - `has_det` → noun ('win'd')
   - Default → noun

6. **`nli_decide()` helper** (lines 124-154) — NEW. Generic NLI helper that other deciders can call.

7. **`decide_tear` rewritten** (lines 591-623) — Uses NLI for most cases. Has special "tear ... eyes away" pattern.

8. **`decide_bass` rewritten** (lines 663-699) — Uses compound head word lists for music vs fish, fish activity verbs, and NLI fallback.

9. **`decide_row` rewritten** (lines 706-741) — Uses compound/npadvmod deps, positional phrases, "row of", and NLI fallback.

10. **`decide_bowed` rewritten** (lines 744-767) — VBN without "heads" → deformation; else NLI.

11. **`decide_wound` rewritten** (lines 770-798) — "wound its way" → wow'nd; non-verb → woond; VB → woond; VBD → wow'nd.

12. **`decide_recreation` rewritten** (lines 801-824) — Compound → rek-reation; else NLI.

13. **`decide_jesus` rewritten** (lines 827-847) — Always NLI.

The DECIDERS dict is the same 22 entries. NLI_WORDS is the same 7 words.

Now let me also check if there were changes to ai_choices.py or other files.

The ai_choices.py seems the same (2594 lines). Let me also check if there are any changes to the AI batch processing, the service.py, or the pos_dictionary.

Now let me also check if the AI service or other files changed:

**Tool: bash**

**Input:**
```json
{
  "command": "wc -l /home/danno/MyApps/BookFix/bookfix/ai/service.py /home/danno/MyApps/BookFix/bookfix/ai/pos_dictionary.py /home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py",
  "description": "Check line counts of key files"
}
```

**Output:**
```
  2050 /home/danno/MyApps/BookFix/bookfix/ai/service.py
   701 /home/danno/MyApps/BookFix/bookfix/ai/pos_dictionary.py
  2594 /home/danno/MyApps/BookFix/bookfix/processors/ai_choices.py
  5345 total

```

**Tool: bash**

**Input:**
```json
{
  "command": "git diff --stat HEAD 2>/dev/null || echo \"no git\"",
  "description": "Check recent changes",
  "workdir": "/home/danno/MyApps/BookFix"
}
```

**Output:**
```
 .ai_learning/choices_pos_dictionary.json |  431 +++---
 CLAUDE.md                                |   48 +-
 DocDNA/ai_instant/function_locator.json  | 2194 +++++++++++++++---------------
 DocDNA/docdna.db                         |  Bin 6463488 -> 7778304 bytes
 bookfix/ai/hybrid_deciders.py            |  626 ++++++++-
 bookfix/ai/review_window.py              |    6 +-
 bookfix/ai/service.py                    |   58 +-
 bookfix/config/config.json               |    4 +-
 bookfix/gui.py                           |    1 +
 bookfix/processors/ai_choices.py         |  805 ++++++++---
 data/choices.json                        |   68 +-
 data/replace.txt                         |    5 +
 data/settings.txt                        |    2 +-
 data/skip_choice.txt                     |    4 +
 project_state.json                       |   43 +-
 15 files changed, 2782 insertions(+), 1513 deletions(-)

```

---

## Assistant (Plan · MiMo V2.5 Free · 10.2s)

_Thinking:_

So the code has been significantly updated across multiple files. The main changes are:

1. `hybrid_deciders.py` - grew from ~407 lines to 876 lines (+626 insertions)
2. `ai_choices.py` - grew from ~1789 to 2594 lines (+805 insertions)
3. `service.py` - 58 line changes
4. `choices_pos_dictionary.json` - 431 line changes
5. `choices.json` - 68 line changes

The user said "the code updated. please update your output." - they want me to update the flowchart to reflect the current code. The `ai_choices.py` grew by 805 lines - that's substantial. Let me read the parts that changed.

Looking at what I've already read:
- Lines 640-1059 of ai_choices.py - this is the main processing loop, seems the same
- Lines 1273-1522 - _run_all_rules, seems the same
- Lines 1654-1853 - _get_consensus_from_rules, seems the same

Wait, the file went from ~1789 to 2594 lines. That's +805 lines. Let me check what's new - probably new methods were added.

Significant changes across 15 files. Let me find what was added to `ai_choices.py` (grew by ~805 lines):

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/danno/MyApps/BookFix && git diff HEAD -- bookfix/processors/ai_choices.py | head -200",
  "description": "Check ai_choices.py diff header"
}
```

**Output:**
```
diff --git a/bookfix/processors/ai_choices.py b/bookfix/processors/ai_choices.py
index ff1e23e..99eb7d2 100644
--- a/bookfix/processors/ai_choices.py
+++ b/bookfix/processors/ai_choices.py
@@ -11,13 +11,13 @@ from typing import List, Dict, Optional, Tuple, TYPE_CHECKING, Any

 # Ensure NLTK data is available for sentence tokenization
 try:
-    nltk.data.find('tokenizers/punkt')
+    nltk.data.find("tokenizers/punkt")
 except LookupError:
-    nltk.download('punkt', quiet=True)
+    nltk.download("punkt", quiet=True)
 try:
-    nltk.data.find('tokenizers/punkt_tab')
+    nltk.data.find("tokenizers/punkt_tab")
 except LookupError:
-    nltk.download('punkt_tab', quiet=True)
+    nltk.download("punkt_tab", quiet=True)

 if TYPE_CHECKING:
     from ..context import BookfixContext
@@ -25,6 +25,7 @@ if TYPE_CHECKING:
 from .choices import InteractiveChoiceProcessor
 from ..ai.service import BookfixAIService
 from ..ai.change_tracker import AIChangeTracker
+
 # Choices learning system retired — replaced by dep_rules (choices_pos_dictionary.json)
 # and curated examples in choices.json. Files preserved at .ai_learning/ for reference.
 from ..ai.pos_tagger import get_pos_tagger
@@ -72,10 +73,11 @@ class AIChoiceProcessor(InteractiveChoiceProcessor):

         # Initialize spaCy and lexicon
         import spacy
+
         try:
-            self.nlp = spacy.load('en_core_web_md')
+            self.nlp = spacy.load("en_core_web_md")
         except OSError:
-            self.nlp = spacy.load('en_core_web_sm')
+            self.nlp = spacy.load("en_core_web_sm")
         self.lexicon_loader = LexiconLoader()
         self.word_choices = self.lexicon_loader.get_all_words()

@@ -163,6 +165,7 @@ class AIChoiceProcessor(InteractiveChoiceProcessor):

         except Exception as e:
             import traceback
+
             log_message(f"Failed to initialize AI service: {e}", level="ERROR")
             log_message(traceback.format_exc(), level="ERROR")
             self.ai_enabled = False
@@ -206,10 +209,14 @@ class AIChoiceProcessor(InteractiveChoiceProcessor):
         os.makedirs(os.path.join(log_dir, "logs"), exist_ok=True)

         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
-        mode = "Rules-Only" if self.rules_only_mode else ("Hybrid" if self.ai_enabled else "Verify-All")
+        mode = (
+            "Rules-Only"
+            if self.rules_only_mode
+            else ("Hybrid" if self.ai_enabled else "Verify-All")
+        )
         total_words = len(ctx.choices) if ctx and ctx.choices else 0

-        for filename in ["rules_choices.log", "rule_reasoning.log"]:
+        for filename in ["rules_choices.log", "rule_reasoning.log", "aiprompt.txt"]:
             filepath = os.path.join(log_dir, "logs", filename)
             if os.path.exists(filepath):
                 try:
@@ -219,7 +226,7 @@ class AIChoiceProcessor(InteractiveChoiceProcessor):
                     log_message(f"Failed to delete {filename}: {e}", level="WARNING")

         header = f"""=== NEW PROCESSING RUN STARTED: {timestamp} ===
-Input file: {ctx.current_file_path if ctx and ctx.current_file_path else 'unknown'}
+Input file: {ctx.current_file_path if ctx and ctx.current_file_path else "unknown"}
 Mode: {mode}
 Total homographs configured: {total_words}
 ================================================
@@ -255,7 +262,11 @@ Total homographs configured: {total_words}
         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
         timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

-        total_changes = len(self.change_tracker.changes) if self.change_tracker and self.change_tracker.changes else 0
+        total_changes = (
+            len(self.change_tracker.changes)
+            if self.change_tracker and self.change_tracker.changes
+            else 0
+        )
         stats = dict(self.decision_stats)

         summary = f"""
@@ -293,8 +304,13 @@ Decision breakdown: {stats}
             try:
                 from transformers import pipeline as hf_pipeline
                 import torch
+
                 device = 0 if torch.cuda.is_available() else -1
-                self.nli = hf_pipeline("zero-shot-classification", model="roberta-large-mnli", device=device)
+                self.nli = hf_pipeline(
+                    "zero-shot-classification",
+                    model="roberta-large-mnli",
+                    device=device,
+                )
                 log_message("RoBERTa-MNLI NLI model initialized for hybrid deciders")
             except Exception as e:
                 log_message(f"Failed to initialize NLI model: {e}", level="WARNING")
@@ -311,9 +327,10 @@ Decision breakdown: {stats}
         """Load configuration from config.json."""
         import json
         from pathlib import Path
+
         config_path = Path(__file__).parent.parent / "config" / "config.json"
         if config_path.exists():
-            with open(config_path, 'r') as f:
+            with open(config_path, "r") as f:
                 return json.load(f)
         return {}

@@ -552,8 +569,13 @@ Decision breakdown: {stats}

         # Clear logs at start of processing
         import os
+
         log_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
-        log_files_to_clear = ["rule_reasoning.log", "rules_choices.log", "review_changes.log"]
+        log_files_to_clear = [
+            "rule_reasoning.log",
+            "rules_choices.log",
+            "review_changes.log",
+        ]
         for log_file in log_files_to_clear:
             log_path = os.path.join(log_dir, "logs", log_file)
             if os.path.exists(log_path):
@@ -579,6 +601,7 @@ Decision breakdown: {stats}
             self._ensure_pos_services()
             # Reload POS dictionary from disk to pick up manual edits
             from ..ai.pos_dictionary import reset_pos_dictionary
+
             reset_pos_dictionary()
             self._refresh_pos_dictionary()

@@ -729,7 +752,15 @@ Decision breakdown: {stats}
                             "confidence": 1.0,
                             "reason": explanation,
                         }
-                        self._log_comprehensive_rule_entry(word, match, {"replace_rule": replace_decision}, detected_pos_tag, replace_decision, "replace_rule", options)
+                        self._log_comprehensive_rule_entry(
+                            word,
+                            match,
+                            {"replace_rule": replace_decision},
+                            detected_pos_tag,
+                            replace_decision,
+                            "replace_rule",
+                            options,
+                        )
                         continue  # Skip all other rules and AI for this match
                 else:
                     log_message(
@@ -744,7 +775,7 @@ Decision breakdown: {stats}
                     )
                     self._current_sentence = (_before + _w + _after).strip()
                 except Exception:
-                    self._current_sentence = ''
+                    self._current_sentence = ""

                 # Run all local rules
                 all_rules, detected_pos_tag = self._run_all_rules(
@@ -756,86 +787,250 @@ Decision breakdown: {stats}
                 decision_source = None

                 # Check for consensus
-                ai_decision, decision_source = self._get_consensus_from_rules(
+                # Now returns 3-tuple to support disagreement gate: (decision, source, best_guess)
+                ai_decision, decision_source, best_guess = self._get_consensus_from_rules(
                     all_rules, context_full, word, options
                 )

                 if ai_decision:
-                    # Rule-based decision was made, log it directly
-                    self.decision_stats[decision_source] += 1
+                    if self.ai_verify_all and self.ai_service:
+                        # AI VERIFY ALL MODE: Rules produced a decision, but AI
+                        # must verify EVERY decision per config. Queue the item
+                        # for AI batch; store the rule decision as a safe fallback
+                        # so we don't lose work if the AI call fails.
+                        self._log_to_choices_log(
+                            f"Queuing '{word}' for AI verification (Verify ALL mode)."
+                        )
+                        if all_rules:
+                            _rules_summary = ", ".join(
+                                f"{r}={v['choice']}({v['confidence']:.2f})"
+                                for r, v in all_rules.items()
+                            )
+                            _ai_reason = f"rule consensus ({decision_source}); verify all — rules fired: {_rules_summary}"
+                        else:
+                            _ai_reason = (
+                                f"rule consensus ({decision_source}); verify all"
+                            )
+                        self._log_rule_choice(
+                            word, "→ AI verify", 0.0, f"queued [{_ai_reason}]"

```

---

## Assistant (Plan · MiMo V2.5 Free · 51.4s)

_Thinking:_

The diff is huge - 2782 insertions, 1513 deletions across 15 files. The user just wants me to update the flowchart based on the current code. The main structural changes I can see are:

1. **`_get_consensus_from_rules`** now returns a 3-tuple `(decision, source, best_guess)` - this was already reflected in my previous flowchart
2. **AI VERIFY ALL mode** was added - rules produce a decision but it still gets queued for AI verification, with the rule decision as fallback
3. **Disagreement path** now routes to contextualized AI (rich prompt) instead of batch
4. **`hybrid_deciders.py`** expanded from 407 to 876 lines - new helper functions `is_verb_context`, `is_noun_context`, `nli_decide`, and many deciders were rewritten

The ai_choices.py core structure is the same but the `process_choices_ai_review_mode` method was significantly restructured to add:
- AI VERIFY ALL mode (rules decide but AI verifies every decision)
- Disagreement gate with contextualized AI path
- Batch fallback for non-disagreement no-consensus cases

The flowchart I already provided was based on the current code - it was accurate. Let me re-read it and note that it already covers these changes. The user's "the code updated" may be referring to the hybrid_deciders.py changes.

Let me provide an updated, cleaner version of the flowchart that accounts for all changes.

Actually, looking at the diff more carefully, the core flow of ai_choices.py is the same as what I already documented. The key differences from the "old" version (which was what I originally read) are:
1. `_get_consensus_from_rules` returns 3-tuple (was 2-tuple)
2. The `if ai_decision:` branch was split into `ai_verify_all` and direct-apply
3. The `elif self.ai_enabled and self.ai_service:` branch was split into disagreement (contextualized) and batch paths
4. The `else` branch is rules-only mode

But my flowchart already captured all of this. So the main updates needed are:

1. **`hybrid_deciders.py`**: New helper functions, rewritten deciders for live, invalid, wind, tear, bass, row, bowed, wound, recreation, jesus
2. **`_get_consensus_from_rules`**: Now returns 3-tuple with best_guess
3. **AI VERIFY ALL mode**: Added in the `if ai_decision:` branch
4. **Disagreement → contextualized AI path**: Added with fallback to hybrid best_guess
5. **Non-disagreement → batch path**: Queues for batch processing

Let me present the updated flowchart.

The diff is massive (2782 insertions, 1513 deletions across 15 files). The core flow structure is the same as my previous flowchart, but with significant enhancements. Let me summarize the key changes:

**Key changes since my original flowchart:**

1. **`_get_consensus_from_rules`** now returns a 3-tuple: `(decision, source, best_guess)` — the `best_guess` carries the hybrid dict for the disagreement→AI path
2. **AI VERIFY ALL mode** added — rules decide but every decision still gets queued for AI verification, with rule decision as fallback
3. **Disagreement → contextualized AI** (rich prompt) — separate path from batch
4. **`hybrid_deciders.py`** massively expanded (407→876 lines): new `is_verb_context()`, `is_noun_context()`, `nli_decide()` helpers; rewritten deciders for `live`, `invalid`, `wind`, `tear`, `bass`, `row`, `bowed`, `wound`, `recreation`, `jesus`

Here is the **updated flowchart**:

---

## Updated AI Choices Processing Flowchart

### Main Loop: `process_choices_ai_review_mode`

```
START
  │
  ▼
┌─────────────────────────────────────────┐
│ For each word in ctx.choices             │
│   Find all regex matches in text        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ For each match occurrence               │
└──────────────┬──────────────────────────┘
               │
               ▼
        ┌──────────────────┐
        │ SKIP CHECK       │ ← 60-char window, normalize, substring match
        │ skip_choice      │   ~90 phrases (close, present, Jesus, etc.)
        └──────┬───────────┘
               │
         Match? ──YES──→ SKIP
               │ NO
               ▼
        ┌──────────────────┐
        │ Extract context  │ ← _extract_context() → "before [word] after"
        │ with [word]      │
        └──────┬───────────┘
               │
               ▼
        ┌──────────────────────────────────┐
        │ REPLACE RULE CHECK (highest)     │ ← context.split("[word]")
        │ Hardcoded phrase matching        │   Check left/right for direct
        │                                  │   replacement triggers
        └──────┬───────────────────────────┘
               │
         Match? ──YES──→ APPLY (1.0 conf) → log → continue to next match
               │ NO
               ▼
        ┌──────────────────────────────────┐
        │ Extract single sentence for log  │
        └──────┬───────────────────────────┘
               │
               ▼
        ┌──────────────────────────────────┐
        │ _run_all_rules(word, ctx)        │
        │                                  │
        │  1. spaCy POS tagger             │ ← get_token_and_dependency()
        │     → pos_token, dep_info, doc   │
        │                                  │
        │  2. HYBRID DECIDER               │ ← decide_<word>(tag, dep, head,
        │     (if word in DECIDERS)        │   has_det, nli, sentence)
        │     → 0.95 conf                  │
        │                                  │
        │  3. COMPLEX POS RULES            │ ← get_pronunciation_by_
        │     (dep_rules from JSON)        │   complex_pos_rules()
        │     → 0.98 conf                  │   Rule types: dep_relation,
        │                                  │   pos_category, pos_tag,
        │  4. SIMPLE POS TAG lookup        │   prep_child, advmod_child,
        │     → 0.80 conf                  │   cop_child, prev_token,
        │                                  │   capitalized
        │  5. SEMANTIC MATCHING            │   match_mode: ALL or ANY
        │     (nearby keywords)            │
        │                                  │
        │  6. ENTITY CONTEXT               │
        │     (NER check)                  │
        └──────┬───────────────────────────┘
               │
               ▼ all_rules dict
        ┌──────────────────────────────────┐
        │ _get_consensus_from_rules()      │
        │ → returns (decision, source,     │
        │            best_guess) 3-tuple   │
        └──────┬───────────────────────────┘
               │
    ┌──────────┴──────────────────────────┐
    │                                     │
    ▼ RULES-ONLY MODE                     ▼ HYBRID/VERIFY MODE
┌──────────────────┐               ┌──────────────────────────┐
│ Best rule conf   │               │ ① complex_pos present?   │
│ ≥ 0.75 threshold?│               │   YES → USE IT (0.98)    │
│ YES → use best   │               │                           │
│ NO  → defer      │               │ ② hybrid + pos BOTH      │
│ None → force     │               │   present & DISAGREE?     │
│  first option    │               │   YES → DISAGREEMENT GATE │
└──────────────────┘               │   (None, "disagreement",  │
                                   │    hybrid as best_guess)  │
                                   │                           │
                                   │ ③ hybrid alone? → USE(0.95)
                                   │                           │
                                   │ ④ pos alone, ≥0.80?       │
                                   │   YES → USE IT            │
                                   │                           │
                                   │ ⑤ Otherwise → None        │
                                   └──────────┬───────────────┘
                                              │
              ┌───────────────────────────────┼───────────────────────┐
              │                               │                       │
              ▼                               ▼                       ▼
        ┌──────────┐                  ┌──────────────┐        ┌──────────┐
        │ai_decision│                 │decision_source│       │best_guess│
        │ = dict   │                  │= "disagreement"│      │= hybrid  │
        └─────┬────┘                  └──────────────┘       │  dict    │
              │                                               └──────────┘
    ┌─────────┴──────────────────────────┐
    │                                    │
    ▼                                    ▼
┌────────────────────┐          ┌─────────────────────────┐
│ ai_verify_all?     │          │ ai_decision = None      │
│ (config flag)      │          │ (no consensus)          │
└────────┬───────────┘          └─────────┬───────────────┘
         │                                │
  YES    │    NO                   ┌──────┴──────────┐
  ▼      ▼                        │                 │
┌──────────────┐          ┌───────┴────────┐  ┌─────┴──────────┐
│ QUEUE for    │          │ disagreement?  │  │ Other no-      │
│ AI batch     │          │ source ==      │  │ consensus case │
│ (store rule  │          │ "disagreement" │  │                │
│ as fallback) │          │ & best_guess?  │  └──────┬─────────┘
└──────┬───────┘          └───────┬────────┘         │
       │                          │                  │
       │                  YES     │    NO            │
       │                  ▼       │    ▼             │
       │          ┌───────────────┴────┐  ┌──────────┴─────────┐
       │          │CONTEXTUALIZED AI   │  │ QUEUE for AI BATCH │
       │          │(rich per-item)     │  │ (efficient batch   │
       │          │ • definitions from │  │  prompt with       │
       │          │   choices.json     │  │  REFERENCE EXAMPLES│
       │          │ • POS tag clue     │  │  from choices.json)│
       │          │ • context_keywords │  └────────┬───────────┘
       │          │ • best_guess       │           │
       │          │ • show_reasoning   │           │
       │          └────────┬──────────┘           │
       │                   │                      │
       │          ┌────────┴────────┐             │
       │          │                 │             │
       │     SUCCESS           FAIL│             │
       │          │                 │             │
       │          ▼                 ▼             │
       │   ┌────────────┐  ┌──────────────┐      │
       │   │ USE AI     │  │ FALLBACK to  │      │
       │   │ DECISION   │  │ hybrid       │      │
       │   │ (source=   │  │ best_guess   │      │
       │   │  "llm")    │  │ (source=     │      │
       │   └────────────┘  │  "hybrid")   │      │
       │                   └──────────────┘      │
       │                                         │
       │           ┌─────────────────────────────┘
       │           │
       │           ▼
       │  ┌──────────────────────────┐
       │  │ AI BATCH PROCESSING      │
       │  │                          │
       │  │ analyze_homographs_batch │
       │  │ • Ollama: 1-at-a-time    │
       │  │ • Other: true batching    │
       │  │                          │
       │  │ For each item:           │
       │  │  • Prompt with choices   │
       │  │    .json examples        │
       │  │  • Parse JSON response   │
       │  │  • Validate spelling     │
       │  └──────────┬───────────────┘
       │             │
       │       ┌─────┴─────┐
       │       │           │
       │  SUCCESS      FAIL│
       │       │           │
       │       ▼           ▼
       │ ┌──────────┐ ┌──────────────┐
       │ │ USE AI   │ │ FALLBACK to  │
       │ │ decision │ │ stored rule  │
       │ │ (source= │ │ decision     │
       │ │  "llm")  │ │ (original    │
       │ └──────────┘ │  source)     │
       │              └──────────────┘
       │
       ├─────────────────────┐
       │                     │
       │  (both batch &      │
       │   verify_all paths  │
       │   converge here)    │
       │                     │
       ▼                     ▼
┌─────────────────────────────────────────┐
│ APPLY AI DECISION                       │
│ • Log to choices_log                    │
│ • Log comprehensive rule entry          │
│ • Apply to change_tracker               │
│ • Update decision_stats                 │
└─────────────────────────────────────────┘
```

### Rule Priority (Hybrid/Verify Mode)

| Priority | Rule | Confidence | When it wins |
|----------|------|-----------|-------------|
| 1 | REPLACE rules | 1.0 | Context phrase matches (checked first, before rules) |
| 2 | complex_pos (dep_rules) | 0.98 | Structural dep_rules from JSON match |
| 3 | **Disagreement gate** | — | hybrid & pos disagree → contextualized AI |
| 4 | hybrid (decide_\<word\>) | 0.95 | Only hybrid fired, or hybrid+pos agree |
| 5 | pos (simple tag lookup) | 0.80 | Only pos fired, conf ≥ 0.80 |
| 6 | AI (contextualized) | var | Disagreement path — rich per-item prompt |
| 7 | AI (batch) | var | No consensus / verify-all — batch prompt |

### Hybrid Deciders — Key Helpers (NEW)

```
is_verb_context(tag, dep, head, sentence) → bool
  Used by: decide_live
  Checks:
    1. dep ∈ {ROOT, xcomp, ccomp, advcl, relcl, acl} → True
    2. head ∈ verb_heads (do/did/can/will/have/be/is/to) → True
    3. 8 sentence patterns: "that live", "live here", "live longer",
       "do ... live", "people ... live", etc. → True
    4. tag ∈ VERB_PRESENT/VERB_PAST → True
    5. else → False

is_noun_context(tag, dep, head, has_det, sentence) → bool
  Used by: decide_invalid
  Checks:
    1. Surface patterns: "an invalid", "being an invalid",
       "as an invalid", "invalid." (sentence-final) → True
    2. dep ∈ {nsubj, dobj, pobj, attr, appos, conj, nsubjpass, ROOT} → True
    3. has_det && dep ∈ {nsubj, dobj, pobj, attr, acomp, appos} → True
    4. else → False

nli_decide(nli, sentence, word, q_a, label_a, q_b, label_b) → (pron, route)
  Used by: decide_lead, decide_tear, decide_bass, decide_row,
           decide_bowed, decide_recreation, decide_jesus
  RoBERTa zero-shot: picks between two pronunciation hypotheses
  Fallback: label_a if nli disabled or error
```

### Data Flows

```
skip_choice.txt ─────→ ctx.skip_choice ────→ 60-char window substring match
                       (~90 phrases)

choices.json ────────→ options, definitions, ──→ AI prompts (batch + contextualized)
                       examples, context_keywords

choices_pos_         → dep_rules ──────────→ complex_pos evaluator
dictionary.json        (dep_relation,         (match_mode: ALL/ANY)
                        pos_category,
                        pos_tag,
                        prep_child,
                        advmod_child,
                        cop_child,
                        prev_token,
                        capitalized)

hybrid_deciders.py   → 22 decide_<word>() ──→ hybrid rule (0.95 conf)
                       functions               with NLI_WORDS fallback

NLI_WORDS            → 7 words (row, bass, ──→ RoBERTa-large-MNLI
  = {row, bass,        bowed, recreation,      zero-shot classification
     bowed, recreation, jesus, tear, lead)
     jesus, tear, lead}
```

### Key Configuration Flags

| Flag | Location | Effect |
|------|----------|--------|
| `DISAGREEMENT_TO_AI` | Thresholds config | Enables/disables disagreement gate (default: True) |
| `ai_verify_all` | Processing mode | Queues every rule-decided item for AI verification |
| `rules_only_mode` | Processing mode | No AI at all; forces first option or defers below 0.75 threshold |
| `ai_enabled` | Processing mode | Enables AI batch + contextualized paths |





---
