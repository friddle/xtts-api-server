"""
Fix for TTS config loading issue with coqpit library.
This module patches the load_config function to handle issubclass() error.
"""

import logging
import sys
import importlib

def patch_coqpit():
    """
    Patch coqpit to handle the issubclass() error when loading TTS config.
    """
    try:
        import coqpit
        from coqpit import coqpit
        
        # Store the original _deserialize function
        original_deserialize = coqpit._deserialize
        
        def patched_deserialize(value, field_type):
            """
            Patched version of _deserialize that handles the issubclass() error.
            """
            try:
                # Try the original function first
                return original_deserialize(value, field_type)
            except TypeError as e:
                if "issubclass() arg 1 must be a class" in str(e):
                    # Handle the case where field_type is not a class
                    logging.warning(f"Coqpit issubclass error handled: {e}")
                    # Return the value as-is if we can't deserialize it
                    return value
                else:
                    # Re-raise if it's a different TypeError
                    raise
        
        # Apply the patch
        coqpit._deserialize = patched_deserialize
        logging.info("Applied coqpit compatibility patch for TTS config loading")
        return True
    except ImportError:
        logging.warning("coqpit not available, cannot apply patch")
        return False
    except Exception as e:
        logging.error(f"Failed to apply coqpit patch: {e}")
        return False

def patch_tts_config():
    """
    Patch TTS config loading to handle compatibility issues.
    """
    try:
        from TTS.config import load_config
        
        # Store the original load_config function
        original_load_config = load_config
        
        def patched_load_config(config_path):
            """
            Patched version of load_config that handles compatibility issues.
            """
            try:
                # Try the original function first
                return original_load_config(config_path)
            except TypeError as e:
                if "issubclass() arg 1 must be a class" in str(e):
                    logging.warning(f"TTS config loading error handled: {e}")
                    # Apply the coqpit patch and try again
                    if patch_coqpit():
                        return original_load_config(config_path)
                    else:
                        raise
                else:
                    # Re-raise if it's a different TypeError
                    raise
        
        # Apply the patch
        import TTS.config
        TTS.config.load_config = patched_load_config
        logging.info("Applied TTS config loading compatibility patch")
        return True
    except ImportError:
        logging.warning("TTS.config not available, cannot apply patch")
        return False
    except Exception as e:
        logging.error(f"Failed to apply TTS config patch: {e}")
        return False

# Apply the patches
patch_coqpit()
patch_tts_config()

print("Applied TTS config compatibility patches")
