# $Id: fitting.py,v 1.4 2011-04-05 19:20:01 wirawan Exp $
#
# wpylib.math.fitting module
# Created: 20100120
# Wirawan Purwanto
#
# Imported 20100120 from $PWQMC77/expt/Hybrid-proj/analyze-Eh.py
# (dated 20090323).
#
# fit_func_base was imported 20150520 from Cr2_analysis_cbs.py
# (dated 20141017, CVS rev 1.143).
#
# Some references on fitting:
# * http://stackoverflow.com/questions/529184/simple-multidimensional-curve-fitting
# * http://www.scipy.org/Cookbook/OptimizationDemo1 (not as thorough, but maybe useful)

"""
wpylib.math.fitting

Basic tools for two-dimensional curve fitting


ABOUT THE FITTING METHODS

We depend on module scipy.optimize and (optionally) lmfit to provide the
minimization routines for us.

The following methods are currently supported for scipy.optimize:

* `fmin`
  The Nelder-Mead Simplex algorithm.

* `fmin_bfgs` or `bfgs`
  The Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm

* `anneal`
  Similated annealing algorithm

* `leastsq`
  The Levenberg-Marquardt nonlinear least square (NLLS) method

See the documentation of `scipy.optimize` for more details.
The `fmin` algorithm is the slowest although it is fairly foor proof to
converge it (it may take many iterations).
The leastsq` algorithm is the best but it requires parameter guess that is
reasonable.
I don't have much success with `anneal`--it seems to behave erratically in
my limited experience. YMMV.


The lmfit package is supported if it can be found at runtime.
This package provides richer set of features, including constraints on
parameters and parameter interdependency.
Various minimization methods under this package are available.
To use lmfit, use keyword `lmfit:<method>` as the fit method name.
Example: `lmfit:leastsq`.
See the documentation here:

http://cars9.uchicago.edu/software/python/lmfit/fitting.html#fit-methods-label
"""

import numpy
import scipy.optimize
from wpylib.db.result_base import result_base

try:
  import lmfit
  HAS_LMFIT = True
except ImportError:
  HAS_LMFIT = False

last_fit_rslt = None
last_chi_sqr = None

class fit_result(result_base):
  """The basic values expected in fit_result are:
  - xopt
  - chi_square

  Optional values:
  - funcalls
  - xerr
  """
  pass

def fit_func(Funct, Data=None, Guess=None, Params=None,
             x=None, y=None,
             w=None, dy=None,
             debug=0,
             outfmt=1,
             Funct_hook=None,
             method='leastsq', opts={}):
  """
  Performs a function fitting.
  The domain of the function is a D-dimensional vector, and the function
  yields a scalar.

  Funct is a python function (or any callable object) with argument list of
  (C, x), where:
  * C is the cofficients (parameters) being adjusted by the fitting process
    (it is a sequence or a 1-D array)
  * x is a 2-D array (or sequence of like nature), say,
    of size "N rows times M columns".
    N is the dimensionality of the domain, while
    M is the number of data points, whose count must be equal to the
    size of y data below.
    For a 2-D curve (y = f(x)) fitting, for example,
    x should be a column array.

  An input guess for the parameters can be specified via Guess argument.
  It is an ordered list of scalar values for these parameters.

  The Params argument is reserved for lmfit-style fitting.
  It is ignored in other cases.

  The "y" array is a 1-D array of length M, which contain the "measured"
  value of the function at every domain point given in "x".

  The "w" or "dy" array (only one of them can be specified in a call),
  if given, specifies either the weight or standard error of the y data.
  If "dy" is specified, then "w" is defined to be (1.0 / dy**2), per usual
  convention.

  Inspect Poly_base, Poly_order2, and other similar function classes in the
  funcs_poly module to see the example of the Funct function.

  The measurement (input) datasets, against which the function is to be fitted,
  can be specified in one of two ways:
  * via x and y arguments. x is a multi-column dataset, where each row is the
    (multidimensional) coordinate of the Funct's domain.
    y is a one-dimensional dataset.
    Or,
  * via Data argument (which is a multi-column dataset, where the first row
    is the "y" argument).

  OUTPUT

  By default, only the fitted parameters are returned.
  To return as complete information as possible, use outfmt=0.
  The return value will be a struct-like object (class: fit_result).

  DEBUGGING

  Debugging and other investigations can be done with "Funct_hook", which,
  if defined, will be called every time right after "Funct" is called.
  It is called with the following signature:
    Funct_hook(C, x, y, f, r)
  where
    f := f(C,x)
    r := f(C,x) - y
  Note that the reference to the hook object is passed as the first argument
  to facilitate object oriented programming.


  SUPPORT FOR LMFIT MODULE

  This routine also supports the lmfit module.
  In this case, the Funct object must supply additional attributes:
  * param_names: an ordered list of parameter names.
    This is used in the case that Params argument is not defined.

  Input parameters can be specified ahead of time in the following ways:
  * If Params is None (default), then unconstrained minimization is done
    and the necessary Parameter objects are created on-the fly.
  * If Params is a Parameters object, then they are used.
    Note that these parameters *will* be clobbered!

  The input Guess parameter can be set to False, in which case Params *must*
  be defined and the initial values will be used as Guess.
  """
  global last_fit_rslt, last_chi_sqr
  from scipy.optimize import fmin, fmin_bfgs, leastsq, anneal
  # We want to minimize this error:
  if Data != None:
    # an alternative way to specifying x and y
    Data = numpy.asarray(Data)
    y = Data[0]
    x = Data[1:] # possibly multidimensional!
  else:
    x = numpy.asarray(x)
    y = numpy.asarray(y)

  if debug >= 1:
    print "fit_func: using function=%s, minimizer=%s" \
        % (repr(Funct), method)

  if debug >= 10:
    print "fit routine opts = ", opts
    print "Dimensionality of the domain is: ", len(x)

  if method.startswith("lmfit:"):
    if not HAS_LMFIT:
      raise ValueError, \
        "Module lmfit is not found, cannot use `%s' minimization method." \
        % (method,)
    use_lmfit = True
    from lmfit import minimize, Parameters, Parameter
    param_names = Funct.param_names
    if debug >= 10:
      print "param names: ", param_names
  else:
    use_lmfit = False

  if Guess != None:
    pass
  elif hasattr(Funct, "Guess_xy"):
    # Try to provide an initial guess
    Guess = Funct.Guess_xy(x, y)
  elif hasattr(Funct, "Guess"):
    # Try to provide an initial guess
    # This is an older version with y-only argument
    Guess = Funct.Guess(y)
  elif Guess == None:
    # VERY OLD, DO NOT USE ANYMORE! Will likely not work for anythingnonlinear
    # functions.
    Guess = [ y.mean() ] + [0.0, 0.0] * len(x)

  if use_lmfit:
    if Params == None:
      if debug >= 10:
        print "No input Params given; creating unconstrained params"
      # Creates a default list of Parameters for use later
      assert Guess != False
      Params = Parameters()
      for (g,pn) in zip(Guess, param_names):
        Params.add(pn, value=g)
    else:
      if debug >= 10:
        print "Input Params specified; use them"
      if Guess == None or Guess == False:
        # copy the Params' values to Guess
        Guess = [ Params[pn].value for pn in param_names ]
      else:
        # copy the Guess values onto the Params' values
        for (g,pn) in zip(Guess, param_names):
          Params[pn].value = g

    if debug >= 10:
      print "lmfit guess parameters:"
      for k1 in Params:
        print " - ", Params[k1]

  if debug >= 5:
    print "Guess params:"
    print "  ", Guess

  if Funct_hook != None:
    if not hasattr(Funct_hook, "__call__"):
      raise TypeError, "Funct_hook argument must be a callable function."
    def fun_err(CC, xx, yy, ww):
      """Computes the error of the fitted functional against the
      reference data points:

      * CC = current function parameters
      * xx = domain points of the ("measured") data
      * yy = target points of the ("measured") data
      * ww = weights of the ("measured") data (usually, 1/error**2 of the data)
      """
      ff = Funct(CC,xx)
      r = (ff - yy) * ww
      Funct_hook(CC, xx, yy, ff, r)
      return r
  elif debug < 20:
    def fun_err(CC, xx, yy, ww):
      ff = Funct(CC,xx)
      r = (ff - yy) * ww
      return r
  else:
    def fun_err(CC, xx, yy, ww):
      ff = Funct(CC,xx)
      r = (ff - yy) * ww
      print "  err: %s << %s << %s, %s, %s" % (r, ff, CC, xx, ww)
      return r

  fun_err2 = lambda CC, xx, yy, ww: numpy.sum(abs(fun_err(CC, xx, yy, ww))**2)

  if w != None and dy != None:
    raise TypeError, "Only one of w or dy can be specified."
  if dy != None:
    sqrtw = 1.0 / numpy.asarray(dy)
  elif w != None:
    sqrtw = numpy.sqrt(w)
  else:
    sqrtw = 1.0

  # Full result is stored in rec
  rec = fit_result()
  extra_keys = {}
  chi_sqr = None
  if method == 'leastsq':
    # modified Levenberg-Marquardt algorithm
    rslt = leastsq(fun_err,
                   x0=Guess, # initial coefficient guess
                   args=(x,y,sqrtw), # data onto which the function is fitted
                   full_output=1,
                   **opts
                   )
    keys = ('xopt', 'cov_x', 'infodict', 'mesg', 'ier') # ier = error message code from MINPACK
    extra_keys = {
      # map the output values to the same keyword as other methods below:
      'funcalls': (lambda : rslt[2]['nfev']),
    }
    # Added estimate of fit parameter uncertainty (matching GNUPLOT parameter
    # uncertainty.
    # The error is estimated to be the diagonal of cov_x, multiplied by the WSSR
    # (chi_square below) and divided by the number of fit degrees of freedom.
    # I used newer scipy.optimize.curve_fit() routine as my cheat sheet here.
    if outfmt == 0:
      if rslt[1] != None and len(y) > len(rslt[0]):
        NDF = len(y) - len(rslt[0])
        extra_keys['xerr'] = (lambda:
            numpy.sqrt(numpy.diagonal(rslt[1]) * rec['chi_square'] / NDF)
        )
  elif method == 'fmin':
    # Nelder-Mead Simplex algorithm
    rslt = fmin(fun_err2,
                x0=Guess, # initial coefficient guess
                args=(x,y,sqrtw), # data onto which the function is fitted
                full_output=1,
                **opts
               )
    keys = ('xopt', 'fopt', 'iter', 'funcalls', 'warnflag', 'allvecs')
  elif method == 'fmin_bfgs' or method == 'bfgs':
    # Broyden-Fletcher-Goldfarb-Shanno (BFGS) algorithm
    rslt = fmin_bfgs(fun_err2,
                     x0=Guess, # initial coefficient guess
                     args=(x,y,sqrtw), # data onto which the function is fitted
                     full_output=1,
                     **opts
                    )
    keys = ('xopt', 'fopt', 'funcalls', 'gradcalls', 'warnflag', 'allvecs')
  elif method == 'anneal':
    rslt = anneal(fun_err2,
                  x0=Guess, # initial coefficient guess
                  args=(x,y,sqrtw), # data onto which the function is fitted
                  full_output=1,
                  **opts
                 )
    keys = ('xopt', 'fopt', 'T', 'funcalls', 'iter', 'accept', 'retval')
  elif use_lmfit:
    submethod = method.split(":",1)[1]
    minrec = minimize(fun_err, Params,
                      args=(x,y,sqrtw),
                      method=submethod,
                      # backend ("real" minimizer) options:
                      full_output=1,
                      **opts
                     )
   
    xopt = [ Params[k1].value for k1 in param_names ]
    keys = ('xopt', 'minobj', 'params')
    rslt = [ xopt, minrec, Params ]
    # map the output values (in the Minimizer instance, minrec), to
    # the same keyword as other methods for backward compatiblity.
    rec['funcalls'] = minrec.nfev
    try:
      chi_sqr = minrec.chi_sqr
    except:
      pass
    # These seem to be particular to leastsq:
    try:
      rec['ier'] = minrec.ier
    except:
      pass
    try:
      rec['mesg'] = minrec.lmdif_message
    except:
      pass
    try:
      rec['message'] = minrec.message
    except:
      pass

    # Added estimate of fit parameter uncertainty (matching GNUPLOT parameter
    # uncertainty.
    # The error is estimated to be the diagonal of cov_x, multiplied by the WSSR
    # (chi_square below) and divided by the number of fit degrees of freedom.
    # I used newer scipy.optimize.curve_fit() routine as my cheat sheet here.
    if outfmt == 0:
      try:
        has_errorbars = minrec.errorbars
      except:
        has_errorbars = False

      if has_errorbars:
        try:
          rec['xerr'] = [ Params[k1].stderr for k1 in param_names ]
        except:
          # it shouldn't fail like this!
          import warnings
          warnings.warn("wpylib.math.fitting.fit_func: Fail to get standard error of the fit parameters")

      if debug >= 10:
        if 'xerr' in rec:
          print "param errorbars are found:"
          print "  ", tuple(rec['xerr'])
        else:
          print "param errorbars are NOT found!"

  else:
    raise ValueError, "Unsupported minimization method: %s" % method

  # Final common post-processing:
  if chi_sqr == None:
    chi_sqr = fun_err2(rslt[0], x, y, sqrtw)
  last_chi_sqr = chi_sqr
  last_fit_rslt = rslt
  if (debug >= 10):
    #print "Fit-message: ", rslt[]
    print "Fit-result:"
    print "\n".join([ "%2d  %s" % (ii, rslt[ii]) for ii in xrange(len(rslt)) ])
  if debug >= 1:
    print "params = ", rslt[0]
    print "chi square = ", last_chi_sqr / len(y)
  if outfmt == 0: # outfmt == 0 -- full result.
    rec.update(dict(zip(keys, rslt)))
    rec['chi_square'] = chi_sqr
    rec['fit_method'] = method
    # If there are extra keys, record them here:
    for (k,v) in extra_keys.iteritems():
      rec[k] = v()
    return rec
  elif outfmt == 1:
    return rslt[0]
  else:
    try:
      x = str(outfmt)
    except:
      x = "(?)"
    raise ValueError, "Invalid `outfmt' argument = " + x



# Imported 20150520 from Cr2_analysis_cbs.py .
class fit_func_base(object):
  """Base class for function 2-D fitting object.
  This is an enhanced OO interface to fit_func.

  In the derived class, a __call__ method must be implemented with
  this prototype:

      def __call__(self, C, x)

  where
  - `C' is the parameters which we sought through the fitting
    procedure, and
  - `x' is the x values of the data samples against which we want
    to do the curve fitting.

  A few user-adjustable parameters need to be attached as attributes
  to this object:

  - fit_method
  - fit_opts (a dict or multi_fit_opts object)
  - debug
  - dbg_params
  - Params

  `fit_method' is a string containing the name of the fitting method to use,
  see this module document.

  Additional attributes are required to support lmfit-based fitting:

  - param_names: a list/tuple of parameter names, in the same order as in
    the legacy 'C' __call__ argument above.

  The input-data-based automatic parameter guess is specified via Guess parameter.
  See wpylib.math.fitting.fit_func for detail.

  - if Guess==None (default), then it attempts to use self.Guess_xy() method
    (better, new default) or old self.Guess() method.
  - if Guess==False (only for lmfit case), existing values from Params object
    will be used.
  - TODO: dict-like Guess should be made possible.
  - otherwise, the guess values will be used as the initial values.

  Refer to various function objects in wpylib.math.fitting.funcs_simple
  for actual examples of how to use and create your own fit_func_base object.
  """
  class multi_fit_opts(dict):
    """A class for defining default control parameters for different fit methods.
    The fit method name is the dict key, and the value, which is also a dict,
    is the default set of fitting control parameters for that particular fit method.
    """
    pass
  # Some reasonable parameters are set:
  fit_default_opts = multi_fit_opts(
    fmin=dict(xtol=1e-5, maxfun=100000, maxiter=10000, disp=0),
    fmin_bfgs=dict(gtol=1e-6, disp=0),
    leastsq=dict(xtol=1e-8, epsfcn=1e-6),
  )
  fit_default_opts["lmfit:leastsq"] = dict(xtol=1e-8, epsfcn=1e-6)
  debug = 1
  dbg_params = 1
  fit_method = 'fmin'
  fit_opts = fit_default_opts
  #fit_opts = dict(xtol=1e-5, maxfun=100000, maxiter=10000, disp=0)
  def fit(self, x, y, dy=None, fit_opts=None, Funct_hook=None, Guess=None):
    """Main entry function for fitting."""
    x = numpy.asarray(x)
    if len(x.shape) == 1:
      # fix common "mistake" for 1-D domain: make it 2-D
      x = x.reshape((1, x.shape[0]))
    if fit_opts == None:
      # Use class default if it is available
      fit_opts = getattr(self, "fit_opts", {})
    if isinstance(fit_opts, self.multi_fit_opts):  # multiple choice :-)
      fit_opts = fit_opts.get(self.fit_method, {})
    if Guess == None:
      Guess = getattr(self, "Guess", None)
    if self.dbg_params:
      self.dbg_params_log = []
    if self.debug >= 5:
      print "fit: Input Params = ", getattr(self, "Params", None)
    self.last_fit = fit_func(
                      Funct=self,
                      Funct_hook=Funct_hook,
                      x=x, y=y, dy=dy,
                      Guess=Guess,
                      Params=getattr(self, "Params", None),
                      method=self.fit_method,
                      opts=fit_opts,
                      debug=self.debug,
                      outfmt=0, # yield full result
                    )
    if self.use_lmfit_method:
      if not hasattr(self, "Params"):
        self.Params = self.last_fit.params
    return self.last_fit['xopt']

  def func_call_hook(self, C, x, y):
    """Common hook function called when calling 'THE'
    function, e.g. for debugging purposes."""
    from copy import copy
    if self.dbg_params:
      if not hasattr(self, "dbg_params_log"):
        self.dbg_params_log = []
      self.dbg_params_log.append(copy(C))
    #print "Call morse2_fit_func(%s, %s) -> %s" % (C, x, y)

  def get_params(self, C, *names):
    """Special support function to extract the values (or
    representative objects) of the parameters contained in 'C',
    the list of parameters.

    In the legacy case, C is simply a tuple/list of numbers.

    In the lmfit case, C is a Parameters object.
    """
    try:
      from lmfit import Parameters
      # new way: using lmfit.Parameters:
      if isinstance(C, Parameters):
        return tuple(C[k].value for k in names)
    except:
      pass

    # old way: using positional parameters
    return tuple(C)

  @property
  def use_lmfit_method(self):
    return self.fit_method.startswith("lmfit:")

  @staticmethod
  def domain_array(x):
    """Creates a domain array (x) for nonlinear fitting.
    Also accomodates a common "mistake" for 1-D domain by making it
    correctly 2-D in shape.
    """
    x = numpy.asarray(x)
    if len(x.shape) == 1:
      # fix common "mistake" for 1-D domain: make it 2-D
      x = x.reshape((1, x.shape[0]))
    return x


