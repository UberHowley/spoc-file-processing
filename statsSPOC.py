__author__ = 'IH'
__project__ = 'spoc-file-processing'

import pandas as pd
import utilsSPOC as utils
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot, abline_plot
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.weightstats import ttest_ind

import numpy as np
from scipy.cluster.vq import kmeans,vq
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
#import kmeans as mykm

def run():
    """
    run function - coordinates the main statistical analyses
    :return: None
    """
    # Exception handling in case the logfile doesn't exist
    filename = utils.MOD_FILE+utils.FILE_EXTENSION
    try:
        data = pd.io.parsers.read_csv(filename, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " +utils.MOD_FILE+utils.FILE_EXTENSION + " does not exist. Did you run logfileSPOC.py?")

    cluster(data)

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data)
    user_input = input(">> Display descriptive statistics plot? [y/n]: ")
    if is_yes(user_input):
        compare_plot_instances(data)

    user_input = input(">> Display descriptive plot of " + utils.COL_NUM_COMMENTS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data)

    user_input = input("> Display comparison plots of conditions -> "+utils.COL_NUM_COMMENTS+"? [y/n]: ")
    if is_yes(user_input):
        compare_plot_helpers(data)

    user_input = input("> Print t-test statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        t_test(data)

    user_input = input("> Print One-Way ANOVA statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        one_way_anova(data)

    user_input = input("> Print Two-Way ANOVA Interaction voting*prompt statistics? [y/n]: ")
    if is_yes(user_input):
        anova_interaction(data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

def cluster(data):
    """
    Trying out unsupervised clustering
    http://nbviewer.ipython.org/github/nborwankar/LearnDataScience/blob/master/notebooks/D3.%20K-Means%20Clustering%20Analysis.ipynb
    :param data: the data loaded into a DataFrame
    :return:
    """
    # recoding our categorical variables as numerical values
    int_prefix = "int_"
    new_voting = int_prefix + utils.COL_VOTING
    new_prompts = int_prefix + utils.COL_PROMPTS
    data[new_voting] = pd.Categorical.from_array(data.Condition).codes
    data[new_prompts] = pd.Categorical.from_array(data.EncouragementType).codes
    cluster_data = data[[new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_NUM_COMMENTS, utils.COL_MIDTERM]].dropna().astype(np.float64)

    # We run the following SciPy and NumPy code in [1]
    # and generate the plots mentioned above using Matplotlib

    # load the dataset transformed to float with 5 numeric columns,
    # voting, prompts, numPrompts, numComments, midterm
    X = cluster_data.values

    ##### cluster data into K=1..10 clusters #####
    #K, KM, centroids,D_k,cIdx,dist,avgWithinSS = kmeans.run_kmeans(X,10)
    K = range(1, 10)

    # scipy.cluster.vq.kmeans
    KM = [kmeans(X, k) for k in K]  # apply kmeans 1 to 10
    centroids = [cent for (cent, var) in KM]   # cluster centroids

    D_k = [cdist(X, cent, 'euclidean') for cent in centroids]

    cIdx = [np.argmin(D, axis=1) for D in D_k]
    dist = [np.min(D, axis=1) for D in D_k]
    avgWithinSS = [sum(d)/X.shape[0] for d in dist]

    kIdx = 2
    # plot elbow curve
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(K, avgWithinSS, 'b*-')
    ax.plot(K[kIdx], avgWithinSS[kIdx], marker='o', markersize=12, markeredgewidth=2, markeredgecolor='r', markerfacecolor='None')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Average within-cluster sum of squares')
    tt = plt.title('Elbow for K-Means clustering')
    plt.show()

    num_clusters = input("> How many clusters? ")
    km = KMeans(int(num_clusters), init='k-means++')  # initialize
    km.fit(X)
    c = km.predict(X)  # classify into three clusters

    # TODO: elbow plot works, now...
    # see the code in helper library kmeans.py
    # it wraps a number of variables and maps integers to categoriy labels
    # this wrapper makes it easy to interact with this code and try other variables
    # as we see below in the next plot
    #(pl0,pl1,pl2) = mykm.plot_clusters(X,c,3,2) # column 3 GDP, vs column 2 infant mortality. Note indexing is 0 based

def t_test(data):
    """
    T-test to predict each condition --> num helpers selected
    http://statsmodels.sourceforge.net/devel/stats.html

    Note: T-tests are for 1 categorical variable with 2 levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """
    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]
    # utils.COL_VERSION -> has 'TA' and 'student' instead of 'y' and 'n'

    fig = plt.figure()
    i = 1

    for cond in conditions:
        df = data[[cond, utils.COL_NUM_COMMENTS]].dropna()
        cat1 = df[df[cond] == utils.COND_PROMPT_POS][utils.COL_NUM_COMMENTS]
        cat2 = df[df[cond] == utils.COND_PROMPT_NEUTRAL][utils.COL_NUM_COMMENTS]

        print("\n"+utils.FORMAT_LINE)
        print("T-test: " + cond)
        print(utils.FORMAT_LINE)
        print(ttest_ind(cat1, cat2))  # returns t-stat, p-value, and degrees of freedom
        print("(t-stat, p-value, df)")

        ax = fig.add_subplot(1, 2, i)
        ax = df.boxplot(utils.COL_NUM_COMMENTS, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(utils.COL_NUM_COMMENTS)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        plt.show()

def one_way_anova(data):
    """
    One-way ANOVA to predict each condition --> num helpers selected
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 1way ANOVAs are for 1 categorical independent/causal variable with 3+ levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """
    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]
    linear_df = data[[utils.COL_VOTING, utils.COL_PROMPTS, utils.COL_NUM_COMMENTS]]

    fig = plt.figure()
    i = 1

    for cond in conditions:
        cond_table = linear_df[[cond, utils.COL_NUM_COMMENTS]].dropna()
        cond_lm = ols(utils.COL_NUM_COMMENTS + " ~ C(" + cond + ")", data=cond_table).fit()
        anova_table = anova_lm(cond_lm)

        print("\n"+utils.FORMAT_LINE)
        print("One-Way ANOVA: " + cond)
        print(utils.FORMAT_LINE)
        print(anova_table)
        #print(cond_lm.model.data.orig_exog)
        print(cond_lm.summary())

        ax = fig.add_subplot(1, 2, i)
        ax = cond_table.boxplot(utils.COL_NUM_COMMENTS, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(utils.COL_NUM_COMMENTS)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        plt.show()


def anova_interaction(data):
    """
    Two-way ANOVA and interaction analysis of badges*voting --> num helpers selected
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 2way ANOVAs are for 2+ categorical independent/causal variables, with 2+ levels each
    :param data: data frame containing the independent and dependent variables
    :return: None
    """

    factor_groups = data[[utils.COL_VOTING, utils.COL_PROMPTS, utils.COL_NUM_COMMENTS]].dropna()

    # two-way anova
    formula = utils.COL_NUM_COMMENTS + " ~ C(" + utils.COL_PROMPTS + ") + C(" + utils.COL_VOTING + ")"
    formula_interaction = formula.replace('+', '*')
    badge_vote_lm = ols(formula, data=factor_groups).fit()  # linear model
    print(badge_vote_lm.summary())

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUM_COMMENTS + " = " + utils.COL_PROMPTS + " * " + utils.COL_VOTING + " Interaction -")
    print(anova_lm(ols(formula_interaction, data=factor_groups).fit(), badge_vote_lm))

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUM_COMMENTS + " = " + utils.COL_PROMPTS + " + " + utils.COL_VOTING + " ANOVA -")
    print(anova_lm(ols(utils.COL_NUM_COMMENTS + " ~ C(" + utils.COL_PROMPTS + ")", data=factor_groups).fit(), ols(utils.COL_NUM_COMMENTS +" ~ C("+utils.COL_PROMPTS+") + C(" + utils.COL_VOTING+", Sum)", data=factor_groups).fit()))

    print(utils.FORMAT_LINE)
    print("- " + utils.COL_NUM_COMMENTS + " = " + utils.COL_PROMPTS + " + " + utils.COL_VOTING + " ANOVA -")
    print(anova_lm(ols(utils.COL_NUM_COMMENTS + " ~ C(" + utils.COL_VOTING + ")", data=factor_groups).fit(), ols(utils.COL_NUM_COMMENTS +" ~ C("+utils.COL_PROMPTS+") + C(" + utils.COL_VOTING+", Sum)", data=factor_groups).fit()))

    # interaction plot
    user_input = input(">> Display Interaction plot? [y/n]: ")

    if is_yes(user_input):
        # TODO: fix the boxplot generating a separate plot (why doesn't subplots work?)
        plt.figure()

        plt.subplot(121)
        interaction_plot(factor_groups[utils.COL_VOTING], factor_groups[utils.COL_PROMPTS], factor_groups[utils.COL_NUM_COMMENTS], colors=['red', 'blue', 'green'], markers=['D', '^', 'o'], ms=10, ax=plt.gca())

        plt.subplot(122)
        factor_groups.boxplot(return_type='axes', column=utils.COL_NUM_COMMENTS, by=[utils.COL_PROMPTS, utils.COL_VOTING])
        plt.show()

def compare_plot_helpers(data):
    """
    Print comparison plots for given data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
    # TODO: These should be box plots, not bar plots
    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]
    fig = plt.figure()
    i = 1
    for cond in conditions:
        ax = fig.add_subplot(1, 2, i)
        #df_compare = pd.concat([data.groupby(cond)[cond].count(), data.groupby(cond)[utils.COL_NUMHELPERS].mean()], axis=1) # displays num helpers selected in each condition
        df_compare = data.groupby(cond)[utils.COL_NUM_COMMENTS].mean()  # displays num helpers selected in each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("mean " + utils.COL_NUM_COMMENTS)
        i += 1
    plt.show()

def compare_plot_instances(data):
    """
    Print comparison plots for given data frame, show num instances in each condition
    :param data: pandas dataframe we are exploring
    :return: None
    """
    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]
    fig = plt.figure()
    i = 1
    for cond in conditions:
        ax = fig.add_subplot(1, 2, i)
        df_compare = data.groupby(cond)[cond].count()  # displays num instances assigned to each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("count instances")
        i += 1
    plt.show()


def descriptive_plot(data):
    """
    Print descriptive plot for give data frame
    :param data: pandas dataframe we are exploring
    :return: None
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    comments_hist = data[utils.COL_NUM_COMMENTS]
    ax1 = comments_hist.plot(kind='hist', title="Histogram Num Helpers Selected", by=utils.COL_NUM_COMMENTS)
    #ax1.locator_params(axis='x', nbins=10)
    ax1.set_xlabel(utils.COL_NUM_COMMENTS)
    ax1.set_ylabel("Count")

    ax2 = fig.add_subplot(122)
    prompts_hist = data[utils.COL_NUM_PROMPTS]
    ax2 = prompts_hist.plot(kind='hist', title="Histogram Num Helpers Selected", by=utils.COL_NUM_PROMPTS)
    #ax2.locator_params(axis='x', nbins=10)
    ax2.set_xlabel(utils.COL_NUM_PROMPTS)
    ax2.set_ylabel("Count")
    plt.show()

def descriptive_stats(data):
    """
    Print descriptive statistics for give data frame

    # Note: Descriptive stats help check independent/causal vars (that are categorical) for even assignment/distribution
    # Note: For scalar indepenent variables, you check for normal distribution (easy way: distribution plots)
    :param data: pandas dataframe we are exploring
    :return: None
    """
    # Summary of numerical columns
    numerical = [utils.COL_NUM_COMMENTS, utils.COL_NUM_PROMPTS, utils.COL_NUM_UPVOTES, utils.COL_NUM_DOWNVOTES, utils.COL_MIDTERM]
    numerical.extend(utils.COL_ASSIGNMENTS)
    numerical.extend(utils.COL_EXERCISE)
    cols = data[numerical]
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: numerical columns")
    print(cols.describe())
    print(utils.FORMAT_LINE)

    # Descriptive Statistics of conditions
    print(utils.FORMAT_LINE)
    print("Descriptive statistics for: all conditions")
    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]
    print(data.describe())
    df_conditions = data[conditions]
    print(df_conditions.describe())

    # Count/Descriptive Stats of individual conditions & mean num helps of each (2^5) conditions
    print(utils.FORMAT_LINE)
    print("Breakdown by Condition: ")
    for cond in conditions:
        print(utils.FORMAT_LINE)
        print("Counts & Mean " + utils.COL_NUM_COMMENTS + " for: \'" + cond)
        print(pd.concat([data.groupby(cond)[cond].count(), data.groupby(cond)[utils.COL_NUM_COMMENTS].mean(), data.groupby(cond)[utils.COL_NUM_PROMPTS].mean()], axis=1))
    print(utils.FORMAT_LINE)

'''
...So that statsMOOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
