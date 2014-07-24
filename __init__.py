# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
        "name": "Hotkey Viewer",
        "description":"Interactive Viewer for learning hotkeys.",
        "author":"dustractor",
        "version":(0,1),
        "blender":(2,65,0),
        "location":"hkx:witch",
        "warning":"",
        "wiki_url":"",
        "category": "Development"
        }

import sqlite3
import bpy

cx = None

def enumtypes(proptype):
    for e in proptype.bl_rna.properties['type'].enum_items:
        yield (e.identifier,e.name,e.identifier)

def kmi_iter():
    for wm in bpy.data.window_managers:
        for kc in wm.keyconfigs:
            for km in kc.keymaps:
                for kmi in km.keymap_items:
                    yield wm,kc,km,kmi

def make_cx():
    global cx
    cx = sqlite3.connect(":memory:")
    cx.executescript("create table hkx( wm_name, kc_name, km_name, name, type, ctrl, alt, shift, oskey, disp );")
    insert = "insert into hkx( wm_name,kc_name,km_name, name, type, ctrl, alt, shift, oskey, disp) values(?,?,?, ?,?,?, ?,?,?, ?)"

    for wm,kc,km,kmi in kmi_iter():
        kdesc = kmi.value.title()
        kmod = "+".join(filter(lambda _:_, ( "ctrl" if kmi.ctrl else None, "alt" if kmi.alt else None, "shift" if kmi.shift else None, "oskey" if kmi.oskey else None)))
        if kmod:
            kdesc += " " + kmod
        kdesc += " " + " ".join(map(str.title,kmi.type.split("_")))
        if kmi.properties:
            kdesc += repr(kmi.properties.items()) 


        cx.execute(insert,( wm.name, kc.name, km.name, kmi.name, kmi.type, kmi.ctrl, kmi.alt, kmi.shift, kmi.oskey,kdesc))


def refresh(self,context):
    if self.refresh:
        make_cx()
        self.refresh = False


class hkxwitch(bpy.types.PropertyGroup):
    refresh = bpy.props.BoolProperty(default=True,update=refresh)
    ktype = bpy.props.StringProperty()
    ctrl = bpy.props.BoolProperty()
    alt = bpy.props.BoolProperty()
    shift = bpy.props.BoolProperty()
    oskey = bpy.props.BoolProperty()
    rtype = bpy.props.EnumProperty(items=list(enumtypes(bpy.types.Region)))
    ktype = bpy.props.EnumProperty(items=list(enumtypes(bpy.types.KeyMapItem)))
    ktype_view = bpy.props.EnumProperty(items=[(_,_,_) for _ in ("keyboard","numpad","mouse","ndof")])
    def numpad_display(self,layout):
        R = layout.row(align=True)
        col = R.column(align=True)
        row = col.row(align=True)
        row.prop_enum(self,'ktype','NONE')
        row.prop_enum(self,'ktype','NUMPAD_SLASH')
        row.prop_enum(self,'ktype','NUMPAD_ASTERIX')
        row = col.row(align=True)
        row.prop_enum(self,'ktype','NUMPAD_7')
        row.prop_enum(self,'ktype','NUMPAD_8')
        row.prop_enum(self,'ktype','NUMPAD_9')
        row = col.row(align=True)
        row.prop_enum(self,'ktype','NUMPAD_4')
        row.prop_enum(self,'ktype','NUMPAD_5')
        row.prop_enum(self,'ktype','NUMPAD_6')
        row = col.row(align=True)
        row.prop_enum(self,'ktype','NUMPAD_1')
        row.prop_enum(self,'ktype','NUMPAD_2')
        row.prop_enum(self,'ktype','NUMPAD_3')
        row = col.row(align=True)
        col2 = row.column(align=True)
        col2.scale_x = 2
        col2.prop_enum(self,'ktype','NUMPAD_0')
        col2 = row.column(align=True)
        col2.prop_enum(self,'ktype','NUMPAD_PERIOD')
        col = R.column(align=True)
        row = col.row()
        row.prop_enum(self,'ktype','NUMPAD_MINUS')
        row = col.row()
        row.scale_y = 2
        row.prop_enum(self,'ktype','NUMPAD_PLUS')
        row = col.row()
        row.scale_y = 2
        row.prop_enum(self,'ktype','NUMPAD_ENTER')
    def mouse_display(self,layout):
        col = layout.column(align=True)
        for r in [
                ["LEFTMOUSE", "MIDDLEMOUSE", "RIGHTMOUSE"],
                ["BUTTON4MOUSE", "BUTTON5MOUSE","BUTTON6MOUSE", "BUTTON7MOUSE"],
                ["ACTIONMOUSE", "SELECTMOUSE","MOUSEMOVE", "INBETWEEN_MOUSEMOVE"],
                ["TRACKPADPAN", "TRACKPADZOOM"],
                ["MOUSEROTATE", "WHEELUPMOUSE", "WHEELDOWNMOUSE", "WHEELINMOUSE", "WHEELOUTMOUSE"],
                ["EVT_TWEAK_L", "EVT_TWEAK_M", "EVT_TWEAK_R", "EVT_TWEAK_A", "EVT_TWEAK_S"]
            ]:
            row = col.row(align=True)
            for c in r:
                row.prop_enum(self,'ktype',c)

    def keyboard_display(self,layout):
        col = layout.column(align=True)
        for r in [
                ["ESC","F1","F2","F3","F4","F5","F6","F7","F8","F9","F10","F11","F12"],
                ["ACCENT_GRAVE","ONE","TWO","THREE","FOUR","FIVE","SIX","SEVEN","EIGHT","NINE","ZERO","MINUS","EQUAL","BACK_SPACE","NONE"],
                ["TAB","Q","W","E","R","T","Y","U","I","O","P","LEFT_BRACKET","RIGHT_BRACKET","BACK_SLASH"],
                ["NONE","A","S","D","F","G","H","J","K","L","SEMI_COLON","QUOTE","RET"],
                ["LEFT_SHIFT","Z","X","C","V","B","N","M","COMMA","PERIOD","SLASH","RIGHT_SHIFT"],
                ["LEFT_CTRL","LEFT_ALT","OSKEY","NONE","SPACE","NONE","RIGHT_ALT","RIGHT_CTRL"]
            ]:
            row = col.row(align=True)
            row.scale_y = 2
            for c in r:
                row.prop_enum(self,'ktype',c)
    def ndof_display(self,layout):
        col = layout.column(align=True)
        for r in [
                ['NDOF_BUTTON_1', 'NDOF_BUTTON_6', 'NDOF_BUTTON_PLUS', 'NDOF_BUTTON_ISO1', 'NDOF_BUTTON_ISO2', 'NDOF_BUTTON_DOMINANT', 'NDOF_BUTTON_MENU', 'NDOF_BUTTON_FIT'],
                ['NDOF_BUTTON_2', 'NDOF_BUTTON_7', 'NDOF_BUTTON_MINUS', 'NDOF_BUTTON_ROLL_CW', 'NDOF_BUTTON_ROLL_CCW', 'NDOF_BUTTON_ESC', 'NDOF_BUTTON_BOTTOM', 'NDOF_BUTTON_TOP'],
                ['NDOF_BUTTON_3', 'NDOF_BUTTON_8', 'NDOF_BUTTON_A', 'NDOF_BUTTON_SPIN_CW', 'NDOF_BUTTON_SPIN_CCW', 'NDOF_BUTTON_ALT', 'NDOF_BUTTON_RIGHT', 'NDOF_BUTTON_LEFT'],
                ['NDOF_BUTTON_4', 'NDOF_BUTTON_9', 'NDOF_BUTTON_B', 'NDOF_BUTTON_TILT_CW', 'NDOF_BUTTON_TILT_CCW', 'NDOF_BUTTON_SHIFT', 'NDOF_BUTTON_BACK', 'NDOF_BUTTON_FRONT'],
                ['NDOF_BUTTON_5', 'NDOF_BUTTON_10', 'NDOF_BUTTON_C', 'NDOF_BUTTON_ROTATE', 'NDOF_BUTTON_PANZOOM', 'NDOF_BUTTON_CTRL', 'NDOF_MOTION', 'NONE']
            ]:
            row = col.row(align=True)
            for c in r:
                row.prop_enum(self,'ktype',c)
    def display(self,layout):
        {
            'numpad':self.numpad_display,
            'keyboard':self.keyboard_display,
            'mouse':self.mouse_display,
            'ndof':self.ndof_display
        }[self.ktype_view](layout)

class HKX_WITCH_PT_hkxpanel(bpy.types.Panel):
    bl_label = "hkx"
    bl_space_type = "USER_PREFERENCES"
    bl_region_type = "WINDOW"
    @classmethod
    def poll(self,context):
        return context.user_preferences.active_section == "INPUT"
    def draw(self,context):
        hkx = context.window_manager.hkx
        layout = self.layout
        layout.separator()
        
        layout.prop(hkx,"refresh",toggle=True,text="",icon="FILE_REFRESH")
        layout.prop(hkx,"ktype_view",expand=True)

        hkx.display(layout.box())


        if hkx.refresh:
            hkx.refresh = True
        if cx:
            for (T,) in cx.execute("select disp from hkx where type=?",(hkx.ktype,)):
                layout.label(T)


def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.hkx = bpy.props.PointerProperty(type=hkxwitch)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.WindowManager.hkx
    

