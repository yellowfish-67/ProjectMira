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
    tool = Part.makeCylinder(d / 2.0, z1 - z0, FreeCAD.Vector(x, y, z0),
                             FreeCAD.Vector(0, 0, 1))
    return shape.cut(tool)

''' Make a tube.
'''
def MakeTube(outerD, innerD, height, x, y, z0):
    outer = Part.makeCylinder(outerD / 2.0, height, FreeCAD.Vector(x, y, z0), FreeCAD.Vector(0, 0, 1))
    inner = Part.makeCylinder(innerD / 2.0, height, FreeCAD.Vector(x, y, z0), FreeCAD.Vector(0, 0, 1))
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
        mount = Part.makeBox(38, 60, self.height + 2, FreeCAD.Vector(-19, -135, -1))
        edges = [mount.Edges[0], mount.Edges[2], mount.Edges[4], mount.Edges[6]]
        mount = mount.makeFillet(18, edges)
        return mount

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base plate
        basePlate = Part.makeBox(160, 200, self.height, FreeCAD.Vector(-80, -150, 0))

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
        pad1 = Part.makeCylinder(48, 2, FreeCAD.Vector(0, 0, -2), FreeCAD.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(48, 2, FreeCAD.Vector(0, 0, 12), FreeCAD.Vector(0, 0, 1))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        # Spindle body
        param1 = [27, 8, 14]
        shape = gearShape.fuse(Part.makeCylinder(param1[0], param1[1], FreeCAD.Vector(0, 0, param1[2]),
                FreeCAD.Vector(0, 0, 1)))
        param2 = [22.7, 38, param1[2] + param1[1]]
        shape = shape.fuse(Part.makeCylinder(param2[0], param2[1], FreeCAD.Vector(0, 0, param2[2]),
                FreeCAD.Vector(0, 0, 1)))

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
        pad1 = Part.makeCylinder(12, 2, FreeCAD.Vector(0, 0, -2), FreeCAD.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(12, 2, FreeCAD.Vector(0, 0, 15), FreeCAD.Vector(0, 0, 1))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        # Motor body
        motorBody = Part.makeBox(43, 43, 48, FreeCAD.Vector(-21.5, -21.5, 33))
        edges = [motorBody.Edges[0], motorBody.Edges[2], motorBody.Edges[4], motorBody.Edges[6]]
        motorBody = motorBody.makeFillet(5, edges)

        # Motor mount holes
        for y in (-16, 16):
            for x in (-16, 16):
                motorBody = MakeHoleZ(motorBody, x, y, 4, 33, 38)

        # Motor pad and shaft
        motorPad = Part.makeCylinder(11, 2, FreeCAD.Vector(0, 0, 31), FreeCAD.Vector(0, 0, 1))
        motorShaft = Part.makeCylinder(2.5, 20, FreeCAD.Vector(0, 0, 11), FreeCAD.Vector(0, 0, 1))

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
        base = Part.makeBox(120, 100, 10, FreeCAD.Vector(-60, -50, 0))
        edges = [base.Edges[0], base.Edges[2], base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(20, edges)

        # Spindle mounting holes
        shape = MakeHoleZ(shape, 0, 15, 5, -1, 11)
        shape = MakeHoleZ(shape, 0, -15, 5, -1, 11)
        shape = MakeHoleZ(shape, 15, 0, 5, -1, 11)
        shape = MakeHoleZ(shape, -15, 0, 5, -1, 11)

        # Bearing holder
        shape = shape.fuse(MakeTube(55, 45.5, 6, 0, 0, -6))

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

''' J2 wall 1
'''
class J2_Wall1:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        base = Part.makeBox(125, 80, 10, FreeCAD.Vector(0, 40, 0), FreeCAD.Vector(1, 0, 0))
        edges = [base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(20, edges)

        # Mounting edge
        me = Part.makeBox(20, 80, 10, FreeCAD.Vector(-20, -40, 0))
        edges = [me.Edges[0], me.Edges[2]]
        me = me.makeFillet(10, edges)
        shape = shape.fuse(me)

        # Mounting holes
        for y in (-30, 0, 30):
            shape = MakeHoleZ(shape, -10, y, 5, -1, 11)

        # Bearing hole
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(3, 0, 40),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(21, 12, FreeCAD.Vector(-1, 0, 40),
                FreeCAD.Vector(1, 0, 0)))

        # Motor hole
        mh = Part.makeBox(50, 40, 10, FreeCAD.Vector(0, 20, 66), FreeCAD.Vector(1, 0, 0))
        edges = [mh.Edges[0], mh.Edges[2], mh.Edges[4], mh.Edges[6]]
        mh = mh.makeFillet(19, edges)
        shape = shape.cut(mh)

        # Motor mount holes
        shape = shape.cut(Part.makeCylinder(2, 10, FreeCAD.Vector(0, 28, 80),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(2, 10, FreeCAD.Vector(0, 28, 102),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(2, 10, FreeCAD.Vector(0, -28, 80),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(2, 10, FreeCAD.Vector(0, -28, 102),
                FreeCAD.Vector(1, 0, 0)))

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 wall 2
'''
class J2_Wall2:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        base = Part.makeBox(70, 80, 10, FreeCAD.Vector(0, 40, 0), FreeCAD.Vector(1, 0, 0))
        edges = [base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(20, edges)

        # Mounting edge
        me = Part.makeBox(20, 80, 10, FreeCAD.Vector(10, -40, 0))
        edges = [me.Edges[4], me.Edges[6]]
        me = me.makeFillet(10, edges)
        shape = shape.fuse(me)

        # Mounting holes
        for y in (-30, 0, 30):
            shape = MakeHoleZ(shape, 20, y, 5, -1, 11)

        # Bearing hole
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(0, 0, 40),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(21, 12, FreeCAD.Vector(-1, 0, 40),
                FreeCAD.Vector(1, 0, 0)))

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 arm
'''
class J2_Arm:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        base = Part.makeBox(260, 80, 16, FreeCAD.Vector(3, 40, 0), FreeCAD.Vector(1, 0, 0))
        edges = [base.Edges[0], base.Edges[2], base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(38, edges)

        # Gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = 30
        gear.height = 12
        gear.type = "htd5"
        doc.recompute()
        gear.Visibility = False

        # Gear pads
        pad1 = Part.makeCylinder(26, 5, FreeCAD.Vector(0, 0, -5), FreeCAD.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(26, 2, FreeCAD.Vector(0, 0, 12), FreeCAD.Vector(0, 0, 1))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        gearShape = gearShape.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90)
        shape = shape.fuse(gearShape.translated(FreeCAD.Vector(-2, 0, 32)))

        # J3 bearing hole
        shape = shape.fuse(Part.makeCylinder(35, 10, FreeCAD.Vector(19, 0, 225),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(22, 0, 225),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(3, 0, 225),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(17.5, 30, FreeCAD.Vector(3, 0, 225),
                FreeCAD.Vector(1, 0, 0)))

        # Placement
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 arm shaft
'''
class J2_ArmShaft:
    def __init__(self, height):
        self.height = height

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = Part.makeCylinder(19, self.height, FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 0, 1))
        shape = shape.fuse(Part.makeCylinder(17.7, 10, FreeCAD.Vector(0, 0, -10),
                FreeCAD.Vector(0, 0, 1)))

        # Placement
        if rVec != None:
            shape = shape.rotate(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()


''' J2 bearing.
'''
class J2_Bearing:
    def __init__(self):
        self.innerD = 35
        self.outerD = 47
        self.height = 7

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = MakeTube(self.outerD, self.innerD, self.height, 0, 0, 0)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 motor.
'''
class J2_Motor:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Body
        shape = Part.makeBox(42, 42, 53, FreeCAD.Vector(-21, -21, 0))
        edges = [shape.Edges[0], shape.Edges[2], shape.Edges[4], shape.Edges[6]]
        shape = shape.makeFillet(5, edges)

        # Motor gear
        shape = shape.fuse(Part.makeCylinder(18, 30, FreeCAD.Vector(0, 0, 53)))
        shape = shape.fuse(Part.makeCylinder(11, 2, FreeCAD.Vector(0, 0, 83)))
        # Shaft
        shape = shape.fuse(Part.makeCylinder(4, 16, FreeCAD.Vector(0, 0, 85)))

        # Mounting holes
        for y in (-10, 10):
            for x in (-10, 10):
                shape = MakeHoleZ(shape, x, y, 3, 78, 83)

        # Load gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = 15
        gear.height = 11
        gear.type = "htd5"
        doc.recompute()
        gear.Visibility = False

        pad1 = Part.makeCylinder(14, 2, FreeCAD.Vector(0, 0, -2))
        pad2 = Part.makeCylinder(14, 2, FreeCAD.Vector(0, 0, 11))
        base = Part.makeCylinder(9, 8, FreeCAD.Vector(0, 0, -10))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)
        gearShape = gearShape.fuse(base)

        shape = shape.fuse(gearShape.translated(FreeCAD.Vector(0, 0, 104)))

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()


''' J2 motor mount.
'''
class J2_MotorMount:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Body
        shape = Part.makeBox(50, 70, 5, FreeCAD.Vector(-25, -35, 0))
        edges = [shape.Edges[0], shape.Edges[2], shape.Edges[4], shape.Edges[6]]
        shape = shape.makeFillet(5, edges)

        # Motor mounting holes
        for y in (-10, 10):
            for x in (-10, 10):
                shape = MakeHoleZ(shape, x, y, 3, 0, 5)

        # Motor hole
        shape = MakeHoleZ(shape, 0, 0, 22.5, 0, 5)

        # Mounting holes
        mh = Part.makeBox(42, 4, 5, FreeCAD.Vector(-21, -30, 0))
        edges = [mh.Edges[0], mh.Edges[2], mh.Edges[4], mh.Edges[6]]
        mh = mh.makeFillet(1.8, edges)
        shape = shape.cut(mh)

        mh = Part.makeBox(42, 4, 5, FreeCAD.Vector(-21, 26, 0))
        edges = [mh.Edges[0], mh.Edges[2], mh.Edges[4], mh.Edges[6]]
        mh = mh.makeFillet(1.8, edges)
        shape = shape.cut(mh)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J3 gear
'''
class J3_Gear:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = 30
        gear.height = 12
        gear.type = "htd5"
        doc.recompute()
        gear.Visibility = False

        # Gear pads
        pad1 = Part.makeCylinder(26, 2, FreeCAD.Vector(0, 0, -2))
        pad2 = Part.makeCylinder(26, 2, FreeCAD.Vector(0, 0, 12))
        gearShape = gear.Shape.fuse(pad1)
        gearShape = gearShape.fuse(pad2)

        # Gear shafts
        shape = Part.makeCylinder(17.5, 6, FreeCAD.Vector(0, 0, -8))
        shape = shape.fuse(gearShape)
        shape = shape.fuse(Part.makeCylinder(20, 3, FreeCAD.Vector(0, 0, 14)))
        shape = shape.fuse(Part.makeCylinder(17.5, 39, FreeCAD.Vector(0, 0, 17)))

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J3 platform
'''
class J3_Platform:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        shape = Part.makeBox(80, 60, 8, FreeCAD.Vector(-40, -30, 0))

        # Walls
        wall = Part.makeBox(80, 60, 8, FreeCAD.Vector(-40, 30, 8), FreeCAD.Vector(1, 0, 0))
        edges = [wall.Edges[4], wall.Edges[6]]
        wall = wall.makeFillet(19, edges)
        shape = shape.fuse(wall)

        wall = Part.makeBox(80, 60, 8, FreeCAD.Vector(32, 30, 8), FreeCAD.Vector(1, 0, 0))
        edges = [wall.Edges[4], wall.Edges[6]]
        wall = wall.makeFillet(19, edges)
        shape = shape.fuse(wall)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()


### Design layout.

# User needs to create a new document.
doc = App.activeDocument()

# The arm base.
BasePlate().Instantiate(doc, "BasePlate")

# J1 bearings
J1_Bearing().Instantiate(doc, "J1_Bearing1", FreeCAD.Vector(0, 0, 5))
J1_Bearing().Instantiate(doc, "J1_Bearing2", FreeCAD.Vector(0, 0, 21))

# J1 spindle
J1_Spindle().Instantiate(doc, "J1_Spindle", FreeCAD.Vector(0, 0, -17))

# J1 motor.
J1_Motor().Instantiate(doc, "J1_Motor", FreeCAD.Vector(0, -105, -18))

# J2 platform.
J2_Platform().Instantiate(doc, "J2_Platform", FreeCAD.Vector(0, 0, 43))

# J2 platform walls
J2_Wall1().Instantiate(doc, "J2_Wall1", FreeCAD.Vector(-40, 0, 53))
J2_Wall2().Instantiate(doc, "J2_Wall2", FreeCAD.Vector(30, 0, 53))

# J2 arm
J2_Arm().Instantiate(doc, "J2_Arm", FreeCAD.Vector(-10, 0, 61))
J2_ArmShaft(4).Instantiate(doc, "J2_ArmShaft1", FreeCAD.Vector(-30, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
J2_ArmShaft(24).Instantiate(doc, "J2_ArmShaft2", FreeCAD.Vector(30, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

J2_Bearing().Instantiate(doc, "J2_Bearing1", FreeCAD.Vector(-37, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
J2_Bearing().Instantiate(doc, "J2_Bearing2", FreeCAD.Vector(37, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

J2_Motor().Instantiate(doc, "J2_Motor", FreeCAD.Vector(-128, 0, 144),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

J2_MotorMount().Instantiate(doc, "J2_MotorMount", FreeCAD.Vector(-45, 0, 144),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

# J3 arm
J2_Motor().Instantiate(doc, "J3_Motor", FreeCAD.Vector(92, 0, 180),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

J2_Bearing().Instantiate(doc, "J3_Bearing1", FreeCAD.Vector(-7, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
J2_Bearing().Instantiate(doc, "J3_Bearing2", FreeCAD.Vector(19, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

J3_Gear().Instantiate(doc, "J3_Gear", FreeCAD.Vector(-24, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

J3_Platform().Instantiate(doc, "J3_Platform", FreeCAD.Vector(0, 0, 350),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 180])
