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

''' Bearing.
'''
class Bearing:
    def __init__(self, outerD, innerD, height):
        self.outerD = outerD
        self.innerD = innerD
        self.height = height

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

''' Gear
'''
class Gear:
    def __init__(self, gearType, numTeeth, height, padD=0.0, padH=0.0, baseD=0.0, baseH=0.0,
            shaftD=0.0, shaftL=0.0):
        self.type = gearType
        self.numTeeth = numTeeth
        self.height = height
        self.padD = padD
        self.padH = padH
        self.baseD = baseD
        self.baseH = baseH
        self.shaftD = shaftD
        self.shaftL = shaftL

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # HTD5 gear
        gear = freecad.gears.commands.CreateTimingGear.create()
        gear.num_teeth = self.numTeeth
        gear.height = self.height
        gear.type = self.type
        doc.recompute()
        gear.Visibility = False
        shape = gear.Shape
        top = self.height

        # Gear pads
        if self.padD > 0.0 and self.padH > 0.0:
            pad1 = Part.makeCylinder(self.padD / 2.0, self.padH, FreeCAD.Vector(0, 0, -self.padH))
            pad2 = Part.makeCylinder(self.padD / 2.0, self.padH, FreeCAD.Vector(0, 0, self.height))
            shape = shape.fuse(pad1)
            shape = shape.fuse(pad2)
            top += self.padH

        # Gear base
        if self.baseD > 0.0 and self.baseH > 0.0:
            base = Part.makeCylinder(self.baseD / 2.0, self.baseH,
                    FreeCAD.Vector(0, 0, self.height + self.padH))
            shape = shape.fuse(base)
            top += self.baseH

        # Shaft hole
        if self.shaftD > 0.0 and self.shaftL > 0.0:
            shaft = Part.makeCylinder(self.shaftD / 2.0, self.shaftL,
                    FreeCAD.Vector(0, 0, top - self.shaftL))
            shape = shape.cut(shaft)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' NEMA motor
'''
class NEMA_Motor:
    ''' base, height, shaftD, shaftL
    '''
    def __init__(self, base, height, shaftD, shaftL):
        self.base = base
        self.height = height
        self.shaftD = shaftD
        self.shaftL = shaftL

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Motor body
        shape = Part.makeBox(self.base, self.base, self.height,
                FreeCAD.Vector(-self.base / 2.0, -self.base / 2.0, -self.height))
        edges = [shape.Edges[0], shape.Edges[2], shape.Edges[4], shape.Edges[6]]
        shape = shape.makeFillet(5, edges)

        # Motor pad and shaft
        motorPad = Part.makeCylinder(11, 2, FreeCAD.Vector(0, 0, 0))
        motorShaft = Part.makeCylinder(self.shaftD / 2.0, self.shaftL, FreeCAD.Vector(0, 0, 2))

        # Motor mount holes
        for y in (-16, 16):
            for x in (-16, 16):
                shape = MakeHoleZ(shape, x, y, 4, -5, 0)

        # Fuse all the parts
        shape = shape.fuse(motorPad)
        shape = shape.fuse(motorShaft)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' NEMA motor with gear.
'''
class NEMA_GearedMotor:
    def __init__(self, base, height, gearD, gearH, shaftD, shaftL):
        self.base = base
        self.height = height
        self.gearD = gearD
        self.gearH = gearH
        self.shaftD = shaftD
        self.shaftL = shaftL

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Body
        shape = Part.makeBox(self.base, self.base, self.height,
                FreeCAD.Vector(-self.base / 2.0, -self.base / 2.0, -self.height))
        edges = [shape.Edges[0], shape.Edges[2], shape.Edges[4], shape.Edges[6]]
        shape = shape.makeFillet(5, edges)

        # Motor gear
        shape = shape.fuse(Part.makeCylinder(self.gearD / 2.0, self.gearH, FreeCAD.Vector(0, 0, 0)))
        shape = shape.fuse(Part.makeCylinder(11, 2, FreeCAD.Vector(0, 0, self.gearH)))
        # Shaft
        shape = shape.fuse(Part.makeCylinder(self.shaftD / 2.0, self.shaftL,
                FreeCAD.Vector(0, 0, self.gearH + 2)))

        # Mounting holes
        for y in (-10, 10):
            for x in (-10, 10):
                shape = MakeHoleZ(shape, x, y, 3, self.gearH - 5, self.gearH)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

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
        self.height = 16

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        base = Part.makeBox(260, 80, self.height, FreeCAD.Vector(0, -40, 0))
        edges = [base.Edges[0], base.Edges[2], base.Edges[4], base.Edges[6]]
        shape = base.makeFillet(38, edges)

        # Extra bearing holder
        shape = shape.fuse(Part.makeCylinder(35, 10, FreeCAD.Vector(225, 0, 16)))
        # J3 bearing holes
        shape = shape.cut(Part.makeCylinder(23.5 + 0.2, 7, FreeCAD.Vector(225, 0, 19)))
        shape = shape.cut(Part.makeCylinder(23.5 + 0.2, 7, FreeCAD.Vector(225, 0, 0)))
        # Shaft hole
        shape = shape.cut(Part.makeCylinder(20, 30, FreeCAD.Vector(225, 0, 0)))

        # Mounting holes
        offset = 32
        shape = MakeHoleZ(shape, offset - 10, 0, 6.5, 0, self.height)
        shape = MakeHoleZ(shape, offset + 10, 0, 6.5, 0, self.height)
        shape = MakeHoleZ(shape, offset, -10, 6.5, 0, self.height)
        shape = MakeHoleZ(shape, offset, 10, 6.5, 0, self.height)

        # J3 motor hole
        offset = 74
        mh = Part.makeBox(50, 40, self.height, FreeCAD.Vector(offset, -20, 0))
        edges = [mh.Edges[0], mh.Edges[2], mh.Edges[4], mh.Edges[6]]
        mh = mh.makeFillet(19, edges)
        shape = shape.cut(mh)

        # J3 motor mounting holes
        shape = shape.cut(Part.makeCylinder(2, self.height, FreeCAD.Vector(offset + 15, 28, 0)))
        shape = shape.cut(Part.makeCylinder(2, self.height, FreeCAD.Vector(offset + 35, 28, 0)))
        shape = shape.cut(Part.makeCylinder(2, self.height, FreeCAD.Vector(offset + 15, -28, 0)))
        shape = shape.cut(Part.makeCylinder(2, self.height, FreeCAD.Vector(offset + 35, -28, 0)))

        # Cut lower for motor mount
        mh = Part.makeBox(70, 70, 5, FreeCAD.Vector(offset - 10, -35, self.height - 5))
        edges = [mh.Edges[0], mh.Edges[2], mh.Edges[4], mh.Edges[6]]
        mh = mh.makeFillet(2, edges)
        shape = shape.cut(mh)

        # Flip 180 degree
        shape = shape.rotate(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 180)

        # Placement
        if rVec != None:
            shape = shape.rotate(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 gear
'''
class J2_Gear:
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
        pad1 = Part.makeCylinder(26, 5, FreeCAD.Vector(0, 0, -5), FreeCAD.Vector(0, 0, 1))
        pad2 = Part.makeCylinder(26, 2, FreeCAD.Vector(0, 0, 12), FreeCAD.Vector(0, 0, 1))
        shape = gear.Shape.fuse(pad1)
        shape = shape.fuse(pad2)

        # Bearing shaft
        shape = shape.fuse(Part.makeCylinder(19, 4, FreeCAD.Vector(0, 0, 14)))
        shape = shape.fuse(Part.makeCylinder(17.7, 10, FreeCAD.Vector(0, 0, 18)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 6.5, -5, 28)
        shape = MakeHoleZ(shape, 10, 0, 6.5, -5, 28)
        shape = MakeHoleZ(shape, 0, -10, 6.5, -5, 28)
        shape = MakeHoleZ(shape, 0, 10, 6.5, -5, 28)

        # Placement
        if rVec != None:
            shape = shape.rotate(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J2 spindle
'''
class J2_Spindle:
    def __init__(self, height):
        self.height = height

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = Part.makeCylinder(19, self.height, FreeCAD.Vector(0, 0, 0))
        shape = shape.fuse(Part.makeCylinder(17.7, 10, FreeCAD.Vector(0, 0, self.height)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 6.5, 0, self.height + 10)
        shape = MakeHoleZ(shape, 10, 0, 6.5, 0, self.height + 10)
        shape = MakeHoleZ(shape, 0, -10, 6.5, 0, self.height + 10)
        shape = MakeHoleZ(shape, 0, 10, 6.5, 0, self.height + 10)

        # Placement
        if rVec != None:
            shape = shape.rotate(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        # Create the object
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
        shape = Part.makeBox(50, 120, 5, FreeCAD.Vector(-25, -85, 0))
        edges = [shape.Edges[0], shape.Edges[2], shape.Edges[4], shape.Edges[6]]
        shape = shape.makeFillet(5, edges)

        # Motor mounting holes
        for y in (-66, -46):
            for x in (-10, 10):
                shape = MakeHoleZ(shape, x, y, 3, 0, 5)

        # Motor hole
        shape = MakeHoleZ(shape, 0, -56, 22.5, 0, 5)

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

''' J3 motor mount.
'''
class J3_MotorMount:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Body
        shape = Part.makeBox(50, 68, 5, FreeCAD.Vector(-25, -34, 0))
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
        # shape = shape.fuse(Part.makeCylinder(17.5, 39, FreeCAD.Vector(0, 0, 17)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 4, -8, 17)
        shape = MakeHoleZ(shape, 10, 0, 4, -8, 17)
        shape = MakeHoleZ(shape, 0, -10, 4, -8, 17)
        shape = MakeHoleZ(shape, 0, 10, 4, -8, 17)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J3 spindle
'''
class J3_Spindle:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = Part.makeCylinder(20, 3, FreeCAD.Vector(0, 0, 0))
        shape = shape.fuse(Part.makeCylinder(17.5, 39, FreeCAD.Vector(0, 0, -26)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 4, -26, 17)
        shape = MakeHoleZ(shape, 10, 0, 4, -26, 17)
        shape = MakeHoleZ(shape, 0, -10, 4, -26, 17)
        shape = MakeHoleZ(shape, 0, 10, 4, -26, 17)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J4 platform
'''
class J4_Platform:
    def __init__(self):
        self.mountHoleD = 4.0

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        shape = Part.makeBox(140, 60, 10, FreeCAD.Vector(-40, -30, 0))

        # Bearing mount 1
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(0, 0, 3)))
        # Bearing mount 2
        shape = shape.fuse(Part.makeCylinder(28, 10, FreeCAD.Vector(0, 0, -10)))
        shape = shape.cut(Part.makeCylinder(23.5, 7, FreeCAD.Vector(0, 0, -10),
                FreeCAD.Vector(0, 1, 0)))

        # Bearing hole
        shape = shape.cut(Part.makeCylinder(20, 20, FreeCAD.Vector(0, 0, -10)))

        # Walls
        wall = Part.makeBox(80, 60, 8, FreeCAD.Vector(-40, 30, 8), FreeCAD.Vector(1, 0, 0))
        edges = [wall.Edges[4], wall.Edges[6]]
        wall = wall.makeFillet(19, edges)
        shape = shape.fuse(wall)

        wall = Part.makeBox(80, 60, 8, FreeCAD.Vector(32, 30, 8), FreeCAD.Vector(1, 0, 0))
        edges = [wall.Edges[4], wall.Edges[6]]
        wall = wall.makeFillet(19, edges)
        shape = shape.fuse(wall)

        # Mounting holes in wall 1
        mountHoleR = self.mountHoleD / 2
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(-40, 0, 54),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(-40, 0, 74),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(-40, -10, 64),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(-40, 10, 64),
                FreeCAD.Vector(1, 0, 0)))

        # Mounting holes in wall 2
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(32, 0, 54),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(32, 0, 74),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(32, -10, 64),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.cut(Part.makeCylinder(mountHoleR, 8, FreeCAD.Vector(32, 10, 64),
                FreeCAD.Vector(1, 0, 0)))

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J4 spindle
'''
class J4_Spindle:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        shape = Part.makeCylinder(20, 5, FreeCAD.Vector(0, 0, 0))
        shape = shape.fuse(Part.makeCylinder(17.5, 20, FreeCAD.Vector(0, 0, 5)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 4, 0, 30)
        shape = MakeHoleZ(shape, 10, 0, 4, 0, 30)
        shape = MakeHoleZ(shape, 0, -10, 4, 0, 30)
        shape = MakeHoleZ(shape, 0, 10, 4, 0, 30)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J4 gear
'''
class J4_Gear:
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
        shape = gear.Shape.fuse(pad1)
        shape = shape.fuse(pad2)

        shape = shape.fuse(Part.makeCylinder(20, 3, FreeCAD.Vector(0, 0, -5)))
        shape = shape.fuse(Part.makeCylinder(20, 3, FreeCAD.Vector(0, 0, 14)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 4, -5, 17)
        shape = MakeHoleZ(shape, 10, 0, 4, -5, 17)
        shape = MakeHoleZ(shape, 0, -10, 4, -5, 17)
        shape = MakeHoleZ(shape, 0, 10, 4, -5, 17)

        # Placement
        if rVec != None:
            shape = shape.rotated(rVec[0], rVec[1], rVec[2])
        if tVec != None:
            shape = shape.translated(tVec)

        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shape
        doc.recompute()

''' J4 arm
'''
class J4_Arm:
    def __init__(self):
        pass

    def Instantiate(self, doc, name, tVec=None, rVec=None):
        # Base
        shape = Part.makeBox(60, 60, 8, FreeCAD.Vector(-30, -30, 0))
        # Arms
        shape = shape.fuse(Part.makeBox(200, 60, 8, FreeCAD.Vector(-30, 30, 8),
                FreeCAD.Vector(1, 0, 0)))
        shape = shape.fuse(Part.makeBox(200, 60, 8, FreeCAD.Vector(22, 30, 8),
                FreeCAD.Vector(1, 0, 0)))

        # Mounting holes
        shape = MakeHoleZ(shape, -10, 0, 4, 0, 8)
        shape = MakeHoleZ(shape, 10, 0, 4, 0, 8)
        shape = MakeHoleZ(shape, 0, -10, 4, 0, 8)
        shape = MakeHoleZ(shape, 0, 10, 4, 0, 8)

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
Bearing(75, 45, 16).Instantiate(doc, "J1_Bearing1", FreeCAD.Vector(0, 0, 5))
Bearing(75, 45, 16).Instantiate(doc, "J1_Bearing2", FreeCAD.Vector(0, 0, 21))

# J1 spindle
J1_Spindle().Instantiate(doc, "J1_Spindle", FreeCAD.Vector(0, 0, -17))

# J1 motor.
NEMA_Motor(43, 48, 5, 20).Instantiate(doc, "J1_Motor", FreeCAD.Vector(0, -105, 15),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 180])
# gearType, numTeeth, height, padD=0.0, padH=0.0, baseD=0.0, baseH=0.0, shaftD=0.0, shaftL=0.0
Gear('htd5', 15, 16, 24, 2, 0, 0, 5, 20).Instantiate(doc, "J1_Gear", FreeCAD.Vector(0, -105, -3))

# J2 platform.
J2_Platform().Instantiate(doc, "J2_Platform", FreeCAD.Vector(0, 0, 43))

# J2 platform walls
J2_Wall1().Instantiate(doc, "J2_Wall1", FreeCAD.Vector(-40, 0, 53))
J2_Wall2().Instantiate(doc, "J2_Wall2", FreeCAD.Vector(30, 0, 53))

# J2 parts
J2_Arm().Instantiate(doc, "J2_Arm", FreeCAD.Vector(-7, 0, 61),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])
J2_Gear().Instantiate(doc, "J2_Gear", FreeCAD.Vector(-12, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])
J2_Spindle(21).Instantiate(doc, "J2_Spindle", FreeCAD.Vector(9, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

Bearing(47, 35, 7).Instantiate(doc, "J2_Bearing1", FreeCAD.Vector(-37, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
Bearing(47, 35, 7).Instantiate(doc, "J2_Bearing2", FreeCAD.Vector(37, 0, 93),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

NEMA_GearedMotor(43, 53, 36, 30, 8, 16).Instantiate(doc, "J2_Motor", FreeCAD.Vector(-75, -56, 144),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
# gearType, numTeeth, height, padD=0.0, padH=0.0, baseD=0.0, baseH=0.0, shaftD=0.0, shaftL=0.0
Gear('htd5', 15, 11, 28, 2, 18, 8, 8, 30).Instantiate(doc, "J2_MotorGear",
        FreeCAD.Vector(-13, -56, 144),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])
J2_MotorMount().Instantiate(doc, "J2_MotorMount", FreeCAD.Vector(-45, 0, 144),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

# J3 parts
NEMA_GearedMotor(43, 53, 36, 30, 8, 16).Instantiate(doc, "J3_Motor", FreeCAD.Vector(39, 0, 160),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])
# gearType, numTeeth, height, padD=0.0, padH=0.0, baseD=0.0, baseH=0.0, shaftD=0.0, shaftL=0.0
Gear('htd5', 15, 11, 28, 2, 18, 8, 8, 30).Instantiate(doc, "J3_MotorGear",
        FreeCAD.Vector(-23, 0, 160),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
J3_MotorMount().Instantiate(doc, "J3_MotorMount", FreeCAD.Vector(9, 0, 160),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

Bearing(47, 35, 7).Instantiate(doc, "J3_Bearing1", FreeCAD.Vector(-7, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
Bearing(47, 35, 7).Instantiate(doc, "J3_Bearing2", FreeCAD.Vector(19, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

J3_Gear().Instantiate(doc, "J3_Gear", FreeCAD.Vector(-24, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])
J3_Spindle().Instantiate(doc, "J3_Spindle", FreeCAD.Vector(19, 0, 286),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), 90])

# J4 parts
J4_Platform().Instantiate(doc, "J4_Platform", FreeCAD.Vector(0, 0, 350),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(1, 0, 0), 180])
J4_Spindle().Instantiate(doc, "J4_Spindle", FreeCAD.Vector(0, 0, 335))
J4_Gear().Instantiate(doc, "J4_Gear", FreeCAD.Vector(0, 0, 365))
NEMA_Motor(43, 21, 5, 18).Instantiate(doc, "J4_Motor", FreeCAD.Vector(70, 0, 340))
J4_Arm().Instantiate(doc, "J4_Arm", FreeCAD.Vector(0, 0, 382))

Bearing(47, 35, 7).Instantiate(doc, "J4_Bearing1", FreeCAD.Vector(0, 0, 340))
Bearing(47, 35, 7).Instantiate(doc, "J4_Bearing2", FreeCAD.Vector(0, 0, 353))

# J5 parts
NEMA_Motor(43, 21, 5, 18).Instantiate(doc, "J5_Motor", FreeCAD.Vector(30, 0, 560),
        [FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(0, 1, 0), -90])

# J6 parts
NEMA_Motor(43, 21, 5, 18).Instantiate(doc, "J6_Motor", FreeCAD.Vector(0, 0, 620))
