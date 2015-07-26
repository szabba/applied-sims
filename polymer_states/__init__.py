#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.


import functools
import operator


class Link(int):
    """A polymer chain link on a 2D lattice."""

    VALID_LINK_VALUES = {1 << i for i in range(5)}

    def __init__(self, value):
        if value not in Link.VALID_LINK_VALUES:
            raise ValueError("invalid link value {}".format(value))

    def __repr__(self):
        return {
            Link.UP: 'Link.UP',
            Link.DOWN: 'Link.DOWN',
            Link.LEFT: 'Link.LEFT',
            Link.RIGHT: 'Link.RIGHT',
            Link.SLACK: 'Link.SLACK',
        }[self]

    def is_slack(self):
        return self == Link.SLACK

    def is_taut(self):
        return not self.is_slack()

    def perpendicular_to(self, other):
        return (self, other) in Link.PERPENDICULAR_PAIRS

    def opposite(self):
        return {
            Link.UP: Link.DOWN,
            Link.DOWN: Link.UP,
            Link.LEFT: Link.RIGHT,
            Link.RIGHT: Link.LEFT,
            Link.SLACK: Link.SLACK,
        }[self]


Link.LINKS = {Link(i) for i in Link.VALID_LINK_VALUES}
Link.UP, Link.DOWN, Link.LEFT, Link.RIGHT, Link.SLACK = Link.LINKS

Link.TAUT_LINKS = {link for link in Link.LINKS if link.is_taut()}
Link.PERPENDICULAR_PAIRS = {
    (Link.UP, Link.LEFT),
    (Link.UP, Link.RIGHT),
    (Link.DOWN, Link.LEFT),
    (Link.DOWN, Link.RIGHT),
    (Link.LEFT, Link.UP),
    (Link.LEFT, Link.DOWN),
    (Link.RIGHT, Link.UP),
    (Link.RIGHT, Link.DOWN),
}


class Polymer:
    """A chain of N links."""

    def __init__(self, links):
        self.__links = tuple(map(Link, links))

    def __repr__(self):
        return 'Polymer([{}])'.format(', '.join(map(repr, self.links())))

    def __hash__(self):
        return hash(self.links())

    def __eq__(self, other):
        if not isinstance(other, Polymer): return False
        return self.links() == other.links()

    def __ne__(self, other):
        return not self == other

    @classmethod
    def all_with_n_links(cls, n):
        """Polymer.all_with_n_lins(n) -> set of Polymers

        Creates a set of all valid Polymers with n links.
        """
        curled_up = Polymer.all_curled_up(n)

        old, new = set(), {curled_up}
        grow_by = curled_up.reachable_from()

        while new != old:
            old, new = new, new | grow_by
            grow_by = functools.reduce(
                operator.or_,
                (polymer.reachable_from() for polymer in grow_by))

        return new

    @classmethod
    def all_curled_up(cls, link_count):
        """Polymer.all_curled_up(link_count) -> a Polymer

        Creates a Polymer that has link_count links (ie, link_count + 1 reptons)
        and all reptons placed in a single cell.
        """

        return cls([Link.SLACK] * link_count)

    def reachable_from(self) -> set:
        """P.reachable_from() -> set

        Returns the set of polymers that this one can transform into in a single
        step.
        """
        return set(self.transition_rates({}).keys())

    # TODO: Use move rates dictionary.
    # TODO: Separate out the moving of reptons on either end of the chain from moving those in the middle.
    def transition_rates(self, move_rates: dict, sum_with = operator.add) -> dict:
        """P.transition_rates(move_rates[, sum_with]) -> dict with polymer keys

        Calculates the transition rates to all states reachable from the current
        one in one step, given that `move_rates` is a dictionary mapping kinds
        of moves to rates.

        The rates for different moves are combined using `sum_with` which
        defaults to `operator.add`.
        """

        reachable = set()
        reachable.update(self.__wiggle_end_links())

        for i, pair in enumerate(self.link_pairs()):

            if Polymer.both_slacks(pair):
                reachable.update(self.__create_hernias_at(i, pair))

            if Polymer.can_reptate(pair):
                reachable.update(self.__reptate_at(i, pair))

            if Polymer.is_hernia(pair):
                reachable.add(self.__annihilate_hernia_at(i))
                reachable.update(self.__change_hernia_bend_direction(i, pair))

            if Polymer.is_bent_pair(pair):
                reachable.add(self.__flip_at(i, pair))

        return dict.fromkeys(reachable, 0)

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

    def substitute_pair(self, p, replacement_pair):
        """P.substitute_pair(p, replacement_pair) -> Polymer

        Produces a polymer in which the `p`-th pair is substituted with the one
        specified.

        The pair index `p` corresponds to the position of a pair in
        `P.link_pairs()`.
        """
        first, second = replacement_pair
        vlinks = (None, ) + self.links() + (None, )
        new_vlinks = [
            first if i == p else
            second if i - 1 == p else
            link
            for i, link in enumerate(vlinks)
        ]
        return Polymer(new_vlinks[1:-1])

    def __create_hernias_at(self, i, current):
        return {
            self.substitute_pair(i, pair)
            for pair in {
                (Link.UP, Link.DOWN),
                (Link.DOWN, Link.UP),
                (Link.LEFT, Link.RIGHT),
                (Link.RIGHT, Link.LEFT)
            } if pair != current
        }

    def __annihilate_hernia_at(self, i):
        return self.substitute_pair(i, (Link.SLACK, Link.SLACK))

    def __reptate_at(self, i, pair):
        first, second = pair
        return {
            self.substitute_pair(i, (second, first))
        } if first != second else set()

    def __wiggle_end_links(self):
        current_first = self.links()[0]
        current_last = self.links()[-1]
        wiggle_front = {
            self.substitute_pair(0, (None, link))
            for link in Link.LINKS
            if link != current_first
        }
        wiggle_back = {
            self.substitute_pair(len(self.links()), (link, None))
            for link in Link.LINKS
            if link != current_last
        }
        return wiggle_front | wiggle_back

    def __flip_at(self, i, current):
        first, second = current
        return self.substitute_pair(i, (second, first))

    def __change_hernia_bend_direction(self, i, current):
        return {
            self.substitute_pair(i, hernia)
            for hernia in HERNIA_PAIRS
            if hernia != current
        }

    def link_pairs(self):
        """P.link_pairs() -> iterable of 2-element Link tuples

        Returns all pairs of consecutive links. As a special case, the first
        pair contains a None instead of the first link, and the last pair
        contains a None instead of the last link.

        The indices accepted by P.substitute_pair correspond to the position in
        this iterator.
        """
        return zip((None, ) + self.links(), self.links() + (None, ))

    def __inner_pairs(self):
        return tuple(self.link_pairs())[1:-1]

    def __outer_pairs(self):
        return ((None, self.links[0]),
                (self.links[-1], None))

    def links(self):
        """P.links() -> tuple of Links, starting from the chain's head """
        return self.__links

    @staticmethod
    def is_edge_pair(pair):
        return None in pair

    @staticmethod
    def is_bent_pair(pair):
        return pair in Link.PERPENDICULAR_PAIRS

    @staticmethod
    def can_reptate(pair):
        return not Polymer.is_edge_pair(pair) and Link.SLACK in pair

    @staticmethod
    def is_hernia(pair):
        """Polymer.is_hernia(pair) -> a bool

        Returns True if the given pair of links forms a hernia.
        """
        return set(pair) in [{Link.UP, Link.DOWN}, {Link.LEFT, Link.RIGHT}]

    @staticmethod
    def both_slacks(pair):
        return pair == (Link.SLACK, Link.SLACK)

HERNIA_PAIRS = {(link, link.opposite()) for link in Link.TAUT_LINKS}

HERNIAS = {
    Polymer([Link.UP, Link.DOWN]), Polymer([Link.DOWN, Link.UP]),
    Polymer([Link.LEFT, Link.RIGHT]), Polymer([Link.RIGHT, Link.LEFT]),
}