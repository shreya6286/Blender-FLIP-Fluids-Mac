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

import bpy

from ..operators import helper_operators
from . import domain_display_ui
from ..utils import version_compatibility_utils as vcu


def _draw_whitewater_display_settings(self, context):
    obj = vcu.get_active_object(context)
    dprops = obj.flip_fluid.domain
    domain_display_ui.draw_whitewater_display_settings(self, context, dprops.whitewater)


def _draw_geometry_attributes_menu(self, context):
    obj = vcu.get_active_object(context)
    dprops = obj.flip_fluid.domain
    wprops = dprops.whitewater
    show_documentation = vcu.get_addon_preferences(context).show_documentation_in_ui
    prefs = vcu.get_addon_preferences()

    box = self.layout.box()
    row = box.row(align=True)
    row.prop(wprops, "geometry_attributes_expanded",
        icon="TRIA_DOWN" if wprops.geometry_attributes_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Whitewater Attributes:")

    if wprops.geometry_attributes_expanded:
        if not prefs.is_developer_tools_enabled():
            warn_box = box.box()
            warn_column = warn_box.column(align=True)
            warn_column.enabled = True
            warn_column.label(text="     This feature is affected by a current bug in Blender.", icon='ERROR')
            warn_column.label(text="     The Developer Tools option must be enabled in preferences")
            warn_column.label(text="     to use this feature.")
            warn_column.separator()
            warn_column.prop(prefs, "enable_developer_tools", text="Enable Developer Tools in Preferences")
            warn_column.separator()
            warn_column.operator(
                "wm.url_open", 
                text="Important Info and Limitations", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Preferences-Menu-Settings#developer-tools"
            return

        column = box.column(align=True)
        if not vcu.is_blender_31():
            column.enabled = False
            column.label(text="Geometry attribute features for whitewater are only available in", icon='ERROR')
            column.label(text="Blender 3.1 or later", icon='ERROR')
            return

        column = box.column(align=True)
        column.prop(wprops, "enable_velocity_vector_attribute")
        column.prop(wprops, "enable_id_attribute")
        column.prop(wprops, "enable_lifetime_attribute")
        column.separator()
        column.operator("flip_fluid_operators.helper_initialize_motion_blur")
    else:
        if not vcu.is_blender_31():
            row = row.row(align=True)
            row.enabled = False
            row.alignment = 'RIGHT'
            row.label(text="(Blender 3.1 or later required)")
            return
        if not prefs.is_developer_tools_enabled():
            return
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(wprops, "enable_velocity_vector_attribute", text="Velocity")
        row.prop(wprops, "enable_id_attribute", text="ID")
        row.prop(wprops, "enable_lifetime_attribute", text="Lifetime")


    if show_documentation:
        column = box.column(align=True)
        column.operator(
            "wm.url_open", 
            text="Domain Attributes Documentation", 
            icon="WORLD"
        ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Domain-Attributes-and-Data-Settings"
        column.operator(
            "wm.url_open", 
            text="Attributes and Motion Blur Example Scenes", 
            icon="WORLD"
        ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Example-Scene-Descriptions#attribute-and-motion-blur-examples"


class FLIPFLUID_PT_DomainTypeWhitewaterPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_category = "FLIP Fluid"
    bl_label = "FLIP Fluid Whitewater"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if vcu.get_addon_preferences(context).enable_tabbed_domain_settings_view:
            return False
        obj_props = vcu.get_active_object(context).flip_fluid
        is_addon_disabled = context.scene.flip_fluid.is_addon_disabled_in_blend_file()
        return obj_props.is_active and obj_props.object_type == "TYPE_DOMAIN" and not is_addon_disabled


    def draw(self, context):
        obj = vcu.get_active_object(context)
        dprops = obj.flip_fluid.domain
        wprops = dprops.whitewater
        is_whitewater_enabled = wprops.enable_whitewater_simulation
        show_documentation = vcu.get_addon_preferences(context).show_documentation_in_ui
        show_advanced_whitewater = (wprops.whitewater_ui_mode == 'WHITEWATER_UI_MODE_ADVANCED')
        highlight_advanced = wprops.highlight_advanced_settings

        if show_documentation:
            column = self.layout.column(align=True)
            column.operator(
                "wm.url_open", 
                text="Whitewater Documentation", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Domain-Whitewater-Settings"
            column.operator(
                "wm.url_open", 
                text="Simulation not generating enough whitewater", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Scene-Troubleshooting#simulation-not-generating-enough-whitewater-foambubblespray"
            column.operator(
                "wm.url_open", 
                text="Whitewater particles are rendered too large", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Scene-Troubleshooting#whitewater-particles-are-too-largesmall-when-rendered"
            column.operator(
                "wm.url_open", 
                text="Whitewater particles are not rendered in preview render", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Scene-Troubleshooting#whitewater-particles-are-not-rendered-when-viewport-shading-is-set-to-rendered"
            column.operator(
                "wm.url_open", 
                text="Whitewater particles are not exported to Alembic", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Alembic-Export-Support#rendering-alembic-whitewater-on-a-render-farm"
            column.operator(
                "wm.url_open", 
                text="Whitewater rendering tips", 
                icon="WORLD"
            ).url = "https://github.com/rlguy/Blender-FLIP-Fluids/wiki/Domain-Whitewater-Settings#whitewater-rendering-tips"


        column = self.layout.column(align=True)
        column.prop(wprops, "enable_whitewater_simulation")
        column.separator()

        box = self.layout.box()
        box.enabled = is_whitewater_enabled

        column = box.column(align=True)
        split = column.split(align=True)
        column_left = split.column(align=True)
        column_right = split.column(align=True)

        row = column_left.row(align=True)
        row.prop(wprops, "settings_view_mode_expanded",
            icon="TRIA_DOWN" if wprops.settings_view_mode_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Settings View Mode:")

        if not wprops.settings_view_mode_expanded:
            row = column_right.row(align=True)
            row.alignment = 'RIGHT'
            row.prop(wprops, "whitewater_ui_mode", expand=True)

        if wprops.settings_view_mode_expanded:
            column = box.column(align=True)
            row = column.row()
            row.prop(wprops, "whitewater_ui_mode", expand=True)

            split = column.split()
            split.column()
            column_right = split.column()
            column_right.enabled = show_advanced_whitewater
            column_right.prop(wprops, "highlight_advanced_settings")

        box = self.layout.box()
        box.enabled = is_whitewater_enabled
        row = box.row(align=True)
        row.prop(wprops, "whitewater_simulation_particles_expanded",
            icon="TRIA_DOWN" if wprops.whitewater_simulation_particles_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Whitewater Particles:")

        if not wprops.whitewater_simulation_particles_expanded:
            info_text = ""
            enabled_particles = []
            if wprops.enable_foam:
                enabled_particles.append("Foam")
            if wprops.enable_bubbles:
                enabled_particles.append("Bubble")
            if wprops.enable_spray:
                enabled_particles.append("Spray")
            if wprops.enable_dust:
                enabled_particles.append("Dust")

            if enabled_particles:
                for ptype in enabled_particles:
                    info_text += ptype + "/"
                info_text = info_text.rstrip("/")
            else:
                info_text = "None"

            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.label(text=info_text)

        if wprops.whitewater_simulation_particles_expanded:
            column = box.column(align=True)
            column.enabled = is_whitewater_enabled

            row = column.row()
            row.prop(wprops, "enable_foam")
            row.prop(wprops, "enable_bubbles")
            row.prop(wprops, "enable_spray")
            row.prop(wprops, "enable_dust")

        box = self.layout.box()
        box.enabled = is_whitewater_enabled
        row = box.row(align=True)
        row.prop(wprops, "emitter_settings_expanded",
            icon="TRIA_DOWN" if wprops.emitter_settings_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Emitter Settings:")

        if wprops.emitter_settings_expanded:
            column = box.column(align=True)

            column.prop(wprops, "enable_whitewater_emission")

            if show_advanced_whitewater:
                column = box.column(align=True)
                column.alert = highlight_advanced
                column.prop(wprops, "whitewater_emitter_generation_rate")

            column = box.column(align=True)
            column.prop(wprops, "wavecrest_emission_rate")
            column.prop(wprops, "turbulence_emission_rate")
            column = column.column(align=True)
            column.enabled = wprops.enable_dust
            column.prop(wprops, "dust_emission_rate")

            column = box.column(align=True)
            column.prop(wprops, "spray_emission_speed", slider=True)

            if show_advanced_whitewater:
                column = box.column(align=True)
                row = column.row(align=True)
                row.prop(wprops.min_max_whitewater_energy_speed, "value_min")
                row.prop(wprops.min_max_whitewater_energy_speed, "value_max")

                row = column.row(align=True)
                row.alert = highlight_advanced
                row.prop(wprops.min_max_whitewater_wavecrest_curvature, "value_min")
                row.prop(wprops.min_max_whitewater_wavecrest_curvature, "value_max")

                row = column.row(align=True)
                row.alert = highlight_advanced
                row.prop(wprops.min_max_whitewater_turbulence, "value_min")
                row.prop(wprops.min_max_whitewater_turbulence, "value_max")
            else:
                column = box.column()
                row = column.row(align=True)
                row.prop(wprops.min_max_whitewater_energy_speed, "value_min")
                row.prop(wprops.min_max_whitewater_energy_speed, "value_max")

            column = box.column(align=True)
            column.prop(wprops, "max_whitewater_particles")

            if show_advanced_whitewater:
                column = box.column(align=True)
                column.alert = highlight_advanced
                column.prop(wprops, "enable_whitewater_emission_near_boundary")

            column = box.column(align=True)
            column.enabled = wprops.enable_dust
            column.prop(wprops, "enable_dust_emission_near_boundary", text="Enable dust emission near domain floor")

        box = self.layout.box()
        box.enabled = is_whitewater_enabled
        row = box.row(align=True)
        row.prop(wprops, "particle_settings_expanded",
            icon="TRIA_DOWN" if wprops.particle_settings_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Particle Behavior Settings:")

        if wprops.particle_settings_expanded:
            column = box.column()
            column.label(text="Foam:")

            row = column.row()
            row.prop(wprops, "foam_advection_strength", text="Advection Strength", slider=True)

            if show_advanced_whitewater:
                row = column.row()
                row.alert = highlight_advanced
                row.prop(wprops, "foam_layer_depth", text="Depth", slider=True)

                row = column.row()
                row.alert = highlight_advanced
                row.prop(wprops, "foam_layer_offset", text="Offset", slider=True)

            column = box.column(align=True)
            column.label(text="Bubble:")
            column.prop(wprops, "bubble_drag_coefficient", text="Drag Coefficient", slider=True)
            column.prop(wprops, "bubble_bouyancy_coefficient", text="Buoyancy Coefficient")

            column = box.column(align=True)
            column.label(text="Spray:")
            column.prop(wprops, "spray_drag_coefficient", text="Drag Coefficient", slider=True)

            column = box.column(align=True)
            column.enabled = wprops.enable_dust
            column.label(text="Dust:")
            column.prop(wprops, "dust_drag_coefficient", text="Drag Coefficient", slider=True)
            column.prop(wprops, "dust_bouyancy_coefficient", text="Buoyancy Coefficient")

            column = box.column(align=True)
            split = column.split()
            column = split.column(align=True)
            column.label(text="Lifespan:")
            column.prop(wprops.min_max_whitewater_lifespan, "value_min", text="Min")
            column.prop(wprops.min_max_whitewater_lifespan, "value_max", text="Max")
            column.prop(wprops, "whitewater_lifespan_variance", text="Variance")

            column = split.column(align=True)
            column.label(text="Lifespan Modifiers:")
            column.prop(wprops, "foam_lifespan_modifier", text="Foam")
            column.prop(wprops, "bubble_lifespan_modifier", text="Bubble")
            column.prop(wprops, "spray_lifespan_modifier", text="Spray")
            column = column.column(align=True)
            column.enabled = wprops.enable_dust
            column.prop(wprops, "dust_lifespan_modifier", text="Dust")

        box = self.layout.box()
        row = box.row(align=True)
        row.prop(wprops, "boundary_behaviour_settings_expanded",
            icon="TRIA_DOWN" if wprops.boundary_behaviour_settings_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Domain Boundary Collisions:")

        if not wprops.boundary_behaviour_settings_expanded:
            info_text = ""
            if wprops.whitewater_boundary_collisions_mode == 'BOUNDARY_COLLISIONS_MODE_INHERIT':
                info_text = "Inherit"
            elif wprops.whitewater_boundary_collisions_mode == 'BOUNDARY_COLLISIONS_MODE_CUSTOM':
                info_text = "Custom"

            row = row.row(align=True)
            row.alignment = 'RIGHT'
            row.label(text=info_text)

        if wprops.boundary_behaviour_settings_expanded:
            column = box.column()
            row = column.row(align=True)
            row.prop(wprops, "whitewater_boundary_collisions_mode", expand=True)

            if wprops.whitewater_boundary_collisions_mode == 'BOUNDARY_COLLISIONS_MODE_INHERIT':
                sprops = dprops.simulation
                column = box.column()
                column.enabled = False
                row = column.row(align=True)
                row.alignment = 'LEFT'
                row.prop(sprops, "fluid_boundary_collisions", index=0, text="X –")
                row.prop(sprops, "fluid_boundary_collisions", index=1, text="X+")
                row = column.row(align=True)
                row.alignment = 'LEFT'
                row.prop(sprops, "fluid_boundary_collisions", index=2, text="Y –")
                row.prop(sprops, "fluid_boundary_collisions", index=3, text="Y+")
                row = column.row(align=True)
                row.alignment = 'LEFT'
                row.prop(sprops, "fluid_boundary_collisions", index=4, text="Z –")
                row.prop(sprops, "fluid_boundary_collisions", index=5, text="Z+")
            else:
                split = column.split(align=True)
                column1 = split.column(align=True)
                column2 = split.column(align=True)
                column3 = split.column(align=True)
                column4 = split.column(align=True)

                column1.label(text="Foam:")
                row = column1.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "foam_boundary_collisions", index=0, text="X –")
                row.prop(wprops, "foam_boundary_collisions", index=1, text="X+")
                row = column1.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "foam_boundary_collisions", index=2, text="Y –")
                row.prop(wprops, "foam_boundary_collisions", index=3, text="Y+")
                row = column1.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "foam_boundary_collisions", index=4, text="Z –")
                row.prop(wprops, "foam_boundary_collisions", index=5, text="Z+")

                column2.label(text="Bubble:")
                row = column2.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "bubble_boundary_collisions", index=0, text="X –")
                row.prop(wprops, "bubble_boundary_collisions", index=1, text="X+")
                row = column2.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "bubble_boundary_collisions", index=2, text="Y –")
                row.prop(wprops, "bubble_boundary_collisions", index=3, text="Y+")
                row = column2.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "bubble_boundary_collisions", index=4, text="Z –")
                row.prop(wprops, "bubble_boundary_collisions", index=5, text="Z+")

                column3.label(text="Spray:")
                row = column3.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "spray_boundary_collisions", index=0, text="X –")
                row.prop(wprops, "spray_boundary_collisions", index=1, text="X+")
                row = column3.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "spray_boundary_collisions", index=2, text="Y –")
                row.prop(wprops, "spray_boundary_collisions", index=3, text="Y+")
                row = column3.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "spray_boundary_collisions", index=4, text="Z –")
                row.prop(wprops, "spray_boundary_collisions", index=5, text="Z+")

                column4.label(text="Dust:")
                row = column4.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "dust_boundary_collisions", index=0, text="X –")
                row.prop(wprops, "dust_boundary_collisions", index=1, text="X+")
                row = column4.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "dust_boundary_collisions", index=2, text="Y –")
                row.prop(wprops, "dust_boundary_collisions", index=3, text="Y+")
                row = column4.row(align=True)
                row.alignment = 'LEFT'
                row.prop(wprops, "dust_boundary_collisions", index=4, text="Z –")
                row.prop(wprops, "dust_boundary_collisions", index=5, text="Z+")

        box = self.layout.box()
        box.enabled = is_whitewater_enabled
        row = box.row(align=True)
        row.prop(wprops, "obstacle_settings_expanded",
            icon="TRIA_DOWN" if wprops.obstacle_settings_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Obstacle Influence Settings:")

        if wprops.obstacle_settings_expanded:
            column = box.column(align=True)

            # The following properties are probably set at reasonable values and
            # are not needed by the user
            """
            column.prop(wprops, "obstacle_influence_base_level", text="Base Level")
            column.prop(wprops, "obstacle_influence_decay_rate", text="Decay Rate")
            """

            obstacle_objects = context.scene.flip_fluid.get_obstacle_objects()
            indent_str = 5 * " "
            column.label(text="Obstacle Object Influence:")
            if len(obstacle_objects) == 0:
                column.label(text=indent_str + "No obstacle objects found...")
            else:
                split = vcu.ui_split(column, factor=0.25, align=True)
                column_left = split.column(align=True)
                column_right = split.column(align=True)
                for ob in obstacle_objects:
                    pgroup = ob.flip_fluid.get_property_group()
                    column_left.label(text=ob.name, icon="OBJECT_DATA")
                    row = column_right.row()
                    row.alignment = 'RIGHT'
                    row.prop(pgroup, "whitewater_influence", text="influence")
                    row.prop(pgroup, "dust_emission_strength", text="dust emission")

        _draw_whitewater_display_settings(self, context)
        _draw_geometry_attributes_menu(self, context)

        self.layout.separator()
        column = self.layout.column(align=True)
        column.operator("flip_fluid_operators.helper_delete_whitewater_objects", icon="X").whitewater_type = 'TYPE_ALL'
    

def register():
    bpy.utils.register_class(FLIPFLUID_PT_DomainTypeWhitewaterPanel)


def unregister():
    bpy.utils.unregister_class(FLIPFLUID_PT_DomainTypeWhitewaterPanel)
