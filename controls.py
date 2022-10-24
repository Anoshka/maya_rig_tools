"""in progress"""

import pymel.core as pm
import maya.OpenMayaUI as omui
import pymel.core as pm
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance
from . import dict_lib

"""All the options to modify control shape and colour
Will add a size option"""

def swap_shape():
    """takes first selected shape and swaps the other shapes to match it"""

    #takes selection of controls for swap
    all_controls = pm.ls(selection = True)

    #establishes original control shape
    orig_ctrl = all_controls[0]
    all_controls.remove(orig_ctrl)

    new_control = pm.duplicate(orig_ctrl, rr = True)[0]
    new_shape = new_control.getShape()
    print("The shape node is {} and it's type {}".format(new_shape.name(), type(new_shape)))

    #swaps individual shapes
    for ctrl in all_controls:

        current_shape = ctrl.getShape()
        pm.parent(new_shape, ctrl, s=True, r=True)

        pm.delete(current_shape)
    pm.delete(new_control)



def pick_control(control_selected):
    """changes control shape to chosen shape"""

    #takes selection of controls to be changed
    cur_curve = pm.ls(selection=True)

    #checks if selection is appropriate
    for ctrl in cur_curve:
        if pm.nodeType(ctrl) != "transform":
            pm.error("please select a transform node")
            break


    #create swappable curve - this is a test - works with ring and plus

    #new_curve = pm.curve(per=dict_lib.controls_dict[control_selected]['per'],
                         p=dict_lib.controls_dict[control_selected]['points'],
                         k=dict_lib.controls_dict[control_selected]['knots'],
                         d=dict_lib.controls_dict[control_selected]['degree'])
    #new_curve_node = pm.PyNode(new_curve)
    #creates selection to send to swap curve function
    #pm.select(new_curve, replace = True)
    #pm.select(cur_curve, add = True)
    #swap_shape()
    #pm.delete(new_curve_node)



def set_colour():
    """provides selection window for colour"""

    #creates qolor window
    qcolor = QtWidgets.QColorDialog().getColor()

    #checks colour an sets up rgb for maya
    if qcolor.isValid():
        new = qcolor.getRgb()
        colors = [new[0] * 0.001, new[1] * 0.001, new[2] * 0.001]


    return colors

def pick_colour():
    """ sets the control colour based on selection"""

    #takes in control selection for colour change
    ctrl = pm.ls(selection=True)
    colors_list = set_colour()

    #assigns rgb values
    r_value = colors_list[0]
    g_value = colors_list[1]
    b_value = colors_list[2]

    #updates each control
    for each_ctrl in ctrl:
        pm.setAttr(each_ctrl + ".overrideEnabled", 1)
        pm.setAttr(each_ctrl + ".overrideRGBColors", 1)
        pm.setAttr(each_ctrl + ".overrideColorRGB", r_value, g_value, b_value)
