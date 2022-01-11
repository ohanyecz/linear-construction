.. _api.accessstructure:

===============
AccessStructure
===============
.. currentmodule:: linearconstruction.access_structure


Constructor
~~~~~~~~~~~

An access structure can be created by passing the number of participants to ``n`` and
the minimal qualified groups to ``gamma_min``. The optional parameter ``create_dual``
creates the dual access structure of the passed minimal qualified groups.

An access structure can be created by using the method ``from_args()`` or ``from_iterable()``.
See the examples at the methods.

.. autosummary::
   :toctree: api/

   AccessStructure
   AccessStructure.from_args
   AccessStructure.from_iterable


Methods
~~~~~~~

.. autosummary::
   :toctree: api/

   AccessStructure.dual
