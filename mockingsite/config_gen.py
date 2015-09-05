import sys
import os
import re

# Get the patterns that look like an environmental variable
pattern = re.compile("\$[A-Z]+")

# The template file
templateFile = sys.argv[1]

# the config file
configFile = sys.argv[2]

# dictionary mapping the env. variables to it's values
substDict = {}

# We read the contents of the template file
contents = open(templateFile, "r").read()

# We extract possible candidates of environmental variables
placeHolders = pattern.findall(contents)


# If an environmental variable exist in that name we populate the dictionary
for placeHolder in placeHolders:
	if os.environ.get(placeHolder[1:]):
		substDict [placeHolder.replace('$', '\$')] = os.environ.get(placeHolder[1:])

# We are ready to substitute the environmental variables
searchPattern = re.compile('(' + '|'.join(substDict.keys()) + ')')
result = searchPattern.sub (lambda x: substDict[x.group().replace('$', '\$')], contents)

# We write the generate config into config file
with open (configFile, 'w') as f: f.write (result)
