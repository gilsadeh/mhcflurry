# Copyright (c) 2016. Mount Sinai School of Medicine
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import listdir
from os.path import splitext, join

import numpy as np

from .regression_target import MAX_IC50
from .predictor_base import PredictorBase

class Ensemble(PredictorBase):
    def __init__(
            self,
            predictors,
            name=None,
            max_ic50=MAX_IC50,
            allow_unknown_amino_acids=True,
            verbose=False):
        PredictorBase.__init__(
            self,
            name=name,
            max_ic50=max_ic50,
            allow_unknown_amino_acids=allow_unknown_amino_acids,
            verbose=verbose)
        self.predictors = predictors

    @classmethod
    def from_directory(
            cls,
            predictor_class,
            directory_path,
            name=None,
            allow_unknown_amino_acids=True,
            max_ic50=MAX_IC50,
            verbose=False):
        filenames = listdir(directory_path)
        filename_set = set(filenames)
        predictors = []
        for filename in filenames:
            prefix, ext = splitext(filename)
            if ext == ".json":
                weights_filename = prefix + ".hdf5"
                if weights_filename in filename_set:
                    json_path = join(directory_path, filename)
                    weights_path = join(directory_path, weights_filename)
                    predictor = predictor_class.from_disk(
                        json_path,
                        weights_path,
                        name=name + ("_%d" % (len(predictors))),
                        max_ic50=max_ic50,
                        allow_unknown_amino_acids=allow_unknown_amino_acids,
                        verbose=verbose)
                    predictors.append(predictor)
        return cls(
            predictors,
            name=name,
            max_ic50=max_ic50,
            allow_unknown_amino_acids=allow_unknown_amino_acids,
            verbose=verbose)

    def to_directory(self, directory_path, base_name=None):
        if not base_name:
            base_name = self.name
        if not base_name:
            raise ValueError("Base name for serialized models required")
        raise ValueError("Not yet implemented")

    def predict(self, X):
        X = np.asarray(X)
        if len(X.shape) != 2:
            raise ValueError("Expected encoded peptides to be 2d, got %s array" % (
                X.shape,))
        n = len(X)
        y_combined = np.zeros(n)
        for predictor in self.predictors:
            y = predictor.predict(X)
            assert len(y) == len(y_combined)
            y_combined += y
        y_combined /= len(self.predictors)
        return y_combined
