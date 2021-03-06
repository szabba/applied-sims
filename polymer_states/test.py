#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
import functools

import unittest
from unittest.util import safe_repr
import operator

from polymer_states import Polymer, HERNIAS, Link, MoveType, TransitionMatrix


class SetAssertions(unittest.TestCase):
    """Mix-in providing assertions related to sets"""

    NOT_SUBSET_OF_MSG_TEMPLATE = """{} is not a subset of {}, missing {}"""

    def assertIsSubsetOf(self, subset: set, superset: set, msg=None):
        """Asserts that one set is a subset of another one."""
        if not subset.issubset(superset):
            missing = subset.difference(superset)
            standardMsg = self.NOT_SUBSET_OF_MSG_TEMPLATE\
                .format(safe_repr(subset),
                        safe_repr(superset),
                        safe_repr(missing))
            self.fail(self._formatMessage(msg, standardMsg))


class LinkTest(unittest.TestCase):

    def test_value_error_for_invalid_link_values(self):
        self.assertRaises(ValueError, Link, -1)
        self.assertRaises(ValueError, Link, 32)

    def test_no_error_for_valid_link_values(self):
        for valid_link_value in Link.VALID_LINK_VALUES:
            Link(valid_link_value)

    def test_link_equal_to_its_value(self):
        for valid_link_value in Link.VALID_LINK_VALUES:
            self.assertEqual(Link(valid_link_value), valid_link_value)


class PolymerEqualityTest(unittest.TestCase):

    def test_polymers_with_equal_links_are_equal(self):
        links = [Link.UP, Link.LEFT, Link.RIGHT, Link.DOWN, Link.SLACK, Link.UP]
        polymer_one = Polymer(links)
        polymer_two = Polymer(links)

        self.assertEqual(polymer_one, polymer_two)

    def test_polymers_with_different_links_are_not_equal(self):
        links = [Link.UP, Link.LEFT, Link.RIGHT, Link.DOWN, Link.SLACK, Link.UP]
        polymer_one = Polymer(links)
        polymer_two = Polymer(reversed(links))

        self.assertNotEqual(polymer_one, polymer_two)

    def test_polymers_with_different_length_are_not_equal(self):
        polymer_one = Polymer.all_curled_up(2)
        polymer_two = Polymer.all_curled_up(3)

        self.assertNotEqual(polymer_one, polymer_two)


class PolymerModificationTest(unittest.TestCase):

    def test_substitution_for_first_link_pair(self):
        polymer = Polymer.all_curled_up(3)

        modified = polymer.substitute_pair(0, (None, Link.UP))

        self.assertEqual(modified, Polymer([Link.UP, Link.SLACK, Link.SLACK]))

    def test_substitution_for_last_link_pair(self):
        polymer = Polymer.all_curled_up(3)

        modified = polymer.substitute_pair(3, (Link.DOWN, None))

        self.assertEqual(modified, Polymer([Link.SLACK, Link.SLACK, Link.DOWN]))

    def test_substitution_inside_chain(self):
        polymer = Polymer.all_curled_up(4)

        modified = polymer.substitute_pair(2, (Link.DOWN, Link.UP))

        self.assertEqual(modified,
                         Polymer([Link.SLACK, Link.DOWN, Link.UP, Link.SLACK]))


class PolymerReachabilityTest(SetAssertions, unittest.TestCase):

    def test_polymer_reachable_returns_set(self):
        polymer = Polymer.all_curled_up(3)

        reachable = polymer.reachable_from()

        self.assertIsInstance(reachable, set)

    def test_polymer_knows_it_contains_hernia(self):
        polymer = Polymer([Link.UP, Link.DOWN, Link.SLACK])

        self.assertTrue(polymer.contains_hernia())

    def test_polymer_knows_it_does_not_contain_hernia(self):
        polymer = Polymer([Link.UP, Link.SLACK, Link.DOWN])

        self.assertFalse(polymer.contains_hernia())

    def test_polymer_knows_it_contains_two_consecutive_slacks(self):
        polymer_with_slack_pair = Polymer([Link.UP, Link.SLACK, Link.SLACK])

        self.assertTrue(polymer_with_slack_pair.contains_slack_pair())

    def test_polymer_knows_it_does_not_contain_two_consecutive_slacks(self):
        polymer_wihtout_slack_pair = Polymer([Link.UP, Link.UP, Link.LEFT, Link.RIGHT, Link.DOWN])

        self.assertFalse(polymer_wihtout_slack_pair.contains_slack_pair())

    def test_polymer_reachable_set_does_not_contain_self(self):
        # All kinds of legal moves are possible in the polymer given below.
        polymer = Polymer([
            # Starts with a slack link
            Link.SLACK,
            # Contains a taut-slack pair
            Link.RIGHT, Link.SLACK,
            # Contains two slack links in a single cell
            Link.SLACK, Link.SLACK,
            # Contains a three cells "bent knee"
            Link.RIGHT, Link.UP,
            # Contains a hernia
            Link.RIGHT, Link.LEFT,
            # Ends with a taut link
            Link.UP
        ])

        reachable = polymer.reachable_from()

        self.assertNotIn(polymer, reachable)

    def test_two_slacks_can_turn_into_hernia(self):
        two_slack_polymer = Polymer.all_curled_up(2)

        reachable = two_slack_polymer.reachable_from()

        self.assertIsSubsetOf(HERNIAS, reachable)

    def test_three_slacks_generate_hernias(self):
        init_polymer = Polymer.all_curled_up(3)

        reachable = init_polymer.reachable_from()

        self.assertTrue(
            any(polymer.contains_hernia() for polymer in reachable))

    def test_hernia_generates_polymer_with_two_slacks(self):
        hernia = Polymer([Link.UP, Link.DOWN])

        reachable = hernia.reachable_from()

        self.assertTrue(
            any(polymer.contains_slack_pair() for polymer in reachable))

    def test_repton_can_move_between_cells_when_it_has_one_slack_link(self):
        polymer = Polymer([Link.UP, Link.LEFT, Link.SLACK, Link.LEFT, Link.DOWN])
        with_slack_moved = {
            Polymer([Link.UP, Link.SLACK, Link.LEFT, Link.LEFT, Link.DOWN]),
            Polymer([Link.UP, Link.LEFT, Link.LEFT, Link.SLACK, Link.DOWN]),
        }

        reachable = polymer.reachable_from()

        self.assertIsSubsetOf(with_slack_moved, reachable)

    def test_first_link_can_go_from_slack_to_taut(self):
        polymer = Polymer([Link.SLACK, Link. RIGHT])
        with_first_link_changed = {
            Polymer([Link.RIGHT, Link.RIGHT]),
            Polymer([Link.LEFT, Link.RIGHT]),
            Polymer([Link.UP, Link.RIGHT]),
            Polymer([Link.DOWN, Link.RIGHT]),
        }

        reachable = polymer.reachable_from()

        self.assertIsSubsetOf(with_first_link_changed, reachable)

    def test_last_link_can_go_from_slack_to_taut(self):
        polymer = Polymer([Link.RIGHT, Link.SLACK])
        with_last_link_changed = {
            Polymer([Link.RIGHT, Link.RIGHT]),
            Polymer([Link.RIGHT, Link.LEFT]),
            Polymer([Link.RIGHT, Link.UP]),
            Polymer([Link.RIGHT, Link.DOWN]),
        }

        reachable = polymer.reachable_from()

        self.assertIsSubsetOf(with_last_link_changed, reachable)

    def test_first_link_can_become_slack_when_taut(self):
        polymer = Polymer([Link.UP, Link.LEFT, Link.UP])
        with_first_slacked = Polymer([Link.SLACK, Link.LEFT, Link.UP])

        reachable = polymer.reachable_from()

        self.assertIn(with_first_slacked, reachable)

    def test_last_link_can_become_slack_when_taut(self):
        polymer = Polymer([Link.UP, Link.LEFT, Link.UP])
        with_last_slacked = Polymer([Link.UP, Link.LEFT, Link.SLACK])

        reachable = polymer.reachable_from()

        self.assertIn(with_last_slacked, reachable)

    def test_right_angle_link_pairs_can_be_flipped_over(self):
        polymer = Polymer([Link.UP, Link.RIGHT])
        flipped = Polymer([Link.RIGHT, Link.UP])

        reachable = polymer.reachable_from()

        self.assertIn(flipped, reachable)

    def test_hernias_can_change_bend_direction_to_any_other(self):
        polymer = Polymer([Link.UP, Link.DOWN])

        reachable = polymer.reachable_from()

        self.assertIsSubsetOf(HERNIAS - {polymer}, reachable)

    def test_end_link_can_become_anything_except_itself(self):
        first_link, last_link = Link.SLACK, Link.RIGHT
        polymer = Polymer([first_link, Link.UP, last_link])
        with_end_links_changed = {
            Polymer([link, Link.UP, Link.RIGHT]) for link in Link.LINKS
            if link != first_link
        }.union({
            Polymer([Link.SLACK, Link.UP, link]) for link in Link.LINKS
            if link != last_link
        })

        reachable = polymer.reachable_from()

        self.assertIsSubsetOf(with_end_links_changed, reachable)


class TransitionRates(unittest.TestCase):

    MOVE_RATES = dict(
        (move_type, move_type)
        for move_type in (
            MoveType.HERNIA_CREATION,
            MoveType.REPTATION,
            MoveType.BARRIER_CROSSING,
            MoveType.HERNIA_ANNIHILATION,
            MoveType.HERNIA_REDIRECTION,
            MoveType.END_CONTRACTION,
            MoveType.END_EXTENSION,
            MoveType.END_WIGGLE))


class PolymerTransitionRatesTest(TransitionRates):

    @classmethod
    def all_with_3_links(cls):
        if not hasattr(cls, 'ALL_WITH_3_LINKS'):
            cls.ALL_WITH_3_LINKS = Polymer.all_with_n_links(3)
        return cls.ALL_WITH_3_LINKS

    def assertTransitionTypePresent(self, rates: dict, transition_type):
        """PTRT.assertTransitionTypePresent(rates, transition_type)

        Asserts that the result of calling `Polymer.transition_rates` with
        `MOVE_RATES` and `operator.op_` contains a transition of type
        `transition_type`.
        """

        all_types = functools.reduce(operator.or_, rates.values(), 0)

        if not (all_types & transition_type):
            self.fail(
                "{} doesn't contain a transition of type {}"
                .format(rates, transition_type))

    def test_transition_rates_returns_a_dictionary(self):
        for polymer in PolymerTransitionRatesTest.all_with_3_links():
            self.assertIsInstance(
                polymer.transition_rates(
                    self.MOVE_RATES,
                    sum_with=operator.or_),
                dict)

    def test_keys_are_the_values_reachable_from_the_given_polymer(self):
        for polymer in PolymerTransitionRatesTest.all_with_3_links():
            transition_rates = polymer.transition_rates(
                self.MOVE_RATES,
                sum_with=operator.or_)

            reachable = polymer.reachable_from()

            self.assertEqual(
                set(transition_rates.keys()),
                reachable)

    def test_hernia_creation_present_when_possible(self):
        polymer = Polymer([Link.SLACK, Link.SLACK])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.HERNIA_CREATION)

    def test_hernia_annihilation_present_when_possible(self):
        polymer = Polymer([Link.UP, Link.DOWN])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.HERNIA_ANNIHILATION)

    def test_hernia_redirection_present_when_possible(self):
        polymer = Polymer([Link.UP, Link.DOWN])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.HERNIA_REDIRECTION)

    def test_reptation_present_when_possible(self):
        polymer = Polymer([Link.UP, Link.SLACK])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.REPTATION)

    def test_barrier_crossing_present_when_possible(self):
        polymer = Polymer([Link.UP, Link.RIGHT])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.BARRIER_CROSSING)

    def test_end_contraction_present_when_possible(self):
        polymer = Polymer([Link.RIGHT, Link.SLACK, Link.SLACK])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.END_CONTRACTION)

    def test_end_extension_present_when_possible(self):
        polymer = Polymer([Link.RIGHT, Link.SLACK, Link.SLACK])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.END_EXTENSION)

    def test_end_wiggle_present_when_possible(self):
        polymer = Polymer([Link.RIGHT, Link.SLACK, Link.SLACK])

        transition_rates = polymer.transition_rates(self.MOVE_RATES,
                                                    operator.or_)

        self.assertTransitionTypePresent(transition_rates,
                                         MoveType.END_WIGGLE)


class PolymerPossibleConfigurationsTest(unittest.TestCase):

    def test_unit_polymer_contains_all_types_of_links(self):
        length = 1
        polymers = Polymer.all_with_n_links(1)

        self.assertTrue(
            all(any(link in polymer.links()
                    for polymer in polymers)
                for link in Link.LINKS))

    def test_number_of_polymers_of_given_length_is_right(self):
        for length in range(1, 3):
            polymers = Polymer.all_with_n_links(length)

            self.assertEqual(len(polymers), len(Link.LINKS) ** length)

    def test_all_with_n_links_returns_polymer_set(self):
        for length in range(1, 3):
            polymers = Polymer.all_with_n_links(length)

            self.assertIsInstance(polymers, set)
            self.assertTrue(all(isinstance(polymer, Polymer)
                                for polymer in polymers))

    # TODO: Build up a TransitionMatrix.


class PolymerTransitionMatrixTest(TransitionRates):

    def test_can_create_a_transition_matrix(self):
        polymer_length = 3

        matrix = Polymer.transition_matrix(
            polymer_length, self.MOVE_RATES, operator.or_)

        self.assertIsInstance(matrix, TransitionMatrix)

    def test_transition_matrix_has_right_dimmensions(self):
        polymer_length = 3
        state_count = len(Polymer.all_with_n_links(polymer_length))

        matrix = Polymer.transition_matrix(
            polymer_length, self.MOVE_RATES, operator.or_)

        self.assertEqual(matrix.size(), state_count)

    def test_transition_matrix_indexes(self):
        polymer_length = 2
        state_count = len(Polymer.all_with_n_links(polymer_length))
        first_state = Polymer([Link.UP, Link.RIGHT])
        second_state = Polymer([Link.SLACK, Link.RIGHT])

        matrix = Polymer.transition_matrix(
            polymer_length, self.MOVE_RATES, operator.or_)

        transition_rate = matrix[first_state, second_state]

        self.assertEqual(transition_rate,
                         self.MOVE_RATES[MoveType.END_CONTRACTION])

    def test_transition_matrix_states(self):
        polymer_length = 3
        all_states = Polymer.all_with_n_links(polymer_length)

        matrix = Polymer.transition_matrix(polymer_length, self.MOVE_RATES, operator.or_)

        matrix_states = matrix.states()

        self.assertEqual(all_states, matrix_states)
