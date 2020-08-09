"""Module for calculating random or non-random delay
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from math import ceil, log, sqrt
from numpy import arange
from random import uniform
import sys
from typing import Dict, Union, List
from time import time
from logging import warning, Logger

from scipy.special import expit

from jobfunnel.resources import DelayAlgorithm
from jobfunnel.config import DelayConfig
from jobfunnel.backend import Job


def _c_delay(list_len: int, delay: Union[int, float]):
    """Sets single delay value to whole list.
    """
    delays = [delay] * list_len
    # sets incrementing offsets to the first 8 elements
    inc = .2  # Increment set to .2
    offset = len(delays[0:8]) / 5  # offset
    # checks if delay is < 1.5
    if delay < 1.5:
        # changes increment and offset, to prevent 0s and negative nums
        inc = delay / 8
        offset = float(len(delays[0:8])) * inc
    # division here is faster since they are both ints
    delays[0:8] = [(x - offset) + i * inc for i, x in enumerate(delays[0:8])]
    return delays


def _lin_delay(list_len: int, delay: Union[int, float]):
    """Calculates y=.2*x and sets y=delay at intersection of x between lines.
    """
    # calculates x value where lines intersect
    its = 5 * delay  # its = intersection
    # any delay of .2 or less is hard delay
    if its <= 1:
        return _c_delay(list_len, delay)
    else:
        # prevents slicing from breaking if delay is a float
        if isinstance(its, float):
            its = int(ceil(its))
        # create list of x values based on scrape list size
        delays = [*range(list_len)]
        delays[0:its] = [x / 5 for x in delays[0:its]]
        delays[its:] = [delay] * (len(delays) - its)
        return delays


# https://en.wikipedia.org/wiki/Generalised_logistic_function
def _sig_delay(list_len: int, delay: Union[int, float]):
    """Calculates Richards/Sigmoid curve for delay.
    """
    gr = sqrt(delay) * 4  # growth rate
    y_0 = log(4 * delay)  # Y(0)
    # calculates sigmoid curve using vars rewritten to be our x
    delays = delay * expit(arange(list_len) / gr - y_0)
    return delays.tolist()  # convert np array back to list


def calculate_delays(list_len: int, delay_config: DelayConfig) -> List[float]:
    """Checks delay config and returns calculated delay list.

    NOTE: we do this to be respectful to online job sources
    TODO: make this return a delay value based on list_len so we can use this
    on-demand with the thread executor's GET queue.

    Args:
        list_len: length of scrape job list
        delay_config: Delay configuration dictionary

    Returns:
        list of delay time matching length of scrape job list
    """
    delay_config.validate()

    # Delay calculations using specified equations
    if delay_config.algorithm == DelayAlgorithm.CONSTANT:
        delay_vals = _c_delay(list_len, delay_config.max_duration)
    elif delay_config.algorithm == DelayAlgorithm.LINEAR:
        delay_vals = _lin_delay(list_len, delay_config.max_duration)
    elif delay_config.algorithm == DelayAlgorithm.SIGMOID:
        delay_vals = _sig_delay(list_len, delay_config.max_duration)
    else:
        raise ValueError(f"Cannot calculate delay for {delay_config.algorithm}")

    # Check if minimum delay is above 0 and less than last element
    if 0 < delay_config.min_duration:
        # sets min_duration to values greater than itself in delay_vals
        for i, n in enumerate(delay_vals):
            if n > delay_config.min_duration:
                break
            delay_vals[i] = delay_config.min_duration

    # Outputs final list of delays rounded up to 3 decimal places
    if delay_config.random:  # check if random delay was specified
        # random.uniform(a, b) a = lower bound, b = upper bound
        if delay_config.converge:  # checks if converging delay is True
            # delay_vals = lower bound, delay = upper bound
            durations = [
                round(uniform(x, delay_config.max_duration), 3)
                for x in delay_vals
            ]
        else:
            # lb = lower bounds, delay_vals = upper bound
            durations = [
                round(uniform(delay_config.min_delay, x), 3) for x in delay_vals
            ]

    else:
        durations = [round(i, 3) for i in delay_vals]

    # Always set first element to 0 so scrape starts right away
    durations[0] = 0

    return durations


def delay_threader(jobs_list: List[Job], scrape_fn: object,
                   parse_fn: object, threads: ThreadPoolExecutor,
                   logger: Logger, delays: List[float] = None) -> None:
    """Method to scrape descriptions from individual indeed postings.
    with respectful-delaying
    """

    # Submits jobs and stores futures in dict
    start = time()
    results = {}
    for job, delay in zip(jobs_list, delays):
        results[threads.submit(scrape_fn, job=job, delay=delay)] = job.key_id

    # Loops through futures as completed and removes each if successfully parsed
    while results:
        for future in as_completed(results):
            job, html = future.result()
            parse_fn(job, html)
            del results[future]
            del html

    # Cleanup + log
    threads.shutdown()
    end = time()
    logger.info(f'Scrape delay took {(end - start):.3f}s')