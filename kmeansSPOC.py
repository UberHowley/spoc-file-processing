__author__ = 'IH'
__project__ = 'spoc-file-processing'

# supporting lib for kmeans clustering
# Original by: Nitin Borwankar (Open Data Science Training)
# https://github.com/nborwankar/LearnDataScience/blob/master/notebooks/kmeans.py

import numpy as np
from sklearn.cluster import KMeans
from scipy.cluster.vq import kmeans, vq
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import utilsSPOC as utils
import pandas as pd


def load_data(filename=utils.MOD_FILE+utils.FILE_EXTENSION):
    """
    Load the data, converting categorical variables and everything else to float values.
    :param filename: filename where data is stored
    :return: a matrix of np.float64
    """
    # Exception handling in case the logfile doesn't exist
    try:
        data = pd.io.parsers.read_csv(filename, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " + filename + " does not exist. Did you run logfileSPOC.py?")

    # recoding our categorical variables as numerical values
    int_prefix = "int_"
    new_voting = int_prefix + utils.COL_VOTING
    new_prompts = int_prefix + utils.COL_PROMPTS
    data[new_voting] = pd.Categorical.from_array(data.Condition).codes  # recodes categorical vars as numerical
    data[new_prompts] = pd.Categorical.from_array(data.EncouragementType).codes  # recodes categorical vars as numerical
    columns = [new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM, utils.COL_NUM_COMMENTS]
    cluster_data = data[columns].dropna().astype(np.float64)

    # load the dataset transformed to float with numeric columns,
    # [new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM, utils.COL_NUM_COMMENTS]
    X = cluster_data.values
    return X


def run_kmeans(X, n=10):
    """
    Runs the kmeans analysis on a given dataset with given number of clusters
    :param X: dataset to cluster
    :param n: number of clusters
    :return: a large tuples of (K, KM, centroids, D_k, cIdx, dist, avgWithinSS)
    """
    _K = range(1, n)

    # scipy.cluster.vq.kmeans
    _KM = [kmeans(X, k) for k in _K]  # apply kmeans 1 to 10
    _centroids = [cent for (cent, var) in _KM]  # cluster centroids

    _D_k = [cdist(X, cent, 'euclidean') for cent in _centroids]

    _cIdx = [np.argmin(D, axis=1) for D in _D_k]
    _dist = [np.min(D, axis=1) for D in _D_k]
    _avgWithinSS = [sum(d) / X.shape[0] for d in _dist]

    return (_K, _KM, _centroids, _D_k, _cIdx, _dist, _avgWithinSS)


def plot_elbow_curve(K, avgWithinSS, kIdx=0):
    """
    Plots an elbow curve for determining how many clusters is ideal.
    The cluster number with the largest delta in y-axis is generally best
    :param K: range of clusters to explore
    :param avgWithinSS: average within sum of squares
    :param kIdx: ideal number of clusters (+1), optional for if you know the answer already
    :return: the figure and axes as a tuple
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(K, avgWithinSS, 'b*-')
    if kIdx >= 0:  # only plot the circle selector if we've passed in a value
        ax.plot(K[kIdx], avgWithinSS[kIdx], marker='o', markersize=12, markeredgewidth=2, markeredgecolor='r', markerfacecolor='None')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Average within-cluster sum of squares')
    tt = plt.title('Elbow for KMeans clustering')
    return (fig, ax)


def plot_clusters(orig, pred, outcome, yaxis, legend=True):
    """
    Wraps a number of variables and maps integers to category labels, one at a time.
    This wrapper makes it easy to interact with this code and try other variables.
    :param orig: original data to plot
    :param pred: number of clusters
    :param outcome: index of the outcome variable
    :param yaxis: what [index] to display on the y-axis
    :param legend: boolean for displaying the legend on the plots
    :return: axes plot
    """
    data = orig
    ylabels = {0: utils.COL_VOTING, 1: utils.COL_PROMPTS, 2: utils.COL_NUM_PROMPTS, 3: utils.COL_MIDTERM}
    #orig = [new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM, utils.COL_NUM_COMMENTS]
    # plot data into three clusters based on value of c
    p0 = plt.plot(data[pred == 0, outcome], data[pred == 0, yaxis], 'ro', label='group0')
    p1 = plt.plot(data[pred == 1, outcome], data[pred == 1, yaxis], 'bo', label='group1')
    p2 = plt.plot(data[pred == 2, outcome], data[pred == 2, yaxis], 'go', label='group2')
    p3 = plt.plot(data[pred == 3, outcome], data[pred == 3, yaxis], 'mo', label='group3')  # why a fourth color if only 3 clusters?

    lx = p1[0].axes.set_xlabel(utils.COL_NUM_COMMENTS)
    ly = p1[0].axes.set_ylabel(ylabels[yaxis])
    tt = plt.title('SPOC User Dataset')
    if legend:
        ll = plt.legend()
    return (p0, p1, p2, p3)

def subplot_clusters(orig, pred, outcome, legend=True):
    """
    Wraps a number of variables and maps integers to category labels as subplots.
    This wrapper makes it easy to interact with this code and try other variables.
    :param orig: original data to plot
    :param pred: number of clusters
    :param outcome: index of the outcome variable
    :param legend: boolean for displaying the legend on the plots
    :return: axes plot
    """
    data = orig
    ylabels = {0: utils.COL_VOTING, 1: utils.COL_PROMPTS, 2: utils.COL_NUM_PROMPTS, 3: utils.COL_MIDTERM}
    #orig = [new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM, utils.COL_NUM_COMMENTS]
    fig = plt.figure()

    for yaxis in range(0, 4):
        ax = fig.add_subplot(2, 2, yaxis+1)
        # plot data into three clusters based on value of c
        ax.plot(data[pred == 0, outcome], data[pred == 0, yaxis], 'ro', label='group0')
        ax.plot(data[pred == 1, outcome], data[pred == 1, yaxis], 'bo', label='group1')
        ax.plot(data[pred == 2, outcome], data[pred == 2, yaxis], 'go', label='group2')
        ax.plot(data[pred == 3, outcome], data[pred == 3, yaxis], 'mo', label='group3')  # why a fourth color if only 3 clusters?

        lx = ax.set_xlabel(utils.COL_NUM_COMMENTS)
        ly = ax.set_ylabel(ylabels[yaxis])
        tt = plt.title("SPOC User Dataset")
        if legend:
            ll = plt.legend()
    plt.tight_layout()
    plt.show()
    return ax


'''
...So that kmeansSPOC can act as either a reusable module, or as a standalone program.
'''
if __name__ == '__main__':
    X = load_data()
    #  (_K, _KM, _centroids, _D_k, _cIdx, _dist, _avgWithinSS)
    cluster_model = run_kmeans(X)
    K = cluster_model[0]
    avg_w_ss = cluster_model[6]

    # elbow plot to determine optimum number of clusters
    plot_elbow_curve(K, avg_w_ss, 2)
    plt.show()

    num_clusters = input("> How many clusters? (which num clusters had max change in y-value?)")
    km = KMeans(int(num_clusters), init='k-means++')  # initialize
    km.fit(X)
    c = km.predict(X)  # classify into however many clusters we determined appropriate

    ax = subplot_clusters(X, c, 4, False)  # column 4 is num comments
