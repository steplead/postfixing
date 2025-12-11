# AGENT RULES: WordPress Post Fixing Protocol

**CRITICAL INSTRUCTION**: ANY Agent attempting to "fix", "repair", or "update" a calculator post in this project MUST follow this protocol.

## Rule 1: The "Nuclear" Option (Hex Encoding)
**NEVER** use inline JavaScript or `data-formula` attributes. WordPress filters will corrupt them.
*   **Action**: You MUST convert all Calculator Logic (`window.OZ_FORMULAS`) into a **Hexadecimal String**.
*   **Implementation**:
    1.  Get the pure JS logic string.
    2.  Encode it to Hex (0-9, A-F only).
    3.  Store it in: `<input type="hidden" id="oz-safe-code" value="HEX_STRING_HERE">`.
    4.  Use the **Standard v12 Loader** (see below) to decode and execute it.

## Rule 2: The "Clean Fragment" Standard
**NEVER** output a full HTML document (with `<html>`, `<body>`, `<main>`).
*   **Reason**: Pasting these tags into WordPress creates nested pages, causing huge white gaps and layout breakage.
*   **Action**: Output **ONLY** the content fragment.
    *   ✅ `<style>...</style>`
    *   ✅ `<input type="hidden">`
    *   ✅ `<script>...</script>`
    *   ✅ `<h1>Title</h1>`
    *   ✅ Content...

## Rule 3: The Standard v12 Loader
You MUST use this exact script to load the Hex payload. Do not write custom loaders unless requested.

```html
<script>!function(){if(!window.ozExecuteCalc)window.ozExecuteCalc=function(){console.warn("OZ: Loading...")};function l(){try{var e=document.getElementById("oz-safe-code");if(e){var r=e.value.replace(/[^0-9A-Fa-f]/g,"");if(r)window.eval(r.match(/.{1,2}/g).map(function(n){return String.fromCharCode(parseInt(n,16))}).join(""))}}catch(e){console.error(e)}}"complete"===document.readyState?l():window.addEventListener("load",l)}();</script>
```

## Rule 4: Verification
Before marking task done, verify:
1.  Are there any `’` (smart quotes) in the JS? (Should be none, because it's Hex).
2.  Did you look for `<body>` tags? (Should be none).
3.  Did you test the Hex string decoding?

## Rule 5: Stealth Mode (Avoid Theme Conflicts)
If the user reports "Uncaught TypeError" or "IntersectionObserver" errors:
*   **Cause**: The Theme is trying to hook into `<section>` tags in your injected code.
*   **Fix**: Replace all `<section>`, `<article>`, `<header>` tags with generic `<div class="oz-section">`.
*   **Wrap**: Enclose the entire fragment in `<div class="oz-calculator-app">`.

## Rule 6: The "No Response" Troubleshooting Protocol
If a calculator yields "No Response" (clicks do nothing), you MUST proceed through these checks **One by One** until fixed.

### Phase 1: The "Silent Failure" Checklist
1.  **Check Schema (Variable Mismatch)**:
    *   *Symptom*: Calculator runs but finds 0 inputs.
    *   *Fix*: Ensure all inputs use `data-var="name"`. **DO NOT** use `data-itb-input` or `name` attributes.
2.  **Check Smart Quotes**:
    *   *Symptom*: `SyntaxError: Invalid or unexpected token`.
    *   *Fix*: Ensure NO curly quotes (`’`, `“`, `”`) exist in the JS/HTML. Use strict Hex Encoding (Rule 1).
3.  **Check Filter Corruption (Regex Death)**:
    *   *Symptom*: Loader runs but logic never executes (random/unstable).
    *   *Cause*: Security plugins strip `/[^0-9]/` from the loader regex.
    *   *Fix*: **ESCALATE to Level 2 (External Reference)** immediately.

### Phase 2: Escalation (Level 2)
If Phase 1 fails or results are unstable ("works sometimes"):
*   **Action**: Abandon Inline Hex.
*   **Implement**: **External Reference**.
    1.  Extract logic to `oz-calc-vXX.js`.
    2.  Upload to Media Library.
    3.  Link in post: `<script src="/path/to/oz-calc-vXX.js"></script>`.

## Rule 7: Environmental Troubleshooting (The "Ghost" & "Zombie" Protocol)
When code is correct but fails on the Live Site, it is an Environment Issue.

### 1. The "Ghost" Autosave (Reverting Changes)
*   **Symptom**: You delete a button/code, update, but it comes back.
*   **Cause**: WordPress Autosave conflict.
*   **Fix**:
    *   **User**: Disable in `wp-config.php`: `define('AUTOSAVE_INTERVAL', 86400);`
    *   **Agent**: Instruct user to "Paste & Immediately Update" to overwrite the ghost.

### 2. The "Zombie" Button (WP Auto-Correct)
*   **Symptom**: Code has no button, but WP injects one because "Forms need buttons."
*   **Fix**: Do NOT delete the button. **Hide it** instead.
    *   `<button style="display:none !important;"></button>`
    *   This satisfies WP's validator while keeping the UI clean.

### 3. The "NaN" Error (Attribute Mismatch)
*   **Symptom**: Calculator runs but outputs `NaN` or `0`.
*   **Cause**: HTML input uses `data-itb-input` but JS expects `data-var`.
*   **Fix**: **Strictly** use `data-var="paramName"` on ALL inputs.

### 4. The "Plugin Shield" (Crash Survival)
*   **Symptom**: Calculator never loads because *another* plugin (e.g., `load-more.js`) crashed.
*   **Fix**: Decouple the loader using `setTimeout`.
    *   `setTimeout(function() { ... loader ... }, 500);`
    *   This lets the other plugin die peacefully before we start.

## Rule 8: Legacy Tool Restoration Protocol (Mass Hydration)
When you encounter a post with "Dead Code" (raw JSON blocks, shortcodes, or placeholders):
*   **Symptom**: User sees `<pre>{"id": "tool-name"}</pre>` or `[itb-tool]` instead of a calculator.
*   **Fix**: You must **Hydrate** the dead code.
    1.  **Extract**: Parse the JSON/Shortcode to understand the inputs/logic.
    2.  **Convert**: Generate standard "Level 5" HTML containers with `data-var` inputs.
    3.  **Implement**: Write the JS logic into the Hex Payload (`generate_hex_vXX.py`).
    4.  **Replace**: Overwrite the dead blocks with the new HTML.
    5.  **Clean Sweep**: Run `grep` to ensure NO other JSON blocks (`{"id":`) remain in the file. Users often report the *first* one they see; there may be more.
*   **Goal**: Zero dead code. If it looks like a tool, make it work.

## Rule 9: Codebase Management (The "App" Pattern)
For complex, multi-tool posts, treat the solution as an Application, not a Snippet.
*   **Central Logic Core**: Maintain a single Python script (`generate_hex_vX.py`) that contains the JS logic for ALL tools. This is your "Build System".
*   **Dynamic Conversion**: Do not hardcode HTML. Use a converter script (`convert_legacy.py` or similar) to transform JSON/Defs into Level 5 HTML.
*   **Workflow**:
    1.  Update Logic in Python (`generate_hex_vX.py`).
    2.  Update Structure in JSON/Defs.
    3.  Run Builder -> Output `hex_payload`.
    4.  Inject into `post.html`.

## Rule 10: Content Integrity (The "User Diff" Protocol)
If the user provides new post content via a chat diff or message (e.g., "The following changes were made..."):
*   **Action**: You MUST explicitly write this content to the target file (`errorpost.html`) using `write_to_file`.
*   **Reason**: The file on disk may not auto-update from the chat context. Scanners will fail (find 0 tools) if you scan the old file.
*   **Trigger**: Always verify file content matches the user's intent *before* running scanners.

## Rule 11: Workspace Hygiene (Clean As You Go)
This project generates temporary assets. Do not leave them rotting.
*   **Scanner Scripts**: Delete `scan_*.py` immediately after verification.
*   **JSON Dumps**: Delete `found_tools_*.json` immediately after verification.
*   **Why**: Stale JSON files can confuse future phases. Keep the workspace pure.

---
*This file is the single source of truth for post repairs.*

## Rule 12: Robust Conversion (The "Dirty Input" Protocol)
Real-world data is messy. Scanners and Converters must be defensive.
*   **Regex Flexibility**: When scanning HTML, ALWAYS handle attributes.
    *   ❌ `r'<pre>...</pre>'` (Fails if class/style exists)
    *   ✅ `r'<pre[^>]*>...</pre>'` (Robust)
*   **ID Fallback**: If a tool definition lacks an ID, Generate one.
    *   **Logic**: `slugify(name)` -> `tool-name`.
    *   **Never Crash**: Do not assume `['id']` exists. Use `.get('id')` and provide a default.
*   **Key Sanitization**: JSON keys vary (e.g., `id` vs `name`). Check both or normalize before generating code.

## Rule 13: The "Reactive" Event Protocol (Inputs vs Selects)
Users expect instant feedback. Your engine must listen to the right events.
*   **Symptom**: "No Output" when changing Dropdowns (`<select>`) or Radio Buttons.
*   **Cause**: The `input` event is unreliable for non-text inputs on some browsers.
*   **Fix**: You MUST listen for **BOTH** `input` and `change` events.
    ```javascript
    document.addEventListener('input', updateCalc);
    document.addEventListener('change', updateCalc); // Mandatory for Select/Radio
    ```

## Rule 14: The "Scope Safety" Protocol (Silent Crash Prevention)
Calculators run in a delicate environment. A single syntax error kills the *entire* engine silently.
*   **Symptom**: Engine never loads (`ozExecuteCalc is not a function`). No errors in console (unless decoded manually).
*   **Cause**: Pasting logic *outside* the `Object.assign` block or leaving trailing commas/unclosed braces.
*   **Fix**:
    1.  **Structure**: Verify `Key: Function` pairs are strictly inside `Object.assign(window.OZ_FORMULAS, {HERE})`.
    2.  **Validation**: If generating via Python, print the JS string and visually verify the structure before Hex encoding.
    3.  **Closure**: Ensure the main closure `(function(){ ... })();` is balanced.

## Rule 15: Verification & Persistence Protocol
When users provide content via chat (paste/diffs) or when tools "silently" modify files:
1.  **Trust But Verify**: NEVER assume `replace_file_content` worked if targeting by line number on a dynamic file.
2.  **Payload Delta**: When injecting huge payloads (like Hex), check the **File Size** before and after.
    *   *Example*: size +1kb = Something broke. size +15kb = Logic injected.
3.  **Disk Sync**: If a file seems stale after a chat paste, confirm with `ls -l` timestamp. If stale, ask user to **Save**.

## Rule 16: Robust Injection (The "Anchor" Protocol)
Targeting line numbers in large, shifting files (`generate_hex.py` > 1000 lines) is a gamble.
*   **Avoid**: Hardcoded Line Numbers (e.g., `StartLine: 1199`).
*   **Prefer**: Context Anchors.
    *   Find: `// END OF LOGIC` or `window.OZ_FORMULAS =`.
    *   Replace: `// New Logic Here\n// END OF LOGIC`.
*   **Fallback**: If `replace_file_content` fails with "empty target", **Re-Read** the file immediately to get fresh line numbers. Do not guess.

## Rule 17: The "Golden Egg" Protocol (Payload Integrity)
**CRITICAL**: The Hex Payload is the *only* thing that makes the calculator work. It is fragile.
*   **The Trap**: When resizing/refactoring HTML (removing `<section>` or dead code), it is easy to accidentally delete the `<input id="oz-safe-code">` line or the standard loader.
*   **The Check**: Before marking a task "Fixed":
    *   **Visual**: Is `<input type="hidden" id="oz-safe-code" ...>` present?
    *   **Size**: Is the file size > 50KB? (Hex payloads are huge).
    *   **Scope**: Did your regex `replace` accidentally swallow the footer?

## Rule 18: Escalation Velocity (Don't Panic-Switch)
When a fix doesn't work effectively immediately:
*   **Protocol**: Do NOT switch methods (e.g., Inline -> External) until you have verified the *basics* of the current method.
*   **Why**: We often switch to External JS because we *think* Inline failed, when in reality:
    1.  The payload was missing (Zero KB).
    2.  There was a typo in the ID.
    3.  A legacy block was visible above the real calculator.
*   **Rule**: "Fix the Implementation" before "Changing the Architecture." Verify logic presence first.

## Rule 19: Atomic Relocation (The "Teleport" Rule)
*   **The Trap**: When asking to "Move Tool X to Section Y", agents often *copy* Tool X to Y but fail to *delete* it from the original spot.
*   **Result**: Duplicate calculators (one working, one legacy).
*   **Protocol**: A "Move" operation is ALWAYS two steps:
    1.  **Inject** at new location.
    2.  **Delete** from old location (Regex/Line Range).
    3.  **Verify**: Grep for the ID. Count should be **exactly 1**.

## Rule 20: The "Cache-Buster" Visual Protocol
*   **Symptom**: User reports "I still see the old version" or "Tool is missing" despite verification.
*   **Cause**: Browser Caching (common with large HTML/Hex payloads).
*   **Fix**: Do not argue with verified files.
    *   **Action**: Append a visible **Version Tag** to the H1 or Tool Title (e.g., `<small>v5.2</small>`).
    *   **Instruct**: Tell user to "Refresh until you see 'v5.2'".
    *   **Why**: This provides a shared truth mechanism between Agent (Server) and User (Client).

## Rule 21: Negative Verification (The "Ghost Hunter" Protocol)
*   **Symptom**: "Tool X is missing."
*   **Action**: Do not just check if it renders. Check if it *exists*.
    *   **Grep**: `grep -c "tool-id" file.html`
    *   **Zero**: It's truly missing. Re-inject.
    *   **One**: It's there but hidden/broken (JS error, style `display:none`).
    *   **Two+**: It's duplicated (See Rule 19).
