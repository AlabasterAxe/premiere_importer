""" NOTE: THIS FILE IS INTENDED TO BE EXECUTED WITHIN BLENDER IT ALMOST CERTAINLY WON't WORK OTHERWISE. """

import json
import os
from os.path import (
    basename,
    dirname,
    exists,
    join,
    relpath,
)

from xml.etree import ElementTree

import bpy
from bpy.props import (
    StringProperty,
    PointerProperty,
    EnumProperty,
    IntProperty,
)
from bpy.types import PropertyGroup, Operator
from bpy_extras.io_utils import ImportHelper, ExportHelpe

bl_info = {
    "name": "Premiere Importer",
    "author": "Matt Keller <matthew.ed.keller@gmail.com>",
    "version": (0, 1, 0),
    "blender": (2, 90, 1),
    "location": "File > Import > Premiere (.xml)",
    "description": "Import Premiere XML files into Blender",
    "warning": "Safety not guaranteed.",
    "wiki_url": "thkp.co",
    "tracker_url": "thkp.co",
    "support": "COMMUNITY",
    "category": "Import-Export",
}


def import_premiere_file(filepath, media_dir_path):
    root = ElementTree.parse(filepath).getroot()

    seq = root.find("sequence")

    scene = bpy.context.scene

    scene.frame_end = int(seq.find("duration").text)
    scene.render.resolution_x = int(seq.find("width").text)
    scene.render.resolution_y = int(seq.find("height").text)
    scene.render.resolution_y = int(seq.find("height").text)

    #scene.render.fps = int(seq.find("rate").find("timebase").text)

    video_tracks = seq.find("media").find("video").findall("track")

    tracknum = 1
    for track in video_tracks:
        for clip in track.findall("clipitem"):
            newseq = scene.sequence_editor.sequences.new_movie(
                clip.attrib["id"],
                media_dir_path + clip.find("name").text,
                tracknum,
                int(clip.find("start").text) - int(clip.find("in").text)
            )
            newseq.frame_offset_start = int(clip.find("in").text)
            newseq.frame_final_duration = int(
                clip.find("end").text) - int(clip.find("start").text)
        tracknum += 1

    audio_tracks = seq.find("media").find("audio").findall("track")

    sounds = {}

    for track in audio_tracks:
        for clip in track.findall("clipitem"):
            filename = clip.find("name").text
            newseq = scene.sequence_editor.sequences.new_sound(
                clip.attrib["id"],
                media_dir_path + filename,
                tracknum,
                int(clip.find("start").text) - int(clip.find("in").text)
            )

            clipsound = sounds.get(filename)
            if clipsound is not None:
                newseq.sound = clipsound
            else:
                sounds[filename] = newseq.sound
            newseq.frame_offset_start = int(clip.find("in").text)
            newseq.frame_final_duration = int(
                clip.find("end").text) - int(clip.find("start").text)
            newseq.show_waveform = True
        tracknum += 1


class IMPORT_OT_premiere(Operator, ImportHelper):
    bl_idname = "import.premiere"
    bl_label = "Import Premiere (*.xml)"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".xml"
    filter_glob: StringProperty(
        default="*" + filename_ext, options={'HIDDEN'},)

    def execute(self, context):
        # This is in order to solve this strange 'relative path' thing.
        filepath_pdb = bpy.path.abspath(self.filepath)

        # Execute main routine
        import_premiere_file(filepath_pdb, bpy.path.abspath("//../raw/"))

        return {'FINISHED'}


def menu_func_import_premiere_xml(self, context):
    lay = self.layout
    lay.operator(IMPORT_OT_premiere.bl_idname, text="Premiere (.xml)")


def register():
    from bpy.utils import register_class

    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_premiere_xml)