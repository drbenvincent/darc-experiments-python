import numpy as np
from collections import namedtuple
import logging
from darc.designs import DesignGeneratorABC

# define useful data structures
Prospect = namedtuple('Prospect', ['reward', 'delay', 'prob'])
Design = namedtuple('Design', ['ProspectA', 'ProspectB'])


class Kirby2009(DesignGeneratorABC):
    '''
    A class to provide designs from the Kirby (2009) delay discounting task.

    Kirby, K. N. (2009). One-year temporal stability of delay-discount rates.
    Psychonomic Bulletin & Review, 16(3):457–462.
    '''

    # NOTE: these should probably not be class attributes, but declared in the __init__
    # only likely to be a problem if we have mulitple Kirby2009 object instances. We'd
    # also have to explicitly call the superclass constructor at that point, I believe.
    max_trials = 27
    _RA = [80, 34, 25, 11, 49, 41, 34, 31, 19, 22, 55, 28, 47,
          14, 54, 69, 54, 25, 27, 40, 54, 15, 33, 24, 78, 67, 20]
    _DA = 0
    _RB = [85, 50, 60, 30, 60, 75, 35, 85, 25, 25, 75, 30, 50,
          25, 80, 85, 55, 30, 50, 55, 60, 35, 80, 35, 80, 75, 55]
    _DB = [157, 30, 14, 7, 89, 20, 186, 7, 53, 136, 61, 179, 160, 19,
          30, 91, 117, 80, 21, 62, 111, 13, 14, 29, 162, 119, 7]
    _PA, _PB = 1, 1

    def get_next_design(self, _):
        # NOTE: This is un-Pythonic as we are asking permission... we should just do it, and have a catch ??
        if self.trial < self.max_trials - 1:
            logging.info(f'Getting design for trial {self.trial}')
            design = Design(ProspectA=Prospect(reward=self._RA[self.trial], delay=self._DA, prob=self._PA),
                            ProspectB=Prospect(reward=self._RB[self.trial], delay=self._DB[self.trial], prob=self._PB))
            return design
        else:
            return None


class Griskevicius2011(DesignGeneratorABC):
    '''
    A class to provide designs from the Griskevicius et al (2011) delay
    discounting task.

    Griskevicius, V., Tybur, J. M., Delton, A. W., & Robertson, T. E. (2011).
    The influence of mortality and socioeconomic status on risk and delayed
    rewards: A life history theory approach. Journal of Personality and
    Social Psychology, 100(6), 1015–26. http://doi.org/10.1037/a0022403
    '''

    # NOTE: these should probably not be class attributes, but declared in the __init__
    # only likely to be a problem if we have mulitple instances. We'd
    # also have to explicitly call the superclass constructor at that point, I believe.
    max_trials = 7
    _RA = 100
    _DA = 0
    _RB = [110, 120, 130, 140, 150, 160, 170]
    _DB = 90
    _PA, _PB = 1, 1

    def get_next_design(self, _):
        # NOTE: This is un-Pythonic as we are asking permission...
        # we should just do it, and have a catch ??
        if self.trial < self.max_trials:
            logging.info(f'Getting design for trial {self.trial}')
            design = Design(ProspectA=Prospect(reward=self._RA, delay=self._DA, prob=self._PA),
                            ProspectB=Prospect(reward=self._RB[self.trial], delay=self._DB, prob=self._PB))
            return design
        else:
            return None


class Koffarnus_Bickel(DesignGeneratorABC):
    '''
    This function returns a function which returns designs according to the
    method described by:
    Koffarnus, M. N., & Bickel, W. K. (2014). A 5-trial adjusting delay
    discounting task: Accurate discount rates in less than one minute.
    Experimental and Clinical Psychopharmacology, 22(3), 222-228.
    http://doi.org/10.1037/a0035973
    '''

    # NOTE: these should probably not be class attributes, but declared in the __init__
    # only likely to be a problem if we have mulitple instances. We'd
    # also have to explicitly call the superclass constructor at that point, I believe.
    max_trials = 5
    _RB = 100
    _DA = 0
    _RA = _RB*0.5
    _DB = np.concatenate([(1/24)*np.array([1, 2, 3, 4, 6, 9, 12]),
         np.array([1, 1.5, 2, 3, 4]),
         7*np.array([1, 1.5, 2, 3]),
         29*np.array([1, 2, 3, 4, 6, 8]),
         365*np.array([1, 2, 3, 4, 5, 8, 12, 18, 25])])
    _PA, _PB = 1, 1
    _delay_index = 16-1 # this is always the initial delay used (equals 3 weeks)
    _index_increments = 8
    # trial = 1

    def get_next_design(self, _):

        if self.trial >= self.max_trials:
            return None

        if self.trial == 0:
            design = Design(ProspectA=Prospect(reward=self._RA, delay=self._DA, prob=self._PA),
                            ProspectB=Prospect(reward=self._RB, delay=self._DB[self._delay_index], prob=self._PB))
        else:

            if self.get_last_response_chose_B():
                self._delay_index += self._index_increments
            else:
                self._delay_index -= self._index_increments

            # each trial, the increments half, so will be: 8, 4, 2, 1
            self._index_increments = int(max(self._index_increments/2, 1))

        design = Design(ProspectA=Prospect(reward=self._RA, delay=self._DA, prob=self._PA),
                        ProspectB=Prospect(reward=self._RB, delay=self._DB[self._delay_index], prob=self._PB))
        return design


class Frye(DesignGeneratorABC):
    '''
    A class to provide designs based on the Frye et al (2016) protocol.

    Frye, C. C. J., Galizio, A., Friedel, J. E., DeHart, W. B., & Odum, A. L.
    (2016). Measuring Delay Discounting in Humans Using an Adjusting Amount
    Task. Journal of Visualized Experiments, (107), 1-8.
    http://doi.org/10.3791/53584
    '''

    def __init__(self, DB=[7, 30, 30*3, 30*6, 365], RB=100., trials_per_delay=5):
        self._DA = 0
        self._DB = DB
        self._RB = RB
        self._R_A = RB * 0.5
        self._post_choice_adjustment = 0.25
        self._trials_per_delay = trials_per_delay
        self._trial_per_delay_counter = 0
        self._delay_counter = 0
        self._PA = 1
        self._PB = 1
        self.max_trials = len(self._DB) * self._trials_per_delay
        # call the superclass constructor
        super().__init__()

    def get_next_design(self, _):
        """return the next design as a tuple of prospects"""

        if self._delay_counter == len(self._DB):
            return None

        logging.info(f'Getting design for trial {self.trial}')
        last_response_chose_B = self.get_last_response_chose_B()

        if self._trial_per_delay_counter is 0:
            self._RA = self._RB * 0.5
        else:
            self._update_RA_given_last_response(last_response_chose_B)
            self._post_choice_adjustment *= 0.5

        design = Design(ProspectA=Prospect(reward=self._RA, delay=self._DA, prob=self._PA),
                        ProspectB=Prospect(reward=self._RB, delay=self._DB[self._delay_counter], prob=self._PB))
        self._increment_counter()
        return design

    # Below are helper functions

    def _increment_counter(self):
        """Increment trial counter, and increment delay counter if we have done all the trials per delay"""
        self._trial_per_delay_counter += 1
        # reset trial_per_delay_counter if need be
        if self._trial_per_delay_counter > self._trials_per_delay-1:
            self._increment_delay()


    def _increment_delay(self):
        """ Done trials_per_delay trials for this delay, so we'll move on to the next delay level now"""
        self._delay_counter += 1
        self._trial_per_delay_counter = 0
        self._post_choice_adjustment = 0.25

    def _update_RA_given_last_response(self, last_response_chose_B):
        # change things depending upon last response
        if last_response_chose_B:
            self._RA = self._RA + (self._RB * self._post_choice_adjustment)
        else:
            self._RA = self._RA - (self._RB * self._post_choice_adjustment)