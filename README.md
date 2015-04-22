# spoc-file-processing
A set of scripts for parsing files related to a small, private online course. Parses, does LDA topic modeling, and some basic statistics.

## running
**logfileSPOC.py** and **statsSPOC.py** are the main scripts to run and they rely on constants supplied by **utilsSPOC.py**. First, run **logfileSPOC.py** then run **statsSPOC.py**.

## code
**logfileSPOC.py** the main script for parsing the basic CSV logfile and outputting a (slightly) modified version of it.

**statsSPOC.py** a script for running basic descriptive statistics and a few plots on the output from logfileSPOC.py. Uses pandas.

**kmeansSPOC.py** does unsupervised automated of clustering of the main data. Displays scatterplots to explore the clusters.

**utilsSPOC.py** a file containing the constant values that the user can modify. Contains things like the delimiter character, logfile names, column headers, etc. 

**topicModelLDA.py** an internal class for creating an LDA topic model and then predicting the topic for a new document. Has utility function for cleaning strings and turning documents into bags of words before feeding into the model.

**UserSPOC.py** an internal class representing one user in the original logfile. The conditions they saw, their number of comments, number of prompts seen, etc.
