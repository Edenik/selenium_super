import os
import glob
import shutil

class FolderUtils():
    def check_folder(self, path):
        return os.path.isdir(path)

    # Create directory if it doesn't exist to save files
    def create_folder(self, path):
        # If folder doesn't exist, then create it.
        if not self.check_folder(path):
            os.makedirs(path)

    def find_empty_dirs(self, path):
        for dirpath, dirs, files in os.walk(path):
            if not dirs and not files:
                yield dirpath

    def remove_empty_dirs(self, path):
        empty_dirs = self.find_empty_dirs(path)
        for directory in empty_dirs:
            os.rmdir(directory)

    def get_all_file_names(self, path, clean_text=None, clean_path=False, required_text=None, declined_text=None, name_parser=None):
        files = glob.glob(f"{path}*")
        if clean_text is None:
            return files
        else:
            clean_name_files = []
            for file in files:
                name = file
                has_required_text = (required_text is not None and required_text in file) or required_text is None
                has_declined_text = (declined_text is not None and declined_text in file) or declined_text is None
                if clean_text is not None:
                    for text_to_clean in clean_text:
                        name = name.replace(text_to_clean, '')
                if clean_path is True:
                    name = name.replace(path[0:-1], '').replace('\\', '')
                if name_parser is not None:
                    name = name_parser(name)
                if has_required_text and not has_declined_text:
                    clean_name_files.append(name)
            return clean_name_files

    def get_all_file_names_contains(self, path, required_text=None):
        files = glob.glob(f"{path}*")
    
        clean_name_files = []
        for file in files:
            name = file
            has_required_text = (required_text is not None and required_text in file) or (required_text is None)
            if has_required_text:
                clean_name_files.append(name)
        return clean_name_files

    def move_files_from_folder(self, source_folder, destination_folder):
        # fetch all files
        for file_name in os.listdir(source_folder):
            # construct full file path
            source = source_folder + file_name
            destination = destination_folder + file_name
            # move only files
            if os.path.isfile(source):
                shutil.move(source, destination)
                print('Moved:', file_name)
                
    def get_base_paths(self, base_path, folder_name, folder_path=os.path.realpath(__file__)):
        base_path = os.path.join(base_path,  f"../db/{folder_name}/")
        base_media_path = os.path.join(base_path,  f"../db/{folder_name}/media/")
        base_data_path = os.path.join(base_path,  f"../db/{folder_name}/data/")
        self.create_folder(base_path)
        self.create_folder(base_media_path)
        self.create_folder(base_data_path)
        folder_path = os.path.join(os.path.dirname(folder_path)) + '/'
        return base_path, base_media_path, base_data_path, folder_path