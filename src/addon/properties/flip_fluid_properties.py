# Blender FLIP Fluids Add-on
# Copyright (C) 2024 Ryan L. Guy
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import bpy, os
from bpy.props import (
        BoolProperty,
        StringProperty,
        PointerProperty
        )

from ..utils import version_compatibility_utils as vcu


class FlipFluidProperties(bpy.types.PropertyGroup):
    conv = vcu.convert_attribute_to_28
    
    show_render = BoolProperty(
            name="Show Render",
            description="Display simulation in render. If disabled, simulation data will not be loaded in the render",
            default=True,
            ); exec(conv("show_render"))
    show_viewport = BoolProperty(
            name="Show Viewport",
            description="Display simulation in viewport. If disabled, simulation data will not be loaded in the viewport."
                " Disable to speed up playback while working on other areas of your scene",
            default=True,
            ); exec(conv("show_viewport"))

    logo_name = StringProperty("flip_fluids_logo"); exec(conv("logo_name"))
    domain_object_name = StringProperty(default=""); exec(conv("domain_object_name"))


    @classmethod
    def register(cls):
        bpy.types.Scene.flip_fluid = PointerProperty(
                name="Flip Fluid Properties",
                description="",
                type=cls,
                )
        cls.custom_icons = bpy.utils.previews.new()


    @classmethod
    def unregister(cls):
        bpy.utils.previews.remove(cls.custom_icons)
        del bpy.types.Scene.flip_fluid


    def load_post(self):
        self._initialize_custom_icons()


    def is_addon_disabled_in_blend_file(self):
        return bpy.context.scene.flip_fluid_helper.is_addon_disabled_in_blend_file()


    def is_domain_object_set(self):
        return self.get_domain_object() is not None


    def get_num_domain_objects(self):
        n = 0
        for obj in bpy.data.objects:
            if obj.flip_fluid.is_domain():
                n += 1
        return n


    def get_domain_object(self):
        domain = bpy.data.objects.get(self.domain_object_name)
        if not domain or not domain.flip_fluid.is_domain():
            for obj in bpy.data.objects:
                if obj.flip_fluid.is_domain():
                    domain = obj
                    try:
                        # This operation may not be allowed depending on
                        # the Blender context. It's harmless if this fails.
                        self.domain_object_name = domain.name
                    except:
                        pass
                    break
        if domain is not None and domain.flip_fluid.object_type != 'TYPE_DOMAIN':
            return None
        return domain


    def get_domain_properties(self):
        domain_object = self.get_domain_object()
        if domain_object is None:
            return
        return domain_object.flip_fluid.domain


    def is_domain_in_active_scene(self):
        domain_object = self.get_domain_object()
        if domain_object is None:
            return False
        return domain_object.name in bpy.context.scene.collection.all_objects


    def get_num_fluid_objects(self):
        n = 0
        for obj in vcu.get_all_scene_objects():
            if obj.flip_fluid.is_fluid():
                n += 1
        return n


    def get_fluid_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_fluid():
                objects.append(obj)
        return objects


    def get_num_obstacle_objects(self):
        n = 0
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if obj.flip_fluid.is_obstacle():
                n += 1
        return n


    def get_obstacle_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_obstacle():
                objects.append(obj)
        return objects


    def get_num_inflow_objects(self):
        n = 0
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if obj.flip_fluid.is_inflow():
                n += 1
        return n


    def get_inflow_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_inflow():
                objects.append(obj)
        return objects


    def get_num_outflow_objects(self):
        n = 0
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if obj.flip_fluid.is_outflow():
                n += 1
        return n


    def get_outflow_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_outflow():
                objects.append(obj)
        return objects


    def get_num_force_field_objects(self):
        n = 0
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if obj.flip_fluid.is_force_field():
                n += 1
        return n


    def get_force_field_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_force_field():
                objects.append(obj)
        return objects


    def get_simulation_objects(self, skip_hide_viewport=False):
        objects = []
        for obj in vcu.get_all_scene_objects():
            if obj.flip_fluid.object_type == 'TYPE_NONE':
                continue
            if not obj.flip_fluid.is_active:
                continue
            if skip_hide_viewport and obj.hide_viewport:
                continue
            if obj.flip_fluid.is_domain():
                # get all FLIP Fluid objects that are not a domain
                continue
            objects.append(obj)

        return objects


    def get_logo_icon(self):
        return self.custom_icons.get(self.logo_name)


    def _initialize_custom_icons(self):
        addon_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if vcu.is_blender_28():
            icon_filename = "flip_fluids_logo_28.png"
        else:
            icon_filename = "flip_fluids_logo_27.png"
        logo_path = os.path.join(addon_dir, "icons", icon_filename)
        self.custom_icons.clear()
        if os.path.isfile(logo_path):
            self.custom_icons.load(self.logo_name, logo_path, 'IMAGE')


def load_post():
    bpy.context.scene.flip_fluid.load_post()


def register():
    bpy.utils.register_class(FlipFluidProperties)


def unregister():
    bpy.utils.unregister_class(FlipFluidProperties)