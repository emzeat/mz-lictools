#
# tes2t.cmake
# 
# Copyright (c) 2010-2021 Marius Zwicker
# All rights reserved.
# 
# @LICENSE_HEADER_START@
# meee
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
  
  def update_header( str, lang )
    contents2 = @contents.sub( /#{Regexp.escape(lang.comment_begin)}.*@LICENSE_HEADER_START@.*@LICENSE_HEADER_END@\n#{Regexp.escape(lang.comment_end)}/m, str )
    
    if( contents2 != @contents ) # only write when changed
      File.open(@file, 'w') {|f| f.write contents2 }
    end
  end
   
end

