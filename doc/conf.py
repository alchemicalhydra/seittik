# Sphinx master config file
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from datetime import date
from functools import wraps

from docutils.parsers.rst import directives

from seittik import __version__


########################################################################
# Project
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Seittik'
author = 'Tom Tobin'
copyright = f"{date.today().year}, {author}"
release = __version__
version = release


########################################################################
# General
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'autodoc2',
    'IPython.sphinxext.ipython_console_highlighting',
    'IPython.sphinxext.ipython_directive',
    'myst_parser',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.intersphinx',
    'sphinxcontrib_dooble',
    'sphinxcontrib.mermaid',
]

templates_path = ['_templates']
exclude_patterns = [
    '_build',
    '.doctrees',
    'node_modules',
]

pygments_style = 'igor'


########################################################################
# HTML
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'github_url': 'https://github.com/alchemicalhydra/seittik',
    'navbar_end': ['navbar-icon-links'],
    'show_nav_level': 4,
    'show_toc_level': 4,
}
html_static_path = ['_static']
html_css_files = [
    'css/local.css',
]
# I'd like to include the Mermaid JS in here bundled locally
html_js_files = [
    'js/index.js',
]
html_context = {
    'default_mode': 'light',
}


########################################################################
# Extlinks

extlinks = {
    'clj-core': ('https://clojure.github.io/clojure/clojure.core-api.html#clojure.core/%s', "Clojure core: %s"),
    'clj-medley': ('http://weavejester.github.io/medley/medley.core.html#var-%s', "Clojure Medley: %s"),
    'hs-data-list': ('https://hackage.haskell.org/package/base/docs/Data-List.html#v:%s', "Haskell Data.List: %s"),
    'js-fxts': ('https://fxts.dev/docs/%s', "JavaScript: FxTS: %s"),
    'js-lfi': ('https://github.com/TomerAberbach/lfi/blob/main/docs/modules.md#%s', "JavaScript: lfi: %s"),
    'js-ramda': ('https://ramdajs.com/docs/#%s', "JavaScript: Ramda: %s"),
    'py-array': ('https://docs.python.org/3/library/array.html#array.%s', "Python array: %s"),
    'py-builtins': ('https://docs.python.org/3/library/functions.html#%s', "Python builtins: %s"),
    # Hack because extlinks isn't very flexible
    'py-builtins-func': ('https://docs.python.org/3/library/functions.html#func-%s', "Python builtins: %s"),
    'py-collections': ('https://docs.python.org/3/library/collections.html#collections.%s', "Python collections: %s"),
    'py-functools': ('https://docs.python.org/3/library/functools.html#functools.%s', "Python functools: %s"),
    'py-itertools': ('https://docs.python.org/3/library/itertools.html#itertools.%s', "Python itertools: %s"),
    'py-math': ('https://docs.python.org/3/library/math.html#math.%s', "Python math: %s"),
    'py-more-itertools': ('https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.%s', "Python more-itertools: %s"),
    'py-pathlib': ('https://docs.python.org/3/library/pathlib.html#pathlib.%s', "Python pathlib: %s"),
    'py-random': ('https://docs.python.org/3/library/random.html#random.%s', "Python random: %s"),
    'py-statistics': ('https://docs.python.org/3/library/statistics.html#statistics.%s', "Python statistics: %s"),
    'py-struct': ('https://docs.python.org/3/library/struct.html#struct.%s', "Python struct: %s"),
    'rb-enumerable': ('https://ruby-doc.org/3.2.1/Enumerable.html#method-i-%s', "Ruby Enumerable: %s"),
    # Hack because extlinks isn't very flexible
    'rb-enumerable-qm': ('https://ruby-doc.org/3.2.1/Enumerable.html#method-i-%s-3F', "Ruby Enumerable: %s?"),
}


########################################################################
# Intersphinx

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}


########################################################################
# MyST
# https://myst-parser.readthedocs.io/en/latest/configuration.html

myst_enable_extensions = [
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#block-attributes
    'attrs_block',
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#inline-attributes
    'attrs_inline',
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#code-fences-using-colons
    'colon_fence',
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#field-lists
    'fieldlist',
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#typography
    'replacements',
    'smartquotes',
    # https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#substitutions-with-jinja2
    'substitution',
]

# https://myst-parser.readthedocs.io/en/latest/syntax/optional.html#substitutions-with-jinja2
myst_substitutions = {
    'pipe_source': '[**Source:**]{.pipe-source}',
    'pipe_step': '[**Step:**]{.pipe-step}',
    'pipe_sink': '[**Sink:**]{.pipe-sink}',
    'pipe_sourcestep': '[**Source:**]{.pipe-source}/[**Step:**]{.pipe-step}',
}

# https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#customising-external-url-resolution
myst_url_schemes = {
    'http': None,
    'https': None,
    'ftp': None,
    'mailto': None,
    'wp': 'https://en.wikipedia.org/wiki/{{path}}#{{fragment}}',
}


########################################################################
# Autodoc2
# https://sphinx-autodoc2.readthedocs.io/en/latest/config.html

autodoc2_packages = [
    {
        'path': '../src/seittik',
        'auto_mode': True,
        'exclude_dirs': [
            '__pycache__',
            'utils',
        ],
    },
]
autodoc2_render_plugin = 'myst'
autodoc2_module_all_regexes = [
    r'^seittik\..*',
]
autodoc2_index_template = None


########################################################################
# IPython
# https://ipython.readthedocs.io/en/stable/sphinxext.html

ipython_execlines = [
    'from seittik.pipes import Pipe, Pipe as P',
    'from seittik.shears import ShearVar, X, Y, Z',
]
ipython_reset_history = True


########################################################################
# Mermaid
# https://github.com/mgaitan/sphinxcontrib-mermaid

# We bundle Mermaid locally via Webpack
mermaid_version = ''
mermaid_init_js = ''


########################################################################
# Unspeakable Horrors

# Monkey-patch IPythonDirective to allow us to reset counts
def _monkey_patch_ipython_directive():
    from IPython.sphinxext.ipython_directive import IPythonDirective
    ipython_directive_setup = IPythonDirective.setup
    IPythonDirective.option_spec = {
        'reset_history': directives.flag,
        **IPythonDirective.option_spec,
    }
    @wraps(IPythonDirective.setup)
    def setup(self):
        ret = ipython_directive_setup(self)
        config = self.state.document.settings.env.config
        if config.ipython_reset_history or 'reset_history' in self.options:
            self.shell.IP.history_manager.reset()
            self.shell.IP.execution_count = 1
        return ret
    IPythonDirective.setup = setup
_monkey_patch_ipython_directive()


# Monkey-patch dooble to fix missing layout
def _monkey_patch_dooble():
    import matplotlib.pyplot as plt
    from dooble import render as dooble_render_module
    from sphinxcontrib_dooble import dooble as sphinxcontrib_dooble_module
    # Originals:
    dooble_render_to_file = sphinxcontrib_dooble_module.render_to_file
    plt_savefig = dooble_render_module.plt.savefig
    plt_subplots = dooble_render_module.plt.subplots
    @wraps(plt_subplots)
    def subplots(*args, **kwargs):
        kwargs['layout'] = 'constrained'
        fig, ax = plt_subplots(*args, **kwargs)
        @wraps(plt_savefig)
        def savefig(*args, **kwargs):
            ax_bottom, ax_top = ax.get_ylim()
            ax.set_ylim(bottom=ax_bottom - 0.2, top=ax_top + 0.2)
            ret = plt_savefig(*args, **kwargs)
            # Restore savefig
            dooble_render_module.plt.savefig = plt_savefig
            return ret
        # Hijack savefig
        dooble_render_module.plt.savefig = savefig
        # Restore subplots
        dooble_render_module.plt.subplots = plt_subplots
        return (fig, ax)
    @wraps(dooble_render_to_file)
    def render_to_file(marble, filename, theme):
        # Hijack subplots
        dooble_render_module.plt.subplots = subplots
        dooble_render_to_file(marble, filename, theme)
    # Hijack render_to_file
    sphinxcontrib_dooble_module.render_to_file = render_to_file
_monkey_patch_dooble()


########################################################################
# Setup

def setup(app):
    app.add_config_value('ipython_reset_history', False, 'env')
