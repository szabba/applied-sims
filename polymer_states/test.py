#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.util import safe_repr
from polymer_states import Polymer, HERNIAS, Link


class SetAssertions(unittest.TestCase):
    """Mix-in providing assertions related to sets"""

    def assertIsSubsetOf(self, subset, superset, msg=None):
        """Asserts that one set is a subset of another one."""
        if not subset.issubset(superset):
            standardMsg = '{} is not a subset of {}'.format(
                safe_repr(subset), safe_repr(superset))
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


class PolymerTest(SetAssertions, unittest.TestCase):

    def test_value_error_for_zero_links(self):
        self.assertRaises(ValueError, Polymer, [])

    def test_value_error_for_zero_links_when_curled_up(self):
        self.assertRaises(ValueError, Polymer.all_curled_up, 0)

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

    def test_polymer_reachable_set_contains_self(self):
        polymer = Polymer.all_curled_up(3)

        reachable = polymer.reachable_from()

        self.assertIn(polymer, reachable)

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

    # TODO: Barrier crossings
    # TODO: Hernia migrations
    # TODO: End-link migrations