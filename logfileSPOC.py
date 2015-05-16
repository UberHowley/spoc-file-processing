__author__ = 'IH'
__project__ = 'spoc-file-processing'

import csv
import datetime
import utilsSPOC as utils
import UserSPOC as user
from topicModelLDA import LDAtopicModel as ldat

# variables
all_users = {}  # uid -> UserSPOC: all users in the file and their conditions
list_sentences = []  # a list of bag of words from all comments

def run():
    process_conditions()
    process_comments()

def process_conditions(filename=utils.FILE_CONDITIONS+utils.FILE_EXTENSION):
    """
    Calculate the average per-user accuracy (user’s percentage correct / total problems done)
    and user accuracy segmented by engagement level (by your categorization from the previous section). What trends do you see?
    :return: None
    """
    # --------------------
    print("Processing " + filename)
    modfile_out = open(utils.MOD_FILE + utils.FILE_EXTENSION, 'w')
    modfile_out.write(user.UserSPOC.get_headers(utils.DELIMITER) + "\n")

    with open(filename, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        cleaned_headers = [s.replace(' ', '') for s in headers]

        for array_line in rows:
            user_id = array_line[cleaned_headers.index(utils.COL_ID)]
            num_comments = array_line[cleaned_headers.index(utils.COL_NUM_COMMENTS)]
            voting_cond = array_line[cleaned_headers.index(utils.COL_VOTING)]
            prompting_cond = array_line[cleaned_headers.index(utils.COL_PROMPTS)]
            num_prompts = array_line[cleaned_headers.index(utils.COL_NUM_PROMPTS)]
            num_upvotes = array_line[cleaned_headers.index(utils.COL_NUM_UPVOTES)]
            num_downvotes = array_line[cleaned_headers.index(utils.COL_NUM_DOWNVOTES)]
            assignments = []
            assignment_lates = []
            exercises = []
            exams = []
            for i in range(0, len(utils.COL_ASSIGNMENTS)):  # iterating through assignment headers
                score = array_line[cleaned_headers.index(utils.COL_ASSIGNMENTS[i])]
                if len(score) < 1:
                    score = ""
                assignments.append(score)
                assignment_lates.append(array_line[cleaned_headers.index(utils.COL_ASSIGN_LATE[i])])
            for header in utils.COL_EXERCISE:  # iterating through exercise headers
                score = array_line[cleaned_headers.index(header)]
                if len(score) < 1:
                    score = ""
                exercises.append(score)
            exams.extend([array_line[cleaned_headers.index(utils.COL_E1)], array_line[cleaned_headers.index(utils.COL_E1D)], array_line[cleaned_headers.index(utils.COL_FINAL)]])
            midterm = array_line[cleaned_headers.index(utils.COL_MIDTERM)]
            final = array_line[cleaned_headers.index(utils.COL_FINAL)]

            new_user = user.UserSPOC(user_id, num_comments, voting_cond, prompting_cond, int(num_prompts), num_upvotes, num_downvotes, assignments, assignment_lates, exams, midterm, final, exercises)

            # removing students from list
            if user_id not in utils.DROP_STUDENTS:
                all_users[user_id] = new_user
                modfile_out.write(new_user.to_string(utils.DELIMITER) + '\n')

    csvfile.close()
    modfile_out.close()
    print("Done processing "+filename+"\n")

def process_comments(filename=utils.FILE_POSTS+utils.FILE_EXTENSION):
    """
    Parses a CSV file with the students' comments, user ids, and timestamps and assigns an automated topic.
    IMPORTANT: Either all commas must be removed from the comment text beforehand, or some unique delimiter
    must be used instead of commas.
    :return:
    """
    print("Processing " + filename)
    with open(filename, 'r', encoding="utf8") as csvfile:
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        cleaned_headers = [s.replace(' ', '') for s in headers]  # removing spaces

        # reading comments in initially and passing to LDA topic model
        for array_line in rows:
            comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]
            if len(comment) > 0:
                list_sentences.append(ldat.to_bow(ldat.clean_string(comment)))
        print("Done processing "+filename+"\n")

        # preparing to output LDA topic analysis stuff
        print("\tProcessing " + utils.LDA_FILE+utils.FILE_EXTENSION)
        csvfile.seek(0)  # start at beginning of file again
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        file_out = open(utils.LDA_FILE+utils.FILE_EXTENSION, 'w', encoding="utf8")
        file_out.write(utils.DELIMITER.join(cleaned_headers))
        file_out.write(utils.DELIMITER + utils.COL_LDA + utils.DELIMITER + utils.COL_VOTING + utils.DELIMITER + utils.COL_PROMPTS + '\n')

        lda = ldat(utils.NUM_LDA_TOPICS, list_sentences)  # create topic model

        for array_line in rows:
            user_id = array_line[cleaned_headers.index(utils.COL_AUTHOR)]
            comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]

            """# No need to find/store this additional data
            post_id = array_line[cleaned_headers.index(utils.COL_ID)]
            tstamp = array_line[cleaned_headers.index(utils.COL_TIMESTAMP)]
            slide = array_line[cleaned_headers.index(utils.COL_SLIDE)]
            num_upvotes = int(array_line[cleaned_headers.index(utils.COL_UPVOTES)])
            num_downvotes = array_line[cleaned_headers.index(utils.COL_DOWNVOTES)]
            edit_time = array_line[cleaned_headers.index(utils.COL_EDITED)]
            edit_user = array_line[cleaned_headers.index(utils.COL_EDITAUTHOR)]
            edit_reason = array_line[cleaned_headers.index(utils.COL_EDITREASON)]
            """

            topic_name = lda.predict_topic(comment)  # assign LDA topic


            line = utils.DELIMITER.join(array_line).replace("0000-00-00 00:00:00","")  # removing invalid/null timestamps
            line += utils.DELIMITER + topic_name + utils.DELIMITER
            if user_id not in all_users:
                print("WARNING: user_id " + str(user_id) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " not in "+ utils.FILE_POSTS+utils.FILE_EXTENSION)
                line += "" + utils.DELIMITER + ""
            else:
                line += getattr(all_users[user_id], 'voting_cond')
                line += utils.DELIMITER + getattr(all_users[user_id], 'prompting_cond')
                file_out.write(line + '\n')

        csvfile.close()
        file_out.close()

    print("Done processing " + filename +"\n")

def process_prompts(filename=utils.FILE_POSTS+utils.FILE_EXTENSION):
    """
    Parses a CSV file with the students' comments, user ids, and timestamps and assigns an automated topic.
    IMPORTANT: Either all commas must be removed from the comment text beforehand, or some unique delimiter
    must be used instead of commas.
    :return:
    """
    print("Processing " + filename)
    with open(filename, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        cleaned_headers = [s.replace(' ', '') for s in headers]  # removing spaces

        # reading comments in initially and passing to LDA topic model
        for array_line in rows:
            comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]
            if len(comment) > 0:
                list_sentences.append(ldat.to_bow(ldat.clean_string(comment)))
        print("Done processing "+filename+"\n")

        # preparing to output LDA topic analysis stuff
        print("\tProcessing " + utils.LDA_FILE+utils.FILE_EXTENSION)
        csvfile.seek(0)  # start at beginning of file again
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        file_out = open(utils.LDA_FILE+utils.FILE_EXTENSION, 'w')
        file_out.write(utils.DELIMITER.join(cleaned_headers))
        file_out.write(utils.DELIMITER + utils.COL_LDA + utils.DELIMITER + utils.COL_VOTING + utils.DELIMITER + utils.COL_PROMPTS + '\n')

        lda = ldat(utils.NUM_LDA_TOPICS, list_sentences)  # create topic model

        for array_line in rows:
            recipients = array_line[cleaned_headers.index(utils.COL_RECIPIENTS)]
            print(recipients)
            """# Don't need to store these
            prompt_id = array_line[cleaned_headers.index(utils.COL_ID)]
            parent_type = array_line[cleaned_headers.index(utils.COL_PARENTTYPE)]
            parent_id = array_line[cleaned_headers.index(utils.COL_PARENT_ID)]
            author_id = array_line[cleaned_headers.index(utils.COL_AUTHOR_ID)]
            message = array_line[cleaned_headers.index(utils.COL_MESSAGE)]
            prompt_type = int(array_line[cleaned_headers.index(utils.COL_PROMPT_TYPE)])
            encouragement = array_line[cleaned_headers.index(utils.COL_ENCOURAGEMENT_TYPE)]
            timestamp = array_line[cleaned_headers.index(utils.COL_TIMESTAMP)]
            author = array_line[cleaned_headers.index(utils.COL_AUTHOR)]
            """

            line = utils.DELIMITER.join(array_line)

            file_out.write(line + '\n')
        csvfile.close()
        file_out.close()

    print("Done processing " + filename +"\n")

def get_timestamp(tstamp):
    """
    Clean the timestamp from a string in the logfiles
    :param tstamp: string containing the timestamp
    :return: the datetime object
    """
    try:
        tstamp = datetime.datetime.strptime(tstamp, '%Y-%m-%dT%H:%M:%S.%f')  # TODO adjust for matching datetime format
    except ValueError as err:
        print(tstamp, err)
    return tstamp

if __name__ == '__main__':
    print("Running logfileSPOC")
    run()