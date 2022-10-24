from pickletools import long4
from pymel.core.datatypes import Vector
import maya.OpenMayaUI as omui
import pymel.core as pm
import sys
# Trust all the following to ship with Maya.
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import gc
import sys

# From related modules:

from . import skinning
from . import connections
from . import controls
from . import deform
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)



class MainDialog(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    def __init__(self, parent=maya_main_window()):
        super(MainDialog, self).__init__(parent)
        self.setWindowTitle("Shaper Rigs Suite Utilities v{}".format(globals.srsu_version))
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        # Remove help button flag on windows wm.
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

        return


    def create_widgets(self):
        # Prep tabs:
        self.tools_tab = QtWidgets.QTabWidget(self)
        self.tools_tab.setGeometry(QtCore.QRect(20, 20, 371, 600))
        self.tools_tab.setAutoFillBackground(False)

        # Skinning Tab:
        self.skin_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.skin_tab, "skinning")

        self.copy_sw_btn = QtWidgets.QPushButton(self.skin_tab)
        self.copy_sw_btn.setText("Copy SkinWeights")

        self.select_bj_btn = QtWidgets.QPushButton(self.skin_tab)
        self.select_bj_btn.setText("Select Bound Joints")

        self.save_skin_btn = QtWidgets.QPushButton(self.skin_tab)
        self.save_skin_btn.setText("Save Skin to JSON")

        # Rip Skin Tab Groupbox
        self.rip_box = QtWidgets.QGroupBox("Rip Skin Tool", self.skin_tab)
        self.rip_box.move(10, 175)
        self.rip_box.resize(360, 240)
        

        self.h_source_txtbox = QtWidgets.QLabel(self.skin_tab)
        self.h_source_txtbox.setText("Input Source Mesh")
        self.get_source_mesh = QtWidgets.QLineEdit(self.skin_tab)
        self.h_target_txtbox = QtWidgets.QLabel(self.skin_tab)
        self.h_target_txtbox.setText("Input Target Mesh")
        self.get_target_mesh = QtWidgets.QLineEdit(self.skin_tab)


        self.match_by_options_label = QtWidgets.QLabel(self.skin_tab)
        self.match_by_options_label.setText("Match by")
        self.match_by_options = QtWidgets.QComboBox(self.skin_tab)

        all_options = ["Closest Point", "UVs"]
        for option in all_options:
            self.match_by_options.addItem(option)
        
        self.influence_options_label = QtWidgets.QLabel(self.skin_tab)
        self.influence_options_label.setText("Influence Option")
        self.influence_options = QtWidgets.QComboBox(self.skin_tab)

        all_options = ["Closest Joint", "Namespace"]
        for option in all_options:
            self.influence_options.addItem(option)


        self.rip_skin_btn = QtWidgets.QPushButton(self.skin_tab)
        self.rip_skin_btn.setText("Rip Skin")


        self.vbox = QtWidgets.QVBoxLayout()
        self.rip_box.setLayout(self.vbox)
        self.vbox.addWidget(self.h_source_txtbox)
        self.vbox.addWidget(self.get_source_mesh)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.h_target_txtbox)
        self.vbox.addWidget(self.get_target_mesh)
        self.rip_box.layout().addLayout(self.vbox)     
        self.vbox.addWidget(self.match_by_options_label)
        self.vbox.addWidget(self.match_by_options)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.influence_options_label)
        self.vbox.addWidget(self.influence_options)
        self.rip_box.layout().addLayout(self.vbox)
        self.vbox.addWidget(self.rip_skin_btn)

        # Connections tab
        self.connections_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.connections_tab, "Connections")
        self.h_connect_xforms_btn = QtWidgets.QPushButton(self.connections_tab)
        self.h_connect_xforms_btn.setText("Connect Xform")

        #     add driver attribute prompt  and textbox
        self.h_input_driver_txtbox = QtWidgets.QLabel(self.connections_tab)
        self.h_input_driver_txtbox.setText("Input Driver Attribute")
        self.get_driver = QtWidgets.QLineEdit(self.connections_tab)
        self.get_driver.move(150, 36)
        self.get_driver.resize(200, 20)

        #     add driven attribute prompt and textbox
        self.h_input_driven_txtbox = QtWidgets.QLabel(self.connections_tab)
        self.h_input_driven_txtbox.setText("Input Driven Attributes")
        self.get_driven = QtWidgets.QLineEdit(self.connections_tab)
        self.get_driven.move(150, 57)
        self.get_driven.resize(210, 20)

        #    attribute connector button
        self.h_batch_connector_btn = QtWidgets.QPushButton(self.connections_tab)
        self.h_batch_connector_btn.setText("Connect Attributes")

        # Controls tab
        self.controls_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.controls_tab, "Controls")
        self.h_swap_control_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_swap_control_btn.setText("Swap Shape")
        # self.h_swap_control_btn.resize(370, 20)

        self.shape_options = QtWidgets.QComboBox(self.controls_tab)
        self.shape_options.move(10, 81)
        self.shape_options.resize(200, 30)
        self.shape_options.setStyleSheet("border: 3px solid blue; border-right-width: 0px;")
        all_options = dict_lib.controls()
        for key in all_options:
            self.shape_options.addItem(key)

        self.h_control_selection_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_control_selection_btn.setText("Set Control Shape")
        self.control_selection = self.shape_options.currentText()
        self.h_control_selection_btn.move(200, 81)
        self.h_control_selection_btn.resize(150, 30)
        self.h_control_selection_btn.setStyleSheet("border: 3px solid blue;border-left-width: 0px;")

        # add colour options
        self.h_color_options_btn = QtWidgets.QPushButton(self.controls_tab)
        self.h_color_options_btn.setText("Colour Options")

        # Deform Tab tab
        self.deform_tab = QtWidgets.QWidget()
        self.tools_tab.addTab(self.deform_tab, "Deform")

        self.new_geo_txtbox = QtWidgets.QLabel(self.deform_tab)
        self.new_geo_txtbox.setText("Input New Geo")
        self.new_geo_txtbox.move(10, 21)
        self.get_new_geo = QtWidgets.QLineEdit(self.deform_tab)
        self.get_new_geo.move(150, 21)
        self.get_new_geo.resize(210, 20)

        self.new_geo_txtbox = QtWidgets.QLabel(self.deform_tab)
        self.new_geo_txtbox.setText("Input Old Geo")
        self.new_geo_txtbox.move(10, 42)
        self.get_old_geo = QtWidgets.QLineEdit(self.deform_tab)
        self.get_old_geo.move(150, 42)
        self.get_old_geo.resize(210, 20)

        self.tweak_node = QtWidgets.QLabel(self.deform_tab)
        self.tweak_node.setText("Input Tweak Node")
        self.tweak_node.move(10, 63)
        self.get_tweak_node = QtWidgets.QLineEdit(self.deform_tab)
        self.get_tweak_node.move(150, 63)
        self.get_tweak_node.resize(210, 20)

        self.h_deform_btn = QtWidgets.QPushButton(self.deform_tab)
        self.h_deform_btn.setText("Bake Deltas")
        self.h_deform_btn.move(10, 84)
        self.h_deform_btn.resize(360, 20)


        return


    def create_layouts(self):
       
        # Create the skinning tab layout:
        skin_tab_layout = QtWidgets.QFormLayout(self.skin_tab)
        skin_tab_layout.addRow(self.save_skin_btn)
        skin_tab_layout.addRow(self.select_bj_btn)

        # Create Connections Tab layout:
        connections_tab_layout = QtWidgets.QFormLayout(self.connections_tab)
        connections_tab_layout.addRow(self.h_connect_xforms_btn)
        connections_tab_layout.addRow(self.h_input_driver_txtbox)
        connections_tab_layout.addRow(self.h_input_driven_txtbox)
        connections_tab_layout.addRow(self.h_batch_connector_btn)

        # Create Controls Tab layout:
        controls_tab_layout = QtWidgets.QFormLayout(self.controls_tab)
        controls_tab_layout.addRow(self.h_color_options_btn)
        controls_tab_layout.addRow(self.h_swap_control_btn)

        # Create Transforms Tab layout:
        transforms_tab_layout = QtWidgets.QFormLayout(self.transforms_tab)

        return


    def create_connections(self):
        self.jfc_btn.clicked.connect(self.ui_joint_from_component)
        self.copy_sw_btn.clicked.connect(self.ui_copy_skinweights)
        self.select_bj_btn.clicked.connect(self.ui_find_related_joints)
        self.h_connect_xforms_btn.clicked.connect(self.ui_connect_xform)
        self.get_driver.text()
        self.get_driven.text()
        self.h_batch_connector_btn.clicked.connect(self.ui_batch_connect)
        self.h_swap_control_btn.clicked.connect(self.ui_swap_controls)
        self.shape_options.currentText()
        self.h_control_selection_btn.clicked.connect(self.ui_control_options)
        self.h_color_options_btn.clicked.connect(self.ui_colour_options)
        self.rip_skin_btn.clicked.connect(self.ui_rip_skin_btn)
        self.h_deform_btn.clicked.connect(self.ui_bake_deltas)

        return


    # UI commands:

    def ui_joint_from_component(self):
        print ("UI call for skeleton.joint_from_components()")
        skeleton.joint_from_components()

        return


    def ui_copy_skinweights(self):
        print ("UI call for skinning.copy_skinweights()")
        skinning.copy_skinweights()

        return


    def ui_find_related_joints(self):
        print ("UI call for skinning.select_bound_joints()")
        skinning.select_bound_joints()

        return


    def ui_connect_xform(self):
        print ("UI call for connections.connect_xforms()")
        connections.connect_xforms()

        return


    def ui_batch_connect(self):
        print ("UI call for connections.batch_connect()")
        # uses input attributes for parameters
        connections.batch_connect(str(self.get_driver.text()), str(self.get_driven.text()))

        return


    def ui_swap_controls(self):
        print ("UI call for swapping control shape")
        controls.swap_shape()

        return


    def ui_control_options(self):
        print ("UI call for picking control")
        controls.pick_control(self.shape_options.currentText())

        return


    def ui_colour_options(self):
        print ("UI call for picking colour")
        controls.pick_colour()

        return


    def ui_bake_deltas(self):
        if not self.get_new_geo.text():
            geo = pm.ls(selection = True)
            new_geo = geo[0]
            old_geo = geo[1]
        else:
            new_geo = self.get_new_geo.text()
            old_geo = self.get_old_geo.text()
            
        deform.deltas_to_tweak(new_geo, old_geo, self.get_tweak_node.text())


    def ui_rip_skin_attrs(self):
        if not self.get_source_mesh.text():
            source_mesh = pm.ls(selection = True)[0]
        else:
            source_mesh = self.get_source_mesh.text()
        
        if not self.get_target_mesh.text():
            target_mesh = pm.ls(selection = True)[1]
        else:
            target_mesh = self.get_target_mesh.text()
        
        return(source_mesh, target_mesh)


    def ui_rip_skin_btn(self):
        skinning.rip_skin(self.ui_rip_skin_attrs()[0], self.ui_rip_skin_attrs()[1], 
                        self.match_by_options.currentIndex(), self.influence_options.currentIndex())


def run():
    """displays windows"""

    for obj in gc.get_objects():
        #checks all objects in scene and verifies whether an instance of the window exists

        if isinstance(obj, MainDialog):
            print ("checking for instances")
            obj.close()


    srsu_main_dialog = MainDialog()

    #shows window
    srsu_main_dialog.show(dockable=True, floating=True)

    return
