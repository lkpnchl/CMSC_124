extends Control

@onready var loadscreen = preload("res://load.tscn")
@onready var root = get_tree().get_root()
@onready var buttons = root.get_node("Main/TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX")
@onready var save_button = buttons.get_node("Save")
@onready var saveas_button = buttons.get_node("Saveas")
@onready var close_button = buttons.get_node("Close")
@onready var undo_button = buttons.get_node("Undo")
@onready var redo_button = buttons.get_node("Redo")
@onready var copy_button = buttons.get_node("Copy")
@onready var cut_button = buttons.get_node("Cut")
@onready var paste_button = buttons.get_node("Paste")
@onready var compile = buttons.get_node("Compile")
@onready var run = buttons.get_node("Run")

var open_file_dialog : FileDialog  # Reference to the FileDialog instance
var save_as_file_dialog : FileDialog  # Reference to the FileDialog instance

var content : String
var code_edit : CodeEdit  # Reference to the CodeEdit instance
var file : FileAccess # For FileAccess

var app_name = "BOB Compiler"
var current_file = "Untitled"
var CC_press = 0


func _ready():
	update_window_title()
	# Load references to FileDialog and CodeEdit
	open_file_dialog = $OpenFileDialog
	save_as_file_dialog = $SaveFileDialog
	code_edit = get_node("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/PanelContainer/CodeEdit")
	connect_signals()
	
func connect_signals():
	# Connect the New button pressed signal to a function
	var new_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/New")
	new_button.pressed.connect(_on_new_pressed)
	
	# Connect the Open File button pressed signal to a function
	var open_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Open")
	open_button.pressed.connect(_on_open_pressed)
	open_file_dialog.file_selected.connect(_on_open_file_dialog_file_selected)
	
	# Connect the Save File button pressed signal to a function
	var save_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Saveas")
	save_button.pressed.connect(_on_save_pressed)
	save_as_file_dialog.file_selected.connect(_on_save_as_file_dialog_file_selected)
	
	# Connect the Save As File button pressed signal to a function
	var save_as_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Saveas")
	save_as_button.pressed.connect(_on_save_pressed)
	save_as_file_dialog.file_selected.connect(_on_save_as_file_dialog_file_selected)
	
func update_window_title():
	DisplayServer.window_set_title(app_name + ' - ' + current_file)
	
### NEW
# Function called when the New File button is pressed
func _on_new_pressed() -> void:
	if len(code_edit.text)>0 && current_file=="Untitled":
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
	
	save_button.disabled = true
	saveas_button.disabled = true
	close_button.disabled = true
	undo_button.disabled = true
	redo_button.disabled = true
	copy_button.disabled = true
	cut_button.disabled = true
	paste_button.disabled = true
	compile.disabled = true
	run.disabled = true
	CC_press = 0

### OPEN
# Function called when the Open File button is pressed
func _on_open_pressed() -> void:
	# Open the file dialog
	open_file_dialog.popup_centered()

# Gets file from directory and opens it	
func _on_open_file_dialog_file_selected(path: String) -> void: 
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

### SAVE
# Function called when the Save File button is pressed
func _on_save_pressed() -> void:
	var path = current_file
	if path == 'Untitled':
		print("Save As")
		save_as_file_dialog.popup_centered()
	else: 
		print("Save")
		var file = FileAccess.open(path, FileAccess.WRITE)
		content = code_edit.text
		file.store_string(content)
		file.close()
	save_button.disabled = true	
	
### SAVE AS	
func _on_saveas_pressed():
	save_as_file_dialog.popup_centered()
	
func _on_save_as_file_dialog_file_selected(path: String) -> void:
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(code_edit.text)
	current_file = path.get_file()
	update_window_title()
	save_button.disabled = true		

### CLOSE
func _on_close_pressed():
	pass # Replace with function body.

### UNDO
func _on_undo_pressed():
	code_edit.undo()
	if code_edit.has_undo() && code_edit.has_redo():
		undo_button.disabled = false
		redo_button.disabled = false
	elif !code_edit.has_undo():
		undo_button.disabled = true
		redo_button.disabled = false
	elif !code_edit.has_redo():
		undo_button.disabled = false
		redo_button.disabled = true 
		
### REDO
func _on_redo_pressed():
	code_edit.redo()
	if code_edit.has_undo() && code_edit.has_redo():
		undo_button.disabled = false
		redo_button.disabled = false
	elif !code_edit.has_undo():
		undo_button.disabled = true
		redo_button.disabled = false
	elif !code_edit.has_redo():
		undo_button.disabled = false
		redo_button.disabled = true 		

### CUT/COPY/PASTE
func _on_copy_pressed():	
	code_edit.copy()
	CC_press = 1
	paste_button.disabled = false
	
func _on_cut_pressed():	
	code_edit.cut()
	CC_press = 1
	paste_button.disabled = false
	
func _on_paste_pressed():
	code_edit.paste()

func show_error(message: String) -> void:
	# Display the error to the user, perhaps with a Popup or Label
	print("Error: " + message)

func _on_code_edit_text_changed():
	if len(code_edit.text) > 0:
		save_button.disabled = false
		saveas_button.disabled = false
		close_button.disabled = false		
		
		copy_button.disabled = false
		cut_button.disabled = false
		
		## COPY/CUT/PASTE FUNCTIONS
		if copy_button.is_pressed()||cut_button.is_pressed():
			CC_press = 1
		if CC_press == 1:
			paste_button.disabled = false
		
		compile.disabled = false
		run.disabled = false
		
		## UNDO/REDO 
		if code_edit.has_undo() && code_edit.has_redo():
			undo_button.disabled = false
			redo_button.disabled = false
		elif !code_edit.has_undo():
			undo_button.disabled = true
			redo_button.disabled = false
		elif !code_edit.has_redo():
			undo_button.disabled = false
			redo_button.disabled = true 
