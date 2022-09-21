# pythor-tools

Tools to preprocess THÖR dataset used in Context-free Self-Conditioned GAN for Trajectory Forecasting.

## Installation

Install [miniconda](http://docs.conda.io/en/latest/miniconda.html). Then, you can install all packages required by running:

```
conda env create -f environment.yml
```


Then, you need to download the raw THÖR dataset from [Zenodo repository](https://zenodo.org/record/3382145#.YxcPhdJBzmE).

## Filtering and splitting

Firstly, set the [config file](https://github.com/tmralmeida/pythor-tools/blob/main/cfg/ds_params.yaml). Then, run:

```
python -m pythor-tools.run
```

Secondly, creating training, validation, and test sets:

```
python -m pythor-tools.split_sets
```

In the end, you will have one `output` folder containing the preprocessed files and the respective training, validation, and test sets.
