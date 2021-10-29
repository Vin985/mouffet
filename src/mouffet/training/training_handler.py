import copy
import time
import traceback
from datetime import datetime

import pandas as pd

from ..data.data_handler import DataHandler
from ..options.model_options import ModelOptions
from ..utils import common as common_utils
from ..utils import file as file_utils
from ..utils.model_handler import ModelHandler


class TrainingHandler(ModelHandler):

    MODELS_STATS_FILE_NAME = "models_stats.csv"

    DB_TYPES = [
        DataHandler.DB_TYPE_TRAINING,
        DataHandler.DB_TYPE_VALIDATION,
    ]

    def expand_training_scenarios(self):
        scenarios = []
        if "scenarios" in self.opts:
            clean = dict(self.opts)
            scens = clean.pop("scenarios")
            for scenario in scens:
                for opts in common_utils.expand_options_dict(scenario):
                    res = dict(clean)
                    res = common_utils.deep_dict_update(res, opts, copy=True)
                    scenarios.append(res)
        else:
            scenarios.append(dict(self.opts))
        return scenarios

    def load_scenarios(self):
        return self.expand_training_scenarios()

    def get_scenario_databases_options(self, scenario):
        db_opts = []
        opts_update = scenario.get("databases_options", {})
        databases = scenario.get("databases")
        if not isinstance(databases, list):
            databases = [databases]
        for db_name in databases:
            db_opt = self.data_handler.update_database(opts_update, db_name)
            if db_opt:
                db_opts.append(db_opt)
        return db_opts

    def is_already_trained(self, scenario, models_stats, model_opts):
        if model_opts.get("skip_trained", False):
            tmp = models_stats.loc[
                models_stats.opts == str(scenario)  # pylint: disable=no-member
            ]
            if not tmp.empty:
                return True
        return False

    def train_scenario(self, scenario):
        try:
            scenario_info = {}
            start = time.time()
            models_stats = None
            common_utils.print_title(
                "Training scenario with options: {}".format(scenario)
            )
            model_opts = ModelOptions(copy.deepcopy(scenario))

            # * Load model stats database
            models_stats_path = model_opts.model_dir / self.MODELS_STATS_FILE_NAME
            if models_stats_path.exists():
                models_stats = pd.read_csv(models_stats_path)
            # * Check if model has already been trained
            if models_stats is not None and self.is_already_trained(
                scenario, models_stats, model_opts
            ):
                common_utils.print_info(
                    "Training for the model has already been completed and resume_training is True. Skipping scenario"
                )
                return

            # * Check datasets
            databases = self.get_scenario_databases_options(scenario)
            self.data_handler.check_datasets(
                databases=databases, db_types=self.DB_TYPES
            )
            # *  Get model instance
            model = self.get_model_instance(model_opts)
            # * Prepare data for training (e.g. preprocessing)
            data = [
                model.prepare_data(
                    self.data_handler.load_datasets(db_type, databases=databases)
                )
                for db_type in self.DB_TYPES
            ]
            # * Save databases options for training
            model.save_options("databases.yaml", databases)

            train_start = time.time()
            # * Perform training
            train_stats = model.train(*data)
            end = time.time()

            # * Save model training information

            scenario_info["date"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            scenario_info["global_duration"] = round(end - start, 2)
            scenario_info["training_duration"] = round(end - train_start, 2)
            scenario_info["n_epochs"] = scenario["n_epochs"]
            scenario_info["model_id"] = model_opts.model_id
            scenario_info["n_parameters"] = model.n_parameters
            scenario_info["opts"] = str(scenario)
            scenario_info.update(train_stats)

            df = pd.DataFrame([scenario_info])
            if models_stats is not None:
                models_stats = pd.concat([models_stats, df])
            else:
                models_stats = df
            file_utils.ensure_path_exists(models_stats_path, is_file=True)
            models_stats.to_csv(models_stats_path, index=False)

        except Exception:
            print(traceback.format_exc())
            common_utils.print_error(
                "Error training the model for scenario {}".format(scenario)
            )

    def train(self):
        if not self.data_handler:
            raise AttributeError(
                "An instance of class DataHandler must be provided in data_handler"
                + "attribute or at class initialisation"
            )
        for scenario in self.scenarios:
            self.train_scenario(scenario)
