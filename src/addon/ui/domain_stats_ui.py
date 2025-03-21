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

import bpy, math

from ..utils import version_compatibility_utils as vcu


def format_bytes(num):
    # Method adapted from: http://stackoverflow.com/a/10171475
    unit_list = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB']
    decimal_list = [0, 0, 1, 2, 2, 2]

    if num > 1:
        exponent = min(int(math.log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent], decimal_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'


def format_number(num):
    return format(num, "6,d").replace(",", " ")


def format_time(t):
    return "{:0.2f}".format(t) + " s"


def format_long_time(t):
    m, s = divmod(t, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def draw_frame_info_simulation_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats
    simprops = vcu.get_active_object(context).flip_fluid.domain.simulation

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "frame_info_simulation_stats_expanded",
        icon="TRIA_DOWN" if sprops.frame_info_simulation_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Simulation Stats")

    if sprops.frame_info_simulation_stats_expanded:
        column = subbox.column()
        split = column.split()
        column = split.column()
        column.label(text="Frame ID:")
        column.label(text="Timeline Frame:")
        column.label(text="Timestep:")
        column.label(text="Substeps:")
        column.label(text="Fluid Particles:")
        if sprops.display_frame_diffuse_particle_stats:
            column.label(text="Whitewater Particles:")
            column.label(text="             Foam:")
            column.label(text="             Bubble:")
            column.label(text="             Spray:")
            column.label(text="             Dust:")
        column.label(text="Performance Score:")

        column = split.column()
        column.label(text=str(sprops.frame_info_id))
        column.label(text=str(sprops.frame_start + sprops.frame_info_id))
        column.label(text=format_time(sprops.frame_delta_time))
        column.label(text=str(sprops.frame_substeps))
        column.label(text=format_number(sprops.frame_fluid_particles).lstrip())
        if sprops.display_frame_diffuse_particle_stats:
            column.label(text=format_number(sprops.frame_diffuse_particles).lstrip())
            column.label(text=format_number(sprops.foam_mesh.verts).lstrip())
            column.label(text=format_number(sprops.bubble_mesh.verts).lstrip())
            column.label(text=format_number(sprops.spray_mesh.verts).lstrip())
            column.label(text=format_number(sprops.dust_mesh.verts).lstrip())

        performance_score_str = "0"
        if sprops.frame_performance_score != -1:
            performance_score_str = str(sprops.frame_performance_score)
        column.label(text=performance_score_str)


def draw_frame_info_solver_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "frame_info_solver_stats_expanded",
        icon="TRIA_DOWN" if sprops.frame_info_solver_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Solver Stats")

    if sprops.frame_info_solver_stats_expanded:
        if sprops.frame_pressure_solver_enabled:
            stress_threshold = 80.0

            stat_box = subbox.box()
            row = stat_box.row()
            row.prop(sprops, "frame_info_pressure_solver_stats_expanded",
                icon="TRIA_DOWN" if sprops.frame_info_pressure_solver_stats_expanded else "TRIA_RIGHT",
                icon_only=True, 
                emboss=False
            )
            row.label(text="Pressure Solver")

            if sprops.frame_info_pressure_solver_stats_expanded:
                column = stat_box.column(align=True)
                split = column.split()
                column1 = split.column(align=True)
                column2 = split.column(align=True)

                column1.label(text="Solver Status:")
                column1.label(text="Iterations:")
                column1.label(text="Estimated Error:")
                row = column1.row(align=True)
                row.alert = sprops.frame_pressure_solver_stress.stress_level > stress_threshold
                row.label(text="Stress Level:")

                status_state = "Success"
                if not sprops.frame_pressure_solver_success:
                    status_state = "FAILED"
                iterations_str = str(sprops.frame_pressure_solver_iterations) + " / " + str(sprops.frame_pressure_solver_max_iterations)
                error_str = '{0:.12f}'.format(sprops.frame_pressure_solver_error)

                column2.label(text=status_state)
                column2.label(text=iterations_str)
                column2.label(text=error_str)

                stress_status = "OK"
                if sprops.frame_pressure_solver_stress.stress_level > stress_threshold:
                    stress_status = "HIGH"
                if sprops.frame_pressure_solver_stress.stress_level == 100:
                    stress_status = "MAX"
                row = column2.row(align=True)
                row.alert = sprops.frame_pressure_solver_stress.stress_level > stress_threshold
                row.prop(sprops.frame_pressure_solver_stress, "stress_level", slider=True, text=stress_status)

        if sprops.frame_viscosity_solver_enabled:
            stat_box = subbox.box()
            row = stat_box.row()
            row.prop(sprops, "frame_info_viscosity_solver_stats_expanded",
                icon="TRIA_DOWN" if sprops.frame_info_viscosity_solver_stats_expanded else "TRIA_RIGHT",
                icon_only=True, 
                emboss=False
            )
            row.label(text="Viscosity Solver")

            if sprops.frame_info_viscosity_solver_stats_expanded:
                column = stat_box.column(align=True)
                column.alert = not sprops.frame_viscosity_solver_success

                split = column.split()
                column1 = split.column(align=True)
                column2 = split.column(align=True)

                column1.label(text="Solver Status:")
                column1.label(text="Iterations:")
                column1.label(text="Estimated Error:")
                row = column1.row(align=True)
                row.alert = sprops.frame_viscosity_solver_stress.stress_level > stress_threshold
                row.label(text="Stress Level:")

                status_state = "Success"
                if not sprops.frame_viscosity_solver_success:
                    status_state = "FAILED"
                iterations_str = str(sprops.frame_viscosity_solver_iterations) + " / " + str(sprops.frame_viscosity_solver_max_iterations)
                error_str = '{0:.12f}'.format(sprops.frame_viscosity_solver_error)

                column2.label(text=status_state)
                column2.label(text=iterations_str)
                column2.label(text=error_str)

                stress_status = "OK"
                if sprops.frame_viscosity_solver_stress.stress_level > stress_threshold:
                    stress_status = "HIGH"
                if sprops.frame_viscosity_solver_stress.stress_level == 100:
                    stress_status = "MAX"
                row = column2.row(align=True)
                row.alert = sprops.frame_viscosity_solver_stress.stress_level > stress_threshold
                row.prop(sprops.frame_viscosity_solver_stress, "stress_level", slider=True, text=stress_status)


def draw_frame_info_timing_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "frame_info_timing_stats_expanded",
        icon="TRIA_DOWN" if sprops.frame_info_timing_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Timing Stats")

    if sprops.frame_info_timing_stats_expanded:
        column = subbox.column()
        split = vcu.ui_split(column, factor=0.75)
        column = split.column(align = True)
        column.prop(sprops.time_mesh, "pct", slider = True, text = "Mesh Generation")
        column.prop(sprops.time_advection, "pct", slider = True, text = "Velocity Advection")
        column.prop(sprops.time_particles, "pct", slider = True, text = "Fluid Particles")
        column.prop(sprops.time_pressure, "pct", slider = True, text = "Pressure Solver")
        if sprops.display_frame_diffuse_timing_stats:
            column.prop(sprops.time_diffuse, "pct", slider = True, text = "Whitewater Solver")
        if sprops.display_frame_viscosity_timing_stats:
            column.prop(sprops.time_viscosity, "pct", slider = True, text = "Viscosity Solver")
        column.prop(sprops.time_objects, "pct", slider = True, text = "Simulation Objects")
        column.prop(sprops.time_other, "pct", slider = True, text = "Other")

        column = split.column(align = True)
        padstr = " "
        column.label(text=padstr + format_time(sprops.time_mesh.time))
        column.label(text=padstr + format_time(sprops.time_advection.time))
        column.label(text=padstr + format_time(sprops.time_particles.time))
        column.label(text=padstr + format_time(sprops.time_pressure.time))
        if sprops.display_frame_diffuse_timing_stats:
            column.label(text=padstr + format_time(sprops.time_diffuse.time))
        if sprops.display_frame_viscosity_timing_stats:
            column.label(text=padstr + format_time(sprops.time_viscosity.time))
        column.label(text=padstr + format_time(sprops.time_objects.time))
        column.label(text=padstr + format_time(sprops.time_other.time))

        total_time = (sprops.time_mesh.time + sprops.time_advection.time +
                      sprops.time_particles.time + sprops.time_pressure.time +
                      sprops.time_diffuse.time + sprops.time_viscosity.time +
                      sprops.time_objects.time + sprops.time_other.time)

        column = subbox.column()
        split = column.split()
        column = split.column()
        column = split.column()
        split = column.split()
        column = split.column()
        column.label(text="      Total:")
        column = split.column()
        column.label(text=format_time(total_time))


def draw_frame_info_mesh_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats
    simprops = vcu.get_active_object(context).flip_fluid.domain.simulation

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "frame_info_mesh_stats_expanded",
        icon="TRIA_DOWN" if sprops.frame_info_mesh_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Mesh Stats")

    if sprops.frame_info_mesh_stats_expanded:
        column = subbox.column()
        split = column.split()
        column1 = split.column()
        column2 = split.column()
        column3 = split.column()
        column4 = split.column()

        column1.label(text="")
        column2.label(text="Verts")
        column3.label(text="Faces")
        column4.label(text="Size")

        total_bytes = 0
        if sprops.surface_mesh.enabled:
            column1.label(text="Surface")
            column2.label(text=format_number(sprops.surface_mesh.verts))
            column3.label(text=format_number(sprops.surface_mesh.faces))
            column4.label(text=format_bytes(sprops.surface_mesh.bytes.get()))
            total_bytes += sprops.surface_mesh.bytes.get()

        if sprops.preview_mesh.enabled:
            column1.label(text="Preview")
            column2.label(text=format_number(sprops.preview_mesh.verts))
            column3.label(text=format_number(sprops.preview_mesh.faces))
            column4.label(text=format_bytes(sprops.preview_mesh.bytes.get()))
            total_bytes += sprops.preview_mesh.bytes.get()

        if sprops.surfaceblur_mesh.enabled:
            column1.label(text="Motion Blur")
            column2.label(text=format_number(sprops.surfaceblur_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfaceblur_mesh.bytes.get()))
            total_bytes += sprops.surfaceblur_mesh.bytes.get()

        if sprops.surfacevelocity_mesh.enabled:
            column1.label(text="Velocity")
            column2.label(text=format_number(sprops.surfacevelocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacevelocity_mesh.bytes.get()))
            total_bytes += sprops.surfacevelocity_mesh.bytes.get()

        if sprops.surfacespeed_mesh.enabled:
            column1.label(text="Speed")
            column2.label(text=format_number(sprops.surfacespeed_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacespeed_mesh.bytes.get()))
            total_bytes += sprops.surfacespeed_mesh.bytes.get()

        if sprops.surfacevorticity_mesh.enabled:
            column1.label(text="Vorticity")
            column2.label(text=format_number(sprops.surfacevorticity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacevorticity_mesh.bytes.get()))
            total_bytes += sprops.surfacevorticity_mesh.bytes.get()

        if sprops.surfaceage_mesh.enabled:
            column1.label(text="Age")
            column2.label(text=format_number(sprops.surfaceage_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfaceage_mesh.bytes.get()))
            total_bytes += sprops.surfaceage_mesh.bytes.get()

        if sprops.surfacelifetime_mesh.enabled:
            column1.label(text="Lifetime")
            column2.label(text=format_number(sprops.surfacelifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacelifetime_mesh.bytes.get()))
            total_bytes += sprops.surfacelifetime_mesh.bytes.get()

        if sprops.surfacewhitewaterproximity_mesh.enabled:
            column1.label(text="Whitewater Proximity")
            column2.label(text=format_number(sprops.surfacewhitewaterproximity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacewhitewaterproximity_mesh.bytes.get()))
            total_bytes += sprops.surfacewhitewaterproximity_mesh.bytes.get()

        if sprops.surfacecolor_mesh.enabled:
            column1.label(text="Color")
            column2.label(text=format_number(sprops.surfacecolor_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacecolor_mesh.bytes.get()))
            total_bytes += sprops.surfacecolor_mesh.bytes.get()

        if sprops.surfacesourceid_mesh.enabled:
            column1.label(text="Source ID")
            column2.label(text=format_number(sprops.surfacesourceid_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfacesourceid_mesh.bytes.get()))
            total_bytes += sprops.surfacesourceid_mesh.bytes.get()

        if sprops.surfaceviscosity_mesh.enabled:
            column1.label(text="Viscosity")
            column2.label(text=format_number(sprops.surfaceviscosity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.surfaceviscosity_mesh.bytes.get()))
            total_bytes += sprops.surfaceviscosity_mesh.bytes.get()

        if sprops.foam_mesh.enabled:
            column1.label(text="Foam")
            column2.label(text=format_number(sprops.foam_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.foam_mesh.bytes.get()))
            total_bytes += sprops.foam_mesh.bytes.get()

        if sprops.bubble_mesh.enabled:
            column1.label(text="Bubble")
            column2.label(text=format_number(sprops.bubble_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.bubble_mesh.bytes.get()))
            total_bytes += sprops.bubble_mesh.bytes.get()

        if sprops.spray_mesh.enabled:
            column1.label(text="Spray")
            column2.label(text=format_number(sprops.spray_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.spray_mesh.bytes.get()))
            total_bytes += sprops.spray_mesh.bytes.get()

        if sprops.dust_mesh.enabled:
            column1.label(text="Dust")
            column2.label(text=format_number(sprops.dust_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.dust_mesh.bytes.get()))
            total_bytes += sprops.dust_mesh.bytes.get()

        if sprops.foamblur_mesh.enabled:
            column1.label(text="Foam Motion Blur")
            column2.label(text=format_number(sprops.foamblur_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.foamblur_mesh.bytes.get()))
            total_bytes += sprops.foamblur_mesh.bytes.get()

        if sprops.bubbleblur_mesh.enabled:
            column1.label(text="Bubble Motion Blur")
            column2.label(text=format_number(sprops.bubbleblur_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.bubbleblur_mesh.bytes.get()))
            total_bytes += sprops.bubbleblur_mesh.bytes.get()

        if sprops.sprayblur_mesh.enabled:
            column1.label(text="Spray Motion Blur")
            column2.label(text=format_number(sprops.sprayblur_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.sprayblur_mesh.bytes.get()))
            total_bytes += sprops.sprayblur_mesh.bytes.get()

        if sprops.dustblur_mesh.enabled:
            column1.label(text="Dust Motion Blur")
            column2.label(text=format_number(sprops.dustblur_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.dustblur_mesh.bytes.get()))
            total_bytes += sprops.dustblur_mesh.bytes.get()

        if sprops.foamvelocity_mesh.enabled:
            column1.label(text="Foam Velocity")
            column2.label(text=format_number(sprops.foamvelocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.foamvelocity_mesh.bytes.get()))
            total_bytes += sprops.foamvelocity_mesh.bytes.get()

        if sprops.bubblevelocity_mesh.enabled:
            column1.label(text="Bubble Velocity")
            column2.label(text=format_number(sprops.bubblevelocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.bubblevelocity_mesh.bytes.get()))
            total_bytes += sprops.bubblevelocity_mesh.bytes.get()

        if sprops.sprayvelocity_mesh.enabled:
            column1.label(text="Spray Velocity")
            column2.label(text=format_number(sprops.sprayvelocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.sprayvelocity_mesh.bytes.get()))
            total_bytes += sprops.sprayvelocity_mesh.bytes.get()

        if sprops.dustvelocity_mesh.enabled:
            column1.label(text="Dust Velocity")
            column2.label(text=format_number(sprops.dustvelocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.dustvelocity_mesh.bytes.get()))
            total_bytes += sprops.dustvelocity_mesh.bytes.get()

        if sprops.foamid_mesh.enabled:
            column1.label(text="Foam ID")
            column2.label(text=format_number(sprops.foamid_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.foamid_mesh.bytes.get()))
            total_bytes += sprops.foamid_mesh.bytes.get()

        if sprops.bubbleid_mesh.enabled:
            column1.label(text="Bubble ID")
            column2.label(text=format_number(sprops.bubbleid_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.bubbleid_mesh.bytes.get()))
            total_bytes += sprops.bubbleid_mesh.bytes.get()

        if sprops.sprayid_mesh.enabled:
            column1.label(text="Spray ID")
            column2.label(text=format_number(sprops.sprayid_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.sprayid_mesh.bytes.get()))
            total_bytes += sprops.sprayid_mesh.bytes.get()

        if sprops.dustid_mesh.enabled:
            column1.label(text="Dust ID")
            column2.label(text=format_number(sprops.dustid_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.dustid_mesh.bytes.get()))
            total_bytes += sprops.dustid_mesh.bytes.get()

        if sprops.foamlifetime_mesh.enabled:
            column1.label(text="Foam Lifetime")
            column2.label(text=format_number(sprops.foamlifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.foamlifetime_mesh.bytes.get()))
            total_bytes += sprops.foamlifetime_mesh.bytes.get()

        if sprops.bubblelifetime_mesh.enabled:
            column1.label(text="Bubble Lifetime")
            column2.label(text=format_number(sprops.bubblelifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.bubblelifetime_mesh.bytes.get()))
            total_bytes += sprops.bubblelifetime_mesh.bytes.get()

        if sprops.spraylifetime_mesh.enabled:
            column1.label(text="Spray Lifetime")
            column2.label(text=format_number(sprops.spraylifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.spraylifetime_mesh.bytes.get()))
            total_bytes += sprops.spraylifetime_mesh.bytes.get()

        if sprops.dustlifetime_mesh.enabled:
            column1.label(text="Dust Lifetime")
            column2.label(text=format_number(sprops.dustlifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.dustlifetime_mesh.bytes.get()))
            total_bytes += sprops.dustlifetime_mesh.bytes.get()

        if sprops.fluid_particle_mesh.enabled:
            column1.label(text="Fluid Particles")
            column2.label(text=format_number(sprops.fluid_particle_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_mesh.bytes.get()

        if sprops.fluid_particle_id_mesh.enabled:
            column1.label(text="Fluid Particles ID")
            column2.label(text=format_number(sprops.fluid_particle_id_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_id_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_id_mesh.bytes.get()

        if sprops.fluid_particle_velocity_mesh.enabled:
            column1.label(text="Fluid Particles Velocity")
            column2.label(text=format_number(sprops.fluid_particle_velocity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_velocity_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_velocity_mesh.bytes.get()

        if sprops.fluid_particle_speed_mesh.enabled:
            column1.label(text="Fluid Particles Speed")
            column2.label(text=format_number(sprops.fluid_particle_speed_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_speed_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_speed_mesh.bytes.get()

        if sprops.fluid_particle_vorticity_mesh.enabled:
            column1.label(text="Fluid Particles Vorticity")
            column2.label(text=format_number(sprops.fluid_particle_vorticity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_vorticity_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_vorticity_mesh.bytes.get()

        if sprops.fluid_particle_color_mesh.enabled:
            column1.label(text="Fluid Particles Color")
            column2.label(text=format_number(sprops.fluid_particle_color_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_color_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_color_mesh.bytes.get()

        if sprops.fluid_particle_age_mesh.enabled:
            column1.label(text="Fluid Particles Age")
            column2.label(text=format_number(sprops.fluid_particle_age_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_age_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_age_mesh.bytes.get()

        if sprops.fluid_particle_lifetime_mesh.enabled:
            column1.label(text="Fluid Particles Lifetime")
            column2.label(text=format_number(sprops.fluid_particle_lifetime_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_lifetime_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_lifetime_mesh.bytes.get()

        if sprops.fluid_particle_viscosity_mesh.enabled:
            column1.label(text="Fluid Particles Viscosity")
            column2.label(text=format_number(sprops.fluid_particle_viscosity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_viscosity_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_viscosity_mesh.bytes.get()

        if sprops.fluid_particle_whitewater_proximity_mesh.enabled:
            column1.label(text="Fluid Particles Whitewater Proximity")
            column2.label(text=format_number(sprops.fluid_particle_whitewater_proximity_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_whitewater_proximity_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_whitewater_proximity_mesh.bytes.get()

        if sprops.fluid_particle_source_id_mesh.enabled:
            column1.label(text="Fluid Particles Source ID")
            column2.label(text=format_number(sprops.fluid_particle_source_id_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.fluid_particle_source_id_mesh.bytes.get()))
            total_bytes += sprops.fluid_particle_source_id_mesh.bytes.get()

        if sprops.debug_particle_mesh.enabled:
            column1.label(text="Debug Particles")
            column2.label(text=format_number(sprops.debug_particle_mesh.verts))
            column3.label(text="")
            column4.label(text=format_bytes(sprops.debug_particle_mesh.bytes.get()))
            total_bytes += sprops.debug_particle_mesh.bytes.get()

        if sprops.obstacle_mesh.enabled:
            column1.label(text="Obstacle")
            column2.label(text=format_number(sprops.obstacle_mesh.verts))
            column3.label(text=format_number(sprops.obstacle_mesh.faces))
            column4.label(text=format_bytes(sprops.obstacle_mesh.bytes.get()))
            total_bytes += sprops.obstacle_mesh.bytes.get()

        column3.label(text="     Total:")
        column4.label(text=format_bytes(total_bytes))


def draw_frame_info(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats
    simprops = vcu.get_active_object(context).flip_fluid.domain.simulation

    column = box.column()
    split = column.split()
    column = split.column()
    column.enabled = not sprops.lock_info_frame_to_timeline
    column.prop(sprops, "current_info_frame")
    column = split.column()
    column.prop(sprops, "lock_info_frame_to_timeline")

    if sprops.is_frame_info_available:
        box.label(text="")
    else:
        box.label(text="Data Not Available (frame " + str(sprops.current_info_frame) + ")", icon='ERROR')

    box.separator()
    draw_frame_info_simulation_stats(self, context, box)
    draw_frame_info_solver_stats(self, context, box)
    draw_frame_info_timing_stats(self, context, box)
    draw_frame_info_mesh_stats(self, context, box)


def draw_cache_info_simulation_stats(self, context, box):
    dprops = vcu.get_active_object(context).flip_fluid.domain
    sprops = dprops.stats
    simprops = dprops.simulation

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "cache_info_simulation_stats_expanded",
        icon="TRIA_DOWN" if sprops.cache_info_simulation_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Simulation Stats")

    if sprops.cache_info_simulation_stats_expanded:
        num_frames = dprops.simulation.frame_end - sprops.frame_start + 1
        num_baked_frames = sprops.num_cache_frames

        column = subbox.column()
        split = column.split()
        column = split.column()
        column.label(text="Completed Frames:")
        column.label(text="Start Frame:")
        column.label(text="End Frame:")
        column.label(text="Average Performance Score:")

        column = split.column()
        if num_baked_frames > num_frames:
            column.label(text=str(num_baked_frames))
        else:
            column.label(text=str(num_baked_frames) + "  /  " + str(num_frames))

        column.label(text=str(sprops.frame_start))
        #column.label(text=str(simprops.frame_end))
        column.label(text=str(sprops.frame_start + num_baked_frames - 1))
        column.label(text=str(sprops.average_performance_score))

        if dprops.bake.is_simulation_running:
            column = subbox.column()
            split = column.split()
            column = split.column()

            if sprops.is_estimated_time_remaining_available:
                column.label(text="Estimated Time Remaining:")
            else:
                column.label(text="Calculating time remaining...")
            
            column = split.column()
            column.label(text=sprops.get_time_remaining_string(context))


def draw_cache_info_solver_stats(self, context, box):
    dprops = vcu.get_active_object(context).flip_fluid.domain
    sprops = dprops.stats
    simprops = dprops.simulation

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "cache_info_solver_stats_expanded",
        icon="TRIA_DOWN" if sprops.cache_info_solver_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Solver Stats")

    if not sprops.cache_info_solver_stats_expanded:
        return

    if sprops.pressure_solver_enabled:
        pressure_box = subbox.box()
        row = pressure_box.row()
        row.prop(sprops, "cache_info_pressure_solver_stats_expanded",
            icon="TRIA_DOWN" if sprops.cache_info_pressure_solver_stats_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Pressure Solver")

        if sprops.cache_info_pressure_solver_stats_expanded:
            column = pressure_box.column(align=True)
            split = column.split(align=True)
            column_left = split.column(align=True)
            column_middle = split.column(align=True)
            column_right = split.column(align=True)

            column_left.label(text="Solver Failures:")
            column_left.label(text="Max Iterations:")
            column_left.label(text="Max Error:")
            column_left.label(text="Max Stress:")

            failure_str = str(sprops.pressure_solver_failures) + " failures / " + str(sprops.pressure_solver_steps) + " steps"
            iterations_str = str(sprops.pressure_solver_max_iterations)
            error_str = '{0:.12f}'.format(sprops.pressure_solver_max_error)
            stress_threshold = 80.0
            stress_state = "OK"
            if sprops.pressure_solver_max_stress > stress_threshold:
                stress_state = "HIGH"
            if sprops.pressure_solver_max_stress >= 99.999:
                stress_state = "MAX"
            stress_str = '{0:.1f}'.format(sprops.pressure_solver_max_stress) + "%   " + stress_state

            column_middle.label(text=failure_str)
            column_middle.label(text=iterations_str)
            column_middle.label(text=error_str)
            column_middle.label(text=stress_str)

            column_right.label(text="")
            column_right.label(text="(frame " + str(sprops.pressure_solver_max_iterations_frame) + ")")
            column_right.label(text="(frame " + str(sprops.pressure_solver_max_error_frame) + ")")
            column_right.label(text="(frame " + str(sprops.pressure_solver_max_stress_frame) + ")")

    if sprops.viscosity_solver_enabled:
        viscosity_box = subbox.box()
        row = viscosity_box.row()
        row.prop(sprops, "cache_info_viscosity_solver_stats_expanded",
            icon="TRIA_DOWN" if sprops.cache_info_viscosity_solver_stats_expanded else "TRIA_RIGHT",
            icon_only=True, 
            emboss=False
        )
        row.label(text="Viscosity Solver")

        if sprops.cache_info_viscosity_solver_stats_expanded:
            column = viscosity_box.column(align=True)
            split = column.split(align=True)
            column_left = split.column(align=True)
            column_middle = split.column(align=True)
            column_right = split.column(align=True)

            column_left.label(text="Solver Failures:")
            column_left.label(text="Max Iterations:")
            column_left.label(text="Max Error:")
            column_left.label(text="Max Stress:")

            failure_str = str(sprops.viscosity_solver_failures) + " failures / " + str(sprops.viscosity_solver_steps) + " steps"
            iterations_str = str(sprops.viscosity_solver_max_iterations)
            error_str = '{0:.12f}'.format(sprops.viscosity_solver_max_error)
            stress_threshold = 80.0
            stress_state = "OK"
            if sprops.viscosity_solver_max_stress > stress_threshold:
                stress_state = "HIGH"
            if sprops.viscosity_solver_max_stress >= 99.999:
                stress_state = "MAX"
            stress_str = '{0:.1f}'.format(sprops.viscosity_solver_max_stress) + "%   " + stress_state

            column_middle.label(text=failure_str)
            column_middle.label(text=iterations_str)
            column_middle.label(text=error_str)
            column_middle.label(text=stress_str)

            column_right.label(text="")
            column_right.label(text="(frame " + str(sprops.viscosity_solver_max_iterations_frame) + ")")
            column_right.label(text="(frame " + str(sprops.viscosity_solver_max_error_frame) + ")")
            column_right.label(text="(frame " + str(sprops.viscosity_solver_max_stress_frame) + ")")


def draw_cache_info_timing_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "cache_info_timing_stats_expanded",
        icon="TRIA_DOWN" if sprops.cache_info_timing_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Timing Stats")

    if sprops.cache_info_timing_stats_expanded:
        column = subbox.column()
        split = vcu.ui_split(column, factor=0.75)
        column = split.column(align=True)
        column.prop(sprops.time_mesh, "pct", slider=True, text="Mesh Generation")
        column.prop(sprops.time_advection, "pct", slider=True, text="Velocity Advection")
        column.prop(sprops.time_particles, "pct", slider=True, text="Fluid Particles")
        column.prop(sprops.time_pressure, "pct", slider=True, text="Pressure Solver")
        if sprops.display_frame_diffuse_timing_stats:
            column.prop(sprops.time_diffuse, "pct", slider = True, text = "Whitewater Solver")
        if sprops.display_frame_viscosity_timing_stats:
            column.prop(sprops.time_viscosity, "pct", slider = True, text = "Viscosity Solver")
        column.prop(sprops.time_objects, "pct", slider = True, text = "Simulation Objects")
        column.prop(sprops.time_other, "pct", slider = True, text = "Other")

        column = split.column(align=True)
        padstr = " "
        column.label(text=padstr + format_long_time(sprops.time_mesh.time))
        column.label(text=padstr + format_long_time(sprops.time_advection.time))
        column.label(text=padstr + format_long_time(sprops.time_particles.time))
        column.label(text=padstr + format_long_time(sprops.time_pressure.time))
        if sprops.display_frame_diffuse_timing_stats:
            column.label(text=padstr + format_long_time(sprops.time_diffuse.time))
        if sprops.display_frame_viscosity_timing_stats:
            column.label(text=padstr + format_long_time(sprops.time_viscosity.time))
        column.label(text=padstr + format_long_time(sprops.time_objects.time))
        column.label(text=padstr + format_long_time(sprops.time_other.time))

        total_time = (sprops.time_mesh.time + sprops.time_advection.time +
                      sprops.time_particles.time + sprops.time_pressure.time +
                      sprops.time_diffuse.time + sprops.time_viscosity.time +
                      sprops.time_objects.time + sprops.time_other.time)

        column = subbox.column()
        split = column.split()
        column = split.column()
        column = split.column()
        split = column.split()
        column = split.column()
        column.label(text="      Total:")
        column = split.column()
        column.label(text=format_long_time(total_time))


def draw_cache_info_mesh_stats(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats

    subbox = box.box()
    row = subbox.row()
    row.prop(sprops, "cache_info_mesh_stats_expanded",
        icon="TRIA_DOWN" if sprops.cache_info_mesh_stats_expanded else "TRIA_RIGHT",
        icon_only=True, 
        emboss=False
    )
    row.label(text="Mesh Stats")

    if sprops.cache_info_mesh_stats_expanded:
        column = subbox.column()
        split = vcu.ui_split(column, factor=0.5)
        column1 = split.column()
        column2 = split.column()

        stats_exist = (sprops.surface_mesh.enabled or 
                       sprops.preview_mesh.enabled or 
                       sprops.surfaceblur_mesh.enabled or 
                       sprops.surfacevelocity_mesh.enabled or 
                       sprops.surfacespeed_mesh.enabled or 
                       sprops.surfacevorticity_mesh.enabled or 
                       sprops.surfaceage_mesh.enabled or 
                       sprops.surfacelifetime_mesh.enabled or 
                       sprops.surfacewhitewaterproximity_mesh.enabled or 
                       sprops.surfacecolor_mesh.enabled or 
                       sprops.surfacesourceid_mesh.enabled or 
                       sprops.surfaceviscosity_mesh.enabled or 
                       sprops.foam_mesh.enabled or 
                       sprops.bubble_mesh.enabled or 
                       sprops.spray_mesh.enabled or 
                       sprops.dust_mesh.enabled or 
                       sprops.foamblur_mesh.enabled or 
                       sprops.bubbleblur_mesh.enabled or 
                       sprops.sprayblur_mesh.enabled or 
                       sprops.dustblur_mesh.enabled or 
                       sprops.foamvelocity_mesh.enabled or 
                       sprops.bubblevelocity_mesh.enabled or 
                       sprops.sprayvelocity_mesh.enabled or 
                       sprops.dustvelocity_mesh.enabled or 
                       sprops.foamid_mesh.enabled or 
                       sprops.bubbleid_mesh.enabled or 
                       sprops.sprayid_mesh.enabled or 
                       sprops.dustid_mesh.enabled or 
                       sprops.foamlifetime_mesh.enabled or 
                       sprops.bubblelifetime_mesh.enabled or 
                       sprops.spraylifetime_mesh.enabled or 
                       sprops.dustlifetime_mesh.enabled or 
                       sprops.fluid_particle_mesh.enabled or
                       sprops.fluid_particle_id_mesh.enabled or
                       sprops.fluid_particle_velocity_mesh.enabled or
                       sprops.fluid_particle_speed_mesh.enabled or
                       sprops.fluid_particle_vorticity_mesh.enabled or
                       sprops.fluid_particle_color_mesh.enabled or
                       sprops.fluid_particle_age_mesh.enabled or
                       sprops.fluid_particle_lifetime_mesh.enabled or
                       sprops.fluid_particle_viscosity_mesh.enabled or
                       sprops.fluid_particle_whitewater_proximity_mesh.enabled or
                       sprops.fluid_particle_source_id_mesh.enabled or
                       sprops.debug_particle_mesh.enabled or
                       sprops.obstacle_mesh.enabled)

        if stats_exist:
            column1.label(text="")
            column2.label(text="Size")

        total_size = 0
        row_count = 0
        if sprops.surface_mesh.enabled:
            column1.label(text="Surface")
            column2.label(text=format_bytes(sprops.surface_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surface_mesh.bytes.get()

        if sprops.preview_mesh.enabled:
            column1.label(text="Preview")
            column2.label(text=format_bytes(sprops.preview_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.preview_mesh.bytes.get()

        if sprops.surfaceblur_mesh.enabled:
            column1.label(text="Motion Blur")
            column2.label(text=format_bytes(sprops.surfaceblur_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfaceblur_mesh.bytes.get()

        if sprops.surfacevelocity_mesh.enabled:
            column1.label(text="Velocity")
            column2.label(text=format_bytes(sprops.surfacevelocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacevelocity_mesh.bytes.get()

        if sprops.surfacespeed_mesh.enabled:
            column1.label(text="Speed")
            column2.label(text=format_bytes(sprops.surfacespeed_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacespeed_mesh.bytes.get()

        if sprops.surfacevorticity_mesh.enabled:
            column1.label(text="Vorticity")
            column2.label(text=format_bytes(sprops.surfacevorticity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacevorticity_mesh.bytes.get()

        if sprops.surfaceage_mesh.enabled:
            column1.label(text="Age")
            column2.label(text=format_bytes(sprops.surfaceage_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfaceage_mesh.bytes.get()

        if sprops.surfacelifetime_mesh.enabled:
            column1.label(text="Lifetime")
            column2.label(text=format_bytes(sprops.surfacelifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacelifetime_mesh.bytes.get()

        if sprops.surfacewhitewaterproximity_mesh.enabled:
            column1.label(text="Whitewater Proximity")
            column2.label(text=format_bytes(sprops.surfacewhitewaterproximity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacewhitewaterproximity_mesh.bytes.get()

        if sprops.surfacecolor_mesh.enabled:
            column1.label(text="Color")
            column2.label(text=format_bytes(sprops.surfacecolor_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacecolor_mesh.bytes.get()

        if sprops.surfacesourceid_mesh.enabled:
            column1.label(text="Source ID")
            column2.label(text=format_bytes(sprops.surfacesourceid_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfacesourceid_mesh.bytes.get()

        if sprops.surfaceviscosity_mesh.enabled:
            column1.label(text="Viscosity")
            column2.label(text=format_bytes(sprops.surfaceviscosity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.surfaceviscosity_mesh.bytes.get()

        if sprops.foam_mesh.enabled:
            column1.label(text="Foam")
            column2.label(text=format_bytes(sprops.foam_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.foam_mesh.bytes.get()

        if sprops.bubble_mesh.enabled:
            column1.label(text="Bubble")
            column2.label(text=format_bytes(sprops.bubble_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.bubble_mesh.bytes.get()

        if sprops.spray_mesh.enabled:
            column1.label(text="Spray")
            column2.label(text=format_bytes(sprops.spray_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.spray_mesh.bytes.get()

        if sprops.dust_mesh.enabled:
            column1.label(text="Dust")
            column2.label(text=format_bytes(sprops.dust_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.dust_mesh.bytes.get()

        if sprops.foamblur_mesh.enabled:
            column1.label(text="Foam Motion Blur")
            column2.label(text=format_bytes(sprops.foamblur_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.foamblur_mesh.bytes.get()

        if sprops.bubbleblur_mesh.enabled:
            column1.label(text="Bubble Motion Blur")
            column2.label(text=format_bytes(sprops.bubbleblur_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.bubbleblur_mesh.bytes.get()

        if sprops.sprayblur_mesh.enabled:
            column1.label(text="Spray Motion Blur")
            column2.label(text=format_bytes(sprops.sprayblur_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.sprayblur_mesh.bytes.get()

        if sprops.dustblur_mesh.enabled:
            column1.label(text="Dust Motion Blur")
            column2.label(text=format_bytes(sprops.dustblur_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.dustblur_mesh.bytes.get()

        if sprops.foamvelocity_mesh.enabled:
            column1.label(text="Foam Velocity")
            column2.label(text=format_bytes(sprops.foamvelocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.foamvelocity_mesh.bytes.get()

        if sprops.bubblevelocity_mesh.enabled:
            column1.label(text="Bubble Velocity")
            column2.label(text=format_bytes(sprops.bubblevelocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.bubblevelocity_mesh.bytes.get()

        if sprops.sprayvelocity_mesh.enabled:
            column1.label(text="Spray Velocity")
            column2.label(text=format_bytes(sprops.sprayvelocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.sprayvelocity_mesh.bytes.get()

        if sprops.dustvelocity_mesh.enabled:
            column1.label(text="Dust Velocity")
            column2.label(text=format_bytes(sprops.dustvelocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.dustvelocity_mesh.bytes.get()

        if sprops.foamid_mesh.enabled:
            column1.label(text="Foam ID")
            column2.label(text=format_bytes(sprops.foamid_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.foamid_mesh.bytes.get()

        if sprops.bubbleid_mesh.enabled:
            column1.label(text="Bubble ID")
            column2.label(text=format_bytes(sprops.bubbleid_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.bubbleid_mesh.bytes.get()

        if sprops.sprayid_mesh.enabled:
            column1.label(text="Spray ID")
            column2.label(text=format_bytes(sprops.sprayid_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.sprayid_mesh.bytes.get()

        if sprops.dustid_mesh.enabled:
            column1.label(text="Dust ID")
            column2.label(text=format_bytes(sprops.dustid_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.dustid_mesh.bytes.get()

        if sprops.foamlifetime_mesh.enabled:
            column1.label(text="Foam Lifetime")
            column2.label(text=format_bytes(sprops.foamlifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.foamlifetime_mesh.bytes.get()

        if sprops.bubblelifetime_mesh.enabled:
            column1.label(text="Bubble Lifetime")
            column2.label(text=format_bytes(sprops.bubblelifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.bubblelifetime_mesh.bytes.get()

        if sprops.spraylifetime_mesh.enabled:
            column1.label(text="Spray Lifetime")
            column2.label(text=format_bytes(sprops.spraylifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.spraylifetime_mesh.bytes.get()

        if sprops.dustlifetime_mesh.enabled:
            column1.label(text="Dust Lifetime")
            column2.label(text=format_bytes(sprops.dustlifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.dustlifetime_mesh.bytes.get()

        if sprops.fluid_particle_mesh.enabled:
            column1.label(text="Fluid Particles")
            column2.label(text=format_bytes(sprops.fluid_particle_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_mesh.bytes.get()

        if sprops.fluid_particle_id_mesh.enabled:
            column1.label(text="Fluid Particles ID")
            column2.label(text=format_bytes(sprops.fluid_particle_id_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_id_mesh.bytes.get()

        if sprops.fluid_particle_velocity_mesh.enabled:
            column1.label(text="Fluid Particles Velocity")
            column2.label(text=format_bytes(sprops.fluid_particle_velocity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_velocity_mesh.bytes.get()

        if sprops.fluid_particle_speed_mesh.enabled:
            column1.label(text="Fluid Particles Speed")
            column2.label(text=format_bytes(sprops.fluid_particle_speed_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_speed_mesh.bytes.get()

        if sprops.fluid_particle_vorticity_mesh.enabled:
            column1.label(text="Fluid Particles Vorticity")
            column2.label(text=format_bytes(sprops.fluid_particle_vorticity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_vorticity_mesh.bytes.get()

        if sprops.fluid_particle_color_mesh.enabled:
            column1.label(text="Fluid Particles Color")
            column2.label(text=format_bytes(sprops.fluid_particle_color_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_color_mesh.bytes.get()

        if sprops.fluid_particle_age_mesh.enabled:
            column1.label(text="Fluid Particles Age")
            column2.label(text=format_bytes(sprops.fluid_particle_age_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_age_mesh.bytes.get()

        if sprops.fluid_particle_lifetime_mesh.enabled:
            column1.label(text="Fluid Particles Lifetime")
            column2.label(text=format_bytes(sprops.fluid_particle_lifetime_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_lifetime_mesh.bytes.get()

        if sprops.fluid_particle_viscosity_mesh.enabled:
            column1.label(text="Fluid Particles Viscosity")
            column2.label(text=format_bytes(sprops.fluid_particle_viscosity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_viscosity_mesh.bytes.get()

        if sprops.fluid_particle_whitewater_proximity_mesh.enabled:
            column1.label(text="Fluid Particles Whitewater Proximity")
            column2.label(text=format_bytes(sprops.fluid_particle_whitewater_proximity_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_whitewater_proximity_mesh.bytes.get()

        if sprops.fluid_particle_source_id_mesh.enabled:
            column1.label(text="Fluid Particles Source ID")
            column2.label(text=format_bytes(sprops.fluid_particle_source_id_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.fluid_particle_source_id_mesh.bytes.get()

        if sprops.debug_particle_mesh.enabled:
            column1.label(text="Debug Particles")
            column2.label(text=format_bytes(sprops.debug_particle_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.debug_particle_mesh.bytes.get()

        if sprops.obstacle_mesh.enabled:
            column1.label(text="Obstacle")
            column2.label(text=format_bytes(sprops.obstacle_mesh.bytes.get()))
            row_count += 1
            total_size += sprops.obstacle_mesh.bytes.get()

        if stats_exist:
            column = subbox.column()
            split = column.split()
            column1 = split.column()
            column2 = split.column()
            row = column2.row()
            row.label(text="Total:    " + format_bytes(total_size))


def draw_cache_info(self, context, box):
    sprops = vcu.get_active_object(context).flip_fluid.domain.stats

    box.separator()
    if not sprops.is_cache_info_available:
        box.label(text="Data Not Available")
        return

    draw_cache_info_simulation_stats(self, context, box)
    draw_cache_info_solver_stats(self, context, box)
    draw_cache_info_timing_stats(self, context, box)
    draw_cache_info_mesh_stats(self, context, box)


class FLIPFLUID_PT_DomainTypeStatsPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_category = "FLIP Fluid"
    bl_label = "FLIP Fluid Stats"
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        if vcu.get_addon_preferences(context).enable_tabbed_domain_settings_view:
            return False
        obj_props = vcu.get_active_object(context).flip_fluid
        is_addon_disabled = context.scene.flip_fluid.is_addon_disabled_in_blend_file()
        return obj_props.is_active and obj_props.object_type == "TYPE_DOMAIN" and not is_addon_disabled


    def draw(self, context):
        sprops = vcu.get_active_object(context).flip_fluid.domain.stats

        row = self.layout.row()
        row.prop(sprops, "cache_info_type", expand=True)
        row = self.layout.row()
        row.operator("flip_fluid_operators.refresh_stats", icon='FILE_REFRESH')

        column = self.layout.column()
        if sprops.cache_info_type == "CACHE_INFO":
            draw_cache_info(self, context, column)
        elif sprops.cache_info_type == "FRAME_INFO":
            draw_frame_info(self, context, column)

        self.layout.separator()
        column = self.layout.column(align=True)
        split = vcu.ui_split(column, align=True, factor=0.33)
        column = split.column(align=True)
        column.enabled = sprops.is_cache_info_available
        column.operator("flip_fluid_operators.export_stats_csv", 
                        text="Export to CSV", 
                        icon='FILE')

        column = split.column(align=True)
        split = vcu.ui_split(column, align=True, factor=0.66)
        column = split.column(align=True)
        column.prop(sprops, "csv_save_filepath")

        column = split.column(align=True)
        row = column.row(align=True)
        row.prop(sprops, "csv_region_format", expand=True)

        self.layout.separator()
        self.layout.separator()
        self.layout.separator()
        
    
def register():
    bpy.utils.register_class(FLIPFLUID_PT_DomainTypeStatsPanel)


def unregister():
    bpy.utils.unregister_class(FLIPFLUID_PT_DomainTypeStatsPanel)
