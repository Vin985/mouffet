# Mouffet: MOdelling Unified Framework For Evaluation and Training

A framework that offers a platform agnostic framework to ease training and evaluation of machine learning models.

Model training and evaluation is done by class inheritance and configuration file.
Multiple scenarios can be trained or evaluated easily via the configuration file and scenario expansion.

# Installation

## Installing python

If you do not already have one, first install a python version on your computer. A python 3 version is required.
We recommend downloading the latest miniconda version that can be found here:
https://docs.conda.io/en/latest/miniconda.html

The site provides information on how to install it on all platforms. Note that you will be required to
use a terminal for program to work. On windows, miniconda installs a terminal directly. You can find it in the
application start menu.

Once miniconda is install, open a terminal. To make sure the installation has worked correctly, you can try to enter
the following command in the terminal:

    python

This should launch a python terminal. To exit the python terminal, type:

    exit()

## Setting up an environment
The following steps are optional but are good practice in Python. If you do no want to proceed, go directly to the next section 

To isolate our work, we will create a python environment. Python environments allow to create an isolated place
where we can avoid package conflicts. To do so, type the following commands:

    cd path/where_I_want_my_environment   # Moves into the working directory
    python -m venv mouffet_env

This should create the environment in the subfolder mouffet_env. Now that it is created, we need to activate it
to let python know where to install our packages

    mouffet_env/Scripts/activate            # This should be the path on Windows
    mouffet_env/bin/activate                # This should work on Linux and Mac

## Installing the dependencies

Now we need to install the dependencies. To do so we will install them using the pip package manager that comes with python.
If this is the first time you use python, you will probably need to update pip. For that, type in you terminal:

    pip install pip --upgrade

Once this is done, you can install the mouffet package using this command:

    pip install -U git+https://github.com/vin985/mouffet.git



