__author__ = 'IH'
__project__ = 'spoc-file-processing'

import urllib.request as ur
import re
from html.parser import HTMLParser

class liwc(object):
    """
    Class contains an LDA topic model for one set of documents.
    Mostly exists as a way to access (and setup) topic_names
    """
    negative_words = []
    positive_words = []
    FORMAT_LINE = "--------------------"

    def __init__(self, path='http://www.unc.edu/~ncaren/haphazard/',  files=['negative.txt', 'positive.txt']):
        """
        Initialize class with documents of positive/negative sentiment words
        :param path: the URL location of the files
        :param files: filenames of sentiment files
        :return: None
        """
        pos_sent = open("positive.txt").read()
        self.positive_words = pos_sent.split('\n')
        neg_sent = open("negative.txt").read()
        self.negative_words = neg_sent.split('\n')

    def count_sentiments(self, line):
        """
        Counts the number of positive, negative and total words in a given string
        :param use_input: Whether or not to ask the user to name each topic
        :return: the number of positive, negative, and total words as a tuple
        """
        num_positive = 0
        num_negative = 0
        words = line.lower().split(' ')
        for word in words:
            if word in self.positive_words:
                num_positive += 1
            elif word in self.negative_words:
                num_negative += 1
        return num_positive, num_negative, len(words)

    @staticmethod
    def clean_string(sentence):
        """
        Clean the string by removing all punctuation and HTML
        http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
        :param sentence: the string potentially containing HTML and other non-alphanumerics
        :return: the string cleaned of all tags, undesirables as a list of strings (bag of words)
        """
        s = MLStripper()
        s.feed(sentence)
        no_html = s.get_data()
        # This code apparently removes all text in a string without any HTML
        if len(no_html) < 10:
            no_html = sentence
        cleaned = re.sub(r'[^a-zA-Z\' ]+', '', no_html)  # Leaving in letters and apostrophes
        # TODO: How to handle URLs? 'httplightsidelabscomwhatresearch'
        # TODO: Contractions (i.e., can't) are okay, but possession isn't (i.e., Carolyn's)
        # TODO: Should removed characters be replaced with a space? Or no space (as is)?
        return cleaned.lower()

class MLStripper(HTMLParser):
    """
    A class for stripping HTML tags from a string
    """
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)
