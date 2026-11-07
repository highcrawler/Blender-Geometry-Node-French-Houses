"""Minimal reusable WALL_PLAIN infill definition; independent of Blender and Godot."""
from dataclasses import dataclass

TYPE_ID = 'WALL_PLAIN'
# Local u=(world +Y), v=(world +Z), n=(world +X); positive determinant.
AXES = {'u_horizontal': (0, 1, 0), 'v_vertical': (0, 0, 1), 'n_outward': (1, 0, 0)}


@dataclass(frozen=True)
class WallPlain:
    """One definition reused for any positive-width bay of this test wall."""
    height: float
    thickness: float
    infill_material: str = '09I_A_clay_constant'

    def geometry(self, width: float, cap_left: bool = True, cap_right: bool = True):
        if not (width > 0 and self.height > 0 and self.thickness > 0):
            raise ValueError('positive width, height and thickness required')
        half = self.thickness / 2
        vertices = [(u, v, n) for n in (-half, half) for v in (0., self.height) for u in (0., width)]
        faces = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3)]
        if cap_left:
            faces.append((0, 4, 6, 2))
        if cap_right:
            faces.append((1, 3, 7, 5))
        return vertices, faces

    def contract(self, module_id: str, width: float, world_mount, mesh_name: str,
                 cap_left: bool, cap_right: bool):
        """Assembly metadata. Coordinates are module-local; world_mount is the pivot."""
        return {'id': module_id, 'type': TYPE_ID, 'width_m': width,
                'height_m': self.height, 'thickness_m': self.thickness,
                'local_origin': [0, 0, 0], 'world_mount': list(world_mount),
                'axes_world': AXES,
                'connectors_local': {
                    'left': [[0, 0, 0], [0, self.height, 0]],
                    'right': [[width, 0, 0], [width, self.height, 0]],
                    'lower_edge': [[0, 0, 0], [width, 0, 0]],
                    'upper_edge': [[0, self.height, 0], [width, self.height, 0]]},
                'materials': {'infill': self.infill_material},
                'owned_meshes': [mesh_name],
                'assembled_cap_left': cap_left, 'assembled_cap_right': cap_right}
