__author__ = 'Gianluca Barbon'

# this library allows to make this class an abstract class
from abc import ABCMeta, abstractmethod

# notice that in java this is an interface, but python as no interfaces!

# old implementation
# class AsipWriter( object ):
#
#     def write(self, val):
#         raise NotImplementedError( "Should have implemented this" )


# python 2.7 version
class AsipWriter(object):
    __metaclass__=ABCMeta

    @abstractmethod
    def write(self, val):
        pass

# python 3 version
# class AsipWriter (metaclass=ABCMeta):
#
#     @abstractmethod
#     def write(self, val):
#         pass