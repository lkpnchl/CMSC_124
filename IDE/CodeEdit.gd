extends CodeEdit


@onready var root = get_tree().get_root()
@onready var buttons = root.get_node("Main/TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX")
@onready var save = buttons.get_node("Save")
@onready var saveas = buttons.get_node("Saveas")
@onready var close = buttons.get_node("Close")
@onready var undo = buttons.get_node("Undo")
@onready var redo = buttons.get_node("Redo")
@onready var copy = buttons.get_node("Copy")
@onready var cut = buttons.get_node("Cut")
#@onready var paste = buttons.get_node("Paste")
@onready var compile = buttons.get_node("Compile")
@onready var run = buttons.get_node("Run")

func _on_text_changed():
	if len(text) > 0:
		save.disabled = false
		saveas.disabled = false
		close.disabled = false
		undo.disabled = false
		redo.disabled = false
		copy.disabled = false
		cut.disabled = false
		#paste.disabled = false
		compile.disabled = false
		run.disabled = false
	else:
		save.disabled = true
		saveas.disabled = true
		close.disabled = true
		undo.disabled = true
		redo.disabled = true
		copy.disabled = true
		cut.disabled = true
		#paste.disabled = true
		compile.disabled = true
		run.disabled = true
