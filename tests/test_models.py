import sys
sys.path.insert(0, '/Users/btvincent/git-local/darc-experiments-python')

from collections import namedtuple
import pandas as pd
import numpy as np
import pytest
from darc.delayed import models as delayed_models
from darc.risky import models as risky_models
from darc.delayed_and_risky import models as delayed_and_risky_models


# define useful data structures
Prospect = namedtuple('Prospect', ['reward', 'delay', 'prob'])
Design = namedtuple('Design', ['ProspectA', 'ProspectB'])

delayed_models_list = [
    delayed_models.Hyperbolic,
    delayed_models.Exponential,
    delayed_models.HyperbolicMagnitudeEffect,
    delayed_models.ExponentialMagnitudeEffect,
    delayed_models.ModifiedRachlin,
    delayed_models.MyersonHyperboloid,
    #delayed_models.HyperbolicNonLinearUtility
]

risky_models_list = [
    risky_models.Hyperbolic,
    risky_models.ProportionalDifference,
    #risky_models.ProspectTheory
]

delayed_and_risky_models_list = [
    delayed_and_risky_models.MultiplicativeHyperbolic
]


# test model instantiation

@pytest.mark.parametrize("model", delayed_models_list + risky_models_list + delayed_and_risky_models_list)
def test_model_creation(model):
    n_particles = 10
    model_instance = model(n_particles=n_particles)
    assert isinstance(model_instance, model)


# test calc_decision_variable() method of model classes ==========

@pytest.mark.parametrize("model", delayed_models_list + risky_models_list + delayed_and_risky_models_list)
def test_calc_decision_variable(model):
    n_particles = 10
    model_instance = model(n_particles=n_particles)

    faux_design = pd.DataFrame({'RA': [100.], 'DA': [0.], 'PA': [1.],
                                'RB': [150.], 'DB': [14.], 'PB': [1.]})
    dv = model_instance.calc_decision_variable(model_instance.θ, faux_design)
    assert isinstance(dv, np.ndarray)


# tests to confirm that we can update beliefs

# THIS IS NO LONGER HOW UPDATING OF data WORKS: NEED TO UPDATE THIS TEST
# @pytest.mark.parametrize("model", delayed_models_list + risky_models_list + delayed_and_risky_models_list)
# def test_update_beliefs(model):
#     # set up model
#     n_particles = 100
#     model_instance = model(n_particles=n_particles)
#     # set up faux data
#     data_columns = ['RA', 'DA', 'PA', 'RB', 'DB', 'PB', 'R']
#     data = pd.DataFrame(columns=data_columns)
#     faux_trial_data = {'RA': [100.], 'DA': [0.], 'PA': [1.],
#                        'RB': [160.], 'DB': [60.], 'PB': [1.],
#                        'R': [int(False)]}
#     data = data.append(pd.DataFrame(faux_trial_data))
#     model_instance.update_beliefs(data)
#     # basically checking model_instance is a model and that we've not errored by this point
#     assert isinstance(model_instance, model)


@pytest.mark.parametrize("model", delayed_models_list + risky_models_list + delayed_and_risky_models_list)
def test_generate_faux_true_params(model):
    model_instance = model(n_particles=30)
    model_instance = model_instance.generate_faux_true_params()
    isinstance(model_instance.θ_true, dict)


@pytest.mark.parametrize("model", delayed_models_list + risky_models_list + delayed_and_risky_models_list)
def test_get_simulated_response(model):
    # set up model
    n_particles = 100
    model_instance = model(n_particles=n_particles)
    model_instance = model_instance.generate_faux_true_params()

    faux_design = pd.DataFrame({'RA': [100.], 'DA': [0.], 'PA': [1.],
                                'RB': [150.], 'DB': [14.], 'PB': [1.]})

    response = model_instance.get_simulated_response(faux_design)
    isinstance(response, bool)

