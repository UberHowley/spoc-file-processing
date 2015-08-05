__author__ = 'IH'
__project__ = 'spoc-file-processing'

"""
This utilsSPOC file holds the text constants for parsing the datafiles
"""

import datetime

# date/time related stuff
CONST_FIRST_DAY = datetime.date(2015, 2, 7)  # approximate day experiment began
CONST_LAST_DAY = datetime.date(2015, 5, 8)  # last day of classes + 1 week

# constants
FILE_CONDITIONS = "150512_spoc_full_data"
FILE_POSTS = "150512_spoc_comments"
FILE_PROMPTS = "150512_spoc_prompts"
PROMPT_MOD = FILE_PROMPTS + "_mod"
MOD_FILE = FILE_CONDITIONS + "_mod"
LDA_FILE = FILE_POSTS + "_lda"
FILE_EXTENSION = ".csv"
DELIMITER = ","
NUM_LDA_TOPICS = 15
WEEK_THRESHOLD = 3  # threshhold num weeks after a lecture for comment to be considered 'punctual'

# student issues
DROP_STUDENTS = [15, 78, 105, 133, 181]
# 133 and 181 are the same user with different accounts. Saw different conditions, remove them both
# 15, 78, and 105 are not enrolled in the course
CONSENTING_STUDENTS = [9, 10, 13, 14, 15, 16, 17, 20, 21, 23, 29, 34, 37, 41, 42, 43, 44, 45, 46, 47, 50, 54, 55, 58,
                       59, 60, 62, 66, 67, 70, 72, 74, 76, 78, 80, 81, 82, 84, 87, 92, 93, 94, 95, 97, 100, 101, 105,
                       108, 109, 115, 117, 119, 121, 123, 127, 128, 131, 133, 134, 136, 145, 151, 152, 153, 160, 164,
                       165, 180, 181, 182]
# IDs of all the consenting students

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
COL_E1 = "Exam1"
COL_E1D = "Exam1(Deal)"
COL_E1F = "Exam1(Final)"
COL_MIDGRADE = "MidGrade"
COL_E2 = "Exam2"
COL_EXERCISE = ["Exercise1", "Exercise2", "Exercise3", "Exercise4", "Exercise5", "Exercise6"]

# outside of database created columns
COL_NUM_LEGIT_COMMENTS = "num_punctual_comments"  # some students post comments waaaaay after the lecture is posted, keep track of legitimate comment count!
COL_HELP_REQS = "num_help_requests"
LIWC_POSITIVE = "liwc_positive_words"
LIWC_NEGATIVE = "liwc_negative_words"
COMMENT_CHARS = "comment_length"
COMMENT_WORDS = "num_comment_words"
LATE_COMMENTS = "num_late_comments"
BEFORE_EXP_COMMENTS = "num_comments_before_experiment"

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
COL_ORIGINAL = "original_comment"

# prompts
COL_AUTHOR_ID = "author_id"
COL_PARENTTYPE = "parent_type"
COL_PARENT_ID = "parent_id"
COL_MESSAGE = "message"
COL_PROMPT_TYPE = "prompt_type"
COL_ENCOURAGEMENT_TYPE = "encouragement_segment"
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
COND_NO_PROMPT = "NO_PROMPT"
COND_OTHER = "OTHER"

FORMAT_LINE = "--------------------"

# mapping from lecture number to date posted, so we can toss
# comments posted at the last minute deadline
# parent_id(slide) -> date(of slide)
lecture_dates = [(2, datetime.date(2015, 1, 12)),
                 (3, datetime.date(2015, 1, 14)),
                 (4, datetime.date(2015, 1, 21)),
                 (5, datetime.date(2015, 1, 26)),
                 (6, datetime.date(2015, 1, 28)),
                 # 1 comment for 7: What does "-bind-to-core" do?
                 # 2 comments for 8: Doesn't the slide show *inclusive* scan, and you subtract the original vector to get exclusive scan?
                 (9, datetime.date(2015, 2, 2)),
                 (10, datetime.date(2015, 2, 4)),
                 (11, datetime.date(2015, 2, 9)),
                 (12, datetime.date(2015, 2, 11)),
                 # no 13
                 (14, datetime.date(2015, 2, 16)),
                 (15, datetime.date(2015, 2, 18)),
                 (16, datetime.date(2015, 2, 23)),
                 (17, datetime.date(2015, 2, 25)),
                 (18, datetime.date(2015, 3, 4)),
                 (19, datetime.date(2015, 3, 16)),
                 (20, datetime.date(2015, 3, 18)),
                 (21, datetime.date(2015, 3, 23)),
                 (22, datetime.date(2015, 3, 25)),
                 # no 23
                 (24, datetime.date(2015, 3, 30)),
                 (25, datetime.date(2015, 4, 1)),
                 (26, datetime.date(2015, 4, 6)),
                 (27, datetime.date(2015, 4, 8)),
                 (28, datetime.date(2015, 4, 13)),
                 (30, datetime.date(2015, 4, 15)),
                 (29, datetime.date(2015, 4, 20)),
                 (31, datetime.date(2015, 4, 22)),
                 (32, datetime.date(2015, 4, 27)),
                 (33, datetime.date(2015, 4, 29))]