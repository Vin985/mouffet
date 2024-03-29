import ast
from pathlib import Path
import pandas as pd
from . import common_utils

MODELS_STATS_FILE_NAME = "models_stats.csv"


def get_option(x, opt_name):
    return ast.literal_eval(x).get(opt_name, "")


def load_options(opts, updates=None, model_id=None):
    updates = updates or {}
    new = ast.literal_eval(opts)
    new.update(updates)
    if model_id is not None:
        new["model_id"] = model_id
    return new


# def load_model_options(opts, updates={}, model_id=None):
#     model_opt = ast.literal_eval(opts)
#     model_opt.update(updates)
#     if model_id is not None:
#         model_opt["model_id"] = model_id
#     return model_opt


# def get_models_conf(config):
#     """Get configuration from multiple models based on model list saved at training

#     Args:
#         config (_type_): _description_

#     Returns:
#         _type_: _description_
#     """
#     # * Get reference
#     models = config.get("models", [])
#     append = config.get("add_models_from_list", False)
#     if not models or append:
#         models_dir = config.get("models_list_dir")
#         models_stats_path = Path(models_dir) / MODELS_STATS_FILE_NAME
#         models_stats = None
#         if models_stats_path.exists():
#             models_stats = pd.read_csv(models_stats_path).drop_duplicates(
#                 "opts", keep="last"
#             )
#         if models_stats is not None:
#             model_ids = config.get("model_ids", [])
#             if model_ids:
#                 models_stats = models_stats.loc[models_stats.model_id.isin(model_ids)]
#             models += [load_options(row.opts) for row in models_stats.itertuples()]
#             config["models"] = models

#     return config


def get_models_conf(config, updates=None):
    """Get configuration from multiple models based on model list saved at training

    Args:
        config (_type_): _description_

    Returns:
        _type_: _description_
    """
    # * Get reference
    models = config.get("models", [])
    append = config.get("add_models_from_list", False)
    if not models or append:
        models_dir = config.get("models_list_dir")
        models_stats_path = Path(models_dir) / MODELS_STATS_FILE_NAME
        models_stats = None
        if models_stats_path.exists():
            models_stats = pd.read_csv(models_stats_path).drop_duplicates(
                "opts", keep="last"
            )
            if models_stats is not None:
                list_opts = config.get("models_list_options", {})
                if updates:
                    list_opts = common_utils.deep_dict_update(
                        list_opts, updates, copy=True
                    )
                model_ids = config.get("model_ids", [])
                if model_ids:
                    models_stats = models_stats.loc[
                        models_stats.model_id.isin(model_ids)
                    ]
                models += [
                    load_options(row.opts, list_opts, row.model_id)
                    for row in models_stats.itertuples()
                ]
                config["models"] = models
            else:
                common_utils.print_warning("Model list file is empty")
        else:
            common_utils.print_warning("Path to model list file not found.")

    return config
