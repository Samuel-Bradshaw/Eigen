# Author: Sam Bradshaw
# 25/10/2021
# Developed using python 3.10

import os
import getopt
import sys
import traceback
from WordData import WordData
from CLIOption import CLIOption

OPTIONS = {
	CLIOption('file', 'f', 'output file to record results in. If this is not included, results are printed to console.', 'filename'),
	CLIOption('num', 'n', 'specifies the number of words to include in result. By default, 15 are retrieved.', 'n'),
	CLIOption('omit_sentences', 'o', 'omit sentences that word occured in from the results.'),
	CLIOption('all', 'a', 'retrieve all results. This overrides num option.'),
	CLIOption('min_count', 'm', 'set a minimum number of times a word should appear in texts for it to be included in results.', 'min'),
	CLIOption('interested_in', 'i', 'Choose the type of words you want to see in results from "verbs", "adjectives", "nouns". By default, all nouns, adjectives, numerical, and foreign words are included in results.', 'type'),
	CLIOption('lemmatize', 'l', 'lemmatize words when extracting data. By default words are not lemmatized.'), # Warning: Seems buggy, possibly due to limitations of wordnet lemmatizer 
	CLIOption('help', 'h', 'print this help message.')
} 
""" Set of command line options"""


def extract_word_data(input_files, file=None, num=15, omit_sentences=False, all=False, min_count=None, interested_in=None, lemmatize=False):
	"""
	Extracts word data from files in dir and outputs data on interesting words, 
	including total number of occurences and which files they were found in.

	Args:
		input_files: List of input files.
		file: File to output results to. If None (default), then results are printed to console.
		num: Number of words to include in results.
		omit_sentences: If True, the sentences that each word occured in are omitted in results. Else sentences are included.
		all: Include all results in output (overrides num).
		min_count: The miniumum number of times a word needs to appear in the data for it to be included in the results.
		interested_in: A list of word types to be returned in the results. Valid entries are "verbs", "adjectives", or "nouns".
		lemmatize: If True, all words are lemmatized when added to data. E.g. "walking" -> "walk", "children" -> "child", etc.
	"""
	from WordExtractor import WordExtractor # import here as nltk packages are downloaded when WordExtractor is imported
	if interested_in:
		try:
			WordExtractor.set_interesting_types(interested_in)
		except ValueError as e:
			print(f'Error: invalid value specified for --interesting option. {e}')
			print_help_and_exit(1)

	word_data = WordData(lemmatize)
	# Extract word data from files
	for input_file in input_files:
		we = WordExtractor(input_file)
		print(f"Extracting word data from {input_file}...")
		we.extract_words(word_data)
	
	# Retrieve word results in descending order of total number of occurences in all files
	if all is True: num = None
	count_desc_alphabetical = lambda word_pos: (-word_data.get_count(word_pos), word_pos[0].lower())
	results = word_data.get_results(n=num, min_count=min_count, sort_by=count_desc_alphabetical)
	word_data.print_results(results, not omit_sentences, file=file)


def get_files(dir):
	"""
	Returns a list of all files in a given directory
	"""
	if not os.path.isdir(dir):
		raise TypeError(f"get_files must be supplied with a valid path of a directory")
	return [os.path.join(dir, f) for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))]


def print_help_and_exit(exit_code=0):
	print('\nTool for extracting data on "interesting" words from text files. A word is considered "interesting" if it is a noun (including proper nouns), adjective, or foreign word.')
	print('Displays results in descending order of total number of occurences, and includes data on the files and full sentences that the words were found in.')
	print('\nUsage: python extract_word_data.py [dir_containing_input_files] [options]*')
	print('\nwhere [options] can be:\n')
	for o in OPTIONS:
		arg = f' [{o.arg_name}]' if o.arg_name else ''
		print(f'-{o.short} | --{o.long + arg :24} {o.description}')
	print('\nFor example: "python extract.py /path/to/docs -f results.txt -n 100 -i verbs -i nouns" will print the top 100 verbs and nouns in the files in the "docs" folder to output file "results.txt".')
	sys.exit(exit_code)


def parse_command_line_args(args):
	shorts = ''
	longs = []
	for o in OPTIONS:
		shorts += o.short + (':' if o.arg_name else '')
		longs.append(o.long + ("=" if o.arg_name else ''))
	return getopt.getopt(args, shorts, longs)


def extract_args(optlist: tuple):
	""" 
	Extracts a list of arguments from command line options to pass to extract_word_data function. 
	
	Args:
		optlist: list of (option, value) tuples.
	Returns:
		A dictionary of arguments to pass to extract_word_data function.
	"""
	args = {}
	interesting_types = []
	for opt, value in optlist:
		opt = opt.strip('-')
		if opt in ('help', 'h'):
			print_help_and_exit()
		elif opt in ('omit_sentences', 'o'):
			args['omit_sentences'] = True
		elif opt in ('all', 'a'):
			args['all'] = True
		elif opt in ('interested_in', 'i'):
			interesting_types.append(value)
		elif opt in ('lemmatize', 'l'):
			args['lemmatize'] = True
		else:
			for valid_option in OPTIONS:
				if opt == valid_option:
					args[valid_option.long] = int(value) if value.isdigit() else value
	if interesting_types:
		args['interested_in'] = interesting_types
	return args


def main():
	"""
	Parses command line options, extracts data from files listed in given folder, 
	and outputs data on "interesting" words found in files.
	"""
	if len(sys.argv) == 1 or sys.argv[1] in ('--help', '-h'):
		print_help_and_exit()
	try:
		optlist, _ = parse_command_line_args(sys.argv[2:])
	except getopt.GetoptError as e:
		print(e.msg)
		print_help_and_exit(1)
	extract_word_data_args = extract_args(optlist)
	try:
		input_files = get_files(sys.argv[1])
	except TypeError:
		print(f'Error: first argument supplied must be a valid path to a directory containing input files. Instead got "{sys.argv[1]}"')
		print_help_and_exit(1)
	try:
		extract_word_data(input_files, **extract_word_data_args)
	except TypeError:
		print(traceback.format_exc())
		print_help_and_exit(1)


if __name__ == '__main__':
	main()

