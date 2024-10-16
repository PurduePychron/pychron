# ===============================================================================
# Copyright 2013 Jake Ross
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

# ============= enthought library imports =======================
from pyface.timer.do_later import do_after
from traits.api import List, Event
from traitsui.api import View, UItem, Group, VSplit
from traitsui.editors.api import TabularEditor
from traitsui.tabular_adapter import TabularAdapter

# ============= standard library imports ========================
# ============= local library imports  ==========================
from pychron.core.helpers.formatting import floatfmt
from pychron.pipeline.plot.editors.figure_editor import FigureEditor
from pychron.pipeline.plot.models.series_model import SeriesModel
from pychron.pychron_constants import DELTA

TOOLTIP_MAP = {
    "label": "Label",
    "mean": "Weighted mean if data has errors otherwise average",
    "n": "Number of data points",
    "std": "Standard Deviation",
    "se": "Standard Error, aka Taylor error.  1/sqrt(sum(weights)). If data has no errors this column "
    "will be a replica of SD column",
    "sem": "Standard Error of the Mean.  SD/sqrt(n)",
    "mswd": "MSWD of the current fit type",
    "mean_mswd": "MSWD of a mean fit to the data",
    "min": "Minimum value of the data",
    "max": "Maximum value of the data",
    "dev": "Delta, aka difference between Min and Max",
}


class SeriesStatsTabularAdapter(TabularAdapter):
    columns = [
        ("Label", "label"),
        ("Mean", "mean"),
        ("N", "fn"),
        ("SD", "std"),
        ("SE", "se"),
        ("SEM", "sem"),
        ("Fit MSWD", "mswd"),
        ("Mean MSWD", "mean_mswd"),
        ("Min", "min"),
        ("Max", "max"),
        (DELTA, "dev"),
    ]

    def get_tooltip(self, obj, trait, row, column):
        name = self.column_map[column]
        return TOOLTIP_MAP.get(name, "")


class SeriesStatistics:
    def __init__(self, label, reg):
        self.label = label
        self._reg = reg

    def __getattr__(self, attr):
        if hasattr(self._reg, attr):
            v = getattr(self._reg, attr)
            if isinstance(v, float):
                v = floatfmt(v)
            return v


class SeriesEditor(FigureEditor):
    figure_model_klass = SeriesModel
    pickle_path = "series"
    basename = "Series"
    statistics = List
    update_needed = Event

    def _get_component_hook(self, model=None):
        if model is None:
            model = self.figure_model

        ss = []
        for p in model.panels:
            g = p.figures[0].graph
            if g:
                if self.plotter_options.show_statistics_as_table:
                    g.on_trait_change(self._handle_reg, "regression_results")
                    for plot in reversed(g.plots):
                        for k, v in plot.plots.items():
                            if k.startswith("fit") and hasattr(v[0], "regressor"):
                                label = plot.y_axis.title
                                for tag in ("sub", "sup"):
                                    label = label.replace("<{}>".format(tag), "")
                                    label = label.replace("</{}>".format(tag), "")

                                ss.append(SeriesStatistics(label, v[0].regressor))

                else:
                    g.on_trait_change(
                        self._handle_reg, "regression_results", remove=True
                    )

        do_after(1, self.trait_set, statistics=ss)

    def _handle_reg(self, new):
        self.update_needed = True

    def traits_view(self):
        tblgrp = Group(
            UItem(
                "statistics",
                height=100,
                editor=TabularEditor(
                    adapter=SeriesStatsTabularAdapter(), update="update_needed"
                ),
            ),
            visible_when="object.plotter_options.show_statistics_as_table",
            label="Stats.",
        )

        v = View(VSplit(self.get_component_view(), tblgrp), resizable=True)
        return v


# ============= EOF =============================================
