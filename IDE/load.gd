extends Control


# Called when the node enters the scene tree for the first time.
func _ready():
	$AnimationPlayer.play("Fade in")
	await get_tree().create_timer(5).timeout
	$AnimationPlayer.play("Fade out")
	await get_tree().create_timer(3).timeout
#	get_tree().change_scene("res://MainIDE.tscn")
