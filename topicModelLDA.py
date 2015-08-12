__author__ = 'IH'
__project__ = 'processMOOC'

import re
from html.parser import HTMLParser
from stop_words import get_stop_words
from gensim import corpora, models

class LDAtopicModel(object):
    """
    Class contains an LDA topic model for one set of documents.
    Mostly exists as a way to access (and setup) topic_names
    """
    number_of_topics = 1
    docs = []
    topic_names = []
    lda = None
    FORMAT_LINE = "--------------------"

    def __init__(self, nt, docs_as_bow):
        """
        Initialize class with documents to train the model on
        :param docs_as_bow: a list of text documents as bags of words
        :return: None
        """
        self.docs = docs_as_bow
        self.number_of_topics = nt
        self.create_lda()

    def create_lda(self, use_input=False):
        """
        Runs all posts through an LDA topic model, to determine the basic topic of the post.
        http://chrisstrelioff.ws/sandbox/2014/11/13/getting_started_with_latent_dirichlet_allocation_in_python.html
        http://radimrehurek.com/topic_modeling_tutorial/2%20-%20Topic%20Modeling.html
        :param use_input: Whether or not to ask the user to name each topic
        :return: None
        """
        print("Creating LDA topic model from " + str(len(self.docs)) + " documents.")
        num_topics = self.number_of_topics
        chunk_size = int(len(self.docs)/100)
        if chunk_size < 1:
            chunk_size = 1  # small number of sentences

        all_tokens = sum(self.docs, [])
        # process our stop words like all our words have been processed
        tokens_stop = []
        for word in get_stop_words('en'):
            tokens_stop.extend(self.to_bow(word))

        tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
        # remove words that appear only once or are stop words
        texts = [[word for word in sentence if word not in tokens_once and word not in tokens_stop] for sentence in self.docs]

        # constructing topic model
        dict_lda = corpora.Dictionary(texts)
        mm_corpus = [dict_lda.doc2bow(text) for text in texts]
        self.lda = models.ldamodel.LdaModel(corpus=mm_corpus, id2word=dict_lda, num_topics=num_topics, update_every=1, chunksize=chunk_size, passes=1)
        #topics = lda.print_topics(self.number_of_topics)

        if use_input:
            # get list of lda topic names
            print(self.FORMAT_LINE)
            # printing each topic
            for topic in self.lda.print_topics(self.number_of_topics):
                print(topic)
            print(self.FORMAT_LINE)

            print("\n")

            print("- Begin naming topics -")
            # naming each topic
            i = 1
            for topic in self.lda.print_topics(self.number_of_topics):
                print("\t(" + str(i) + ") "+ topic)
                self.topic_names.append(input("> A name for topic (" + str(i) + "): "))
                i += 1
        else:
            print("- Begin guessing topics -")
            # naming each topic based on top _n_ matching words
            for topic in self.lda.show_topics(self.number_of_topics):
                name = self.get_topic_name(topic, 2)
                print("\t- " + name + " = " + topic)
                self.topic_names.append(name)
        print("Done creating LDA topic model")

    def get_topic_name(self, topic, num_words):
        # 0.025*can + 0.023*time + 0.020*two + 0.020*work + 0.018*may + 0.017*transaction...
        all_words = topic.split('+')
        if num_words > len(all_words):
            num_words = len(all_words)

        name = ""
        for i in range(0, num_words):
            name += all_words[i][topic.index('*')+1:].strip()
        return name

    def topic_distribution_scores(self, document):
        """
        Acquire the topic distribution probabilities for the given document
        :param document: the string to predict the topic for
        :return: the string topic name
        """
        if self.lda is None:
            print("ERROR in lda_topic_model.topic_distribution_scores(): Need to create_lda() before predicting topics.")
        dict_lda = getattr(self.lda, 'id2word')
        lda_vector = self.lda[dict_lda.doc2bow(self.to_bow(document))]
        return lda_vector

    def topic_distribution_scores_list(self, document):
        """
        Turns a tuple list of topic distribution scores into a list by index
        :return: the string topic name
        """
        # Turn list of tuples into a standard list
        # [(3, 0.056740372898456126), (4, 0.27516198725956603), (5, 0.24956765283142127), (7, 0.076124760183927817), (8, 0.059447458221449888), (12, 0.19117117467036432), (13, 0.063716414727980106)]
        list_lda = [0] * self.number_of_topics
        for t in self.topic_distribution_scores(document):
            list_lda[t[0]] = t[1]

        return list_lda


    def predict_topic(self, document):
        """
        Predict the most likely topic for the given document
        :param document: the string to predict the topic for
        :return: the string topic name
        """
        lda_vector = self.topic_distribution_scores(document)
        return self.topic_names[max(lda_vector, key=lambda item: item[1])[0]]

    @staticmethod
    def clean_string(sentence):
        """
        Clean the string by removing all punctuation and HTML
        http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
        :param sentence: the string potentially containing HTML and other non-alphanumerics
        :return: the string cleaned of all tags, undesirables as a list of strings (bag of words)
        """
        # TODO: Should removed characters be replaced with a space? Or no space (as is)?
        removed_char = ''

        s = MLStripper()
        s.feed(sentence)
        no_html = s.get_data()
        # This code apparently removes all text in a string without any HTML
        if len(no_html) < 10:
            no_html = sentence

        # Remove "'s" possession contractions
        cleaned = no_html.replace("'s", removed_char)

        cleaned = re.sub(r'[^a-zA-Z\' ]+', removed_char, cleaned)  # Leaving in letters and apostrophes

        # Handling URLs by splitting the 'http' off from the rest of the URL ('httplightsidelabscomwhatresearch')
        cleaned = cleaned.replace("http", "http ")

        return cleaned.lower()

    @staticmethod
    def to_bow(sentence):
        """
        Turn given string into a bag of words
        :param sentence: the string to turn into a list
        :return: the string  as a list of strings (bag of words)
        """
        texts = [word for word in sentence.split()]  # turning each word into an item in a list
        return texts

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
