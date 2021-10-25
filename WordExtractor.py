# Author: Sam Bradshaw

from WordData import WordData
import nltk

class WordExtractor:
	"""
	Class for reading text from a file and extracting interesting words and information on where they occured. 
	"""
	nltk.download('punkt') 
	nltk.download('stopwords')
	nltk.download('averaged_perceptron_tagger')

	STOP_WORDS = set(nltk.corpus.stopwords.words('english')) 
	""" Set of commonly used words in English language. """
	
	interesting_types = { 
		'NN', # nouns
		'NNS', # nouns (plural)
		'NNP', # proper nouns (singular)
		'NNPS', # proper nouns (plural)
		'JJ', # adjectives
		'JJR', # adjectives (comparative)
		'JJS', # adjectives (superlative)
		'CD', # numerical 
		'FW' # foreign words
	}
	""" Types of words to include. See nltk documentation for pos tagging. Run nltk.help.upenn_tagset() to see full list of nltk pos tags. """

	def __init__(self, filepath, encoding=None):
		"""
		filepath: path to text file to extract word data from.
		encoding: Encoding of file (default is "utf8").
		"""
		self.filepath = filepath
		self.encoding = encoding or 'utf8'

	def extract_words(self, data: WordData):
		"""
		Reads an input text file, tockenizing it into words, and adds any "interesting" words to data object.
		
		Args:
			data: WordData object to add word data to.
		"""
		with open(self.filepath, encoding=self.encoding) as file:
			for line in file:
				for sentence in nltk.tokenize.sent_tokenize(line):
					words = nltk.word_tokenize(sentence)
					word_pos_tuples = nltk.pos_tag(words) # pos = part-of-speech
					for word_pos in set(word_pos_tuples): # Convert to set so if same word appears twice in same sentence it is not duplicated in data.
						word, pos = word_pos
						# convert to lowercase if word is not a proper noun.
						if pos not in ('NNP','NNPS') and word[0].isupper(): 
							word_pos = (word.lower(), pos)
						if WordExtractor.is_interesting(word_pos):
							if pos.startswith('V') and not "'" in word\
								or not pos.startswith('V'):
								data.add(word_pos, file.name, word_pos_tuples)

	@staticmethod
	def set_interesting_types(word_types):
		""" 
		Updates the WordExtractor.interesting_types static variable set.
		
		Raises:
			ValueError if entry in word_types is not "nouns", "verbs", or "adjectives"
		 """
		interesting = set()
		for type in word_types:
			if type not in ('nouns', 'verbs', 'adjectives'):
				raise ValueError(f'Valid options are "nouns", "verbs", or "adjectives". Instead got "{type}".')
			# run nltk.help.upenn_tagset() to see full list of nltk pos tags
			if type == "nouns":
				interesting.update({'NN', 'NNS', 'NNP', 'NNPS'})
			elif type == "verbs":
				interesting.update({'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'})
			elif type == "adjectives":
				interesting.update({'JJ', 'JJR', 'JJS'})
		WordExtractor.interesting_types = interesting


	@staticmethod
	def is_interesting(word_pos: tuple):
		"""
		Determines if a word is "interesting". A word is deemed "interesting" if it does not appear 
		in a set of common stopwords and it is a type defined in interesting_types set.

		Returns:
			True if a word is considered interesting, False otherwise.
		"""
		word, pos = word_pos
		return word not in WordExtractor.STOP_WORDS \
				and pos in WordExtractor.interesting_types \

