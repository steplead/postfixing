import re
import json

# Read the HTML file
try:
    with open('errorpost.html', 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print("Error: errorpost.html not found.")
    exit(1)

# Pattern to find the JSON within <pre ...><code class="itb-tool">
# Adhering to Rule 12: Robust Regex for attributes
pattern = r'<pre[^>]*><code class="itb-tool">\s*(.*?)\s*</code></pre>'
matches = re.findall(pattern, content, re.DOTALL)

tools_found = []

for json_str in matches:
    try:
        # Clean up potential HTML entities if any (basic ones)
        json_clean = json_str.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        tool_json = json.loads(json_clean)
        tools_found.append(tool_json)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic string: {json_str[:100]}...")

print(f"Found {len(tools_found)} tools.")

# Save to found_tools_phase9.json
with open('found_tools_phase9.json', 'w', encoding='utf-8') as f:
    json.dump(tools_found, f, indent=2)
print("Saved to found_tools_phase9.json")
