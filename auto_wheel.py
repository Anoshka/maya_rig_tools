"""auto wheel builder in progress"""

import sys
import os
import maya.utils
import maya.utils
import pymel.core as pm

#from . import all_control_options

def wheel_builder(wheel_ctrl = None, wheel_up = "Y", wheel_rot = "X"):

    if wheel_ctrl is None:
        wheel_ctrl = pm.ls(selection = True)[0]
    wheel_drv = pm.listRelatives(wheel_ctrl, p = True)[0]

    #establish axes
    wheel_up = "Y"
    wheel_rot = "X"
    wheel_front = ""

    #get front axis
    if wheel_up == wheel_rot:
        pm.error("wheel rotate axis and up axis cannot be the same")

    allAxes = ["X", "Y", "Z"]
    for i in allAxes:
        if i == wheel_up or i == wheel_rot:
            pass
        else:
            wheel_front = i

    #create nodes
    decMat = pm.shadingNode("decomposeMatrix", asUtility = True)
    cond = pm.shadingNode("condition", asUtility = True)
    doubLin_01 = pm.shadingNode("addDoubleLinear", asUtility = True)
    doubLin_02 = pm.shadingNode("addDoubleLinear", asUtility = True)
    unitConv = pm.shadingNode("unitConversion", asUtility = True)
    mulDiv = pm.shadingNode("multiplyDivide", asUtility = True)
    plusMinus = pm.shadingNode("plusMinusAverage", asUtility = True)

    name = wheel_ctrl.split("_WHEEL")
    new_name = name[0] + "_WHEEL_BASE" + name[1]
    new_name = new_name.split("CNT_")[1]

    #create control setup
    ctrl = pm.group(em = True, n = "CNT_" + new_name)
    drv = pm.group(em = True, n = "DRV_" + new_name)
    xfrm = pm.group(em = True, n = "XFORM_" + new_name)
    par = pm.group(em = True, n = "control_" + new_name)
    pm.parent(ctrl, drv)
    pm.parent(drv, xfrm)
    pm.parent(xfrm, par)
    #place base
    pm.matchTransform(xfrm, wheel_ctrl)
    pm.setAttr(xfrm + ".translate" + wheel_up, 0)

    #create attrs
    pm.addAttr(ctrl, ln = "speed", at = "double", dv = 0, keyable = True)
    pm.addAttr(ctrl, ln = "autoRoll", at = "enum", en = "OFF:ON:", keyable = True)
    pm.setAttr(ctrl + ".speed", 1)
    pm.setAttr(ctrl + ".autoRoll", 1)

    #connect attrs
    pm.connectAttr(ctrl + ".worldInverseMatrix[0]", decMat + ".inputMatrix", force = True)
    pm.connectAttr(ctrl + ".speed", cond + ".colorIfFalseR", force = True)
    pm.connectAttr(ctrl + ".autoRoll", cond + ".firstTerm", force = True)
    pm.connectAttr(decMat + ".outputTranslate.outputTranslate" + wheel_front, doubLin_01 + ".input1", force = True)
    pm.connectAttr(doubLin_01 + ".output", mulDiv + ".input1X", force = True)
    pm.connectAttr(cond + ".outColorR", mulDiv + ".input2X", force = True)
    pm.connectAttr(mulDiv + ".outputX", plusMinus + ".input1D[0]", force = True)
    pm.disconnectAttr(mulDiv + ".outputX", plusMinus + ".input1D[0]")
    pm.connectAttr(mulDiv + ".outputX", plusMinus + ".input1D[1]", force = True)
    pm.setAttr(plusMinus + ".operation", 2)
    pm.connectAttr(ctrl + ".translate" + wheel_front, unitConv + ".input", force = True)
    pm.setAttr(unitConv + ".conversionFactor", -2, force = True)
    pm.connectAttr(unitConv + ".output", doubLin_02 + ".input1", force = True)
    pm.connectAttr(plusMinus + ".output1D", doubLin_02 + ".input2", force = True)
    pm.connectAttr(doubLin_02 + ".output", wheel_drv + ".rotate" + wheel_rot, force = True)
    pm.connectAttr(ctrl + ".translate" + wheel_up, wheel_drv + ".translate" + wheel_up, force = True)

    square_curve = pm.curve(d = 1, p = [(-60, 0, -60), (-60, 0, 60), (60, 0, 60), (60, 0, -60), (-60, 0, -60)], 
                            k = (0, 1, 2, 3, 4)) 

    pm.select(square_curve, r = True)
    pm.select(ctrl, add = True)

    #all_control_options.swap_shape()

    pm.select(square_curve)
    pm.delete()
