"""
MIT License

Copyright (c) 2020 Collin Brooks

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from abc import ABC, abstractmethod
META = '_meta'

class Decorator(ABC):
    """Abstract base class for all decorators
    """
    __slots__ = ['_cls']

    def __init__(self):
        self._cls = None

    def __call__(self, cls):
        self._cls = cls

        #Make sure our classes have the meta dict
        if not hasattr(self._cls, META):
            setattr(self._cls, META, {})

        #Perform our decorator's work
        self.do()

        #Return the original class
        return self._cls

    @abstractmethod
    def do(self):
        """Method called after our metadata has been setup. Performs the work
        of the extending decorator.
        """

    @property
    def cls(self):
        """Get the decorator's cls reference

        Returns:
            [object]: The class this decorator is attached to.
        """
        return self._cls

    @property
    def meta(self):
        """Get the entire metadata for this descriptor's cls.

        Returns:
            dict: The metadata.
        """
        if not hasattr(self._cls, META):
            setattr(self._cls, META, {})

        return getattr(self._cls, META)

    def get_meta(self, key):
        """Get the value of our metadata at the given key.

        Args:
            key (str): The key whose value in the metadata should be
                       returned.
        Returns:
            mixed: The metadata at the given key
        """
        return getattr(self._cls, META).get(key)

    def set_meta(self, key, value):
        """Setter for our metadata.

        Args:
            key (str): The key to store the value in.
            value (mixed): The value for the metadata
        """
        meta = self.meta

        meta[key] = value

    def add_method_to_cls(self, fn_name, getter, doc):
        """Add the given method to this decorator's cls.

        Args:
            fn_name (str): The name of the method.
            getter (callable): The method itself.
            doc (str): The documentation for the method.
        """
        getter.__doc__ = doc
        setattr(self.cls, fn_name, getter)

    @staticmethod
    def provide(data, key, default):
        """Provide the given data with a default value at key if none exists.

        Args:
            data (dict): The data to provision.
            key (str): The key which should be provided a value.
            default (mixed): The default value to set if the key does not
                             exist.

        Returns:
            [mixed]: The value at key in the given data.
        """
        if data.get(key) is None:
            data[key] = default

        return data[key]

    @property
    def xsd(self):
        """Get the xsd of this decorator's class.

        Returns:
            [str]: The xsd name of this decorator's class.
        """
        return self.cls.__module__.split('.')[2]
