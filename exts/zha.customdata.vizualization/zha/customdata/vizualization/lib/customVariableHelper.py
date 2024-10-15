import omni.ext
import omni.ui as ui

import omni.usd
import omni.kit.commands

from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import numpy as np


def get_custom_variables(prim):
    # Get all variables from the prim
    custom_variables = {}
    
    for attr in prim.GetAttributes():
        if attr.GetName().startswith("custom:"):
            value = attr.Get()

            type_name = attr.GetTypeName()
            
            try:
                if type_name == Sdf.ValueTypeNames.String:
                    custom_variables[attr.GetName()] = str(value)
                elif type_name == Sdf.ValueTypeNames.StringArray:
                    custom_variables[attr.GetName()] = [str(v) for v in value]
                elif type_name == Sdf.ValueTypeNames.Bool:
                    custom_variables[attr.GetName()] = bool(value)
                elif type_name == Sdf.ValueTypeNames.BoolArray:
                    custom_variables[attr.GetName()] = [bool(v) for v in value]
                else:
                    if np.array(value).size == 1 and len(np.array(value).shape) == 0:
                        custom_variables[attr.GetName()] = np.array([value])
                    else:
                        custom_variables[attr.GetName()] = np.array(value)
            except:
                print("Error getting custom variable value")
                continue
                
    return custom_variables


def get_applicable_variables(prim):
    if prim.IsA(UsdGeom.Mesh):
        mesh = UsdGeom.Mesh(prim)
        customVars = get_custom_variables(prim)
        print(customVars)
        for key, value in customVars.items():
            if len(value) == 1:
                print(f"Constant: {key} - {value}")
            if len(mesh.GetFaceVertexCountsAttr().Get()) == len(value):
                print(f"Uniform: {key} - {value}")
            if len(mesh.GetPointsAttr().Get()) == len(value):
                print(f"FaceVarying: {key} - {value}")
