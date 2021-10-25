# Author: Sam Bradshaw

from os import path
from itertools import islice
from typing import Iterable
from nltk.tokenize.treebank import TreebankWordDetokenizer
# from nltk.corpus import wordnet # TODO Uncomment to add lemmatize option. Currently buggy, possibly due to limitations of wordnet limitizer 
# import nltk # TODO

class WordData:
	""" Class for storing data on words and the files and sentences they were found in. """

	def __init__(self):	# TODO: Add "lemmatize=False" param to add lemmatize option. 
		self.data = dict()
		# self.lemmatizer = nltk.stem.WordNetLemmatizer() if lemmatize else None # TODO: uncomment to add lemmatize option
	
	def add(self, word_pos, file, sentence_pos):
		"""
		Adds occurence of word to data, including information on 
		the file and sentence that the word occured in.

		Args:
			word_pos: The (word, pos) tuple to add to data.
			file: The file the word was found in.
			sentence_pos: The full sentence the word occured in, split in to an array of (word, pos_tags) tuples.
		"""
		# TODO: add option to lemmatize tokens
		# if self.lemmatizer:
		# 	lemmatized_word = self.lemmatizer.lemmatize(word_pos[0], pos=WordData.get_wordnet_pos(pos))
		# 	word_pos = (lemmatized_word, pos)

		if self.data.get(word_pos) is None: # Word has not been seen yet
			self.data[word_pos] = dict()
		if self.data.get(word_pos).get(file) is None: # Word has not been seen in given file
			self.data[word_pos][file] = []
		self.data[word_pos][file].append(sentence_pos)

	def get_count(self, word_pos, file=None):
		""" 
		Args:
			word_pos: The (word, pos) to get the count of occurences for.
			file: If included, gets the number of occurences of (word, pos) in a particular file.
		Returns:
			The total number of occurences of a particular word in the data.
		"""
		count = 0
		if self.data.get(word_pos) is not None:
			# Get list of sentences word appears in
			if file is not None:
				sentences = self.data.get(word_pos).get(file) or []
			else:
				# Flatten 2d array of sentences to 1d array
				sentences = [s for doc in list(self.data.get(word_pos).values()) for s in doc]
			# Check how many times word appears in each sentence
			for sentence_pos in sentences:
				for wp in sentence_pos:
					if WordData.is_equivalent(word_pos, wp):
						count += 1
		return count

	def generate_results(self, min_count=None, sort_by=None):
		"""
		Generates tuples containing words and information on where they occured.
		
		Args:
			sort_by: Parameter to pass to 'key' argument of :py:func:`list.sort` function. \
				Use if results should be generated in a particular order.
		"""
		words_pos_list = list(self.data.keys())
		if sort_by:
			words_pos_list.sort(key=sort_by)
		for word_pos in words_pos_list:
			if min_count is None or self.get_count(word_pos) >= min_count:
				yield (word_pos, self.data[word_pos])

	def get_results(self, n=None, min_count=None, sort_by=None):
		"""
		Args:
			n: Number of results to include. If None, then data on all words are included.
			min_count: Minimum number of times a word needs to occur in data for it to be included in results.

			sort_by: Parameter to pass to 'key' argument of :py:meth:`list.sort` function to determine order of results. 
		Returns: 
			An iterable object of results in tuple form, where each tuple \
				is a word followed by its dictionary of occurrences.
		"""
		n = n or len(self.data.keys())
		results_iter = self.generate_results(min_count=min_count, sort_by=sort_by)
		return islice(results_iter, 0 , n)

	@staticmethod
	def is_equivalent(word_pos, word_pos_in_sentence):
		""" 
		Returns True if a word in the context of a sentence is counted as being the same as word, accounting for potential lemmatisation.
		
		Args:
			word_pos: The (word, pos) tuple as it appears as a key in the self.data dict.
			word_pos_in_sentence: The (word, pos) tuple as it appears in the context of a full sentence.
		"""
		w, p = word_pos_in_sentence
		if p not in ('NNP', 'NNPS') and w[0].isupper():
			w = w.lower()
		return word_pos[0] == w and word_pos[1] == p


	def print_results(self, results: Iterable, include_sentences=True, file=None):
		"""
		Prints a list of results in following format: 
			rank - word (total_count) {
				file (count_in_file) [
					sentences
				]
			}
		Args:
			results: An iterable object containing ((word, pos), occurence) tuples, \
				where occurence is dictionary of {files: [sentences]} where word occured.
			include_sentences: Determines whether sentences should be included in output results.
			file: If not None, print results to output file with this name. Else print to console.
		"""
		output_lines = []
		
		def underline_bold(word):
			""" Adds formatting to console output """
			return f'\033[4m\033[1m{word}\033[0m\033[0m'
		
		if is_printing_to_console := file is None: 
			output_lines.append(f"\n{underline_bold('Results')}:\n")
		else: 
			output_lines.append(f"Results:")
			output_lines.append("")

		for rank, (word_pos, occurences) in enumerate(results):
			word_info = f"{rank + 1} - {word_pos[0]} ({self.get_count(word_pos)})"
			if is_printing_to_console: 
				word_info = underline_bold(word_info) # add formatting
			output_lines.append(f'{word_info} {{')
			# Print file names that word occured in 
			for filepath in list(occurences.keys()):
				filename = path.split(filepath)[-1]
				file_info = f'\t{filename} ({self.get_count(word_pos, file=filepath)})' + (' [' if include_sentences else ',')
				output_lines.append(file_info)
				# Print sentences that word occured in
				if include_sentences:
					for sentence in occurences[filepath]:
						words = [wp[0] for wp in sentence]
						if is_printing_to_console: 
							# add formatting 
							for i, wp in enumerate(sentence):
								if WordData.is_equivalent(word_pos, wp):
									words[i] = underline_bold(wp[0])
						sentence = TreebankWordDetokenizer().detokenize(words)
						output_lines.append(f'\t\t"{sentence}",')
					output_lines.append('\t]')
			output_lines.append('}')
		output = '\n'.join(output_lines)
	
		if is_printing_to_console:
			print(output)
		else:
			# Write results to file
			with open(file, 'w') as f:
				print(output, file=f)
			print(f"\nResults recorded to {file}")

	
	# TODO: Uncomment method required to use wordnet lemmatizer
	# @staticmethod
	# def get_wordnet_pos(nltk_pos):
	# 	""" Maps nltk pos tags to wordnet lemmatizer pos tags """
	# 	if nltk_pos.startswith('J'):
	# 		return wordnet.ADJ
	# 	elif nltk_pos.startswith('V'): 
	# 		return wordnet.VERB
	# 	elif nltk_pos.startswith('N'):
	# 		return wordnet.NOUN
	# 	elif nltk_pos in ('RB', 'RBR', 'RBS'): 
	# 		return wordnet.ADV
	# 	else: 
	# 		return 'n'

