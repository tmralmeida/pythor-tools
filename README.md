# pythor-tools
Tools to handle THOR dataset.


## Current status

* [x] Filtering/Splitting
* [ ] Visualization
* [ ] Statistics
  * [ ] # overal samples, # samples per class
  * **smoothed spline fit distances:**
  * [ ] $\sigma_{x,spline}[m]$, $\sigma_{y,spline}[m]$ [RED eval](https://openaccess.thecvf.com/content_ECCVW_2018/papers/11131/Becker_RED_A_simple_but_effective_Baseline_Predictor_for_the_TrajNet_ECCVW_2018_paper.pdf) 
  * [ ] $R^2_x$, $R^2_y$
  * [ ] Turtuosity, etc. [Undestanding](https://link.springer.com/content/pdf/10.1007/s10109-021-00370-6.pdf)

## Filtering and splitting

First, set the config file. Then, run:

```
python -m pythor-tools.run
```

Finally, creating training, validation, and test sets:

```
python -m pythor-tools.split_sets
```

## Visualization


```
python -m pythor-tools.vis
```


## Statistics