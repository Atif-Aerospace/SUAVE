# test_sweeps.py
#
# Created: Oct 2017, M. Vegh
# Modified Jan 2018, W. Maier 
#          Mar 2020, M. Clarke

# ----------------------------------------------------------------------
#   Imports
# ----------------------------------------------------------------------

import numpy as np
from SUAVE.Optimization import carpet_plot, line_plot
from SUAVE.Core import Units

import sys
sys.path.append('../Regional_Jet_Optimization')
from Optimize2 import setup


# ----------------------------------------------------------------------
#   Main
# ----------------------------------------------------------------------

def main():
    
    # Pull out the problem and reset the bounds
    problem          = setup()
    problem.optimization_problem.inputs = np.array([
        [ 'wing_area'       ,  95, (   90. ,   120.   ) ,   100. , Units.meter**2],
        [ 'cruise_altitude' ,  11, (   10   ,   13.   ) ,   10.  , Units.km]])
    
    outputs_sweep    = linear_sweep(problem)
    truth_obj_sweeps = [[6789.56688781, 6925.72625581]]
    
    #print outputs_sweep
    max_err_sweeps = (np.max(np.abs(outputs_sweep['objective']-truth_obj_sweeps )/truth_obj_sweeps))
    
    print('max_err_sweeps = ', max_err_sweeps)
    assert(max_err_sweeps<1e-6)
    outputs_carpet = variable_sweep(problem)
    
    #print outputs_carpet
    truth_obj_carp  = [[6671.85750894, 6915.38902541],[6989.51098006, 6912.43394347]]
    max_err_carp    = np.max(np.abs(outputs_carpet['objective']-truth_obj_carp)/truth_obj_carp) 
    print(' max_err_carp = ',  max_err_carp)
    assert(max_err_carp<1e-6)
    return
        

def linear_sweep(problem):
    number_of_points = 2
    outputs = line_plot(problem, number_of_points, plot_obj = 0, plot_const = 0)
    return outputs
    
def variable_sweep(problem):    
    number_of_points=2
    #run carpet plot, suppressing default plots
    outputs=carpet_plot(problem, number_of_points,  plot_obj = 0, plot_const = 0)  
    return outputs

if __name__ == '__main__':
    main()