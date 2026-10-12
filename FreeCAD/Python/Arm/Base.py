"""
Robot arm base.

All measurements are in mm.
"""

import math
import FreeCAD as App
from FreeCAD import Base
import Part
from BasicShapes import Shapes

''' Make a hole at Z direction.
'''
def MakeHoleZ(shape, x, y, d, z0, z1):
    tool = Part.makeCylinder(d / 2.0, z1 - z0, Base.Vector(x, y, z0),
                             Base.Vector(0, 0, 1))
    return shape.cut(tool)

''' Make a tube.
'''
def MakeTube(outerD, innerD, height, x, y, z0):
    outer = Part.makeCylinder(outerD / 2.0, height, Base.Vector(x, y, z0), Base.Vector(0, 0, 1))
    inner = Part.makeCylinder(innerD / 2.0, height, Base.Vector(x, y, z0), Base.Vector(0, 0, 1))
    return outer.cut(inner)

class BasePlate:
    def __init__(self):
        self.height = 10
        self.mountHoleD = 6
        self.motorMountHoleD = 4
        pass

    def CreateMotorMount(self):
        mount = Part.makeBox(38, 60, self.height + 2, Base.Vector(-19, -135, -1))
        edges = [mount.Edges[0], mount.Edges[2], mount.Edges[4], mount.Edges[6]]
        mount = mount.makeFillet(18, edges)
        return mount

    def Instantiate(self, doc):
        # Base plate
        basePlate = Part.makeBox(160, 200, self.height, Base.Vector(-80, -150, 0))

        # Create fillet
        edges = [basePlate.Edges[0], basePlate.Edges[2], basePlate.Edges[4], basePlate.Edges[6]]
        basePlate = basePlate.makeFillet(20, edges)

        # Cut the spindle hole
        basePlate = MakeHoleZ(basePlate, 0, 0, 75, -1, self.height + 1)        

        # Add the bearing support
        support = MakeTube(75, 64, 5, 0, 0, 0)
        basePlate = basePlate.fuse(support)

        # Add the bearing holder
        holder = MakeTube(100, 75, 30, 0, 0, self.height)
        basePlate = basePlate.fuse(holder)

        # Cut mounting holes
        for y in (-130, 30):
            for x in (-60, 60):
                basePlate = MakeHoleZ(basePlate, x, y, self.mountHoleD, -1, self.height + 1)

        # Cut motor mount
        motorMount = self.CreateMotorMount()
        basePlate = basePlate.cut(motorMount)

        # Cut motor mounting holes
        for y in (-120.5, -89.5):
            for x in (-25, 25):
                basePlate = MakeHoleZ(basePlate, x, y, self.motorMountHoleD, -1, self.height + 1)

        # Create the object
        base_obj = doc.addObject("Part::Feature", "BasePlate")
        base_obj.Shape = basePlate

        doc.recompute()

# Create a new document.
# doc = FreeCAD.newDocument("DesktopPanTilt")
doc = App.activeDocument()

# Instantiate the base.
BasePlate().Instantiate(doc)
