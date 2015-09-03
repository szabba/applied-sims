#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

import numpy
import scipy.misc
from matplotlib import pyplot
from argparse import ArgumentParser
from polymer_states import Polymer, MoveType

parser = ArgumentParser()
parser.add_argument('link_count', metavar='LINK_COUNT', type=int)
parser.add_argument('h', metavar='H', type=float)
parser.add_argument('c', metavar='C', type=float)
parser.add_argument('--out', '-o', metavar='OUT')
args = parser.parse_args()


def generate_image(matrix):
    state_count = matrix.size()
    image = numpy.zeros((state_count, state_count), dtype=numpy.float)
    state_order = list(sorted(matrix.states()))
    for i, origin in enumerate(state_order):
        for j, target in enumerate(state_order):
            image[i, j] = matrix[origin, target]

    print(image.max())
    image /= image.max()
    return image

if __name__ == '__main__':
    rates = {
        MoveType.REPTATION: 1.0,
        MoveType.HERNIA_CREATION: args.h,
        MoveType.HERNIA_ANNIHILATION: args.h,
        MoveType.HERNIA_REDIRECTION: args.h,
        MoveType.BARRIER_CROSSING: args.c,
        MoveType.END_EXTENSION: 1.0,
        MoveType.END_CONTRACTION: args.h,
        MoveType.END_WIGGLE: args.h,
    }
    matrix = Polymer.transition_matrix(args.link_count, rates)
    image = generate_image(matrix)
    if not args.out:
        pyplot.imshow(image, interpolation='nearest', cmap=pyplot.get_cmap('gray'))
        pyplot.show()
    else:
        scipy.misc.imsave(args.out, image)
