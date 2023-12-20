#------------------------------#
# IMPORTS
#------------------------------#

from strings_with_arrows import *

import string
import os
import math

#------------------------------#
# CONSTANTS
#------------------------------#

NUMERO = '0123456789'
LETRA = string.ascii_letters
LETRA_NUMERO = LETRA + NUMERO

#------------------------------#
# ERRORS
#------------------------------#

# Definition of a generic Error class
class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details

  # Format error details with file information and arrows indicating position
  def as_string(self):
    result  = f'{self.error_name}: {self.details}\n'
    result += f'File {self.pos_start.fn}, line {self.pos_start.ln + 1}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

# Definition of Illegal error classes
class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Illegal Character', details)

# Definition of Expected Char error classes
class ExpectedCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, 'Expected Character', details)

# Definition of Invalid syntax error classes
class InvalidSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details=''):
    super().__init__(pos_start, pos_end, 'Invalid Syntax', details)

# Definition of Runtime error classes
class RTError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, 'Runtime Error', details)
    self.context = context

  # Generate a traceback with file information and arrows indicating position
  def as_string(self):
    result  = self.generate_traceback()
    result += f'{self.error_name}: {self.details}'
    result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start, self.pos_end)
    return result

  # Generate a traceback string with file information
  def generate_traceback(self):
    result = ''
    pos = self.pos_start
    ctx = self.context

    while ctx:
      result = f'  File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
      pos = ctx.parent_entry_pos
      ctx = ctx.parent

    return 'Traceback (most recent call last):\n' + result

#------------------------------#
# POSITION
#------------------------------#

# Definition of a Position class representing a point in the source code
class Position:
  def __init__(self, idx, ln, col, fn, ftxt):
    self.idx = idx
    self.ln = ln
    self.col = col
    self.fn = fn
    self.ftxt = ftxt

  # Move the position to the next character, handling newline characters
  def advance(self, current_char=None):
    self.idx += 1
    self.col += 1

    if current_char == '\n':
      self.ln += 1
      self.col = 0

    return self
  
  # Create a copy of the current position
  def copy(self):
    return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

#------------------------------#
# TOKENS
#------------------------------#

TT_KWARTA			= 'KWARTA'
TT_SINSILYO   = 'SINSILYO'
TT_TIBUOK			= 'TIBUOK'
TT_AYDI	      = 'AYDI'
TT_KEYWORD		= 'KEYWORD'
TT_DUGANG     = 'DUGANG'
TT_KWAI    	  = 'KWAI'
TT_DAGHANON   = 'DAGHANON'
TT_BAHIN      = 'BAHIN'
TT_KAPILAON		= 'KAPILAON'
TT_EQ					= 'EQ'
TT_LPAREN   	= 'LPAREN'
TT_RPAREN   	= 'RPAREN'
TT_LSQUARE    = 'LSQUARE'
TT_RSQUARE    = 'RSQUARE'
TT_EE					= 'EE'
TT_NE					= 'NE'
TT_LT					= 'LT'
TT_GT					= 'GT'
TT_LTE				= 'LTE'
TT_GTE				= 'GTE'
TT_COMMA			= 'COMMA'
TT_ARROW			= 'ARROW'
TT_SUNOD		  = 'SUNOD'
TT_TUMOY			= 'TUMOY'

KEYWORDS = [
  'PASA',
  'UG',
  'KUN',
  'DILI',
  'KUNG',
  'KONDILI',
  'KINI',
  'PARA',
  'PADONG',
  'SAKA',
  'SAMTANG',
  'ROTA',
  'DAYON',
  'LUGAR',
  'BALIK',
  'UNAHAN',
  'HUNONG',
]

class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value

    # Set position start and end if provided
    if pos_start:
      self.pos_start = pos_start.copy()
      self.pos_end = pos_start.copy()
      self.pos_end.advance()

    if pos_end:
      self.pos_end = pos_end.copy()

  # Helper method to check if a token matches a given type and value
  def matches(self, type_, value):
    return self.type == type_ and self.value == value

  # Representation of the token
  def __repr__(self):
    if self.value: return f'{self.type}:{self.value}'
    return f'{self.type}'

#------------------------------#
# LEXER
#------------------------------#

class Lexer:
  # Initialize the Lexer with a filename and text input
  def __init__(self, fn, text):
    self.fn = fn
    self.text = text
    self.pos = Position(-1, 0, -1, fn, text)
    self.current_char = None
    self.advance()

  # Move to the next character in the text
  def advance(self):
    self.pos.advance(self.current_char)
    self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

  # Generate a list of tokens from the input text
  def make_tokens(self):
    tokens = []

    while self.current_char != None:
      if self.current_char in ' \t':
        self.advance()
      elif self.current_char == '#': # Skip comments starting with '#'
        self.skip_comment()
      elif self.current_char in ';\n': # Handle newline or semicolon as a token
        tokens.append(Token(TT_SUNOD, pos_start=self.pos))
        self.advance()
      elif self.current_char in NUMERO:
        tokens.append(self.make_number())
      elif self.current_char in LETRA:
        tokens.append(self.make_identifier())
      elif self.current_char == '"':
        tokens.append(self.make_string())
      elif self.current_char == '+':
        tokens.append(Token(TT_DUGANG, pos_start=self.pos))
        self.advance()
      elif self.current_char == '-':
        tokens.append(self.make_minus_or_arrow())
      elif self.current_char == '*':
        tokens.append(Token(TT_DAGHANON, pos_start=self.pos))
        self.advance()
      elif self.current_char == '/':
        tokens.append(Token(TT_BAHIN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '^':
        tokens.append(Token(TT_KAPILAON, pos_start=self.pos))
        self.advance()
      elif self.current_char == '(':
        tokens.append(Token(TT_LPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == ')':
        tokens.append(Token(TT_RPAREN, pos_start=self.pos))
        self.advance()
      elif self.current_char == '[':
        tokens.append(Token(TT_LSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == ']':
        tokens.append(Token(TT_RSQUARE, pos_start=self.pos))
        self.advance()
      elif self.current_char == '!':
        token, error = self.make_not_equals()
        if error: return [], error
        tokens.append(token)
      elif self.current_char == '=':
        tokens.append(self.make_equals())
      elif self.current_char == '<':
        tokens.append(self.make_less_than())
      elif self.current_char == '>':
        tokens.append(self.make_greater_than())
      elif self.current_char == ',':
        tokens.append(Token(TT_COMMA, pos_start=self.pos))
        self.advance()
      else:
        pos_start = self.pos.copy()
        char = self.current_char
        self.advance()
        return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

    tokens.append(Token(TT_TUMOY, pos_start=self.pos))
    return tokens, None

  # Parse numeric literals (integer or float)
  def make_number(self):
    num_str = ''
    dot_count = 0
    pos_start = self.pos.copy()

    # Loop through characters while they are numeric or '.' to handle decimal point
    while self.current_char != None and self.current_char in NUMERO + '.':
      if self. current_char == '.':
        if dot_count == 1: break
        dot_count += 1
      num_str += self.current_char
      self.advance()

    # Determine token type based on dot_count
    if dot_count == 0:
      return Token(TT_KWARTA, int(num_str), pos_start, self.pos)
    else:
      return Token(TT_SINSILYO, float(num_str), pos_start, self.pos)
  
  # Parse string literals
  def make_string(self):
    string = ''
    pos_start = self.pos.copy()
    escape_character = False
    self.advance()

    escape_characters = {
      'n': '\n',
      't': '\t',
      '"': '"'
    }

    # Loop through characters while not reaching the end of the string to handle escape characters
    while self.current_char != None and (self.current_char != '"' or escape_character):
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
          self.advance()
          continue # Skip the next character after encountering '\'
        else:
          string += self.current_char
      self.advance()
      escape_character = False

    # Move past the closing double quote
    self.advance()
    return Token(TT_TIBUOK, string, pos_start, self.pos)

  # Parse identifiers (keywords or user-defined)
  def make_identifier(self):
    id_str = ''
    pos_start = self.pos.copy()

    while self.current_char != None and self.current_char in LETRA_NUMERO + '_':
      id_str += self.current_char
      self.advance()

    tok_type = TT_KEYWORD if id_str in KEYWORDS else TT_AYDI
    return Token(tok_type, id_str, pos_start, self.pos)

  # Parse '-' or '->
  def make_minus_or_arrow(self):
    tok_type = TT_KWAI
    pos_start = self.pos.copy()
    self.advance()

    # If followed by '>', update token type
    if self.current_char == '>':
      self.advance()
      tok_type = TT_ARROW

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  # Parse '!='
  def make_not_equals(self):
    pos_start = self.pos.copy()
    self.advance()

    # If followed by '=', return not equals token
    if self.current_char == '=':
      self.advance()
      return Token(TT_NE, pos_start=pos_start, pos_end=self.pos), None

    self.advance()
    return None, ExpectedCharError(pos_start, self.pos, "'=' (after '!')")

  # Parse '=' or '=='
  def make_equals(self):
    tok_type = TT_EQ
    pos_start = self.pos.copy()
    self.advance()

    # If followed by '=', update token type
    if self.current_char == '=':
      self.advance()
      tok_type = TT_EE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  # Parse '<' or '<='
  def make_less_than(self):
    tok_type = TT_LT
    pos_start = self.pos.copy()
    self.advance()

    # If followed by '=', update token type
    if self.current_char == '=':
      self.advance()
      tok_type = TT_LTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  # Parse '>' or '>='
  def make_greater_than(self):
    tok_type = TT_GT
    pos_start = self.pos.copy()
    self.advance()

    # If followed by '=', update token type
    if self.current_char == '=':
      self.advance()
      tok_type = TT_GTE

    return Token(tok_type, pos_start=pos_start, pos_end=self.pos)

  # Skip the initial character (assuming it is the '#' that indicates a comment)
  def skip_comment(self):
    self.advance()

    # Loop through characters until a newline character is encountered
    while self.current_char != '\n':
      self.advance()

    self.advance()

#------------------------------#
# NODES
#------------------------------#

# Represents a node for holding a numeric value
class NumberNode:
  def __init__(self, tok):
    self.tok = tok

    # Store the position information for error reporting
    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

# Represents a node for holding a string value
class StringNode:
  def __init__(self, tok):
    self.tok = tok

    # Store the position information for error reporting
    self.pos_start = self.tok.pos_start
    self.pos_end = self.tok.pos_end

  def __repr__(self):
    return f'{self.tok}'

# Represents a node for holding a list of element nodes
class ListNode:
  def __init__(self, element_nodes, pos_start, pos_end):
    self.element_nodes = element_nodes

    # Store the position information for error reporting
    self.pos_start = pos_start
    self.pos_end = pos_end

# Represents a node for accessing a variable
class VarAccessNode:
  def __init__(self, var_name_tok):
    self.var_name_tok = var_name_tok

    # Store the position information for error reporting
    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.var_name_tok.pos_end

# Represents a node for assigning a value to a variable
class VarAssignNode:
  def __init__(self, var_name_tok, value_node):
    self.var_name_tok = var_name_tok
    self.value_node = value_node

    # Store the position information for error reporting
    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.value_node.pos_end

# Represents a node for binary operations
class BinOpNode:
  def __init__(self, left_node, op_tok, right_node):
    self.left_node = left_node
    self.op_tok = op_tok
    self.right_node = right_node

    # Store the position information for error reporting
    self.pos_start = self.left_node.pos_start
    self.pos_end = self.right_node.pos_end

  def __repr__(self):
    return f'({self.left_node}, {self.op_tok}, {self.right_node})'

# Represents a node for unary operations
class UnaryOpNode:
  def __init__(self, op_tok, node):
    self.op_tok = op_tok
    self.node = node

    # Store the position information for error reporting
    self.pos_start = self.op_tok.pos_start
    self.pos_end = node.pos_end

  def __repr__(self):
    return f'({self.op_tok}, {self.node})'

# Represents a node for an if statement
class IfNode:
  def __init__(self, cases, else_case):
    self.cases = cases
    self.else_case = else_case

    # Determine the position information based on the first and last cases
    self.pos_start = self.cases[0][0].pos_start
    self.pos_end = (self.else_case or self.cases[len(self.cases) - 1])[0].pos_end

# Represents a node for a for loop
class ForNode:
  def __init__(self, var_name_tok, start_value_node, end_value_node, step_value_node, body_node, should_return_null):
    self.var_name_tok = var_name_tok
    self.start_value_node = start_value_node
    self.end_value_node = end_value_node
    self.step_value_node = step_value_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    # Store the position information for error reporting
    self.pos_start = self.var_name_tok.pos_start
    self.pos_end = self.body_node.pos_end

# Represents a node for a while loop
class WhileNode:
  def __init__(self, condition_node, body_node, should_return_null):
    self.condition_node = condition_node
    self.body_node = body_node
    self.should_return_null = should_return_null

    # Store the position information for error reporting
    self.pos_start = self.condition_node.pos_start
    self.pos_end = self.body_node.pos_end

# Represents a node for function definition
class FuncDefNode:
  def __init__(self, var_name_tok, arg_name_toks, body_node, should_auto_return):
    self.var_name_tok = var_name_tok
    self.arg_name_toks = arg_name_toks
    self.body_node = body_node
    self.should_auto_return = should_auto_return

    # Determine the position information based on the components
    if self.var_name_tok:
      self.pos_start = self.var_name_tok.pos_start
    elif len(self.arg_name_toks) > 0:
      self.pos_start = self.arg_name_toks[0].pos_start
    else:
      self.pos_start = self.body_node.pos_start

    self.pos_end = self.body_node.pos_end

# Represents a node for a function call
class CallNode:
  def __init__(self, node_to_call, arg_nodes):
    self.node_to_call = node_to_call
    self.arg_nodes = arg_nodes

    # Determine the position information based on the components
    self.pos_start = self.node_to_call.pos_start

    if len(self.arg_nodes) > 0:
      self.pos_end = self.arg_nodes[len(self.arg_nodes) - 1].pos_end
    else:
      self.pos_end = self.node_to_call.pos_end

# Represents a node for a return statement
class ReturnNode:
  def __init__(self, node_to_return, pos_start, pos_end):
    self.node_to_return = node_to_return

    # Store the position information for error reporting
    self.pos_start = pos_start
    self.pos_end = pos_end

# Represents a node for a continue statement
class ContinueNode:
  def __init__(self, pos_start, pos_end):
    # Store the position information for error reporting
    self.pos_start = pos_start
    self.pos_end = pos_end

# Represents a node for a break statement
class BreakNode:
  def __init__(self, pos_start, pos_end):
    # Store the position information for error reporting
    self.pos_start = pos_start
    self.pos_end = pos_end

#------------------------------#
# PARSE RESULT
#------------------------------#

class ParseResult:
  
  # Initialize ParseResult attributes
  def __init__(self):
    self.error = None
    self.node = None
    self.last_registered_advance_count = 0
    self.advance_count = 0
    self.to_reverse_count = 0
  
  # Register an advancement, updating counts
  def register_advancement(self):
    self.last_registered_advance_count = 1
    self.advance_count += 1

  # Register the result of a parsing attempt
  def register(self, res):
    self.last_registered_advance_count = res.advance_count
    self.advance_count += res.advance_count
    if res.error: self.error = res.error
    return res.node

  # Try registering a result, handling errors
  def try_register(self, res):
    if res.error:
      self.to_reverse_count = res.advance_count
      return None
    return self.register(res)

  # Register the result of a parsing attempt
  def success(self, node):
    self.node = node
    return self

  # Handle a parsing failure, updating error if needed
  def failure(self, error):
    if not self.error or self.last_registered_advance_count == 0:
      self.error = error
    return self

#------------------------------#
# PARSER
#------------------------------#

class Parser:
  # Initialize the Parser with a list of tokens
  def __init__(self, tokens):
    self.tokens = tokens
    self.tok_idx = -1
    self.advance()

  # Move to the next token and update the current token
  def advance(self):
    self.tok_idx += 1
    self.update_current_tok()
    return self.current_tok

  # Move back by a specified amount of tokens and update the current token
  def reverse(self, amount=1):
    self.tok_idx -= amount
    self.update_current_tok()
    return self.current_tok

  # Update the current token based on the current index
  def update_current_tok(self):
    if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
      self.current_tok = self.tokens[self.tok_idx]

  # Parse the entire program and return the result
  def parse(self):
    res = self.statements()
    if not res.error and self.current_tok.type != TT_TUMOY:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Token cannot appear after previous tokens"
      ))
    return res

  ###################################

  # Parse a series of statements
  def statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_tok.pos_start.copy()

    # Skip any leading newlines
    while self.current_tok.type == TT_SUNOD:
      res.register_advancement()
      self.advance()

    # Parse the first statement
    statement = res.register(self.statement())
    if res.error: return res
    statements.append(statement)

    more_statements = True

    # Parse additional statements separated by newlines
    while True:
      newline_count = 0
      while self.current_tok.type == TT_SUNOD:
        res.register_advancement()
        self.advance()
        newline_count += 1
      if newline_count == 0:
        more_statements = False

      if not more_statements: break
      
      # Try to parse another statement, stop if unsuccessful
      statement = res.try_register(self.statement())
      if not statement:
        self.reverse(res.to_reverse_count)
        more_statements = False
        continue
      statements.append(statement)

    # Return a ListNode containing all parsed statements
    return res.success(ListNode(
      statements,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  # Parse a single statement
  def statement(self):
    res = ParseResult()
    pos_start = self.current_tok.pos_start.copy()

  # Check for different statement types
    # Return statement
    if self.current_tok.matches(TT_KEYWORD, 'BALIK'):
      res.register_advancement()
      self.advance()

      expr = res.try_register(self.expr())
      if not expr:
        self.reverse(res.to_reverse_count)
      return res.success(ReturnNode(expr, pos_start, self.current_tok.pos_start.copy()))

    # Continue statement
    if self.current_tok.matches(TT_KEYWORD, 'UNAHAN'):
      res.register_advancement()
      self.advance()
      return res.success(ContinueNode(pos_start, self.current_tok.pos_start.copy()))

    # Break statement
    if self.current_tok.matches(TT_KEYWORD, 'HUNONG'):
      res.register_advancement()
      self.advance()
      return res.success(BreakNode(pos_start, self.current_tok.pos_start.copy()))

    # Default to expression parsing if no specific statement type is matched
    expr = res.register(self.expr())
    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'BALIK', 'UNAHAN', 'HUNONG', 'PASA', 'KUNG', 'PARA', 'SAMTANG', 'ROTA', int, float, identifier, '+', '-', '(', '[' or 'DILI'"
      ))
    return res.success(expr)

  # Parse an expression
  def expr(self):
    res = ParseResult()

    # Variable assignment
    if self.current_tok.matches(TT_KEYWORD, 'PASA'):
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_AYDI:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected identifier"
        ))

      var_name = self.current_tok
      res.register_advancement()
      self.advance()

      if self.current_tok.type != TT_EQ:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected '='"
        ))

      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      return res.success(VarAssignNode(var_name, expr))

    # Parse binary operations
    node = res.register(self.bin_op(self.comp_expr, ((TT_KEYWORD, 'UG'), (TT_KEYWORD, 'OR'))))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected 'PASA', 'KUNG', 'PARA', 'SAMTANG', 'ROTA', int, float, identifier, '+', '-', '(', '[' or 'DILI'"
      ))

    return res.success(node)

  # Parse a comparison expression
  def comp_expr(self):
    res = ParseResult()

    # Unary 'not' operation
    if self.current_tok.matches(TT_KEYWORD, 'DILI'):
      op_tok = self.current_tok
      res.register_advancement()
      self.advance()

      node = res.register(self.comp_expr())
      if res.error: return res
      return res.success(UnaryOpNode(op_tok, node))

    # Parse binary operations with comparison operators
    node = res.register(self.bin_op(self.arith_expr, (TT_EE, TT_NE, TT_LT, TT_GT, TT_LTE, TT_GTE)))

    if res.error:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        "Expected int, float, identifier, '+', '-', '(', '[', 'KUNG', 'PARA', 'SAMTANG', 'ROTA' or 'DILI'"
      ))

    return res.success(node)

  # Parse arithmetic expressions using the bin_op function with addition and subtraction operators
  def arith_expr(self):
    return self.bin_op(self.term, (TT_DUGANG, TT_KWAI))

  # Parse term expressions using the bin_op function with multiplication and division operators
  def term(self):
    return self.bin_op(self.factor, (TT_DAGHANON, TT_BAHIN))

  # Parse factor expressions
  def factor(self):
    res = ParseResult()
    tok = self.current_tok

    # Handle unary operations (positive and negative)
    if tok.type in (TT_DUGANG, TT_KWAI):
      res.register_advancement()
      self.advance()
      factor = res.register(self.factor())
      if res.error: return res
      return res.success(UnaryOpNode(tok, factor))

    return self.power()

  # Parse power expressions
  def power(self):
    return self.bin_op(self.call, (TT_KAPILAON, ), self.factor)

  # Parse function calls
  def call(self):
    res = ParseResult()
    atom = res.register(self.atom())
    if res.error: return res

    # Handle function calls with arguments
    if self.current_tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      arg_nodes = []

      # No arguments in the function call
      if self.current_tok.type == TT_RPAREN:
        res.register_advancement()
        self.advance()
      else: # Parse and collect function arguments
        arg_nodes.append(res.register(self.expr()))
        if res.error:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected ')', 'PASA', 'KUNG', 'PARA', 'SAMTANG', 'ROTA', int, float, identifier, '+', '-', '(', '[' or 'DILI'"
          ))

        # Handle multiple arguments in the function call
        while self.current_tok.type == TT_COMMA:
          res.register_advancement()
          self.advance()

          arg_nodes.append(res.register(self.expr()))
          if res.error: return res

        # Expecting the closing parenthesis of the function call
        if self.current_tok.type != TT_RPAREN:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected ',' or ')'"
          ))

        res.register_advancement()
        self.advance()
      return res.success(CallNode(atom, arg_nodes))
    return res.success(atom)

  # Parse atomic expressions
  def atom(self):
    res = ParseResult()
    tok = self.current_tok

    # Parse numeric constants (int or float)
    if tok.type in (TT_KWARTA, TT_SINSILYO):
      res.register_advancement()
      self.advance()
      return res.success(NumberNode(tok))

    # Parse string constants
    elif tok.type == TT_TIBUOK:
      res.register_advancement()
      self.advance()
      return res.success(StringNode(tok))

    # Parse variable access
    elif tok.type == TT_AYDI:
      res.register_advancement()
      self.advance()
      return res.success(VarAccessNode(tok))

    # Parse expressions enclosed in parentheses
    elif tok.type == TT_LPAREN:
      res.register_advancement()
      self.advance()
      expr = res.register(self.expr())
      if res.error: return res
      if self.current_tok.type == TT_RPAREN: # Ensure closing parenthesis is present
        res.register_advancement()
        self.advance()
        return res.success(expr)
      else: # Missing closing parenthesis
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ')'"
        ))

    # Parse list expressions
    elif tok.type == TT_LSQUARE:
      list_expr = res.register(self.list_expr())
      if res.error: return res
      return res.success(list_expr)

    # Parse if expressions
    elif tok.matches(TT_KEYWORD, 'KUNG'):
      if_expr = res.register(self.if_expr())
      if res.error: return res
      return res.success(if_expr)

    # Parse for expressions
    elif tok.matches(TT_KEYWORD, 'PARA'):
      for_expr = res.register(self.for_expr())
      if res.error: return res
      return res.success(for_expr)

    # Parse while expressions
    elif tok.matches(TT_KEYWORD, 'SAMTANG'):
      while_expr = res.register(self.while_expr())
      if res.error: return res
      return res.success(while_expr)

    # Parse function definitions
    elif tok.matches(TT_KEYWORD, 'ROTA'):
      func_def = res.register(self.func_def())
      if res.error: return res
      return res.success(func_def)

    # If none of the above patterns match, raise an error
    return res.failure(InvalidSyntaxError(
      tok.pos_start, tok.pos_end,
      "Expected int, float, identifier, '+', '-', '(', '[', KUNG', 'PARA', 'SAMTANG', 'ROTA'"
    ))

  # Parse list expressions
  def list_expr(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_tok.pos_start.copy()

    # Ensure the list starts with '['
    if self.current_tok.type != TT_LSQUARE:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '['"
      ))

    res.register_advancement()
    self.advance()

    # Empty list
    if self.current_tok.type == TT_RSQUARE:
      res.register_advancement()
      self.advance()
    else: # Parse and collect list elements
      element_nodes.append(res.register(self.expr()))
      if res.error:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          "Expected ']', 'PASA', 'KUNG', 'PARA', 'SAMTANG', 'ROTA', int, float, identifier, '+', '-', '(', '[' or 'DILI'"
        ))

      # Handle multiple elements in the list
      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        element_nodes.append(res.register(self.expr()))
        if res.error: return res

      # Ensure the list ends with ']'
      if self.current_tok.type != TT_RSQUARE:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ']'"
        ))

      res.register_advancement()
      self.advance()

    # Return the parsed list expression
    return res.success(ListNode(
      element_nodes,
      pos_start,
      self.current_tok.pos_end.copy()
    ))

  # Parse if expression
  def if_expr(self):
    res = ParseResult()
    all_cases = res.register(self.if_expr_cases('KUNG'))
    if res.error: return res
    cases, else_case = all_cases
    return res.success(IfNode(cases, else_case))

  # Parse if-else expression
  def if_expr_b(self):
    return self.if_expr_cases('KONDILI')

  # Parse else expression
  def if_expr_c(self):
    res = ParseResult()
    else_case = None

    # Parse else keyword
    if self.current_tok.matches(TT_KEYWORD, 'KINI'):
      res.register_advancement()
      self.advance()

      # Parse additional statements separated by newlines
      if self.current_tok.type == TT_SUNOD:
        res.register_advancement()
        self.advance()

        # Parse statements block
        statements = res.register(self.statements())
        if res.error: return res
        else_case = (statements, True)

        # Parse until end keyword
        if self.current_tok.matches(TT_KEYWORD, 'LUGAR'):
          res.register_advancement()
          self.advance()
        else:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            "Expected 'LUGAR'"
          ))
      else: # Parse single statement
        expr = res.register(self.statement())
        if res.error: return res
        else_case = (expr, False)

    return res.success(else_case)

  # Parse if expression is followed by an if-else or else
  def if_expr_b_or_c(self):
    res = ParseResult()
    cases, else_case = [], None

    # Parse if-else keyword
    if self.current_tok.matches(TT_KEYWORD, 'KONDILI'):
      all_cases = res.register(self.if_expr_b())
      if res.error: return res
      cases, else_case = all_cases
    else: # Parse else keyword
      else_case = res.register(self.if_expr_c())
      if res.error: return res

    return res.success((cases, else_case))

  # Parse if expression cases
  def if_expr_cases(self, case_keyword):
    res = ParseResult()
    cases = []
    else_case = None

    # Check for the expected keyword (if-else or else)
    if not self.current_tok.matches(TT_KEYWORD, case_keyword):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '{case_keyword}'"
      ))

    res.register_advancement()
    self.advance()

    # Parse condition expression
    condition = res.register(self.expr())
    if res.error: return res

    # Check for then keyword after the condition
    if not self.current_tok.matches(TT_KEYWORD, 'DAYON'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'DAYON'"
      ))

    res.register_advancement()
    self.advance()

    # Parse additional statements separated by newlines
    if self.current_tok.type == TT_SUNOD:
      res.register_advancement()
      self.advance()

      statements = res.register(self.statements())
      if res.error: return res
      cases.append((condition, statements, True))

      # Check end keyword after the statements block
      if self.current_tok.matches(TT_KEYWORD, 'LUGAR'):
        res.register_advancement()
        self.advance()
      else: # Check end keyword is not present, parse the alternative cases
        all_cases = res.register(self.if_expr_b_or_c())
        if res.error: return res
        new_cases, else_case = all_cases
        cases.extend(new_cases)
    else: # Check if there's no new line, parse single statement
      expr = res.register(self.statement())
      if res.error: return res
      cases.append((condition, expr, False))

      # Parse alternative cases
      all_cases = res.register(self.if_expr_b_or_c())
      if res.error: return res
      new_cases, else_case = all_cases
      cases.extend(new_cases)

    return res.success((cases, else_case))

  # Parse for expression
  def for_expr(self):
    res = ParseResult()

    # Parse for keyword
    if not self.current_tok.matches(TT_KEYWORD, 'PARA'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'PARA'"
      ))

    res.register_advancement()
    self.advance()

    # Check identifiers after for keyword
    if self.current_tok.type != TT_AYDI:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected identifier"
      ))

    var_name = self.current_tok
    res.register_advancement()
    self.advance()

    # Check the equal token after the identifier
    if self.current_tok.type != TT_EQ:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '='"
      ))

    res.register_advancement()
    self.advance()

    # Parse start value of the range
    start_value = res.register(self.expr())
    if res.error: return res

    # Check to keyword
    if not self.current_tok.matches(TT_KEYWORD, 'PADONG'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'PADONG'"
      ))

    res.register_advancement()
    self.advance()

    # Parse end value of the range
    end_value = res.register(self.expr())
    if res.error: return res

    # Check for optional step keyword and parse step value
    if self.current_tok.matches(TT_KEYWORD, 'SAKA'):
      res.register_advancement()
      self.advance()

      step_value = res.register(self.expr())
      if res.error: return res
    else:
      step_value = None

    # Check for then keyword
    if not self.current_tok.matches(TT_KEYWORD, 'DAYON'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'DAYON'"
      ))

    res.register_advancement()
    self.advance()

    # Parse additional statements separated by newlines
    if self.current_tok.type == TT_SUNOD:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      # Check end keyword after statements block
      if not self.current_tok.matches(TT_KEYWORD, 'LUGAR'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'LUGAR'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(ForNode(var_name, start_value, end_value, step_value, body, True))

    # If there's no new line, parse single statement
    body = res.register(self.statement())
    if res.error: return res

    return res.success(ForNode(var_name, start_value, end_value, step_value, body, False))

  # Parse while expression
  def while_expr(self):
    res = ParseResult()

    # Check for while keyword
    if not self.current_tok.matches(TT_KEYWORD, 'SAMTANG'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'SAMTANG'"
      ))

    res.register_advancement()
    self.advance()

    # Parse condition expression
    condition = res.register(self.expr())
    if res.error: return res

    # Check for then keyword
    if not self.current_tok.matches(TT_KEYWORD, 'DAYON'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'DAYON'"
      ))

    res.register_advancement()
    self.advance()

    # Parse additional statements separated by newlines
    if self.current_tok.type == TT_SUNOD:
      res.register_advancement()
      self.advance()

      body = res.register(self.statements())
      if res.error: return res

      # Check end keyword after statements block
      if not self.current_tok.matches(TT_KEYWORD, 'LUGAR'):
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected 'LUGAR'"
        ))

      res.register_advancement()
      self.advance()

      return res.success(WhileNode(condition, body, True))

    # If there's no new line, parse single statement
    body = res.register(self.statement())
    if res.error: return res

    return res.success(WhileNode(condition, body, False))

  # Parse function definition
  def func_def(self):
    res = ParseResult()

    # Check for function keyword 
    if not self.current_tok.matches(TT_KEYWORD, 'ROTA'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'ROTA'"
      ))

    res.register_advancement()
    self.advance()

    # Parse function name if present
    if self.current_tok.type == TT_AYDI:
      var_name_tok = self.current_tok
      res.register_advancement()
      self.advance()
      
      # Check for '(' after function name
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected '('"
        ))
    else: # Check for '(' after function keyword
      var_name_tok = None
      if self.current_tok.type != TT_LPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or '('"
        ))

    res.register_advancement()
    self.advance()
    arg_name_toks = []

    # Parse function arguments if present
    if self.current_tok.type == TT_AYDI:
      arg_name_toks.append(self.current_tok)
      res.register_advancement()
      self.advance()

      while self.current_tok.type == TT_COMMA:
        res.register_advancement()
        self.advance()

        # Check for identifier after ',' in arguments
        if self.current_tok.type != TT_AYDI:
          return res.failure(InvalidSyntaxError(
            self.current_tok.pos_start, self.current_tok.pos_end,
            f"Expected identifier"
          ))

        arg_name_toks.append(self.current_tok)
        res.register_advancement()
        self.advance()

      # Check for ')' after function arguments
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected ',' or ')'"
        ))
    else: # Check for ')' after '('
      if self.current_tok.type != TT_RPAREN:
        return res.failure(InvalidSyntaxError(
          self.current_tok.pos_start, self.current_tok.pos_end,
          f"Expected identifier or ')'"
        ))

    res.register_advancement()
    self.advance()

    # Check for '->' and parse expression for function body
    if self.current_tok.type == TT_ARROW:
      res.register_advancement()
      self.advance()

      body = res.register(self.expr())
      if res.error: return res

      return res.success(FuncDefNode(
        var_name_tok,
        arg_name_toks,
        body,
        True
      ))

    # Check for newline and parse statements for function body
    if self.current_tok.type != TT_SUNOD:
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected '->' or SUNOD"
      ))

    res.register_advancement()
    self.advance()

    body = res.register(self.statements())
    if res.error: return res

    # Check for end keyword after statements
    if not self.current_tok.matches(TT_KEYWORD, 'LUGAR'):
      return res.failure(InvalidSyntaxError(
        self.current_tok.pos_start, self.current_tok.pos_end,
        f"Expected 'LUGAR'"
      ))

    res.register_advancement()
    self.advance()

    return res.success(FuncDefNode(
      var_name_tok,
      arg_name_toks,
      body,
      False
    ))

  ###################################

  # If func_b is not provided, set it to func_a
  def bin_op(self, func_a, ops, func_b=None):
    if func_b == None:
      func_b = func_a

    # Parse left operand using func_a
    res = ParseResult()
    left = res.register(func_a())
    if res.error: return res

    # Continue parsing while the current token is an operator
    while self.current_tok.type in ops or (self.current_tok.type, self.current_tok.value) in ops:
      op_tok = self.current_tok # Get the operator token
      res.register_advancement()
      self.advance()
      right = res.register(func_b()) # Parse right operand using func_b
      if res.error: return res
      left = BinOpNode(left, op_tok, right) # Create a binary operation node with left, operator, and right operands

    return res.success(left)

#------------------------------#
# RUNTIME RESULT
#------------------------------#

class RTResult:
  # Initialize runtime result attributes
  def __init__(self):
    self.reset()

  # Reset all runtime result attributes
  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  # Register the attributes from another runtime result
  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  # Set the result to success and store the value
  def success(self, value):
    self.reset()
    self.value = value
    return self

  # Set the result to success with a return value for functions
  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self

  # Set the result to success with a continue flag for loops
  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  # Set the result to success with a break flag for loops
  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  # Set the result to failure and store the error
  def failure(self, error):
    self.reset()
    self.error = error
    return self

  # Allows to continue and break outside the current function
  def should_return(self):
    return (
      self.error or
      self.func_return_value or
      self.loop_should_continue or
      self.loop_should_break
    )

#------------------------------#
# VALUES
#------------------------------#

class Value:
  # Initialize position and context for error reporting
  def __init__(self):
    self.set_pos()
    self.set_context()

  # Set position attributes for error reporting
  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  # Set context for error reporting
  def set_context(self, context=None):
    self.context = context
    return self

  # Default method for addition operation
  def added_to(self, other):
    return None, self.illegal_operation(other)

  # Default method for subtraction operation
  def subbed_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for multiplication operation
  def multed_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for division operation
  def dived_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for power operation
  def powed_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for equal comparison
  def get_comparison_eq(self, other):
    return None, self.illegal_operation(other)

  # Default method for not equal comparison
  def get_comparison_ne(self, other):
    return None, self.illegal_operation(other)

  # Default method for less than comparison
  def get_comparison_lt(self, other):
    return None, self.illegal_operation(other)

  # Default method for greater than comparison
  def get_comparison_gt(self, other):
    return None, self.illegal_operation(other)

  # Default method for less than equal comparison
  def get_comparison_lte(self, other):
    return None, self.illegal_operation(other)

  # Default method for greater than equal comparison
  def get_comparison_gte(self, other):
    return None, self.illegal_operation(other)

  # Default method for logical AND operator
  def anded_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for logical OR operator
  def ored_by(self, other):
    return None, self.illegal_operation(other)

  # Default method for logical NOT operation
  def notted(self,other):
    return None, self.illegal_operation(other)

  # Default method for executing a value as a function
  def execute(self, args):
    return RTResult().failure(self.illegal_operation())

  # Raise an exception if the copy method is not defined
  def copy(self):
    raise Exception('No copy method defined')

  # Default method for checking truthiness of a value
  def is_true(self):
    return False

  # Return an error for an illegal operation
  def illegal_operation(self, other=None):
    if not other: other = self
    return RTError(
      self.pos_start, other.pos_end,
      'Illegal operation',
      self.context
    )

class Number(Value):
  # Initialize the Number object with a numeric value
  def __init__(self, value):
    super().__init__()
    self.value = value

  # Add the current Number to another Number
  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Subtract another Number from the current Number
  def subbed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Multiply the current Number by another Number
  def multed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Divide the current Number by another Number
  def dived_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Division by zero',
          self.context
        )

      return Number(self.value / other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Raise the current Number to the power of another Number
  def powed_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for equals
  def get_comparison_eq(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for not equals
  def get_comparison_ne(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for less than
  def get_comparison_lt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for greater than
  def get_comparison_gt(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for less than equals
  def get_comparison_lte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Compare the current number to check for greater than equals
  def get_comparison_gte(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Logical AND operation on the current Number
  def anded_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Logical OR operation on the current Number
  def ored_by(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Logical NOT operation on the current Number
  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  # Create a copy of the current Number
  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  # Check if the Number is logically true
  def is_true(self):
    return self.value != 0

  # Convert the Number to a string for display
  def __str__(self):
    return str(self.value)

  # Representation of the Number object
  def __repr__(self):
    return str(self.value)

# Class attributes for predefined Number values
Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)

class String(Value):
  # Initialize the String object with a string value
  def __init__(self, value):
    super().__init__()
    self.value = value

  # Concatenate the current String with another String
  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Repeat the current String by a numeric factor
  def multed_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Retrieve a character from the current String at a specified index
  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return String(self.value[other.value]).set_context(self.context), None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from string because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  # Check if the current String is equal to another String
  def get_comparison_eq(self, other):
    if isinstance(other, String):
      return Number(int(self.value == other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Check if the current String is not equal to another String
  def get_comparison_ne(self, other):
    if isinstance(other, String):
      return Number(int(self.value != other.value)).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  # Check if the String is logically true (non-empty)
  def is_true(self):
    return len(self.value) > 0

  # Create a copy of the current String
  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  # Convert the String to a string for display
  def __str__(self):
    return self.value

  # Representation of the String object
  def __repr__(self):
    return f'"{self.value}"'

# List class representing list values
class List(Value):
  # Initialize the List object with a list of elements
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  # Add an element to the current List
  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  # Remove an element from the current List at a specified index
  def subbed_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be removed from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  # Concatenate the current List with another List
  def multed_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)

  # Retrieve an element from the current List at a specified index
  def dived_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RTError(
          other.pos_start, other.pos_end,
          'Element at this index could not be retrieved from list because index is out of bounds',
          self.context
        )
    else:
      return None, Value.illegal_operation(self, other)

  # Create a copy of the current List
  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  # Convert the List to a string for display
  def __str__(self):
    return ", ".join([str(x) for x in self.elements])

  # Representation of the List object
  def __repr__(self):
    return f'[{", ".join([repr(x) for x in self.elements])}]'

# BaseFunction class representing the base class for all functions
class BaseFunction(Value):
  # Initialize the BaseFunction object with a name
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  # Generate a new context for function execution
  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  # Check if the number of arguments passed matches the expected number
  def check_args(self, arg_names, args):
    res = RTResult()

    if len(args) > len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(args) - len(arg_names)} too many args passed into {self}",
        self.context
      ))

    if len(args) < len(arg_names):
      return res.failure(RTError(
        self.pos_start, self.pos_end,
        f"{len(arg_names) - len(args)} too few args passed into {self}",
        self.context
      ))

    return res.success(None)

  # Populate the function's arguments in the symbol table
  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_table.set(arg_name, arg_value)

  # Check arguments and populate them in the symbol table
  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = RTResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return(): return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)

# Function class representing user-defined functions
class Function(BaseFunction):
  # Initialize the Function object with a name, body node, argument names, and auto-return flag
  def __init__(self, name, body_node, arg_names, should_auto_return):
    super().__init__(name)
    self.body_node = body_node
    self.arg_names = arg_names
    self.should_auto_return = should_auto_return

  # Execute the function with the given arguments
  def execute(self, args):
    res = RTResult()
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return(): return res

    value = res.register(interpreter.visit(self.body_node, exec_ctx))
    if res.should_return() and res.func_return_value == None: return res

    ret_value = (value if self.should_auto_return else None) or res.func_return_value or Number.null
    return res.success(ret_value)

  # Create a copy of the current Function
  def copy(self):
    copy = Function(self.name, self.body_node, self.arg_names, self.should_auto_return)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  # Representation of the Function object
  def __repr__(self):
    return f"<function {self.name}>"

class BuiltInFunction(BaseFunction):
  # Initialize the BuiltInFunction object with a name
  def __init__(self, name):
    super().__init__(name)

  # Initialize the BuiltInFunction object with a name
  def execute(self, args):
    res = RTResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(method.arg_names, args, exec_ctx))
    if res.should_return(): return res

    return_value = res.register(method(exec_ctx))
    if res.should_return(): return res
    return res.success(return_value)

  # Raise an exception if no execute_<name> method is defined      
  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  # Create a copy of the current BuiltInFunction
  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  # Representation of the BuiltInFunction object
  def __repr__(self):
    return f"<built-in function {self.name}>"

  # Built-in functions

  # Print the value of the 'value' variable in the symbol table
  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return RTResult().success(Number.null)
  execute_print.arg_names = ['value']

  # Return the value of the 'value' variable as a String
  def execute_print_ret(self, exec_ctx):
    return RTResult().success(String(str(exec_ctx.symbol_table.get('value'))))
  execute_print_ret.arg_names = ['value']

  # Get user input as a string
  def execute_input(self, exec_ctx):
    text = input()
    return RTResult().success(String(text))
  execute_input.arg_names = []

  # Get user input and convert to integer, repeat until valid input
  def execute_input_int(self, exec_ctx):
    while True:
      text = input()
      try:
        number = int(text)
        break
      except ValueError:
        print(f"'{text}' must be an integer. Try again!")
    return RTResult().success(Number(number))
  execute_input_int.arg_names = []

  # Clear the console screen
  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls')
    return RTResult().success(Number.null)
  execute_clear.arg_names = []

  # Check if the 'value' in the symbol table is a Number
  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  # Check if the 'value' in the symbol table is a String
  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  # Check if the 'value' in the symbol table is a List
  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  # Check if the 'value' in the symbol table is a BaseFunction
  def execute_is_function(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return RTResult().success(Number.true if is_number else Number.false)
  execute_is_function.arg_names = ["value"]

  # Append 'value' to 'list' if 'list' is a List
  def execute_append(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    value = exec_ctx.symbol_table.get("value")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    list_.elements.append(value)
    return RTResult().success(Number.null)
  execute_append.arg_names = ["list", "value"]

  # Pop element at 'index' from 'list' if 'list' is a List
  def execute_pop(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")
    index = exec_ctx.symbol_table.get("index")

    if not isinstance(list_, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(index, Number):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be number",
        exec_ctx
      ))

    try:
      element = list_.elements.pop(index.value)
    except:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        'Element at this index could not be removed from list because index is out of bounds',
        exec_ctx
      ))
    return RTResult().success(element)
  execute_pop.arg_names = ["list", "index"]

  # Extend 'listA' with elements from 'listB' if both are Lists
  def execute_extend(self, exec_ctx):
    listA = exec_ctx.symbol_table.get("listA")
    listB = exec_ctx.symbol_table.get("listB")

    if not isinstance(listA, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "First argument must be list",
        exec_ctx
      ))

    if not isinstance(listB, List):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be list",
        exec_ctx
      ))

    listA.elements.extend(listB.elements)
    return RTResult().success(Number.null)
  execute_extend.arg_names = ["listA", "listB"]

  # Get the length of 'list' or 'string'
  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List) and not isinstance(list_, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Argument must be list or string",
        exec_ctx
      ))

    if isinstance(list_, List):
      return RTResult().success(Number(len(list_.elements)))

    return RTResult().success(Number(len(list_.value)))
  execute_len.arg_names = ["list"]

  # Execute a script specified by the 'fn' variable in the symbol table
  def execute_run(self, exec_ctx):
    fn = exec_ctx.symbol_table.get("fn")

    if not isinstance(fn, String):
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        "Second argument must be string",
        exec_ctx
      ))

    fn = fn.value

    try:
      with open(fn, "r") as f:
        script = f.read()
    except Exception as e:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to load script \"{fn}\"\n" + str(e),
        exec_ctx
      ))

    _, error = run(fn, script)

    if error:
      return RTResult().failure(RTError(
        self.pos_start, self.pos_end,
        f"Failed to finish executing script \"{fn}\"\n" +
        error.as_string(),
        exec_ctx
      ))

    return RTResult().success(Number.null)
  execute_run.arg_names = ["fn"]

# Instantiate built-in functions
BuiltInFunction.print       = BuiltInFunction("print")
BuiltInFunction.print_ret   = BuiltInFunction("print_ret")
BuiltInFunction.input       = BuiltInFunction("input")
BuiltInFunction.input_int   = BuiltInFunction("input_int")
BuiltInFunction.clear       = BuiltInFunction("clear")
BuiltInFunction.is_number   = BuiltInFunction("is_number")
BuiltInFunction.is_string   = BuiltInFunction("is_string")
BuiltInFunction.is_list     = BuiltInFunction("is_list")
BuiltInFunction.is_function = BuiltInFunction("is_function")
BuiltInFunction.append      = BuiltInFunction("append")
BuiltInFunction.pop         = BuiltInFunction("pop")
BuiltInFunction.extend      = BuiltInFunction("extend")
BuiltInFunction.len					= BuiltInFunction("len")
BuiltInFunction.run					= BuiltInFunction("run")

#------------------------------#
# CONTEXT
#------------------------------#

# Represents the context in which a statement or expression is executed
class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None

#------------------------------#
# SYMBOL TABLE
#------------------------------#

class SymbolTable:
  # Represents a symbol table for storing variables and their values
  def __init__(self, parent=None):
    self.symbols = {} # Dictionary to store symbol-value pairs
    self.parent = parent # Reference to the parent symbol table

  # Get the value of a symbol by name, checking in the current and parent symbol tables
  def get(self, name):
    value = self.symbols.get(name, None)
    if value == None and self.parent:
      return self.parent.get(name)
    return value
 
  # Set the value of a symbol in the symbol table
  def set(self, name, value):
    self.symbols[name] = value

  # Remove a symbol from the symbol table
  def remove(self, name):
    del self.symbols[name]

#------------------------------#
# INTERPRETER
#------------------------------#

class Interpreter:
  # Visit a specific node based on its type
  def visit(self, node, context):
    method_name = f'visit_{type(node).__name__}'
    method = getattr(self, method_name, self.no_visit_method)
    return method(node, context)

  # Error handling for undefined visit methods
  def no_visit_method(self, node, context):
    raise Exception(f'No visit_{type(node).__name__} method defined')

  ###################################

  # Visit a NumberNode and create a corresponding Number value
  def visit_NumberNode(self, node, context):
    return RTResult().success(
      Number(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  # Visit a StringNode and create a corresponding String value
  def visit_StringNode(self, node, context):
    return RTResult().success(
      String(node.tok.value).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  # Visit a ListNode and create a corresponding List value
  def visit_ListNode(self, node, context):
    res = RTResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return(): return res

    return res.success(
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  # Visit a VarAccessNode and retrieve the value from the symbol table
  def visit_VarAccessNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = context.symbol_table.get(var_name)

    if not value:
      return res.failure(RTError(
        node.pos_start, node.pos_end,
        f"'{var_name}' is not defined",
        context
      ))

    value = value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(value)

  # Visit a VarAssignNode, evaluate the assigned value, and set it in the symbol table
  def visit_VarAssignNode(self, node, context):
    res = RTResult()
    var_name = node.var_name_tok.value
    value = res.register(self.visit(node.value_node, context))
    if res.should_return(): return res

    context.symbol_table.set(var_name, value)
    return res.success(value)

  # Visit a Binary Operation Node, evaluate left and right operands, and perform the corresponding operation
  def visit_BinOpNode(self, node, context):
    res = RTResult()
    left = res.register(self.visit(node.left_node, context))
    if res.should_return(): return res
    right = res.register(self.visit(node.right_node, context))
    if res.should_return(): return res

    # Determine the operation based on the operator token type
    if node.op_tok.type == TT_DUGANG:
      result, error = left.added_to(right)
    elif node.op_tok.type == TT_KWAI:
      result, error = left.subbed_by(right)
    elif node.op_tok.type == TT_DAGHANON:
      result, error = left.multed_by(right)
    elif node.op_tok.type == TT_BAHIN:
      result, error = left.dived_by(right)
    elif node.op_tok.type == TT_KAPILAON:
      result, error = left.powed_by(right)
    elif node.op_tok.type == TT_EE:
      result, error = left.get_comparison_eq(right)
    elif node.op_tok.type == TT_NE:
      result, error = left.get_comparison_ne(right)
    elif node.op_tok.type == TT_LT:
      result, error = left.get_comparison_lt(right)
    elif node.op_tok.type == TT_GT:
      result, error = left.get_comparison_gt(right)
    elif node.op_tok.type == TT_LTE:
      result, error = left.get_comparison_lte(right)
    elif node.op_tok.type == TT_GTE:
      result, error = left.get_comparison_gte(right)
    elif node.op_tok.matches(TT_KEYWORD, 'UG'):
      result, error = left.anded_by(right)
    elif node.op_tok.matches(TT_KEYWORD, 'KUN'):
      result, error = left.ored_by(right)

    # Handle errors and return the result
    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  # Visit a Unary Operation Node, evaluate the operand, and perform the corresponding operation
  def visit_UnaryOpNode(self, node, context):
    res = RTResult()
    number = res.register(self.visit(node.node, context))
    if res.should_return(): return res

    error = None

    # Determine the operation based on the operator token type
    if node.op_tok.type == TT_KWAI:
      number, error = number.multed_by(Number(-1))
    elif node.op_tok.matches(TT_KEYWORD, 'DILI'):
      number, error = number.notted()

    # Handle errors and return the result
    if error:
      return res.failure(error)
    else:
      return res.success(number.set_pos(node.pos_start, node.pos_end))

  # Visit an If Node, evaluate conditions and execute corresponding branches
  def visit_IfNode(self, node, context):
    res = RTResult()

    # Evaluate the condition expression
    for condition, expr, should_return_null in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.should_return(): return res

      # Check if the condition is true, execute the corresponding branch
      if condition_value.is_true():
        expr_value = res.register(self.visit(expr, context))
        if res.should_return(): return res
        return res.success(Number.null if should_return_null else expr_value)

    # Execute the else case if present
    if node.else_case:
      expr, should_return_null = node.else_case
      expr_value = res.register(self.visit(expr, context))
      if res.should_return(): return res
      return res.success(Number.null if should_return_null else expr_value)

    return res.success(Number.null)

  # Visit a For Node, execute a loop with a specified range and step
  def visit_ForNode(self, node, context):
    res = RTResult()
    elements = []

    # Evaluate start, end, and step values
    start_value = res.register(self.visit(node.start_value_node, context))
    if res.should_return(): return res
    end_value = res.register(self.visit(node.end_value_node, context))
    if res.should_return(): return res

    # Evaluate step value or use default step value (1)
    if node.step_value_node:
      step_value = res.register(self.visit(node.step_value_node, context))
      if res.should_return(): return res
    else:
      step_value = Number(1)

    i = start_value.value

    # Define condition based on the step value
    if step_value.value >= 0:
      condition = lambda: i < end_value.value
    else:
      condition = lambda: i > end_value.value

    # Loop through the specified range and execute the body
    while condition():
      context.symbol_table.set(node.var_name_tok.value, Number(i))
      i += step_value.value

      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    # Return the result, considering whether the loop should return null
    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  # Visit a While Node, execute a loop while a condition is true
  def visit_WhileNode(self, node, context):
    res = RTResult()
    elements = []

    # Evaluate the condition
    while True:
      condition = res.register(self.visit(node.condition_node, context))
      if res.should_return(): return res

      # Break the loop if the condition is not true
      if not condition.is_true():
        break

     # Execute the body of the loop
      value = res.register(self.visit(node.body_node, context))
      if res.should_return() and res.loop_should_continue == False and res.loop_should_break == False: return res

      if res.loop_should_continue:
        continue

      if res.loop_should_break:
        break

      elements.append(value)

    # Return the result, considering whether the loop should return null
    return res.success(
      Number.null if node.should_return_null else
      List(elements).set_context(context).set_pos(node.pos_start, node.pos_end)
    )

  # Visit a Function Definition Node, create a function value, and store it in the symbol table
  def visit_FuncDefNode(self, node, context):
    res = RTResult()

    func_name = node.var_name_tok.value if node.var_name_tok else None
    body_node = node.body_node
    arg_names = [arg_name.value for arg_name in node.arg_name_toks]
    func_value = Function(func_name, body_node, arg_names, node.should_auto_return).set_context(context).set_pos(node.pos_start, node.pos_end)

    if node.var_name_tok:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  # Visit a Function Call Node, execute the function with the provided arguments
  def visit_CallNode(self, node, context):
    res = RTResult()
    args = []

    # Evaluate the value to call
    value_to_call = res.register(self.visit(node.node_to_call, context))
    if res.should_return(): return res
    value_to_call = value_to_call.copy().set_pos(node.pos_start, node.pos_end)

    # Evaluate the arguments
    for arg_node in node.arg_nodes:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return(): return res

    # Execute the function with the arguments
    return_value = res.register(value_to_call.execute(args))
    if res.should_return(): return res
    return_value = return_value.copy().set_pos(node.pos_start, node.pos_end).set_context(context)
    return res.success(return_value)

  # Visit a Return Node, evaluate the returned value, and return a success result with the value
  def visit_ReturnNode(self, node, context):
    res = RTResult()

    if node.node_to_return:
      value = res.register(self.visit(node.node_to_return, context))
      if res.should_return(): return res
    else:
      value = Number.null

    return res.success_return(value)

  # Visit a Continue Node and return a success result with a continue flag
  def visit_ContinueNode(self, node, context):
    return RTResult().success_continue()

  # Visit a BreakNode and return a success result with a break flag
  def visit_BreakNode(self, node, context):
    return RTResult().success_break()

#------------------------------#
# RUN
#------------------------------#

# Global Symbol Table with predefined variables and functions
global_symbol_table = SymbolTable()
global_symbol_table.set("WA", Number.null)
global_symbol_table.set("NGI", Number.false)
global_symbol_table.set("OO", Number.true)
global_symbol_table.set("MATH_PI", Number.math_PI)
global_symbol_table.set("SUKLI", BuiltInFunction.print)
global_symbol_table.set("SUKLI_RET", BuiltInFunction.print_ret)
global_symbol_table.set("PLETE", BuiltInFunction.input)
global_symbol_table.set("PLETE_KWARTA", BuiltInFunction.input_int)
global_symbol_table.set("LIMPYO", BuiltInFunction.clear)
global_symbol_table.set("NUMERO_BA", BuiltInFunction.is_number)
global_symbol_table.set("TIBUOK_BA", BuiltInFunction.is_string)
global_symbol_table.set("LINYA_BA", BuiltInFunction.is_list)
global_symbol_table.set("ROTA_BA", BuiltInFunction.is_function)
global_symbol_table.set("PUNO", BuiltInFunction.append)
global_symbol_table.set("BUTO", BuiltInFunction.pop)
global_symbol_table.set("ISWAG", BuiltInFunction.extend)
global_symbol_table.set("SUKOD", BuiltInFunction.len)
global_symbol_table.set("LARGA", BuiltInFunction.run)

def run(fn, text):
  # Lexical analysis: Convert source code text into tokens
  lexer = Lexer(fn, text)
  tokens, error = lexer.make_tokens()
  if error: return None, error

  # Syntax analysis: Parse the tokens into an abstract syntax tree (AST)
  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error: return None, ast.error

  # Semantic analysis and execution: Interpret the AST
  # To run program
  interpreter = Interpreter()
  context = Context('<program>')
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, result.error
