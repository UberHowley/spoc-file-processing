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
    # Exception handling in case the logfile doesn't exist
    try:
        data = pd.io.parsers.read_csv(filename, encoding="utf-8-sig")
    except OSError as e:
        print("ERROR: " +utils.MOD_FILE+utils.FILE_EXTENSION + " does not exist. Did you run logfileSPOC.py?")

    # recoding our categorical variables as numerical values
    int_prefix = "int_"
    new_voting = int_prefix + utils.COL_VOTING
    new_prompts = int_prefix + utils.COL_PROMPTS
    data[new_voting] = pd.Categorical.from_array(data.Condition).codes
    data[new_prompts] = pd.Categorical.from_array(data.EncouragementType).codes
    columns = [utils.COL_NUM_COMMENTS, new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM]
    cluster_data = data[columns].dropna().astype(np.float64)

    # load the dataset transformed to float with numeric columns,
    # voting, prompts, numPrompts, numComments, midterm
    X = cluster_data.values
    return X


def run_kmeans(X, n=10):
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
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(K, avgWithinSS, 'b*-')
    if kIdx is not 0:  # only plot the circle selector if we've passed in a value
        ax.plot(K[kIdx], avgWithinSS[kIdx], marker='o', markersize=12, markeredgewidth=2, markeredgecolor='r', markerfacecolor='None')
    plt.grid(True)
    plt.xlabel('Number of clusters')
    plt.ylabel('Average within-cluster sum of squares')
    tt = plt.title('Elbow for KMeans clustering')
    return (fig, ax)


def plot_clusters(orig, pred, nx, ny, legend=True):
    data = orig
    import matplotlib.pyplot as plt

    ylabels = {0: 'Male life expectancy in yrs', 1: 'Female life expectancy in yrs', 2: 'Infant mortality, per 1000'}
    # plot data into three clusters based on value of c
    #columns = [utils.COL_NUM_COMMENTS, new_voting, new_prompts, utils.COL_NUM_PROMPTS, utils.COL_MIDTERM]
    p0 = plt.plot(data[pred == 0, nx], data[pred == 0, ny], 'ro', label='Underdeveloped')
    p2 = plt.plot(data[pred == 2, nx], data[pred == 2, ny], 'go', label='Developing')
    p1 = plt.plot(data[pred == 1, nx], data[pred == 1, ny], 'bo', label='Developed')

    lx = p1[0].axes.set_xlabel(utils.NUM_COMMENTS)
    ly = p1[0].axes.set_ylabel(ylabels[ny])
    tt = plt.title('UN countries Dataset, KMeans clustering with K=3')
    if legend:
        ll = plt.legend()
    return (p0, p1, p2)

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
    plot_elbow_curve(K, avg_w_ss)
    plt.show()

    num_clusters = input("> How many clusters? (which num clusters had max change in y-value?)")
    km = KMeans(int(num_clusters), init='k-means++')  # initialize
    km.fit(X)
    c = km.predict(X)  # classify into however many clusters we determined appropriate

    # TODO: Plotting the clusters
    # see the code in helper library kmeansSPOC.py
    # it wraps a number of variables and maps integers to category labels
    # this wrapper makes it easy to interact with this code and try other variables
    # as we see below in the next plot
    """
    for i in range(1, len(columns)-1):
        (pl0, pl1, pl2) = plot_clusters(X, c, 0, i)  # column 0 is num comments
    """

    """# Examples from original
    (pl0,pl1,pl2) = mykm.plot_clusters(X,c,3,2) # column 3 GDP, vs column 2 infant mortality. Note indexing is 0 based
    (pl0,pl1,pl2) = mykm.plot_clusters(X,c,3,0,False)
    (pl0,pl1,pl2) = mykm.plot_clusters(X,c,3,1,False)
    """