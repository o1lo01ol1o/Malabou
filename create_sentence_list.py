import sys
import re

def main(path_to_file):
	regex = r"\w+|\S"
	output = []
	with open(path_to_file, 'r') as in_file:
		for line in in_file:
			sentence = []
			for match in re.finditer(regex, line, re.MULTILINE | re.UNICODE):
				sentence.append(match.group())
			if(len(sentence) > 0):
				output.append(sentence)
	print(output)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print('Error: Pass a file to read.', file=sys.stderr)
		sys.exit(1)
	else:
		main(sys.argv[1])