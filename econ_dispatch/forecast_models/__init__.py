# -*- coding: utf-8 -*- {{{
# vim: set fenc=utf-8 ft=python sw=4 ts=4 sts=4 et:

# Copyright (c) 2017, Battelle Memorial Institute
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation
# are those of the authors and should not be interpreted as representing
# official policies, either expressed or implied, of the FreeBSD
# Project.
#
# This material was prepared as an account of work sponsored by an
# agency of the United States Government.  Neither the United States
# Government nor the United States Department of Energy, nor Battelle,
# nor any of their employees, nor any jurisdiction or organization that
# has cooperated in the development of these materials, makes any
# warranty, express or implied, or assumes any legal liability or
# responsibility for the accuracy, completeness, or usefulness or any
# information, apparatus, product, software, or process disclosed, or
# represents that its use would not infringe privately owned rights.
#
# Reference herein to any specific commercial product, process, or
# service by trade name, trademark, manufacturer, or otherwise does not
# necessarily constitute or imply its endorsement, recommendation, or
# favoring by the United States Government or any agency thereof, or
# Battelle Memorial Institute. The views and opinions of authors
# expressed herein do not necessarily state or reflect those of the
# United States Government or any agency thereof.
#
# PACIFIC NORTHWEST NATIONAL LABORATORY
# operated by BATTELLE for the UNITED STATES DEPARTMENT OF ENERGY
# under Contract DE-AC05-76RL01830
# }}}

import abc
import logging
import pkgutil
import pandas as pd

_modelList = [name for _, name, _ in pkgutil.iter_modules(__path__)]

_modelDict = {}


class ForecastModelBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def derive_variables(self, now, independent_variable_values={}):
        """Get the predicted load values based on the independent variables."""
        pass

    @abc.abstractmethod
    def add_training_data(self, now, variable_values={}):
        """Update the training data with the last hour."""
        pass

class HistoryModelBase(ForecastModelBase):
    def __init__(self, history_data_file=None, historical_data_time_column="timestamp"):
        self.setup_historical_data(history_data_file, historical_data_time_column)

    def derive_variables(self, now, independent_variable_values={}):
        now = now.replace(year=self.history_year)
        return self.get_historical_hour(now)

    def add_training_data(self, now, variable_values={}):
        """Update the training data with the last hour."""
        pass

    def setup_historical_data(self, csv_file, historical_data_time_column):
        self.time_column = historical_data_time_column

        self.historical_data = pd.read_csv(csv_file, parse_dates=[self.time_column])

        self.history_year = self.historical_data[self.time_column][0].year

    def get_historical_hour(self, now):
        #Index of the closest timestamp.
        index = abs(self.historical_data[self.time_column] - now).idxmin()
        #Return the row as a dict.
        return dict(self.historical_data.iloc[index])


def get_forecast_model_class(name, type, **kwargs):
    module_name = name + "." + type
    module = __import__(module_name, globals(), locals(), ['Model'], 1)
    klass = module.Model
    return klass(**kwargs)

