
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
   @@options.author = ""
   @@options.company = ""
   @@options.year = ""
   @@options.recursive = false
   @@options.simualte = false
   @@options.quiet = false
   @@options.directory = Dir.pwd

   optparse = OptionParser.new do |opts|
     opts.banner = "Usage: #{binary} <options> <directory>"

     opts.on('-l', '--license LIC', 'Specify the license' ) do |lic|  
       @@options.license = License.new(lic, @@options)
       @@options.report = false
     end

     opts.on('-a', '--author AUTHOR', 'Set the author (e.g. "Max Musterman")' ) do |a|        
       @@options.author = a
       @@options.report = false
     end
     
     opts.on('-c', '--company COMPANY', 'Set the author (e.g. "Orange Fruits")' ) do |a|        
       @@options.company = a
       @@options.report = false
     end

     opts.on('-y', '--year YEAR', 'Set the copyright year (e.g. "2011,2012")' ) do |year|
       @@options.year = year
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

     opts.on_tail('-h', '--help', 'Display this screen' ) do
       puts opts
       exit
     end
   end

   optparse.parse!
   @@options.directory = ARGV[0] unless ARGV[0].nil?
   @@options.company = @@options.author if @@options.company.empty?

   log "License will be set to '#{@@options.license.name}'"
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
    header = @@options.license.make_header
    
    Language::T_SPECS.each do |l|
      if l.file_matches? f
        debug "Type: #{l.name}"
        
        cheader = l.make_comment( header )
        if( fc.has_license )
          fc.update_header( cheader, l ) unless @@options.simulate      
          debug "Prepending header:\n#{cheader}" if @@options.simulate
        else
          fc.add_header( cheader )
          debug "Updating header:\n#{cheader}" if @@options.simulate
        end
        return
      end
    end

    debug "Skipped, unknown type"
 end
   
end

