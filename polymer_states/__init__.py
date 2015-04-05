#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy


# Link states
UP, DOWN, LEFT, RIGHT, SLACK = [1 << i for i in range(5)]


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
        if self.__links.shape != other._Polymer__links.shape:
            return False
        return numpy.equal(self.__links, other._Polymer__links).all()

    def __ne__(self, other):
        return not self == other

    @classmethod
    def all_curled_up(cls, link_count):
        """Polymer.all_curled_up(len) -> a Polymer

        Creates a Polymer that has link_count links (ie, link_count + 1 reptons)
        and all reptons placed in a single cell.
        """

        return cls([SLACK] * link_count)


HERNIAS = {
    Polymer([UP, DOWN]), Polymer([DOWN, UP]),
    Polymer([LEFT, RIGHT]), Polymer([RIGHT, LEFT]),
}