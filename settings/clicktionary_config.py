import os


class config():
    def __init__(self):

        """
        User configuration for creating and updating
        the serrelab image database
        """
        self.db_schema_file = os.path.join('settings', 'db_schema.txt')
        self.relative_path_pointer = '/media/data_cifs/'

        # Path to search for images
        self.experiment_names = [
            'clicktionary',
        ]
        self.parent_experiments = [
            'ILSVRC12'
        ]
        self.label_names = [
            'animal_vehicle'
        ]
        self.image_paths = [
            None
        ]
        self.label_paths = [
            'animal_vehicle.txt'
        ]
        self.encoding = 'rgb'  # Need to automate this eventually...
        self.image_file_filter = '*.JPEG'
        self.image_key = 'synset'
        self.force_channels = 1

        self.child_dataset = None
        self.skip_label_order = True

    def __getitem__(self, name):
        return getattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)
