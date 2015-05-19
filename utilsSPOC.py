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
FILE_CONDITIONS = "150512_spoc_full_data"
FILE_POSTS = "150512_spoc_comments"
FILE_PROMPTS = "150512_spoc_prompts"
MOD_FILE = FILE_CONDITIONS + "_mod"
LDA_FILE = FILE_POSTS + "_lda"
FILE_EXTENSION = ".csv"
DELIMITER = ","
NUM_LDA_TOPICS = 7

# student issues
DROP_STUDENTS = [15, 78, 105, 133, 181]
# 133 and 181 are the same user with different accounts. Saw different conditions, remove them both
# 15, 78, and 105 are not enrolled in the course

# column headers (as written in the in-file)
# Note: I've removed the spaces from all of these at read-in.
COL_ID = "id"
COL_VOTING = "Condition"
COL_PROMPTS = "EncouragementType"
COL_NUM_PROMPTS = "NumTimesPrompted"
COL_NUM_COMMENTS = "NumComments"
COL_NUM_UPVOTES = "NumUpvotes"
COL_NUM_DOWNVOTES = "NumDownvotes"
COL_ASSIGNMENTS = ["Asst1", "Asst2", "Asst3", "Asst4"]
COL_ASSIGN_LATE = ["A1Late", "A2Late", "A3Late", "A4Late"]
COL_TOT_LATE = "TotalLate"
COL_E1 = "Exam1(Final)"
COL_E1D = "Exam1(Deal)"
COL_MIDTERM = "MidGrade"
COL_FINAL = "Exam2"
COL_EXERCISE = ["Exercise1", "Exercise2", "Exercise3", "Exercise4"]

# comments
COL_SLIDE = "parent_item"
COL_COMMENT = "body_markdown"
COL_TIMESTAMP = "created"
COL_EDITED = "edit_timestamp"
COL_AUTHOR = "author"
COL_UPVOTES = "total_upvotes"
COL_DOWNVOTES = "total_downvotes"
COL_EDITAUTHOR = "edit_author"
COL_EDITREASON = "edit_reason"

# prompts
COL_AUTHOR_ID = "author_id"
COL_PARENTTYPE = "parent_type"
COL_PARENT_ID = "parent_id"
COL_MESSAGE = "message"
COL_PROMPT_TYPE = "prompt_type"
COL_ENCOURAGEMENT_TYPE ="encouragement_segment"
COL_RECIPIENTS = "recipients"
COL_TSTAMP = "timestamp"

COL_ANY_VOTE = "hasAnyVoting"
COL_NEG_VOTE = "negativeVoting"
COL_LDA = "LDAtopic"
COL_HELP = "isHelpSeeking"

# conditions
COND_VOTE = "VOTE"
COND_VOTE_BOTH = "UPDOWNVOTE_GROUP"
COND_VOTE_NONE = "NOVOTE_GROUP"
COND_VOTE_UP = "UPVOTE_GROUP"
COND_PROMPT_POS = "POSITIVE"
COND_PROMPT_NEUTRAL = "NEUTRAL"
COND_NO_PROMPT = "NO_PROMPT"  # need to remove these, there should only be ~2
COND_OTHER = "OTHER"

FORMAT_LINE = "--------------------"
