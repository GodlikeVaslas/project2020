import numpy as np
import random


def manhattan(x, y):
    return np.sum(np.absolute(x - y))


def euclid(x, y):
    return np.linalg.norm(x - y)


def k_medoids(_data, _k, _fn, _niter):
    """
            :param _df: Input data frame.
            :param _k: Number of medoids.
            :param _fn: The distance function to use.
            :param _niter: The number of iterations.
            :return: Cluster label.
    """
    size = len(_data)
    medoids_sample = random.sample([i for i in range(size)], _k)
    prior_cost, medoids = compute_cost(_data, _fn, medoids_sample)
    current_cost = prior_cost
    iter_count = 0
    best_choices = []
    best_results = {}

    while iter_count < _niter:
        for m in medoids:
            clust_iter = 0
            for item in medoids[m]:
                if item != m:
                    idx = medoids_sample.index(m)
                    swap_temp = medoids_sample[idx]
                    medoids_sample[idx] = item
                    tmp_cost, tmp_medoids = compute_cost(_data, _fn, medoids_sample)
                    if (tmp_cost < current_cost) & (clust_iter < 1):
                        best_choices = list(medoids_sample)
                        best_results = dict(tmp_medoids)
                        current_cost = tmp_cost
                        clust_iter += 1
                    else:
                        best_choices = best_choices
                        best_results = best_results
                        current_cost = current_cost
                    medoids_sample[idx] = swap_temp

        iter_count += 1
        if best_choices == medoids_sample:
            break

        if current_cost <= prior_cost or prior_cost == -1:
            prior_cost = current_cost
            medoids = best_results
            medoids_sample = best_choices

    return size


def compute_cost(_data, _fn, _cur_choice):
        """
        :param _data: The input data frame.
        :param _fn: The distance function.
        :param _cur_choice: The current set of medoid choices.
        :param cache_on: Binary flag to turn caching.
        :return: The total configuration cost, the mediods.
        """
        size = len(_data)
        total_cost = 0.0
        medoids = {}
        for idx in _cur_choice:
            medoids[idx] = []

        for i in range(size):
            choice = -1
            min_cost = np.inf
            for m in medoids:

                tmp = _fn(_data[m], _data[i])

                if tmp < min_cost:
                    choice = m
                    min_cost = tmp

            medoids[choice].append(i)
            total_cost += min_cost

        return total_cost, medoids


def clara(_runs, _data, _k, _fn, _niter):
    """
    :param _runs: Clara algo runs
    :param _data: Input data frame.
    :param _k: Number of medoids.
    :param _fn: The distance function to use.
    :param _niter: number of k_medoid iters
    :return: The minimized cost, the best medoid choices and the final configuration.
    """
    size = len(_data)
    min_avg_cost = np.inf
    best_choices = []
    best_results = {}

    for j in range(_runs):
        sampling_idx = random.sample([i for i in range(size)], (40 + _k * 2))
        sampling_data = []
        for idx in sampling_idx:
            sampling_data.append(_data.iloc[idx])

        pre_cost, pre_choice, pre_medoids = k_medoids(sampling_data, _k, _fn, 1000)
        tmp_avg_cost, tmp_medoids = compute_cost(_data, _fn, pre_choice)
        tmp_avg_cost /= len(tmp_medoids)
        if tmp_avg_cost <= min_avg_cost:
            min_avg_cost = tmp_avg_cost
            best_choices = list(pre_choice)
            best_results = dict(tmp_medoids)

    return best_choices, best_results

