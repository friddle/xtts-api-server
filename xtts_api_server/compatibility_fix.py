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
        import coqpit
        original_deserialize = coqpit.coqpit._deserialize
        
        def safe_deserialize(value, field_type):
            try:
                return original_deserialize(value, field_type)
            except TypeError as e:
                if "issubclass() arg 1 must be a class" in str(e):
                    # Handle the case where field_type is not a class
                    if not inspect.isclass(field_type):
                        return value
                # Re-raise the error if it's a different issue
                raise
        
        coqpit.coqpit._deserialize = safe_deserialize
        logging.info("Applied coqpit compatibility patch")
    except ImportError:
        # coqpit not available yet
        pass
    except Exception as e:
        logging.warning(f"Could not patch coqpit: {e}")

def apply_all_patches():
    """Apply all compatibility patches."""
    patch_issubclass()
    patch_coqpit()

# Apply patches when module is imported
apply_all_patches()
print("Applied compatibility fixes for TTS and related libraries")
