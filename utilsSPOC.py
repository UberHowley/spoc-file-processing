__author__ = 'IH'
__project__ = 'spoc-file-processing'

"""
This utilsSPOC file holds the text constants for parsing the datafiles
"""

import datetime

# date/time related stuff
#CONST_FIRST_DAY = datetime.date(2015, 1, 1)
#CONST_LAST_DAY = datetime.date(2015, 5, 5)
CONST_SWITCH_DAY = datetime.date(2015, 4, 11)  # the day prompting conditions switched

# constants
FILE_CONDITIONS = "150404_spoc_full_data"
FILE_POSTS = "150404_spoc_comment_data"  # TODO: not yet received
LDA_FILE = FILE_CONDITIONS + "_lda"
FILE_EXTENSION = ".csv"
DELIMITER = ","
NUM_LDA_TOPICS = 7

# student issues
DROP_STUDENTS = [15, 78, 105, 133, 181]
# 133 and 181 are the same user with different accounts. Saw different conditions, remove them both
# 15, 78, and 105 are not enrolled in the course

# column headers (as written in the in-file)
COL_ID = "id"
COL_VOTING = "Condition"
COL_PROMPTS = "Encouragement Type"
COL_PROMPTS2 = "TODO_prompts2"  # TODO: Column header for prompts after the switch?
COL_NUM_PROMPTS = "TODO_numPrompts"  # TODO: where's number of prompts user received?
COL_NUM_COMMENTS = "Num Comments"
COL_NUM_UPVOTES = "Num Upvotes"
COL_NUM_DOWNVOTES = "Num Downvotes"
COL_ASSIGNMENTS = ["Asst 1", "Asst 2", "Asst 3", "Asst 4"]
COL_ASSIGN_LATE = ["A1 Late", "A2 Late", "A3 Late", "A4 Late"]
COL_TOT_LATE = "Total Late"
COL_E1 = "Exam 1"
COL_E1D = "Exam 1 (Deal)"
COL_E2 = "Exam 2"
COL_MIDTERM = "Mid Grade"
COL_FINAL = "TODO_final"
COL_EXERCISE = ["Exercise 1", "Exercise 2", "Exercise 3", "Exercise 4"]

COL_SLIDE = "TODO_slide"  # TODO
COL_COMMENT = "TODO_commentText"  # TODO
COL_TIMESTAMP = "TODO_timestamp"  # TODO

COL_ANY_VOTE = "hasAnyVoting"
COL_LDA = "LDAtopic"

# conditions
COND_VOTE = "VOTE_GROUP"
COND_VOTE_BOTH = "UPDOWNVOTE_GROUP"
COND_VOTE_NONE = "NOVOTE_GROUP"
COND_VOTE_UP = "UPVOTE_GROUP"
COND_PROMPT_POS = "POSITIVE"
COND_PROMPT_NEUTRAL = "NEUTRAL"
