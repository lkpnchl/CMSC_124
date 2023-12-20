import BisCom

# Infinite loop for the interactive BisCom shell
while True:
	text = input('BisCom > ') # Get user input for BisCom commands
	if text.strip() == "": continue # Check if the input is empty and continue to the next iteration if so
    
	result, error = BisCom.run('<stdin>', text)

	if error: print(error.as_string())
	elif result: # Check if there is only one element in the result
		if len(result.elements) == 1: pass
		else: print(repr(result))
