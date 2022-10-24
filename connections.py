import pymel.core as pm

def connect_xforms(source=None, target=None, trans=True, rot=True, scale=False):
    '''
    connect_xforms
    Connects the transform attributes of a source node to a target node.  Direct connection with
    1:1 influence.

    usage:
    connect_xforms(source=[Pynode or string], target=[list of PyNode or string], trans=[bool],
        rot=[bool], scale=[bool])

    Defaults is "None" for source and target, if either isn't specified function will fall back on
    viewport selection.  
    trans and rot flags default to true.
    scale defaults to false.
    '''

    # Check if we need to use selection
    if((target == None) or (source == None)):
        selection = pm.ls(sl=True)
        source = selection[0]
        selection.remove(source)
        target = selection

    # Connect transforms if flagged.
    if(trans):
        for node in target:
            print("Connecting {}.translate to {}.translate.".format(source.name(), node.name()))
            source.translate >> node.translate

    if(rot):
        for node in target:
            print("Connecting {}.rotate to {}.rotate.".format(source.name(), node.name()))
            source.rotate >> node.rotate

    if(scale):
        for node in target:
            print("Connecting {}.scale to {}.scale.".format(source.name(), node.name()))
            source.scale >> node.scale

    return


def batch_connect(driver_attr = None, driven_attr = None):
    """takes input driver attr and driven attr and batch connects them.
    Select the driver as your first object and shift select all the driven objects with it.
    usage:
    batch_connect(driver_attr=[Pynode or string], driven_attr=[PyNode or string])

    Defaults is "None" for driver_attr and driven_attr, if either isn't specified function will fall back on
    viewport selection.
    """

    # makes a string of driven objects
    all_objects = pm.ls(selection=True)
    driver = all_objects[0]
    all_objects.remove(driver)

    # splits all attributes to be connected into list
    all_driven_attr = driven_attr.split(" ")

    # connects driver to all driven objects
    for object in all_objects:

        # connects driver to individual given attribute of each driven object
        for attr in all_driven_attr:
            pm.connectAttr(driver + '.' + driver_attr, object + '.' + attr, force=True)

