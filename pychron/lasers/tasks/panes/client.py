# ===============================================================================
# Copyright 2020 ross
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
from traitsui.api import (
    VGroup,
    HGroup,
    UItem,
    Item,
    EnumEditor,
    ButtonEditor,
    RangeEditor,
    InstanceEditor,
    Group,
    spring,
    View,
)

from pychron.core.ui.custom_label_editor import CustomLabel
from pychron.core.ui.led_editor import LEDEditor
from pychron.envisage.icon_button_editor import icon_button_editor
from pychron.lasers.tasks.laser_panes import ClientPane


class NonPychronClientPane(ClientPane):
    def traits_view(self):
        pos_grp = self._get_positioning_group()
        calibration_grp = self._get_calibration_group()
        tgrp = Group(pos_grp, calibration_grp, layout="tabbed")

        egrp = HGroup(
            UItem("enabled", editor=LEDEditor(colors=["red", "green"])),
            UItem("enable", editor=ButtonEditor(label_value="enable_label")),
            UItem(
                "fire_laser_button",
                editor=ButtonEditor(label_value="fire_label"),
                enabled_when="enabled",
            ),
            Item("output_power", label="Power"),
            UItem("units"),
            spring,
            icon_button_editor("snapshot_button", "camera"),
            icon_button_editor(
                "test_connection_button", "connect", tooltip="Test Connection"
            ),
        )
        v = View(VGroup(egrp, tgrp))
        return v

    def _get_calibration_group(self):
        calibration_grp = VGroup(
            HGroup(
                UItem(
                    "tray_calibration.style",
                    enabled_when="not tray_calibration.isCalibrating()",
                ),
                UItem(
                    "stage_manager.stage_map_name",
                    editor=EnumEditor(name="stage_manager.stage_map_names"),
                ),
            ),
            UItem(
                "tray_calibration.calibrate",
                editor=ButtonEditor(label_value="tray_calibration.calibration_step"),
            ),
            HGroup(
                Item("tray_calibration.cx", format_str="%0.3f", style="readonly"),
                Item("tray_calibration.cy", format_str="%0.3f", style="readonly"),
            ),
            Item("tray_calibration.rotation", format_str="%0.3f", style="readonly"),
            Item("tray_calibration.scale", format_str="%0.4f", style="readonly"),
            Item("tray_calibration.error", format_str="%0.2f", style="readonly"),
            UItem(
                "tray_calibration.calibrator", style="custom", editor=InstanceEditor()
            ),
            CustomLabel(
                "tray_calibration.calibration_help", color="green", height=75, width=300
            ),
            label="Tray Calibration",
        )
        return calibration_grp

    def _get_positioning_group(self):
        pos_grp = VGroup(
            HGroup(
                UItem(
                    "move_enabled_button",
                    editor=ButtonEditor(label_value="move_enabled_label"),
                ),
                icon_button_editor(
                    "update_position_button",
                    "arrow_refresh",
                    tooltip="Update position. Query laser for current " "xyz position",
                    enabled_when="not _is_moving",
                ),
            ),
            VGroup(
                HGroup(
                    Item("position", enabled_when="not _is_moving"),
                    UItem(
                        "stage_manager.stage_map_name",
                        editor=EnumEditor(name="stage_manager.stage_map_names"),
                    ),
                    UItem("stage_stop_button"),
                ),
                Item(
                    "x",
                    editor=RangeEditor(
                        low_name="stage_manager.xmin", high_name="stage_manager.xmax"
                    ),
                ),
                Item(
                    "y",
                    editor=RangeEditor(
                        low_name="stage_manager.ymin", high_name="stage_manager.ymax"
                    ),
                ),
                Item(
                    "z",
                    editor=RangeEditor(
                        low_name="stage_manager.zmin", high_name="stage_manager.zmax"
                    ),
                ),
                enabled_when="_move_enabled",
            ),
            label="Positioning",
        )
        return pos_grp

    def trait_context(self):
        ctx = super(NonPychronClientPane, self).trait_context()
        ctx["tray_calibration"] = self.model.stage_manager.tray_calibration_manager
        ctx["stage_manager"] = self.model.stage_manager
        return ctx


# ============= EOF =============================================
