from ..options import DatabaseOptions
from ..utils import file_utils
from .dataset import Dataset
from .split import random_split


class Database(DatabaseOptions):

    DATASET = Dataset

    SPLIT_FUNCS = {}

    def __init__(self, opts, updated_opts=None):
        super().__init__(opts, updated_opts)
        self._paths = {}

    @property
    def paths(self):
        if not self._paths:
            self._paths = self.get_paths()
        return self._paths

    def get_paths(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        paths = {}
        root_dir = self.root_dir

        # subfolders = self.get_subfolders(database)

        paths["root"] = root_dir
        paths["data"] = {"default": self.data_dir}
        paths["tags"] = {"default": self.tags_dir}
        paths["dest"] = {"default": self.dest_dir / self.name}
        paths["file_list"] = {}
        paths["save_dests"] = {}

        for db_type in self.db_types:

            by_type = self.get("data_by_type", False)
            if by_type:
                db_type_dir = file_utils.get_full_path(
                    self.opts[db_type + "_dir"], root_dir
                )
            else:
                db_type_dir = root_dir
            paths[db_type + "_dir"] = db_type_dir
            paths["data"][db_type] = file_utils.get_full_path(
                paths["data"]["default"], db_type_dir
            )
            paths["tags"][db_type] = file_utils.get_full_path(
                paths["tags"]["default"], db_type_dir
            )
            dest_dir = file_utils.get_full_path(paths["dest"]["default"], db_type_dir)
            paths["dest"][db_type] = dest_dir
            paths["file_list"][db_type] = self.get(
                db_type + "_file_list_path", dest_dir / (db_type + "_file_list.csv")
            )
        return paths

    def check_file_lists(self, db_types=None):
        file_lists = {}
        msg = "Checking file lists for database {0}... ".format(self["name"])
        if db_types is None:
            file_list_paths = self.paths["file_list"].values()
        else:
            file_list_paths = [self.paths["file_list"][db_type] for db_type in db_types]
        file_lists_exist = all([path.exists() for path in file_list_paths])
        # * Check if file lists are missing or need to be regenerated
        if not file_lists_exist or self.generate_file_lists:
            print(msg + "Generating file lists...")
            file_lists = {}
            # * Check if we have a dedicated function to split the original data
            split_opts = self.get("split", None)
            if split_opts:
                file_lists = self.split()
            else:
                file_lists = self.get_data_file_lists()
            # * Save results
            for db_type, file_list in file_lists.items():
                file_utils.save_file_list(db_type, file_list, self.paths)
        else:
            # * Load files
            print(msg + "Found all file lists. Now loading...")
            file_lists = file_utils.load_file_lists(self.paths, db_types)
        return file_lists

    def get_data_file_lists(self, db_types=None):
        res = {}
        db_types = db_types or self.db_types
        for db_type in db_types:
            res[db_type] = file_utils.list_files(
                self.paths["data"][db_type], self.data_extensions, self.recursive
            )
        return res

    def split(self):
        """Splits files into subsets.
        Splitting is done from the training dataset. This dataset can then be split into
        training and validation and optionally test dataset.
        By default, will split the training dataset into 80% training and 20% validation.
        If a proportion is specified for the test dataset, this proportion will be set aside first,
        and the training and validation will be split from the remainder.
        If not proportion is specified for the test dataset but the database includes a test dataset
        (as specified with the db_types option), the file list will be generated by listing files
        from that directory

        Args:
            paths (list): list of all paths generated by the data_handler
            database (DatabaseOptions): Options relative to the database to split

            ValueError: if the path to the training dataset is not found
            ValueError: If no splitting options - described by the split option - is found

        Returns:
            dict: Dict containing lists for each dataset type
        """
        data_path = self.paths["data"]["training"]
        if not data_path.exists():
            raise ValueError(
                (
                    "Data path {} does not exist. Please provide a valid data folder "
                    + "to split into test, training and"
                    + "validation subsets"
                ).format(data_path)
            )
        split_opts = self.get("split", None)
        if not split_opts:
            raise ValueError("Split option must be provided for splitting")
        split_func = self.SPLIT_FUNCS.get(self.name, random_split)
        split_props = []
        # * Make test split optional
        test_split = split_opts.get("test", 0)
        if test_split:
            split_props.append(test_split)
        val_split = split_opts.get("validation", 0.2)
        split_props.append(val_split)
        splits = split_func(data_path, split_props, self.data_extensions)
        res = {}
        idx = 0
        if test_split:
            res["test"] = splits[idx]
            idx += 1
        elif "test" in self.db_types:
            res.update(self.get_data_file_lists(db_types=["test"]))
        res["validation"] = splits[idx]
        res["training"] = splits[idx + 1]

        print([(k + " " + str(len(v))) for k, v in res.items()])
        return res

    def check_dataset(self, db_types=None):
        """_summary_

        Args:
            db_types (_type_, optional): _description_. Defaults to None.
        """
        file_lists = self.check_file_lists(db_types)
        for db_type, file_list in file_lists.items():
            if db_types and db_type in db_types:
                print("Checking database:", self["name"], "with type", db_type)
                # * Overwrite if generate_file_lists is true as file lists will be recreated
                overwrite = self.overwrite or self.generate_file_lists
                dataset = self.DATASET(
                    database=self,
                    db_type=db_type,
                )
                if not dataset.exists() or overwrite:
                    dataset.generate(file_list, overwrite)

    def load_dataset(
        self,
        db_type,
        load_opts,
    ):
        dataset = self.DATASET(
            database=self,
            db_type=db_type,
        )
        dataset.load(load_opts)
        return dataset
