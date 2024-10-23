from omni.kit.window.file_exporter import get_file_exporter
from typing import List
from PIL import Image

import numpy as np
import pandas as pd

import logging


class ExportHandler:
    def __init__(self):
        self.file_exporter = get_file_exporter()
        self.show_window = self.file_exporter.show_window
        
        self.imagepaths = []
        self.data = None

    def export_images(self, imagepaths: List[str]) -> None:
        self.imagepaths = imagepaths
        self.show_window(
                        title="Export Graphs",
                        export_button_label="Save",
                        export_handler=self.export_png_handler,
                        file_extension_types=[("*.png", "PNG"), ("*.jpeg", "JPEG")],
        )
    
    def export_png_handler(self, filename: str, dirname: str, extension: str = "", selections: List[str] = []):
        logging.warning("Saving image.")
        #save the images
        for i, imagepath in enumerate(self.imagepaths):
            image = Image.open(imagepath)
            # if extension is jpeg convert from RGBA to RGB
            if extension == ".jpeg":
                image = image.convert("RGB")
                
            image.save(f"{dirname}/{filename}_{i}{extension}")
            image.close()
    
    
    def export_csv(self, data: np.ndarray):
        logging.warning("Saving csv.")
        self.data = data.flatten()
        self.show_window(
            title="Export CSV",
            export_button_label="Export",
            export_handler=self.export_csv_handler,
            file_extension_types=[("*.csv", "CSV")],
        )

    def export_csv_handler(self, filename: str, dirname: str, extension: str = "", selections: List[str] = []):
        #save the data as csv
        df = pd.DataFrame(self.data)
        df.to_csv(f"{dirname}/{filename}{extension}")
