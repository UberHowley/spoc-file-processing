__author__ = 'IH'
__project__ = 'spoc-file-processing'

import pandas as pd
import utilsSPOC as utils
import matplotlib.pyplot as plt
from statsmodels.formula.api import ols
from statsmodels.graphics.api import interaction_plot
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.weightstats import ttest_ind

FORMAT_LINE = utils.FORMAT_LINE

def run(filename=utils.MOD_FILE+utils.FILE_EXTENSION):
    """
    run function - coordinates the main statistical analyses
    :return: None
    """
    # Exception handling in case the logfile doesn't exist
    try:
        data = pd.io.parsers.read_csv(filename, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " + filename + " does not exist. Did you run logfileSPOC.py?")

    conditions = [utils.COL_VOTING, utils.COL_PROMPTS]

    user_input = input("> Print descriptive statistics? [y/n]: ")
    if is_yes(user_input):
        descriptive_stats(data[conditions+[utils.COL_NUM_COMMENTS]].dropna())
    user_input = input(">> Display descriptive statistics plot? [y/n]: ")
    if is_yes(user_input):
        compare_plot_instances(data[conditions])

    user_input = input(">> Display descriptive plot of " + utils.COL_NUM_COMMENTS + "? [y/n]: ")
    if is_yes(user_input):
        descriptive_plot(data[[utils.COL_NUM_COMMENTS]])

    user_input = input("> Display comparison plots of conditions -> "+utils.COL_NUM_COMMENTS+"? [y/n]: ")
    if is_yes(user_input):
        compare_plot_outcome(data[conditions+[utils.COL_NUM_COMMENTS]].dropna())

    user_input = input("> Print t-test statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        t_test(data[conditions+[utils.COL_NUM_COMMENTS]].dropna(), utils.COND_PROMPT_POS, utils.COND_PROMPT_NEUTRAL)

    user_input = input("> Print One-Way ANOVA statistics for all conditions? [y/n]: ")
    if is_yes(user_input):
        one_way_anova(data[conditions+[utils.COL_NUM_COMMENTS]].dropna())

    user_input = input("> Print Two-Way ANOVA Interaction " + str(conditions) + " statistics? [y/n]: ")
    exp_data = data[conditions + [utils.COL_NUM_COMMENTS]]
    anova_interaction(exp_data)
    if is_yes(user_input):
        anova_interaction(exp_data)
        user_input = input(">> Display Interaction plot? [y/n]: ")
        if is_yes(user_input):
            plot_interaction(exp_data)


def is_yes(stri):
    """
    Return True if the given string contains a 'y'
    :param str: a string, likely a user console input
    :return: True if the string contains the letter 'y'
    """
    return 'y' in stri.lower()

def t_test(data_lastDV, group1, group2):
    """
    T-test to predict each condition --> numerical outcome variable
    Last column is the outcome variable (DV)
    http://statsmodels.sourceforge.net/devel/stats.html

    Note: T-tests are for 1 categorical variable with 2 levels
    :param data: data frame containing the independent and dependent variables
    :return: None
    """

    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1

    for cond in col_names:
        df = data_lastDV[[cond, outcome]].dropna()
        cat1 = df[df[cond] == group1][outcome]
        cat2 = df[df[cond] == group2][outcome]

        print("\n"+FORMAT_LINE)
        print("T-test: " + cond)
        print(FORMAT_LINE)
        print(ttest_ind(cat1, cat2))  # returns t-stat, p-value, and degrees of freedom
        print("(t-stat, p-value, df)")

        ax = fig.add_subplot(1,2, i)
        ax = df.boxplot(outcome, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(outcome)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        fig.tight_layout()
        plt.show()

def one_way_anova(data_lastDV):
    """
    One-way ANOVA to predict each condition --> numerical outcome variable
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 1way ANOVAs are for 1 categorical independent/causal variable with 3+ levels
    :param data: data frame containing the independent and dependent variables (DV is last item in list)
    :return: None
    """
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    fig = plt.figure()
    i = 1

    for cond in col_names:
        cond_table = data_lastDV[[cond, outcome]].dropna()
        cond_lm = ols(outcome + " ~ C(" + cond + ")", data=cond_table).fit()
        anova_table = anova_lm(cond_lm)

        print("\n"+FORMAT_LINE)
        print("One-Way ANOVA: " + cond + " --> " + outcome)
        print(FORMAT_LINE)
        print(anova_table)
        #print(cond_lm.model.data.orig_exog)
        print(cond_lm.summary())

        ax = fig.add_subplot(1,2, i)
        ax = cond_table.boxplot(outcome, cond, ax=plt.gca())
        ax.set_xlabel(cond)
        ax.set_ylabel(outcome)
        i += 1
    # box plot
    user_input = input(">> Display boxplot of conditions? [y/n]: ")
    if is_yes(user_input):
        fig.tight_layout()
        plt.show()


def anova_interaction(data_lastDV):
    """
    Two-way ANOVA and interaction analysis of given data
    http://statsmodels.sourceforge.net/devel/examples/generated/example_interactions.html

    Note: 2way ANOVAs are for 2+ categorical independent/causal variables, with 2+ levels each
    :param data: data frame containing the independent variables in first two columns, dependent in the third
    :return: None
    """

    col_names = data_lastDV.columns.values  # get the columns' names
    factor_groups = data_lastDV[col_names].dropna()
    if len(col_names) < 3:
        print("ERROR in statsMOOC.py: Not enough columns in dataframe to do interaction analysis: " + len(col_names))

    # two-way anova
    formula = col_names[2] + " ~ C(" + col_names[0] + ") + C(" + col_names[1] + ")"
    formula_interaction = formula.replace('+', '*')
    interaction_lm = ols(formula, data=factor_groups).fit()  # linear model
    print(interaction_lm.summary())

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " * " + col_names[1] + " Interaction -")
    print(anova_lm(ols(formula_interaction, data=factor_groups).fit(), interaction_lm))

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[0] + " + " + col_names[1] + " ANOVA -")
    print(anova_lm(ols(col_names[2] + " ~ C(" + col_names[0] + ")", data=factor_groups).fit(), ols(col_names[2] +" ~ C("+col_names[0]+") + C(" + col_names[1]+", Sum)", data=factor_groups).fit()))

    print(FORMAT_LINE)
    print("- " + col_names[2] + " = " + col_names[1] + " + " + col_names[0] + " ANOVA -")
    print(anova_lm(ols(col_names[2] + " ~ C(" + col_names[1] + ")", data=factor_groups).fit(), ols(col_names[2] +" ~ C("+col_names[0]+") + C(" + col_names[1]+", Sum)", data=factor_groups).fit()))

def plot_interaction(data_lastDV):
    """
    Plot the interaction of the given data (should be three columns)
    :param data: data frame containing the independent variables in first two columns, dependent in the third
    :return: None
    """
    col_names = data_lastDV.columns.values  # get the columns' names
    factor_groups = data_lastDV[col_names].dropna()

    # TODO: fix the boxplot generating a separate plot (why doesn't subplots work?)
    fig = plt.figure()

    plt.subplot(121)
    interaction_plot(factor_groups[col_names[0]], factor_groups[col_names[1]], factor_groups[col_names[2]], colors=['red', 'blue', 'green'], markers=['D', '^', 'o'], ms=10, ax=plt.gca())

    plt.subplot(122)
    factor_groups.boxplot(return_type='axes', column=col_names[2], by=[col_names[0], col_names[1]])
    fig.tight_layout()
    plt.show()

def compare_plot_outcome(data_lastDV):
    """
    Print comparison plots for given data frame
    :param data: dataframe with all variables. Outcome variable in last index.
    :return: None
    """
    # TODO: These should be box plots, not bar plots
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    dimension = 2  # TODO: figure out better way to organize plots by location

    fig = plt.figure()
    i = 1
    for cond in col_names:
        ax = fig.add_subplot(len(col_names)/dimension, dimension, i)
        #df_compare = pd.concat([data.groupby(cond)[cond].count(), data.groupby(cond)[outcome].mean()], axis=1) # displays num helpers selected in each condition
        df_compare = data_lastDV.groupby(cond)[outcome].mean()  # displays num helpers selected in each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("mean " + outcome)
        i += 1
    fig.tight_layout()
    plt.show()

def compare_plot_instances(data_causal):
    """
    Print comparison plots for given data frame, show num instances in each condition
    :param data: pandas dataframe we are exploring
    :return: None
    """
    col_names = data_causal.columns.values  # get the columns' names
    dimension = 2  # TODO: figure out better way to organize plots by location

    fig = plt.figure()
    i = 1
    for cond in col_names:
        ax = fig.add_subplot(len(col_names)/dimension, dimension, i)
        df_compare = data_causal.groupby(cond)[cond].count()  # displays num instances assigned to each condition
        ax = df_compare.plot(kind='bar', title=cond)
        ax.set_xlabel(cond)
        ax.set_ylabel("count instances")
        i += 1
    fig.tight_layout()
    plt.show()


def descriptive_plot(data_onlyDV):
    """
    Print descriptive plots for given data frame (one column of numerical data)
    :param data: pandas dataframe we are exploring
    :return: None
    """
    outcome = data_onlyDV.columns.values[0]  # get the outcome column name

    fig = plt.figure()
    # TODO: subplots appear in same frame instead of 3 separate ones (!!!)
    ax1 = fig.add_subplot(121)
    ax1 = data_onlyDV.plot(kind='hist', title="Histogram: "+outcome, by=outcome)
    ax1.locator_params(axis='x', nbins=4)
    ax1.set_xlabel(outcome+" bins")
    ax1.set_ylabel("Num Instances")

    ax2 = fig.add_subplot(122)
    ax2 = data_onlyDV.plot(kind='kde', title="KDE Density Plot: "+outcome)

    fig.tight_layout()
    plt.show()

def descriptive_stats(data_lastDV):
    """
    Print descriptive statistics for give data frame. If there's *ANY* numerical data before the last column in the
    dataframe, this might ONLY print the numerical columns data. Maybe.

    # Note: Descriptive stats help check independent/causal vars (that are categorical) for even assignment/distribution
    # Note: For scalar indepenent variables, you check for normal distribution (easy way: distribution plots)
    :param data: pandas dataframe we are exploring
    :return: None
    """
    col_names = data_lastDV.columns.values.tolist()  # get the columns' names
    outcome = col_names.pop()  # remove the last item in the list

    # Summary of Number of Helpers Selected
    print(FORMAT_LINE)
    print("Descriptive statistics for: \'" + outcome+"\'")
    print(data_lastDV[outcome].describe())
    print(FORMAT_LINE)

    # Descriptive Statistics of conditions
    print(FORMAT_LINE)
    print("Descriptive statistics for: all conditions")
    df_conditions = data_lastDV[col_names]
    print(df_conditions.describe())
    df_conditions = data_lastDV[col_names+[outcome]]  # add numerical column back in for descriptive stats

    # Count/Descriptive Stats of individual conditions & mean num helps of each (2^5) conditions
    for cond in col_names:
        print(FORMAT_LINE)
        print("Counts & Mean " + outcome + " for: \'" + cond)
        print(pd.concat([df_conditions.groupby(cond)[cond].count(), df_conditions.groupby(cond)[outcome].mean()], axis=1))

'''
...So that statsSPOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    run()
