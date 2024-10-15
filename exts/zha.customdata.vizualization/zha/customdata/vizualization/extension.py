import omni.ext
import omni.ui as ui

from omni.kit.viewport.utility import get_active_viewport_window
import zha.customdata.vizualization.object_info_model as om
import zha.customdata.vizualization.mesh_viz as mv
from .lib.customVariableHelper import *

import omni.usd
import omni.kit.commands

from pxr import Usd, UsdGeom, UsdShade, Sdf, Gf, Tf
import numpy as np

import matplotlib.pyplot as plt

import tempfile
from .lib import stagehelpers as sh
from .lib import graphviz as gv

import omni.client




# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class ZhaCustomdataVizualizationExtension(omni.ext.IExt):
    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def __init__(self):
        self.VizHandler = mv.PrimvizHandler()
        
        self._dataTypeIndex = 0
        self._datatypeDict = {0: "By Mesh", 1: "By Faces", 2: "By Vertices"}
        
        self._window = ui.Window("Prim Data Visualization", width=300, height=400)
        
        self.graphs = []	

    
    
    def update_prims_selected_path(self):
            self.VizHandler.get_prims_selected_path(self._model)
            self.VizHandler.get_usable_custom_variables(self._dataTypeIndex)
            
    
    def on_startup(self, ext_id):
        print("[zha.customdata.vizualization] zha customdata vizualization startup")
        

        with self._window.frame:
            with ui.VStack():

                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    desc = ui.Label("Drop the parent of the meshes to analyze below")

                ui.Spacer(height=10)

                with ui.ScrollingFrame(
                    height=30,
                    horizontal_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_OFF,
                    vertical_scrollbar_policy=ui.ScrollBarPolicy.SCROLLBAR_ALWAYS_ON,
                    style_type_name_override="TreeView",):
                    
                    self._model = om.Model(*["---[Drop Mesh Visualization Parent here]---"])
                    self._model.changeFunction1 = lambda: self.update_prims_selected_path()
                    self._treeview = ui.TreeView(self._model, root_visible=False, style={"margin": 0.5})

                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    self.type_varying = ui.ComboBox(self._dataTypeIndex ,"By Mesh", "By Faces", "By Vertices")
                    self.type_varying.model.add_item_changed_fn(self.on_visMode_changed)
                    self.type_varying.model.add_item_changed_fn(self.get_usable_custom_variables_wrapper)
                
                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    self.variable_combobox = ui.ComboBox(0, " ")
                    self.VizHandler.variable_combobox = self.variable_combobox.model
                
                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    ui.Label("Color Map")
                    
                with ui.VStack(height=20):
                        self.gradient_image = ui.Image(style={'image_url':'data/Blank_512.png'}, 
                        fill_policy=ui.FillPolicy.STRETCH, alignment=ui.Alignment.CENTER)
                        self.gradient_image.set_style({"image_url": self.VizHandler.gradientpath})
                    
                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    self.colormaps = ui.ComboBox(self._dataTypeIndex)
                    for cmap_name in plt.colormaps():
                        self.colormaps.model.append_child_item(None, ui.SimpleStringModel(cmap_name))
                        
                    self.colormaps.model.add_item_changed_fn(
                        lambda model, y: setattr(self.VizHandler, 'cmap', plt.colormaps()[model.get_item_value_model().as_int])
                    )
                    # continue here
                    self.colormaps.model.add_item_changed_fn(
                        lambda model, y: self.gradient_image.set_style({"image_url": self.VizHandler.get_cmap_preview()})
                    )
                
                
                
                with ui.VStack(height=20):
                    ui.Spacer(height=10)
                    self.shaderButton = ui.Button("Create shaders", 
                        clicked_fn=lambda: 
                        self.VizHandler.assign_shader(self.type_varying.model.get_item_value_model().as_int, 
                        self.variable_combobox.model.get_item_value_model().as_int, 
                        ))
                
                with ui.VStack(height=20):
                    self.updateButton = ui.Button("Update",
                    clicked_fn=lambda: self.update_prims_selected_path())


                ui.Spacer(height=10)
                self.graphs.append(ui.Image(style={'image_url':'data/Blank_512.png'}, 
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, alignment=ui.Alignment.CENTER))
                self.graphs.append(ui.Image(style={'image_url':'data/Blank_512.png'}, 
                        fill_policy=ui.FillPolicy.PRESERVE_ASPECT_FIT, alignment=ui.Alignment.CENTER))

        self.VizHandler.graphs = self.graphs
        
        # self.colormap_preview = gv.plot_gradient_sample(cmap_name=plt.colormaps()[self.colormaps.model.get_item_value_model().as_int])
    
                
    def on_visMode_changed(self, model, y):
        self._dataTypeIndex = model.get_item_value_model().as_int
    
    # make sure to also call when new parent is dropped in the treeview
    def get_usable_custom_variables_wrapper(self, model, y):
        self.VizHandler.get_usable_custom_variables(self._dataTypeIndex)
        

    def on_shutdown(self):
        print("[zha.customdata.vizualization] zha customdata vizualization shutdown")


# video on gradient addon
# https://www.youtube.com/watch?v=dNLFpVhBrGs

# side on info widget
# https://github.com/NVIDIA-Omniverse/kit-extension-sample-ui-scene/blob/main/exts/omni.example.ui_scene.widget_info/Tutorial/object.info.widget.tutorial.md