#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from unittest.util import safe_repr
from polymer_states import Polymer, SLACK, UP, DOWN, LEFT, RIGHT, HERNIAS


class SetAssertions(unittest.TestCase):
    """Mix-in providing assertions related to sets"""

    def assertIsSubsetOf(self, subset, superset, msg=None):
        """Asserts that one set is a subset of another one."""
        if not subset.issubset(superset):
            standardMsg = '{} is not a subset of {}'.format(
                safe_repr(subset), safe_repr(superset))
            self.fail(self._formatMessage(msg, standardMsg))


class PolymerTest(SetAssertions, unittest.TestCase):

    def test_value_error_for_zero_links(self):
        self.assertRaises(ValueError, Polymer, [])

    def test_value_error_for_zero_links_when_curled_up(self):
        self.assertRaises(ValueError, Polymer.all_curled_up, 0)

    def test_polymers_with_equal_links_are_equal(self):
        links = [UP, LEFT, RIGHT, DOWN, SLACK, UP]
        polymer_one = Polymer(links)
        polymer_two = Polymer(links)

        self.assertEqual(polymer_one, polymer_two)

    def test_polymers_with_different_links_are_not_equal(self):
        links = [UP, LEFT, RIGHT, DOWN, SLACK, UP]
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
        polymer = Polymer([UP, DOWN, SLACK])

        self.assertTrue(polymer.contains_hernia())

    def test_polymer_knows_it_does_not_contain_hernia(self):
        polymer = Polymer([UP, SLACK, DOWN])

        self.assertFalse(polymer.contains_hernia())

    def test_polymer_knows_it_contains_two_consecutive_slacks(self):
        polymer_with_slack_pair = Polymer([UP, SLACK, SLACK])

        self.assertTrue(polymer_with_slack_pair.contains_slack_pair())

    def test_polymer_knows_it_does_not_contain_two_consecutive_slacks(self):
        polymer_wihtout_slack_pair = Polymer([UP, UP, LEFT, RIGHT, DOWN])

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

    # TODO: Hernia annihilation
    # TODO: Rubinstein-Duke moves
    # TODO: End-link Rubinstein-Duke moves
    # TODO: Barrier crossings
    # TODO: Hernia migrations
    # TODO: End-link migrations