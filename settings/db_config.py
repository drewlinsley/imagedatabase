import os


class config():
    def __init__(self):

        """
        User configuration for creating and updating
        the serrelab image database
        """
        self.db_schema_file = os.path.join('settings', 'db_schema.txt')

        # Path to search for images
        self.experiment_name = 'ILSVRC12'
        self.image_paths = [
            '/media/data_cifs/clicktionary/webapp_data/lmdb_trains',
            '/media/data_cifs/clicktionary/webapp_data/lmdb_trains'
        ]
        self.image_key = 'synset'
        self.image_file_filter = '*.JPEG'

    def __getitem__(self, name):
        return getattr(self, name)

    def __contains__(self, name):
        return hasattr(self, name)
