#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.

from argparse import ArgumentParser
from polymer_states import Polymer


parser = ArgumentParser()
parser.add_argument('link_count', metavar='LINK_COUNT', type=int)
args = parser.parse_args()


if __name__ == '__main__':

    polymers = Polymer.all_with_n_links(args.link_count)
    for polymer in polymers:
        print(polymer)
