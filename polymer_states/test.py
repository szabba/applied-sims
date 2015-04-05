#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import unittest
from polymer_states import Polymer, SLACK, UP, DOWN, LEFT, RIGHT


class PolymerTest(unittest.TestCase):

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
