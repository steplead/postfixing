
import re
import json

# This script finds legacy JSON tool definitions in errorpost.html
# and replaces them with Level 5 HTML Calculator structures.

def generate_html(tool_id, data):
    title = data.get('title_en', tool_id)
    theme_color = "#3b82f6" # default blue
    bg_color = "#eff6ff"
    
    theme = data.get('theme', 'blue')
    if theme == 'amber': theme_color="#f59e0b"; bg_color="#fffbeb"
    if theme == 'green': theme_color="#22c55e"; bg_color="#f0fdf4"
    if theme == 'rose': theme_color="#f43f5e"; bg_color="#fff1f2"
    if theme == 'slate': theme_color="#64748b"; bg_color="#f8fafc"

    html = f"""
<div data-itb-calculator="{tool_id}" style="background: {bg_color}; border-left: 5px solid {theme_color}; padding: 24px; margin: 24px 0; border-radius: 6px;">
    <h3 style="margin-top: 0; color: {theme_color}; font-size: 1.3em;">{title}</h3>
    <div class="itb-inputs">"""

    for inp in data.get('inputs', []):
        label = inp.get('label', inp['name'])
        name = inp['name']
        val = ""
        type_ = "text"
        
        # Build Input Field
        field_html = ""
        if 'options' in inp:
            opts = ""
            for o in inp['options']:
                opts += f'<option value="{o}">{o}</option>'
            field_html = f'<select data-var="{name}">{opts}</select>'
        else:
            if inp.get('type') == 'number':
                type_ = "number"
                val = str(inp.get('min', 0))
                step = str(inp.get('step', 1))
                field_html = f'<input type="number" data-var="{name}" value="{val}" step="{step}">'
            else:
                field_html = f'<input type="text" data-var="{name}" placeholder="..."> '

        html += f"""
        <div class="itb-input-group">
            <label>{label}:</label>
            {field_html}
        </div>"""

    # Add Hidden Button
    html += """
        <button style="display:none !important;" type="button">Calculate</button>
    </div>
    
    <div class="itb-outputs" data-itb-results aria-live="polite">"""

    for out in data.get('outputs', []):
        label = out.get('label', out['name'])
        key = out['name']
        html += f"""
        <div class="itb-output-group">
            <label>{label}:</label>
            <strong data-itb-output="{key}">-</strong>
        </div>"""

    html += """
    </div>
</div>"""
    return html

# Read file
with open('found_tools_phase4.json', 'r', encoding='utf-8') as f:
    tools_data = json.load(f)

tools_map = {t['id']: t for t in tools_data}

with open('errorpost.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <pre> blocks
# Regex to find <code class="itb-tool">{...}</code>
# We iterate through findall to handle replacements carefully
matches = re.findall(r'(<pre><code class="itb-tool">\s*({.*?})\s*</code></pre>)', content, re.DOTALL)

print(f"Found {len(matches)} blocks to replace.")

new_content = content

for full_match, json_str in matches:
    try:
        data = json.loads(json_str)
        tid = data.get('id')
        if tid and tid in tools_map:
            print(f"Converting {tid}...")
            new_html = generate_html(tid, data)
            # Replace logic
            # Using simple replacement might be risky if duplicates exist, but these look unique
            new_content = new_content.replace(full_match, new_html)
    except Exception as e:
        print(f"Error parsing match: {e}")

with open('errorpost.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Conversion complete.")
