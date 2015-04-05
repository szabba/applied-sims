#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy


# Link states
UP, DOWN = (0, 1), (0, -1)
LEFT, RIGHT = (-1, 0), (1, 0)
SLACK = (0, 0)


class Polymer:
    """A chain of N links."""

    def __init__(self, links):
        self.__links = numpy.array(links)