import omni.ext
import omni.ui as ui

import omni.kit.commands
from omni.ui import scene as sc

from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf, Vt
import numpy as np

import matplotlib.pyplot as plt
import matplotlib

from .lib import customVariableHelper as cvh
from .lib import colorramp as cr
from .lib import stagehelpers as sh
from .lib import graphviz as gv
from .lib import temphelpers as th

# object to handle the visualization, to receive the variables form the prim and assign them as colors
class PrimvizHandler:

    def __init__(self) -> None:
        
        self.parent_prim = None
        self.prims = None
        self.colors = None
        
        self.custom_variables = None
        
        self.current_varyingType = 0
        self.usable_custom_variables = []
        self.usable_indices = []
        
        self.variable_combobox = None

        self.variant_set_name = "data_color_visualization"
        
        self.cmap = plt.colormaps()[0]
        
        self.graphpaths = []        
        self.graphs = None
        
        self.gradient = None
        self.gradientpath = None
        self.get_cmap_preview()
    
    
    def get_cmap_preview(self):
        self.colormap_preview = gv.plot_gradient_sample(cmap_name=self.cmap)
        self.gradientpath = th.save_temp_image(self.colormap_preview, "gradient.png")
        return self.gradientpath
    
    
    def get_custom_variables(self):
        if self.prims is not None or len(self.prims) != 0:
            self.custom_variables = [cvh.get_custom_variables(prim) for prim in self.prims]
        else:
            self.custom_variables = None

        
    def get_prims_selected_path(self, model, select=False):
        roots = model.get_item_value()
        print("Root: ", roots)
        
        #select items under the root path
        selected_items = []
        stage = omni.usd.get_context().get_stage()
        
        for root in roots:
            paths = sh.select_all_children(root, stage, select)

            for path in paths:
                selected_items.append(stage.GetPrimAtPath(path))

        self.prims = selected_items
        self.parent_prim = stage.GetPrimAtPath(root)


    def get_usable_custom_variables(self, varying_type: int):
        usable = {}
        indices = {}
        
        self.usable_custom_variables = varying_type
        
        print(f"Selected Visualization type: {varying_type}")
        
        if self.prims is None or len(self.prims) == 0:
            return usable
        
        for index, prim in enumerate(self.prims):
            if prim.IsA(UsdGeom.Mesh):
                
                mesh = UsdGeom.Mesh(prim)  
                customVars = cvh.get_custom_variables(prim)
                
                if len(list(customVars.items())) != 0:
                    for key, value in list(customVars.items()):
                        if type(value) == np.ndarray:
                            
                            if value.size == 1 and varying_type == 0:
                                if key not in usable:
                                    usable[key] = []
                                    indices[key] = []
                                usable[key].append(value)
                                indices[key].append(index)
                                
                            elif len(np.array(mesh.GetFaceVertexCountsAttr().Get())) == value.size and varying_type == 1:
                                if key not in usable:
                                    usable[key] = []
                                    indices[key] = []
                                usable[key].append(value)
                                indices[key].append(index)
                                
                            elif len(np.array(mesh.GetPointsAttr().Get())) == value.size and varying_type == 2:
                                if key not in usable:
                                    usable[key] = []
                                    indices[key] = [] 
                                usable[key].append(value)
                                indices[key].append(index)
                                
                                
        self.set_names_combobox(list(usable.keys()))
        
        self.usable_custom_variables = usable
        self.usable_indices = indices

        return usable, indices


    def set_names_combobox(self, names):
        #first remove all children
        for child in self.variable_combobox.get_item_children():
            self.variable_combobox.remove_item(child)
        
        #set the names of the custom variables in the combobox       
        for name in names:
            self.variable_combobox.append_child_item(None, ui.SimpleStringModel(name))

    
    
    #### ----- Continue here with editing to not set shaders, but create variants ----- ####
    ## working test script at the end of this file - use to build implementation
    def assign_shader(self, type_index: int, attribute_index: int):
        if type_index == 0:
            self.assign_constant_shader(attribute_index, self.cmap)
        elif type_index == 1:
            self.assign_uniform_shader(attribute_index, self.cmap)
        elif type_index == 2:
            self.assign_vertex_shader(attribute_index, self.cmap)
        else:
            return None
    
    
    #####----- All assign functions working with vertex colors -----#####
    
    ##### working like a charme - just add colors as UI input #####
    def assign_constant_shader(self, attribute_index: int, cmap = "viridis"):

        if type(cmap) == str:
            cmap = plt.get_cmap(cmap)
        elif type(cmap) == matplotlib.colors.Colormap:
            cmap = cmap
            
        print(type(cmap))
        
        if self.prims is None or len(self.prims) == 0:
            return None
        
        attribute_name = list(self.usable_custom_variables.keys())[attribute_index]
        attributes = np.array(self.usable_custom_variables[attribute_name])
        
        # Test after here
        if type(attributes) != np.ndarray:
            return None
        
        current_usableIndex = 0
        remapped_values = (attributes - attributes.min()) / (attributes.max() - attributes.min())
        

        #create the variant set if it does not exist yet
        if self.parent_prim.GetVariantSets().HasVariantSet(self.variant_set_name):
            variant_set = self.parent_prim.GetVariantSets().GetVariantSet(self.variant_set_name)
        else: 
            variant_set = self.parent_prim.GetVariantSets().AddVariantSet(self.variant_set_name)
        
        
        #if the variant_set_name has a ":" in it take the part after the last ":"
        variant_name = attribute_name
        if ":" in variant_name:
            variant_name = variant_name.split(":")[-1]
        
        #check if the variant already exists, if not create it
        if variant_set.SetVariantSelection(variant_name):
            variant_set.SetVariantSelection(variant_name)
        else:
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
        
        with variant_set.GetVariantEditContext():
            for index, prim in enumerate(self.prims):
                
                if prim != None and prim.IsA(UsdGeom.Mesh):
                    value = remapped_values[current_usableIndex]
                    sample_color = cmap(value)
                    sample_color = np.squeeze(np.array(sample_color))[:3]

                    mesh = UsdGeom.Mesh(prim)
                    color_primvar = mesh.GetDisplayColorPrimvar()
                    
                    UsdShade.MaterialBindingAPI(mesh).UnbindAllBindings()

                    if not color_primvar:
                        color_primvar = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("displayColor", Vt.Vec3fArray)
                        color_primvar.SetInterpolation("constant")
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(sample_color))
                    else:
                        #set the color values
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(sample_color))
                        color_primvar.SetInterpolation("constant")
                    
                    current_usableIndex += 1
                else:
                    continue
        

        self.graphpaths.clear()
        
        donutChart = gv.plot_donut_chart_transparent(data=attributes, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(donutChart, "graph1.png"))
        
        valueDisGraph = gv.plot_value_distribution_transparent(data=attributes, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(valueDisGraph, "graph2.png"))
        
        
        self.graphs[0].set_style({"image_url": self.graphpaths[0]})
        self.graphs[1].set_style({"image_url": self.graphpaths[1]})

    ##### working like a charme - just add colors as UI input #####
    def assign_uniform_shader(self, attribute_index: int, cmap = "cividis"):
        
        if type(cmap) == str:
            cmap = plt.get_cmap(cmap)
        elif type(cmap) == plt.colors.ListedColormap:
            cmap = cmap
        
        if self.prims is None or len(self.prims) == 0:
            return None
        
        attribute_name = list(self.usable_custom_variables.keys())[attribute_index]
        attributes = self.usable_custom_variables[attribute_name]
        
        #convert the list of arrays to a single array
        attributes_flattened = np.array([item for sublist in attributes for item in sublist])
        attributes_np = [np.array(item) for item in attributes]
        
        if type(attributes_flattened) != np.ndarray:
            return None
        
        current_usableIndex = 0


        ## adding the variant set

        #create the variant set if it does not exist yet
        if self.parent_prim.GetVariantSets().HasVariantSet(self.variant_set_name):
            variant_set = self.parent_prim.GetVariantSets().GetVariantSet(self.variant_set_name)
        else: 
            variant_set = self.parent_prim.GetVariantSets().AddVariantSet(self.variant_set_name)
        
        #if the variant_set_name has a ":" in it take the part after the last ":"
        variant_name = attribute_name
        if ":" in variant_name:
            variant_name = variant_name.split(":")[-1]
        
        #check if the variant already exists, if not create it
        if variant_set.SetVariantSelection(variant_name):
            variant_set.SetVariantSelection(variant_name)
        else:
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
        
        
        with variant_set.GetVariantEditContext():
            for index, prim in enumerate(self.prims):
                if prim != None and prim.IsA(UsdGeom.Mesh):
                    #get the face values form the according attribute
                    values = attributes_np[current_usableIndex]
                    #renormalize the values in the range of attributes_flattened
                    remapped_values = (values - attributes_flattened.min()) / (attributes_flattened.max() - attributes_flattened.min())
                    
                    colors = cmap(remapped_values)[:, :3]

                    #make displayColor primvar
                    mesh = UsdGeom.Mesh(prim)
                    color_primvar = mesh.GetDisplayColorPrimvar()
                    
                    UsdShade.MaterialBindingAPI(mesh).UnbindAllBindings()

                    if not color_primvar:
                        color_primvar = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("displayColor", Vt.Vec3fArray)
                        color_primvar.SetInterpolation("uniform")
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(colors))
                    else:
                        #set the color values
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(colors))
                        color_primvar.SetInterpolation("uniform")

                    current_usableIndex += 1
                    
                else:
                    continue
            
        self.graphpaths.clear()
        
        donutChart = gv.plot_donut_chart_transparent(data=attributes_flattened, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(donutChart, "graph1.png"))
        
        valueDisGraph = gv.plot_value_distribution_transparent(data=attributes_flattened, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(valueDisGraph, "graph2.png"))
        
        
        self.graphs[0].set_style({"image_url": self.graphpaths[0]})
        self.graphs[1].set_style({"image_url": self.graphpaths[1]})

    ##### working like a charme - just add colors as UI input #####
    def assign_vertex_shader(self, attribute_index: int, cmap = "plasma"):
        
        if type(cmap) == str:
            cmap = plt.get_cmap(cmap)
        elif type(cmap) == plt.colors.ListedColormap:
            cmap = cmap
        
        if self.prims is None or len(self.prims) == 0:
            return None
        
        attribute_name = list(self.usable_custom_variables.keys())[attribute_index]
        attributes = self.usable_custom_variables[attribute_name]
        
        #convert the list of arrays to a single array
        attributes_flattened = np.array([item for sublist in attributes for item in sublist])
        attributes_np = [np.array(item) for item in attributes]
        
        if type(attributes_flattened) != np.ndarray:
            return None
        
        current_usableIndex = 0

        ## adding the variant set

        #create the variant set if it does not exist yet
        if self.parent_prim.GetVariantSets().HasVariantSet(self.variant_set_name):
            variant_set = self.parent_prim.GetVariantSets().GetVariantSet(self.variant_set_name)
        else: 
            variant_set = self.parent_prim.GetVariantSets().AddVariantSet(self.variant_set_name)
        
        #if the variant_set_name has a ":" in it take the part after the last ":"
        variant_name = attribute_name
        if ":" in variant_name:
            variant_name = variant_name.split(":")[-1]
        
        #check if the variant already exists, if not create it
        if variant_set.SetVariantSelection(variant_name):
            variant_set.SetVariantSelection(variant_name)
        else:
            variant_set.AddVariant(variant_name)
            variant_set.SetVariantSelection(variant_name)
        
        
        with variant_set.GetVariantEditContext():
            for index, prim in enumerate(self.prims):
                if prim != None and prim.IsA(UsdGeom.Mesh):
                    #get the face values form the according attribute
                    values = attributes_np[current_usableIndex]
                    #renormalize the values in the range of attributes_flattened
                    remapped_values = (values - attributes_flattened.min()) / (attributes_flattened.max() - attributes_flattened.min())
                    
                    colors = cmap(remapped_values)[:, :3]

                    #get the mesh
                    mesh = UsdGeom.Mesh(prim)
                    color_primvar = mesh.GetDisplayColorPrimvar()
                    

                    UsdShade.MaterialBindingAPI(mesh).UnbindAllBindings()

                    if not color_primvar:
                        color_primvar = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar("displayColor", Vt.Vec3fArray)
                        color_primvar.SetInterpolation("vertex")
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(colors))
                    else:
                        #set the color values
                        color_primvar.Set(Vt.Vec3fArray.FromNumpy(colors))
                        color_primvar.SetInterpolation("vertex")
                        
                        
                    current_usableIndex += 1
                else:
                    continue
            
        
        self.graphpaths.clear()
        
        donutChart = gv.plot_donut_chart_transparent(data=attributes_flattened, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(donutChart, "graph1.png"))
        
        valueDisGraph = gv.plot_value_distribution_transparent(data=attributes_flattened, cmap=cmap)
        self.graphpaths.append(th.save_temp_image(valueDisGraph, "graph2.png"))
        
        
        self.graphs[0].set_style({"image_url": self.graphpaths[0]})
        self.graphs[1].set_style({"image_url": self.graphpaths[1]})


    #####----- All assign functions working with vertex colors -----#####
