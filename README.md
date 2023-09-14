## Introduction


At this point you can review the quick steps for installing the TFM project. The readme file provided by Kedro is developed when creating the project with this framework.


## Overview

This is your new Kedro project, which was generated using `Kedro 0.18.5`.

We need to work with Visual Studio Code and python version `3.10.x`.



## Rules and guidelines

In order to get the best out of the template:

* Don't remove any lines from the `.gitignore` file we provide
* Make sure your results can be reproduced by following a [data engineering convention](https://kedro.readthedocs.io/en/stable/faq/faq.html#what-is-data-engineering-convention)
* Don't commit data to your repository
* Don't commit any credentials or your local configuration to your repository. Keep all your credentials and local configuration in `conf/local/`

## How to create/activate a new environment for Kedro

In the project root, run:

```
conda create --name kedro-environment python=3.10 -y
```

Then, to activate, run:

```
conda activate kedro-environment
```

## How to install Kedro

If you don't have Kedro installed, run:

```
pip install kedro
```

To review the status:

```
kedro info
```


## How to install dependencies

Any dependencies are declared in `src/requirements.txt` for the `pip` installation and in `src/environment.yml` for the `conda` installation.
To install them, run:

```
pip install -r src/requirements.txt
```

## How to run your Kedro Data_processing pipeline 

You can run your Kedro project with (You must have the Orphadata source file, in:  "/data/01_raw" with name "enfermedades.xml", to obtain the diseases-symptoms-frequencies) :

```
kedro run
```
Executing Kedro run will only execute the Data_processing pipeline. The prepared information (all matrices) will be obtained to work with the App Web (streamlit).

## How to run your App Web (Streamlit)

In the project root, run:

```
streamlit run src/kedro_project/main.py
```

Please read the TFM documentation for more details.
