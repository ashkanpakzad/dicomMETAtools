import csv
import json

# Open the CSV
f = open( 'requiredtags.csv', 'rU' )
# Change each fieldname to the appropriate field name. I know, so difficult.
reader = csv.DictReader( f, fieldnames = ( "tag1","tag2","fieldname","value","copy original" ))
# Parse the CSV into JSON
out = json.dumps( [ row for row in reader ] )
print("JSON parsed!")
# Save the JSON
f = open( 'requiredtags.json', 'w')
f.write(out)
print("JSON saved!")
