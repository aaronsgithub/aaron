# AUTOGENERATED! DO NOT EDIT! File to edit: ../../nbs/ai/sgd.ipynb.

# %% auto 0
__all__ = ['BaseSchedCB', 'BatchSchedCB', 'HasLearnCB', 'RecorderCB', 'EpochSchedCB']

# %% ../../nbs/ai/sgd.ipynb 2
import matplotlib.pyplot as plt
import torch

from .datasets import *
from .conv import *
from .learner import *
from .activations import *
from .init import *

# %% ../../nbs/ai/sgd.ipynb 3
class BaseSchedCB(Callback):
    def __init__(self, sched): self.sched = sched
    def before_fit(self, learn): self.schedo = self.sched(learn.opt)
    def _step(self, learn):
        if learn.training: self.schedo.step()

# %% ../../nbs/ai/sgd.ipynb 4
class BatchSchedCB(BaseSchedCB):
    def after_batch(self, learn): self._step(learn)

# %% ../../nbs/ai/sgd.ipynb 5
class HasLearnCB(Callback):
    def before_fit(self, learn): self.learn = learn 
    def after_fit(self, learn): self.learn = None

# %% ../../nbs/ai/sgd.ipynb 6
class RecorderCB(Callback):
    def __init__(self, **d): self.d = d
    def before_fit(self, learn):
        self.recs = {k:[] for k in self.d}
        self.pg = learn.opt.param_groups[0]
    
    def after_batch(self, learn):
        if not learn.training: return
        for k,v in self.d.items():
            self.recs[k].append(v(self))

    def plot(self):
        for k,v in self.recs.items():
            plt.plot(v, label=k)
            plt.legend()
            plt.show()

# %% ../../nbs/ai/sgd.ipynb 7
class EpochSchedCB(BaseSchedCB):
    def after_epoch(self, learn): self._step(learn)
