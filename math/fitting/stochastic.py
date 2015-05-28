#
# wpylib.math.fitting.stochastic module
# Created: 20150528
# Wirawan Purwanto
#
# Dependencies:
# - numpy
# - scipy
# - matplotlib (for visualization routines)
#

"""
wpylib.math.fitting.stochastic module

Tools for stochastic curve fitting.
"""

from wpylib.math.fitting import fit_func_base


class StochasticFitting(object):
  """Standard stochastic fit procedure.

  """
  debug = 0
  dbg_guess_params = True
  def_opt_report_final_params = 3
  def __init__(self):
    self.use_nlf_guess = 1
    self.use_dy_weights = True

  def init_func(self, func):
    self.func = func

  def init_samples(self, x, y, dy):
    """
    Initializes the sample data against which we will perform
    the stochastic fitting.
    This function takes N measurement samples:
    - the (multidimensional) domain points, x
    - the measured target points, y
    - the uncertainty of the target points, dy

    """
    x = fit_func_base.domain_array(x)
    if not (len(x[0]) == len(y) == len(dy)):
      raise TypeError, "Length of x, y, dy arrays are not identical."

    # fix (or, actually, provide an accomodation for) a common "mistake"
    # for 1-D domain: make it standard by adding the "first" dimension
    if len(x.shape) == 1:
      x = x.reshape((1, x.shape[0]))

    self.samples_x = x
    self.samples_y = numpy.array(y)
    self.samples_dy = numpy.array(dy)
    self.samples_wt = (self.samples_dy)**(-2)

  def init_rng(self, seed=None, rng_class=numpy.random.RandomState):
    """Initializes a standard random number generator for use in
    the fitting routine."""
    if seed == None:
      seed = numpy.random.randint(numpy.iinfo(int).max)
      print "Using random seed: ", seed
    self.rng_seed = seed
    self.rng = rng_class(seed)

  def num_fit_params(self):
    """An ad-hoc way to determine the number of fitting parameters.

    FIXME: There is still not an a priori way to find the number of
    fit parameters in the fit_func_base class or its derivatives.

    There are a few after-the-fact ways to determine this:

    1) Once the "deterministic" nonlinear fit is done, you can find the
       number of parameters by

         len(self.log_nlf_params)

    2) Once the stochastic fit is done, you can also find the number
       of fit parameters by
  
         len(self.log_mc_params[0])
    """
    try:
      return len(self.log_nlf_params)
    except:
      pass
    try:
      return len(self.log_mc_params[0])
    except:
      pass
    raise RuntimeError, "Cannot determine the number of fit parameters."

  def nlfit1(self):
    """Performs the non-stochastic, standard nonlinear fit."""
    from numpy.linalg import norm

    if self.use_dy_weights:
      dy = self.samples_dy
    else:
      dy = None
    rslt = self.func.fit(self.samples_x, self.samples_y, dy=dy)
    self.log_nlf_params = rslt
    self.nlf_f = self.func(self.log_nlf_params, self.samples_x)

    last_fit = self.func.last_fit
    mval_resid = self.nlf_f - self.samples_y
    self.nlf_ussr = norm(mval_resid)**2
    self.nlf_wssr = norm(mval_resid / self.samples_dy)**2
    self.nlf_funcalls = last_fit['funcalls']
    self.nlf_rec = last_fit

  def mcfit_step1_toss_dice_(self):
    """Generates a single Monte Carlo dataset for the mcfit_step1_
    procedure."""
    self.dice_dy = self.rng.normal(size=len(self.samples_dy))
    self.dice_y = self.samples_y + self.samples_dy * self.dice_dy

  def mcfit_step1_(self):
    """Performs a single Monte Carlo data fit."""
    # Var name conventions:
    # - dice_* = values related to one "dice toss" of the sample
    # - mval_* = values related to the mean value of the samples
    #            (i.e. samples_y)
    # FIXME: In future this *could* be run in parallel but the state vars
    # (such as dice_y, dice_dy, etc.) must be stored on per-thread basis.
    from numpy.linalg import norm
    self.mcfit_step1_toss_dice_()
    if self.use_dy_weights:
      dy = self.samples_dy
    else:
      dy = None
    rslt = self.func.fit(self.samples_x, self.dice_y, dy=dy,
                         Guess=self.dice_param_guess,
                        )
    # fit result of the stochastic data
    self.dice_params = rslt
    self.log_mc_params.append(rslt)
    self.dice_f = self.func(self.dice_params, self.samples_x)

    if self.dbg_guess_params:
      self.log_guess_params.append(self.func.guess_params)

    last_fit = self.func.last_fit
    dice_resid = self.dice_f - self.dice_y
    mval_resid = self.dice_f - self.samples_y
    dice_ussr = norm(dice_resid)**2
    dice_wssr = norm(dice_resid / self.samples_dy)**2
    mval_ussr = norm(mval_resid)**2
    mval_wssr = norm(mval_resid / self.samples_dy)**2
    self.log_mc_stats.append((dice_ussr, dice_wssr, mval_ussr, mval_wssr))
    self.log_mc_funcalls.append(last_fit['funcalls'])

  def mcfit_step1_viz_(self, save=True):
    """Generates a visual representation of the last MC fit step.
    """
    from matplotlib import pyplot
    if not hasattr(self, "fig"):
      self.fig = pyplot.figure()
    self.fig.clf()
    ax = self.fig.add_subplot(1, 1, 1)
    title = "MC fit step %d" % self.mcfit_iter_num
    ax.set_title(title)
    x,y,dy = self.samples_x[0], self.samples_y, self.samples_dy
    ax.errorbar(x=x, y=y, yerr=dy,
                fmt="x", color="SlateGray", label="QMC",
               )
    samples_xmin = x.min()
    samples_xmax = x.max()
    samples_xrange = samples_xmax - samples_xmin
    samples_ymin = y.min()
    samples_ymax = y.max()
    samples_yrange = samples_ymax - samples_ymin
    len_plot_x = 10*len(y)
    plot_x = numpy.linspace(start=samples_xmin - 0.03 * samples_xrange,
                            stop=samples_xmax + 0.03 * samples_xrange,
                            num=len_plot_x,
                            endpoint=True)
    ax.plot(plot_x, self.func(self.nlf_rec.xopt, [plot_x]), "-",
            color="SlateGray", label="nlfit")
    ax.errorbar(x=x, y=self.dice_y, yerr=dy,
                fmt="or", label="MC toss",
               )
    ax.plot(plot_x, self.func(self.dice_params, [plot_x]), "-",
            color="salmon", label="MC fit")

    samples_dy_max = numpy.max(self.samples_dy)
    ax.set_ylim((samples_ymin - samples_dy_max * 8, samples_ymax + samples_dy_max * 8))
    if save:
      self.fig.savefig("mcfit-%04d.png" % self.mcfit_iter_num)

  def mcfit_loop_begin_(self):
    """Performs final initialization before firing up mcfit_loop_.
    This need to be done only before the first mcfit_loop_() call;
    if more samples are collected later, then this routine should NOT be
    called again or else all the accumulators would reset."""
    self.log_guess_params = []
    self.log_mc_params = []
    self.log_mc_stats = []
    self.log_mc_funcalls = []
    if self.use_nlf_guess:
      print "Using guess param from NLF: ",
      self.nlfit1()
      self.dice_param_guess = self.log_nlf_params
      #print "- Params = ", self.log_nlf_params
      print self.log_nlf_params
    else:
      self.dice_param_guess = None

  def mcfit_loop_end_(self):
    """Performs final initialization before firing up do_mc_fitting:
    - Repackage log_mc_stats and log_mc_params as numpy array of structs
    """
    # Number of fit parameters:
    num_params = len(self.log_mc_params[0])
    #if True:
    try:
      pnames = self.func.param_names
      assert len(pnames) == num_params # Otherwise it will be faulty
      if self.func.use_lmfit_method:
        #from lmfit import Parameter
        ptype = float
      else:
        ptype = float
      param_dtype = [ (i, ptype) for i in pnames ]
    except:
      param_dtype = [ ("C"+str(i), float) for i in xrange(num_params) ]
    stats_dtype = [ (i, float) for i in ('dice_ussr', 'dice_wssr', 'mval_ussr', 'mval_wssr') ]

    # Can't initialize the self.mc_params array in a single step with
    # numpy.array construction function; we must copy the records one by one.
    # The reason is this: each element of the log_mc_params list is already
    # a numpy ndarray object.
    self.mc_params = numpy.empty((len(self.log_mc_params),), dtype=param_dtype)
    for (i,p) in enumerate(self.log_mc_params):
      if self.func.use_lmfit_method:
        self.mc_params[i] = tuple(p)
      else:
        self.mc_params[i] = p
    self.mc_stats = numpy.array(self.log_mc_stats, dtype=stats_dtype)
    self.fit_parameters = [ p[0] for p in param_dtype ]

  def mcfit_analysis_(self):
    """Performs analysis of the Monte Carlo fitting.
    This version does no weighting or filtering based on some cutoff criteria.
    """
    flds = self.fit_parameters # == self.mc_params.dtype.names
    rslt = {}
    for F in flds:
      mean = numpy.average(self.mc_params[F])
      err = numpy.std(self.mc_params[F])
      rslt[F] = errorbar(mean, err)
    self.final_mc_params = rslt

  def mcfit_loop1_(self, num_iter, save_fig=0):
    """Performs the Monte-Carlo fit simulation after the
    input parameters are set up."""

    for i in xrange(num_iter):
      self.mcfit_iter_num = i
      if self.debug >= 2:
        print "mcfit_loop1_: iteration %d" % i
      self.mcfit_step1_()
      if save_fig:
        self.mcfit_step1_viz_(save=True)

  def mcfit_report_final_params(self, format=None):
    if format == None:
      format = getattr(self, "opt_report_final_params", self.def_opt_report_final_params)
    if format in (None, False, 0):
      return # quiet!

    parm = self.final_mc_params
    if format == 3:
      print "Final parameters          :",
      print "  ".join([
        "%s" % (parm[k],) for k in self.fit_parameters
      ])
    elif format == 2:
      print "Final parameters:"
      print "\n".join([
        "  %s = %s" % (k, parm[k])
          for k in self.fit_parameters
      ])
    elif format == 1:
      print "Final parameters:"
      print parm

  def mcfit_run1(self, x=None, y=None, dy=None, data=None, func=None, rng_params=None,
                 num_iter=100, save_fig=False):
    """The main routine to perform stochastic fit."""
    if data != None:
      raise NotImplementedError
    elif dy != None:
      # Assume OK
      pass
    elif y != None and dy == None:
      y_orig = y
      y = errorbar_mean(y_orig)
      dy = errorbar_err(y_orig)
    else:
      raise TypeError, "Invalid argument combination for the input data."

    if func != None:
      self.init_func(func)
    if not hasattr(self, "func"):
      raise RuntimeError, \
        "The fit function in the fitting object is undefined."
    self.init_samples(x=x,
                      y=y,
                      dy=dy,
                    )
    if rng_params != None:
      self.init_rng(**rng_params)
    elif not hasattr(self, "rng"):
      self.init_rng()

    self.mcfit_loop_begin_()
    self.mcfit_loop1_(num_iter=num_iter, save_fig=save_fig)
    self.mcfit_loop_end_()
    self.mcfit_analysis_()
    self.mcfit_report_final_params()
    return self.final_mc_params

  # The two routines below gives convenient way to evaluate the
  # fitted curve at arbitrary x values (good so long as they are not
  # far out from the range given by self.samples_x)

  def mcfit_eval_raw(self, x=None, yscale=1.0):
    """Evaluates the curve (y) values for a given set of x value(s).
    This routine generates the raw values based on the stochastically
    sampled parameter values."""
    if x == None:
      x = self.samples_x
    else:
      x = fit_func_base.domain_array(x)

    xlen = len(x[0])
    mc_curve_y = numpy.empty((len(self.mc_params), xlen))
    # The following loop could have been written as a batch operation,
    # but it requires some nontrivial change in the convention of how
    # fit_func_base.__call__() is written.
    # Double broadcasting and other dimensional retrofitting/reduction
    # ('dot product'?) may be required.
    # Example: in harm_fit_func class, the statement
    #     xdisp = (x[0] - C[2])
    # will have to be changed becasuse the length of x[0]
    # (which is the number of data points in the "x" argument)
    # and the length of C[2]
    # (which is the number of MC iterations)
    # will not match--and these numbers must NOT be subtracted elementwise!
    for (i,ppp) in enumerate(self.mc_params):
      mc_curve_y[i] = self.func(ppp, x)

    return mc_curve_y

  def mcfit_eval(self, x=None, yscale=1.0, ddof=1, outfmt=0):
    """Evaluates the curve (y) values for a given set of x value(s).
    This routine generates the finalized values (with errorbar estimate)
    based on the stochastically sampled parameter values."""

    # WARNING: CONVENTION CHANGES FROM ORIGINAL make_curve_errorbar() ROUTINE!
    # The default delta degree of freedom (ddof) should be 1 because we need
    # to take one out for the average itself.
    # If you need to reproduce old result, can revert to ddof=0.
    if x == None:
      x = self.samples_x
    else:
      x = fit_func_base.domain_array(x)
    mc_curve_y = self.mcfit_eval_raw(x=x)

    xlen = len(x[0])
    final_mc_curve = numpy.empty((xlen,), dtype=[('val',float),('err',float)])
    final_mc_curve['val'] = numpy.average(mc_curve_y, axis=0)
    final_mc_curve['err'] = numpy.std(mc_curve_y, axis=0, ddof=ddof)
    if yscale != 1.0:
      final_mc_curve['val'] *= yscale
      final_mc_curve['err'] *= yscale
    if outfmt == 0:
      pass # already in that format
    elif outfmt == 1:
      # Formatted as an array of "errorbar" objects
      final_mc_curve = numpy.array([errorbar(y,dy) for (y,dy) in final_mc_curve], dtype=errorbar)
    else:
      raise ValueError, "Unsupported outfmt value=%s." % (outfmt)
    return final_mc_curve

  def mcfit_dump_param_samples(self, out):
    """Dump the generated parameter samples for diagnostic purposes.
    """
    O = text_output(out)
    pnames = self.mc_params.dtype.names
    snames = self.mc_stats.dtype.names
    O.write("# %s ; %s ; nfev\n" % (" ".join(pnames), " ".join(snames)))
    O.write(matrix_str(array_hstack([ self.mc_params[k] for k in pnames ] + \
                                    [ self.mc_stats[k] for k in snames ] + \
                                    [ self.log_mc_funcalls]),
                       " %#17.10g")+ "\n")



