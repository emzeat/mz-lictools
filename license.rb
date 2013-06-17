#
# license.rb
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


require 'erb'

class License

  attr_accessor :name
  attr_accessor :files
  attr_accessor :short_license_header
  attr_accessor :header

  def initialize(name, options)
    self.name = name
    self.files = Dir.glob("#{File.dirname(__FILE__)}/#{name}/*")
    self.short_license_header = IO.read("#{File.dirname(__FILE__)}/#{name}.erb")
    self.header = IO.read("#{File.dirname(__FILE__)}/header.erb")
    
    @options = options
  end

  def to_s
      txt = ERB.new( short_license_header, 0, "%<>").result(@options.instance_eval { binding });
      return "@LICENSE_HEADER_START@\n#{txt}@LICENSE_HEADER_END@"
  end

  def make_header
    return ERB.new( header, 0, "%<>").result(@options.instance_eval { binding });   
  end

end
