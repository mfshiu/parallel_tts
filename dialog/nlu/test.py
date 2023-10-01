import re

text = '''Primary (main category): Greeting
Secondary (minor category): Normal

So the primary category is "Greeting" and the secondary category is "Normal".'''

# Regular expressions to match primary and secondary categories
primary_re = r'Primary \(main category\):\s*(\w+)'
secondary_re = r'Secondary \(minor category\):\s*(\w+)'

# Search for primary and secondary categories
primary_match = re.search(primary_re, text)
secondary_match = re.search(secondary_re, text)

# Extract and print the values
if primary_match and secondary_match:
    primary_category = primary_match.group(1)
    secondary_category = secondary_match.group(1)
    print(f'The primary category is "{primary_category}" and the secondary category is "{secondary_category}".')
else:
    print('Categories not found.')
