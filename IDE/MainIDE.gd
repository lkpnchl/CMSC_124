extends Control

@onready var loadscreen = preload("res://load.tscn")
@onready var root = get_tree().get_root()
@onready var buttons = root.get_node("Main/TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX")
@onready var save = buttons.get_node("Save")
@onready var saveas = buttons.get_node("Saveas")
@onready var close = buttons.get_node("Close")
@onready var undo = buttons.get_node("Undo")
@onready var redo = buttons.get_node("Redo")
@onready var copy = buttons.get_node("Copy")
@onready var cut = buttons.get_node("Cut")
@onready var paste = buttons.get_node("Paste")
@onready var compile = buttons.get_node("Compile")
@onready var run = buttons.get_node("Run")

var open_file_dialog : FileDialog  # Reference to the FileDialog instance
var save_as_file_dialog : FileDialog  # Reference to the FileDialog instance

var content : String
var code_edit : CodeEdit  # Reference to the CodeEdit instance
var file : FileAccess # For FileAccess
#var path = 

var app_name = "BOB Compiler"
var current_file = "Untitled"

func _ready():
	update_window_title()
	# Load references to FileDialog and CodeEdit
	open_file_dialog = $OpenFileDialog
	save_as_file_dialog = $SaveAsFileDialog
	code_edit = get_node("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/PanelContainer/CodeEdit")

func update_window_title():
	DisplayServer.window_set_title(app_name + ' - ' + current_file)
	
### FILE NEW FUNCTION ###
# Function called when the New File button is pressed
func _on_new_pressed() -> void:
	if content!=code_edit.text || (len(code_edit.text)>0 && current_file=="Untitled"):
		print("unsaved")
		# Display popup
		code_edit.clear()		
		code_edit.placeholder_text = "Start typing here..."		
		current_file = "Untitled"
		update_window_title()
	else:
		print("OK")
		code_edit.clear()					
		code_edit.placeholder_text = "Start typing here..."		
		current_file = "Untitled"
		update_window_title()
		code_edit.editable = true	
	
	save.disabled = true
	saveas.disabled = true
	close.disabled = true
	undo.disabled = true
	redo.disabled = true
	copy.disabled = true
	cut.disabled = true
	paste.disabled = true
	compile.disabled = true
	run.disabled = true

### FILE OPEN FUNCTION ###
# Function called when the Open File button is pressed
func _on_open_pressed() -> void:
	# Open the file dialog
	open_file_dialog.popup_centered()

# Gets file from directory and opens it	
func _on_open_file_dialog_file_selected(path):
	file = FileAccess.open(path, FileAccess.READ)
	if file.file_exists(path):
		content = file.get_as_text()
		code_edit.text = content
		code_edit.editable = true
	else:
		show_error("Failed to load the selected file.")
	current_file = path.get_file()
	update_window_title()
	file.close()

### FILE SAVE FUNCTION ###
# Function called when the Save File button is pressed
func _on_save_pressed() -> void:
	var path = current_file
	if path == 'Untitled':
		print("Save As")
		save_as_file_dialog.popup_centered()
	else: 
		print("Save As")
		var file = FileAccess.open(path, FileAccess.WRITE)
		file.store_string(code_edit.text)
		file.close()
	save.disabled = true	
	
func _on_saveas_pressed():
	save_as_file_dialog.popup_centered()
	
func _on_save_as_file_dialog_file_selected(path):
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(code_edit.text)
	current_file = path.get_file()
	update_window_title()
	save.disabled = true		

### CLOSE

### UNDO
func _on_undo_pressed():
	code_edit.undo()
	
### REDO
func _on_redo_pressed():
	code_edit.redo()


func show_error(message: String) -> void:
	# Display the error to the user, perhaps with a Popup or Label
	print("Error: " + message)

func _on_code_edit_text_changed():
	if (len(code_edit.text) > 0) && (content!=code_edit.text):
		save.disabled = false
		saveas.disabled = false
		close.disabled = false
		undo.disabled = false 
		redo.disabled = true # Disabled unless Undo is performed
		copy.disabled = false
		cut.disabled = false
		paste.disabled = true # Disabled unless Copy/Cut is performed
		compile.disabled = false
		run.disabled = false # Replace with function body.
