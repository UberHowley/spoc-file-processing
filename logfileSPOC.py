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
    process_comments()
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
            if int(user_id) not in utils.DROP_STUDENTS and int(user_id) in utils.CONSENTING_STUDENTS:  # only store consenting students' info
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
        del cleaned_headers[len(cleaned_headers)-1]  # last column header is blank for some reason
        cleaned_headers.remove(utils.COL_ORIGINAL)  # this column is blank, remove it

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
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER, lineterminator='\n')
        headers = next(rows)  # skip first header row
        with open(utils.LDA_FILE+utils.FILE_EXTENSION, 'w', encoding="utf8") as csvout:
            file_out = csv.writer(csvout, delimiter=utils.DELIMITER,quotechar='\"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            file_out.writerow(cleaned_headers + [utils.COL_LDA, utils.COL_HELP] + user.UserSPOC.get_headers(utils.DELIMITER).split(utils.DELIMITER))

            lda = ldat(utils.NUM_LDA_TOPICS, list_sentences)  # create topic model
            count_consenting_crams = 0

            for array_line in rows:
                user_id = array_line[cleaned_headers.index(utils.COL_AUTHOR)].strip()
                parent_id = array_line[cleaned_headers.index(utils.COL_PARENT_ID)].strip()
                tstamp = array_line[cleaned_headers.index(utils.COL_TIMESTAMP)].strip()
                datestamp = get_timestamp(tstamp)

                if user_id not in all_users or int(user_id) in utils.DROP_STUDENTS or int(user_id) not in utils.CONSENTING_STUDENTS:  # this is a non-consenting student (although info is still public)
                    print("Warning: user_id " + str(user_id) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " may not be consenting. Not writing.")
                elif not is_during_experiment(datestamp):
                    print("Warning: comment timestamp " + str(datestamp) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " is not within date range of experiment. Not writing.")
                elif not is_near_posted(datestamp, parent_id):
                    count_consenting_crams += 1
                    print("Warning: comment timestamp " + str(datestamp) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " is not near posting date of lecture #" + parent_id + ": " + str(utils.lecture_dates.get(int(parent_id), "DNE")) + ". Not writing.")
                else:
                    comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]
                    post_id = array_line[cleaned_headers.index(utils.COL_ID)]
                    slide = array_line[cleaned_headers.index(utils.COL_SLIDE)]
                    num_upvotes = int(array_line[cleaned_headers.index(utils.COL_UPVOTES)])
                    num_downvotes = array_line[cleaned_headers.index(utils.COL_DOWNVOTES)]
                    edit_time = array_line[cleaned_headers.index(utils.COL_EDITED)].replace("0000-00-00 00:00:00","")  # removing invalid/null timestamps
                    edit_user = array_line[cleaned_headers.index(utils.COL_EDITAUTHOR)]
                    edit_reason = array_line[cleaned_headers.index(utils.COL_EDITREASON)]
                    cols = [post_id,  "", tstamp, user_id, utils.COL_PARENTTYPE, utils.COL_PARENT_ID, slide, comment, num_upvotes, num_downvotes, edit_time, edit_user, edit_reason]

                    topic_name = lda.predict_topic(comment)  # assign LDA topic
                    is_help_request = is_help_topic(comment)  # determine if this is a help request

                    file_out.writerow(cols + [topic_name, str(is_help_request)] + all_users[user_id].to_string(utils.DELIMITER).split(utils.DELIMITER))

        csvfile.close()

    print("Done processing " + filename)
    print("\tNumber comments from consenting students occuring " + str(utils.WEEK_THRESHOLD) + "+ weeks after lecture posted: " + str(count_consenting_crams) + "\n")

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
            file_out = csv.writer(csvout, delimiter=utils.DELIMITER,quotechar='\"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            file_out.writerow(cleaned_headers)

            for array_line in rows:
                author_id = array_line[cleaned_headers.index(utils.COL_AUTHOR_ID)]
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

                if author_id not in all_users or int(author_id) in utils.DROP_STUDENTS or int(author_id) not in utils.CONSENTING_STUDENTS:  # this is a non-consenting student (although info is still public)
                    print("Warning: user_id " + str(author_id) + " from " + utils.PROMPT_MOD+utils.FILE_EXTENSION + " may not be consenting. Not writing.")
                else:
                    file_out.writerow(array_line)  # only writing consenting students' data
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
    Format: 2015-01-12 14:28:58
    :param tstamp: string containing the timestamp
    :return: the datetime object
    """
    try:
        tstamp = datetime.datetime.strptime(tstamp, '%Y-%m-%d %H:%M:%S')
    except ValueError as err:
        print(tstamp, err)
    return tstamp

def is_during_experiment(comment_date, first_day=utils.CONST_FIRST_DAY, last_day=utils.CONST_LAST_DAY):
    """
    Determine if given date is within the range of dates the experiment took place
    :param comment_date: date to check if it's in range
    :return: True if given date is in our restricted time range
    """
    if comment_date is not None:
        if last_day >= comment_date.date() >= first_day:
            return True
        else:  # Not in given course date range
            return False
    else:
        print("ERROR:: logfileSPOC.is_during_experiment(): Cannot process date: " + comment_date)
        return False

def is_near_posted(comment_date, lecture_id, num_weeks=utils.WEEK_THRESHOLD):
    """
    Determine if given date is within num_weeks of lecture_id
    :param instance_date: date to check if it's in range
    :param lecture_id: id number of lecture the comment date belongs to
    :param num_weeks: number of weeks comment must be posted to lecture within
    :return: True if given date is in our restricted time range
    """
    if int(lecture_id) not in utils.lecture_dates:  # there's three comments on a lecture that does not exist
        return False
    first_day = utils.lecture_dates[int(lecture_id)]
    last_day = first_day + datetime.timedelta(weeks=num_weeks)

    if comment_date is not None:
        if last_day >= comment_date.date() >= first_day:
            return True
        elif first_day > comment_date.date():
            print("WARNING: Comment was posted BEFORE lecture was posted: " + str(first_day) + " > " + str(comment_date))
        else:  # Not in given course date range
            return False
    else:
        print("ERROR:: logfileSPOC.is_near_posted(): Cannot process date: " + comment_date)
        return False

if __name__ == '__main__':
    print("Running logfileSPOC")
    run()