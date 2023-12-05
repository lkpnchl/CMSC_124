extends Control

var file_dialog : FileDialog  # Reference to the FileDialog instance
var code_edit : CodeEdit  # Reference to the CodeEdit instance

func _ready():
	# Load references to FileDialog and CodeEdit
	file_dialog = $OpenFileDialog
	code_edit = get_node("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/PanelContainer/CodeEdit")

	# Connect signals
	connect_signals()

func connect_signals():
	# Connect the Open File button pressed signal to a function
	var open_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Open")
	open_button.pressed.connect(_on_open_pressed)
	file_dialog.file_selected.connect(_on_file_selected)
	# Connect the FileDialog's file_selected signal to a function

# Function called when the Open File button is pressed
func _on_open_pressed() -> void:
	# Open the file dialog
	file_dialog.popup_centered()

# Function called when a file is selected in the FileDialog
func _on_file_selected(path: String) -> void:
	# Read the file and set the content in the CodeEdit
#	var file : File = File.new()
#	if file.file_exists(path) and file.open(path, File.READ) == OK:
#		var content : String = file.get_as_text()
#		file.close()
#		code_edit.text = content
#	else:
#		show_error("Failed to load the selected file.")
	pass

func show_error(message: String) -> void:
	# Display the error to the user, perhaps with a Popup or Label
	print("Error: " + message)
