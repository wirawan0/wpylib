# Created: 20150528
# Test module for stochastic fitting

import numpy
from wpylib.params import struct
from wpylib.math.fitting.stochastic import StochasticFitting

def setup_MC_TZ():
  """
  Internal identifier: Cr2_TZ_data_20140728uhf
  Binding energy of Cr2, phaseless QMC/UHF, cc-pwCVTZ-DK, dt=0.01
  """
  global Cr2_TZ_data_20140728uhf
  from numpy import asarray, matrix
  Cr2_TZ_data_20140728uhf = asarray(matrix("""
       1.550   -1.613    0.025  ;
       1.600   -1.897    0.036  ;
       1.6788  -2.141    0.016  ;
       1.720   -2.143    0.025  ;
       1.800   -2.190    0.022  ;
       1.900   -2.064    0.020  ;
       2.000   -2.038    0.023  ;
       2.400   -1.611    0.019  ;
       3.000   -1.037    0.018
  """))



def test_fit_PEC_MC_TZ(show_samples=True, save_fig=False, rng=None, num_iter=200):
  """20150528
  PEC fitting, using `morse2` functional form.

  Options:
  - show_samples : prints the sample data (recommended)
  - save_fig : dumps the fit result for each stochastic snapshot
    (not recommended unless you are debugging/diagnosing)

  Modeled after do_morse2_sfit routine in Cr2 analysis script.

  Example output:

      test_MC_TZ_PEC_fit::
      ansatz=morse2_fit_func
      Raw data: (x, y, dy)
             1.550   -1.613    0.025
             1.600   -1.897    0.036
             1.679   -2.141    0.016
             1.720   -2.143    0.025
             1.800   -2.190    0.022
             1.900   -2.064    0.020
             2.000   -2.038    0.023
             2.400   -1.611    0.019
             3.000   -1.037    0.018
      Using guess param from NLF:  [-2.18625505  9.82497657  1.80455072  1.86192922]
      Final parameters          : -2.187(10)  9.85(61)  1.8044(66)  1.864(83)
      Total execution time = 0.55 secs
      All testings passed.

  Where the input variables are:
    x     = bond length (angstrom)
    y, dy = binding energy (eV)
  and the final (output) parameters are (in the same order as above):
    Ebind = binding energy minimum (eV)
    k     = spring constant (eV/angstrom**2)
    r0    = equilibrium bond length (angstrom)
    a     = morse2 nonlinear constant (angstrom**-1)

  The guess params from NLF above are the same as what gnuplot fitting
  routine gives, which are:

      Final set of parameters            Asymptotic Standard Error
      =======================            ==========================

      E0              = -2.18626         +/- 0.03193      (1.46%)
      k               = 9.82591          +/- 1.59         (16.19%)
      re              = 1.80454          +/- 0.01763      (0.9771%)
      a               = 1.86206          +/- 0.2172       (11.66%)

  Nonlinear-fitting.pl (perl script) gives the stochastic fit result:

      -2.183(11)  9.97(65)  1.8046(69)  1.886(90)

  Excellent agreement!

  """
  from numpy import array
  from wpylib.text_tools import matrix_str, str_indent
  from wpylib.timer import block_timer as Timer
  from wpylib.math.fitting.funcs_pec import morse2_fit_func
  from wpylib.py import function_name

  global MC_TZ_PEC_fit
  global Cr2_TZ_data_20140728uhf

  print("test_MC_TZ_PEC_fit::")
  setup_MC_TZ()

  # parameters etc
  ansatz = morse2_fit_func()
  if rng is None:
    rng = dict(seed=378711, rng_class=numpy.random.RandomState)
  rawdata = Cr2_TZ_data_20140728uhf
  sfit = MC_TZ_PEC_fit = StochasticFitting()

  print("ansatz=%s" \
        % (function_name(ansatz),))

  # This corresponds to fit_variant==1 in the subroutine
  ansatz.fit_method = "leastsq"
  ansatz.fit_opts['leastsq'] = dict(xtol=1e-8, epsfcn=1e-6)

  sfit.init_func(ansatz)
  sfit.init_samples(x=rawdata[:,0], y=rawdata[:,1], dy=rawdata[:,2])
  sfit.init_rng(**rng)
  if show_samples:
    print("Raw data: (x, y, dy)")
    print(str_indent(matrix_str(rawdata, fmt="%8.3f")))

  with Timer() as tmr:
    sfit.mcfit_loop_begin_()
    sfit.mcfit_loop1_(num_iter=num_iter, save_fig=save_fig)
    sfit.mcfit_loop_end_()
    sfit.mcfit_analysis_()
    sfit.mcfit_report_final_params()

  nlf_fit_result = sfit.nlf_rec['xopt']

  # Verify the results:
  # * deterministic fit (only precise to these digits; more digits are discarded)
  nlf_fit_ref = numpy.array([-2.18625505,  9.82497657,  1.80455072,  1.86192922])

  assert numpy.allclose(nlf_fit_result, nlf_fit_ref, atol=0.6e-8, rtol=0)

  def match_mc_param(name, val_ref, err_ref, atol):
    vv = sfit.final_mc_params[name]
    assert numpy.allclose(vv.value(), val_ref, atol=atol, rtol=0)
    assert numpy.allclose(vv.error(), err_ref, atol=atol, rtol=0)

  match_mc_param('E0', -2.187,  0.010,  0.6e-3)
  match_mc_param('k',   9.85,   0.61,   0.6e-2)
  match_mc_param('r0',  1.8044, 0.0066, 0.6e-4)
  match_mc_param('a',   1.864,  0.083,  0.6e-3)
  print("All testings passed.")


if __name__ == '__main__':
  test_fit_PEC_MC_TZ()
