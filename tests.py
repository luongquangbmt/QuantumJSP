from __future__ import print_function

import matplotlib.pyplot as plt
import time
import neal
import numpy as np

from dwave.system.composites import EmbeddingComposite
from dwave.system.samplers import DWaveSampler

from job_shop_scheduler import get_jss_bqm

from instance_parser import readInstance, transformToMachineDict, find_time_window, solve_greedily

from collections import defaultdict

from pprint import pprint

from statistics import median


def printResults(sampleset, jobs):
    solution_dict = defaultdict(int)

    for sample, occurrences in sampleset.data(
        ["sample", "num_occurrences"]
    ):
        selected_nodes = [k for k, v in sample.items() if v ==
                          1 and not k.startswith('aux')]

        # Parse node information
        task_times = {k: [-1] * len(v) for k, v in jobs.items()}
        for node in selected_nodes:
            job_name, task_time = node.rsplit("_", 1)
            task_index, start_time = map(int, task_time.split(","))
            task_times[job_name][task_index] = start_time

        result = 0
        for job, times in task_times.items():
            if -1 in times:
                solution_dict["error"] += occurrences
                break
            result = max(result, times[-1] + jobs[job][-1][1])
        else:
            solution_dict[result] += occurrences

    best_solution = sampleset.first.sample
    selected_nodes = [k for k, v in best_solution.items() if v ==
                      1 and not k.startswith('aux')]

    # Parse node information
    task_times = {k: [-1] * len(v) for k, v in jobs.items()}
    for node in selected_nodes:
        job_name, task_time = node.rsplit("_", 1)
        task_index, start_time = map(int, task_time.split(","))

        task_times[job_name][task_index] = start_time
        # for job, times in task_times.items():
        #     print("{0:9}: {1}".format(job, times))

    return solution_dict


def num_of_errors_in_times(qpu=False):
    jobs = {"1": [(0, 2), (1, 1), (0, 1)],
            "2": [(1, 1), (0, 1), (2, 2)],
            "3": [(2, 1), (2, 1), (1, 1)]}

    times = range(4, 12)
    errors = defaultdict(list)
    for time in times:
        for i in range(12):
            try:
                bqm = get_jss_bqm(jobs, time, stitch_kwargs={
                    'min_classical_gap': 2.0})
                if qpu:
                    sampler = EmbeddingComposite(
                        DWaveSampler(solver={'qpu': True}))
                    sampleset = sampler.sample(
                        bqm, chain_strength=2, num_reads=1000)
                else:
                    sampler = neal.SimulatedAnnealingSampler()
                    sampleset = sampler.sample(bqm, num_reads=1000)
                sol_dict = printResults(sampleset, jobs)
                errors[time].append(sol_dict['error'])
            except:
                print(f"error: {time}")
                continue
    medians = []
    margins = []
    for key, values in errors.items():
        values.sort()
        values = values[1:-1]
        medians.append(median(values))
        margins.append([abs(values[0] - median(values)),
                        abs(values[-1] - median(values))])
    plt.errorbar(errors.keys(), medians, yerr=np.array(
        margins).T, fmt='ko', color='b')
    plt.xlabel('max_time value')
    plt.ylabel('number of error solutions provided (out of 1000)')
    # plt.show()
    plt.savefig('times.png')
    print(errors)


def num_of_errors_in_chain_strengths(qpu=False):
    jobs = {"1": [(0, 2), (1, 1), (0, 1), (3, 2)],
            "2": [(1, 1), (0, 1), (2, 2), (2, 2)],
            "3": [(2, 1), (2, 1), (1, 1), (1, 3)]}

    strengths = (0.5, 1, 1.25, 1.5, 1.6, 1.7, 1.8, 1.9,
                 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 3.0, 3.5, 4.0)
    errors = defaultdict(list)
    for strength in strengths:
        for i in range(12):
            try:
                bqm = get_jss_bqm(jobs, 8, stitch_kwargs={
                    'min_classical_gap': 2.0})
                if qpu:
                    sampler = EmbeddingComposite(
                        DWaveSampler(solver={'qpu': True}))
                    sampleset = sampler.sample(
                        bqm, chain_strength=strength, num_reads=1000)
                else:
                    sampler = neal.SimulatedAnnealingSampler()
                    sampleset = sampler.sample(bqm, num_reads=1000)
                sol_dict = printResults(sampleset, jobs)
                errors[strength].append(sol_dict['error'])
            except:
                print(f"error: {strength}")
                continue
    medians = []
    margins = []
    for key, values in errors.items():
        values.sort()
        values = values[1:-1]
        medians.append(median(values))
        margins.append([abs(values[0] - median(values)),
                        abs(values[-1] - median(values))])
    plt.errorbar(errors.keys(), medians, yerr=np.array(
        margins).T, fmt='ko', color='b')
    plt.xlabel('chain strength')
    plt.ylabel('number of error solutions provided (out of 1000)')
    # plt.show()
    plt.savefig('chain_strength.png')
    print(errors)


def num_of_errors_in_length(qpu=False):
    jobs3 = {"1": [(0, 2), (1, 1), (0, 1)],
             "2": [(1, 1), (0, 1), (2, 2)],
             "3": [(2, 1), (2, 1), (1, 1)]}
    jobs4 = {"1": [(0, 2), (1, 1), (0, 1)],
             "2": [(1, 1), (0, 1), (2, 2)],
             "3": [(2, 1), (2, 1), (1, 1)]}
    jobs5 = {"1": [(0, 2), (1, 1), (0, 1)],
             "2": [(1, 1), (0, 1), (2, 2)],
             "3": [(2, 1), (2, 1), (1, 1)]}
    jobs6 = {"1": [(0, 2), (1, 1), (0, 1)],
             "2": [(1, 1), (0, 1), (2, 2)],
             "3": [(2, 1), (2, 1), (1, 1)]}
    jobs7 = {"1": [(0, 2), (1, 1), (0, 1)],
             "2": [(1, 1), (0, 1), (2, 2)],
             "3": [(2, 1), (2, 1), (1, 1)]}


if __name__ == "__main__":
    # num_of_errors_in_times(qpu=False)
    num_of_errors_in_chain_strengths(qpu=False)
