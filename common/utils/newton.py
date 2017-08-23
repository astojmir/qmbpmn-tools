""" Newton's method function. """
import numpy as np

def rootfind_newton(func, x0, a, b, maxiter=50, tol=1.0e-11):
    """ Find root using bracketed Newton's method """

    for iter in xrange(maxiter):

        fval, fpval, args = func(x0)
        # print "x0=%.4f fval=%.2e fpval=%.2e [%.4f, %.4f]" % (x0, fval, fpval, a, b)

        if fval < 0:
            a = x0
        else:
            b = x0

        x = x0 - fval/fpval
        if not (a < x < b):
            # Once we have bracketed the root, we don't allow the
            # iterations to leave the bracket.
            x = 0.5*(a+b)

        if np.abs(x-x0) < tol or np.abs(fval) < tol:
            break

        x0 = x

    return x, fval, iter, args
