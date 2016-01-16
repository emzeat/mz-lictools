#
# license_tools.rb
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


require File.dirname(__FILE__) + '/language'
require File.dirname(__FILE__) + '/license'
require File.dirname(__FILE__) + '/filecheck'
require 'optparse'
require 'ostruct'

class LicenseTools

 def self.log( s )
  puts "-- #{ s }" unless @@options.quiet
 end

 def self.debug( s )
  puts "   #{ s }" unless @@options.quiet
 end

 def self.run( binary )

   @@options = OpenStruct.new
   @@options.license = License.new("Apache", @@options)
   @@options.report = true
   @@options.authors = []
   @@options.company = ""
   @@options.recursive = false
   @@options.simualte = false
   @@options.quiet = false
   @@options.missing = false
   @@options.update = false
   @@options.extract = false
   @@options.directory = Dir.pwd

   optparse = OptionParser.new do |opts|
     opts.banner = "Usage: #{binary} <options> <directory>"

     opts.on('-l', '--license LIC', 'Specify the license' ) do |lic|
       @@options.license = License.new(lic, @@options)
       @@options.report = false
     end

     opts.on('-a', '--authors AUTHORS', 'Set the authors (e.g. "Max Musterman:2013" or "Max:2009-2012,Moritz:2012")' ) do |a|
       @@options.authors = Array.new
       a.split(",").each do |author|
        parts = author.split(":")
        a2 = OpenStruct.new
        a2.name = parts[0]
        a2.year = parts[1]
        @@options.authors << a2
       end
       @@options.report = false
     end

     opts.on('-e', '--extract-authors', 'Search for lines ala "Copyright (c) 2012 XYZ" and use them as authors') do
       @@options.extract = true
     end

     opts.on('-c', '--company COMPANY', 'Set the company (e.g. "Orange Fruits")' ) do |a|
       @@options.company = a
       @@options.report = false
     end

     opts.on('-r', '--recursive', 'Search the specified directory recursively') do
       @@options.recursive = true
       @@options.report = false
     end

     opts.on('-s', '--simulate', 'Print the changes but do not append them') do
       @@options.simulate = true
     end

     opts.on('-q', '--quiet', 'Print nothing on screen') do
       @@options.quiet = true
     end

     opts.on('-m', '--missing', 'Add missing headers only') do
       @@options.missing = true
     end

     opts.on('-u', '--update', 'Only update the license, keep copyrights') do
       @@options.update = true
     end

     opts.on_tail('-h', '--help', 'Display this screen' ) do
       puts opts
       exit
     end
   end

   optparse.parse!
   @@options.directory = File.expand_path( ARGV[0] ) unless ARGV[0].nil?
   @@options.company = @@options.author if @@options.company.empty?

   if( @@options.authors.empty? and not @@options.update and not @@options.extract )
    log "WARNING: No authors given, aborting"
    exit
   end

   log "License will be set to '#{@@options.license.name}'"
   log "Updating license only" if @@options.update
   log "Will insert missing copyright notice, keep all other files" if @@options.missing
   scan @@options.directory, @@options.recursive
   log "Finished"
 end

 def self.scan(dir,recurse)
   log "Starting #{recurse ? 'recursive ' : ''}scan of '#{dir}'"

   if recurse
    files = Dir.glob(File.join(dir,"**","*"))
   else
    files = Dir.glob(File.join(dir,"*"))
   end

   files.each do |f|
     if File.file? f
       short_name = f.clone
       short_name[dir + "/"] = ""
       log "File '#{short_name}'"

       handle_file f
     end
   end
 end

 def self.handle_file(f)

    @@options.file = File.basename f

    fc = FileCheck.new( f )
    if @@options.extract
      file_authors = fc.get_authors
      @@options.authors = file_authors unless file_authors.empty?
    end
    header = @@options.license.make_header

    Language::T_SPECS.each do |l|
      if l.file_matches? f
        debug "Type: #{l.name}"
        debug "Authors: #{@@options.authors.map{|a| a.year + ' ' + a.name}}"

        full_header = l.make_comment( header )
        lic_header = l.make_part_of_comment( @@options.license.to_s )
        if( fc.has_license )
          if( not @@options.missing )
            if( @@options.update )
              fc.update_license( lic_header, l ) unless @@options.simulate
              debug "Updating license:\n#{lic_header}" if @@options.simulate
            else
              fc.update_header( full_header, l ) unless @@options.simulate
              debug "Updating header:\n#{full_header}" if @@options.simulate
            end
          end
        else
          fc.add_header( full_header )
          debug "Adding header:\n#{full_header}" if @@options.simulate
        end
        return
      end
    end

    debug "Skipped, unknown type"
 end

end

