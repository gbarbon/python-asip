__author__ = 'Gianluca Barbon'

# notice that in java this is an interface, but python as no interfaces!

# class AsipWriter:
#
#     def __init__(self):
#         pass


class AsipWriter( object ):

    def write(self, val):
        raise NotImplementedError( "Should have implemented this" )