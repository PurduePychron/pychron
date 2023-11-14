# ===============================================================================
# Copyright 2023 Jake Ross
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
from traits.api import provides, Str, Int

from pychron.furnace.ifurnace_controller import IFurnaceController
from pychron.hardware.core.core_device import CoreDevice
from pychron.hardware.eurotherm import ENQ, EOT, STX, calculate_bcc, ETX
from pychron.hardware.eurotherm.base import BaseEurotherm, PID_REGEX
from pychron.hardware.furnace.base_furnace_controller import BaseFurnaceController


class Eurotherm800Series(CoreDevice):
    GID = Int
    UID = Int

    def enquiry(self, mnenonic):
        address = self.unit_address
        transmission = f'{EOT}{address}{mnenonic}{ENQ}'
        resp = self.ask(transmission, verbose=True)
        if resp:
            stx = resp[0]
            rmnenonic = resp[1:3]
            etx = resp[-3]
            bcc = resp[-2:]
            return float(resp[3:-3])

    def change(self, mnenonic, value):
        address = self.unit_address

        packet = f'{mnenonic}{value}{ETX}'
        bcc = calculate_bcc(packet)
        transmission = f'{EOT}{address}{STX}{packet}{bcc}'

        resp = self.ask(transmission, verbose=True)
        # if resp:
        #     stx = resp[0]
        #     rmnenonic = resp[1:3]
        #     etx = resp[-3]
        #     bcc = resp[-2:]
        #     return float(resp[3:-3])

    @property
    def unit_address(self):
        return f'{self.gid}{self.gid}{self.uid}{self.uid}'

    def load_additional_args(self, config):
        """ """

        self.set_attribute(
            config, "protocol", "Communications", "protocol", optional=True
        )

        if self.protocol == "bisynch":
            self.set_attribute(
                config, "GID", "Communications", "GID", cast="int", optional=True
            )

            self.set_attribute(
                config, "UID", "Communications", "UID", cast="int", optional=True
            )

        return True

    def initialize(self, *args, **kw):
        if self.communicator:
            self.communicator.write_terminator = None
        return True


class Eurotherm818(Eurotherm800Series, BaseFurnaceController):
    """
    https://www.eurotherm.com/download/818-operating-instructions-ha020171-iss-10/

    """

    def read_setpoint(self):
        return self.enquiry('SL')

    def test_connection(self):
        return self.read_setpoint()

    def set_process_setpoint_hook(self, v):
        self.change('SL', v)

    def get_process_value_hook(self):
        return self.enquiry('PV')

    def get_output_hook(self):
        return self.enquiry('OP')

    def set_pid(self, s):
        if PID_REGEX.match(s):
            for pa in s.split(";"):
                self.debug("set pid parameters {}".format(pa))
                cmd, value = pa.split(",")
                self.change(cmd, value)
            return True
        else:
            self.warning('invalid pid string "{}"'.format(s))



# ============= EOF =============================================
