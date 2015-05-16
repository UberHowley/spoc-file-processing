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
    prompting_cond = ""
    num_prompts = 0
    num_upvotes = 0
    num_downvotes = 0
    assignments = []
    assignment_lates = []
    exams = []
    midterm = -1
    final = -1
    exercises = []

    def __init__(self, uid, nc, vc, pc, np, up, down, assi, asl, e, mt, f, exc):
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
        self.exams = e
        self.midterm = mt
        self.final = f
        self.exercises = exc

        # setting the any voting vs. no voting column
        self.any_vote_cond = utils.COND_VOTE_NONE
        if self.voting_cond is not utils.COND_VOTE_NONE:
            self.any_vote_condition = utils.COND_VOTE

    def to_string(self, delimiter):
        """
        Create a string for printing this QHInstance, coordinating with the headers
        :param delimiter: character to split each column
        :return: a string for printing this QHInstance, coordinating with the headers
        """
        line = str(self.user_id) + delimiter + str(self.num_comments) + delimiter + self.voting_cond + delimiter
        line += self.any_vote_condition + delimiter
        line += self.prompting_cond + delimiter + str(self.num_prompts) + delimiter
        line += str(self.num_upvotes) + delimiter
        line += str(self.num_downvotes)
        for i in range(0, len(utils.COL_ASSIGNMENTS)):  # iterating through assignment scores
            line += delimiter + self.assignments[i] + delimiter + self.assignment_lates[i]
        for exam in self.exams:  # iterating through exam scores
            line += delimiter + exam
        line += delimiter + self.midterm + delimiter + self.final
        for exc in self.exercises:  # iterating through exercise headers
            line += delimiter + exc
        return line

    @staticmethod
    def get_headers(delimiter):
        """
        Retrieve column headers for a  object for printing
        :param delimiter: character to split each column header
        :return: None
        """
        line = utils.COL_ID + delimiter + utils.COL_NUM_COMMENTS + delimiter
        line += utils.COL_VOTING + delimiter + utils.COL_ANY_VOTE + delimiter
        line += utils.COL_PROMPTS + delimiter + utils.COL_NUM_PROMPTS + delimiter
        line += utils.COL_NUM_UPVOTES + delimiter + utils.COL_NUM_DOWNVOTES + delimiter
        for i in range(0, len(utils.COL_ASSIGNMENTS)):  # iterating through assignment headers
            line += utils.COL_ASSIGNMENTS[i] + delimiter + utils.COL_ASSIGN_LATE[i] + delimiter
        line += utils.COL_E1 + delimiter + utils.COL_E1D + delimiter + utils.COL_FINAL + delimiter
        line += utils.COL_MIDTERM + delimiter + utils.COL_FINAL + delimiter
        for header in utils.COL_EXERCISE:  # iterating through exercise headers
            line += header + delimiter
        return line

