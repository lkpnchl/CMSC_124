extends Control

var open_file_dialog : FileDialog  # Reference to the FileDialog instance
var save_as_file_dialog : FileDialog  # Reference to the FileDialog instance
var content : String
var code_edit : CodeEdit  # Reference to the CodeEdit instance
var file : FileAccess # For FileAccess
#var path = 

func _ready():
	# Load references to FileDialog and CodeEdit
	open_file_dialog = $OpenFileDialog
	save_as_file_dialog = $SaveAsFileDialog
	code_edit = get_node("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/PanelContainer/CodeEdit")

### FILE NEW FUNCTION ###
# Function called when the New File button is pressed
func _on_new_pressed() -> void:
	if len(code_edit.text) > 0:
		# check if file is saved
		# else prompt pop up
			print("hehe")
	else:
		code_edit.editable = true
		code_edit.placeholder_text = "Start typing here..."

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
	file.close()

### FILE SAVE FUNCTION ###
# Function called when the Save File button is pressed
func _on_save_pressed() -> void:
	print("will be back")
	#var file = FileAccess.open("path", FileAccess.WRITE)
	#var test
	#if test=="9":
		#print("wompwomp")
	#else: 
		#print("mompmomp")
	##if file.is_open:
	#file.store_string(code_edit.text)
	##else:
		##save_as_file_dialog.popup_centered()
	#var root = get_tree().get_root()
	#var buttons = root.get_node("Main/TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX")
	#var save = buttons.get_node("Save")
	#save.disabled = true	
		
func _on_save_as_file_dialog_file_selected(path):
	var file = FileAccess.open(path, FileAccess.WRITE)
	file.store_string(code_edit.text)

func show_error(message: String) -> void:
	# Display the error to the user, perhaps with a Popup or Label
	print("Error: " + message)


