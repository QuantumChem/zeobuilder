# ConScan is a molecular connection scanner
# Copyright (C) 2007 - 2010 Toon Verstraelen <Toon.Verstraelen@UGent.be>
#
# This file is part of ConScan.
#
# ConScan is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# ConScan is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#
# --


from molmod import PairSearchInter

import numpy, sys, copy


__all__  = ["Geometry", "Connection", "ProgressMessage"]


class Geometry(object):
    def __init__(self, coordinates, connect_masks, radii):
        assert len(coordinates.shape) == 2
        assert coordinates.shape[1] == 3
        l = len(coordinates)
        assert l > 0
        assert l == len(connect_masks)
        assert l == len(radii)
        self.coordinates = coordinates
        self.connect_masks = connect_masks
        self.radii = radii


class Connection(object):
    def __init__(self, pairs):
        self.transformation = None
        self.inverse_transformation = None
        self.quality = None
        self.duplicate = False
        self.invertible = False
        self.pairs = pairs

    def set_transformation(self, transformation):
        self.transformation = transformation
        if self.transformation.compare(self.transformation.inv):
            self.inverse_transformation = None

    def compute_quality(self, geometry1, geometry2):
        transformed_coordinates2 = self.transformation*geometry2.coordinates

        self.quality = 0.0
        pairs = []
        psi = PairSearchInter(
            geometry1.coordinates,
            transformed_coordinates2,
            max(geometry1.radii.max(), geometry2.radii.max())
        )
        for i1, i2, delta, distance in psi:
            radius = geometry1.radii[i1] + geometry2.radii[i2]
            if distance < radius:
                x = distance/radius
                if geometry1.connect_masks[i1] and geometry2.connect_masks[i2]:
                    self.quality += (1-x**2)
                    pairs.append((i1,i2))
                else:
                    self.quality -= 2*(1-x**2)
        self.pairs = frozenset(pairs)


class ProgressMessage(object):
    def __init__(self, label, progress, maximum):
        self.label = label
        self.progress = progress
        self.maximum = maximum


