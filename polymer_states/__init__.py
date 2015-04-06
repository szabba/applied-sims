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

    def reachable_from(self):
        reachable = {self}
        for i, pair in enumerate(self.link_pairs()):
            if Polymer.both_slacks(pair):
                reachable.update(self.__create_hernias_at(i))
        return reachable

    def contains_hernia(self):
        """P.contains_hernia() -> a bool

        Returns True if the Polymer contains a hernia.
        """
        return any(Polymer.is_hernia(pair) for pair in self.link_pairs())

    def contains_slack_pair(self):
        """P.contains_slack_pair() -> a bool

        Returns True if the Polymer contains a pair of consecutive slacks that
        could be turned into a hernia.
        """
        return any(Polymer.both_slacks(pair) for pair in self.link_pairs())

    def __create_hernias_at(self, i):
        out = set()
        for first, second in [(UP, DOWN), (DOWN, UP),
                              (LEFT, RIGHT), (RIGHT, LEFT)]:
            new_links = self.__links.copy()
            new_links[i] = first
            new_links[i + 1] = second
            out.add(Polymer(new_links))
        return out

    def link_pairs(self):
        return zip(self.__links, self.__links[1:])

    @staticmethod
    def is_hernia(pair):
        """Polymer.is_hernia(pair) -> a bool

        Returns True if the given pair of links forms a hernia.
        """
        return set(pair) in [{UP, DOWN}, {LEFT, RIGHT}]
    @staticmethod
    def both_slacks(pair):
        return pair == (SLACK, SLACK)


HERNIAS = {
    Polymer([UP, DOWN]), Polymer([DOWN, UP]),
    Polymer([LEFT, RIGHT]), Polymer([RIGHT, LEFT]),
}