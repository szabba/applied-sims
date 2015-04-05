#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy


# Link states
UP, DOWN = (0, 1), (0, -1)
LEFT, RIGHT = (-1, 0), (1, 0)
SLACK = (0, 0)


class Polymer:
    """A chain of N links."""

    def __init__(self, links):

        arr_links = numpy.array(list(links))

        if len(arr_links) < 1:
            raise ValueError(("polymer chain must contain at least one "
                              + "link, {} given").format(len(arr_links)))

        self.__links = arr_links

    def __hash__(self):
        return 0

    def __eq__(self, other):
        return (self.__links == other._Polymer__links).all()

    def __ne__(self, other):
        return not self == other

    @classmethod
    def all_curled_up(cls, link_count):
        """Polymer.all_curled_up(len) -> a Polymer

        Creates a Polymer that has link_count links (ie, link_count + 1 reptons)
        and all reptons placed in a single cell.
        """

        return cls([SLACK] * link_count)