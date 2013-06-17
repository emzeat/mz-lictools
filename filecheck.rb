#
# filecheck.rb
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

class FileCheck

  def initialize( file )
    @file = file
    @contents = IO.read( file )
  end
  
  def has_license
    if( @contents.match /@LICENSE_HEADER_START@/ or @contents.match /Copyright (c)/ )
      return true
    end
    
    return false
  end
  
  def add_header( str )
    File.open(@file, 'w') {|f| f.write str + "\n\n" + @contents }
  end
  
  def update_license( str, lang )
    contents2 = @contents.sub( /#{Regexp.escape(lang.comment)} @LICENSE_HEADER_START@.*@LICENSE_HEADER_END@/m, str )
    
    if( contents2 != @contents ) # only write when changed
      File.open(@file, 'w') {|f| f.write contents2 }
    end
  end
  
  def update_header( str, lang )
    contents2 = @contents.sub( /#{Regexp.escape(lang.comment_begin)}.*@LICENSE_HEADER_START@.*@LICENSE_HEADER_END@\n#{Regexp.escape(lang.comment_end)}/m, str )
    
    if( contents2 != @contents ) # only write when changed
      File.open(@file, 'w') {|f| f.write contents2 }
    end
  end
   
end

