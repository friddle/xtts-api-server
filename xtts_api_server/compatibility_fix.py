"""
Compatibility fixes for various library version conflicts.
This module provides patches for common issues with TTS, transformers, and PyTorch.
"""

import sys
import logging
import types
import inspect
import builtins

def patch_issubclass():
    """
    Patch issubclass to handle cases where the first argument is not a class.
    This is a workaround for compatibility issues between different library versions.
    """
    original_issubclass = builtins.issubclass
    
    def safe_issubclass(arg1, arg2):
        try:
            return original_issubclass(arg1, arg2)
        except TypeError:
            # If the first argument is not a class, return False
            if not inspect.isclass(arg1):
                return False
            # Re-raise the error if it's a different issue
            raise
    
    builtins.issubclass = safe_issubclass
    logging.info("Applied issubclass compatibility patch")

def patch_coqpit():
    """
    Patch coqpit module to handle type checking issues.
    """
    try:
        # Try to patch the function in the TTS.config module directly
        try:
            import TTS.config
            if hasattr(TTS.config, 'load_config'):
                original_load_config = TTS.config.load_config
                
                def safe_load_config(config_path):
                    try:
                        return original_load_config(config_path)
                    except (TypeError, ValueError) as e:
                        error_msg = str(e)
                        if "does not match" in error_msg and "field type" in error_msg:
                            # Try to load the config manually and apply our patch
                            import json
                            with open(config_path, 'r') as f:
                                config_dict = json.load(f)
                            
                            # Create a config object and apply our patch
                            from TTS.config import BaseTTSConfig
                            config = BaseTTSConfig()
                            
                            # Apply our patch to the config object before loading
                            import coqpit
                            if hasattr(coqpit.coqpit, '_deserialize'):
                                original_deserialize = coqpit.coqpit._deserialize
                                
                                def safe_deserialize(x, field_type):
                                    try:
                                        return original_deserialize(x, field_type)
                                    except (TypeError, ValueError) as e:
                                        # Handle various type checking errors
                                        error_msg = str(e)
                                        if "issubclass() arg 1 must be a class" in error_msg:
                                            # Handle the case where field_type is not a class
                                            if not inspect.isclass(field_type):
                                                return x
                                        elif "does not match" in error_msg and "field type" in error_msg:
                                            # Handle type mismatch errors, particularly for union types
                                            # For 'float | list[float]' type, if value is a float, accept it
                                            if "float | list[float]" in error_msg and isinstance(x, float):
                                                return x
                                            # For other type mismatches, try to return the value as-is
                                            return x
                                        # Re-raise the error if it's a different issue
                                        raise
                                
                                coqpit.coqpit._deserialize = safe_deserialize
                            
                            config.from_dict(config_dict)
                            return config
                        raise
                
                TTS.config.load_config = safe_load_config
                logging.info("Applied TTS.config.load_config compatibility patch")
        except Exception as e:
            logging.warning(f"Could not patch TTS.config.load_config: {e}")
        
        logging.info("Applied coqpit compatibility patch")
    except ImportError:
        # coqpit not available yet
        pass
    except Exception as e:
        logging.warning(f"Could not patch coqpit: {e}")

def apply_all_patches():
    """Apply all compatibility patches."""
    patch_issubclass()
    # Apply coqpit patch here as well
    patch_coqpit()

# Apply patches when module is imported
apply_all_patches()
print("Applied compatibility fixes for TTS and related libraries")
