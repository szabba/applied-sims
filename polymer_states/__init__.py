#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy


class Link(int):
    """A polymer chain link on a 2D lattice."""

    VALID_LINK_VALUES = {1 << i for i in range(5)}

    def __init__(self, value):
        if value not in Link.VALID_LINK_VALUES:
            raise ValueError("invalid link value {}".format(value))

Link.UP, Link.DOWN, Link.LEFT, Link.RIGHT, Link.SLACK = \
    map(Link, Link.VALID_LINK_VALUES)



class Polymer:
    """A chain of N links."""

    def __init__(self, links):

        arr_links = numpy.array(list(map(Link, links)))

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

        return cls([Link.SLACK] * link_count)

    def reachable_from(self):
        reachable = {self}
        for i, pair in enumerate(self.link_pairs()):
            if Polymer.both_slacks(pair):
                reachable.update(self.__create_hernias_at(i))
            elif Polymer.is_hernia(pair):
                reachable.add(self.__annihilate_hernia_at(i))
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
        for first, second in [(Link.UP, Link.DOWN), (Link.DOWN, Link.UP),
                              (Link.LEFT, Link.RIGHT), (Link.RIGHT, Link.LEFT)]:
            new_links = self.__links.copy()
            new_links[i] = first
            new_links[i + 1] = second
            out.add(Polymer(new_links))
        return out

    def __annihilate_hernia_at(self, i):
        new_links = self.__links.copy()
        new_links[i:i+2] = Link.SLACK
        return Polymer(new_links)

    def link_pairs(self):
        return zip(self.__links, self.__links[1:])

    @staticmethod
    def is_hernia(pair):
        """Polymer.is_hernia(pair) -> a bool

        Returns True if the given pair of links forms a hernia.
        """
        return set(pair) in [{Link.UP, Link.DOWN}, {Link.LEFT, Link.RIGHT}]

    @staticmethod
    def both_slacks(pair):
        return pair == (Link.SLACK, Link.SLACK)


HERNIAS = {
    Polymer([Link.UP, Link.DOWN]), Polymer([Link.DOWN, Link.UP]),
    Polymer([Link.LEFT, Link.RIGHT]), Polymer([Link.RIGHT, Link.LEFT]),
}