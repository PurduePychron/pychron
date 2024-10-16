# ===============================================================================
# Copyright 2015 Jake Ross
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
# ============= standard library imports ========================
# ============= local library imports  ==========================
"""
This file defines the text for various default files.

Values are used in pychron.paths when building directory structure
"""
from __future__ import absolute_import

import yaml

from pychron.core.helpers.strtools import to_bool

# PIPELINE_TEMPLATES = '''- Isotope Evolutions
# - Blanks
# - IC Factor
# - Flux
# - Ideogram
# - Spectrum
# - Inverse Isochron
# - Series
# - Regression Series
# - Radial
# - Analysis Table
# - Interpreted Age Table
# - Interpreted Age Ideogram
# - Auto Ideogram
# - Auto Series
# - Auto Report
# - Report
# - Diff
# - Vertical Flux
# - Xy Scatter
# - Geochron
# - Yield
# - CSV Analyses Export
# - CSV Ideogram
# - Correction Factors
# - Monitor Chain
# - Analysis Metadata
# '''

IDENTIFIERS_DEFAULT = """
- name: Blank
  shortname: b
  extractable: False
  special: True
- name: Blank Air
  shortname: ba
  extractable: False
  special: True
- name: Blank Cocktail
  shortname: bc
  extractable: False
  special: True
- name: Blank Unknown
  shortname: bu
  extractable: False
  special: True
- name: Blank ExtractionLine
  shortname: be
  extractable: False
  special: True
- name: Background
  shortname: bg
  extractable: False
  special: True
- name: Unknown
  shortname: u
  extractable: True
  special: False
- name: Cocktail
  shortname: c
  extractable: False
  special: True
- name: Air
  shortname: a
  extractable: False
  special: True
- name: Pause
  shortname: pa
  extractable: False
  special: True
- name: Degas
  shortname: dg
  extractable: True
  special: True
- name: Detector IC
  shortname: ic
  extractable: False
  special: True
"""

EDIT_UI_DEFAULT = """
predefined: Simple
"""

TASK_EXTENSION_DEFAULT = """
-
 plugin_id: pychron.update.plugin
 actions:
  - pychron.update.check_for_updates, True
  - pychron.update.manage_version, False
  - pychron.update.manage_branch, False
  - pychron.update.build_app, False

-
 plugin_id: pychron.processing.plugin.recall
 actions:
  - pychron.recall.recall, True
  - pychron.recall.configure, True
  - pychron.recall.time_view, True
-
 plugin_id: pychron.processing.plugin.figures
 actions:
  - pychron.figure.spectrum, True
  - pychron.figure.ideogram, True
  - pychron.figure.inv_isochron, True
  - pychron.figure.series, True
  - pychron.figure.composite, True
  - pychron.figure.xyscatter, True
  - pychron.figure.file_ideogram, True
  - pychron.figure.file_spectrum, True
  - pychron.figure.ideogram_file_template, True
  - pychron.figure.spectrum_file_template, True
  - pychron.figure.refresh, True
-
 plugin_id: pychron.processing.plugin.reduction
 actions:
  - pychron.reduction.iso_evo, True
  - pychron.reduction.blanks, True
  - pychron.reduction.ic_factor, True
  - pychron.reduction.discrimination, False
  - pychron.reduction.flux, True
-
 plugin_id: pychron.processing.plugin.dataset
 actions:
  - pychron.reduction.sqlite_dataset, True
  - pychron.reduction.xml_dataset, True
-
 plugin_id: pychron.processing.plugin.grouping
 actions:
  - pychron.grouping.selected, True
  - pychron.grouping.aliquot, True
  - pychron.grouping.lnumber, True
  - pychron.grouping.sample, True
  - pychron.grouping.clear, True
  - pychron.grouping.gselected, True
  - pychron.grouping.gsample, True
-
 plugin_id: pychron.processing.plugin.misc
 actions:
  - pychron.misc.tag, True
  - pychron.misc.drtag, False
  - pychron.misc.select_drtag, False
  - pychron.misc.db_save, True
  - pychron.misc.clear_cache, True
  - pychron.misc.modify_k, False
  - pychron.misc.modify_identifier, False
-
 plugin_id: pychron.processing.plugin.agroup
 actions:
  - pychron.agroup.make, False
  - pychron.agroup.delete, False
-
 plugin_id: pychron.experiment.plugin.edit
 task_id: pychron.experiment.task
 actions:
  - pychron.experiment.edit.deselect, False
  - pychron.experiment.edit.reset, True
  - pychron.experiment.edit.sync, True
  - pychron.experiment.edit.undo, False
  - pychron.experiment.edit.configure, False
-
 plugin_id: pychron.experiment.plugin
 actions:
  - pychron.experiment.open_system_conditionals, True
  - pychron.experiment.open_queue_conditionals, True
  - pychron.experiment.open_experiment, True
  - pychron.experiment.open_last_experiment, True
  - pychron.experiment.launch_history, True
  - pychron.experiment.run_history_view, True
  - pychron.experiment.test_notify, False
  - pychron.experiment.new_experiment, True
  - pychron.experiment.signal_calculator, False
  - pychron.experiment.new_pattern, False
  - pychron.experiment.open_pattern, False

-
 plugin_id: pychron.entry.plugin
 task_id: pychron.entry.irradiation.task
 actions:
  - pychron.entry2.transfer_j, True
  - pychron.entry2.import_irradiation, True
  - pychron.entry2.export_irradiation, False
  - pychron.entry2.import_samples_from_file, False
  - pychron.entry2.generate_tray, False
  - pychron.entry2.save_labbook, False
  - pychron.entry2.make_template, False

-
 plugin_id: pychron.entry.plugin
 actions:
  - pychron.entry1.labnumber_entry, True
  - pychron.entry1.sample_entry, True
  - pychron.entry1.sample_prep, True
  - pychron.entry1.generate_irradiation_table, False
  - pychron.entry1.import_irradiation_holder, False
  - pychron.entry1.sensitivity_entry, True
  - pychron.entry1.flux_monitor, False
"""
actions = []
for line in TASK_EXTENSION_DEFAULT.split("\n"):
    line = line.strip()
    if line.startswith("- pychron."):
        a, b = line.split(",")
        if to_bool(b):
            actions.append(a)

SIMPLE_UI_DEFAULT = "\n".join(actions)

DEFAULT_INITIALIZATION = """<root>
    <globals>
    </globals>
    <plugins>
        <general>
            <plugin enabled="false">Processing</plugin>
            <plugin enabled="false">MediaStorage</plugin>
            <plugin enabled="false">PyScript</plugin>
            <plugin enabled="false">Video</plugin>
            <plugin enabled="false">Database</plugin>
            <plugin enabled="false">Entry</plugin>
            <plugin enabled="false">ArArConstants</plugin>
            <plugin enabled="false">Loading</plugin>
            <plugin enabled="false">LabBook</plugin>
            <plugin enabled="false">DashboardServer</plugin>
            <plugin enabled="false">DashboardClient</plugin>
        </general>
        <hardware>
        </hardware>
        <social>
        </social>
    </plugins>
</root>
"""

DEFAULT_STARTUP_TESTS = """
- plugin: Database
  tests:
    - test_pychron
    - test_pychron_version
- plugin: MassSpec
  tests:
    - test_database
- plugin: LabBook
  tests:
- plugin: ArArConstants
  tests:
- plugin: ArgusSpectrometer
  tests:
    - test_communication
    - test_intensity
- plugin: ExtractionLine
  tests:
    - test_valve_communication
    - test_gauge_communication
"""

EXPERIMENT_DEFAULTS = """
columns:
  - Labnumber
  - Aliquot
  - Sample
  - Position
  - Extract
  - Units
  - Duration (s)
  - Cleanup (s)
  - Beam (mm)
  - Pattern
  - Extraction
  - Measurement
  - Conditionals
  - Comment
"""

RATIO_CHANGE_DETECTION = """
# - ratio: Ar40/Ar36
#   nanalyses: 5
#   threshold: 1
##   percent_threshold: 1
##   nominal_ratio: 295
##   nsigma: 3 
#   analysis_type: air
#   failure_count: 2
#   consecutive_failure: True
# - ratio: Ar40/Ar39
#   nanalyses: 5
#   threshold: 1
##   percent_threshold: 1
##   nominal_ratio: 10
##   nsigma: 3
#   analysis_type: cocktail
#   failure_count: 2
#   consecutive_failure: True
"""


def make_screen(**kw):
    obj = {
        "padding_left": 100,
        "padding_right": 100,
        "padding_top": 100,
        "padding_bottom": 100,
        "bgcolor": "white",
        "plot_bgcolor": "white",
        "xtick_in": 1,
        "xtick_out": 5,
        "ytick_in": 1,
        "ytick_out": 5,
        "use_xgrid": True,
        "use_ygrid": True,
    }

    obj.update(kw)
    return yaml.dump(obj, default_flow_style=False)


def make_presentation(**kw):
    obj = {
        "padding_left": 40,
        "padding_right": 40,
        "padding_top": 40,
        "padding_bottom": 40,
        "bgcolor": (239, 238, 185),
        "plot_bgcolor": (208, 243, 241),
        "xtick_in": 1,
        "xtick_out": 5,
        "ytick_in": 1,
        "ytick_out": 5,
        "use_xgrid": True,
        "use_ygrid": True,
    }

    obj.update(kw)
    return yaml.dump(obj, default_flow_style=False)


DEFINE_EQUILIBRATION_SCREEN = make_screen()
ISO_EVO_SCREEN = make_screen()
SERIES_SCREEN = make_screen()
BLANKS_SCREEN = make_screen()
ICFACTOR_SCREEN = make_screen()

BLANKS_PRESENTATION = make_presentation()

iso_d = dict(use_xgrid=False, use_ygrid=False)
inv_iso_d = dict(
    use_xgrid=False,
    use_ygrid=False,
    nominal_intercept_label="Atm",
    nominal_intercept_value=295.5,
    show_nominal_intercept=True,
    invert_nominal_intercept=True,
    inset_marker_size=2.5,
    inset_marker_color="black",
)

ISOCHRON_SCREEN = make_screen(**iso_d)
ISOCHRON_PRESENTATION = make_presentation(**iso_d)

INVERSE_ISOCHRON_SCREEN = make_screen(**inv_iso_d)
INVERSE_ISOCHRON_PRESENTATION = make_presentation(**inv_iso_d)

ideo_d = dict(
    probability_curve_kind="Cumulative",
    mean_calculation_kind="Weighted Mean",
    mean_sig_figs=2,
    index_attr="uage",
)

IDEOGRAM_SCREEN = make_screen(mean_indicator_fontsize=12, **ideo_d)
IDEOGRAM_PRESENTATION = make_presentation(mean_indicator_fontsize=24, **ideo_d)

spec_d = dict(
    plateau_line_width=1,
    plateau_line_color="black",
    plateau_sig_figs=2,
    # calculate_fixed_plateau= False,
    # calculate_fixed_plateau_start= '',
    # calculate_fixed_plateau_end= '',
    pc_nsteps=3,
    pc_gas_fraction=50,
    integrated_sig_figs=2,
    legend_location="Upper Right",
    include_legend=False,
    include_sample_in_legend=False,
    display_step=True,
    display_extract_value=False,
)

SPECTRUM_PRESENTATION = make_presentation(**spec_d)
SPECTRUM_SCREEN = make_screen(**spec_d)

radial_d = dict()
RADIAL_SCREEN = make_screen(**radial_d)

regression_series_d = dict()
REGRESSION_SERIES_SCREEN = make_screen(**regression_series_d)

FLUX_CONSTANTS_DEFAULT = """
# This is an example flux file. Add additional decay_constant and monitor_age pairs here
"FC MIN":
  lambda_ec: [5.80e-11, 0]
  lambda_b: [4.884e-10, 0]
  monitor_age: 28.201
"FC SJ":
  lambda_ec: [5.81e-11, 0]
  lambda_b: [4.962e-10, 0]
  monitor_age: 28.02
"""

REACTORS_DEFAULT = """{
    "Triga": {
            "K4039": [0.007614,0.000105],
            "K3839": [0.013,0.0],
            "K3739": [0.0,0.0],
            "Ca3937": [0.00066,1e-05],
            "Ca3837": [4e-05,2e-06],
            "Ca3637": [0.000264,1e-06],
            "Cl3638": [250.0,0.0],
            "Ca_K": [1.96,0.0],
            "Cl_K": [0.227,0.0]
            }
}
"""

# ============= EOF =============================================
