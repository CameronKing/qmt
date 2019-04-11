from dataclasses import dataclass
from typing import Optional, List, Union
from enum import Enum
from .data_utils import write_deserialised

"""
Once you inherit from a dataclass that has default parameters, you can't add any more
non default parameters to it. To work around this, we split the parameters with
defaults into a separate class and use Python's Method Resolution Order to make sure
that these parameters come later than parameters without defaults
https://stackoverflow.com/questions/51575931/class-inheritance-in-python-3-7-dataclasses
"""


@dataclass
class _PartDataRequired:
    """
    Required fields for the base class of part data
    :field label: The descriptive name of this new part.
    """

    label: str


@dataclass
class _PartDataDefaults:
    """
    Optional fields for the base class of part data
    :field material: The material of the resulting part
    """

    material: Optional[str] = None


class DomainType(Enum):
    """
    The type of domain a part represents. Valid options are:
        - semiconductor -- region permitted to self-consistently accumulate
        - metal_gate -- an electrode
        - virtual -- a part just used for selection (ignores material)
        - dielectric -- no charge accumulation allowed
    """

    semiconductor = 1
    metal_gate = 2
    virtual = 3
    dielectric = 4


@dataclass
class _Part3DDataRequired(_PartDataRequired):
    domain_type: Union[DomainType, str]

    def __post_init__(self):
        if type(self.domain_type) == str:
            try:
                self.domain_type = DomainType[self.domain_type]
            except KeyError:
                raise ValueError(
                    f"{self.domain_type} is not a valid domain type! Valid values are "
                    f"{[domain.name for domain in DomainType]}"
                )
        elif type(self.domain_type) != DomainType:
            raise ValueError(
                f"{self.domain_type} is not a valid domain type! It must be a string or"
                " a DomainType Enum"
            )


@dataclass
class _Part3DDataDefaults(_PartDataDefaults):
    """
    :field fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
        that if the label used for the 3D part is the same as the freeCAD label, and
        that label is unique, None may be used here as a shortcut.
    """

    fc_name: Optional[str] = None
    serial_stp: Optional[str] = None  # This gets set on geometry build
    built_fc_name: Optional[str] = None  # This gets set on geometry build


@dataclass
class Part3DData(_Part3DDataRequired, _Part3DDataDefaults):
    """
    Create a 3D geometric part.


    :param str depo_mode: 'depo' or 'etch' defines the positive or negative mask for the
        deposition of a wire coating.
    :param float z_middle: The location for the "flare out" of the SAG directive.
    :param float t_in: The lateral distance from the 2D profile to the edge of the top bevel
        for the SAG directive.
    :param float t_out: The lateral distance from the 2D profile to the furthest "flare out"
        location for the SAG directive.
    :param int layer_num: The layer number used by the lithography directive. Lower numbers
        go down first, with higher numbers deposited last.
    :param list litho_base: The base partNames to use for the lithography directive.
        For multi-step lithography, the bases are just all merged,
        so there is no need to list this more than once.
    :param float mesh_max_size: The maximum allowable mesh size for this part, in microns.
    :param float mesh_min_size: The minimum allowable mesh size for this part, in microns.
    :param float mesh_growth_rate: The maximum allowable mesh growth rate for this part.
    :param tuple mesh_scale_vector: 3D list with scaling factors for the mesh in
        x, y, z direction.
    :param dict boundary_condition: One or more boundary conditions, if applicable, of
        the form of a type -> value mapping. For example, this could be {'voltage':1.0} or,
        more explicitly, {'voltage': {'type': 'dirichlet', 'value': 1.0,'unit': 'V'}}.
        Assumed by FEniCS solvers to be in the form {"voltage":1.0},
        and the value given is taken to be in meV.
    :param list subtract_list: A list of partNames that should be subtracted from the current
        part when forming the final 3D objects. This subtraction is
        carried out when boundary
        conditions are set.
    :param float ns: Volume charge density of a part, applicable to semiconductor and
        dielectric parts. The units for this are 1/cm^3.
    :param float phi_nl: The neutral level for interface traps, measured in units of eV above
        the valence band maximum (semiconductor only).
    :param float ds: Density of interface traps; units are 1/(cm^2*eV).
    """

    # def __init__(
    #     self,
    #     depo_mode=None,
    #     z_middle=None,
    #     t_in=None,
    #     t_out=None,
    #     layer_num=None,
    #     litho_base=None,
    #     mesh_max_size=None,
    #     mesh_min_size=None,
    #     mesh_growth_rate=None,
    #     mesh_scale_vector=None,
    #     boundary_condition=None,
    #     ns=None,
    #     phi_nl=None,
    #     ds=None,
    # ):

    #     # if domain_type not in ["semiconductor", "dielectric"] and ns is not None:
    #     #     raise ValueError(
    #     #         "Cannot set a volume charge density on a gate or virtual part."
    #     #     )

    #     # Input storage
    #     self.depo_mode = depo_mode
    #     self.z_middle = z_middle
    #     self.t_in = t_in
    #     self.t_out = t_out
    #     self.layer_num = layer_num
    #     self.litho_base = [] if litho_base is None else litho_base
    #     self.mesh_max_size = mesh_max_size
    #     self.mesh_min_size = mesh_min_size
    #     self.mesh_growth_rate = mesh_growth_rate
    #     self.mesh_scale_vector = mesh_scale_vector
    #     self.boundary_condition = boundary_condition
    #     self.ns = ns
    #     self.phi_nl = phi_nl
    #     self.ds = ds

    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = self.label + ".stp"
        write_deserialised(self.serial_stp, file_path)
        return file_path


@dataclass
class _ExtrudeDataRequired:
    """
    :field thickness: The total thickness
    :field z0: The starting z coordinate
    """

    thickness: float
    z0: float


@dataclass
class ExtrudeData(_ExtrudeDataRequired, Part3DData):
    pass


@dataclass
class _WireDataRequired:
    """
    :field thickness: The total thickness
    :field z0: The starting z coordinate
    """

    thickness: float
    z0: float


@dataclass
class WireData(_WireDataRequired, Part3DData):
    pass


@dataclass
class _WireShellDataRequired:
    """
    :param shell_verts: Vertices to use when rendering the coating
    :field target_wire: Target wire directive for coating
    :field thickness: Thickness of the coating
    """

    shell_verts: List
    target_wire: WireData
    thickness: float


@dataclass
class WireShellData(_WireShellDataRequired, Part3DData):
    pass


@dataclass
class _SAGDataRequired:
    """
    :field thickness: The total thickness
    :field z0: The starting z coordinate
    """

    thickness: float
    z0: float


@dataclass
class SAGData(_SAGDataRequired, Part3DData):
    pass


@dataclass
class _LithographyDataRequired:
    """
    :field thickness: The total thickness
    :field z0: The starting z coordinate
    """

    thickness: float
    z0: float


@dataclass
class LithographyData(_LithographyDataRequired, Part3DData):
    pass


@dataclass
class Shape3DData(Part3DData):
    pass
