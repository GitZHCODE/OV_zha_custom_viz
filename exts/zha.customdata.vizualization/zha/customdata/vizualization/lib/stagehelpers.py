import os
import sys

import omni.ext
import omni.ui as ui
from omni.usd import Usd, UsdGeom, Sdf, Gf
from pxr import Vt

from pxr import Usd, UsdGeom
import numpy as np
import math

from typing import List, Dict, Tuple, Callable, Type


def find_prims_by_type(stage: Usd.Stage, prim_type: Type[Usd.Typed]) -> List[Usd.Prim]:
    return [x for x in stage.Traverse() if x.IsA(prim_type)]

def find_prims_by_type_root(stage: Usd.Stage, prim_type: Type[Usd.Typed], root: str ='/origin') -> List[Usd.Prim]:
    return [x for x in Usd.PrimRange(stage.GetPrimAtPath(root)) if x.IsA(prim_type)]

def select_all_children(root_path, stage, select=False):
    # Get the stage
    #stage = omni.usd.get_context().get_stage()
    
    # Get the root prim
    root_prim = stage.GetPrimAtPath(root_path)
    
    if not root_prim:
        print(f"No prim found at path: {root_path}")
        return
    
    # Collect all descendant prims
    descendants = get_all_descendants(root_prim)
    # Create a list of paths for all descendants
    paths_to_select = [str(p.GetPath()) for p in descendants]
    paths_to_select.append(str(root_prim.GetPath()))

    # Select the prims
    if select:
        omni.kit.commands.execute('SelectPrimsCommand',
            old_selected_paths=[],
            new_selected_paths=paths_to_select,
            expand_in_stage=True
        )

    print(f"Selected {len(paths_to_select)} children under {root_path}")
    return paths_to_select

def get_all_descendants(prim):
    descendants = []
    for child in prim.GetChildren():
        descendants.append(child)
        descendants.extend(get_all_descendants(child))
    return descendants



