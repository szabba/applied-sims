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

        links = tuple(links)

        if len(links) < 1:
            raise ValueError(("polymer chain must contain at least one "
                              + "link, {} given").format(len(links)))

        self.__links = tuple(map(Link, links))

    def __hash__(self):
        return hash(self.__links)

    def __eq__(self, other):
        return self.__links == other._Polymer__links

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
            first, second = pair
            if Polymer.both_slacks(pair):
                reachable.update(self.__create_hernias_at(i))
            elif i == 0 and first == Link.SLACK:
                reachable.update(self.__make_slack_end_taut(i))
            elif Link.SLACK in pair:
                reachable.add(self.__reptate_at(i))
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
            new_links = (
                first if j == i
                else second if j == i + 1
                else link
                for j, link in enumerate(self.__links)
            )
            out.add(Polymer(new_links))
        return out

    def __annihilate_hernia_at(self, i):
        new_links = (
            Link.SLACK if j in (i, i + 1) else link
            for j, link in enumerate(self.__links)
        )
        return Polymer(new_links)

    def __reptate_at(self, i):
        new_links = (
            self.__links[j + 1] if j == i
            else self.__links[j - 1] if j == i + 1
            else link
            for j, link in enumerate(self.__links)
        )
        return Polymer(new_links)

    def __make_slack_end_taut(self, i):
        out = set()
        for taut_link in [Link.UP, Link.DOWN, Link.LEFT, Link.RIGHT]:
            new_links = (taut_link, ) + self.__links[1:]
            out.add(Polymer(new_links))
        return out

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