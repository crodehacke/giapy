"""
giamc.py

    Methods and classes to support MCMC calculations using the emcee module.

    Author: Samuel B. Kachuck
"""

import numpy as np
import time
import sys

def uniform_lnprior(params, lower, upper):
    """For boxcar (uniform) prior in range, return 0 in range, -np.inf outside.

    Parameters
    ----------
    params : float or np.ndarray
        The parameter (or list of parameters) drawn from a uniform probability.
    lower  : float or np.ndarray
    upper  : float or np.ndarray
        The lower and upper bounds of the parameter(s). Must have same shape as
        params.
    """
    assert np.asarray(params).shape == np.asarray(upper).shape ==\
        np.asarray(lower).shape, 'Input shapes incompatible.' 

    if np.all(np.logical_and( lower < params, params < upper)): 
        return 0.0
    return -np.inf

def sampleOut(sampler, pos, lnprob0, blobs0, fname, nsteps, blobs=False, verbose=False):
    """Iteratively sample and store from an emcee Sampler starting at pos.

    If the output file exists, the results are appended. If not, it is created.

    Parameters
    ----------
    sampler : <emcee.EnsembleSampler>
        An instance of the emcee EnsemleSampler class.
    pos : np.ndarray
        The starting position og the sampler. Must have a shape 
        (nwalkers, ndim).
    fname : str
        The name of the output file to write to.
    nsteps : int
        The number of steps to take in this sampling.
    blobs: bool
        If the sampler also returns predictive blobs to store (default False).
    verbose : bool
        If terminal feedback on calculation is desired (default False).
    """
    # Check if the file exists and, if not,
    try:
        f = open(fname, 'r')
        f.close()
    # create it.
    except IOError:
        f = open(fname, 'w')
        f.close()

    if verbose: 
        tstart = time.time()
        outmsg = 'Taking step {0:d}/{1:d}\033[K\r'
        donemessage = ''

    for i, step in enumerate(sampler.sample(pos, lnprob0=lnprob0, blobs0=blobs0, 
                                iterations=nsteps, storechain=False), start=2):
        if verbose:
            sys.stdout.write(outmsg.format(i, nsteps))
            sys.stdout.flush()
        # For each step we create an output dump.
        output = ''
        # Iterate over the walkers.
        for k in range(step[0].shape[0]):

            #f.write('{0:4d}\t{1:.5e}\t{2:s}\t{3:s}\n'
            #.format(k, step[1][k], '\t'.join(step[0][k]),
            #                       '\t'.join(step[3][k]))
            # Write the logProbability.
            output += '{0:d}\t{1:e}\t'.format(k, step[1][k])
            # Write out all parameters.
            for param in step[0][k]:
                output += '{0:f}\t'.format(param)
            # Write out the blobs, if asked to.
            if blobs:
                for blob in step[3][k]:
                    output += '{0}\t'.format(blob)
            # End the line.
            output += '\n'
        # Dump the output.
        with open(fname, 'a') as f:
            f.write(output)

    if verbose:
        ttotal = time.time() - tstart
        if ttotal > 3600:
            ttotal = ttotal / 3600
            unit = 'hrs'
        elif ttotal > 60:
            ttotal = ttotal / 60
            unit = 'min'
        else:
            unit = 's'
        avgaccept = np.mean(sampler.naccepted)/nsteps
        donemessage += '{0:3d} steps in {1:.3f} {2}, with {3:.3f} accepted.\033[K\n'
        sys.stdout.write(donemessage.format(nsteps, ttotal, unit, avgaccept))
