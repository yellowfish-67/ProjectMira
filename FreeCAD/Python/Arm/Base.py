"""
Robot arm base.

All measurements are in mm.
"""

import math
import FreeCAD as App
from FreeCAD import Base
import Part
from BasicShapes import Shapes
import freecad.gears.commands

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

''' Base plate definition.
'''
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

    def Instantiate(self, doc, name, tVec=None, rVec=None):
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
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = basePlate
        doc.recompute()

''' J1 bearing.
'''
class J1_Bearing:
    def __init__(self):
        self.innerD = 45
        self.outerD = 75
        self.height = 16

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = MakeTube(self.outerD, self.innerD, self.height, 0, 0, 0)

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)
        # shape = shape.rotated(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 45)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' Spindle definition.
'''
class J1_Spindle:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # HTD5 gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = 60
        gear.height = 12
        gear.type = "htd5"
        doc.recompute()
        gear.Visibility = False

        # Gear pads
        pad1 = Part.makeCylinder(48, 2, Base.Vector(0, 0, -2), Base.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(48, 2, Base.Vector(0, 0, 12), Base.Vector(0, 0, 1))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        # Spindle body
        param1 = [27, 8, 14]
        shape = gearShape.fuse(Part.makeCylinder(param1[0], param1[1], Base.Vector(0, 0, param1[2]),
                Base.Vector(0, 0, 1)))
        param2 = [22.7, 38, param1[2] + param1[1]]
        shape = shape.fuse(Part.makeCylinder(param2[0], param2[1], Base.Vector(0, 0, param2[2]),
                Base.Vector(0, 0, 1)))

        # Cut mounting holes
        z = param2[1] + param2[2] - 10
        shape = MakeHoleZ(shape, 0, 15, 5, z, z + 10)
        shape = MakeHoleZ(shape, 0, -15, 5, z, z + 10)
        shape = MakeHoleZ(shape, 15, 0, 5, z, z + 10)
        shape = MakeHoleZ(shape, -15, 0, 5, z, z + 10)

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)
        if rVec != None:
            shape = shape.rotated(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 45)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J1 motor
'''
class J1_Motor:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # HTD5 gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = 15
        gear.height = 16
        gear.type = "htd5"
        doc.recompute()
        gear.Visibility = False

        # Gear pads
        pad1 = Part.makeCylinder(12, 2, Base.Vector(0, 0, -2), Base.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(12, 2, Base.Vector(0, 0, 15), Base.Vector(0, 0, 1))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        # Motor body
        motorBody = Part.makeBox(43, 43, 48, Base.Vector(-21.5, -21.5, 33))
        edges = [motorBody.Edges[0], motorBody.Edges[2], motorBody.Edges[4], motorBody.Edges[6]]
        motorBody = motorBody.makeFillet(5, edges)

        # Motor mount holes
        for y in (-16, 16):
            for x in (-16, 16):
                motorBody = MakeHoleZ(motorBody, x, y, 4, 33, 38)

        # Motor pad and shaft
        motorPad = Part.makeCylinder(11, 2, Base.Vector(0, 0, 31), Base.Vector(0, 0, 1))
        motorShaft = Part.makeCylinder(2.5, 20, Base.Vector(0, 0, 11), Base.Vector(0, 0, 1))

        # Fuse all the parts
        motorShape = gearShape.fuse(motorBody)
        motorShape = motorShape.fuse(motorPad)
        motorShape = motorShape.fuse(motorShaft)

        # Placement
        if tVec != None:
            motorShape = motorShape.translated(tVec)
        if rVec != None:
            motorShape = motorShape.rotated(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1), 45)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = motorShape
        doc.recompute()

''' J1 motor holder
'''


''' J2 platform
'''
class J2_Platform:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        base = Part.makeBox(120, 100, 10, Base.Vector(-60, -50, 0))
        edges = [base.Edges[0], base.Edges[2], base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(20, edges)

        # Spindle mounting holes
        shape = MakeHoleZ(shape, 0, 15, 5, -1, 11)
        shape = MakeHoleZ(shape, 0, -15, 5, -1, 11)
        shape = MakeHoleZ(shape, 15, 0, 5, -1, 11)
        shape = MakeHoleZ(shape, -15, 0, 5, -1, 11)

        # Bearing holder
        shape = shape.fuse(MakeTube(53, 48, 6, 0, 0, -6))

        # Wall mounting holes
        for y in (-30, 0, 30):
            for x in (-50, 50):
                shape = MakeHoleZ(shape, x, y, 5, -1, 11)

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()


### Design layout.

# User needs to create a new document.
doc = App.activeDocument()

# Instantiate the base.
BasePlate().Instantiate(doc, "BasePlate")

J1_Bearing().Instantiate(doc, "J1_Bearing1", FreeCAD.Vector(0, 0, 5))
J1_Bearing().Instantiate(doc, "J1_Bearing2", FreeCAD.Vector(0, 0, 21))

# Instantiate J1 spindle
J1_Spindle().Instantiate(doc, "J1_Spindle", FreeCAD.Vector(0, 0, -17))

# Instantiate J1 motor.
J1_Motor().Instantiate(doc, "J1_Motor", FreeCAD.Vector(0, -105, -18))

# Instantiate J2 platform.
J2_Platform().Instantiate(doc, "J2_Platform", FreeCAD.Vector(0, 0, 43))
