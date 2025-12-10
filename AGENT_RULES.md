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

---
*This file is the single source of truth for post repairs.*
