""" takes a blendshape target, nand allows you to import image maps to split that target into desired weights"""

import maya.cmds as cmds
import pymel.core as pm 
import maya.mel
import os

#sets string names
maya.mel.eval("string $weightName =\"\"")
maya.mel.eval("string $tgt_name =\"\"")
maya.mel.eval("int $idx_int")

#gets and sorts files
def get_files(smooth_iter = 0):
    """gets files and smooths based on smooth iter
    params: 
      smooth_iter(int): smooths each tgt that many times
    """ 
    #gets mesh selection
    mesh = pm.ls(selection = True)[0]
    print ("mesh is", mesh)
    #gets blendshapes (bs)
    bs = get_targets(mesh)[0]
    print ("bs is", bs)
    #gets bs targets
    tgts = get_targets(mesh)[1]
    print ("tgts are", tgts)
    num_tgts = len(tgts)
    #gets files from user
    files = pm.fileDialog2(fileMode = 4)
    print ("files are", files)
    index = num_tgts
    par_list = []
    
    for file_path in files:
      #runs import map funtion
        par = import_map(mesh, file_path, index, bs, tgts, smooth_iter)
        par_list.append(par)
        index += 1
        print ("index is", index)
    
        
def get_targets(mesh):
    """gets blendshape and target from mesh"""
    #gets bs
    bs = pm.listHistory(mesh, type = 'blendShape')[0]
    #gets tgt from bs
    tgts = pm.listAttr(bs + ".w" , m=True)

    return bs, tgts

def import_map(mesh, file_path, index, bs, tgts, smooth_iter):
    """imports in bs weight maps
       params:
              mesh(str): input mesh based on selection
              file_path(str): input by user selection
              index(int): number of targets
              bs(str): got from mesh
              tgt(list): got from bs
              smooth_iter(int): default - 0
   """
    #get file name
    file_name = os.path.basename(file_path)
    new_name_break = file_name.replace("_start", "").replace("_end", "")
    new_name = new_name_break.split(".")[0]
    print ("new_name is,", new_name)

    #check if matching tgt exists
    top_name = " "
    for i in new_name:
        if i == "_":
            top_name = file_name.split(i)[0]
            print ("top name exists", top_name)
            break
    
    cur_tgts = []
    

    #getting matching targets
    for j in tgts:
        if top_name in j:
            cur_tgts.append(j) 
            
        pm.setAttr(bs + "." + j, 1)
        

    print ("cur_tgts are", cur_tgts)
    #running through targets and copying 
    for tgt in cur_tgts:

        #duplicates mesh to transfer blendshape
        dup_mesh = pm.duplicate(mesh, n = "dupe_" + mesh)[0]
        #transfers bs to dup mesh
        pm.blendShape(bs, e = True, tc = 1, t = [str(mesh), index, str(dup_mesh), 1.0], w = [index, 1])
        pm.blendShape(bs, e = True, rtd = [0, index])
        new_name_str = "\"" + str(new_name) + "\""   
        idx = index
        #creates new target name based on file name
        maya.mel.eval("$tgt_name =" + new_name_str + ";")
        maya.mel.eval("$idx_int =" + str(idx) + ";")
        get_tgt_name = cmds.aliasAttr(bs + '.w[' + str(idx) + ']', q = True)
        print ("tgt is", get_tgt_name)
        #copies weight
        cmds.aliasAttr(new_name, bs + "." + get_tgt_name) #rename blendshape target alias
        #maya.mel.eval("blendShapeRenameTargetAlias blendShape1 $idx_int $tgt_name")
        
        get_tgt_name = cmds.aliasAttr(bs + '.w[' + str(idx) + ']', q = True)
        print ("new tgt is", get_tgt_name)

        #opening bs paint context
        pm.select(mesh)
        cmds.ArtPaintBlendShapeWeightsToolOptions()
        ctx = cmds.currentCtx()
        print (ctx)
        
        maya.mel.eval("artAttrPaintOperation artAttrCtx Replace;")

        #selects target name in bs paint weights context
        new_name_str = "\"" + str(get_tgt_name) + "\""
        maya.mel.eval("$weightName =" + new_name_str + ";")
        maya.mel.eval("artBlendShapeSelectTarget artAttrCtx $weightName")

        try:
            #imports file
            cmds.artAttrCtx(ctx, e = True, ifl = file_path, importfilemode= 'Luminance')
            print ("imported file successfully")
            break
        except:
            print("could not import")
            break
        
        for i in smooth_iter:
            #runs smooth operation
            maya.mel.eval("artAttrPaintOperation artAttrCtx Smooth;")
            maya.mel.eval("artAttrCtx -e -clear `currentCtx`;")
        
        
def prep_scene():
    """cleans scene after importing tgts"""

    #identifies duplicates for sorting/deletion
    dupes = pm.ls("*dupe_*")
    #identifies and renames original mesh
    mesh = dupes[0].replace("dupe_", "")
    #identifies blendshapes and targets
    bs = pm.listHistory(mesh, type = 'blendShape')[0]
    tgts = pm.listAttr(bs + ".w" , m=True)
    dupes = pm.ls("*dupe_*")
    #deletes duplicates
    pm.delete(dupes)

    for tgt in tgts: pm.setAttr(bs + "." + tgt, 0)  #sets all targets to 0

    for tgt in tgts:
        #sets individual targets to 1, duplicates mesh to save as bs shape
        pm.setAttr(bs + "." + tgt, 1)
        tgt_name = tgt.replace("_start", "").replace("_end", "")
        dup_tgt = pm.duplicate(mesh, n = tgt_name)
        #sets back to 0
        pm.setAttr(bs + "." + tgt, 0)
