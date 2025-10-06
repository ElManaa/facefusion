from typing import Optional, Tuple
import os

import gradio

from facefusion import state_manager, wording
from facefusion.face_store import clear_static_faces
from facefusion.filesystem import is_image, is_video, is_file
from facefusion.uis.core import register_ui_component
from facefusion.uis.types import ComponentOptions, File

TARGET_FILE : Optional[gradio.File] = None
TARGET_PATH_TEXTBOX : Optional[gradio.Textbox] = None
TARGET_IMAGE : Optional[gradio.Image] = None
TARGET_VIDEO : Optional[gradio.Video] = None


def render() -> None:
	global TARGET_FILE
	global TARGET_PATH_TEXTBOX
	global TARGET_IMAGE
	global TARGET_VIDEO

	is_target_image = is_image(state_manager.get_item('target_path'))
	is_target_video = is_video(state_manager.get_item('target_path'))
	TARGET_FILE = gradio.File(
		label = wording.get('uis.target_file'),
		value = state_manager.get_item('target_path') if is_target_image or is_target_video else None
	)
	TARGET_PATH_TEXTBOX = gradio.Textbox(
		label = wording.get('uis.target_path_textbox'),
		placeholder = 'Enter local file path (e.g., /path/to/video.mp4)',
		max_lines = 1,
		value = state_manager.get_item('target_path') if is_target_image or is_target_video else None
	)
	target_image_options : ComponentOptions =\
	{
		'show_label': False,
		'visible': False
	}
	target_video_options : ComponentOptions =\
	{
		'show_label': False,
		'visible': False
	}
	if is_target_image:
		target_image_options['value'] = TARGET_FILE.value.get('path') if TARGET_FILE.value else state_manager.get_item('target_path')
		target_image_options['visible'] = True
	if is_target_video:
		target_video_options['value'] = TARGET_FILE.value.get('path') if TARGET_FILE.value else state_manager.get_item('target_path')
		target_video_options['visible'] = True
	TARGET_IMAGE = gradio.Image(**target_image_options)
	TARGET_VIDEO = gradio.Video(**target_video_options)
	register_ui_component('target_image', TARGET_IMAGE)
	register_ui_component('target_video', TARGET_VIDEO)
	register_ui_component('target_path_textbox', TARGET_PATH_TEXTBOX)


def listen() -> None:
	TARGET_FILE.change(update_from_file, inputs = TARGET_FILE, outputs = [ TARGET_PATH_TEXTBOX, TARGET_IMAGE, TARGET_VIDEO ])
	TARGET_PATH_TEXTBOX.change(update_from_path, inputs = TARGET_PATH_TEXTBOX, outputs = [ TARGET_IMAGE, TARGET_VIDEO ])


def update_from_file(file : File) -> Tuple[gradio.Textbox, gradio.Image, gradio.Video]:
	clear_static_faces()

	if file and is_image(file.name):
		state_manager.set_item('target_path', file.name)
		return gradio.Textbox(value = file.name), gradio.Image(value = file.name, visible = True), gradio.Video(value = None, visible = False)

	if file and is_video(file.name):
		state_manager.set_item('target_path', file.name)
		return gradio.Textbox(value = file.name), gradio.Image(value = None, visible = False), gradio.Video(value = file.name, visible = True)

	state_manager.clear_item('target_path')
	return gradio.Textbox(value = None), gradio.Image(value = None, visible = False), gradio.Video(value = None, visible = False)


def update_from_path(file_path : str) -> Tuple[gradio.Image, gradio.Video]:
	clear_static_faces()

	if file_path and os.path.isabs(file_path) and is_file(file_path):
		if is_image(file_path):
			state_manager.set_item('target_path', file_path)
			return gradio.Image(value = file_path, visible = True), gradio.Video(value = None, visible = False)
		
		if is_video(file_path):
			state_manager.set_item('target_path', file_path)
			return gradio.Image(value = None, visible = False), gradio.Video(value = file_path, visible = True)

	state_manager.clear_item('target_path')
	return gradio.Image(value = None, visible = False), gradio.Video(value = None, visible = False)
