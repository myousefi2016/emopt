"""Demonstrate how to use the emopt mode solver (for 3D problems with 2D
slices).

On most *nix-based machines, run the script with:

    $ mpirun -n 8 python wg_modes.py

If you wish to increase the number of cores that the example is executed on,
change 8 to the desired number of cores.
"""
import emopt
from emopt.misc import NOT_PARALLEL

import numpy as np
from math import pi

####################################################################################
# Set up the size of the problem
####################################################################################
W = 3.0
H = 3.22
dx = 0.02
dy = 0.02
N = int(np.ceil(W/dy)+1)
M = int(np.ceil(H/dy)+1)
W = (N-1)*dy
H = (M-1)*dy

wavelength = 1.31

####################################################################################
# Define the material distributions!
####################################################################################
eps_Si = 3.5**2
eps_SiO2 = 1.444**2

w_wg = 1.5
h_SOI = 0.22
h_etched = 0.0

# we need to set up the geometry of the cross section for which the mode will
# be computed. Ultimately, all we supply is two 2D arrays containing the
# permittivity and permeability distributions. How you create these
# distributions is up to you. Here we use emopt.grid objects to do it.
rib = emopt.grid.Rectangle(W/2, 1.5+h_SOI/2.0, w_wg, h_SOI)
etched = emopt.grid.Rectangle(W/2, 1.5+h_etched/2.0, 2*W, h_etched)
eps_bg = emopt.grid.Rectangle(W/2, H/2, 2*W, 2*H)

rib.layer = 1; rib.material_value = eps_Si
etched.layer = 1; etched.material_value = eps_Si
eps_bg.layer = 2; eps_bg.material_value = eps_SiO2

eps = emopt.grid.StructuredMaterial2D(W,H,dx,dy)
eps.add_primitive(rib); eps.add_primitive(etched); eps.add_primitive(eps_bg)

mu = emopt.grid.ConstantMaterial2D(1.0)

eps_arr = eps.get_values(0,M,0,N)
mu_arr = mu.get_values(0,M,0,N)

####################################################################################
# setup the mode solver
####################################################################################
neigs = 16
modes = emopt.modes.Mode_FullVector(wavelength, dx, dy, eps_arr, mu_arr, n0=np.sqrt(eps_Si), neigs=neigs)
modes.build() # build the eigenvalue problem internally
modes.solve() # solve for the effective indices and mode profiles

Ex = modes.get_field_interp(0, 'Ex')
if(NOT_PARALLEL):
    import matplotlib.pyplot as plt

    print modes.neff[0]

    #Ex = fields[0:M,:]
    vmin = np.min(np.abs(Ex))
    vmax = np.max(np.abs(Ex))
    levels = np.linspace(vmin, vmax, 16)

    f = plt.figure()
    ax = f.add_subplot(111)
    im = ax.contourf(np.abs(Ex), extent=[0,W,0,H], levels=levels, vmin=vmin,
                     vmax=vmax, cmap='hot')
    ax.contour(np.abs(Ex), extent=[0,W,0,H], linewidths=[0.5,],
               colors='k')
    # Technically epsilon is defined half a grid cell below the field
    # interpolation points. We shift epsilon up by this much to make the
    # visualization look correct
    ax.contour(eps_arr.real, levels=[eps_Si,], extent=[0,W,dy/2.0,H+dy/2.0],
                linewidths=[1,], colors=['w'])
    f.colorbar(im)
    plt.show()
