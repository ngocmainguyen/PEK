import maya.cmds as cmds
import maya.mel as mel
import sys
import math

all_locs = []
all_jnts = []
dynamic_ik_curves = []
dynamic_handles = []
total_spikes = []
total_name = []
last_dorsalLG = []
last_L_pelvicLG = []
last_R_pelvicLG = []
last_analLG = []
dynamic_offset_groups = []
dynamic_sdk_groups = []
dynamic_oc_groups = []
dorsal = 0
l_pect = 0
tail = 0
rb_selection = []
bind_jnt = []
con_jnt = []
rb_chain = []
sine_number = []


class NM_Window:

    # constructor
    def __init__(self):
        self.window = "NM_Window"
        self.title = "PEK Auto Rig"
        self.size = (200, 400)

        # close old window is open
        if cmds.window (self.window, exists=True):
            cmds.deleteUI (self.window, window=True)

        # create new window
        self.window = cmds.window (self.window, title=self.title, widthHeight=self.size, s=1)

        # UI
        tabs = cmds.tabLayout ()
        child1 = cmds.columnLayout ()
        self.general_note = cmds.text(l='''Click shelf button to restart
Same value every steps of the process''', al ="center", w=200)
        self.separate = cmds.separator (w=200, h=5)
        self.spine_amount = cmds.intFieldGrp (label='Spine', cl3=["left", "left", "right"],
                                              cw3=[70, 70, 50], el="joints", value1=8)
        self.spine_distance = cmds.floatFieldGrp (label='Distance', cl3=["left", "left", "right"],
                                                  cw3=[70, 70, 50], el="units", value1=2)
        self.spine_span = cmds.intFieldGrp (label='Spine Curve', cl3=["left", "left", "right"],
                                            cw3=[70, 70, 50], el="spans", value1=10)
        cmds.rowColumnLayout (nc=2)
        self.spine_loc_button = cmds.button (l="Spine LOC", w=99, c=self.create_spine_loc)
        self.spine_joint_button = cmds.button (l="Spine JNT", w=99, c=self.create_spine_jnt)
        cmds.setParent (child1)
        self.spine_cluster_per_CV = cmds.intFieldGrp (label='Cluster/ CV', cl3=["left", "left", "right"],
                                               cw3=[70, 70, 50], el="cluster", value1=1)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l="Cluster/CV = 1. Manually Point CNSTR spine_CON_OFFSET to spine_JNT",
                                al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.spine_button = cmds.button (l="Create Spine", w=200, c=self.create_spine)
        self.separate = cmds.separator (w=200, h=10)
        self.jnt_button = cmds.button (l="Select - Create joints", w=200, c=self.create_jnt)
        cmds.rowColumnLayout (nc=2)
        self.sdk_grp = cmds.checkBox (label='SDK', w=41)
        self.con_button = cmds.button (l="Select - Create controls", w=158, c=self.create_con)
        cmds.setParent (child1)
        self.sticky_eye_button = cmds.button (l="Select RB Con - Sticky Eyes", w=200, c=self.sticky_eyes)
        cmds.setParent (tabs)


        child2 = cmds.columnLayout ()
        self.to_do = cmds.text (l= '''DON'T delete FIRST the LAST locators
Once create a fin, DON'T restart''', al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.name_menu = cmds.optionMenuGrp(l='Fin Name', cw2=[70,130], cl2 = ["left","left"])
        self.dorsal = cmds.menuItem(l='dorsal')
        self.dorsal_long = cmds.menuItem(l='dorsalLG')
        self.pelvic = cmds.menuItem (l='L_pelvic')
        self.pelvic_long = cmds.menuItem (l='L_pelvicLG')
        self.anal = cmds.menuItem (l='anal')
        self.anal_long = cmds.menuItem (l='analLG')
        cmds.setParent(child2)
        self.spikes_amount = cmds.intFieldGrp (label='Fin Spikes', cl3=["left", "left", "right"],
                                               cw3=[70, 70, 50], el="chains", value1=10)
        self.spikes_joints = cmds.intFieldGrp (label='Joints/ Spikes', cl3=["left", "left", "right"],
                                               cw3=[70, 70, 50], el="joints", value1=4)
        self.spikes_distance = cmds.floatFieldGrp (label='Distance', cl3=["left", "left", "right"],
                                                   cw3=[70, 70, 50], el="units", value1=.5)
        self.spikes_height = cmds.floatFieldGrp (label='Height', cl3=["left", "left", "right"],
                                                 cw3=[70, 70, 50], el="units", value1=1)
        self.spikes_span = cmds.intFieldGrp (label='Spike Curves', cl3=["left", "left", "right"],
                                             cw3=[70, 70, 50], el="spans", value1=10)
        cmds.rowColumnLayout(nc=3)
        self.spikes_loc_button = cmds.button (l="LOCs", w=48, c=self.create_dynamic_fin_loc)
        self.spikes_parent = cmds.button (l="Parent LOCs", w=80, c=self.parent_dynamic_fin_loc)
        self.spikes_joints_ik = cmds.button (l="Joints - IK", w=70, c=self.create_dynamic_fin)
        cmds.setParent (child2)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l= "Create all fin before moving on!", al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.dynamic_button =  cmds.button (l="Create Dynamic", w=200, c=self.create_dynamic)
        self.spikes_cluster_per_CV = cmds.intFieldGrp (label='Cluster/ CV', cl3=["left", "left", "right"],
                                               cw3=[70, 70, 50], el="cluster", value1=1)
        cmds.setParent (child2)
        self.fin_auto_cluster = cmds.button (l="Auto Cluster", w=200, c=self.create_auto_cluster)
        self.dynamic_master_con = cmds.button (l="Fin Master control", w=200, c=self.create_dynamic_master_control)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l='''For open/ close fin:
Fix master_CON (rotate Y) and OC''', al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.dynamic_clean_button = cmds.button (l="Clean Outliner", w=200, c=self.dynamic_clean)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l= '''Parent follicle under spine joints
Parent dynamic crv under spine joints''', al="center", w=200,
                                ww=1)
        cmds.setParent (tabs)


        child3 = cmds.columnLayout ()
        self.ribbon_name_menu = cmds.optionMenuGrp (l='Fin Name', cw2=[70, 130], cl2=["left", "left"])
        self.left_pectorial = cmds.menuItem (l='L_pect')
        self.tail = cmds.menuItem (l='tail')
        cmds.setParent (child3)
        self.ribbon_chain_amount = cmds.intFieldGrp (label='Fin Control', cl3=["left", "left", "right"],
                                                     cw3=[70, 70, 50], el="chains", value1=3)
        self.ribbon_cons_total = cmds.radioButtonGrp (label='Ctrl/ Chain', cw4=[71,43,43,43],
                                                      cl4=["left", "left","left", "left"], nrb = 3,
                                                      la3 = ['3','5','9'], sl=1)
        cmds.setParent (child3)
        cmds.rowColumnLayout (nc=3)
        self.ribbon_loc_button = cmds.button (l="LOCs", w=48, c=self.create_ribbon_locs)
        self.ribbon_loc_parent = cmds.button (l="Parent LOCs", w=80, c=self.parent_ribbon_loc)
        self.ribbon_joints = cmds.button (l="CON Joints", w=70, c=self.create_ribbon_joint)
        cmds.setParent (child3)
        self.separate = cmds.separator (w=200, h=5)
        self.note = cmds.text (l='''BEFORE MOVING ON:
Create both pect and tail ''', al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l='''Select bottom spikes joints & use CometJointOrient:
Aim Axis: X, Reverse   Up Axis: Z''', al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.create_base_ribbon = cmds.button (l="Create Base Ribbon", w=200, c=self.create_base_ribbon)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (l='''Change rebuildSurface span U & V''', al="center", w=200, ww=1)
        self.separate = cmds.separator (w=200, h=5)
        self.to_do = cmds.text (al="center", w=200, ww=1,
l='''U Count = amount of verticle line
V Count = amount of horizontal line
Edge bounded   Static   New Hair Sys''')
        cmds.rowColumnLayout (nc=2)
        self.create_ribbon = cmds.button (l="Hair Menu", w=99, c=self.create_ribbon)
        self.organize_ribbon = cmds.button (l="Organize RB", w=99, c=self.organize_ribbon)
        cmds.setParent (child3)
        self.ribbon_sine_deformer = cmds.button (l='''Sine Deformer Menu (HB = 2)
In order: L, R, tail''', w=200, c=self.create_ribbon_sine)
        self.separate = cmds.separator (w=200, h=5)
        cmds.rowColumnLayout (nc=2)
        self.sine_amount = cmds.intFieldGrp (label='Sine Amount', cl2=["left", "left"],
                                                     cw2=[70, 70], value1=4)
        self.sine_amount_btn = cmds.button (l="OK", w=50, c=self.sine_info)
        cmds.setParent (child3)
        self.connect_attributes_rb = cmds.button (l='Create master con and connect attr', w=200,
                                                  c=self.connect_ribbon_attributes)
        self.to_do = cmds.text (l= '''Select SDK grp of RB con''', al="center", w=200, ww=1)    
        cmds.rowColumnLayout (nc=3)
        self.l_pect_sdk_oc_button = cmds.button (l="l_pect", w=66, c=self.l_pect_oc)
        self.r_pect_sdk_oc_button = cmds.button (l="r_pect", w=66, c=self.r_pect_oc)
        self.tail_sdk_oc_button = cmds.button (l="tail", w=66, c=self.tail_oc)
        cmds.setParent (child3)
        self.to_do = cmds.text (l= '''Turn on BS in def_RB''', al="center", w=200, ww=1)
        self.rb_clean = cmds.button (l='Clean Outliner', w=200, c=self.rb_clean)
        cmds.setParent (tabs)

        cmds.tabLayout (tabs, edit=True, tabLabel=((child1, 'Spine'), (child2, 'Dynamic'), (child3, 'Ribbon')))

        # display new window
        cmds.showWindow ()


    def create_spine_loc(self, *args):
        amount = cmds.intFieldGrp (self.spine_amount, q=1, value1=1)
        distance = cmds.floatFieldGrp (self.spine_distance, q=1, value1=1)

        # Create locators
        for i in range (amount):
            count = i + 1
            exist_locator = cmds.ls ('spine_{}_LOC'.format (count))
            if not exist_locator:
                spineloc = cmds.spaceLocator (n='spine_{}_LOC'.format (count))[0]
                cmds.setAttr (spineloc + '.translateZ', count * distance * (-1))
                for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                    cmds.setAttr (spineloc + '.' + each, .5)
                cmds.makeIdentity (spineloc, a=1, t=1, r=1, s=1)

        # Parent locators
        for i in range (amount - 1):
            count = i + 2
            cmds.parent ('spine_{}_LOC'.format (count), 'spine_{}_LOC'.format (count - 1))
        root_loc = cmds.spaceLocator (n='root_LOC')[0]
        cmds.parent ('spine_1_LOC', 'root_LOC')
        for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
            cmds.setAttr (root_loc + '.' + each, .5)

    def create_spine_jnt(self, *args):
        amount = cmds.intFieldGrp (self.spine_amount, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spine_span, q=1, value1=1)
        per_cv = cmds.intFieldGrp (self.spine_cluster_per_CV, q=1, value1=1)

        # Spine Joints
        locs = cmds.ls ('*_LOC')
        exist_spine = cmds.ls ('spine_{}_JNT'.format (amount))
        sc = 0
        for loc in locs:
            if not exist_spine:
                par_loc = cmds.listRelatives (loc, p=1)

                # Joints
                cmds.select (cl=1)
                jnt = cmds.joint (n=loc.replace ('_LOC', '_JNT'), sc=sc)
                bind_jnt.append(jnt)
                cnstr = cmds.parentConstraint (loc, jnt)
                cmds.delete (cnstr)
                cmds.makeIdentity (jnt, a=1, t=1, r=1, s=1)
                if par_loc:
                    par_jnt = par_loc[0].replace ('_LOC', '_JNT')
                    cmds.parent (jnt, par_jnt)

    def create_spine(self, *args):
        amount = cmds.intFieldGrp (self.spine_amount, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spine_span, q=1, value1=1)
        per_cv = cmds.intFieldGrp (self.spine_cluster_per_CV, q=1, value1=1)

        # IK handle
        cmds.ikHandle (n='spine_HDL', sj='spine_1_JNT', ee='spine_{}_JNT'.format (amount), sol='ikSplineSolver')
        cmds.select (cl=1)
        cmds.rename ('curve1', 'spine_CRV')
        cmds.rename ('effector1', 'spine_EFF')
        cmds.rebuildCurve ('spine_CRV', s=spans)
        cmds.delete ('spine_CRV', ch=1)

        # autoswim icon
        autocon = cmds.curve (n='autoswim_CON', d=3,
                              p=[(0.705321, 0, 0), (0.732106, 0, 0.424001), (0.785676, 0, 1.272002),
                                 (0.383882, 0, -0.38634), (0.109492, 0, 1.360713), (-1.717037, 0, 0.000239987),
                                 (0.109492, 0, -1.361673), (0.383882, 0, 0.3897), (0.785676, 0, -1.272842),
                                 (0.732106, 0, -0.424281), (0.705321, 0, 0)])

        cmds.setAttr ('autoswim_CON.lineWidth', 2)
        cmds.setAttr ('autoswim_CON.rx', 90)
        cmds.setAttr ('autoswim_CON.ry', 90)
        cmds.setAttr ('autoswim_CON.tx', -1)
        cmds.makeIdentity (autocon, a=1, t=1, r=1, s=1)
        second_shape = cmds.curve (n='autoswim2_CON', d=3,
                                  p=[(0.705321, 0, 0), (0.732106, 0, 0.424001), (0.785676, 0, 1.272002),
                                     (0.383882, 0, -0.38634), (0.109492, 0, 1.360713), (-1.717037, 0, 0.000239987),
                                     (0.109492, 0, -1.361673), (0.383882, 0, 0.3897), (0.785676, 0, -1.272842),
                                     (0.732106, 0, -0.424281), (0.705321, 0, 0)])
        cmds.setAttr ('autoswim2_CON.lineWidth', 2)
        cmds.setAttr ('autoswim2_CON.rx', 90)
        cmds.setAttr ('autoswim2_CON.ry', 90)
        cmds.setAttr ('autoswim2_CON.tx', 1)
        cmds.makeIdentity (second_shape, a=1, t=1, r=1, s=1)
        selection = cmds.listRelatives (second_shape, s=1)
        cmds.select (selection, autocon)
        mel.eval ('parent-r-s;')
        cmds.delete ('autoswim2_CON')
        cmds.select (cl=1)
        cmds.select ('autoswim_CON')
        for each in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility']:
            cmds.setAttr ('autoswim_CON' + '.' + each, l=1, k=0, cb=0, ch=0)
        cmds.setAttr ('autoswim_CON' + '.overrideEnabled', 1, e=1, q=1)
        cmds.setAttr ('autoswim_CON' + '.overrideColor', 9)

        # autoswim attributes
        cmds.addAttr (autocon, at='float', ln='Amplitude', nn='Amplitude')
        cmds.setAttr ('autoswim_CON.Amplitude', e=1, k=1)
        cmds.addAttr (autocon, at='float', ln='Wavelength', nn='Wavelength')
        cmds.setAttr ('autoswim_CON.Wavelength', e=1, k=1)
        cmds.addAttr (autocon, at='float', ln='Autoswim', nn='Autoswim')
        cmds.setAttr ('autoswim_CON.Autoswim', e=1, k=1)
        cmds.select (cl=1)
        cmds.select ('spine_CRV')
        cmds.nonLinear (n='autoswim', type='sine', lowBound=-2, highBound=0)
        cmds.rename ('autoswimHandle', 'autoswim_HDL')
        cmds.setAttr ('autoswim' + '.dropoff', 1)
        cmds.setAttr ('autoswim_HDL' + '.rx', -90)
        last_spine_joint = cmds.ls ('spine_*_JNT')[-1]
        cmds.matchTransform ('autoswim_HDL', last_spine_joint, pos=True)
        cmds.group ('autoswim_CON', n='autoswim_OFFSET')

        # Connect autoswim attributes
        cmds.connectAttr ('autoswim_CON.Amplitude', 'autoswim.amplitude', f=1)
        cmds.shadingNode ("multiplyDivide", n="autoswim_multi", au=1)
        cmds.connectAttr ('autoswim_CON.Autoswim', 'autoswim_multi.input1.input1X', f=1)
        cmds.setAttr ('autoswim_multi.input2X', -1)
        cmds.connectAttr ('autoswim_multi.output.outputX', 'autoswim.offset', f=1)
        cmds.connectAttr ('autoswim_CON.Wavelength', 'autoswim.wavelength', f=1)

        total_cv = spans + 3
        x1 = 2
        y1 = 2
        spine_clusters = []
        x = 0
        y = 1
        z = math.ceil (total_cv / per_cv)

        # cluster middle cvs
        if per_cv == 1:
            # cluster first two cvs
            cmds.selectType (cv=True)
            cmds.select ('spine_CRV' + '.cv[0:1]')
            cluster01 = cmds.cluster (n='spine_1_CLT')[1]
            spine_clusters.append (cluster01)
            for j in range (total_cv - 4):
                cmds.selectType (cv=True)
                cmds.select ('spine_CRV' + '.cv[{}]'.format (x1))
                clusters = cmds.cluster (n='spine_{}_CLT'.format (y1))[1]
                spine_clusters.append (clusters)
                y1 += 1
                x1 += 1
            x1 = 0
            # cluster two last cvs
            cmds.selectType (cv=True)
            cmds.select ('spine_CRV' + '.cv[{}:{}]'.format (total_cv - 2, total_cv - 1))
            last_cluster = cmds.cluster (n='spine_{}_CLT'.format (total_cv - 2))[1]
            spine_clusters.append (last_cluster)

        else:
            for j in range (int (z) + 1):
                cmds.selectType (cv=True)
                cmds.select ('spine_CRV' + '.cv[{}:{}]'.format (x, x + (per_cv - 1)))
                clusters = cmds.cluster (n='spine_{}_CLT'.format (y))[1]
                spine_clusters.append (clusters)
                x += per_cv
                y += 1
            x = 0

        # create controls
        for i in spine_clusters:
            control_name = i.replace ("_CLTHandle", "_CON")
            ctrl = cmds.circle (nr=(0, 0, 1), r=1, n=control_name)[0]
            offset = cmds.group (ctrl, n=ctrl + '_OFFSET')
            cmds.parentConstraint (i, offset, mo=0)
            cmds.delete (cmds.parentConstraint (i, offset))
            cmds.setAttr (control_name + '.lineWidth', 2)
            cmds.setAttr (control_name + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (control_name + '.overrideColor', 17)
            for each in ['rx', 'rz', 'sx', 'sy', 'sz', 'visibility']:
                cmds.setAttr (control_name + '.' + each, l=1, k=0, cb=0, ch=0)

        # Connect attribute
        s = 1
        for each in spine_clusters:
            cmds.connectAttr ('spine_{}_CON.translate'.format (s), each + '.translate')
            cmds.connectAttr ('spine_{}_CON.rotate'.format (s), each + '.rotate')
            s += 1

        # cluster tree
        if per_cv == 1:
            count = 1
            for i in range (10):
                cmds.parent ('spine_{}_CLTHandle'.format (count + 1), 'spine_{}_CLTHandle'.format (count))
                count += 1
        else:
            count = 1
            for j in range (int (z)):
                cmds.parent ('spine_{}_CLTHandle'.format (count + 1), 'spine_{}_CLTHandle'.format (count))
                count += 1

        # create cluster offset. group under root JNT
        cmds.group ('spine_1_CLTHandle', n='spine_CLT_OFFSET')
        cmds.parent ('spine_CLT_OFFSET', 'root_JNT')

        # Make FK control follow autoswim
        spine_con_offset = cmds.ls ('spine_*_CON_OFFSET', assemblies=True)
        spine_jnts = cmds.ls ('spine_*_JNT')
        if per_cv == 1:
            pass
        else:
            count = 1
            for each in spine_con_offset:
                cmds.pointConstraint ('spine_{}_JNT'.format (count), each, mo=True, w=1)
                count += 1

        # group all spine cons
        cmds.group (spine_con_offset, n='spine_con_GRP')

        # COG control
        cir = cmds.circle (n='COG_CON', d=3, ch=0, nry=1, nrx=0, nrz=0)
        shapeNode = cmds.listRelatives (s=1)[0]
        cmds.setAttr (shapeNode + '.lineWidth', 2)
        cmds.setAttr ('COG_CON' + '.overrideEnabled', 1, e=1, q=1)
        cmds.setAttr ('COG_CON' + '.overrideColor', 17)
        grp = cmds.group (n='COG_OFFSET', em=1, w=1)
        cmds.parent (cir, grp)
        cmds.matchTransform ('COG_CON', 'root_JNT', piv=True)
        cmds.parentConstraint ('COG_CON', 'root_JNT', mo=True, w=1)
        cmds.select ('spine_CRV')
        cmds.cluster (n='COG_CLT')
        cmds.parent ('COG_CLTHandle', 'root_JNT')
        cmds.parent ('spine_con_GRP', 'COG_CON')

        # no double transform
        cmds.group ('spine_CRV', 'spine_HDL', 'autoswim_HDL', n='NO_Transform')
        cmds.setAttr ('spine_CRV.inheritsTransform', 0)
        cmds.setAttr ('spine_HDL.inheritsTransform', 0)
        cmds.setAttr ('autoswim_HDL.inheritsTransform', 0)
        cmds.setAttr ('NO_Transform.inheritsTransform', 0)
        cmds.setAttr ('COG_CLTHandle.inheritsTransform', 0)

        # global con
        fourarr = cmds.curve (n='global_CON', d=1,
                              p=[(-1, 0, 1), (-3, 0, 1), (-3, 0, 2), (-4, 0, 0), (-3, 0, -2), (-3, 0, -1), (-1, 0, -1),
                                 (-1, 0, -3), (-2, 0, -3), (0, 0, -4), (2, 0, -3), (1, 0, -3), (1, 0, -1), (3, 0, -1),
                                 (3, 0, -2), (4, 0, 0), (3, 0, 2), (3, 0, 1), (1, 0, 1), (1, 0, 3), (2, 0, 3),
                                 (0, 0, 4), (-2, 0, 3), (-1, 0, 3), (-1, 0, 1)])
        shapeNode = cmds.listRelatives (s=1)[0]
        cmds.setAttr (shapeNode + '.lineWidth', 2)
        cmds.setAttr ('global_CON' + '.overrideEnabled', 1, e=1, q=1)
        cmds.setAttr ('global_CON' + '.overrideColor', 17)
        grp = cmds.group (n='global_OFFSET', em=1, w=1)
        cmds.parent (fourarr, grp)
        cmds.select ('global_CON.cv[0]', 'global_CON.cv[6]', 'global_CON.cv[12]', 'global_CON.cv[18]',
                     'global_CON.cv[24]', r=True)
        mel.eval ('scale -r -p 0cm 0cm 0cm 2.364831 1 2.364831;')
        cmds.select (cl=1)
        cmds.matchTransform ('global_CON', 'COG_CON', piv=True)

        # organize outliner
        cmds.parent ('autoswim_OFFSET', 'COG_CON')
        cmds.parent ('NO_Transform', 'COG_OFFSET', 'global_CON')
        cmds.group ('root_JNT', n='spine_jnt_GRP')
        cmds.group ('root_LOC', n='spine_loc_GRP')
        cmds.scaleConstraint ('global_CON', 'spine_jnt_GRP', mo=True, w=1)
        cmds.setAttr ('NO_Transform.visibility', 0)
        cmds.setAttr ('spine_loc_GRP.visibility', 0)
        cmds.setAttr ('spine_CLT_OFFSET.visibility', 0)
        cmds.setAttr ('COG_CLTHandle.visibility', 0)

    def create_jnt(self,*args):
        # Make joint out of selection
        sc = 0
        locs = cmds.ls (selection=True)
        for loc in locs:
            parLoc = cmds.listRelatives (loc, p=1)
            # Joints
            cmds.select (cl=1)
            jnt = cmds.joint (n=loc.replace ('_LOC', '_JNT'), sc=sc)
            cnstr = cmds.parentConstraint (loc, jnt)
            cmds.delete (cnstr)
            cmds.makeIdentity (jnt, a=1, t=1, r=1, s=1)
            if parLoc:
                parJnt = parLoc[0].replace ('_LOC', '_JNT')
                cmds.parent (jnt, parJnt)

    def create_con(self,*args):
        sdk = cmds.checkBox(self.sdk_grp, q=1, v=1)

        controls = []
        # Make control out of selection
        list = cmds.ls (selection=True)
        for i in list:
            par = cmds.listRelatives (i, p=1)
            control_id = i.replace ('_JNT', '_CON')
            ctrl = cmds.circle (nr=(0, 1, 0), r=1, n=control_id)[0]
            offset = cmds.group (ctrl, n=ctrl + '_OFFSET')
            if sdk == 1:
                group = cmds.group (ctrl, n=ctrl + '_SDK')
            cmds.parentConstraint (i, offset, mo=0)
            cmds.setAttr (offset + "_parentConstraint1.target[0].targetOffsetRotateZ", 90)
            cmds.delete (cmds.parentConstraint (i, offset))
            if par:
                parJnt = par[0].replace ('_JNT', '_CON')
                cmds.parent (offset, parJnt)
            controls.append (ctrl)
        for each in controls:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)

    def sticky_eyes(self,*args):
        # Eyes
        eyeJoint = "eye_JNT"
        eyeConttrol = "eye_CON"

        # offsetValue = 0

        controlList = cmds.ls (sl=1)

        for i in controlList:
            cmds.shadingNode ("multiplyDivide", au=1, n=i + "_multi")
            cmds.shadingNode ("remapValue", au=1, n=i + "_remap")
            cmds.connectAttr (eyeJoint + ".rotate", i + "_multi.input1", f=1)
            cmds.connectAttr (i + "_remap.outValue", i + "_multi.input2X", f=1)
            cmds.connectAttr (i + "_remap.outValue", i + "_multi.input2Y", f=1)
            cmds.connectAttr (i + "_remap.outValue", i + "_multi.input2Z", f=1)
            cmds.connectAttr (i + "_multi.output", i + ".rotate", f=1)

    def create_dynamic_fin_loc(self, *args):
        name = cmds.optionMenuGrp (self.name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.name_menu, q=1, sl=1)
        amount = cmds.intFieldGrp (self.spikes_amount, q=1, value1=1)
        per_spikes_amount = cmds.intFieldGrp (self.spikes_joints, q=1, value1=1)
        distance = cmds.floatFieldGrp (self.spikes_distance, q=1, value1=1)
        height = cmds.floatFieldGrp (self.spikes_height, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spikes_span, q=1, value1=1)
        global dorsal

        # Create locator
        for i in range (per_spikes_amount):
            count = i + 1
            exist_locator = cmds.ls ('{}_LOC_{}'.format (name, count))
            if not exist_locator:
                if name_num == 3 or name_num == 4:
                    spikeloc = cmds.spaceLocator (n='{}_LOC_{}'.format (name, count))[0]
                    cmds.setAttr (spikeloc + '.ty', -3)
                    cmds.setAttr (spikeloc + '.tz', count * height * (-1))
                    cmds.setAttr (spikeloc + '.ty', count * (-height))
                    cmds.setAttr (spikeloc + '.tx', 0.5)
                    for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                        cmds.setAttr (spikeloc + '.' + each, .2)
                    cmds.makeIdentity (spikeloc, a=1, t=1, r=1, s=1)
                elif name_num == 5 or name_num == 6:
                    spikeloc = cmds.spaceLocator (n='{}_LOC_{}'.format (name, count))[0]
                    cmds.setAttr (spikeloc + '.ty', -3)
                    cmds.setAttr (spikeloc + '.tz', count * height * (-1))
                    cmds.setAttr (spikeloc + '.ty', count * (-height))
                    for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                        cmds.setAttr (spikeloc + '.' + each, .2)
                    cmds.makeIdentity (spikeloc, a=1, t=1, r=1, s=1)
                else:
                    spikeloc = cmds.spaceLocator (n='{}_LOC_{}'.format (name, count))[0]
                    cmds.setAttr (spikeloc + '.ty', 3)
                    cmds.setAttr (spikeloc + '.tz', count * height * (-1))
                    cmds.setAttr (spikeloc + '.ty', count * height)
                    for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                        cmds.setAttr (spikeloc + '.' + each, .2)
                    cmds.makeIdentity (spikeloc, a=1, t=1, r=1, s=1)
        
        # Parent to first loc of the tre to edit the locators easier
        for i in range (per_spikes_amount-1):
            count = i + 2
            cmds.parent ('{}_LOC_{}'.format (name, count), '{}_LOC_1'.format (name))

        # Create multiple chains of locator
        for i in range (amount - 1):
            count = i + 1
            copy = cmds.duplicate ('{}_LOC_1'.format (name), rc=1)[0]
            cmds.setAttr (copy + '.tz', count * distance * (-1))
        for i in range (amount * per_spikes_amount):
            count = i + 1
            cmds.rename ('{}_LOC_{}'.format (name, count), '{}_{}_LOC'.format (name, count))

    def parent_dynamic_fin_loc(self, *args):
        name = cmds.optionMenuGrp (self.name_menu, q=1, v=1)
        amount = cmds.intFieldGrp (self.spikes_amount, q=1, value1=1)
        per_spikes_amount = cmds.intFieldGrp (self.spikes_joints, q=1, value1=1)

        # Unparent everything
        created_locs = cmds.ls('{}_*_LOC'.format(name))
        x = 2
        for i  in range(amount):
            for j in range(per_spikes_amount-1):
                cmds.parent('{}_{}_LOC'.format(name, x), w=True)
                x += 1
            x += 1

        # Reparent cleanly
        y = 1
        for j in range(amount):
            for i in range (per_spikes_amount - 1):
                cmds.parent ('{}_{}_LOC'.format (name, y+1), '{}_{}_LOC'.format (name, y))
                y += 1
            y += 1

    def create_dynamic_fin(self, *args):
        name = cmds.optionMenuGrp (self.name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.name_menu, q=1, sl=1)
        amount = cmds.intFieldGrp (self.spikes_amount, q=1, value1=1)
        per_spikes_amount = cmds.intFieldGrp (self.spikes_joints, q=1, value1=1)
        distance = cmds.floatFieldGrp (self.spikes_distance, q=1, value1=1)
        height = cmds.floatFieldGrp (self.spikes_height, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spikes_span, q=1, value1=1)

        # Dynamic Fin Joints
        locs = cmds.ls ('{}_*_LOC'.format(name))
        exist_spike = cmds.ls ('{}_1_JNT'.format (name))
        sc = 0
        for loc in locs:
            if not exist_spike:
                par_loc = cmds.listRelatives (loc, p=1)
                # Joints
                cmds.select (cl=1)
                jnt = cmds.joint (n=loc.replace ('_LOC', '_JNT'), sc=sc)
                cnstr = cmds.parentConstraint (loc, jnt)
                cmds.delete (cnstr)
                cmds.makeIdentity (jnt, a=1, t=1, r=1, s=1)
                if par_loc:
                    par_jnt = par_loc[0].replace ('_LOC', '_JNT')
                    cmds.parent (jnt, par_jnt)

        # Reorient Dynamic Fin Joints
        joints = cmds.ls ('{}_*_JNT'.format (name))
        cmds.select (cl=1)
        for each in joints:
            cmds.select (each)
            mel.eval ("joint -e  -oj xyz -secondaryAxisOrient yup -ch -zso;")
        for i in range (amount):
            count = (i + 1) * per_spikes_amount
            cmds.setAttr ('{}_{}_JNT.jointOrientZ'.format (name, count), 0)

        # Dynamic Fin IK Handle
        for i in range (amount):
            count = (i + 1) * per_spikes_amount
            cmds.ikHandle (n='{}_{}_HDL'.format (name, count),
                           sj='{}_{}_JNT'.format (name, count - (per_spikes_amount - 1)),
                           ee='{}_{}_JNT'.format (name, count), sol='ikSplineSolver', ns= 4)
            cmds.select (cl=1)
            cmds.rename ('curve1', '{}_{}_DCRV'.format (name, count - (per_spikes_amount - 1)))
            cmds.rename ('effector1', '{}_{}_EFF'.format (name, count - (per_spikes_amount - 1)))
            cmds.rebuildCurve ('{}_{}_DCRV'.format (name, count - (per_spikes_amount - 1)), s=spans)
            dynamic_ik_curves.append('{}_{}_DCRV'.format (name, count - (per_spikes_amount - 1)))
            dynamic_handles.append('{}_{}_HDL'.format (name, count))

        # Mirror pelvic joints and ik spline
        x = 1
        y = 1
        if name_num == 3:
            pelvic_jnts = cmds.ls ('L_pelvic_*_JNT', assemblies=True)
            for each in pelvic_jnts:
                cmds.select(each)
                cmds.mirrorJoint(myz=True, mb=True, sr=('L_','R_'))
            for i in range (amount):
                count = (i + 1) * per_spikes_amount
                cmds.rename ('curve{}'.format (x), 'R_pelvic_{}_DCRV'.format (count - (per_spikes_amount - 1)))
                cmds.rebuildCurve ('R_pelvic_{}_DCRV'.format (count - (per_spikes_amount - 1)), s=spans)
                dynamic_ik_curves.append ('R_pelvic_{}_DCRV'.format (count - (per_spikes_amount - 1)))
                dynamic_handles.append ('R_pelvic_{}_HDL'.format (count))
                x += 1
            r_pelvic_jnts = cmds.ls('R_pelvic_*_JNT', assemblies=True)
            r_pelvic_jnts_grp = cmds.group(r_pelvic_jnts, n='R_pelvic_jnts')
            all_jnts.append (r_pelvic_jnts_grp)
        elif name_num == 4:
            pelvic_jnts = cmds.ls ('L_pelvicLG_*_JNT', assemblies=True)
            for each in pelvic_jnts:
                cmds.select(each)
                cmds.mirrorJoint(myz=True, mb=True, sr=('L_','R_'))
            for i in range (amount):
                count = (i + 1) * per_spikes_amount
                cmds.rename ('curve{}'.format (y), 'R_pelvicLG_{}_DCRV'.format (count - (per_spikes_amount - 1)))
                cmds.rebuildCurve ('R_pelvicLG_{}_DCRV'.format (count - (per_spikes_amount - 1)), s=spans)
                dynamic_ik_curves.append ('R_pelvicLG_{}_DCRV'.format (count - (per_spikes_amount - 1)))
                dynamic_handles.append ('R_pelvicLG_{}_HDL'.format (count))
                y += 1
            r_pelviclg_jnts = cmds.ls('R_pelvicLG_*_JNT', assemblies=True)
            r_pelviclg_jnts_grp = cmds.group(r_pelviclg_jnts, n='R_pelvicLG_jnts')
            all_jnts.append (r_pelviclg_jnts_grp)

        # Clean Outliner
        locators = cmds.ls('{}_*_LOC'.format(name), assemblies=True)
        loc_group = cmds.group(locators, n='{}_locs'.format(name))
        joints = cmds.ls('{}_*_JNT'.format(name), assemblies=True)
        jnts_grooup = cmds.group(joints, n='{}_jnts'.format(name))
        all_locs.append(loc_group)
        all_jnts.append(jnts_grooup)

        # Store amount of chain for each fin. To easy access when building cluster
        if name_num == 1:
            total_spikes.append(amount)
            total_name.append(name)
            dorsal += amount
        if name_num == 2:
            total_spikes.append(amount)
            total_name.append (name)
            last_dorsalLG.append(amount * per_spikes_amount)
            dorsal += amount
        if name_num == 3:
            total_spikes.append (amount)
            total_spikes.append (amount)
            total_name.append (name)
            total_name.append ('R_pelvic')
        if name_num == 4:
            total_spikes.append (amount)
            total_spikes.append (amount)
            total_name.append (name)
            total_name.append ('R_pelvicLG')
            last_L_pelvicLG.append(amount * per_spikes_amount)
            last_R_pelvicLG.append(amount * per_spikes_amount)
        if name_num == 5:
            total_spikes.append (amount)
            total_name.append (name)
        if name_num == 6:
            total_spikes.append (amount)
            total_name.append (name)
            last_analLG.append(amount * per_spikes_amount)

    def create_dynamic(self, *args):
        # create dynamic
        cmds.select (cl=1)
        dyn_ik_crv = cmds.ls("dorsal_*_DCRV", "dorsalLG_*_DCRV", "L_pelvic_*_DCRV", "R_pelvic_*_DCRV", "L_pelvicLG_*_DCRV", "R_pelvicLG_*_DCRV", "anal_*_DCRV", "analLG_*_DCRV")
        cmds.select(dyn_ik_crv)
        mel.eval ('DynCreateHairMenu MayaWindow|mainHairMenu;')
        mel.eval ('HairAssignHairSystemMenu MayaWindow|mainHairMenu|hairAssignHairSystemItem;')
        mel.eval ('assignNewHairSystem;')
        cmds.select (cl=1)

        # rename dynamic curve
        dynamic_crv = cmds.listRelatives ('hairSystem1OutputCurves')
        name_order = ["dorsal", "dorsalLG", "L_pelvic", "R_pelvic", "L_pelvicLG", "R_pelvicLG", "anal", "analLG"]
        x = 0
        y = 1
        z = 1
        for each in name_order:
            for i in range(total_spikes[x]):
                cmds.rename ('curve{}'.format(y), '{}_{}_HCRV'.format(each, z))
                y += 1
                z += 1
            z = 1
            x += 1

        # connect to have initial position
        dynamics = cmds.listRelatives ('hairSystem1OutputCurves', c=1)
        dyn_hdl = cmds.ls("dorsal_*_HDL", "dorsalLG_*_HDL", "L_pelvic_*_HDL", "R_pelvic_*_HDL", "L_pelvicLG_*_HDL", "R_pelvicLG_*_HDL", "anal_*_HDL", "analLG_*_HDL")
        i = 0
        for each in dyn_hdl:
            cmds.connectAttr (dynamics[i] + '.worldSpace[0]', each + '.inCurve', f=1)
            i += 1

        # Dynamic Parameters
        cmds.setAttr ("nucleus1.gravity", 0)
        cmds.setAttr ("hairSystemShape1.stretchResistance", 1000)
        cmds.setAttr ("hairSystemShape1.extraBendLinks", 2)
        cmds.setAttr ("hairSystemShape1.stiffnessScale[0].stiffnessScale_FloatValue", 0)
        cmds.setAttr ("hairSystemShape1.stiffnessScale[1].stiffnessScale_FloatValue", 0)
        cmds.setAttr ("hairSystemShape1.startCurveAttract", 1)
        cmds.setAttr ("hairSystemShape1.attractionScale[0].attractionScale_Interp", 3)
        cmds.setAttr ("hairSystemShape1.attractionScale[0].attractionScale_FloatValue", 0.8)
        cmds.setAttr ("hairSystemShape1.attractionScale[1].attractionScale_FloatValue", 0)
        cmds.setAttr ("hairSystemShape1.attractionScale[2].attractionScale_Position", 0.434783)
        cmds.setAttr ("hairSystemShape1.attractionScale[2].attractionScale_FloatValue", 0.58)
        cmds.setAttr ("hairSystemShape1.attractionScale[2].attractionScale_Interp", 3)
        cmds.setAttr ("hairSystemShape1.mass", 0.4)
        cmds.setAttr ("hairSystemShape1.drag", 0)
        cmds.setAttr ("hairSystemShape1.tangentialDrag", 0.2)
        cmds.setAttr ("hairSystemShape1.motionDrag", 0.4)
        cmds.setAttr ("hairSystemShape1.damp", 2)
        cmds.setAttr ("hairSystemShape1.dynamicsWeight", 0.1)

        # Clean outliner
        cmds.group (all_locs, n='dynamic_locs')
        cmds.group (all_jnts, n='dynamic_jnts')
        cmds.group (dyn_hdl, n='dynamic_hdl')


    def create_auto_cluster(self, *arg):
        name = cmds.optionMenuGrp (self.name_menu, q=1, v=1)
        amount = cmds.intFieldGrp (self.spikes_amount, q=1, value1=1)
        per_spikes_amount = cmds.intFieldGrp (self.spikes_joints, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spikes_span, q=1, value1=1)
        per_cv = cmds.intFieldGrp( self.spikes_cluster_per_CV, q=1, value1=1)

        # create clusters
        total_cv = spans + 3
        x = 0
        y = 1
        z = math.ceil(total_cv / per_cv)
        dynamic_curves = cmds.listRelatives ('hairSystem1OutputCurves', c=1)
        all_clusters = []
        if per_cv == 1:
            for each in dynamic_curves:
                for j in range (total_cv):
                    cmds.selectType(cv=True)
                    cmds.select (each + '.cv[{}]'.format(x))
                    clusters = cmds.cluster(n=each + '_{}_CLT'.format(y))[1]
                    all_clusters.append(clusters)
                    y += 1
                    x += 1
                x = 0
        else:
            for each in dynamic_curves:
                for j in range(int(z)+1):
                    cmds.selectType (cv=True)
                    cmds.select (each + '.cv[{}:{}]'.format (x, x + (per_cv-1)))
                    clusters = cmds.cluster(n=each + '_{}_CLT'.format(y))[1]
                    all_clusters.append (clusters)
                    x += per_cv
                    y += 1
                x = 0

        # control and offset group
        for i in all_clusters:
            control_name = i.replace ("_CLTHandle", "_CON")
            ctrl = cmds.circle (nr=(1, 0, 0), r=1, n=control_name)[0]
            sdk = cmds.group (ctrl, n=ctrl + '_SDK')
            open_close = cmds.group(ctrl, n=ctrl + '_OC')
            offset = cmds.group (sdk, n=ctrl + '_OFFSET')
            cmds.parentConstraint (i, offset, mo=0)
            cmds.delete (cmds.parentConstraint (i, offset))            
            dynamic_offset_groups.append(offset)
            dynamic_sdk_groups.append(sdk)
            dynamic_oc_groups.append(open_close)

        # Reorient offset group for set driven keys
        dorsal_offset = cmds.ls ('dorsal_*_HCRV_*_CON_OFFSET')
        dorsal_lg_offset = cmds.ls ('dorsalLG_*_HCRV_*_CON_OFFSET')
        l_pelvic_offset = cmds.ls ('L_pelvic_*_HCRV_*_CON_OFFSET')
        r_pelvic_offset = cmds.ls ('R_pelvic_*_HCRV_*_CON_OFFSET')
        l_pelvic_lg_offset = cmds.ls ('L_pelvicLG_*_HCRV_*_CON_OFFSET')
        r_pelvic_lg_offset = cmds.ls ('R_pelvicLG_*_HCRV_*_CON_OFFSET')
        anal_offset = cmds.ls ('anal_*_HCRV_*_CON_OFFSET')
        anal_lg_offset = cmds.ls ('analLG_*_HCRV_*_CON_OFFSET')
        offsets = cmds.group(dorsal_offset, dorsal_lg_offset, l_pelvic_offset,r_pelvic_offset,l_pelvic_lg_offset,r_pelvic_lg_offset,anal_offset,anal_lg_offset, n='offset_grp')
        offset_groups=cmds.listRelatives(offsets, c=1)
        x = 0
        y = 0
        if per_cv == 1:
            for each in total_spikes:
                set_amount = int (each)
                total_amount = set_amount * total_cv
                for i in range (total_amount):
                    cmds.matchTransform (offset_groups[x], '{}_1_JNT'.format (total_name[y]), rot=True)
                    x += 1
                y += 1
        else:
            for each in total_spikes:
                set_amount = int (each)
                total_amount = set_amount * (int(z)+1)
                for i in range (total_amount):
                    cmds.matchTransform (offset_groups[x], '{}_1_JNT'.format (total_name[y]), rot=True)
                    x += 1
                y += 1

        con_list01 = cmds.listRelatives ('dorsal_*_CON', s=1)
        for each in con_list01:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        con_list02 = cmds.listRelatives ('dorsalLG_*_CON', s=1)
        for each in con_list02:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        con_list03 = cmds.listRelatives ('*_pelvic_*_CON', s=1)
        for each in con_list03:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        con_list04 = cmds.listRelatives ('*_pelvicLG_*_CON', s=1)
        for each in con_list04:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        con_list05 = cmds.listRelatives ('anal_*_CON', s=1)
        for each in con_list05:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        con_list06 = cmds.listRelatives ('analLG_*_CON', s=1)
        for each in con_list06:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        # create cluster trees
        if per_cv == 1:
            x = 1
            for each in total_spikes:
                set_amount = int (each)
                for i in range(set_amount):
                    for j in range(int(z-1)):
                        cmds.parent('*_HCRV_{}_CON_OFFSET'.format(x+1), '*_HCRV_{}_CON'.format(x))
                        x += 1
                    x += 1
        else:
            x = 1
            for each in total_spikes:
                set_amount = int (each)
                for i in range (set_amount):
                    for j in range (int (z)):
                        cmds.parent ('*_HCRV_{}_CON_OFFSET'.format (x + 1), '*_HCRV_{}_CON'.format (x))
                        x += 1
                    x += 1

        # Parent cluster back under controlers
        dyn_hdl = cmds.ls("*_HCRV_*_CLTHandle")
        dyn_con = cmds.ls("*_HCRV_*_CON")

        z = 0
        for i in dyn_con:
            cmds.parent(dyn_hdl[z], i)
            z += 1


    def create_dynamic_master_control(self, *args):
        name = cmds.optionMenuGrp (self.name_menu, q=1, v=1)
        amount = cmds.intFieldGrp (self.spikes_amount, q=1, value1=1)
        per_spikes_amount = cmds.intFieldGrp (self.spikes_joints, q=1, value1=1)
        distance = cmds.floatFieldGrp (self.spikes_distance, q=1, value1=1)
        height = cmds.floatFieldGrp (self.spikes_height, q=1, value1=1)
        spans = cmds.intFieldGrp (self.spikes_span, q=1, value1=1)
        per_cv = cmds.intFieldGrp( self.spikes_cluster_per_CV, q=1, value1=1)

        # Naming of master control
        master_name = ["dorsal", "L_pelvic", "R_pelvic", "anal"]

        # master control icon
        master_cons = []
        for i in master_name:
            cir = cmds.circle (n='{}_master_CON'.format(i), d=3, ch=0, nry=1, nrx=0, nrz=0, r=0.5)
            cir2 = cmds.circle (n='{}_master02_CON'.format(i), d=3, ch=0, nry=0, nrx=0, nrz=0, r=0.5)
            cir3 = cmds.circle (n='{}_master03_CON'.format(i), d=3, ch=0, nry=0, nrx=1, nrz=0, r=0.5)
            shape_node2 = cmds.listRelatives (cir2, s=1)
            shape_node3 = cmds.listRelatives (cir3, s=1)
            cmds.select (cl=1)
            cmds.select (shape_node2, shape_node3, cir)
            mel.eval ('parent-r-s;')
            cmds.delete (cir2, cir3)
            cir_shape = cmds.listRelatives (cir, s=1)
            for each in cir_shape:
                cmds.setAttr (each + '.lineWidth', 2)
                cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
                cmds.setAttr (each + '.overrideColor', 9)
            cmds.makeIdentity (cir, a=1, t=1, r=1, s=1)
            grp = cmds.group (n='{}_master_OFFSET'.format(i), em=1, w=1)
            cmds.parent (cir, grp)
            for each in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'visibility']:
                cmds.setAttr ('{}_master_CON'.format (i) + '.' + each, l=1, k=0, cb=0, ch=0)
            master_cons.append('{}_master_CON'.format(i))
        
        # Position the master icon
        cmds.matchTransform ('dorsal_master_OFFSET', 'dorsalLG_{}_LOC'.format (last_dorsalLG[0]), pos=True)
        cmds.matchTransform ('L_pelvic_master_OFFSET', 'L_pelvicLG_{}_LOC'.format (last_L_pelvicLG[0]), pos=True)
        cmds.matchTransform ('R_pelvic_master_OFFSET', 'R_pelvicLG_{}_JNT'.format (last_L_pelvicLG[0]), pos=True)
        cmds.matchTransform ('anal_master_OFFSET', 'analLG_{}_LOC'.format (last_analLG[0]), pos=True)

        # Set Driven Keys for master control:
        dorsal_sdk = cmds.ls ('dorsal*_SDK')
        L_pelvic_sdk = cmds.ls('L_pelvic*_SDK')
        R_pelvic_sdk = cmds.ls ('R_pelvic*_SDK')
        anal_sdk = cmds.ls ('anal*_SDK')

        for each in dorsal_sdk:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='dorsal_master_CON.rotateX', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='dorsal_master_CON.rotateX', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='dorsal_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='dorsal_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")
        for each in L_pelvic_sdk:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pelvic_master_CON.rotateX', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pelvic_master_CON.rotateX', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='L_pelvic_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='L_pelvic_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")
        for each in R_pelvic_sdk:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pelvic_master_CON.rotateX', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pelvic_master_CON.rotateX', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='R_pelvic_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='R_pelvic_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")
        for each in anal_sdk:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='anal_master_CON.rotateX', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='anal_master_CON.rotateX', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='anal_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='anal_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")

        # Set Driven Key for open and close:
        dorsal_oc = cmds.ls ('dorsal*_OC')
        L_pelvic_oc = cmds.ls ('L_pelvic*_OC')
        R_pelvic_oc = cmds.ls ('R_pelvic*_OC')
        anal_oc = cmds.ls ('anal*_OC')

        for each in dorsal_oc:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='dorsal_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='dorsal_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
        for each in L_pelvic_oc:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pelvic_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pelvic_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
        for each in R_pelvic_oc:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pelvic_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pelvic_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
        for each in anal_oc:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='anal_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='anal_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")

        # Selection Set for fixing open and close
        cmds.select(cl=1)
        cmds.select(dorsal_oc)
        cmds.sets (n='dorsal_OC')
        cmds.select (cl=1)
        cmds.select (L_pelvic_oc)
        cmds.sets (n='L_pelvic_OC')
        cmds.select (cl=1)
        cmds.select (R_pelvic_oc)
        cmds.sets (n='R_pelvic_OC')
        cmds.select (cl=1)
        cmds.select (anal_oc)
        cmds.sets (n='anal_OC')
        cmds.select (cl=1)

        # Create dynamic_master_con
        dynamic_con = cmds.curve (d=3, n='dynamic_CON', p =[(0, 0, 1), (0, 0.555556, 0.555556), ( 0, 1.666667, -0.333333),  (0, -0.666667, 0.333333), (0, 0.444444, -0.555556), (0, 1, -1)] )
        cmds.group(dynamic_con, n='dynamic_CON_OFFSET')
        cmds.setAttr (dynamic_con + '.lineWidth', 2)
        cmds.setAttr (dynamic_con + '.overrideEnabled', 1, e=1, q=1)
        cmds.setAttr (dynamic_con + '.overrideColor', 9)
        cmds.makeIdentity (dynamic_con, a=1, t=1, r=1, s=1)
        for each in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility']:
            cmds.setAttr ('dynamic_CON' + '.' + each, l=1, k=0, cb=0, ch=0)
        cmds.addAttr (dynamic_con, at='bool', ln='dynamicEnable', nn="Dynamic Enable")
        cmds.setAttr (dynamic_con + '.dynamicEnable', e=1, k=1)
        cmds.addAttr (dynamic_con, at='long', ln='startFrame', nn="Start Frame", dv=1)
        cmds.setAttr (dynamic_con + '.startFrame', e=1, k=1)
        cmds.addAttr (dynamic_con, at='float', ln='drag', nn="Drag")
        cmds.setAttr (dynamic_con + '.drag', e=1, k=1)
        cmds.addAttr (dynamic_con, at='double', ln='follow', nn="Follow", min=0, max=1, dv=1)
        cmds.setAttr (dynamic_con + '.follow', e=1, k=1)
        cmds.addAttr (dynamic_con, at='bool', ln='playbackEnable', nn="Playback Enable")
        cmds.setAttr (dynamic_con + '.playbackEnable', e=1, k=1)
        cmds.addAttr (dynamic_con, at='float', ln='turbulenceIntensity', nn="Turbulence Intensity")
        cmds.setAttr (dynamic_con + '.turbulenceIntensity', e=1, k=1)
        cmds.addAttr (dynamic_con, at='float', ln='turbulenceFrequency', nn="Turbulence Frequency")
        cmds.setAttr (dynamic_con + '.turbulenceFrequency', e=1, k=1)
        cmds.addAttr (dynamic_con, at='float', ln='turbulenceSpeed', nn="Turbulence Speed")
        cmds.setAttr (dynamic_con + '.turbulenceSpeed', e=1, k=1)

        # connect master control attributes
        cmds.connectAttr (dynamic_con + '.dynamicEnable', 'nucleus1.enable', f=1)
        cmds.connectAttr (dynamic_con + '.startFrame', 'hairSystemShape1.startFrame', f=1)
        cmds.connectAttr (dynamic_con + '.drag', 'hairSystemShape1.drag', f=1)
        cmds.connectAttr (dynamic_con + '.follow', 'hairSystemShape1.startCurveAttract', f=1)
        cmds.connectAttr (dynamic_con + '.playbackEnable', 'hairSystemShape1.disableFollicleAnim', f=1)
        cmds.connectAttr (dynamic_con + '.turbulenceIntensity', 'hairSystemShape1.turbulenceStrength', f=1)
        cmds.connectAttr (dynamic_con + '.turbulenceFrequency', 'hairSystemShape1.turbulenceFrequency', f=1)
        cmds.connectAttr (dynamic_con + '.turbulenceSpeed', 'hairSystemShape1.turbulenceSpeed', f=1)

    def dynamic_clean(self,*args):
        # Organize the outliner
        selection = cmds.ls ('dynamic_locs', 'dynamic_jnts', 'dynamic_hdl', '*_CLTHandle')
        for each in selection:
            cmds.setAttr (each + '.visibility', 0)
        con_offset_groups = cmds.ls ('*_HCRV_*_CON_OFFSET', assemblies=True)
        cmds.group (con_offset_groups, n='controls_GRP')
        master_con_offset_groups = cmds.ls ('*_master_OFFSET', assemblies=True)
        cmds.group (master_con_offset_groups, n='master_con_GRP')
        do_not_touch = cmds.ls ('hairSystem1', 'nucleus1', 'hairSystem1Follicles', 'hairSystem1OutputCurves', 'dynamic_hdl')
        cmds.group (do_not_touch, n='DO_NOT_TOUCH_GRP')
        cmds.setAttr ('DO_NOT_TOUCH_GRP.visibility', 0)
        dynamic_sys = cmds.ls ('DO_NOT_TOUCH_GRP', 'dynamic_CON_OFFSET', 'controls_GRP', 'master_con_GRP')
        cmds.group (dynamic_sys, n='dynamic_system')

        # bind joints set for skinning
        dynamic_joints = cmds.listRelatives ('dynamic_jnts', ad=True, typ='joint')
        bind_jnt.append(dynamic_joints)

    def create_ribbon_locs(self,*args):
        name = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, sl=1)
        chain_amount = cmds.intFieldGrp (self.ribbon_chain_amount, q=1, value1=1)
        total_con_select = cmds.radioButtonGrp (self.ribbon_cons_total , q=1, sl=1)

        total_con = 0
        if total_con_select == 1:
            total_con += 3
        elif total_con_select == 2:
            total_con += 5
        elif total_con_select == 3:
            total_con += 9

        if name_num == 1:
            # Create pectorial ribbon locs
            for j in range (total_con):
                count = j + 1
                loc = cmds.spaceLocator (n='{}_LOC_{}'.format (name, count))[0]
                cmds.setAttr (loc + '.translateX', count * 2)
                for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                    cmds.setAttr (loc + '.' + each, .5)
                cmds.makeIdentity (loc, a=1, t=1, r=1, s=1)
        elif name_num ==2:
            # Create tail ribbon locs
            for i in range (total_con):
                count = i + 1
                loc = cmds.spaceLocator (n='{}_LOC_{}'.format (name,count))[0]
                cmds.setAttr (loc + '.translateZ', count * (-2))
                for each in ['localScaleX', 'localScaleY', 'localScaleZ']:
                    cmds.setAttr (loc + '.' + each, .5)
                cmds.makeIdentity (loc, a=1, t=1, r=1, s=1)

        # Parent to first loc of the tre to edit the locators easier
        for i in range (total_con-1):
            count = i + 2
            cmds.parent ('{}_LOC_{}'.format (name, count), '{}_LOC_1'.format (name))


        # Create multiple chains of locator
        y = 0
        for i in range (chain_amount - 1):
            copy = cmds.duplicate ('{}_LOC_1'.format (name), rc=1)[0]
            cmds.setAttr (copy + '.ty', y - 1)
            y -= 1

        # Rename
        for i in range (chain_amount * total_con):
            count = i + 1
            cmds.rename ('{}_LOC_{}'.format (name, count), '{}_{}_LOC'.format (name, count))

        # Point Constraint
        x = 1
        y = 2
        if total_con_select == 1:
            for i in range (chain_amount):
                for j in range (total_con - 2):
                    cmds.pointConstraint ('{}_{}_LOC'.format (name, x), '{}_{}_LOC'.format (name, x + 2),
                                          '{}_{}_LOC'.format (name, y))
                    y += 1
                x += 3
                y += 2
        elif total_con_select == 2:
            z = 0.75
            for i in range (chain_amount):
                for j in range (total_con - 2):
                    cmds.pointConstraint ('{}_{}_LOC'.format (name, x), '{}_{}_LOC'.format (name, x + 4),
                                          '{}_{}_LOC'.format (name, y))
                    cmds.setAttr ('{}_{}_LOC_pointConstraint1'.format (name, y) + '.{}_{}_LOCW0'.format (name, x), z)
                    cmds.setAttr ('{}_{}_LOC_pointConstraint1'.format (name, y) + '.{}_{}_LOCW1'.format (name, x + 4),
                                  1 - z)
                    y += 1
                    z -= 0.25
                z = 0.75
                x += 5
                y += 2
        elif total_con_select == 3:
            z = 0.875
            for i in range (chain_amount):
                for j in range (total_con - 2):
                    cmds.pointConstraint ('{}_{}_LOC'.format (name, x), '{}_{}_LOC'.format (name, x + 8),
                                          '{}_{}_LOC'.format (name, y))
                    cmds.setAttr ('{}_{}_LOC_pointConstraint1'.format (name, y) + '.{}_{}_LOCW0'.format (name, x), z)
                    cmds.setAttr ('{}_{}_LOC_pointConstraint1'.format (name, y) + '.{}_{}_LOCW1'.format (name, x + 8),
                                  1 - z)
                    y += 1
                    z -= 0.125
                z = 0.875
                x += 9
                y += 2


    def parent_ribbon_loc(self,*args):
        name = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, sl=1)
        chain_amount = cmds.intFieldGrp (self.ribbon_chain_amount, q=1, value1=1)
        total_con_select = cmds.radioButtonGrp (self.ribbon_cons_total , q=1, sl=1)

        total_con = 0
        if total_con_select == 1:
            total_con += 3
        elif total_con_select == 2:
            total_con += 5
        elif total_con_select == 3:
            total_con += 9

        # Remove point Constraint
        point_cnst = cmds.ls ('{}_*_LOC_pointConstraint1'.format (name))
        for each in point_cnst:
            cmds.select (cl=1)
            cmds.select (each)
            cmds.delete ()

        # Unparent everything
        created_locs = cmds.ls ('{}_*_LOC'.format (name))
        x = 2
        for i in range (chain_amount):
            for j in range (total_con - 1):
                cmds.parent ('{}_{}_LOC'.format (name, x), w=True)
                x += 1
            x += 1

        # Reparent cleanly
        y = 1
        for j in range (chain_amount):
            for i in range (total_con - 1):
                cmds.parent ('{}_{}_LOC'.format (name, y + 1), '{}_{}_LOC'.format (name, y))
                y += 1
            y += 1

    def create_ribbon_joint(self,*args):
        name = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, sl=1)
        chain_amount = cmds.intFieldGrp (self.ribbon_chain_amount, q=1, value1=1)
        total_con_select = cmds.radioButtonGrp (self.ribbon_cons_total , q=1, sl=1)

        global l_pect
        global tail

        total_con = 0
        if total_con_select == 1:
            total_con += 3
        elif total_con_select == 2:
            total_con += 5
        elif total_con_select == 3:
            total_con += 9

        # Ribbon Fin Joints
        locs = cmds.ls ('{}_*_LOC'.format (name))
        exist_spike = cmds.ls ('{}_1_JNT'.format (name))
        sc = 0
        for loc in locs:
            if not exist_spike:
                par_loc = cmds.listRelatives (loc, p=1)
                # Joints
                cmds.select (cl=1)
                jnt = cmds.joint (n=loc.replace ('_LOC', '_JNT'), sc=sc, rad=2)
                cnstr = cmds.parentConstraint (loc, jnt)
                cmds.delete (cnstr)
                cmds.makeIdentity (jnt, a=1, t=1, r=1, s=1)
                if par_loc:
                    par_jnt = par_loc[0].replace ('_LOC', '_JNT')
                    cmds.parent (jnt, par_jnt)
                con_jnt.append(jnt)

        # Reorient Dynamic Fin Joints
        joints = cmds.ls ('{}_*_JNT'.format (name))
        cmds.select (cl=1)
        for each in joints:
            cmds.select (each)
            mel.eval ("joint -e  -oj xyz -secondaryAxisOrient yup -ch -zso;")
        for i in range (chain_amount):
            count = (i + 1) * total_con
            cmds.setAttr ('{}_{}_JNT.jointOrientX'.format (name, count), 0)

        # Mirror pectorial joints
        if name_num == 1:
            pect_jnts = cmds.ls ('L_pect_*_JNT', assemblies=True)
            for each in pect_jnts:
                cmds.select (each)
                cmds.mirrorJoint (myz=True, mb=True, sr=('L_', 'R_'))

        # amount of chain information stored
        if name_num == 1:
            l_pect += chain_amount
            rb_selection.append(total_con)
            rb_selection.append (total_con)
            rb_chain.append(l_pect)
            rb_chain.append (l_pect)
        if name_num == 2:
            tail += chain_amount
            rb_selection.append(total_con)
            rb_chain.append (tail)

    def create_base_ribbon(self,*args):
        name = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, sl=1)
        chain_amount = cmds.intFieldGrp (self.ribbon_chain_amount, q=1, value1=1)
        total_con_select = cmds.radioButtonGrp (self.ribbon_cons_total, q=1, sl=1)

        # Conversion
        total_con = 0
        if total_con_select == 1:
            total_con += 3
        elif total_con_select == 2:
            total_con += 5
        elif total_con_select == 3:
            total_con += 9

        pect_position = []
        tail_position = []
        x = 0
        y = 0

        pect_list = cmds.ls ('L_pect_*_JNT', 'R_pect_*_JNT')
        for each in pect_list:
            position = cmds.joint (each, query=True, p=1)
            pect_position.append (position)

        tail_list = cmds.ls ('tail_*_JNT')
        for each in tail_list:
            position02 = cmds.joint (each, query=True, p=1)
            tail_position.append (position02)

        # Curves for pectorial fins
        range_num = l_pect * 2
        if rb_selection[0] == 3:
            for i in range (range_num):
                cmds.curve (p=[pect_position[x], pect_position[x + 1], pect_position[x + 2]], d=1)
                x += 3
        elif rb_selection[0] == 5:
            for i in range (range_num):
                cmds.curve (p=[pect_position[x], pect_position[x + 1], pect_position[x + 2], pect_position[x + 3],
                               pect_position[x + 4]], d=1)
                x += 5
        elif rb_selection[0] == 9:
            for i in range (range_num):
                cmds.curve (p=[pect_position[x], pect_position[x + 1], pect_position[x + 2], pect_position[x + 3],
                               pect_position[x + 4], pect_position[x + 5], pect_position[x + 6], pect_position[x + 7],
                               pect_position[x + 8]], d=1)
                x += 9

        # Curves for tail
        if rb_selection[2] == 3:
            for i in range (tail):
                cmds.curve (p=[tail_position[y], tail_position[y + 1], tail_position[y + 2]], d=1)
                y += 3
        elif rb_selection[2] == 5:
            for i in range (tail):
                cmds.curve (p=[tail_position[y], tail_position[y + 1], tail_position[y + 2], tail_position[y + 3],
                               tail_position[y + 4]], d=1)
                y += 5
        elif rb_selection[2] == 9:
            for i in range (tail):
                cmds.curve (p=[tail_position[y], tail_position[y + 1], tail_position[y + 2], tail_position[y + 3],
                               tail_position[y + 4], tail_position[y + 5], tail_position[y + 6], tail_position[y + 7],
                               tail_position[y + 8]], d=1)
                y += 9

        # Rename curves
        rb_name = ['L_pect', 'R_pect', 'tail']
        x = 0
        y = 1
        z = 1
        for i in rb_name:
            for j in range (rb_chain[x]):
                cmds.rename ('curve{}'.format (y), '{}_{}_RCRV'.format (i, z))
                y += 1
                z += 1
            z = 1
            x += 1

        # Create base ribbon and rebuilt it
        selection01 = cmds.ls ('L_pect_*_RCRV')
        l_pect_baserb = cmds.loft (selection01, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=True,
                                   n='L_pect_base_RB')
        cmds.rebuildSurface (l_pect_baserb)

        selection02 = cmds.ls ('R_pect_*_RCRV')
        r_pect_baserb = cmds.loft (selection02, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=True,
                                   n='R_pect_base_RB')
        cmds.rebuildSurface (r_pect_baserb)

        selection03 = cmds.ls ('tail_*_RCRV')
        tail_baserb = cmds.loft (selection03, ch=1, u=1, c=0, ar=1, d=3, ss=1, rn=0, po=0, rsn=True,
                                 n='tail_base_RB')
        cmds.rebuildSurface (tail_baserb)

    def create_ribbon(self,*args):
        mel.eval ('CreateHairOptions;')

    def organize_ribbon(self,*args):
        name = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, v=1)
        name_num = cmds.optionMenuGrp (self.ribbon_name_menu, q=1, sl=1)
        chain_amount = cmds.intFieldGrp (self.ribbon_chain_amount, q=1, value1=1)
        total_con_select = cmds.radioButtonGrp (self.ribbon_cons_total, q=1, sl=1)

        global con_jnt

        # delete non used node
        cmds.delete ('pfxHair1', 'hairSystem2')
        folli_crv = cmds.ls ('curve*')
        cmds.delete (folli_crv)

        # Create bind joints
        folli = cmds.ls ('*_RBF*', typ='transform')
        for each in folli:
            cmds.select (each)
            cmds.joint (n=each.replace ('RB', 'bindJNT_'), rad=0.5)
            cmds.select (cl=1)

        # Put ribbon bind joints in bindJNT selection set
        bind_jnt = []
        rb_bind_jnt = cmds.ls ('*_bindJNT_*')
        for each in rb_bind_jnt:
            bind_jnt.append (each)
        cmds.select (cl=1)

        # duplicate base ribbon for sine deformer
        base_rb = cmds.ls ('*_base_RB')
        bs_rb = []
        for i in base_rb:
            name = i.replace ('base_RB', 'def_RB')
            copy = cmds.duplicate (i, n=name)
            for each in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                cmds.setAttr (name + '.' + each, l=0)
            bs_rb += copy

        # blenshape for ribbon
        x = 0
        for j in bs_rb:
            cmds.blendShape (j, base_rb[x])
            x += 1

        # bind skin con jnt to ribbon
        l_pect_jnt = cmds.ls ('L_pect_*_JNT')
        r_pect_jnt = cmds.ls ('R_pect_*_JNT')
        tail_jnt = cmds.ls ('tail_*_JNT')
        cmds.skinCluster (l_pect_jnt, 'L_pect_base_RB', tsb=True)
        cmds.skinCluster (r_pect_jnt, 'R_pect_base_RB', tsb=True)
        cmds.skinCluster (tail_jnt, 'tail_base_RB', tsb=True)

        # Con joint selection set
        con_jnt = l_pect_jnt + r_pect_jnt + tail_jnt
        cmds.select (cl=1)
        cmds.select (con_jnt)
        cmds.sets (n='con_jnt')
        cmds.select (cl=1)

        # Create controls
        for i in con_jnt:
            control_name = i.replace ("_JNT", "_CON")
            ctrl = cmds.circle (nr=(1, 0, 0), r=1, n=control_name)[0]
            offset = cmds.group (ctrl, n=ctrl + '_OFFSET')
            cmds.parentConstraint (i, offset, mo=0)
            cmds.delete (cmds.parentConstraint (i, offset))

        # change con width and color
        l_pect_shape = cmds.listRelatives ('L_pect_*_CON', s=1)
        r_pect_shape = cmds.listRelatives ('R_pect_*_CON', s=1)
        tail_shape = cmds.listRelatives ('tail_*_CON', s=1)
        shape = l_pect_shape + r_pect_shape + tail_shape
        for each in shape:
            cmds.setAttr (each + '.lineWidth', 2)
            cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
            cmds.setAttr (each + '.overrideColor', 18)

        # Make control tree
        x = 1
        for i in range (l_pect):
            for j in range (rb_selection[0] - 1):
                cmds.parent ('L_pect_{}_CON_OFFSET'.format (x + 1), 'L_pect_{}_CON'.format (x))
                cmds.parent ('R_pect_{}_CON_OFFSET'.format (x + 1), 'R_pect_{}_CON'.format (x))
                x += 1
            x += 1
        x = 1
        for i in range (tail):
            for j in range (rb_selection[2] - 1):
                cmds.parent ('tail_{}_CON_OFFSET'.format (x + 1), 'tail_{}_CON'.format (x))
                x += 1
            x += 1

        # Parent control joints under control tree
        l_pect_offset = cmds.ls ('L_pect_*_CON_OFFSET')
        set_amount01 = len (l_pect_offset)
        for i in range (set_amount01):
            i += 1
            cmds.parent ('L_pect_{}_JNT'.format (i), 'L_pect_{}_CON'.format (i))

        r_pect_offset = cmds.ls ('R_pect_*_CON_OFFSET')
        set_amount02 = len (r_pect_offset)
        for i in range (set_amount02):
            i += 1
            cmds.parent ('R_pect_{}_JNT'.format (i), 'R_pect_{}_CON'.format (i))

        tail_offset = cmds.ls ('tail_*_CON_OFFSET')
        set_amount03 = len (tail_offset)
        for i in range (set_amount03):
            i += 1
            cmds.parent ('tail_{}_JNT'.format (i), 'tail_{}_CON'.format (i))

        # Clean Outliner
        l_pect_loc = cmds.ls('L_pect_*_LOC', assemblies=True)
        cmds.group(l_pect_loc, n='L_pect_locs')
        tail_loc = cmds.ls('tail_*_LOC', assemblies=True)
        cmds.group(tail_loc, n='tail_locs')
        cmds.group('L_pect_locs', 'tail_locs', n='ribbon_locs')
        cmds.setAttr('ribbon_locs.visibility', 0)
        cmds.group(base_rb, n='base_ribbon_GRP')
        cmds.group(bs_rb, n='deform_ribbon_GRP')
        rb_curves = cmds.ls('*_RCRV')
        cmds.group(rb_curves, n='Ribbon_Curves_GRP')
        cmds.select(cl=1)
        cmds.select(bind_jnt)
        cmds.sets (n='bindJNT')
        cmds.select (cl=1)

    def create_ribbon_sine(self,*args):
        mel.eval('SineOptions;')

    def sine_info(self, *args):
        sine_handle_amount = cmds.intFieldGrp (self.sine_amount, q=1, v1=1)

        # Store amount of sine handle for each fin. For naming and connecting attributes. Put twice for the pectorial fin because there is L and R
        sine_number.append(sine_handle_amount)

    def connect_ribbon_attributes(self,*args):
        names = ['L_pect', 'R_pect', 'tail']
        global sine_number
        # Make master control
        master_con = []
        for i in names:
            cir = cmds.circle (n='{}_master_CON'.format (i), d=3, ch=0, nry=1, nrx=0, nrz=0, r=0.5)
            cir2 = cmds.circle (n='{}_master02_CON'.format (i), d=3, ch=0, nry=0, nrx=0, nrz=0, r=0.5)
            cir3 = cmds.circle (n='{}_master03_CON'.format (i), d=3, ch=0, nry=0, nrx=1, nrz=0, r=0.5)
            shape_node2 = cmds.listRelatives (cir2, s=1)
            shape_node3 = cmds.listRelatives (cir3, s=1)
            cmds.select (cl=1)
            cmds.select (shape_node2, shape_node3, cir)
            mel.eval ('parent-r-s;')
            cmds.delete (cir2, cir3)
            cir_shape = cmds.listRelatives (cir, s=1)
            for each in cir_shape:
                cmds.setAttr (each + '.lineWidth', 2)
                cmds.setAttr (each + '.overrideEnabled', 1, e=1, q=1)
                cmds.setAttr (each + '.overrideColor', 9)
            cmds.makeIdentity (cir, a=1, t=1, r=1, s=1)
            grp = cmds.group (n='{}_master_OFFSET'.format (i), em=1, w=1)
            cmds.parent (cir, grp)
            for each in ['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'visibility']:
                cmds.setAttr ('{}_master_CON'.format (i) + '.' + each, l=1, k=0, cb=0, ch=0)
            master_con += cir

        # Set master control attributes
        for i in names:
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='amplitude', nn='Amplitude')
            cmds.setAttr ('{}_master_CON'.format (i) + '.amplitude', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='wavelength', nn='Wavelength')
            cmds.setAttr ('{}_master_CON'.format (i) + '.wavelength', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='Offset1', nn='Offset1')
            cmds.setAttr ('{}_master_CON'.format (i) + '.Offset1', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='Offset2', nn='Offset2')
            cmds.setAttr ('{}_master_CON'.format (i) + '.Offset2', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='Offset3', nn='Offset3')
            cmds.setAttr ('{}_master_CON'.format (i) + '.Offset3', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='Offset4', nn='Offset4')
            cmds.setAttr ('{}_master_CON'.format (i) + '.Offset4', e=1, k=1)
            cmds.addAttr ('{}_master_CON'.format (i), at='float', ln='Offset5', nn='Offset5')
            cmds.setAttr ('{}_master_CON'.format (i) + '.Offset5', e=1, k=1)

        # Rename sine handles
        sine_hdl = cmds.ls ('sine*Handle')
        z = 0
        t = 1
        x = 0
        for each in names:
            for j in range (sine_number[x]):
                cmds.rename (sine_hdl[z], '{}_{}_SINE'.format (each, t))
                z += 1
                t += 1
            t = 1
            x += 1

        # Connect attributes of master control to sine noneLinear
        sine = cmds.ls ('sine*', typ='nonLinear')
        x = 1
        y = 1
        z = 0
        for each in master_con:
            for i in range (sine_number[z]):
                cmds.connectAttr (each + '.amplitude', 'sine{}.amplitude'.format (x), f=1)
                cmds.connectAttr (each + '.wavelength', 'sine{}.wavelength'.format (x), f=1)
                x += 1
            z += 1

        # Create SDK group for root joint of ribbon system to open and close
        con_selection = cmds.ls("L_pect_*_CON", "R_pect_*_CON", "tail_*_CON")
        con_selection.remove("L_pect_master_CON")
        con_selection.remove("R_pect_master_CON")
        con_selection.remove("tail_master_CON")
        for i in con_selection:
            sdk_grp = cmds.group(i, n=i.replace("_CON", "_SDK"))

        # Put Pivot of sdk group same as the joint and the controler
        sdk_selection = cmds.ls("L_pect_*_SDK", "R_pect_*_SDK", "tail_*_SDK")
        x = 0
        for i in sdk_selection:
            cmds.matchTransform (i, con_selection[x], piv=True)
            x += 1

        # Set Driven Key with master con for bend in Y axis
        l_pect_sdk = cmds.ls("L_pect_*_SDK")
        for each in l_pect_sdk:
            cmds.setDrivenKeyframe (each + '.rotateY', cd='L_pect_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='L_pect_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")

        r_pect_sdk = cmds.ls("R_pect_*_SDK")
        for each in r_pect_sdk:
            cmds.setDrivenKeyframe (each + '.rotateY', cd='R_pect_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='R_pect_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")

        tail_sdk = cmds.ls("tail_*_SDK")
        for each in tail_sdk:
            cmds.setDrivenKeyframe (each + '.rotateY', cd='tail_master_CON.rotateY', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateY', cd='tail_master_CON.rotateY', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateY')
            cmds.setInfinity (pri="linear", poi="linear")

    def l_pect_oc(self, *args):
        root_sdk_select = cmds.ls(sl=1)
        for each in root_sdk_select:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pect_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='L_pect_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")

    def r_pect_oc(self, *args):
        root_sdk_select = cmds.ls(sl=1)
        for each in root_sdk_select:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pect_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='R_pect_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")

    def tail_oc(self, *args):
        root_sdk_select = cmds.ls(sl=1)
        for each in root_sdk_select:
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='tail_master_CON.rotateZ', itt="spline", ott="spline")
            cmds.setDrivenKeyframe (each + '.rotateZ', cd='tail_master_CON.rotateZ', v=30, dv=30, itt="spline",
                                    ott="spline")
            cmds.selectKey (each + '.rotateZ')
            cmds.setInfinity (pri="linear", poi="linear")

    def rb_clean(self,*args):
        # Ribbon controls in one group
        rb_offset = []
        l_pect_offset = cmds.ls ('L_pect_*_CON_OFFSET', assemblies=True)
        r_pect_offset = cmds.ls ('R_pect_*_CON_OFFSET', assemblies=True)
        tail_offset = cmds.ls ('tail_*_CON_OFFSET', assemblies=True)
        rb_offset = l_pect_offset + r_pect_offset + tail_offset
        cmds.group (rb_offset, n='ribbon_con_GRP')

        # master control grp
        master_offset = ['L_pect_master_OFFSET', 'R_pect_master_OFFSET', 'tail_master_OFFSET']
        cmds.group (master_offset, n='ribbon_master_con_GRP')

        # sine handle
        sine = cmds.ls ('*_SINE')
        cmds.group (sine, n='ribbon_sine_GRP')

        # ribbon system
        rb = ['deform_ribbon_GRP', 'Ribbon_Curves_GRP', 'ribbon_con_GRP', 'ribbon_master_con_GRP', 'ribbon_sine_GRP']
        cmds.group (rb, n='ribbon_system')


myWindow = NM_Window ()
