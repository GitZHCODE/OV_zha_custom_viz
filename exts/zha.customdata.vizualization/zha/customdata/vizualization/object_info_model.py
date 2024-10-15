from omni.ui import scene as sc
import omni.usd
import omni.ui as ui



class Item(ui.AbstractItem):
    """Single item of the model"""

    def __init__(self, text):
        super().__init__()
        self.name_model = ui.SimpleStringModel(text)

    def __repr__(self):
        return self.name_model.as_string
    
    def rename(self, text):
        self.name_model.as_string = text


class Model(ui.AbstractItemModel):
    def __init__(self, *args):
        super().__init__()
        self._children = [Item(t) for t in args]
        # self._label.alignment = ui.Alignment.CENTER
        self.changeFunction1 = None
        #self.changeFunction2 = None

    def get_item_children(self, item):
        if item is not None:
            return []

        return self._children

    def get_item_value_model_count(self, item):
        return 1

    def get_item_value_model(self, item, column_id):
        return item.name_model

    def get_drag_mime_data(self, item):
        """Returns data for be able to drop this item somewhere"""
        return item.name_model.as_string

    def drop_accepted(self, target_item, source):
        """Return true to accept the current drop"""
        # Accept anything
        return True

    def drop(self, target_item, source):
        """Called when the user releases the mouse"""
        # Change text on the label
        target_item.rename(source)
        self.changeFunction1()
        #self.changeFunction2()
        
        return True
        
    def get_item_value(self):
        return [item.name_model.as_string for item in self._children]