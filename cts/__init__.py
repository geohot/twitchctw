"""
The ``cts`` package provides a Python implementation of the CTS algorithm.

``cts.model.CTS``
=================

.. autoclass:: cts.model.CTS
    :members:
    :undoc-members:
    :special-members: __init__

``cts.model.ContextualSequenceModel``
=====================================

.. autoclass:: cts.model.ContextualSequenceModel
    :members:
    :undoc-members:
    :special-members: __init__

``cts.fastmath``
================

.. autofunction:: cts.fastmath.log_add
"""

from . import fastmath
from . import model

__version__ = '0.1'
