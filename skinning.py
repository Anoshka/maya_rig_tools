import pymel.core as pm
import maya.mel as mel


def copy_skinweights(source="", target=""):
    '''
    copy_skinweights

    Copy the skin influences from a source (even between unlike pieces of geo) to any number of 
    targets.

    usage:
    copy_skinweights(source=[string/PyNode], target=[string/PyNode])
    
    source - a string or PyNode pointing to a skinned piece of geo.
    target - a string or PyNode pointing to an unskinned piece of geo.
    '''

    # If nothing is supplied by argument, use a selection.
    if(source == "" or target == ""):
        selection = pm.ls(sl=True)
        if(selection == []):
            pm.warning("Must select some skinned geo.")
            return

    source = selection[0]
    del selection[0]
    target = selection

    # Find joints and skinCluster node:
    sourceSkin = find_related_skinCluster(source)
    joints = select_bound_joints(source)

    # Start a progress bar
    
    count = 0
    for geo in target:
        # Build a skinCluster node on the target
        #pm.skinCluster()
        print ("Copying skin influences to {}".format(geo))
        
        try:
            pm.skinCluster(geo.name(), joints, omi=False, tsb=True)
        except:
            print ("{} already has a skinCluster on it...".format(geo.name()))
            continue

        try:
            dest_skin = find_related_skinCluster(geo)
        except:
            print ("{} already has a skinCluster on it...".format(dest_skin))
            continue
        pm.copySkinWeights(ss=sourceSkin, ds=dest_skin, noMirror=True, sm=True)
        count += 1

    print ("Done.  Copied skins to {} target geos.".format(count))

    return 


def select_bound_joints(node=None):
    '''
    select_bound_joints
    Selected the joints that are bound by skinCluster to the selected geo.

    usage:
    select_bound_joints(node=[geo node]) # node defaults to using the selection if not specified.
    '''

    if(node == None):
        node = pm.ls(sl=True)[0]
        
    print ("Looking for joints influencing {}...".format(node))
    
    #joints = pm.listConnections((node.name() + ".matrix"), d=False, s=True)
    joints = pm.skinCluster(node, query=True, inf=True)
    print ("Selected joints influencing {}:\n{}".format(node, joints))

    pm.select(cl=True)
    pm.select(joints)

    return joints


def get_info(source_mesh=None, target_mesh=None):
    '''
    rip_skin
    Copies skinning from one mesh to another, using duplicated joints instead of the same ones.
    Capable of pulling a skin from a referenced rig.

    usage:
    rip_skin(source_mesh=[PyNode], target_mesh=[PyNode])

    If source_mesh and target_mesh aren't specificed, function will resort to selection.
    '''


    # Get the skincluster and list of influences on the source mesh
    old_skinCluster = find_related_skinCluster(node=source_mesh)
    old_joints = select_bound_joints(node=source_mesh)

    # Get the skincluster and the list of influences on the new mesh
    new_skinCluster = find_related_skinCluster(node=target_mesh)
    new_joints = select_bound_joints(node=target_mesh)

    #get shape nodes
    old_shapeNode = pm.listRelatives(source_mesh, shapes = True)[0]
    new_shapeNode = pm.listRelatives(target_mesh, shapes = True)[0]
    
    #get vertices
    source_vertex = pm.ls(source_mesh+'.vtx[*]', fl=True)
    target_vertex = pm.ls(target_mesh+'.vtx[*]', fl=True)

    source_vtx = []
    target_vtx = []

    

    for k in source_vertex:
        source_vtx.append(str(k))
    
    for k in target_vertex:
        target_vtx.append(str(k))
    
    print ("source_vtx", source_vtx)

    # Make a list of just the joint names for comparision
    old_names=[]
    for joint in old_joints:
        old_names.append(joint.name())
    missing_infs = old_joints

    # Now make warnings about what is or isn't matching in the lists.
    for joint in new_joints:
        if(joint.name() in old_names):
            missing_infs.remove(joint.name())
            
    # Now new_joint and old_joints should have contents with the same names... let's check how much
    # they do or do not match.
    source_data = {'skinCluster': old_skinCluster, 
                    'shapeNode': old_shapeNode,
                    'vertex': source_vtx,
                    'joints': old_joints}
    target_data = {'skinCluster': new_skinCluster, 
                    'shapeNode': new_shapeNode,
                    'vertex': target_vtx,
                    'joints': old_joints}
    return (source_data, target_data)


def get_skinCluster_info(vertices, skinCluster):

    if len(vertices) != 0 and skinCluster != "":
        verticeDict = {}
        
        for vtx in vertices:
            influenceVals = pm.skinPercent(skinCluster, vtx, 
                                             q=1, v=1, ib=0.001)
            
            influenceNames = pm.skinPercent(skinCluster, vtx, 
                                              transform=None, q=1, 
                                              ib=0.001) 
                        
            verticeDict[vtx] = zip(influenceNames, influenceVals)
        
        return verticeDict
    else:
        pm.error("No Vertices or SkinCluster passed.")
    

def rip_skin(source_mesh = None, target_mesh = None, match_option = 0, influence = 0):
    """select source mesh, target mesh and run this to copy skin
        params:
            source mesh (str): either by selection or input
            target mesh (str): either by selection or input
            match option (int): 0 -> closest point, 1 -> UVs
            influence(int): 0 -> closest joint, 1 -> name
    """
    
    if(source_mesh == None):
        #checks if source mesh exists and selects 

        source_mesh = pm.ls(sl=True)[0]
        target_mesh = pm.ls(sl=True)[1]

    pm.select(source_mesh, target_mesh)

    print ("ripping skin")
    if influence == 0:
        if match_option == 0:
            #if the options selected are closest points and closest joint
            pm.copySkinWeights(surfaceAssociation = "closestPoint", 
                                influenceAssociation = "closestJoint", noMirror = True)
        else:
            #if the options selected are uv and closest joint
            pm.copySkinWeights(surfaceAssociation = "closestPoint", uvSpace = ['map1', 'map1'], 
                                influenceAssociation = "closestJoint", noMirror = True)
    else:
        joints = select_bound_joints(node = source_mesh)
        pm.select(joints)
        strip = pm.selected()[0].namespace()
        for jnt in joints:
            #stripping namespace
            name = jnt.replace(strip, "")
            pm.rename(jnt, name)
        if match_option == 0:
            #if the options selected are closest points and namespace
            pm.copySkinWeights(surfaceAssociation = "closestPoint", 
                                influenceAssociation = "name", noMirror = True)
        else:
            #if the options selected are uv and namespace
            pm.copySkinWeights(surfaceAssociation = "closestPoint", uvSpace = ['map1', 'map1'], 
                                influenceAssociation = "name", noMirror = True)
        
        for jnt in joints:
            name = jnt
            if "|" in jnt:
                #adding namespace back
                name = jnt.split("|")[-1]
            pm.rename(jnt, strip + name)
    
    return
