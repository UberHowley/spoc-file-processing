__author__ = 'IH'
__project__ = 'spoc-file-processing'

import csv
import datetime
import utilsSPOC as utils
import UserSPOC as user
from topicModelLDA import LDAtopicModel as ldat
import liwc as liwc

# variables
is_only_second_half = True
all_users = {}  # uid -> UserSPOC: all users in the file and their conditions
list_sentences = []  # a list of bag of words from all comments

first_prompt_dates = {}  # uid --> timestamp: first time of prompt being received by student

def run():
    process_conditions()
    process_comments()
    process_prompts()

    # writing the users file to CSV
    filename = utils.MOD_FILE + utils.FILE_EXTENSION
    if is_only_second_half:
        filename = utils.MOD_FILE + utils.MT_FILE + utils.FILE_EXTENSION

    modfile_out = open(filename, 'w')
    modfile_out.write(user.UserSPOC.get_headers(utils.DELIMITER) + '\n')

    for usr in all_users:
        modfile_out.write(all_users[usr].to_string(utils.DELIMITER) + '\n')
    modfile_out.close()


def process_conditions(filename=utils.FILE_CONDITIONS+utils.FILE_EXTENSION):
    """
    Calculate the average per-user accuracy (user’s percentage correct / total problems done)
    and user accuracy segmented by engagement level (by your categorization from the previous section). What trends do you see?
    :return: None
    """
    # --------------------
    print("Processing " + filename)

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
            tot_late = array_line[cleaned_headers.index(utils.COL_TOT_LATE)]
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
            exams.extend([array_line[cleaned_headers.index(utils.COL_E1)], array_line[cleaned_headers.index(utils.COL_E1D)], array_line[cleaned_headers.index(utils.COL_E1F)], array_line[cleaned_headers.index(utils.COL_E2)]])
            midterm = array_line[cleaned_headers.index(utils.COL_MIDGRADE)]

            if int(num_prompts) < 1:  # had to have seen at least one prompt in order to be in a prompting condition!
                prompting_cond = utils.COND_NO_PROMPT

            # first prompt date
            first_prompt = utils.first_prompts.get(int(user_id.strip()), "")
            if len(first_prompt) > 1 :
                first_prompt = datetime.datetime.strptime(first_prompt, '%m/%d/%Y')

            new_user = user.UserSPOC(user_id, num_comments, voting_cond, prompting_cond, int(num_prompts), num_upvotes, num_downvotes, assignments, assignment_lates, tot_late, exams, midterm, exercises, first_prompt)

            # removing students from list
            if is_consenting_student(user_id):  # only store consenting students' info
                all_users[user_id] = new_user

    csvfile.close()
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

            if len(comment) > 0 and is_consenting_student(user_id):  # only include comment in LDA model if student is consenting
                list_sentences.append(ldat.to_bow(ldat.clean_string(comment)))
        print("Done processing "+filename+"\n")

        # preparing to output LDA topic analysis stuff
        print("\tProcessing " + utils.LDA_FILE+utils.FILE_EXTENSION)
        csvfile.seek(0)  # start at beginning of file again
        rows = csv.reader(csvfile, delimiter=utils.DELIMITER, lineterminator='\n')
        headers = next(rows)  # skip first header row

        # load up LIWC libraries for quick sentiment analysis
        sentiment = liwc.liwc()

        filename = utils.LDA_FILE+utils.FILE_EXTENSION
        if is_only_second_half:
            filename = utils.LDA_FILE + utils.MT_FILE + utils.FILE_EXTENSION
        with open(filename, 'w', encoding="utf8") as csvout:
            file_out = csv.writer(csvout, delimiter=utils.DELIMITER,quotechar='\"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
            new_headers = cleaned_headers
            new_headers += ["num_days_after_post", "lecture_post_date", "lecture_week_num", utils.COMMENT_WORDS, utils.COMMENT_CHARS]
            new_headers += [utils.LIWC_POSITIVE, utils.LIWC_NEGATIVE, utils.COL_LDA, utils.COL_HELP]
            new_headers += ["mean_word_length", "median_word_length", utils.COL_COMMENTS_AFTER_PROMPT, utils.COL_COMMENTS_WEEK_AFTER, "is_3_days_after_prompt"]
            for i in range(0, utils.NUM_LDA_TOPICS):  # topic headers for topic distribution scores
                new_headers += ["topic_" + str(i)]
            new_headers += user.UserSPOC.get_headers(utils.DELIMITER).split(utils.DELIMITER)
            file_out.writerow(new_headers)

            lda = ldat(utils.NUM_LDA_TOPICS, list_sentences)  # create topic model
            count_consenting_crams = 0

            for array_line in rows:
                user_id = array_line[cleaned_headers.index(utils.COL_AUTHOR)].strip()
                parent_id = array_line[cleaned_headers.index(utils.COL_PARENT_ID)].strip()
                tstamp = array_line[cleaned_headers.index(utils.COL_TIMESTAMP)].strip()
                datestamp = get_timestamp(tstamp)

                if user_id not in all_users or not is_consenting_student(user_id):  # this is a non-consenting student (although info is still public)
                    print("Warning: user_id " + str(user_id) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " may not be consenting. Not writing.")
                elif not is_during_experiment(datestamp):
                    print("Warning: comment timestamp " + str(datestamp) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " is not within date range of experiment. Not writing.")
                    setattr(all_users[user_id], utils.BEFORE_EXP_COMMENTS, getattr(all_users[user_id],utils.BEFORE_EXP_COMMENTS) + 1)  # keep count of comments posted too late for each user
                elif not is_near_posted(datestamp, parent_id):
                    count_consenting_crams += 1
                    setattr(all_users[user_id], utils.LATE_COMMENTS, getattr(all_users[user_id],utils.LATE_COMMENTS) + 1)  # keep count of comments posted too late for each user
                    print("Warning: comment timestamp " + str(datestamp) + " from " + utils.LDA_FILE+utils.FILE_EXTENSION + " is not near posting date of lecture #" + parent_id + ". Not writing.")
                else:
                    comment = array_line[cleaned_headers.index(utils.COL_COMMENT)]
                    post_id = array_line[cleaned_headers.index(utils.COL_ID)]
                    slide = array_line[cleaned_headers.index(utils.COL_SLIDE)]
                    num_upvotes = int(array_line[cleaned_headers.index(utils.COL_UPVOTES)])
                    num_downvotes = array_line[cleaned_headers.index(utils.COL_DOWNVOTES)]
                    edit_time = array_line[cleaned_headers.index(utils.COL_EDITED)].replace("0000-00-00 00:00:00","")  # removing invalid/null timestamps
                    edit_user = array_line[cleaned_headers.index(utils.COL_EDITAUTHOR)]
                    edit_reason = array_line[cleaned_headers.index(utils.COL_EDITREASON)]
                    ptype = array_line[cleaned_headers.index(utils.COL_PARENTTYPE)]
                    pid = array_line[cleaned_headers.index(utils.COL_PARENT_ID)]
                    cols = [post_id,  "", tstamp, user_id, ptype, pid, slide, comment, num_upvotes, num_downvotes, edit_time, edit_user, edit_reason]

                    topic_name = lda.predict_topic(comment)  # assign LDA topic
                    topic_distribution_scores = lda.topic_distribution_scores_list(comment)
                    is_help_request = is_help_topic(comment)  # determine if this is a help request

                    comment_mean_word_length = sum(len(word) for word in comment.split())/len(comment.split())  # mean word length of comment
                    word_lengths = []
                    for word in comment.split():
                        word_lengths.append(len(word))
                    comment_median_word_length = median(word_lengths)  # median word length of comment

                    # only process if we're including all valid dates
                    if not is_only_second_half or (is_only_second_half and datestamp.date() > utils.CONST_MIDTERM):
                        # add this to our count of legitimate/punctual comments
                        setattr(all_users[user_id], utils.COL_NUM_LEGIT_COMMENTS, getattr(all_users[user_id],utils.COL_NUM_LEGIT_COMMENTS) + 1)

                        # add this help request to our counts of student help requests
                        if is_help_request and all_users.get(user_id, None) is not None:
                            setattr(all_users[user_id], utils.COL_HELP_REQS, getattr(all_users[user_id],utils.COL_HELP_REQS) + 1)

                        # count num comments before and after first prompt
                        first_prompt = getattr(all_users[user_id], utils.COL_FIRST_PROMPT_DATE, None)
                        is_after = ""
                        if first_prompt is None or len(str(first_prompt)) < 1:
                            # no first prompt, nothing to change
                            setattr(all_users[user_id], utils.COL_COMMENTS_AFTER_PROMPT, "")
                            setattr(all_users[user_id], utils.COL_COMMENTS_BEFORE_PROMPT, "")
                        elif first_prompt <= datestamp:  # this comment is after the first prompt
                            setattr(all_users[user_id], utils.COL_COMMENTS_AFTER_PROMPT, getattr(all_users[user_id],utils.COL_COMMENTS_AFTER_PROMPT) + 1)
                            is_after = "y"
                        elif first_prompt > datestamp:  # this comment is before the first prompt
                            setattr(all_users[user_id], utils.COL_COMMENTS_BEFORE_PROMPT, getattr(all_users[user_id],utils.COL_COMMENTS_BEFORE_PROMPT) + 1)
                            is_after = "n"

                        # count num comments X weeks before and after first prompt
                        first_prompt = getattr(all_users[user_id], utils.COL_FIRST_PROMPT_DATE, None)
                        is_week_after = ""
                        if first_prompt is None or len(str(first_prompt)) < 1:
                            # no first prompt, nothing to change
                            setattr(all_users[user_id], utils.COL_COMMENTS_WEEK_AFTER, "")
                            setattr(all_users[user_id], utils.COL_COMMENTS_WEEK_BEFORE, "")
                        elif is_on_posted(datestamp, first_prompt) > 0:  # this comment is X weeks AFTER first prompt
                            setattr(all_users[user_id], utils.COL_COMMENTS_WEEK_AFTER, getattr(all_users[user_id], utils.COL_COMMENTS_WEEK_AFTER) + 1)
                            is_week_after = "y"
                        elif is_on_posted(datestamp, first_prompt) > -1:  # this comment is X weeks BEFORE the first prompt
                            setattr(all_users[user_id], utils.COL_COMMENTS_WEEK_BEFORE, getattr(all_users[user_id], utils.COL_COMMENTS_WEEK_BEFORE) + 1)
                            is_week_after = ""

                        # count num comments X days after first prompt
                        first_prompt = getattr(all_users[user_id], utils.COL_FIRST_PROMPT_DATE, None)
                        is_three_after = ""
                        if first_prompt is None or len(str(first_prompt)) < 1:
                            # no first prompt, nothing to change
                            is_three_after = ""
                        elif is_on_posted(datestamp, first_prompt, 3) > 0:  # this comment is X days AFTER first prompt
                            is_three_after = "y"
                            setattr(all_users[user_id], utils.COL_COMMENTS_DAYS_AFTER, getattr(all_users[user_id], utils.COL_COMMENTS_DAYS_AFTER) + 1)
                        else:
                            is_three_after = "n"

                        # LIWC - count the number of positive/negative words in the comment
                        num_positive, num_negative, num_comment_words = sentiment.count_sentiments(comment)
                        # LIWC - add these counts to our student user
                        if all_users.get(user_id, None) is not None:
                            setattr(all_users[user_id], utils.LIWC_POSITIVE, getattr(all_users[user_id], utils.LIWC_POSITIVE) + num_positive)
                            setattr(all_users[user_id], utils.LIWC_NEGATIVE, getattr(all_users[user_id], utils.LIWC_NEGATIVE) + num_negative)
                            setattr(all_users[user_id], utils.COMMENT_CHARS, getattr(all_users[user_id], utils.COMMENT_CHARS) + len(comment))
                            setattr(all_users[user_id], utils.COMMENT_WORDS, getattr(all_users[user_id], utils.COMMENT_WORDS) + num_comment_words)

                        dict_ld = dict(utils.lecture_dates)
                        # TODO: print to_counts_string() later
                        line = cols
                        line += [days_after(datestamp, parent_id), str(dict_ld[int(parent_id)]), str([y[0] for y in utils.lecture_dates].index(int(parent_id)))]
                        line += [num_comment_words, len(comment), num_positive, num_negative, topic_name, str(is_help_request), comment_mean_word_length, comment_median_word_length]
                        line += [is_after, is_week_after, is_three_after]
                        line += topic_distribution_scores
                        file_out.writerow(line + all_users[user_id].to_const_string(utils.DELIMITER).split(utils.DELIMITER))

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
        cleaned_headers += ["recip0", "recip1"]  # splitting recipients into separate columns

        filename = utils.PROMPT_MOD+utils.FILE_EXTENSION
        if is_only_second_half:
            filename = utils.PROMPT_MOD + utils.MT_FILE + utils.FILE_EXTENSION
        with open(filename, 'w') as csvout:
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

                # only process/write if during valid dates
                if not is_only_second_half or (is_only_second_half and get_timestamp(timestamp).date() > utils.CONST_MIDTERM):
                    # removing non-consenting prompt recipients
                    consenting = []
                    for recip in recipients:
                        recip = recip.replace(' ', '')
                        if is_consenting_student(recip):
                            consenting.append(recip)
                        else:
                            print("Warning: recipient of prompt (" + str(recip) + ") from " + utils.PROMPT_MOD+utils.FILE_EXTENSION + " not consenting.")
                            consenting.append("non_consent")
                    consenting.sort()
                    array_line[cleaned_headers.index(utils.COL_RECIPIENTS)] = utils.DELIMITER.join(consenting)
                    array_line += consenting
                    file_out.writerow(array_line)  # only writing consenting students' data
        csvfile.close()
    print("Done processing " + filename)

def median(x):
  """
  Takes in a list of numbers and output the middle number
  """
  if len(x) < 1:
      return 0
  x.sort()  # after taking the list, sort it
  return (x[int(len(x)/2)])

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
    :param comment_date: date to check if it's in range
    :param lecture_id: id number of lecture the comment date belongs to
    :param num_weeks: number of weeks comment must be posted to lecture within
    :return: True if given date is in our restricted time range
    """
    dict_ld = dict(utils.lecture_dates)
    if int(lecture_id) not in dict_ld:  # there's three comments on a lecture that does not exist
        return False
    first_day = dict_ld[int(lecture_id)]
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

def is_on_posted(comment_date, target_date, num_days=7):
    """
    Determine if given date is num_weeks before (0), num_weeks after (1),
    or more than 1 week (-1) from the first prompt date (target_date)
    :param comment_date: date to check if it's in range
    :param target_date: target date we're checking against
    :param num_days: number of days comment must be posted within from target_date
    :return: -1 if more than num_weeks away, 0 if before, 1 if on or after
    """
    before_deadline = target_date - datetime.timedelta(days=num_days)
    after_deadline = target_date + datetime.timedelta(days=num_days)

    if comment_date is not None:
        if target_date.date() <= comment_date.date() <= after_deadline.date():  # after target date
            return 1
        elif before_deadline.date() <= comment_date.date() < target_date.date():  # before target date
            return 0
        else:  # Not in given date range
            return -1
    else:
        print("ERROR:: logfileSPOC.is_on_posted(): Cannot process date: " + comment_date)
        return -1

def days_after(comment_date, lecture_id):
    """
    Determine number of days apart comment is from lecture it was posted to
    :param instance_date: date to check if it's in range
    :param lecture_id: id number of lecture the comment date belongs to
    :return: True if given date is in our restricted time range
    """
    dict_ld = dict(utils.lecture_dates)
    if int(lecture_id) not in dict_ld:  # there's three comments on a lecture that does not exist
        return ""
    lecture_date = dict_ld[int(lecture_id)]

    if comment_date is not None:
        return (comment_date.date() - lecture_date).days
    else:
        print("ERROR:: logfileSPOC.days_after(): Cannot process date: " + comment_date)
        return ""

def is_consenting_student(user_id):
    """
    Check to see if given user ID is a consenting one
    :param user_id: a user id to check
    :return: True if user is consenting
    """
    return int(user_id) not in utils.DROP_STUDENTS and int(user_id) in utils.CONSENTING_STUDENTS

if __name__ == '__main__':
    print("Running logfileSPOC")
    run()