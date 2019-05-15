## @ingroup Analyses-Aerodynamics
# Vortex_Lattice.py
#
# Created:  Nov 2013, T. Lukaczyk
# Modified:     2014, T. Lukaczyk, A. Variyar, T. Orra
#           Feb 2016, A. Wendorff
#           Apr 2017, T. MacDonald
#           Nov 2017, E. Botero


# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

# SUAVE imports
import SUAVE

from SUAVE.Core import Data
from SUAVE.Core import Units

from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.VLM import VLM

# local imports
from .Aerodynamics import Aerodynamics
from SUAVE.Methods.Aerodynamics.Common.Fidelity_Zero.Lift.compute_vortex_distribution import compute_vortex_distribution
from SUAVE.Plots import plot_vehicle_vlm_panelization

# package imports
import numpy as np


# ----------------------------------------------------------------------
#  Class
# ----------------------------------------------------------------------
## @ingroup Analyses-Aerodynamics
class Vortex_Lattice_Surrogate(Aerodynamics):
    """This builds a surrogate and computes lift using a basic vortex lattice.

    Assumptions:
    None

    Source:
    None
    """ 

    def __defaults__(self):
        """This sets the default values and methods for the analysis.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        N/A
        """  
        self.tag = 'Vortex_Lattice'

        self.geometry = Data()
        self.settings = Data()

        # vortex lattice configurations
        self.settings.number_panels_spanwise  = 16
        self.settings.number_panels_chordwise = 4
        self.settings.vortex_distribution = Data()
        
        # conditions table, used for surrogate model training
        self.training = Data()        
        self.training.angle_of_attack       = np.array([[-10.,-5.,0.,5.,10.]]).T * Units.deg
        self.training.lift_coefficient      = None
        self.training.wing_lift_coefficient = None
        self.training.drag_coefficient      = None
        self.training.wing_drag_coefficient = None
        
        # surrogoate models
        self.surrogates = Data()
        self.surrogates.lift_coefficient = None        
        
    def initialize(self):
        """Drives functions to get training samples and build a surrogate.

        Assumptions:
        None

        Source:
        N/A

        Inputs:
        None

        Outputs:
        None

        Properties Used:
        None
        """                      
        # Unpack:
        geometry = self.geometry
        settings = self.settings        
           
        # generate vortex distribution
        VD = compute_vortex_distribution(geometry,settings)      
        
        # Pack
        self.settings.vortex_distribution = VD
        
        # Plot vortex discretization of vehicle
        #plot_vehicle_vlm_panelization(VD)        
        
        # sample training data
        self.sample_training()
                    
        # build surrogate
        self.build_surrogate()        


    def evaluate(self,state,settings,geometry):
        """Evaluates lift and drag using available surrogates.

        Assumptions:
        no changes to initial geometry or settings

        Source:
        N/A

        Inputs:
        state.conditions.
          freestream.dynamics_pressure       [-]
          angle_of_attack                    [radians]

        Outputs:
        conditions.aerodynamics.lift_breakdown.
          inviscid_wings_lift[wings.*.tag]   [-] CL (wing specific)
          inviscid_wings_lift.total          [-] CL
        conditions.aerodynamics.
          lift_coefficient_wing              [-] CL (wing specific)
        inviscid_wings_lift                  [-] CL

        Properties Used:
        self.surrogates.
          lift_coefficient                   [-] CL
          wing_lift_coefficient[wings.*.tag] [-] CL (wing specific)
        """          
        
        # unpack        
        conditions = state.conditions
        settings   = self.settings
        geometry   = self.geometry
        AoA        = conditions.aerodynamics.angle_of_attack
           
        # Unapck the surrogates
        CL_surrogate = self.surrogates.lift_coefficient
        CD_surrogate = self.surrogates.drag_coefficient
        wing_CL_surrogates = self.surrogates.wing_lifts 
        wing_CD_surrogates = self.surrogates.wing_drags
        
        # Evaluate the surrogate
        lift_coefficients = CL_surrogate(AoA)
        drag_coefficients = CD_surrogate(AoA)
        
        # Pull out the individual lifts
        wing_lifts = Data()
        wing_drags = Data()
        
        for key in geometry.wings.keys():
            wing_lifts[key] = wing_CL_surrogates[key](AoA)
            wing_drags[key] = wing_CD_surrogates[key](AoA)
        
        # Pack
        inviscid_wings_lift                                              = Data()
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift       = Data()
        
        conditions.aerodynamics.lift_breakdown.inviscid_wings_lift.total = lift_coefficients
        state.conditions.aerodynamics.lift_coefficient                   = lift_coefficients
        
        state.conditions.aerodynamics.lift_breakdown.inviscid_wings_lift = wing_lifts
        state.conditions.aerodynamics.lift_coefficient_wing              = wing_lifts
        
        state.conditions.aerodynamics.drag_coefficient_wing              = wing_drags
        conditions.aerodynamics.drag_breakdown.induced.total             = drag_coefficients
        
        
        return
    
    def sample_training(self):
        # unpack
        geometry = self.geometry
        settings = self.settings
        training = self.training
        
        # Setup Konditions
        konditions              = Data()
        konditions.aerodynamics = Data()
        konditions.aerodynamics.angle_of_attack = training.angle_of_attack
        
        # Get the training data
        total_lift, total_drag, wing_lifts, wing_drags = calculate_lift_vortex_lattice(konditions,settings,geometry)
        
        if np.isnan(total_lift).any():
            print('NaN!')
            plot_vehicle_vlm_panelization(settings.vortex_distribution)  
        
        # Store training data
        training.lift_coefficient = total_lift
        training.drag_coefficient = total_drag
        training.wing_lifts       = wing_lifts
        training.wing_drags       = wing_drags
        
        return
        
    def build_surrogate(self):
        # unpack data
        training = self.training
        AoA_data = training.angle_of_attack
        CL_data  = training.lift_coefficient
        CD_data  =  training.drag_coefficient
        wing_CL_data = training.wing_lifts
        wing_CD_data = training.wing_drags    
        
        # learn the models
        CL_surrogate = np.poly1d(np.polyfit(AoA_data.T[0], CL_data.T[0], 1))
        CD_surrogate = np.poly1d(np.polyfit(AoA_data.T[0], CD_data.T[0], 2))
        
        wing_CL_surrogates = Data()
        wing_CD_surrogates = Data()
        
        for wing in wing_CL_data.keys():
            wing_CL_surrogates[wing] = np.poly1d(np.polyfit(AoA_data.T[0], wing_CL_data[wing].T[0], 1))   
            wing_CD_surrogates[wing] = np.poly1d(np.polyfit(AoA_data.T[0], wing_CD_data[wing].T[0], 2))   
        
        # Pack the outputs
        self.surrogates.lift_coefficient = CL_surrogate
        self.surrogates.drag_coefficient = CD_surrogate
        self.surrogates.wing_lifts       = wing_CL_surrogates
        self.surrogates.wing_drags       = wing_CD_surrogates
        
        
        
        

# ----------------------------------------------------------------------
#  Helper Functions
# ----------------------------------------------------------------------


def calculate_lift_vortex_lattice(conditions,settings,geometry):
    """Calculate the total vehicle lift coefficient and specific wing coefficients (with specific wing reference areas)
    using a vortex lattice method.

    Assumptions:
    None

    Source:
    N/A

    Inputs:
    conditions                      (passed to vortex lattice method)
    settings                        (passed to vortex lattice method)
    geometry.reference_area         [m^2]
    geometry.wings.*.reference_area (each wing is also passed to the vortex lattice method)

    Outputs:
    total_lift_coeff          [array]
    total_induced_drag_coeff  [array]
    wing_lifts                [Data]
    wing_drags                [Data]

    Properties Used:
    
    """            

    # unpack
    vehicle_reference_area = geometry.reference_area

    # iterate over wings
    wing_lifts = Data()
    wing_drags = Data()
    
    total_lift_coeff,total_induced_drag_coeff, CM, CL_wing, CDi_wing= VLM(conditions,settings,geometry)

    ii = 0
    for wing in geometry.wings.values():
        wing_lifts[wing.tag] = 1*(np.atleast_2d(CL_wing[:,ii]).T)
        wing_drags[wing.tag] = 1*(np.atleast_2d(CDi_wing[:,ii]).T)
        ii+=1
        if wing.symmetric:
            wing_lifts[wing.tag] += 1*(np.atleast_2d(CL_wing[:,ii]).T)
            wing_drags[wing.tag] += 1*(np.atleast_2d(CDi_wing[:,ii]).T)
            ii+=1

    return total_lift_coeff, total_induced_drag_coeff, wing_lifts, wing_drags