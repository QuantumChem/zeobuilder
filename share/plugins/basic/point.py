# Zeobuilder is an extensible GUI-toolkit for molecular model construction.
# Copyright (C) 2005 Toon Verstraelen
#
# This file is part of Zeobuilder.
#
# Zeobuilder is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# --


from zeobuilder import context
from zeobuilder.actions.composed import Immediate
from zeobuilder.actions.abstract import AddBase
from zeobuilder.actions.collections.menu import MenuInfo
from zeobuilder.nodes.meta import Property
from zeobuilder.nodes.elementary import GLGeometricBase
from zeobuilder.nodes.model_object import ModelObjectInfo
from zeobuilder.nodes.color_mixin import ColorMixin
from zeobuilder.nodes.glmixin import GLTransformationMixin
from zeobuilder.gui.fields_dialogs import DialogFieldInfo
import zeobuilder.gui.fields as fields
import zeobuilder.actions.primitive as primitive
import zeobuilder.authors as authors

from molmod.transformations import Translation

import numpy


class Point(GLGeometricBase, ColorMixin):
    info = ModelObjectInfo("plugins/basic/point.svg")
    authors = [authors.toon_verstraelen]

    def initnonstate(self):
        GLGeometricBase.initnonstate(self, Translation)

    #
    # Properties
    #

    def set_spike_length(self, spike_length):
        self.spike_length = spike_length
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    def set_spike_thickness(self, spike_thickness):
        self.spike_thickness = spike_thickness
        self.invalidate_draw_list()
        self.invalidate_boundingbox_list()

    properties = [
        Property("spike_length", 0.3, lambda self: self.spike_length, set_spike_length),
        Property("spike_thickness", 0.1, lambda self: self.spike_thickness, set_spike_thickness),
    ]

    #
    # Dialog fields (see action EditProperties)
    #

    dialog_fields = set([
        DialogFieldInfo("Geometry", (2, 7), fields.faulty.Length(
            label_text="Spike length",
            attribute_name="spike_length",
            low=0.0,
            low_inclusive=False
        )),
        DialogFieldInfo("Geometry", (2, 8), fields.faulty.Length(
            label_text="Spike thickness",
            attribute_name="spike_thickness",
            low=0.0,
            low_inclusive=False
        ))
    ])

    #
    # Draw
    #

    def draw_spike(self):
        ColorMixin.draw(self)
        vb = context.application.vis_backend
        vb.draw_quad_strip(
            coordinates = numpy.array([
                [self.spike_length, self.spike_length, self.spike_length],
                [self.spike_thickness, 0, 0],
                [self.spike_length, self.spike_length, self.spike_length],
                [0, self.spike_thickness, 0],
                [self.spike_length, self.spike_length, self.spike_length],
                [0, 0, self.spike_thickness],
                [self.spike_length, self.spike_length, self.spike_length],
                [self.spike_thickness, 0, 0],
            ], float),
            normals = numpy.array([
                [0.5773502692, -0.5773502692, -0.5773502692],
                [1, 0, 0],
                [-0.5773502692, 0.5773502692, -0.5773502692],
                [0, 1, 0],
                [-0.5773502692, -0.5773502692, 0.5773502692],
                [0, 0, 1],
                [0.5773502692, -0.5773502692, -0.5773502692],
                [1, 0, 0],
            ], float),
        )

    def draw(self):
        GLGeometricBase.draw(self)
        vb = context.application.vis_backend
        vb.push_matrix()
        for i in range(2):
            for i in range(4):
                self.draw_spike()
                vb.rotate(90, 1.0, 0.0, 0.0)
            vb.rotate(180, 0.0, 1.0, 0.0)
        vb.pop_matrix

    def write_pov(self, indenter):
        def write_spike(signs):
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("< %f, 0.0, 0.0>," % (signs[0]*self.spike_thickness))
            indenter.write_line("<0.0,  %f, 0.0>" % (signs[1]*self.spike_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("<0.0,  %f, 0.0>," % (signs[1]*self.spike_thickness))
            indenter.write_line("<0.0, 0.0,  %f>" % (signs[2]*self.spike_thickness))
            indenter.write_line("}", -1)
            indenter.write_line("triangle {", 1)
            indenter.write_line("< %f,  %f,  %f>," % (signs[0]*self.spike_length, signs[1]*self.spike_length, signs[2]*self.spike_length))
            indenter.write_line("<0.0, 0.0,  %f>," % (signs[2]*self.spike_thickness))
            indenter.write_line("< %f, 0.0, 0.0>" % (signs[0]*self.spike_thickness))
            indenter.write_line("}", -1)

        signslist = [((i/4 % 2) * 2 - 1, (i/2 % 2) * 2 - 1, (i % 2) * 2 - 1) for i in range(8)]
        indenter.write_line("mesh {", 1)
        for signs in signslist:
            write_spike(signs)
        indenter.write_line("inside_vector <0.0, 0.0, 0.0>")
        indenter.write_line("pigment { rgb <%f, %f, %f> }" % tuple(self.color[0:3]))
        GLGeometricBase.write_pov(self, indenter)
        indenter.write_line("}", -1)

    #
    # Revalidation
    #

    def revalidate_bounding_box(self):
        GLGeometricBase.revalidate_bounding_box(self)
        self.bounding_box.extend_with_corners([-self.spike_length*numpy.ones(3, float), self.spike_length*numpy.ones(3, float)])


class AddPoint(AddBase):
    description = "Add point"
    menu_info = MenuInfo("default/_Object:tools/_Add:3d", "_Point", image_name="plugins/basic/point.svg", order=(0, 4, 1, 0, 0, 2))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        return AddBase.analyze_selection(Point)

    def do(self):
        AddBase.do(self, Point)


class CalculateAverage(Immediate):
    description = "Add point at average"
    menu_info = MenuInfo("default/_Object:tools/_Add:special", "_Point at average", order=(0, 4, 1, 0, 2, 0))
    authors = [authors.toon_verstraelen]

    @staticmethod
    def analyze_selection():
        # A) calling ancestor
        if not Immediate.analyze_selection(): return False
        # B) validating and initialising
        cache = context.application.cache
        if len(cache.nodes) == 0: return False
        if len(cache.translations) == 0: return False
        parent = cache.common_parent
        if parent == None: return False
        while not parent.check_add(Point):
            parent = parent.parent
            if parent == None: return False
        # C) passed all tests:
        return True

    def do(self):
        cache = context.application.cache
        parent = cache.common_parent
        while not parent.check_add(Point):
            parent = parent.parent

        vector_sum = numpy.zeros(3, float)
        num_vectors = 0

        for node in cache.nodes:
            if isinstance(node, GLTransformationMixin) and \
               isinstance(node.transformation, Translation):
                vector_sum += node.get_frame_relative_to(parent).t
                num_vectors += 1

        point = Point(name="Average")
        point.transformation.t = vector_sum / num_vectors
        primitive.Add(point, parent)


nodes = {
    "Point": Point
}

actions = {
    "AddPoint": AddPoint,
    "CalculateAverage": CalculateAverage,
}