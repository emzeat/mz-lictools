#
# language.rb
# 
# Copyright (c) 2012-2013 Marius Zwicker
# All rights reserved.
# 
# @LICENSE_HEADER_START@
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# @LICENSE_HEADER_END@
#


class Language

  attr_accessor :name
  attr_accessor :comment_begin
  attr_accessor :comment
  attr_accessor :comment_end
  attr_accessor :stems

  def initialize(name, c_begin, c, c_end, stems)
    self.name = name
    self.comment_begin = c_begin
    self.comment = c
    self.comment_end = c_end
    self.stems = stems
  end

  def file_matches?( path )
    self.stems.each do |s|
        return true if path.end_with? s
    end

    return false
  end

  def make_comment( str )
    output = comment_begin + "\n"
    str.lines.each {|l| output = output + comment + " " + l}
    return output = output + comment_end
  end
  
  def make_part_of_comment( str )
    output = ""
    str.lines.each {|l| output = output + comment + " " + l}
    return output
  end

  T_SPECS = [
    Language.new('C/C++','/*','*','*/',['.h','.cc','.c','.cxx','.cpp']),
    Language.new('Ruby','#','#','#',['.rb']),
    Language.new('Bash','#','#','#',['.sh']),
    Language.new('XML','<!--','','-->',['.xml','.ui']),
    Language.new('CMake','#','#','#',['CMakeLists.txt','.cmake'])
  ]

end
