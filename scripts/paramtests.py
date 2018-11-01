#!/usr/bin/env python
"""Tools for setting up hyper-parameter testing experiments
with different values each iteration.
"""

import collections
import numpy as np

def create_params_generator(definitions, n_max=None):
    """Returns a generator that yields a dictionary of parameter
    values according to the definition dictionary provided.
    The definition dictionary should contain the names of all
    the parameters you want to include as keys.  The values in
    the dictionary have specific results depending on their type
    as explained below.

    Example:
    >>> import numpy as np
    >>> param_defs = {'alpha': 0.5, 'beta': [0.1, 0.2, 0.3],
    ...               'gamma': np.random.rand}
    >>> params_generator = create_params_generator(param_defs)
    >>> for params in params_generator:
    ...     print(params)
    ...
    {'alpha': 0.5, 'beta': 0.1, 'gamma': 0.8724450463937619}
    {'alpha': 0.5, 'beta': 0.2, 'gamma': 0.2802782437048025}
    {'alpha': 0.5, 'beta': 0.3, 'gamma': 0.4546550406703237}
    >>>

    The values in the definitions dict can include any of the
    following:

     1. Fixed values (e.g. float, int, string)
         Any value that is neither a function, an iterable or a string,
         will simply be replicated every time.

     2. Sequences of values of pre-determined length (e.g. lists,
         numpy arrays)
         Any sequenece (except strings) will be iterated over. After
         the last item has been generated, create_params_generator will
         raise a StopIteration exception (like any generator of finite
         length).

     3. Functions and generators
         If you supply a function or generator it will be called
         iteratively and the value that is returned/yielded will be
         used each iteration. These are useful for sampling from random
         probability distributions such as numpy.random.randn.
     """

    # First, turn any sequences to iterators
    for key, value in definitions.items():
        if isinstance(value, collections.Sequence) and not \
            isinstance(value, str):
            definitions[key] = iter(value)

    while n_max is not 0:
        params = {}

        try:
            for key, value in definitions.items():
                if callable(value):
                    params[key] = value()
                elif isinstance(value, str) or not hasattr(value, '__iter__'):
                    params[key] = value
                elif isinstance(value, collections.Iterable):
                    params[key] = next(value)
                else:
                    raise ValueError("Values of type %s not "
                                      "supported." % str(type(value)))
        except StopIteration:
            break

        n_max -= 1

        yield params


def random_uniform_exponential(low, high, log_base=10):
    """Returns a random number in the range [low, high]. The
    difference between this and numpy.random.uniform is that
    the scale of the range can be logarithmic. This is
    useful when parameters extend over multiple orders of
    magnitude

    Example:
    >>> rng = partial(random_uniform_exponential, 0.0001, 0.1)
    >>> [rng() for i in range(5)]
    [0.00113776004662613, 0.003284579871241146,
    0.00016667282302471582, 0.0630672448919357,
    0.04111194210999248]
    """

    assert high >= low > 0, "low, high must be positive for a log-scale."

    log_low, log_high = math.log(low, log_base), math.log(high, log_base)

    return log_base ** np.random.uniform(log_low, log_high)