# ===============================================================================
# Copyright 2013 Jake Ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================

# ============= enthought library imports =======================

# ============= standard library imports ========================
# ============= local library imports  ==========================
from __future__ import absolute_import
from pychron.loggable import Loggable


class BaseImportMapper(Loggable):
    """
    base class for mapping between two data sources
    use this to fix/change run info on import

    fix typos
    e.g change Mina Bluff > Minna Bluff
    """


class MinnaBluffMapper(BaseImportMapper):
    def map_project(self, project):
        pl = project.lower()
        if pl in ("mina bluff", "minna bluff"):
            project = "Minna Bluff"
        elif pl in ("j", "j-curve"):
            project = "J"
        return project

    def map_material(self, mat):
        # ml=mat.lower()
        # if ml in ('gmc', 'groundmass', 'groundmass conc'):
        #    mat='Groundmass'

        return mat.capitalize()


# ============= EOF =============================================
