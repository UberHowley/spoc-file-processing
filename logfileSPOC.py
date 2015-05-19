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

first_prompt_dates = {}  # uid --> timestamp: first time of prompt being received by student

def run():
    process_conditions()
    #process_comments()
    process_prompts()

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

            if int(num_prompts) < 1:  # had to have seen at least one prompt in order to be in a prompting condition!
                prompting_cond = ""

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
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER, skipinitialspace=True)
        headers = next(rows)  # skip first header row
        cleaned_headers = [s.replace(' ', '') for s in headers]  # removing spaces

        # reading comments in initially and passing to LDA topic model
        for array_line in rows:
            comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]
            user_id = array_line[cleaned_headers.index(utils.COL_AUTHOR)]
            if len(comment) > 0 and user_id in all_users:  # only include comment in LDA model if student is consenting
                list_sentences.append(ldat.to_bow(ldat.clean_string(comment)))
        print("Done processing "+filename+"\n")

        # preparing to output LDA topic analysis stuff
        print("\tProcessing " + utils.LDA_FILE+utils.FILE_EXTENSION)
        csvfile.seek(0)  # start at beginning of file again
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        file_out = open(utils.LDA_FILE+utils.FILE_EXTENSION, 'w', encoding="utf8")
        file_out.write(utils.DELIMITER.join(cleaned_headers))
        file_out.write(utils.COL_LDA + utils.DELIMITER + utils.COL_HELP)
        file_out.write(utils.DELIMITER + user.UserSPOC.get_headers(utils.DELIMITER) + '\n')

        lda = ldat(utils.NUM_LDA_TOPICS, list_sentences)  # create topic model

        for array_line in rows:
            user_id = array_line[cleaned_headers.index(utils.COL_AUTHOR)]

            if user_id not in all_users:  # this is a non-consenting student (although info is still public)
                print("Warning: user_id " + str(user_id) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " not in "+ utils.FILE_POSTS+utils.FILE_EXTENSION)
            else:
                comment = array_line[cleaned_headers.index(utils.COL_COMMENT)].replace(",", ";").replace("\n", " ").replace("\"", "'")  # TODO: use a CSV writer instead

                post_id = array_line[cleaned_headers.index(utils.COL_ID)]
                tstamp = array_line[cleaned_headers.index(utils.COL_TIMESTAMP)]
                slide = array_line[cleaned_headers.index(utils.COL_SLIDE)]
                num_upvotes = int(array_line[cleaned_headers.index(utils.COL_UPVOTES)])
                num_downvotes = array_line[cleaned_headers.index(utils.COL_DOWNVOTES)]
                edit_time = array_line[cleaned_headers.index(utils.COL_EDITED)].replace("0000-00-00 00:00:00","")  # removing invalid/null timestamps
                edit_user = array_line[cleaned_headers.index(utils.COL_EDITAUTHOR)]
                edit_reason = array_line[cleaned_headers.index(utils.COL_EDITREASON)]
                cols = [post_id,  "", tstamp, user_id, utils.COL_PARENTTYPE, utils.COL_PARENT_ID, slide, comment, num_upvotes, num_downvotes, edit_time, edit_user, edit_reason, ""]

                topic_name = lda.predict_topic(comment)  # assign LDA topic
                is_help_request = is_help_topic(comment)  # determine if this is a help request

                line = utils.DELIMITER.join(str(c) for c in cols)
                line += utils.DELIMITER + topic_name + utils.DELIMITER + str(is_help_request)

                line += utils.DELIMITER + all_users[user_id].to_string(utils.DELIMITER)
                file_out.write(line + '\n')

        csvfile.close()
        file_out.close()

    print("Done processing " + filename +"\n")

def process_prompts(filename=utils.FILE_PROMPTS+utils.FILE_EXTENSION):
    """
    Parses a CSV file with the students' received prompts. MUST BE SORTED BY TIMESTAMP
    :return:
    """
    print("Processing " + filename)
    with open(filename, 'r') as csvfile:
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER)
        headers = next(rows)  # skip first header row
        cleaned_headers = [s.replace(' ', '') for s in headers]  # removing spaces
        with open(utils.PROMPT_MOD+utils.FILE_EXTENSION, 'w') as csvout:
            file_out = csv.writer(csvout, delimiter=utils.DELIMITER,quotechar='\"', quoting=csv.QUOTE_MINIMAL)
            file_out.writerow(cleaned_headers)

            for array_line in rows:
                recipients = array_line[cleaned_headers.index(utils.COL_RECIPIENTS)].split(utils.DELIMITER)
                timestamp = array_line[cleaned_headers.index(utils.COL_TSTAMP)]

                """# Don't need to store these
                prompt_id = array_line[cleaned_headers.index(utils.COL_ID)]
                parent_type = array_line[cleaned_headers.index(utils.COL_PARENTTYPE)]
                parent_id = array_line[cleaned_headers.index(utils.COL_PARENT_ID)]
                author_id = array_line[cleaned_headers.index(utils.COL_AUTHOR_ID)]
                message = array_line[cleaned_headers.index(utils.COL_MESSAGE)]
                prompt_type = int(array_line[cleaned_headers.index(utils.COL_PROMPT_TYPE)])
                encouragement = array_line[cleaned_headers.index(utils.COL_ENCOURAGEMENT_TYPE)]
                author = array_line[cleaned_headers.index(utils.COL_AUTHOR)]
                """
                # store timestamp if it's the first time a user's seen the prompt
                for user in recipients:
                    user = user.strip()
                    first_prompt_dates[user] = first_prompt_dates.get(user, timestamp)
                # TODO: calculate num comments before/after first prompt --> merge with main data table

                file_out.writerow(array_line)  # don't actually need to re-write prompts file (not adding/doing), but is an example of csvwriter
        csvfile.close()
    print("Done processing " + filename)

def is_help_topic(sentence):
    """
    Determine if the given string (message post) contains a question or help request.
    :param sentence: a string sentence / message post
    :return: True if the string is about help seeking
    """
    # TODO: this is a super naive way to determine this
    if "help" in sentence or "question" in sentence or "?" in sentence or "dunno" in sentence or "n't know" in sentence:
        return True
    if "confus" in sentence or "struggl" in sentence or "lost" in sentence or "stuck" in sentence or "know how" in sentence:
        return True
    return False

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