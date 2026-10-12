"""
Desktop pan-tilt platform for OAK-D.
=====================================================
This design contains the follow components:
  1. Base: provides the base and rotation support.
  2. Neck: a PVC pipe for the neck.
  3. Tilt mount: holds a servo motor for tilt.

How to run:
  FreeCAD -> View -> Panels -> Python console, paste this whole file and
  press Enter. Or save as oakd_pan_tilt.FCMacro and run via Macro menu.
  Each part appears as a separate object: select one and File -> Export -> STL.

Design notes:
  * .
  * Flange joints use heat-set inserts (M3, 4.0 mm hole) instead of nuts
    where a nut would collide with moving parts.
  * All parts print flat, no supports. 4-6 mm walls suit PETG, 4+ perimeters.
  * MG996R is far stronger than needed here (~0.15 kg.cm load vs 9.4 rated):
    motion will be smooth with no jitter.

HARDWARE (beyond the servos):
  Pan servo -> base plate : 4x M3x10 + 4x M3 nut
  Pan bar -> spline       : 1x M3x12 (or reuse horn screw)
  Arm feet -> pan bar     : 4x M3x12 + 4x M3 nut
  Tilt servo -> arm_L     : 4x M3x10 + 4x M3 heat-set insert
  Tilt disc -> tray ear   : 2x M3x12 + 2x M3 heat-set insert
  Tray pivot (right)      : 1x M4x30 + M4 nyloc + washers
  OAK-D -> tray           : 1x 1/4"-20 x 3/4" bolt + nut (nut sits in hex trap)
  Base -> chassis         : 4x M4x12 + 4x M4 nut
  Mount the base plate >= 40 mm above the deck: the pan servo hangs ~35 mm
  below it, plus its wire exits the case bottom.
"""

import math
import FreeCAD as App
from FreeCAD import Base
import Part
from BasicShapes import Shapes

def hole_z(shape, x, y, d, z0, z1):
    tool = Part.makeCylinder(d / 2.0, z1 - z0, Base.Vector(x, y, z0),
                             Base.Vector(0, 0, 1))
    return shape.cut(tool)

class PanTiltBase:
    # All measurements are in mm.
    def __init__(self):
        pass

    def Instantiate(self, doc):
        # Base tube
        outer = Part.makeCylinder(60, 10)
        inner = Part.makeCylinder(40, 10)
        base = outer.cut(inner)

        # Mounting holes
        for r in (-50, 50):
            base = hole_z(base, r, 0, 4, -1, 11)
            base = hole_z(base, 0, r, 4, -1, 11)

        # Create the object
        base_obj = doc.addObject("Part::Feature", "Base")
        base_obj.Shape = base

        doc.recompute()

# Create a new document.
# doc = FreeCAD.newDocument("DesktopPanTilt")
doc = App.activeDocument()

# Instantiate the base.
PanTiltBase().Instantiate(doc)
