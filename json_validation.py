import re
import json

with open("data/gdp_with_continent_filled.json", "r") as f:
    raw = f.read()

fixed = re.sub(r'\bNaN\b', 'null', raw)
fixed = re.sub(r'#@\$!\\', 'null', fixed) 

json.loads(fixed) 

with open("data/gdp_with_continent_filled.json", "w") as f:
    f.write(fixed)

print("Done! File fixed in place.")