## @defgroup Plots  
# Plots contains functions for generating common figures

from .Mission_Plots  import plot_flight_conditions 
from .Mission_Plots  import plot_aerodynamic_coefficients
from .Mission_Plots  import plot_stability_coefficients
from .Mission_Plots  import plot_aerodynamic_forces
from .Mission_Plots  import plot_drag_components
from .Mission_Plots  import plot_altitude_sfc_weight
from .Mission_Plots  import plot_aircraft_velocities
from .Mission_Plots  import plot_battery_age_conditions
from .Mission_Plots  import plot_battery_cell_conditions
from .Mission_Plots  import plot_battery_pack_conditions
from .Mission_Plots  import plot_propeller_conditions 
from .Mission_Plots  import plot_eMotor_Prop_efficiencies
from .Mission_Plots  import plot_disc_power_loading
from .Mission_Plots  import plot_solar_flux
from .Mission_Plots  import plot_lift_cruise_network  
from .Mission_Plots  import plot_propeller_conditions 
from .Mission_Plots  import plot_surface_pressure_contours
from .Mission_Plots  import create_video_frames

from .Geometry_Plots import plot_airfoil
from .Geometry_Plots import plot_propeller_geometry
from .Geometry_Plots import plot_vehicle_vlm_panelization