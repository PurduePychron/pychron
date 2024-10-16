# ===============================================================================
# Copyright 2017 ross
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ===============================================================================
from pyface.tasks.traits_dock_pane import TraitsDockPane
from pyface.tasks.traits_task_pane import TraitsTaskPane
from traitsui.api import View, UItem, VGroup


# class SimpleIdentifierAdapter(TabularAdapter):
#     columns = [('Identifier', 'identifier'),
#                ('Sample', 'sample_name'),
#                ('Project', 'project_name'),
#                ('PI', 'principal_investigator_name')]
#


class BasicEntryPane(TraitsTaskPane):
    def traits_view(self):
        return View(VGroup(UItem("ms", style="custom"), UItem("ed", style="custom")))


class BasicEntryEditorPane(TraitsDockPane):
    name = "Editor"
    id = "pychron.basic.editor"

    def traits_view(self):
        return View()

    # set_identifier_button = Button('Set Identifier')
    #
    # def _set_identifier_button_fired(self):
    #     self.model.set_identifier()
    #
    # def traits_view(self):
    #     v = View(Item('project_filter', label='Project'),
    #              UItem('selected_project', editor=EnumEditor(name='projects')),
    #              Item('selected_sample', label='Sample', editor=EnumEditor(name='samples')),
    #              UItem('pane.set_identifier_button'))
    #     return v


# ============= EOF =============================================
