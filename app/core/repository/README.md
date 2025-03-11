Repository is a collection of records:

- implements async iterator protocol
- implements `count()` method
- implements slicing

A new Repository instance represents all records of a particular entity.

Slicing returns a copy of a Repository instance that represents a subset of records - to be used for reading data in batches and/or pagination.

Calling `filter_*` methods returns a deep copy of Repository instance, which represents a correspondingly filtered subset of records.

