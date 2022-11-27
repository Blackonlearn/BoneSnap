# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BoneSnap",
    "author" : "Bong",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

import bpy
from bpy.props import *
import mathutils

num_bones = 2
armature_name = 'Armature'
ik_target_name = 'IK_Target'
ik_pole_name = 'IK_Pole'
fk_upperarm_name = 'FK_UpperArm'
fk_forearm_name = 'FK_ForeArm'
ik_forearm_name = 'IK_ForeArm'

class UI(bpy.types.Panel):
    bl_label = "Snap FK/IK"
    bl_idname = "Snap_FKIK"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = 'Misc'
    
    
    @classmethod
    def poll(self, context):
        o = context.active_object
        return o and o.type == 'ARMATURE' and o.mode == 'POSE'
    
    def draw(self, context):
        self.layout.operator("my.fktoik")
        self.layout.operator("my.iktofk")
        
class FKtoIKButton(bpy.types.Operator):
    bl_idname = "my.fktoik"
    bl_label = "FK -> IK"
    bl_options = {'REGISTER', 'UNDO'}
  
    def execute(self, context):
        amt = bpy.data.objects[armature_name]
        ik_target = amt.pose.bones[ik_target_name]
        pole_target = amt.pose.bones[ik_pole_name]
        fk_upperarm = amt.pose.bones[fk_upperarm_name]
        fk_forearm = amt.pose.bones[fk_forearm_name]
        ik_forearm = amt.pose.bones[ik_forearm_name]
        
        bones = []
        fk_it = fk_forearm
        ik_it = ik_forearm
        for i in range(num_bones):
            bones.append((fk_it,ik_it))
            fk_it = fk_it.parent
            ik_it = ik_it.parent
            
        for b in reversed(bones):
            b[0].matrix = b[1].matrix
            bpy.context.view_layer.update()
            
        return {'FINISHED'}
  
  
def set_translation(matrix, loc):
    trs = matrix.decompose()
    rot = trs[1].to_matrix().to_4x4()
    scale = mathutils.Matrix.Scale(1, 4, trs[2])
    return mathutils.Matrix.Translation(loc) * (rot * scale)
  
class IKtoFKButton(bpy.types.Operator):
    bl_idname = "my.iktofk"
    bl_label = "IK -> FK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        amt = bpy.data.objects[armature_name]
        ik_target = amt.pose.bones[ik_target_name]
        pole_target = amt.pose.bones[ik_pole_name]
        fk_upperarm = amt.pose.bones[fk_upperarm_name]
        fk_forearm = amt.pose.bones[fk_forearm_name]
        ik_forearm = amt.pose.bones[ik_forearm_name]

        def set_translation(bone, loc):
            mat = bone.matrix.copy()
            mat[0][3] = loc[0]
            mat[1][3] = loc[1]
            mat[2][3] = loc[2]
            bone.matrix = mat

        def ik2fk(target, pole, upper_fk, fore_fk):
            set_translation(target, fore_fk.tail)
            set_translation(pole, upper_fk.tail)
            
        pose_bones = bpy.context.active_object.pose.bones
        upper_fk = fk_upperarm
        fore_fk = fk_forearm
        target = ik_target
        pole = pole_target

        ik2fk(target, pole, upper_fk, fore_fk)

        return {'FINISHED'}

classes = (
    UI,
    FKtoIKButton,
    IKtoFKButton
)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
if __name__ == "__main__":
    register()