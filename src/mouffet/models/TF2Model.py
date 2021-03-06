from abc import abstractmethod
from pathlib import Path

import tensorflow as tf
from tqdm import tqdm
import tensorflow.keras as keras
from mouffet.utils.common import print_warning

from .dlmodel import DLModel


class TF2Model(DLModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optimizer = None
        self.summary_writer = {}
        self.metrics = {}

    @tf.function
    def train_step(self, data, labels):
        self.basic_step(data, labels, self.STEP_TRAINING)

    @tf.function
    def validation_step(self, data, labels):
        self.basic_step(data, labels, self.STEP_VALIDATION)

    def basic_step(self, data, labels, step_type):
        training = step_type == self.STEP_VALIDATION
        if not training:
            with tf.GradientTape() as tape:
                predictions = self.model(data, training=True)
                loss = self.tf_loss(labels, predictions)
            gradients = tape.gradient(loss, self.model.trainable_variables)
            self.optimizer.apply_gradients(
                zip(gradients, self.model.trainable_variables)
            )
        else:
            predictions = self.model(data, training=False)
            loss = self.tf_loss(labels, predictions)

        self.metrics[step_type + "_loss"](loss)
        self.metrics[step_type + "_accuracy"](labels, predictions)

    @staticmethod
    @abstractmethod
    def tf_loss(y_true, y_pred):
        """This is the loss function.

        Args:
            y_true ([type]): [description]
            y_pred ([type]): [description]
        """
        raise NotImplementedError()

    @abstractmethod
    def init_metrics(self):
        """Inits the metrics used during model evaluation. Fills the metrics
        attribute which is a dict that should contain the following keys:

        - train_loss
        - train_accuracy
        - validation_loss
        - validation accuracy
        """
        raise NotImplementedError()

    @abstractmethod
    def init_samplers(self):
        raise NotImplementedError()

    @abstractmethod
    def init_optimizer(self):
        raise NotImplementedError()

    @abstractmethod
    def init_model(self):
        raise NotImplementedError()

    def init_training(self):
        """This is a function called at the beginning of the training step. In
        this function you should initialize your train and validation samplers,
        as well as the optimizer, loss and accuracy functions for training and
        validation.

        """
        self.opts.add_option("training", True)

        self.init_model()

        self.init_optimizer()

        self.init_metrics()

    def train(self, training_data, validation_data):

        self.init_training()

        print("Training model", self.opts.model_id)

        train_sampler, validation_sampler = self.init_samplers()

        from_epoch = self.opts.get("from_epoch", 0)
        #

        epoch_save_step = self.opts.get("epoch_save_step", None)

        # * Create logging writers
        self.create_writers()

        # tf.profiler.experimental.start(
        #     str(Path(self.opts["logs"]["log_dir"]) / self.opts.model_id)
        # )

        for epoch in range(from_epoch + 1, self.opts["max_epochs"] + 1):
            # * Reset the metrics at the start of the next epoch
            self.reset_states()

            self.run_step("train", training_data, epoch, train_sampler)
            self.run_step("validation", validation_data, epoch, validation_sampler)

            template = (
                "Epoch {}, Loss: {}, Accuracy: {},"
                " Validation Loss: {}, Validation Accuracy: {}"
            )
            print(
                template.format(
                    epoch,
                    self.metrics["train_loss"].result(),
                    self.metrics["train_accuracy"].result() * 100,
                    self.metrics["validation_loss"].result(),
                    self.metrics["validation_accuracy"].result() * 100,
                )
            )

            if epoch_save_step is not None and epoch % epoch_save_step == 0:
                self.save_model(self.opts.get_intermediate_path(epoch))
        # tf.profiler.experimental.stop()
        self.save_model()

    def create_writers(self):
        log_dir = Path(self.opts.logs["log_dir"]) / (
            self.opts.model_id + "_v" + str(self.opts.save_version)
        )

        # TODO: externalize logging directory
        train_log_dir = log_dir / "train"
        validation_log_dir = log_dir / "validation"
        self.summary_writer["train"] = tf.summary.create_file_writer(str(train_log_dir))
        self.summary_writer["validation"] = tf.summary.create_file_writer(
            str(validation_log_dir)
        )

    def reset_states(self):
        for x in ["train", "validation"]:
            self.metrics[x + "_loss"].reset_states()
            self.metrics[x + "_accuracy"].reset_states()

    def run_step(self, step_type, data, step, sampler):
        # i = 0
        # import skimage.io
        # import numpy as np
        # import librosa
        # from datetime import datetime

        # def scale_minmax(X, min=0.0, max=1.0):
        #     X_std = (X - X.min()) / (X.max() - X.min())
        #     X_scaled = X_std * (max - min) + min
        #     return X_scaled
        # filename = datetime.now().strftime("%Y%m%d") + "_{}.png"

        for data, labels in tqdm(
            sampler(self.get_raw_data(data), self.get_ground_truth(data))
        ):

            # mels = librosa.amplitude_to_db(np.abs(data[0]), ref=np.max)
            # # mels = np.log(data[0] + 1e-9)  # add small number to avoid log(0)

            # # min-max scale to fit inside 8-bit range
            # img = scale_minmax(mels, 0, 255).astype(np.uint8)
            # img = np.flip(img, axis=0)  # put low frequencies at the bottom in image
            # img = 255 - img  # invert. make black==more energy

            # # save as PNG
            # skimage.io.imsave(
            #     self.opts.model_dir / "../images" / filename.format(i), img
            # )

            # if i == 1:
            #     break
            # i += 1
            getattr(self, step_type + "_step")(data, labels)
        with self.summary_writer[step_type].as_default():
            tf.summary.scalar(
                "loss", self.metrics[step_type + "_loss"].result(), step=step
            )
            tf.summary.scalar(
                "accuracy", self.metrics[step_type + "_accuracy"].result(), step=step
            )

    def save_weights(self, path=None):
        if not path:
            path = str(self.opts.results_save_dir / self.opts.model_id)
        self.model.save_weights(path)

    def load_weights(self):
        # training = self.opts.get("training", True)
        # weight_opts = self.opts.get("use_weights", {})
        # if training and not weight_opts:
        #     print_warning(
        #         "Warning, no training weights found for the current model. Skipping."
        #     )
        #     return
        self.model.load_weights(self.opts.get_weights_path())

    @abstractmethod
    def predict(self, x):
        """This function calls the model to have a predictions

        Args:
            x (data): The input data to be classified

            NotImplementedError: No basic implementation is provided and it should therefore be
            provided in child classes
        """
        raise NotImplementedError()
