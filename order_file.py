"""
  MIT License

  Copyright (c) 2023 Erreiip

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
"""
import os
import sys
import re


# class Fields
class Fields:
  def __init__(self,  string, index, size=0):
    self.string = string
    self.index = index
    self.size = size

  def add_string(self, string):
    self.string += string

  def get_last_line(self):
    lines = self.string.split('\n')
    return lines[-2]
  
  def has_equal_paranthesis(self):
    return len(re.findall('\(', self.string)) == len(re.findall('\)', self.string))
  
  def remove_unused_lines(self):
    lines = self.string.split('\n')
    while not lines[-1].lstrip() or lines[-1].lstrip() == '\n':
      lines.pop(-1)
    self.string = '\n'.join(lines) + '\n'

  def set_size(self, size):
    self.size = size

  def __lt__(self, other):
    return self.string < other.string

class Methods(Fields):
  def __init__(self, string, index, space):
    super().__init__(string, index)
    self.space = space

  def __lt__(self, other):
    self_lines = self.string.split('\n')
    other_lines = other.string.split('\n')
    if '@api.' in self_lines[0] and '@api.' in other_lines[0]:
      if self_lines[0].split('@api.')[1].split('(')[0] == other_lines[0].split('api.')[1].split('(')[0]:
        return self_lines[1] < other_lines[1]
    return self.string < other.string


# Methods
def check_index(tab, index, field_type):
  if len(tab) < index + 1 or (any(tab[index]) and tab[index][-1].__class__ != field_type):
    tab.append([])
    if (any(tab[index]) and tab[index][-1].__class__ != field_type):
      return 1
  return 0

def number_of_space(line):
  nb_space = 0
  for char in line:
    if char == ' ':
      nb_space += 1
    else:
      return nb_space

def tidy_up_recursively(path):
  full_path = os.path.abspath(path)
  file_in_dir = [ os.path.join(full_path, os.path.split(f.path)[1]) for f in os.scandir(path)]
  for file in file_in_dir:
    if os.path.isdir(file):
      tidy_up_recursively(file)
      continue
    if os.path.splitext(file)[1] == '.py':
      tidy_up_file(file)

def write_on_file(file, tab_to_write):
  total_size = 0
  for field in tab_to_write:
    file.write(field.string)
    total_size += field.size
  return total_size

# Const
METHODS = Methods
FIELDS = Fields

# Main method
def tidy_up_file(file_name):
    try:
      file = open(file_name, "r")
    except IOError:
       raise Exception("Aucun fichier dont le nom est %s trouvable" % file_name)

    # Prepare for the write
    lines = file.readlines()
    file.seek(0)

    # Check all the fields ans set them in the fields array
    field_regex = "..*=?fields\.(.*2.*|boolean|char|selection|integer|date|text|html|datetime|monetary|binary|float)\("
    field_methods = "^( )*((def .*\(.*\):)|\@.*)"
    fields = []
    group_index = 0
    index = 0
    is_in_field = False
    is_in_method = False
    last_line_was_field = False
    last_line_was_method = False
    file_size = len(lines)
    file_last_line = False
    for line in file.readlines():

      if file_size == index + 1:
        file_last_line = True

      is_field = re.search(field_regex, line.lower())
      is_method = re.search(field_methods, line.lower())

      if (not is_in_field and not is_in_method) and not (is_field or is_method) and (last_line_was_field or last_line_was_method):
        if any(line.lstrip()):
          group_index += 1
          last_line_was_field = False
          last_line_was_method = False
        elif last_line_was_field:
          fields[group_index][-1].set_size(fields[group_index][-1].size + 1)

      if is_in_field:
        fields[group_index][-1].add_string(line)
        if fields[group_index][-1].has_equal_paranthesis() or file_last_line:
          fields[group_index][-1].set_size(index - fields[group_index][-1].index + 1 + ( 1 if file_last_line else 0))
          is_in_field = False
          last_line_was_field = True

      if is_in_method:
        has_same_space = number_of_space(line) == fields[group_index][-1].space
        is_not_entry = re.search(field_methods, line.lower()) == None and re.search(field_regex, line.lower()) == None
        last_line_was_space = not fields[group_index][-1].get_last_line().lstrip()
        if (has_same_space and (is_not_entry or (not is_not_entry and last_line_was_space))) or file_last_line:
            fields[group_index][-1].set_size(index - fields[group_index][-1].index)
            is_in_method = False
            last_line_was_method = True
            if file_last_line:
              fields[group_index][-1].add_string(line)
              fields[group_index][-1].set_size(fields[group_index][-1].size + 1)
        else:
          fields[group_index][-1].add_string(line)

      if not is_in_method and not is_in_field:
        if is_field:
          group_index += check_index(fields, group_index, FIELDS)
          fields[group_index].append(Fields(line, index, 1))
          is_in_field = not fields[group_index][-1].has_equal_paranthesis()
          last_line_was_field = fields[group_index][-1].has_equal_paranthesis()
          last_line_was_method = False
        elif is_method:
          group_index += check_index(fields, group_index, METHODS)
          fields[group_index].append(Methods(line, index, number_of_space(line)))
          is_in_method = True
          last_line_was_method = False
          last_line_was_field = False

      index += 1

    # Sorting groups
    index = 1
    for group_fields in fields:
      if index == len(fields):
        group_fields[-1].remove_unused_lines()
      group_fields.sort()
      if group_fields[0].__class__ != METHODS:
        group_fields[-1].add_string('\n')
      index += 1

    # Rewrite on the file
    file.close()
    file_tmp = open(file_name, "w")
    group_to_write = 0
    index = 0
    while index < len(lines):
      line = lines[index]
      is_a_field = False

      if group_to_write < len(fields):
        for field in fields[group_to_write]:
          if field.index == index:
            is_a_field = True

      if is_a_field:
        index += write_on_file(file_tmp, fields[group_to_write])
        group_to_write += 1
      else:
        file_tmp.write(line)
        index += 1

    file_tmp.close()



if len(sys.argv) > 1:
  index_args = 1
  while index_args < len(sys.argv):
    is_dir = os.path.isdir(sys.argv[index_args])
    if is_dir:
      tidy_up_recursively(sys.argv[index_args])
    else:
      tidy_up_file(sys.argv[index_args])
    index_args += 1
else:
   raise Exception("Usage: order_file <file_name1 | dir_name1> <file_name2 | dir_name2> ...")

""" MLS PIR """
