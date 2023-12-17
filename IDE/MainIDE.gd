extends Control

var open_file_dialog : FileDialog  # Reference to the FileDialog instanc
var save_file_dialog : FileDialog  # Reference to the FileDialog instance
var content : String
var code_edit : CodeEdit  # Reference to the CodeEdit instance

func _ready():
	# Load references to FileDialog and CodeEdit
	open_file_dialog = $OpenFileDialog
	save_file_dialog = $SaveFileDialog
	code_edit = get_node("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/PanelContainer/CodeEdit")

	# Connect signals
	connect_signals()

func connect_signals():
	# Connect Close button to empty text
	var new_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/New")
	new_button.pressed.connect(_on_new_pressed)
	
	# Connect the Open File button pressed signal to a function
	var open_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Open")
	open_button.pressed.connect(_on_open_pressed)
	# Connect the File Dialog to open file
	open_file_dialog.file_selected.connect(_on_file_selected)
	
	# Connect the Save File button pressed signal to a function
	var save_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Save")
	save_button.pressed.connect(_on_save_pressed)
	save_file_dialog.file_selected.connect(_on_file_selected)
	
	# Connect Close button to empty text
	var close_button : TextureButton = get_node_or_null("TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX/Close")
	close_button.pressed.connect(_on_close_pressed)

# Function called when the New File button is pressed
func _on_new_pressed() -> void:
	if len(code_edit.text) > 0:
		# check if file is saved
		# else prompt pop up
			print("hehe")
	else:
		code_edit.editable = true
		code_edit.placeholder_text = "Start typing here..."
	
# Function called when the Open File button is pressed
func _on_open_pressed() -> void:
	# Open the file dialog
	open_file_dialog.popup_centered()

# Function called when the Save File button is pressed
func _on_save_pressed() -> void:
	# Open the file dialog
	save_file_dialog.popup_centered()

# Function called when a file is selected in the FileDialog
func _on_file_selected(path: String) -> void:
	if _on_open_pressed: # Read the file and set the content in the CodeEdit
		var file = FileAccess.open(path, FileAccess.READ)
		if FileAccess.file_exists(path):
			content = file.get_as_text()
			code_edit.text = content
			code_edit.editable = true
			
		else:
			show_error("Failed to load the selected file.")
	#elif _on_save_pressed:
		# if new file
		#var file = FileAccess.open(path, FileAccess.WRITE)
		#print(file)
		#print(content)
		#content = code_edit.get_as_text()
		#print(content)
		#print(path)
		#file.store_string(content)
		# if not new file

func _on_close_pressed() -> void:
	_on_new_pressed()

func show_error(message: String) -> void:
	# Display the error to the user, perhaps with a Popup or Label
	print("Error: " + message)
	
func _on_save_file_dialog_file_selected(path):
	var f = FileAccess.open(path,2)
	f.store_string(code_edit.text)
	var root = get_tree().get_root()
	var buttons = root.get_node("Main/TextureRect/PanelContainer2/MarginContainer/VBoxContainer/hbOX")
	var save = buttons.get_node("Save")
	
	save.disabled = true
	
	
	
