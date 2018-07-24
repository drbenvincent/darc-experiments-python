from abc import ABC, abstractmethod
from collections import namedtuple
from bad.base_classes import DesignABC
import pandas as pd


# define useful data structures
Prospect = namedtuple('Prospect', ['reward', 'delay', 'prob'])
Design = namedtuple('Design', ['ProspectA', 'ProspectB'])


## ANOTHER BASE CLASS: Users not to change this

class DARCDesign(DesignABC):

    trial = 0
    RA, DA, PA = None, None, None
    RB, DB, PB = None, None, None

    def __init__(self):
        # generate empty `all_data`
        data_columns = ['RA', 'DA', 'PA', 'RB', 'DB', 'PB', 'R']
        self.all_data = pd.DataFrame(columns=data_columns)

    def enter_trial_design_and_response(self, design, response):
        self.update_all_data(design, response)
        return

    def update_all_data(self, design, response):
        # TODO: need to specify types here I think... then life might be 
        # easier to decant the data out at another point
        trial_data = {'RA': design.ProspectA.reward,
                      'DA': design.ProspectA.delay,
                      'PA': design.ProspectA.prob,
                      'RB': design.ProspectB.reward,
                      'DB': design.ProspectB.delay,
                      'PB': design.ProspectB.prob,
                      'R': [int(response)]}
        self.all_data = self.all_data.append(pd.DataFrame(trial_data))
        return


# CONCRETE DESIGN CLASSES BELOW ======================================================

class Kirby2009(DARCDesign):
    '''
    *** KIRBY REFERENCE HERE ***
    '''

    # NOTE: these should probably not be class attributes, but declared in the __init__ 
    # only likely to be a problem if we have mulitple Kirby2009 object instances. We'd
    # also have to explicitly call the superclass constructor at that point, I believe.
    max_trials = 27
    RA = [80, 34, 25, 11, 49, 41, 34, 31, 19, 22, 55, 28, 47,
          14, 54, 69, 54, 25, 27, 40, 54, 15, 33, 24, 78, 67, 20]
    DA = 0
    RB = [85, 50, 60, 30, 60, 75, 35, 85, 25, 25, 75, 30, 50,
          25, 80, 85, 55, 30, 50, 55, 60, 35, 80, 35, 80, 75, 55]
    DB = [157, 30, 14, 7, 89, 20, 186, 7, 53, 136, 61, 179, 160, 19,
          30, 91, 117, 80, 21, 62, 111, 13, 14, 29, 162, 119, 7]
    PA, PB = 1, 1

    def get_next_design(self, last_response):
        # NOTE: This is un-Pythonic as we are asking permission... we should just do it, and have a catch ??
        if self.trial < self.max_trials - 1:
            design = Design(ProspectA=Prospect(reward=self.RA[self.trial], delay=self.DA, prob=self.PA),
                            ProspectB=Prospect(reward=self.RB[self.trial], delay=self.DB[self.trial], prob=self.PB))
            self.trial += 1
            return design
        else:
            return None


class Frye(DARCDesign):
    '''
    Frye, C. C. J., Galizio, A., Friedel, J. E., DeHart, W. B., & Odum, A. L.
    (2016). Measuring Delay Discounting in Humans Using an Adjusting Amount
    Task. Journal of Visualized Experiments, (107), 1-8.
    http://doi.org/10.3791/53584
    '''
    

    def __init__(self, DB=[7, 30, 365], RB=100., trials_per_delay=5):
        self.DA = 0
        self.DB = DB
        self.RB = RB
        self.R_A = RB * 0.5
        self.post_choice_adjustment = 0.25
        self.trials_per_delay = trials_per_delay
        self.trial_per_delay_counter = 0
        self.delay_counter = 0
        self.PA = 1
        self.PB = 1
        # call the superclass constructor
        super().__init__()


    def get_next_design(self, last_response_chose_delayed):
        """return the next design as a tuple of prospects"""
        print(self.delay_counter, len(self.DB))
        if self.delay_counter == len(self.DB):
            return None

        if self.trial_per_delay_counter is 0:
            self.RA = self.RB * 0.5
        else:
            self._update_RA_given_last_response(last_response_chose_delayed)
            self.post_choice_adjustment *= 0.5

        design = Design(ProspectA=Prospect(reward=self.RA, delay=self.DA, prob=self.PA),
                        ProspectB=Prospect(reward=self.RB, delay=self.DB[self.delay_counter], prob=self.PB))
        self._increment_counter()
        return design


    def _increment_counter(self):
        """Increment trial counter, and increment delay counter if we have done all the trials per delay"""
        self.trial_per_delay_counter += 1
        # reset trial_per_delay_counter if need be
        if self.trial_per_delay_counter > self.trials_per_delay-1:
            self._increment_delay()


    def _increment_delay(self):
        """ Done trials_per_delay trials for this delay, so we'll move on to the next delay level now"""
        self.delay_counter += 1
        self.trial_per_delay_counter = 0
        self.post_choice_adjustment = 0.25

    def _update_RA_given_last_response(self, last_response_chose_delayed):
        # change things depending upon last response
        if last_response_chose_delayed:
            self.RA = self.RA + (self.RB * self.post_choice_adjustment)
        else:
            self.RA = self.RA - (self.RB * self.post_choice_adjustment)


# # TODO|: RETHINK THIS... WE MAYBE WANT SOME ABSTRACT BASE CLASS IN THE `BAD` PACKAGE

# class BAD(DARCDesign):

#     heuristic_order = None

#     @abstractmethod
#     def generate_all_possible_designs(self):
#         pass

#     @abstractmethod
#     def refine_design_space(self, all_possible_designs):
#         ''' In theory we could do design optimisation on ALL possible designs.
#         However, this is complex. You can imagine some sets of designs will map on to
#         very distinct values of the decision variable, but that there are many designs
#         which will be almost invariant to the decision variable. But we would like to 
#         explore the design space sensibly. Our general approach is (on any given trial)
#         to take a subset of the possible designs and conduct design optimisation on this
#         reduced subset. Importantly, over different trials, we are chosing this subset
#         intelligently to maximise exploration over the design space.'''
#         pass

# # CONCRETE BAD CLASSES BELOW -----------------------------------------------------------------

# class BAD_delayed_choices(BAD):

#     PA, PB = 1, 1

#     def __init__(self, DA=0, DB=[7, 14, 30, 365], RA=None, RB=100, fixed_reward_ratio=False):
#         self.DA = DA
#         self.DB = DB
#         self.RA = np.linspace(5, RB, num=20)
#         self.RB = RB
#         self.generate_all_possible_designs()

    
#     def get_next_design(self, last_response):
#         # IMPLEMENT ME
#         pass

#     def refine_design_space(self, all_possible_designs):
#         # IMPLEMENT ME
#         pass

# # class BAD_risky_choices(BAD):


# # class BAD_delayed_and_risky_choices(BAD):