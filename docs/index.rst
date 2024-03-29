********
Mouffet
********

Mouffet is a framework the provides a strong and flexible structure for training and evaluating
models for reproducible science.

A common problem with developping models is that it is generally an iterative problem. To achieve
the desired results, several models are usually created and evaluated, with different settings each.
Keeping track of which model used which settings can quickly become a problem. If several methods
of evaluation are also used, this can soon become problematic.

With the multiplication of model creation tools, each with their own interface, it has also become
more and more complicated to compare different models.

Finally, often in science only the final results are reported, and not always in a
proper manner. This can lead to results that cannot be easily reproduced and thus to bad science.

With mouffet, the goal is to define some core concepts surrounding model creation and evaluation
and provide an interface to these concepts. Reference classes are provided and should be subclassed
to ensure a unified entry into model creation and evaluation.

While initially developed to work with deep learning models, the concepts surrounding the package
are universal and can be used with any type of models. Mouffet was also designed to be platform
and model framework agnostic. This means that several models created with different frameworks
(e.g. tensorflow, pytorch, etc.) could be trained and compared when encapsulated with mouffet.

.. toctree::
   :maxdepth: 1
   :caption: Getting started:

   install
   tutorial

.. toctree::
   :maxdepth: 2
   :caption: Core concepts

   configuration
   scenarios
   classes

.. toctree::
   :maxdepth: 2
   :caption: API Documentation

   api/data
   api/training
   api/evaluation
   api/models
   api/options

.. toctree::
   :maxdepth: 2
   :caption: Configuration options

   config/data_config
   config/training_config
   config/evaluation_config

.. toctree::
   :maxdepth: 1
   :caption: Examples

   faq



