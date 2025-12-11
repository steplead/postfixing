---
description: Standard Protocol for fixing, repairing, or updating WordPress Calculator Posts.
---

# Standard Fix Protocol

Before attempting any fixes on `errorpost.html` or other calculator posts, you **MUST** step through this protocol:

1.  **Mandatory Rule Check**:
    *   Read `AGENT_RULES.md` in the project root.
    *   *Why*: This file contains critical safety protocols (Hex Encoding, anti-caching, legacy cleanup) that prevent site outages.

2.  **Verify State (Negative Verification)**:
    *   Do not assume a tool is missing just because it doesn't render.
    *   Run `grep -c "tool-id" filename.html` to check for physical presence.

3.  **Atomic Operations**:
    *   If moving a tool, ensuring you (1) Inject, (2) Delete old, (3) Verify count == 1.

4.  **Use the Build System**:
    *   Do not write inline JS. Update `generate_hex_v5.py` and run it to regenerate the hex payload.

5.  **Cache Busting**:
    *   If the user claims the fix didn't work but your verification passes, update the visible Version Tag in the HTML header (Rule 20).
