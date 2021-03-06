"""Python interface for grid smoothing code.

Grid smoothing refers to the process of mapping a continuously-defined shapes with
sharp boundaries to a rectangular grid in a continuous manner.  This process results
in a rectangular grid whose material distribution matches the defined shape
except at the boundaries where the effective material value is between the
material value within the bound shape and that of the surrounding medium, hence
making the boundaries appear as if they have been 'smoothed' out.

Ensuring that this mapping from 'real' space to the discretized rectangular
grid is continuous (i.e. small changes in the underlying boundaries produce
small changes in the material distribution of the grid) is very important to
sensitivity analysis. Gradients computed using an adjoint method, in
particular, will be inaccurate if changes to the material distribution occur in
discrete jumps which are too large.

Grid smoothing can be accomplished in a variety of ways.  The implementation
here is very general for sets of shapes which do not require changes in
topology (creation and elimination of holes, etc). It relies on representing
boundaries using polygons and then computing the smoothed grid by applying a
series of boolean subtraction operations (in c++).
"""

from ctypes import *
import numpy as np
from numpy.ctypeslib import ndpointer
import scipy
import os

from misc import DomainCoordinates
from misc import warning_message

__author__ = "Andrew Michaels"
__license__ = "GPL License, Version 3.0"
__version__ = "0.2"
__maintainer__ = "Andrew Michaels"
__status__ = "development"

dir_path = os.path.dirname(os.path.realpath(__file__))

so_path = ''.join([dir_path, '/Grid.so'])
libGrid = cdll.LoadLibrary(so_path)

# some useful definitions
c_complex_2D_p = ndpointer(np.complex128, ndim=2, flags='C')
c_complex_1D_p = ndpointer(np.complex128, ndim=1, flags='C')
c_double_p = ndpointer(np.double, ndim=1, flags='C')

#####################################################################################
# Material configuration 
#####################################################################################
libGrid.Material2D_get_value_real.argtypes = [c_void_p, c_double, c_double]
libGrid.Material2D_get_value_real.restype = c_double
libGrid.Material2D_get_value_imag.argtypes = [c_void_p, c_double, c_double]
libGrid.Material2D_get_value_imag.restype = c_double
libGrid.Material2D_get_values.argtypes = [c_void_p, c_int, c_int, c_int, c_int,
                                          c_complex_1D_p]
libGrid.Material2D_get_values.restype = None

####################################################################################
# GridMaterial configuration
####################################################################################
libGrid.GridMaterial2D_new.argtypes = [c_int, c_int, c_complex_2D_p]
libGrid.GridMaterial2D_new.restype = c_void_p
libGrid.GridMaterial2D_delete.argtypes = [c_void_p]
libGrid.GridMaterial2D_delete.restype = None
libGrid.GridMaterial2D_set_grid.argtypes = [c_void_p, c_int, c_int, c_complex_2D_p]
libGrid.GridMaterial2D_set_grid.restype = None
libGrid.GridMaterial2D_get_M.argtypes = [c_void_p]
libGrid.GridMaterial2D_get_M.restype = c_int
libGrid.GridMaterial2D_get_N.argtypes = [c_void_p]
libGrid.GridMaterial2D_get_N.restype = c_int

####################################################################################
# StructuredMaterial configuration
####################################################################################
libGrid.StructuredMaterial2D_new.argtypes = [c_double, c_double, c_double, c_double]
libGrid.StructuredMaterial2D_new.restype = c_void_p
libGrid.StructuredMaterial2D_delete.argtypes = [c_void_p]
libGrid.StructuredMaterial2D_delete.restype = None
libGrid.StructuredMaterial2D_add_primitive.argtypes = [c_void_p, c_void_p]
libGrid.StructuredMaterial2D_add_primitive.restype = None

####################################################################################
# MaterialPrimitives configuration
####################################################################################
libGrid.MaterialPrimitive_set_layer.argtypes = [c_void_p, c_int]
libGrid.MaterialPrimitive_set_layer.restype = None
libGrid.MaterialPrimitive_get_layer.argtypes = [c_void_p]
libGrid.MaterialPrimitive_get_layer.restype = c_int
libGrid.MaterialPrimitive_contains_point.argtypes = [c_void_p, c_double, c_double]
libGrid.MaterialPrimitive_contains_point.restype = c_bool
libGrid.MaterialPrimitive_get_material_real.argtypes = [c_void_p, c_double, c_double]
libGrid.MaterialPrimitive_get_material_real.restype = c_double
libGrid.MaterialPrimitive_get_material_imag.argtypes = [c_void_p, c_double, c_double]
libGrid.MaterialPrimitive_get_material_imag.restype = c_double


####################################################################################
# Circle configuration
####################################################################################
libGrid.Circle_new.argtypes = [c_double, c_double, c_double]
libGrid.Circle_new.restype = c_void_p
libGrid.Circle_delete.argtypes = [c_void_p]
libGrid.Circle_delete.restype = None
libGrid.Circle_set_material.argtypes = [c_void_p, c_double, c_double]
libGrid.Circle_set_material.restype = None
libGrid.Circle_set_position.argtypes = [c_void_p, c_double, c_double]
libGrid.Circle_set_position.restype = None
libGrid.Circle_set_radius.argtypes = [c_void_p, c_double]
libGrid.Circle_set_radius.restype = None
libGrid.Circle_get_x0.argtypes = [c_void_p]
libGrid.Circle_get_x0.restype = c_double
libGrid.Circle_get_y0.argtypes = [c_void_p]
libGrid.Circle_get_y0.restype = c_double
libGrid.Circle_get_r.argtypes = [c_void_p]
libGrid.Circle_get_r.restype = c_double

####################################################################################
# Rectangle configuration
####################################################################################
libGrid.Rectangle_new.argtypes = [c_double, c_double, c_double, c_double]
libGrid.Rectangle_new.restype = c_void_p
libGrid.Rectangle_delete.argtypes = [c_void_p]
libGrid.Rectangle_delete.restype = None
libGrid.Rectangle_set_material.argtypes = [c_void_p, c_double, c_double]
libGrid.Rectangle_set_material.restype = None
libGrid.Rectangle_set_position.argtypes = [c_void_p, c_double, c_double]
libGrid.Rectangle_set_position.restype = None
libGrid.Rectangle_set_width.argtypes = [c_void_p, c_double]
libGrid.Rectangle_set_width.restype = None
libGrid.Rectangle_set_height.argtypes = [c_void_p, c_double]
libGrid.Rectangle_set_height.restype = None

####################################################################################
# Polygon configuration
####################################################################################
libGrid.Polygon_new.argtypes = []
libGrid.Polygon_new.restype = c_void_p
libGrid.Polygon_delete.argtypes = [c_void_p]
libGrid.Polygon_delete.restype = None
libGrid.Polygon_set_material.argtypes = [c_void_p, c_double, c_double]
libGrid.Polygon_set_material.restype = None
libGrid.Polygon_add_point.argtypes = [c_void_p, c_double, c_double]
libGrid.Polygon_add_point.restype = None
libGrid.Polygon_add_points.argtypes = [c_void_p, c_double_p, c_double_p, c_int]
libGrid.Polygon_add_points.restype = None
libGrid.Polygon_set_points.argtypes = [c_void_p, c_double_p, c_double_p, c_int]
libGrid.Polygon_set_points.restype = None
libGrid.Polygon_set_point.argtypes = [c_void_p, c_double, c_double, c_int]
libGrid.Polygon_set_point.restype = None

####################################################################################
# ConstantMaterial configuration
####################################################################################
libGrid.ConstantMaterial2D_new.argtypes = [c_double, c_double]
libGrid.ConstantMaterial2D_new.restype = c_void_p
libGrid.ConstantMaterial2D_set_material.argtypes = [c_void_p, c_double, c_double]
libGrid.ConstantMaterial2D_set_material.restype = None
libGrid.ConstantMaterial2D_get_material_real.argtypes = [c_void_p]
libGrid.ConstantMaterial2D_get_material_real.restype = None
libGrid.ConstantMaterial2D_get_material_imag.argtypes = [c_void_p]
libGrid.ConstantMaterial2D_get_material_imag.restype = None

####################################################################################
# Misc
####################################################################################
libGrid.row_wise_A_update.argtypes = [c_void_p, c_void_p, c_int, c_int, c_int, c_int, \
                                      c_int, c_int, c_int, c_int, c_complex_1D_p]
libGrid.row_wise_A_update.restype = None

class Material2D(object):
    """Define a general interface for 2D Material distributions.

    Notes
    -----
    Currently material distributions only support 2D systems.

    Methods
    -------
    get_value(self, x, y)
        Get the value of the material distribution at (x,y)
    get_values(self, m1, m2, n1, n2, arr=None)
        Get the values of the material distribution within a set of array
        indicesa set of array indices.
    get_values_on(self, domain)
        Get the values of the material distribution within a domain.
    """

    def __init__(self):
        self._object = None

    def get_value(self, x, y):
        """Get the value of the material distribution at (x,y).

        Parameters
        ----------
        x : int or float
            The (fractional) x index.
        y : int or float
            The (fractional) y index.

        Returns
        -------
        complex128
            The complex material value at the desired location.
        """
        a = libGrid.Material2D_get_value_real(self._object, x, y)
        b = libGrid.Material2D_get_value_imag(self._object, x, y)

        return a + 1j*b

    def get_values(self, k1, k2, j1, j2, arr=None):
        """Get the values of the material distribution within a set of array
        indicesa set of array indices.

        Parameters
        ----------
        k1 : int
            The lower integer bound on x of the desired region
        k2 : int
            The upper integer bound on x of the desired region
        j1 : int
            The lower integer bound on y of the desired region
        j2 : int
            The upper integer bound on y of the desired region
        arr : numpy.ndarray (optional)
            The array with dimension (m2-m1)x(n2-n1) with type np.complex128
            which will store the retrieved material distribution. If None, a
            new array will be created. (optional = None)

        Returns
        -------
        numpy.ndarray
            The retrieved complex material distribution.
        """
        Nx = k2-k1
        Ny = j2-j1

        if(type(arr) == type(None)):
            arr = np.zeros(Nx*Ny, dtype=np.complex128)
        else:
            arr = np.ravel()

        libGrid.Material2D_get_values(self._object, k1, k2, j1, j2, arr)

        # This might result in an expensive copy operation, unfortunately
        arr = np.reshape(arr, [Ny, Nx])

        return arr

    def get_values_on(self, domain):
        """Get the values of the material distribution within a domain.

        Parameters
        ----------
        domain : emopt.misc.DomainCoordinates
            The domain in which the material distribution is retrieved.

        Returns
        -------
        numpy.ndarray
            The retrieved material distribution which lies in the domain.
        """
        j1 = domain.j.start
        j2 = domain.j.stop
        k1 = domain.k.start
        k2 = domain.k.stop

        return self.get_values(k1, k2, j1, j2)

class ConstantMaterial2D(Material2D):
    """A uniform constant material.

    Parameters
    ----------
    value : complex
        The constant material value.

    Attributes
    ----------
    material_value : complex
        The constant material value
    """
    def __init__(self, value):
        self._material_value = value
        self._object = libGrid.ConstantMaterial2D_new(value.real, value.imag)

    @property
    def material_value(self):
        return self._material_value

    @material_value.setter
    def material_value(self, new_value):
        libGrid.ConstantMaterial2D_set_material(self._object,
                                              new_value.real,
                                              new_value.imag)
        self._material_value = new_value

class GridMaterial2D(Material2D):
    """Define a simple rectangular-grid-based Material distribution.

    This is the simplest form of :class:`.Material` object which defines a
    material distribution as a simple rectangular grid. On its own, there is
    no grid smoothing performed by a :class:`.GridMaterial`, however it can be
    used to implement custom grid smoothing subroutines.

    Parameters
    ----------
    M : int
        Number of rows in the grid.
    N : int
        Number of columns in the grid.
    grid : numpy.ndarray
        The complex (dtype=np.complex128) material distribution

    Attributes
    ----------
    M : int
        The number of rows in the grid.
    N : int
        The number of cols in the grid.
    grid : numpy.ndarray
        The complex material distribution.
    """

    def __init__(self, M, N, grid):
        grid = grid.astype(np.complex128, copy=False)
        self._object = libGrid.GridMaterial2D_new(M, N, grid)

        self._M = M
        self._N = N
        self._grid = grid

    def __del__(self):
        libGrid.GridMaterial2D_delete(self._object)

    @property
    def M(self):
        return self._M

    @M.setter
    def M(self, newM):
        libGrid.GridMaterial2D_delete(self._object)
        self._object = libGrid.GridMaterial2D_new(newM, self._N, grid)
        self._M = newM

    @property
    def N(self):
        return self._N

    @N.setter
    def N(self, newN):
        libGrid.GridMaterial_delete(self._object)
        self._object = libGrid.GridMaterial_new(self._M, newN, grid)
        self._N = newN

    @property
    def grid(self):
        return self._grid

    @grid.setter
    def grid(self, new_grid):
        self._grid = new_grid
        self._object = libGrid.GridMaterial2D_new(self._M, self._N, new_grid)

class GridMaterial3D(object):

    def __init__(self, X, Y, Z, Nx, Ny, Nz, grid):
        self.X = X
        self.Y = Y
        self.Z = Z
        self.Nx = Nx
        self.Ny = Ny
        self.Nz = Nz
        self.grid = grid

    def get_value(self, k, j ,i):
        return self.grid[i,j,k]


class MaterialPrimitive(object):
    """Define a MaterialPrimitive.

    A MaterialPrimitive is a material distribution belonging to shapes like
    rectangles, circules, polygons, etc.

    TODO
    ----
    Pythonify this function using properties.

    Methods
    -------
    contains_point(self, x, y)
        Check if a material primitive contains the supplied (x,y) coordinate

    Attributes
    ----------
    layer : int
        The layer of the material primitive. Lower means higher priority in
        terms of visibility.
    """

    def __init__(self):
        self._object = None
        self._layer = 1

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, newlayer):
        self._layer = newlayer
        libGrid.MaterialPrimitive_set_layer(self._object, c_int(newlayer))

    def get_layer(self):
        """Get the layer of the primitive.

        Returns
        -------
        int
            The layer.
        """
        warning_message('get_layer() is deprecated. Use property ' \
            'myprim.layer instead.', 'emopt.grid')
        return libGrid.MaterialPrimitive_get_layer(self._object)

    def set_layer(self, layer):
        """Set the layer of the primitive.

        Parameters
        ----------
        layer : int
            The new layer.
        """
        warning_message('set_layer(...) is deprecated. Use property ' \
            'myprim.layer=... instead.', 'emopt.grid')
        libGrid.MaterialPrimitive_set_layer(self._object, c_int(layer))

    def contains_point(self, x, y):
        """Check if a material primitive contains the supplied (x,y) coordinate

        Parameters
        ----------
        x : float
            The real-space x coordinate
        y : float
            The real-space y coordinate

        Returns
        -------
        bool
            True if the (x,y) point is contained within the primitive, false
            otherwise.
        """
        return libGrid.MaterialPrimitive_contains_point(self._object, x, y)

class Circle(MaterialPrimitive):
    """Define a circle primitive.

    Notes
    -----
    This is not fully implemented.

    TODO
    ----
    Actually fully implement this.
    """
    def __init__(self, x0, y0, r):
        self._object = libGrid.Circle_new(c_double(x0),
                                         c_double(y0),
                                         c_double(r))

    def __del__(self):
        libGrid.Circle_delete(self._object)

    def set_material(self, mat):
        libGrid.Circle_set_material(self._object, mat.real, mat.imag)

    def set_position(self, x0, y0):
        libGrid.Circle_set_position(self._object, x0, y0)

    def set_radius(self, r):
        libGrid.Circle_set_radius(self._object, r)

    def get_x0(self):
        return libGrid.Circle_get_x0(self._object)

    def get_y0(self):
        return libGrid.Circle_get_y0(self._object)

    def get_r(self):
        return libGrid.Circle_get_r(self._object)

class Rectangle(MaterialPrimitive):
    """Define a rectangular material primitive.

    A rectangle is defined by its center position and its width and height.

    Parameters
    ----------
    x0 : float
        The x coordinate of the center of the Rectangle
    y0 : float
        The y coordinate of the center of the Rectangle
    xspan : float
        The width of the Rectangle
    yspan : float
        The height of the Rectangle

    Attributes
    ----------
    x0 : float
        The x coordinate of the center of the Rectangle
    y0 : float
        The y coordinate of the center of the Rectangle
    width : float
        The width of the Rectangle
    height : float
        The height of the Rectangle
    material_value : complex128
        The material value of the Rectangle's interior

    Methods
    -------
    set_material(self, mat)
        (Deprecated) Set the material value of the Rectangle's interior.
    set_position(self, x0, y0)
        Set the (x,y) position of the center of the Rectangle.
    set_width(self, width)
        (Deprecated) Set the width of the rectangle.
    set_height(self, height)
        (Deprecated) Set the height of the rectangle.
    """

    def __init__(self, x0, y0, xspan, yspan):
        self._object = libGrid.Rectangle_new(x0, y0, xspan, yspan)
        self._x0 = x0
        self._y0 = y0
        self._xspan = xspan
        self._yspan = yspan

        self._mat = 1.0

    def __del__(self):
        libGrid.Rectangle_delete(self._object)

    @property
    def x0(self):
        return self._x0

    @property
    def y0(self):
        return self._y0

    @property
    def width(self):
        return self._xspan

    @property
    def height(self):
        return self._yspan

    @property
    def material_value(self):
        return self._mat

    @x0.setter
    def x0(self, x):
        self._x0 = x
        libGrid.Rectangle_set_position(self._object, self._x0, self._y0)

    @y0.setter
    def y0(self, y):
        self._y0 = y
        libGrid.Rectangle_set_position(self._object, self._x0, self._y0)

    @width.setter
    def width(self, w):
        self._xspan = w
        libGrid.Rectangle_set_width(self._object, w)

    @height.setter
    def height(self, h):
        self._yspan = h
        libGrid.Rectangle_set_height(self._object, h)

    @material_value.setter
    def material_value(self, mat):
        self._mat = mat
        libGrid.Rectangle_set_material(self._object, mat.real, mat.imag)

    def set_material(self, mat):
        """(Deprecated) Set the material value of the Rectangle's interior.
        """
        warning_message('set_mateiral(...) is deprecated. Use property ' \
                        'myrect.material_value=... instead.', 'emopt.grid')
        libGrid.Rectangle_set_material(self._object, mat.real, mat.imag)

    def set_position(self, x0, y0):
        """Set the (x,y) position of the center of the Rectangle.

        Parameters
        ----------
        x0 : float
            The x coordinate of the center of the Rectangle.
        y0 : float
            The y coordinate of the center of the Rectangle.
        """
        libGrid.Rectangle_set_position(self._object, x0, y0)
        self._x0 = x0
        self._y0 = y0

    def set_width(self, width):
        """(Deprecated) Set the width of the rectangle.
        """
        warning_message('set_width(...) is deprecated. Use property ' \
                        'myrect.width=... instead.', 'emopt.grid')

        libGrid.Rectangle_set_width(self._object, width)
        self._xspan = width

    def set_height(self, height):
        """(Deprecated) Set the height of the rectangle."""
        warning_message('set_width(...) is deprecated. Use property ' \
                        'myrect.width=... instead.', 'emopt.grid')

        libGrid.Rectangle_set_height(self._object, height)
        self._yspan = height

class Polygon(MaterialPrimitive):

    def __init__(self):
        self._object = libGrid.Polygon_new()

        self._xs = []
        self._ys = []
        self._Np = []
        self._value = 1.0

    @property
    def xs(self):
        return np.copy(self._xs)

    @property
    def ys(self):
        return np.copy(self._ys)

    @property
    def Np(self):
        return self._Np

    @property
    def material_value(self):
        return self._value

    @xs.setter
    def xs(self, vals):
        warning_message('Polygon.xs cannot be set on its own. Use ' \
                        'set_points(x,y) instead', 'emopt.grid.Polygon')

    @ys.setter
    def ys(self, vals):
        warning_message('Polygon.ys cannot be set on its own. Use ' \
                        'set_points(x,y) instead', 'emopt.grid.Polygon')

    @Np.setter
    def Np(self, N):
        warning_message('Polygon.Np cannot be modified in this way.', \
                        'emopt.grid.Polygon')

    @material_value.setter
    def material_value(self, value):
        libGrid.Polygon_set_material(self._object, value.real, value.imag)
        self._value = value

    def __del__(self):
        libGrid.Polygon_delete(self._object)

    def add_point(self, x, y):
        libGrid.Polygon_add_point(self._object, x, y)

        self._Np += 1
        self._xs = np.concatenate(self._xs, [x])
        self._ys = np.concatenate(self._ys, [y])

    def add_points(self, x, y):
        x = np.array(x, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        libGrid.Polygon_add_points(self._object, x, y, len(x))

        self._Np += len(x)
        self._xs = np.concatenate(self._xs, x)
        self._ys = np.concatenate(self._ys, y)

    def set_points(self, x, y):
        x = np.array(x, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        libGrid.Polygon_set_points(self._object, x, y, len(x))

        self._Np = len(x)
        self._xs = np.copy(x)
        self._ys = np.copy(y)

    def set_point(self, index, x, y):
        libGrid.Polygon_set_point(self._object, x, y, index)

        self._xs[index] = x
        self._ys[index] = y

    def set_material(self, mat):
        warning_message('set_material(...) is deprecated. Use property ' \
                        'mypoly.material_value=... instead.', 'emopt.grid')
        libGrid.Polygon_set_material(self._object, mat.real, mat.imag)
        self._value = mat

class StructuredMaterial2D(Material2D):

    def __init__(self, w, h, dx, dy):
        self._object = libGrid.StructuredMaterial2D_new(w, h, dx, dy)

    def __del__(self):
        libGrid.StructuredMaterial2D_delete(self._object)

    def add_primitive(self, prim):
        libGrid.StructuredMaterial2D_add_primitive(self._object, prim._object)

def row_wise_A_update(eps, mu, ib, ie, M, N, x1, x2, y1, y2, vdiag):
    libGrid.row_wise_A_update(eps._object, mu._object, ib, ie, M, N, x1, x2, y1, y2, vdiag)
    return vdiag
