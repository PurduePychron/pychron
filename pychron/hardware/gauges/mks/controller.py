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
from traitsui.api import View, Item, HGroup, Group, ListEditor, InstanceEditor

from pychron.core.ui.color_map_bar_editor import BarGaugeEditor
from pychron.hardware.core.core_device import CoreDevice
from pychron.hardware.gauges.base_controller import BaseGauge, BaseGaugeController


class Gauge(BaseGauge):
    def traits_view(self):
        v = View(HGroup(Item('display_name', show_label=False, style='readonly',
                             width=-30, ),
                        Item('pressure',
                             format_str='%0.2e',
                             show_label=False,
                             style='readonly'),
                        Item('pressure',
                             show_label=False,
                             width=self.width,
                             editor=BarGaugeEditor(low=self.low,
                                                   high=self.high,
                                                   scale='power',
                                                   color_scalar=self.color_scalar,
                                                   width=self.width))))
        return v


class MKSController(BaseGaugeController, CoreDevice):
    gauge_klass = Gauge

    def _read_pressure(self, name, verbose=False):
        g = self.get_gauge(name)
        cmd = self._build_command('PR{}'.format(g.channel))
        r = self.ask(cmd)

        try:
            return float(r)
        except ValueError:
            pass

    def _build_command(self, cmd):
        return '@{}{};FF'.format(self.address, cmd)

    def load_additional_args(self, config, *args, **kw):
        self.address = self.config_get(config, 'General', 'address', optional=False)
        self.display_name = self.config_get(config, 'General', 'display_name', default=self.name)
        # self.mode = self.config_get(config, 'Communications', 'mode', default='rs485')
        self._load_gauges(config)
        return True

    def gauge_view(self):
        v = View(Group(Item('gauges', style='custom',
                            show_label=False,
                            editor=ListEditor(mutable=False,
                                              style='custom',
                                              editor=InstanceEditor())),
                       show_border=True,
                       label=self.display_name))
        return v

# ============= EOF =============================================
