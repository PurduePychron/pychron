# ===============================================================================
# Copyright 2012 Jake Ross
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
import os

from pychron.core.helpers.formatting import floatfmt
from pychron.core.yaml import yload
from pychron.paths import paths

STARTUP_MESSAGE_POSITION = (100, 300)

SPECTROMETER_PROTOCOL = 'pychron.spectrometer.base_spectrometer_manager.BaseSpectrometerManager'
ION_OPTICS_PROTOCOL = 'pychron.spectrometer.ion_optics_manager.IonOpticsManager'
SCAN_PROTOCOL = 'pychron.spectrometer.scan_manager.ScanManager'
EL_PROTOCOL = 'pychron.extraction_line.extraction_line_manager.ExtractionLineManager'
DVC_PROTOCOL = 'pychron.dvc.dvc.DVC'
FURNACE_PROTOCOL = 'pychron.furnace.furnace_manager.BaseFurnaceManager'

TTF_FONTS = ['Andale Mono', 'Arial', 'Arial Black',
             'Calibri', 'Cambria', 'Comic Sans MS', 'Consolas', 'Courier New',
             'Georgia',
             'Helvetica',
             'Impact',
             'Trebuchet MS',
             'Verdana']

FONTS = TTF_FONTS
SIZES = [10, 6, 8, 9, 10, 11, 12, 14, 15, 18, 24, 36]

try:
    from kiva.fonttools.font_manager import fontManager

    fontManager.defaultFamily = {'ttf': 'Arial', 'afm': 'Arial'}
except ImportError:
    pass

PLUSMINUS = '\N{Plus-minus sign}'
SIGMA = '\N{Greek Small Letter Sigma}'
LAMBDA = '\u03BB'
DELTA = '\N{Greek Capital Letter Delta}'

PLUSMINUS_NSIGMA = '{}{{}}{}'.format(PLUSMINUS, SIGMA)
PLUSMINUS_ONE_SIGMA = PLUSMINUS_NSIGMA.format(1)
PLUSMINUS_TWO_SIGMA = PLUSMINUS_NSIGMA.format(2)
PLUSMINUS_PERCENT = '{}%  '.format(PLUSMINUS)
SPECIAL_IDENTIFIER = 'Special Identifier'
NULL_STR = '---'
LINE_STR = '---------'
TOP = 'Top'
BOTTOM = 'Bottom'
AUTO_SCROLL_KINDS = (NULL_STR, TOP, BOTTOM)

MEASUREMENT = 'measurement'
POST_MEASUREMENT = 'post_measurement'
POST_EQUILIBRATION = 'post_equilibration'
EXTRACTION = 'extraction'
EM_SCRIPT_KEYS = (EXTRACTION, MEASUREMENT)
SCRIPT_KEYS = [MEASUREMENT, POST_MEASUREMENT, EXTRACTION, POST_EQUILIBRATION]

SCRIPT_NAMES = ['{}_script'.format(si) for si in SCRIPT_KEYS]

SE = 'SE'
SD = 'SD'
SEM = 'SEM'
MSEM = 'SEM, but if MSWD>1 use SEM * sqrt(MSWD)'
MSE = 'SE but if MSWD>1 use SE * sqrt(MSWD)'

ERROR_TYPES = [MSEM, SEM, SD]
SIG_FIGS = range(0, 15)
STD_SIG_FIGS = ['Std', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]

WEIGHTED_MEAN = 'Weighted Mean'
PLATEAU = 'Plateau'
INTEGRATED = 'Total Integrated'
DEFAULT_INTEGRATED = '{} else Valid Integrated'.format(PLATEAU)
VALID_INTEGRATED = 'Valid Integrated'
PLATEAU_INTEGRATED = '{} Integrated'.format(PLATEAU)

FIT_TYPES = ['Linear', 'Parabolic', 'Cubic',
             'Average', 'Exponential', WEIGHTED_MEAN]

FIT_ERROR_TYPES = [SD, SEM, MSEM, 'CI', 'MonteCarlo']
SERIES_FIT_TYPES = [NULL_STR] + FIT_TYPES
ISOCHRON_ERROR_TYPES = [SE, MSE]

INTERPOLATE_TYPES = ['Preceding', 'Bracketing Interpolate', 'Bracketing Average', 'Succeeding']
FIT_TYPES_INTERPOLATE = FIT_TYPES + INTERPOLATE_TYPES

ARITHMETIC_MEAN = 'Arithmetic Mean'
PLATEAU_ELSE_WEIGHTED_MEAN = 'Plateau else Weighted Mean'
ISOCHRON = 'Isochron'
ISOCHRON_PLATEAU = '{} of {} Steps'.format(ISOCHRON, PLATEAU)

AGE_SUBGROUPINGS = (PLATEAU_ELSE_WEIGHTED_MEAN, WEIGHTED_MEAN,
                    INTEGRATED, VALID_INTEGRATED, PLATEAU_INTEGRATED, DEFAULT_INTEGRATED,
                    ARITHMETIC_MEAN, PLATEAU, ISOCHRON, ISOCHRON_PLATEAU)
SUBGROUPINGS = [WEIGHTED_MEAN,
                INTEGRATED, VALID_INTEGRATED, PLATEAU_INTEGRATED, DEFAULT_INTEGRATED,
                ARITHMETIC_MEAN]

SUBGROUPING_ATTRS = ('age', 'kca', 'kcl', 'radiogenic_yield', 'moles_k39', 'signal_k39')

FLECK_PLATEAU_DEFINITION = 'X contiguous Steps, Representing >Y% of the gas, Overlapping at 2 sigma'
MAHON_PLATEAU_DEFINITION = 'X contiguous Steps, Representing >Y% of the gas, ' \
                           'with all plateau steps yielding a valid MSWD'

FLECK = 'Fleck 1977'
MAHON = 'Mahon 1996'

OMIT = 'omit'
INVALID = 'invalid'
OUTLIER = 'outlier'
SKIP = 'skip'
OMIT_ISOCHRON = 'omit_isochron'

EXCLUDE_TAGS = (OMIT, INVALID, OUTLIER, SKIP)

WEIGHTINGS = (NULL_STR, 'Volume', 'Variance')

INVALID_MSWD_CHR = '*'


def format_mswd(m, v, n=3, include_tag=False):
    tag = ''
    if include_tag:
        if isinstance(include_tag, str):
            tag = include_tag
        else:
            tag = 'MSWD='

    return '{}{}{}'.format(tag, '' if v else INVALID_MSWD_CHR, floatfmt(m, n=n))


DELIMITERS = {',': 'comma', '\t': 'tab', ' ': 'space'}

# AGE_SCALARS = {'Ga': 1e9, 'Ma': 1e6, 'ka': 1e3, 'a': 1}
# AGE_MA_SCALARS = {'Ma': 1, 'ka': 1e-3, 'a': 1e-6, 'Ga': 1e3}

DESCENDING = 'Descending'
ASCENDING = 'Ascending'
AGE_SORT_KEYS = (NULL_STR, ASCENDING, DESCENDING)

UNKNOWN = 'unknown'
COCKTAIL = 'cocktail'
BLANK = 'blank'
DETECTOR_IC = 'detector_ic'
PAUSE = 'pause'
DEGAS = 'degas'
AIR = 'air'
BACKGROUND = 'background'

BLANK_UNKNOWN = 'blank_unknown'
BLANK_EXTRACTIONLINE = 'blank_extractionline'
BLANK_TYPES = [BLANK_UNKNOWN, 'blank_air', 'blank_cocktail']

SNIFF = 'sniff'
SIGNAL = 'signal'
BASELINE = 'baseline'
WHIFF = 'whiff'

EXTRACT_DEVICE = 'Extract Device'
NO_EXTRACT_DEVICE = 'No Extract Device'

NO_BLANK_CORRECT = (BLANK, DETECTOR_IC, BACKGROUND)

MAIN = 'Main'
APPEARANCE = 'Appearance'
SPECTRUM = 'Spectrum'
ISOCHRON = 'Isochron'
IDEOGRAM = 'Ideogram'
DISPLAY = 'Display'
GROUPS = 'Groups'
CALCULATIONS = 'Calculations'
INSET = 'Inset'

INTERFERENCE_KEYS = ('K4039', 'K3839', 'K3739', 'Ca3937', 'Ca3837', 'Ca3637', 'Cl3638')
RATIO_KEYS = ('Ca_K', 'Cl_K')

AR40 = 'Ar40'
AR39 = 'Ar39'
AR38 = 'Ar38'
AR37 = 'Ar37'
AR36 = 'Ar36'

ARGON_KEYS = (AR40, AR39, AR38, AR37, AR36)

ARAR_MAPPING = dict({k: v for k, v in zip(ARGON_KEYS, ARGON_KEYS)})

IRRADIATION_KEYS = [('k4039', 'K_40_Over_39'),
                    ('k3839', 'K_38_Over_39'),
                    ('k3739', 'K_37_Over_39'),
                    ('ca3937', 'Ca_39_Over_37'),
                    ('ca3837', 'Ca_38_Over_37'),
                    ('ca3637', 'Ca_36_Over_37'),
                    ('cl3638', 'P36Cl_Over_38Cl')]

DECAY_KEYS = [('a37decayfactor', '37_Decay'),
              ('a39decayfactor', '39_Decay')]

MEASUREMENT_COLOR = '#FF7EDF'  # magenta
EXTRACTION_COLOR = '#FFFF66'
SUCCESS_COLOR = '#66FF33'  # light green
SKIP_COLOR = '#33CCFF'
CANCELED_COLOR = '#FF9999'
TRUNCATED_COLOR = 'orange'
FAILED_COLOR = 'red'
END_AFTER_COLOR = 'gray'
NOT_EXECUTABLE_COLOR = 'red'

LIGHT_RED = '#FF7373'
LIGHT_YELLOW = '#F7F6D0'
LIGHT_GREEN = '#99FF99'

DETECTOR_ORDER = ['H2', 'H1', 'AX', 'L1', 'L2', 'CDD']
DETECTOR_MAP = {o: i for i, o in enumerate(DETECTOR_ORDER)}

IC_ANALYSIS_TYPE_MAP = {'air': 0, 'cocktail': 1}

QTEGRA_INTEGRATION_TIMES = [0.065536, 0.131072, 0.262144, 0.524288,
                            1.048576, 2.097152, 4.194304, 8.388608,
                            16.777216, 33.554432, 67.108864]
QTEGRA_DEFAULT_INTEGRATION_TIME = 1.048576
ISOTOPX_INTEGRATION_TIMES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 2.0, 3.0, 4.0, 5.0, 10.0, 20.0]
ISOTOPX_DEFAULT_INTEGRATION_TIME = 1

DEFAULT_INTEGRATION_TIME = 1

K_DECAY_CONSTANTS = {'Min et al., 2000': (5.80e-11, 0.099e-10, 4.883e-10, 0.014e-10),
                     'Steiger & Jager 1977': (5.81e-11, 0, 4.962e-10, 0)}

FLUX_CONSTANTS = {'FC Min': {'lambda_ec': [5.80e-11, 0.099e-10], 'lambda_b': [4.883e-10, 0.014e-10],
                             'monitor_name': 'FC-2',
                             'monitor_material': 'Sanidine',
                             'monitor_age': 28.201},
                  'FC SJ': {'lambda_ec': [5.81e-11, 0],
                            'lambda_b': [4.962e-10, 0],
                            'monitor_name': 'FC-2',
                            'monitor_material': 'Sanidine',
                            'monitor_age': 28.02}}

LEAST_SQUARES_1D = 'LeastSquares1D'
WEIGHTED_MEAN_1D = 'WeightedMean1D'
MATCHING = 'Matching'
BRACKETING = 'Bracketing'
NN = 'Nearest Neighbors'
PLANE = 'Plane'
BOWL = 'Bowl'
FLUX_MODEL_KINDS = PLANE, BOWL, WEIGHTED_MEAN, MATCHING, NN, BRACKETING, LEAST_SQUARES_1D, WEIGHTED_MEAN_1D

if paths.setup_dir:
    flux_constants = os.path.join(paths.setup_dir, 'flux_constants.yaml')
    if os.path.isfile(flux_constants):
        with open(flux_constants, 'r') as rf:
            obj = yload(rf)
            try:
                FLUX_CONSTANTS.update(obj)
            except BaseException:
                pass

AR_AR = 'Ar/Ar'

QTEGRA_SOURCE_KEYS = ('extraction_lens', 'ysymmetry', 'zsymmetry', 'zfocus')
QTEGRA_SOURCE_NAMES = ('ExtractionLens', 'Y-Symmetry', 'Z-Symmetry', 'Z-Focus')

BLANKS = ['Blank Unknown', 'Blank Air', 'Blank Cocktail', 'Blank']
REFERENCE_ANALYSIS_TYPES = ['Air', 'Cocktail', 'IC']
ANALYSIS_TYPES = ['Unknown'] + REFERENCE_ANALYSIS_TYPES + BLANKS

DEFAULT_MONITOR_NAME = 'FC-2'

ELLIPSE_KINDS = ('1' + SIGMA, '2' + SIGMA, '95%')
ELLIPSE_KIND_SCALE_FACTORS = dict(zip(ELLIPSE_KINDS, (1, 2, 2.4477)))

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

DEFAULT_PIPELINE_ROOTS = ('Fit', 'Edit', 'Plot', 'Table', 'History', 'Share', 'Transfer', 'MDD', 'User')

# SAMPLE PREP ===================================================
INITIAL_STEPS = ('crush', 'sieve', 'wash')
HIGH_GRADE_STEPS = ('frantz', 'heavy_liquid', 'gold_table', 'acid', 'pick')
IMAGE_STEPS = ('mount', 'us_wand', 'eds', 'cl', 'bse', 'se')

SAMPLE_PREP_STEPS = INITIAL_STEPS + HIGH_GRADE_STEPS + IMAGE_STEPS

SAMPLE_METADATA = ('sample',
                   'material',
                   'grainsize',
                   'project',
                   'principal_investigator',
                   'latitude',
                   'longitude',
                   'unit',
                   'lithology',
                   'lithology_class',
                   'lithology_group',
                   'lithology_type',
                   'rlocation',
                   'irradiation',
                   'irradiation_level',
                   'irradiation_position')

EXTRACTION_ATTRS = ('weight', 'extract_device', 'tray',
                    'extract_value',
                    'extract_units',
                    'load_name',
                    'load_holder',
                    'extract_duration',
                    'cleanup_duration',
                    'pre_cleanup_duration',
                    'post_cleanup_duration',
                    'light_value',
                    'pattern', 'beam_diameter', 'ramp_duration', 'ramp_rate')

META_ATTRS = ('analysis_type', 'uuid', 'identifier', 'aliquot', 'increment',
              'comment', 'mass_spectrometer',
              'username', 'queue_conditionals_name',
              'repository_identifier',
              'acquisition_software',
              'data_reduction_software', 'instrument_name', 'laboratory', 'experiment_queue_name', 'experiment_type',

              ) + SAMPLE_METADATA

# ============= EOF =============================================
