# PyInstaller hook for gradio
# This ensures that all critical gradio modules are included in the build

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Collect all data, binaries, and hidden imports for gradio
datas, binaries, hiddenimports = collect_all('gradio')

# Add specific modules that might be missed
additional_modules = [
    'gradio.blocks_events',
    'gradio.components',
    'gradio.themes',
    'gradio.themes.utils',
    'gradio._simple_templates',
    'gradio._simple_templates.simpledropdown',
    'gradio._simple_templates.simpleimage', 
    'gradio._simple_templates.simpletextbox',
    'gradio.helpers',
    'gradio.queue',
    'gradio.events',
    'gradio.flagging',
    'gradio.interpretation',
    'gradio.external',
    'gradio.networking',
    'gradio.reload',
    'gradio.oauth',
    'gradio.server',
    'gradio.cli',
    'gradio.routes',
    'gradio.utils', 
    'gradio.queueing',
    'gradio.route_utils',
    'gradio.processing_utils',
    'gradio.data_classes',
]

hiddenimports.extend(additional_modules)

# Also collect submodules
gradio_submodules = collect_submodules('gradio')
hiddenimports.extend(gradio_submodules)

# Remove duplicates
hiddenimports = list(set(hiddenimports))