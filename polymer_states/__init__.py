#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.


__all__ = ['Link', 'MoveType', 'Polymer', 'HERNIAS', 'HERNIA_PAIRS']


import functools
import operator


class Link(int):
    """A polymer chain link on a 2D lattice."""

    VALID_LINK_VALUES = {1 << i for i in range(5)}

    def __new__(cls, value):
        if value not in Link.VALID_LINK_VALUES:
            raise ValueError("invalid link value {}".format(value))
        return int.__new__(Link, value)

    def __init__(self, value):
        pass

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


class MoveType(int):
    """A type of move with which we can associate a transition rate."""

    VALID_MOVE_TYPE_VALUES = {1 << i for i in range(8)}

    def __new__(cls, value):
        if value not in MoveType.VALID_MOVE_TYPE_VALUES:
            raise ValueError("invalid move type value {}".format(value))
        return int.__new__(MoveType, value)

    def __init__(self, value):
        pass


MoveType.MOVE_TYPES = {MoveType(i) for i in MoveType.VALID_MOVE_TYPE_VALUES}
(
    MoveType.HERNIA_CREATION,
    MoveType.REPTATION,
    MoveType.BARRIER_CROSSING,
    MoveType.HERNIA_ANNIHILATION,
    MoveType.HERNIA_,
    MoveType.END_CONTRACTION,
    MoveType.END_EXTENSION,
    MoveType.END_WIGGLE,
) = MoveType.MOVE_TYPES


def at_end_pairs(f):
    """A decorator turning `Link -> set of Links` functions into `Polymer`
    methods that transform the end links of a chain.
    """
    @functools.wraps(f)
    def wrapper(self, p, pair):
        if not Polymer.is_edge_pair(pair):
            return set()
        link = [l for l in pair if l is not None][0]
        new_links = f(link)
        new_pairs = {
            tuple([
                      old_link if old_link is None else new_link
                      for old_link
                      in pair
                      ])
            for new_link
            in new_links
        }
        return {
            self.substitute_pair(p, new_pair)
            for new_pair
            in new_pairs
        }
    return wrapper


class Polymer:
    """A chain of N links."""

    def __init__(self, links):
        self.__links = tuple(map(Link, links))
        self.__polymer_transformers = (
            self.__contract_taut_ends_if_possible,
            self.__extract_slack_ends_if_possible,
            self.__wiggle_end_links_if_possible,
            self.__create_hernias_if_possible,
            self.__repate_if_possible,
            self.__anihilate_hernias_if_possible,
            self.__change_hernia_bend_direction_if_possible,
            self.__flip_bent_pair_if_possible,
        )

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
    def transition_rates(self, move_rates: dict, sum_with = operator.add, zero = 0) -> dict:
        """P.transition_rates(move_rates[, sum_with]) -> dict with polymer keys

        Calculates the transition rates to all states reachable from the current
        one in one step, given that `move_rates` is a dictionary mapping kinds
        of moves to rates.

        The rates for different moves are combined using `sum_with` which
        defaults to `operator.add`. It must be associative and commutative.

        `zero` should be the identify of `sum_with`.
        """

        rates = {}
        for p, pair in enumerate(self.link_pairs()):
            for t in self.__polymer_transformers:
                new_polymers = t(p, pair)

                for new_polymer in new_polymers:
                    old_rate = rates.get(new_polymer, zero)
                    new_rate = sum_with(old_rate, zero)
                    rates[new_polymer] = new_rate

        return rates

    def __repate_if_possible(self, p, pair):
        if Polymer.can_reptate(pair):
            return self.__reptate_at(p, pair)
        return set()

    def __create_hernias_if_possible(self, p, pair):
        if Polymer.both_slacks(pair):
            return self.__create_hernias_at(p, pair)
        return set()

    def __anihilate_hernias_if_possible(self, p, pair):
        if Polymer.is_hernia(pair):
            return {
                self.__annihilate_hernia_at(p)
            }
        return set()

    def __change_hernia_bend_direction_if_possible(self, p, pair):
        if Polymer.is_hernia(pair):
            return self.__change_hernia_bend_direction(p, pair)
        return set()

    def __flip_bent_pair_if_possible(self, p, pair):
        if Polymer.is_bent_pair(pair):
            return {
                self.__flip_at(p, pair)
            }
        return set()

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

    @at_end_pairs
    def __contract_taut_ends_if_possible(link):
        if link.is_taut():
            return {Link.SLACK}
        return set()

    @at_end_pairs
    def __extract_slack_ends_if_possible(link):
        if link.is_slack():
            return Link.TAUT_LINKS
        return set()

    @at_end_pairs
    def __wiggle_end_links_if_possible(link):
        if not link.is_taut():
            return set()
        return {
            taut_link
            for taut_link
            in Link.TAUT_LINKS
            if taut_link != link
        }

    def __flip_at(self, i, current):
        first, second = current
        return self.substitute_pair(i, (second, first))

    def __change_hernia_bend_direction(self, i, current):
        return {
            self.substitute_pair(i, hernia)
            for hernia in HERNIA_PAIRS
            if hernia != current
        }

    # TODO: What happens when the Polymer has no links?
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