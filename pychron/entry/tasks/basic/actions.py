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
from pyface.tasks.action.task_action import TaskAction
from traitsui.menu import Action


class SaveAction(TaskAction):
    name = "Save"
    method = "save"


class BasicEntryAction(Action):
    name = "Basic Database"
    dname = "Basic Database"
    id = "pychron.basic.database"

    def perform(self, event):
        pid = "pychron.entry.basic.task"
        app = event.task.window.application
        app.get_task(pid)


# ============= EOF =============================================
