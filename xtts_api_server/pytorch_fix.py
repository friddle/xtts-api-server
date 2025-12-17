"""
Fix for PyTorch 2.6+ compatibility with TTS library.
This module patches torch.load to handle weights_only parameter correctly.
"""

import torch
import pickle
import logging
import sys

# Store the original torch.load function only if not already patched
if not hasattr(torch.load, '_pytorch26_patched'):
    _original_torch_load = torch.load

    def patched_torch_load(f, map_location=None, pickle_module=pickle, **kwargs):
        """
        Patched version of torch.load that handles weights_only parameter for TTS compatibility.
        """
        # If weights_only is not specified, set it to False for TTS compatibility
        if 'weights_only' not in kwargs:
            kwargs['weights_only'] = False
        
        # Call the original torch.load with the modified parameters
        return _original_torch_load(f, map_location=map_location, pickle_module=pickle_module, **kwargs)

    # Mark as patched and apply the monkey patch
    patched_torch_load._pytorch26_patched = True
    torch.load = patched_torch_load

# Also add safe globals for XttsConfig if available
def add_safe_globals():
    try:
        from TTS.tts.configs.xtts_config import XttsConfig
        if hasattr(torch.serialization, 'add_safe_globals'):
            torch.serialization.add_safe_globals([XttsConfig])
            logging.info("Added XttsConfig to safe globals for PyTorch 2.6+")
    except ImportError:
        # TTS not available yet, will be added later
        pass
    except Exception as e:
        logging.warning(f"Could not add XttsConfig to safe globals: {e}")

# Apply the safe globals patch
add_safe_globals()

# Patch TTS.utils.io.load_fsspec when it's imported
def patch_tts_io():
    try:
        import TTS.utils.io
        original_load_fsspec = TTS.utils.io.load_fsspec
        
        def patched_load_fsspec(model_path, map_location=None, **kwargs):
            # Ensure weights_only is set to False for compatibility
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return original_load_fsspec(model_path, map_location=map_location, **kwargs)
        
        TTS.utils.io.load_fsspec = patched_load_fsspec
        logging.info("Patched TTS.utils.io.load_fsspec for PyTorch 2.6+ compatibility")
    except (ImportError, AttributeError):
        # TTS not available yet or load_fsspec doesn't exist
        pass
    except Exception as e:
        logging.warning(f"Could not patch TTS.utils.io.load_fsspec: {e}")

# Try to patch TTS.io now, and also set up a hook to patch it when imported
patch_tts_io()

# Set up an import hook to patch TTS.utils.io when it's imported
class TTSPatchImporter:
    def find_spec(self, fullname, path, target=None):
        if fullname == 'TTS.utils.io':
            # Use the default importer
            spec = None
            for finder in sys.meta_path:
                if hasattr(finder, 'find_spec'):
                    spec = finder.find_spec(fullname, path, target)
                    if spec is not None:
                        break
            
            # Create a loader that will patch the module after import
            if spec is not None:
                original_loader = spec.loader
                
                def patched_loader(module):
                    original_loader.exec_module(module)
                    # Patch the load_fsspec function
                    if hasattr(module, 'load_fsspec'):
                        original_load_fsspec = module.load_fsspec
                        
                        def patched_load_fsspec(model_path, map_location=None, **kwargs):
                            # Ensure weights_only is set to False for compatibility
                            if 'weights_only' not in kwargs:
                                kwargs['weights_only'] = False
                            return original_load_fsspec(model_path, map_location=map_location, **kwargs)
                        
                        module.load_fsspec = patched_load_fsspec
                        logging.info("Patched TTS.utils.io.load_fsspec for PyTorch 2.6+ compatibility")
                    return module
                
                spec.loader = patched_loader
            return spec
        return None

# Install the import hook
sys.meta_path.insert(0, TTSPatchImporter())

print("Applied PyTorch 2.6+ compatibility patch for TTS")
