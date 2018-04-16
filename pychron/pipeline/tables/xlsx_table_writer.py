# ===============================================================================
# Copyright 2016 ross
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
import os
import re

import xlsxwriter
from pyface.confirmation_dialog import confirm
from pyface.constant import YES
from traits.api import Instance, Enum, Str, Bool, Int, Float, BaseStr
from traitsui.api import View, VGroup, Item, UItem, Tabbed, HGroup, Label
from uncertainties import nominal_value, std_dev, ufloat

from pychron.core.helpers.filetools import add_extension, unique_path2, view_file
from pychron.core.persistence_options import BasePersistenceOptions
from pychron.paths import paths
from pychron.persistence_loggable import dumpable
from pychron.pipeline.tables.base_table_writer import BaseTableWriter
from pychron.pipeline.tables.util import iso_value, value, error, icf_value, icf_error, correction_value, age_value
from pychron.processing.analyses.analysis_group import InterpretedAgeGroup
from pychron.pychron_constants import PLUSMINUS_ONE_SIGMA, PLUSMINUS_NSIGMA, SIGMA, AGE_MA_SCALARS
import six


subreg = re.compile(r'^<sub>(?P<item>\w+)</sub>')
supreg = re.compile(r'^<sup>(?P<item>\w+)</sup>')

DEFAULT_UNKNOWN_NOTES = ('Corrected: Isotopic intensities corrected for blank, baseline, radioactivity decay and '
                         'detector intercalibration, not for interfering reactions.',
                         'Intercepts: t-zero intercept corrected for detector baseline.',
                         'Time interval (days) between end of irradiation and beginning of analysis',

                         'X symbol preceding sample ID denotes analyses excluded from plateau age calculations.',)


class SingleStr(BaseStr):
    def validate(self, obj, name, value):
        if value and len(value) > 1:
            self.error(obj, name, value)
        else:
            return value


class XLSXTableWriterOptions(BasePersistenceOptions):
    table_kind = dumpable(Enum('Fusion', 'Step Heat'))

    power_units = dumpable(Enum('W', 'C'))
    age_units = dumpable(Enum('Ma', 'Ga', 'ka', 'a'))
    hide_gridlines = dumpable(Bool(False))
    include_F = dumpable(Bool(True))
    include_radiogenic_yield = dumpable(Bool(True))
    include_production_ratios = dumpable(Bool(True))
    include_plateau_age = dumpable(Bool(True))
    include_integrated_age = dumpable(Bool(True))
    include_isochron_age = dumpable(Bool(True))
    include_kca = dumpable(Bool(True))
    include_rundate = dumpable(Bool(True))
    include_time_delta = dumpable(Bool(True))
    include_k2o = dumpable(Bool(True))
    include_isochron_ratios = dumpable(Bool(False))
    include_blanks = dumpable(Bool(True))
    include_intercepts = dumpable(Bool(True))

    use_weighted_kca = dumpable(Bool(True))
    repeat_header = dumpable(Bool(False))

    name = dumpable(Str('Untitled'))
    auto_view = dumpable(Bool(False))
    unknown_notes = dumpable(Str('''Errors quoted for individual analyses include analytical error only, without interfering reaction or J uncertainties.
Integrated age calculated by summing isotopic measurements of all steps.
Plateau age is inverse-variance-weighted mean of selected steps.
Plateau age error is inverse-variance-weighted mean error (Taylor, 1982) times root MSWD where MSWD>1.
Plateau error is weighted error of Taylor (1982).
Decay constants and isotopic abundances after {decay_ref:}
Ages calculated relative to FC-2 Fish Canyon Tuff sanidine interlaboratory standard at {monitor_age:} Ma'''))

    unknown_title = dumpable(Str('Ar/Ar analytical data.'))
    air_notes = dumpable(Str(''''''))
    air_title = dumpable(Str(''''''))
    blank_notes = dumpable(Str(''''''))
    blank_title = dumpable(Str(''''''))
    monitor_notes = dumpable(Str(''''''))
    monitor_title = dumpable(Str(''''''))

    include_summary_sheet = dumpable(Bool(True))
    include_summary_age = dumpable(Bool(True))
    include_summary_age_type = dumpable(Bool(True))
    include_summary_material = dumpable(Bool(True))
    include_summary_sample = dumpable(Bool(True))

    include_summary_identifier = dumpable(Bool(True))
    include_summary_unit = dumpable(Bool(True))
    include_summary_location = dumpable(Bool(True))
    include_summary_irradiation = dumpable(Bool(True))
    include_summary_n = dumpable(Bool(True))
    include_summary_percent_ar39 = dumpable(Bool(True))
    include_summary_mswd = dumpable(Bool(True))
    include_summary_kca = dumpable(Bool(True))
    include_summary_comments = dumpable(Bool(True))

    summary_age_nsigma = dumpable(Enum(1, 2, 3))
    summary_kca_nsigma = dumpable(Enum(1, 2, 3))

    plateau_nsteps = dumpable(Int(3))
    plateau_gas_fraction = dumpable(Float(50))
    fixed_step_low = dumpable(SingleStr)
    fixed_step_high = dumpable(SingleStr)

    _persistence_name = 'xlsx_table_options'

    def _table_kind_changed(self):
        if self.table_kind == 'Fusion':
            self.include_summary_percent_ar39 = False
        else:
            self.include_summary_percent_ar39 = True

    @property
    def age_scalar(self):
        return AGE_MA_SCALARS[self.age_units]

    @property
    def path(self):
        name = self.name
        if not name or name == 'Untitled':
            path, _ = unique_path2(paths.table_dir, 'Untitled', extension='.xlsx')
        else:
            path = os.path.join(paths.table_dir, add_extension(name, ext='.xlsx'))
        return path

    def traits_view(self):
        unknown_grp = VGroup(Item('unknown_title', label='Table Heading'),
                             VGroup(UItem('unknown_notes', style='custom'),
                                    show_border=True, label='Notes'), label='Unknowns')

        air_grp = VGroup(Item('air_title', label='Table Heading'),
                         VGroup(UItem('air_notes', style='custom'), show_border=True, label='Notes'), label='Airs')
        blank_grp = VGroup(Item('blank_title', label='Table Heading'),
                           VGroup(UItem('blank_notes', style='custom'), show_border=True, label='Notes'),
                           label='Blanks')
        monitor_grp = VGroup(Item('monitor_title', label='Table Heading'),
                             VGroup(UItem('monitor_notes', style='custom'), show_border=True,
                                    label='Notes'), label='Monitors')

        grp = VGroup(Item('table_kind', label='Kind'),
                     Item('name', label='Filename'),
                     Item('auto_view', label='Open in Excel'),
                     show_border=True)

        appearence_grp = VGroup(Item('hide_gridlines', label='Hide Gridlines'),
                                Item('power_units', label='Power Units'),

                                Item('age_units', label='Age Units'),
                                Item('repeat_header', label='Repeat Header'),
                                show_border=True, label='Appearance')

        arar_col_grp = VGroup(Item('include_F', label='40Ar*/39ArK'),
                              Item('include_radiogenic_yield', label='%40Ar*'),
                              Item('include_kca', label='K/Ca'),
                              Item('use_weighted_kca', label='K/Ca Weighted Mean', enabled_when='include_kca'),
                              Item('include_k2o', label='K2O wt. %'),
                              Item('include_production_ratios', label='Production Ratios'),
                              Item('include_plateau_age', label='Plateau',
                                   visible_when='table_kind=="Step Heat"'),
                              Item('include_integrated_age', label='Integrated',
                                   visible_when='table_kind=="Step Heat"'),
                              Item('include_isochron_age', label='Isochron'),
                              Item('include_isochron_ratios', label='Isochron Ratios'),
                              Item('include_time_delta', label='Time since Irradiation'),
                              label='Ar/Ar')

        general_col_grp = VGroup(Item('include_rundate', label='Analysis RunDate'),
                                 Item('include_blanks', label='Applied Blank'),
                                 Item('include_intercepts', label='Intercepts'),
                                 label='General')
        columns_grp = HGroup(general_col_grp, arar_col_grp,
                             label='Columns', show_border=True)
        g1 = VGroup(grp, columns_grp, appearence_grp, label='Main')

        summary_grp = VGroup(Item('include_summary_sheet', label='Summary Sheet'),
                             VGroup(

                                 Item('include_summary_sample', label='Sample'),
                                 Item('include_summary_identifier', label='Identifier'),
                                 Item('include_summary_unit', label='Unit'),
                                 Item('include_summary_location', label='Location'),
                                 Item('include_summary_material', label='Material'),
                                 Item('include_summary_irradiation', label='Irradiation'),
                                 Item('include_summary_age_type', label='Age Type'),
                                 Item('include_summary_n', label='N'),
                                 Item('include_summary_percent_ar39', label='%39Ar'),
                                 Item('include_summary_mswd', label='MSWD'),
                                 HGroup(Item('include_summary_kca', label='KCA'),
                                        Item('summary_kca_nsigma', label=SIGMA)),
                                 HGroup(Item('include_summary_age', label='Age'),
                                        Item('summary_age_nsigma', label=SIGMA)),
                                 Item('include_summary_comments', label='Comments'),
                                 enabled_when='include_summary_sheet',
                                 label='Columns',
                                 show_border=True),
                             label='Summary')

        plat_grp = VGroup(Item('plateau_nsteps', label='Num. Steps', tooltip='Number of contiguous steps'),
                          Item('plateau_gas_fraction', label='Min. Gas%',
                               tooltip='Plateau must represent at least Min. Gas% release'),
                          HGroup(UItem('fixed_step_low'),
                                 Label('To'),
                                 UItem('fixed_step_high'),
                                 show_border=True,
                                 label='Fixed Steps'),
                          visible_when='table_kind=="Step Heat"',
                          show_border=True,
                          label='Plateau')

        calc_grp = VGroup(plat_grp, label='Calc.')

        v = View(Tabbed(g1, unknown_grp, calc_grp, blank_grp, air_grp, monitor_grp, summary_grp),
                 resizable=True,
                 width=750,
                 title='XLSX Analysis Table Options',
                 buttons=['OK', 'Cancel'])
        return v


class XLSXTableWriter(BaseTableWriter):
    _workbook = None
    _current_row = 0
    _bold = None
    _superscript = None
    _subscript = None

    _options = Instance(XLSXTableWriterOptions)

    def _new_workbook(self, path):
        self._workbook = xlsxwriter.Workbook(add_extension(path, '.xlsx'), {'nan_inf_to_errors': True})

    def build(self, path=None, unknowns=None, airs=None, blanks=None, monitors=None, options=None):
        if options is None:
            options = XLSXTableWriterOptions()

        self._options = options
        if path is None:
            path = options.path
        self.debug('saving table to {}'.format(path))

        self._new_workbook(path)

        self._bold = self._workbook.add_format({'bold': True})
        self._superscript = self._workbook.add_format({'font_script': 1})
        self._subscript = self._workbook.add_format({'font_script': 2})

        if unknowns:
            # make a human optimized table
            self._make_human_unknowns(unknowns)

            # make a machine optimized table
            self._make_machine_unknowns(unknowns)

        if airs:
            self._make_airs(airs)

        if blanks:
            self._make_blanks(blanks)

        if monitors:
            self._make_monitors(monitors)

        if not self._options.include_production_ratios:
            self._make_irradiations(unknowns)

        if self._options.include_summary_sheet:
            self._make_summary_sheet(unknowns)

        self._workbook.close()

        view = self._options.auto_view
        if not view:
            view = confirm(None, 'Table saved to {}\n\nView Table?'.format(path)) == YES

        if view:
            view_file(path, application='Excel')

    # private
    def _get_columns(self, name, grps):

        detectors = {i.detector for g in grps
                     for a in g.analyses
                     for i in a.isotopes.values()}

        options = self._options

        ubit = name in ('Unknowns', 'Monitor')
        bkbit = ubit and options.include_blanks
        ibit = options.include_intercepts

        kcabit = ubit and options.include_kca
        age_units = '({})'.format(options.age_units)
        columns = [(True, '', '', 'status'),
                   (True, 'N', '', 'aliquot_step_str'),
                   (True, 'Tag', '', 'tag'),
                   (ubit, 'Power', options.power_units, 'extract_value'),

                   (ubit, 'Age', age_units, 'age', age_value),
                   (ubit, PLUSMINUS_ONE_SIGMA, age_units, 'age_err_wo_j', age_value),

                   (kcabit, 'K/Ca', '', 'kca', value),
                   (ubit, PLUSMINUS_ONE_SIGMA, '', 'kca', error),

                   (ubit and options.include_radiogenic_yield,
                    ('%', '<sup>40</sup>', 'Ar'), '(%)', 'rad40_percent', value),
                   (ubit and options.include_F,
                    ('<sup>40</sup>', 'Ar*/', '<sup>39</sup>', 'Ar', '<sub>K</sub>'), '', 'uF', value),
                   (ubit and options.include_k2o, ('K', '<sub>2</sub>', 'O'), '(wt. %)', 'k2o', value),
                   (ubit and options.include_isochron_ratios, ('<sup>39</sup>', 'Ar/', '<sup>40</sup>', 'Ar'), '',
                    'isochron3940',
                    value),
                   (ubit and options.include_isochron_ratios, ('<sup>36</sup>', 'Ar/', '<sup>40</sup>', 'Ar'), '',
                    'isochron3640',
                    value),
                   # True, disc/ic corrected
                   (True, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('disc_ic_corrected', ve='error')),

                   # intercepts baseline corrected
                   (ibit, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('intercept', ve='error')),

                   # blanks
                   (bkbit, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('blank', ve='error')),

                   (True, 'Disc', '', 'discrimination', value),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'discrimination', error),

                   ]

        for det in detectors:
            tag = '{}_ic_factor'.format(det)
            columns.extend([(True, ('IC', '<sup>{}</sup>'.format(det)), '', tag, icf_value),
                            (True, PLUSMINUS_ONE_SIGMA, '', tag, icf_error)])

        columns.extend([(options.include_rundate, 'RunDate', '', 'rundate'),
                        (options.include_time_delta, (u'\u0394t', '<sup>3</sup>'), '(days)', 'decay_days'),
                        (ubit, 'J', '', 'j', value),
                        (ubit, PLUSMINUS_ONE_SIGMA, '', 'j', error),
                        (ubit, ('<sup>39</sup>', 'Ar Decay'), '', 'ar39decayfactor', value),
                        (ubit, ('<sup>37</sup>', 'Ar Decay'), '', 'ar37decayfactor', value)])

        if options.include_production_ratios:
            pr = self._get_irradiation_columns(ubit)
            columns.extend(pr)
        else:
            irr = [(ubit, 'Irradiation', '', 'irradiation_label')]
            columns.extend(irr)

        return [c for c in columns if c[0]]

    def _get_machine_columns(self, name):
        options = self._options

        ubit = name in ('Unknowns', 'Monitor')
        bkbit = ubit and options.include_blanks
        ibit = options.include_intercepts

        kcabit = ubit and options.include_kca
        age_units = '({})'.format(options.age_units)
        columns = [(True, '', '', 'status'),
                   (True, 'Identifier', '', 'identifier'),
                   (True, 'Sample', '', 'sample'),
                   (True, 'Material', '', 'material'),
                   (True, 'Project', '', 'project'),
                   (True, 'Tag', '', 'tag'),

                   (True, 'N', '', 'aliquot_step_str'),
                   (ubit, 'Power', options.power_units, 'extract_value'),

                   (ubit, 'Age', age_units, 'age', age_value),
                   (ubit, PLUSMINUS_ONE_SIGMA, age_units, 'age_err_wo_j', age_value),

                   (kcabit, 'K/Ca', '', 'kca', value),
                   (ubit, PLUSMINUS_ONE_SIGMA, '', 'kca', error),

                   (ubit and options.include_radiogenic_yield,
                    ('%', '<sup>40</sup>', 'Ar'), '(%)', 'rad40_percent', value),
                   (ubit and options.include_F,
                    ('<sup>40</sup>', 'Ar*/', '<sup>39</sup>', 'Ar', '<sub>K</sub>'), '', 'uF', value),
                   (ubit and options.include_k2o, ('K', '<sub>2</sub>', 'O'), '(wt. %)', 'k2o', value),
                   (ubit and options.include_isochron_ratios, ('<sup>39</sup>', 'Ar/', '<sup>40</sup>', 'Ar'), '',
                    'isochron3940',
                    value),
                   (ubit and options.include_isochron_ratios, ('<sup>36</sup>', 'Ar/', '<sup>40</sup>', 'Ar'), '',
                    'isochron3640',
                    value),
                   # True, disc/ic corrected
                   (True, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('disc_ic_corrected', ve='error')),
                   (True, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('disc_ic_corrected')),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('disc_ic_corrected', ve='error')),

                   # intercepts baseline corrected
                   (ibit, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('intercept', ve='error')),
                   (ibit, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('intercept')),
                   (ibit, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('intercept', ve='error')),

                   # blanks
                   (bkbit, ('<sup>40</sup>', 'Ar'), '(fA)', 'Ar40', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar40', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>39</sup>', 'Ar'), '(fA)', 'Ar39', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar39', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>38</sup>', 'Ar'), '(fA)', 'Ar38', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar38', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>37</sup>', 'Ar'), '(fA)', 'Ar37', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar37', iso_value('blank', ve='error')),
                   (bkbit, ('<sup>36</sup>', 'Ar'), '(fA)', 'Ar36', iso_value('blank')),
                   (bkbit, PLUSMINUS_ONE_SIGMA, '', 'Ar36', iso_value('blank', ve='error')),

                   (True, 'Disc', '', 'discrimination', value),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'discrimination', error),
                   (True, ('IC', '<sup>CDD</sup>'), '', 'CDD_ic_factor', icf_value),
                   (True, PLUSMINUS_ONE_SIGMA, '', 'CDD_ic_factor', icf_error),

                   (options.include_rundate, 'RunDate', '', 'rundate'),
                   (options.include_time_delta, (u'\u0394t', '<sup>3</sup>'), '(days)', 'decay_days'),
                   (ubit, 'J', '', 'j', value),
                   (ubit, PLUSMINUS_ONE_SIGMA, '', 'j', error),
                   (ubit, ('<sup>39</sup>', 'Ar Decay'), '', 'ar39decayfactor', value),
                   (ubit, ('<sup>37</sup>', 'Ar Decay'), '', 'ar37decayfactor', value)]

        if options.include_production_ratios:
            pr = self._get_irradiation_columns(ubit)
            columns.extend(pr)
        else:
            irr = [(ubit, 'Irradiation', '', 'irradiation_label')]
            columns.extend(irr)

        return [c for c in columns if c[0]]

    def _get_irradiation_columns(self, ubit):
        cols = [(ubit, ('(', '<sup>40</sup>', 'Ar/', '<sup>39</sup>', 'Ar)', '<sub>K</sub>'), '', 'K4039',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'K4039', correction_value(ve='error')),
                (ubit, ('(', '<sup>38</sup>', 'Ar/', '<sup>39</sup>', 'Ar)', '<sub>K</sub>'), '', 'K3839',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'K3839', correction_value(ve='error')),
                (ubit, ('(', '<sup>37</sup>', 'Ar/', '<sup>39</sup>', 'Ar)', '<sub>K</sub>'), '', 'K3739',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'K3739', correction_value(ve='error')),
                (ubit, ('(', '<sup>39</sup>', 'Ar/', '<sup>37</sup>', 'Ar)', '<sub>Ca</sub>'), '', 'Ca3937',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Ca3937', correction_value(ve='error')),
                (ubit, ('(', '<sup>38</sup>', 'Ar/', '<sup>37</sup>', 'Ar)', '<sub>Ca</sub>'), '', 'Ca3837',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Ca3837', correction_value(ve='error')),
                (ubit, ('(', '<sup>36</sup>', 'Ar/', '<sup>37</sup>', 'Ar)', '<sub>Ca</sub>'), '', 'Ca3637',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Ca3637', correction_value(ve='error')),
                (ubit, ('(', '<sup>36</sup>', 'Ar/', '<sup>38</sup>', 'Ar)', '<sub>Cl</sub>'), '', 'Cl3638',
                 correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Cl3638', correction_value(ve='error')),
                (ubit, 'Ca/K', '', 'Ca_K', correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Ca_K', correction_value(ve='error')),
                (ubit, 'Cl/K ', '', 'Cl_K', correction_value()),
                (ubit, PLUSMINUS_ONE_SIGMA, '', 'Cl_K', correction_value(ve='error'))]
        return cols

    def _get_summary_columns(self):
        opt = self._options

        def get_kca_error(ag, *args):
            return std_dev(ag.weighted_kca) * opt.summary_kca_nsigma

        def get_preferred_age_kind(ag, *args):
            ret = ''
            if isinstance(ag, InterpretedAgeGroup):
                ret = ag.preferred_age_kind
            return ret

        def get_preferred_age(ag, *args):
            return nominal_value(ag.preferred_age)

        def get_preferred_age_error(ag, *args):
            return std_dev(ag.preferred_age) * opt.summary_age_nsigma

        is_step_heat = opt.table_kind == 'Step Heat'
        age_units = '({})'.format(opt.age_units)

        cols = [(opt.include_summary_sample, 'Sample', '', 'sample'),
                (opt.include_summary_identifier, 'Identifier', '', 'identifier'),
                (opt.include_summary_unit, 'Unit', '', 'unit'),
                (opt.include_summary_location, 'Location', '', 'location'),
                (opt.include_summary_irradiation, 'Irradiation', '', 'irradiation_label'),
                (opt.include_summary_material, 'Material', '', 'material'),

                (opt.include_summary_age, 'Age Type', '', '', get_preferred_age_kind),
                # (opt.include_summary_age, 'Age Type', '', 'preferred_age_kind'),

                (opt.include_summary_n, 'N', '', 'nanalyses'),
                (opt.include_summary_percent_ar39, ('%', '<sup>39</sup>', 'Ar'), '', 'percent_39Ar'),
                (opt.include_summary_mswd, 'MSWD', '', 'mswd'),
                (opt.include_summary_kca, 'K/Ca', '', 'weighted_kca', value),

                (opt.include_summary_kca, PLUSMINUS_NSIGMA.format(opt.summary_kca_nsigma), '', 'weighted_kca',
                 get_kca_error),

                (opt.include_summary_age, 'Age {}'.format(age_units), '', '', get_preferred_age),

                (opt.include_summary_age, PLUSMINUS_NSIGMA.format(opt.summary_age_nsigma), '', '',
                 get_preferred_age_error),

                (opt.include_summary_comments, 'Comments', '', None),

                # Hidden Cols
                (True, 'WeightedMeanAge', '', 'weighted_age', value),
                (True, PLUSMINUS_ONE_SIGMA, '', 'weighted_age', error),
                (True, 'ArithmeticMeanAge', '', 'arith_age', value),
                (True, PLUSMINUS_ONE_SIGMA, '', 'arith_age', error),
                (True, 'IsochronAge', '', 'isochron_age', value),
                (True, PLUSMINUS_ONE_SIGMA, '', 'isochron_age', error),
                (is_step_heat, 'PlateauAge', '', 'plateau_age', value),
                (is_step_heat, PLUSMINUS_ONE_SIGMA, '', 'plateau_age', error),
                (is_step_heat, 'IntegratedAge', '', 'integrated_age', value),
                (is_step_heat, PLUSMINUS_ONE_SIGMA, '', 'integrated_age', error),
                ]
        return cols

    def _make_human_unknowns(self, unks):
        self._make_sheet(unks, 'Unknowns')

    def _make_machine_unknowns(self, unks):
        self._make_machine_sheet(unks, 'Unknowns (Machine)')

    def _make_airs(self, airs):
        self._make_sheet(airs, 'Airs')

    def _make_blanks(self, blanks):
        self._make_sheet(blanks, 'Blanks')

    def _make_monitors(self, monitors):
        self._make_sheet(monitors, 'Monitors')

    def _make_summary_sheet(self, unks):
        self._current_row = 1
        sh = self._workbook.add_worksheet('Summary')
        self._format_generic_worksheet(sh)

        cols = self._get_summary_columns()
        cols = [c for c in cols if c[0]]
        self._make_title(sh, 'Summary', cols)

        fmt = self._workbook.add_format({'bottom': 1, 'align': 'center'})
        sh.set_row(self._current_row, 5)
        self._current_row += 1

        idx = next((i for i, c in enumerate(cols) if c[1] == 'Age Type'), 6)
        idx_e = next((i for i, c in enumerate(cols) if c[1] == 'Age'), 12) + 1
        # sh.write_rich_string(self._current_row, idx, 'Preferred Age', border)
        sh.merge_range(self._current_row, idx, self._current_row, idx_e, 'Preferred Age', cell_format=fmt)

        # hide extra age columns
        for hidden in ('WeightedMeanAge', 'ArithmeticMeanAge', 'IsochronAge', 'PlateauAge', 'IntegratedAge'):
            hc = next((i for i, c in enumerate(cols) if c[1] == hidden), None)
            if hc is not None:
                sh.set_column(hc, hc + 1, options={'hidden': True})

        self._current_row += 1
        sh.set_row(self._current_row, 5)
        self._current_row += 1
        self._write_header(sh, cols, include_units=False)
        center = self._workbook.add_format({'align': 'center'})
        for ug in unks:
            ug.set_temporary_age_units(self._options.age_units)
            for i, ci in enumerate(cols):
                txt = self._get_txt(ug, ci)
                sh.write(self._current_row, i, txt, center)
            self._current_row += 1
            ug.set_temporary_age_units(None)

        self._make_notes(sh, len(cols), 'summary')

    def _make_irradiations(self, unks):
        self._current_row = 1
        sh = self._workbook.add_worksheet('Irradiations')
        self._format_generic_worksheet(sh)
        cols = [(True, 'Name', '', 'irradiation')]
        icols = self._get_irradiation_columns(True)
        cols.extend(icols)

        # write header
        self._write_header(sh, cols, include_units=True)

        cols = [c for c in cols if c[0]]
        for ug in unks:
            for i, ci in enumerate(cols):
                try:
                    txt = self._get_txt(ug.analyses[0], ci)
                except AttributeError as e:
                    txt = self._get_txt(ug, ci)

                sh.write(self._current_row, i, txt)
            self._current_row += 1

    def _make_sheet(self, groups, name):
        self._current_row = 1

        worksheet = self._workbook.add_worksheet(name)

        cols = self._get_columns(name, groups)
        self._format_worksheet(worksheet, cols)

        self._make_title(worksheet, name, cols)

        repeat_header = self._options.repeat_header

        for i, group in enumerate(groups):
            group.set_temporary_age_units(self._options.age_units)

            self._make_meta(worksheet, group)
            if repeat_header or i == 0:
                self._make_column_header(worksheet, cols, i)

            n = len(group.analyses) - 1
            for i, item in enumerate(group.analyses):
                ounits = item.arar_constants.age_units
                item.arar_constants.age_units = self._options.age_units
                self._make_analysis(worksheet, cols, item, i == n)
                item.arar_constants.age_units = ounits

            self._make_summary(worksheet, cols, group)
            self._current_row += 1

            group.set_temporary_age_units(None)

        self._make_notes(worksheet, len(cols), name)
        self._current_row = 1

    def _make_machine_sheet(self, groups, name):
        self._current_row = 1
        worksheet = self._workbook.add_worksheet(name)

        cols = self._get_machine_columns(name)
        self._format_worksheet(worksheet, cols)

        self._make_title(worksheet, name, cols)

        repeat_header = self._options.repeat_header

        for i, group in enumerate(groups):
            if repeat_header or i == 0:
                self._make_column_header(worksheet, cols, i)

            n = len(group.analyses) - 1
            for i, item in enumerate(group.analyses):
                self._make_analysis(worksheet, cols, item, i == n)
            self._current_row += 1

        self._current_row = 1

    def _format_generic_worksheet(self, sh):
        if self._options.hide_gridlines:
            sh.hide_gridlines(2)

    def _format_worksheet(self, sh, cols):
        self._format_generic_worksheet(sh)
        if self._options.include_rundate:
            idx = next((i for i, c in enumerate(cols) if c[1] == 'RunDate'))
            sh.set_column(idx, idx, 12)

        sh.set_column(0, 0, 2)
        if not self._options.repeat_header:
            sh.freeze_panes(7, 2)

    def _make_title(self, sh, name, cols):
        try:
            title = getattr(self._options, '{}_title'.format(name.lower()[:-1]))
        except AttributeError:
            title = None

        fmt = self._workbook.add_format({'font_size': 14, 'bold': True,
                                         'bottom': 6 if not title else 0})
        sh.write_rich_string(self._current_row, 0, 'Table X. {}'.format(name), fmt)
        if title:
            self._current_row += 1
            sh.write_rich_string(self._current_row, 0, title)

        for i in range(1, len(cols)):
            sh.write_blank(self._current_row, i, '', cell_format=fmt)
        self._current_row += 1

    def _make_column_header(self, sh, cols, it):

        start = next((i for i, c in enumerate(cols) if c[3] == 'Ar40'), 9)

        if self._options.repeat_header and it > 0:
            sh.write(self._current_row, start, 'Corrected')
            sh.write(self._current_row, start + 10, 'Intercepts')
        else:
            sh.write_rich_string(self._current_row, start, 'Corrected', self._superscript, '1')
            sh.write_rich_string(self._current_row, start + 10, 'Intercepts', self._superscript, '2')

        sh.write(self._current_row, start + 20, 'Blanks')
        self._current_row += 1
        self._write_header(sh, cols)

    def _write_header(self, sh, cols, include_units=True):
        names, units = self._get_names_units(cols)

        border = self._workbook.add_format({'bottom': 2, 'align': 'center'})
        center = self._workbook.add_format({'align': 'center'})
        if include_units:
            t = ((names, False), (units, True))
        else:
            t = ((names, True),)

        for items, use_border in t:
            row = self._current_row
            for i, ci in enumerate(items):
                if isinstance(ci, tuple):
                    args = []
                    for cii in ci:
                        for reg, fmt in ((supreg, self._superscript),
                                         (subreg, self._subscript)):
                            m = reg.match(cii)
                            if m:
                                args.append(fmt),
                                args.append(m.group('item'))
                                break
                        else:
                            args.append(cii)

                    if not use_border:
                        args.append(center)
                    else:
                        args.append(border)
                    sh.write_rich_string(row, i, *args)
                else:
                    if use_border:
                        # border.set_align('center')
                        sh.write_rich_string(row, i, ci, border)
                    else:
                        sh.write_rich_string(row, i, ci, center)
            self._current_row += 1

    def _make_meta(self, sh, group):
        fmt = self._bold
        row = self._current_row
        sh.write_rich_string(row, 1, 'Sample:', fmt)
        sh.write_rich_string(row, 2, group.sample, fmt)

        sh.write_rich_string(row, 5, 'Identifier:', fmt)
        sh.write_rich_string(row, 6, group.identifier, fmt)

        self._current_row += 1

        row = self._current_row
        sh.write_rich_string(row, 1, 'Material:', fmt)
        sh.write_rich_string(row, 2, group.material, fmt)
        self._current_row += 1

    def _make_analysis(self, sh, cols, item, last):
        status = 'X' if item.is_omitted() else ''
        row = self._current_row

        border = self._workbook.add_format({'bottom': 1})
        fmt2 = self._workbook.add_format()
        fmt3 = self._workbook.add_format()
        fmt4 = self._workbook.add_format()
        fmt = []
        if last:
            fmt2 = self._workbook.add_format({'bottom': 1})
            fmt3 = self._workbook.add_format({'bottom': 1})
            fmt = [border]
        fmt2.set_align('center')
        fmt3.set_num_format('mm/dd/yy hh:mm')
        fmt4.set_num_format('0.0000000')
        sh.write(row, 0, status, *fmt)
        for j, c in enumerate(cols[1:]):
            txt = self._get_txt(item, c)

            if c[1] in ('N', 'Power'):
                sh.write(row, j + 1, txt, fmt2)
            elif c[1] == 'RunDate':
                sh.write_datetime(row, j + 1, txt, fmt3)
            elif c[3] == 'j':
                sh.write_number(row, j+1, txt, fmt4)
            else:
                sh.write(row, j + 1, txt, *fmt)

        self._current_row += 1

    def _make_summary(self, sh, cols, group):
        fmt = self._bold
        start_col = 0
        if self._options.include_kca:
            idx = next((i for i, c in enumerate(cols) if c[1] == 'K/Ca'))
            sh.write_rich_string(self._current_row, start_col, u'K/Ca {}'.format(PLUSMINUS_ONE_SIGMA), fmt)
            kca = group.weighted_kca if self._options.use_weighted_kca else group.arith_kca
            sh.write(self._current_row, idx, nominal_value(kca))
            sh.write(self._current_row, idx + 1, std_dev(kca))
            self._current_row += 1

        idx = next((i for i, c in enumerate(cols) if c[1] == 'Age'))

        sh.write_rich_string(self._current_row, start_col, u'Weighted Mean Age {}'.format(PLUSMINUS_ONE_SIGMA), fmt)
        sh.write(self._current_row, idx, nominal_value(group.weighted_age))
        sh.write(self._current_row, idx + 1, std_dev(group.weighted_age))

        sh.write_rich_string(self._current_row, idx + 2, 'n={}/{}'.format(group.nanalyses, group.total_n), fmt)

        self._current_row += 1
        if self._options.table_kind == 'Step Heat':
            if self._options.include_plateau_age and hasattr(group, 'plateau_age'):
                sh.write_rich_string(self._current_row, start_col, u'Plateau {}'.format(PLUSMINUS_ONE_SIGMA), fmt)
                sh.write(self._current_row, 3, 'steps {}'.format(group.plateau_steps_str))
                sh.write(self._current_row, idx, nominal_value(group.plateau_age))
                sh.write(self._current_row, idx + 1, std_dev(group.plateau_age))

                self._current_row += 1

            if self._options.include_integrated_age and hasattr(group, 'integrated_age'):
                sh.write_rich_string(self._current_row, start_col, u'Integrated Age {}'.format(PLUSMINUS_ONE_SIGMA),
                                     fmt)
                sh.write(self._current_row, idx, nominal_value(group.integrated_age))
                sh.write(self._current_row, idx + 1, std_dev(group.integrated_age))

                self._current_row += 1

        if self._options.include_isochron_age:
            sh.write_rich_string(self._current_row, start_col, u'Isochron Age {}'.format(PLUSMINUS_ONE_SIGMA),
                                 fmt)
            sh.write(self._current_row, idx, nominal_value(group.isochron_age))
            sh.write(self._current_row, idx + 1, std_dev(group.isochron_age))

            self._current_row += 1

    def _make_notes(self, sh, ncols, name):
        top = self._workbook.add_format({'top': 1})
        sh.write_rich_string(self._current_row, 0, self._bold, 'Notes:', top)
        for i in range(1, ncols):
            sh.write_blank(self._current_row, i, 'Notes:', cell_format=top)
        self._current_row += 1

        func = getattr(self, '_make_{}_notes'.format(name.lower()))
        func(sh)

        for i in range(0, ncols):
            sh.write_blank(self._current_row, i, 'Notes:', cell_format=top)

    def _make_summary_notes(self, sh):
        sh.write(self._current_row, 0, 'Plateau Criteria:')
        self._current_row += 1

        sh.write(self._current_row, 0, '\t\tN Steps= {}'.format(self._options.plateau_nsteps))
        self._current_row += 1

        sh.write(self._current_row, 0, '\t\tGas Fraction= {}'.format(self._options.plateau_gas_fraction))
        self._current_row += 1
        if self._options.fixed_step_low or self._options.fixed_step_high:
            sh.write(self._current_row, 0, '\t\tFixed Steps= {},{}'.format(self._options.fixed_step_low,
                                                                           self.fixed_step_high))
            self._current_row += 1

    def _make_unknowns_notes(self, sh):
        monitor_age = 28.201
        decay_ref = u'Steiger and J\u00E4ger (1977)'
        notes = six.text_type(self._options.unknown_notes)
        notes = notes.format(monitor_age=monitor_age, decay_ref=decay_ref)

        sh.write_rich_string(self._current_row, 0, self._superscript, '1', DEFAULT_UNKNOWN_NOTES[0])
        self._current_row += 1
        sh.write_rich_string(self._current_row, 0, self._superscript, '2', DEFAULT_UNKNOWN_NOTES[1])
        self._current_row += 1
        if self._options.include_time_delta:
            sh.write_rich_string(self._current_row, 0, self._superscript, '3', DEFAULT_UNKNOWN_NOTES[2])
            self._current_row += 1

        sh.write(self._current_row, 0, DEFAULT_UNKNOWN_NOTES[3])
        self._current_row += 1

        self._write_notes(sh, notes)

    def _make_blanks_notes(self, sh):
        notes = six.text_type(self._options.blank_notes)
        self._write_notes(sh, notes)

    def _make_airs_notes(self, sh):
        notes = six.text_type(self._options.air_notes)
        self._write_notes(sh, notes)

    def _make_monitor_notes(self, sh):
        notes = six.text_type(self._options.monitor_notes)
        self._write_notes(sh, notes)

    def _write_notes(self, sh, notes):
        for line in notes.split('\n'):
            sh.write(self._current_row, 0, line)
            self._current_row += 1

    def _get_names_units(self, cols):
        names = [c[1] for c in cols]
        units = [c[2] for c in cols]
        return names, units

    def _get_txt(self, item, col):
        attr = col[3]
        if attr is None:
            return ''

        if len(col) == 5:
            getter = col[4]
        else:
            getter = getattr

        if getter is None:
            return ''
        else:
            return getter(item, attr)


if __name__ == '__main__':
    x = XLSXTableWriter()

    from random import random
    from datetime import datetime


    def frand(digits, scalar=1):
        return round(scalar * random(), digits)


    class Iso:
        def __init__(self, name):
            self.name = name
            self.uvalue = ufloat(frand(10, 10), frand(10))
            self.blank = Blank(name)

        def get_intensity(self):
            return ufloat(frand(10, 10), frand(10))


    class Blank:
        def __init__(self, name):
            self.name = name
            self.uvalue = ufloat(frand(10, 1), frand(10))

        def get_intensity(self):
            return ufloat(frand(10, 1), frand(10))


    class A:
        def __init__(self, a):
            self.identifier = 'Foo'
            self.project = 'Bar'
            self.material = 'Moo'
            self.sample = 'Bat'
            self.aliquot_step_str = a
            self.isotopes = {'Ar40': Iso('Ar40'),
                             'Ar39': Iso('Ar39'),
                             'Ar38': Iso('Ar38'),
                             'Ar37': Iso('Ar37'),
                             'Ar36': Iso('Ar36')}
            self.tag = 'ok'
            self.aliquot_step_str = '01'
            self.extract_value = frand(1)
            self.kca = ufloat(frand(2), frand(2))
            self.age = frand(10, 10)
            self.age_err_wo_j = frand(10)
            self.discrimination = 0
            self.j = 0

            self.ar39decayfactor = 0
            self.ar37decayfactor = 0
            self.interference_corrections = {}
            self.production_ratios = {'Ca_K': 1.312}
            self.uF = ufloat(frand(10, 10), frand(10))
            self.rad40_percent = frand(3, 100)
            self.rundate = datetime.now()
            self.decay_days = frand(2, 200)
            self.k2o = frand(2)
            self.irradiation_label = 'NM-284 E9'
            self.irradiation = 'NM-284'
            self.isochron3940 = ufloat(frand(10), frand(10))
            self.isochron3640 = ufloat(frand(10), frand(10))

        def get_ic_factor(self, det):
            return 1
            # def __getattr__(self, item):
            #     return 0


    class G:
        sample = 'MB-1234'
        material = 'Groundmass'
        identifier = '13234'
        analyses = [A('01'), A('02')]
        arith_age = 132
        weighted_age = 10.01
        plateau_age = 123
        integrated_age = 1231
        plateau_steps_str = 'A-F'
        isochron_age = 123323
        weighted_kca = 1412
        arith_kca = 0.123
        preferred_age = 1213.123
        unit = ''
        location = ''
        mswd = frand(10)
        irradiation_label = 'Foo'
        preferred_age_kind = 'Plateau'
        nanalyses = 2
        percent_39Ar = 0.1234


    g = G()
    p = '/Users/ross/Sandbox/testtable.xlsx'
    paths.build('_dev')
    options = XLSXTableWriterOptions()
    options.configure_traits()
    x.build(path=p, unknowns=[g, g], options=options)
    options.dump()
    # app_path = '/Applications/Microsoft Office 2011/Microsoft Excel.app'
    #
    # try:
    #     subprocess.call(['open', '-a', app_path, p])
    # except OSError:
    #     subprocess.call(['open', p])
# ============= EOF =============================================
