__author__ = 'Gianluca Barbon'

# this library allows to make this class an abstract class
# from abc import ABCMeta, abstractmethod

# notice that in java this is an interface, but python as no interfaces!


# python 2.7 version
# class AsipWriter(object):
#     __metaclass__=ABCMeta
#
#     @abstractmethod
#     def write(self, val):
#         pass

# python 3 version
# class AsipWriter (metaclass=ABCMeta):
#
#     @abstractmethod
#     def write(self, val):
#         pass

# this version actually is not an abstract class, but we need to implement it in this way in order to be compatible
# with both python versions, without the use of external libraries (for compatibility)
class AsipWriter:

    #method that will be overridden in child classes
    def write(self, val):
        raise NotImplementedError( "Should have implemented this" )