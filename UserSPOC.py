__author__ = 'IH'
__project__ = 'spoc-file-processing'

import utilsSPOC as utils

class UserSPOC(object):
    """
    The UserSPOC class represents a single user
    """
    user_id = "-1"
    num_comments = 0
    voting_cond = ""
    any_vote_condition = ""
    neg_vote_condition =""
    prompting_cond = ""
    num_prompts = 0
    num_upvotes = 0
    num_downvotes = 0
    assignments = []
    assignment_lates = []
    tot_late = 0
    exams = []
    midterm = -1
    exercises = []

    first_prompt_date = ""

    # user counting
    num_punctual_comments = 0  # some students post comments waaaaay after the lecture is posted, keep track of legitimate comment count!
    num_help_requests = 0
    # keeping track of LIWC comment word counts
    liwc_positive_words = 0
    liwc_negative_words = 0
    comment_length = 0
    num_comment_words = 0
    num_late_comments = 0
    num_comments_before_experiment = 0

    # num comments before/after first prompt
    comments_before_prompt = 0
    comments_after_prompt = 0

    def __init__(self, uid, nc, vc, pc, np, up, down, assi, asl, tl, e, mg, exc, fpd):
        """

        :param uid: user id
        :param nc: number of comments
        :param vc: voting condition
        :param pc: first prompting condition
        :param np: number of prompts received
        :param up: number of upvotes
        :param down: number of downvotes
        :param assi: list of assignment grades (each index lines up with exam number)
        :param asl: list of assignment lates
        :param e: list of exam scores
        :param mt: midterm score
        :param f: final score
        :param exc: list of exercise scores
        :return: None
        """
        self.user_id = uid
        self.num_comments = nc
        self.voting_cond = vc
        self.prompting_cond = pc
        self.num_prompts = np
        self.num_upvotes = up
        self.num_downvotes = down
        self.assignments = assi
        self.assignment_lates = asl
        self.tot_late = tl
        self.exams = e
        self.midgrade = mg
        self.exercises = exc
        self.first_prompt_date = fpd

        # setting additional voting columns (also checking for valid condition names)
        if self.voting_cond == utils.COND_VOTE_NONE:
            self.any_vote_condition = "NO"+utils.COND_VOTE
            self.neg_vote_condition = utils.COND_OTHER
        elif self.voting_cond == utils.COND_VOTE_UP:
            self.any_vote_condition = utils.COND_VOTE
            self.neg_vote_condition = utils.COND_OTHER
        elif self.voting_cond == utils.COND_VOTE_BOTH:
            self.any_vote_condition = utils.COND_VOTE
            self.neg_vote_condition = utils.COND_VOTE_BOTH
        else:
            self.any_vote_condition = ""

        # checking for valid condition names
        if self.prompting_cond != utils.COND_PROMPT_POS and self.prompting_cond != utils.COND_PROMPT_NEUTRAL and self.prompting_cond != utils.COND_NO_PROMPT:
            self.prompting_cond = ""

        # Removed "_GROUP" from variable name, for display purposes
        vc = vc.split("_")[0]
        self.voting_cond = vc

    def to_string(self, delimiter):
        """
        Create a string for printing all UserSPOC variables
        :param delimiter: character to split each column
        :return: a string for printing all variables from this UserSPOC object
        """
        return self.to_const_string(delimiter) + delimiter + self.to_count_string(delimiter)

    def to_const_string(self, delimiter):
        """
        Create a string for printing constant/non-count variables
        :param delimiter: character to split each column
        :return: a string for printing non-count variables from this UserSPOC object
        """
        line = str(self.user_id) + delimiter + str(self.num_comments) + delimiter
        line += self.voting_cond + delimiter
        line += self.any_vote_condition + delimiter + self.neg_vote_condition + delimiter
        line += self.prompting_cond + delimiter + str(self.num_prompts) + delimiter
        line += str(self.num_upvotes) + delimiter
        line += str(self.num_downvotes)
        for i in range(0, len(utils.COL_ASSIGNMENTS)):  # iterating through assignment scores
            line += delimiter + self.assignments[i] + delimiter + self.assignment_lates[i]
        line += delimiter + self.tot_late
        for exam in self.exams:  # iterating through exam scores
            line += delimiter + exam
        line += delimiter + self.midgrade
        for exc in self.exercises:  # iterating through exercise headers
            line += delimiter + exc
        line += delimiter + str(self.first_prompt_date)
        return line

    def to_count_string(self, delimiter):
        """
        Create a string for printing only variables that are counts (from comments, usually)
        :param delimiter: character to split each column
        :return: a string for printing this UserSPOC, coordinating with the headers
        """
        line = str(self.num_punctual_comments) + delimiter + str(self.num_late_comments)
        line += delimiter + str(self.num_comments_before_experiment)
        line += delimiter + str(self.num_help_requests)
        line += delimiter + str(self.liwc_positive_words)
        line += delimiter + str(self.liwc_negative_words)
        line += delimiter + str(self.num_comment_words)
        line += delimiter + str(self.comment_length)
        line += delimiter + str(self.comments_before_prompt)
        line += delimiter + str(self.comments_after_prompt)
        return line

    @staticmethod
    def get_headers(delimiter):
        """
        Retrieve column headers for a  object for printing
        :param delimiter: character to split each column header
        :return: None
        """
        # constant variables
        line = utils.COL_ID + delimiter + utils.COL_NUM_COMMENTS + delimiter
        line += utils.COL_VOTING + delimiter + utils.COL_ANY_VOTE + delimiter + utils.COL_NEG_VOTE + delimiter
        line += utils.COL_PROMPTS + delimiter + utils.COL_NUM_PROMPTS + delimiter
        line += utils.COL_NUM_UPVOTES + delimiter + utils.COL_NUM_DOWNVOTES + delimiter
        for i in range(0, len(utils.COL_ASSIGNMENTS)):  # iterating through assignment headers
            line += utils.COL_ASSIGNMENTS[i] + delimiter + utils.COL_ASSIGN_LATE[i] + delimiter
        line += utils.COL_TOT_LATE + delimiter
        line += utils.COL_E1 + delimiter + utils.COL_E1D + delimiter + utils.COL_E1F + delimiter + utils.COL_E2 + delimiter
        line += utils.COL_MIDGRADE
        for header in utils.COL_EXERCISE:  # iterating through exercise headers
            line += delimiter + header
        line += delimiter + utils.COL_FIRST_PROMPT_DATE

        # count variables
        line += delimiter + utils.COL_NUM_LEGIT_COMMENTS
        line += delimiter + utils.LATE_COMMENTS
        line += delimiter + utils.BEFORE_EXP_COMMENTS
        line += delimiter + utils.COL_HELP_REQS
        line += delimiter + utils.LIWC_POSITIVE
        line += delimiter + utils.LIWC_NEGATIVE
        line += delimiter + utils.COMMENT_WORDS
        line += delimiter + utils.COMMENT_CHARS
        line += delimiter + utils.COL_COMMENTS_BEFORE_PROMPT
        line += delimiter + utils.COL_COMMENTS_AFTER_PROMPT
        return line

