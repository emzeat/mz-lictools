
require File.dirname(__FILE__) + '/language'
require File.dirname(__FILE__) + '/license'
require 'optparse'
require 'irb'
require 'ostruct'

class LicenseTools

 def self.log( s )
  puts "-- #{ s }"
 end
 
 def self.debug( s )
  puts "   #{ s }"
 end
 
 def self.run( binary )

   @@options = OpenStruct.new
   @@options.license = License.new("Apache")
   @@options.report = true
   @@options.author = ""
   @@options.year = ""
   @@options.recursive = false
   @@options.simualte = false
   @@options.directory = Dir.pwd

   optparse = OptionParser.new do |opts|
     opts.banner = "Usage: #{binary} <options> <directory>"

     opts.on('-l', '--license LIC', 'Specify the license' ) do |lic|  
       @@options.license = License.new(lic)
       @@options.report = false
     end

     opts.on('-a', '--author AUTHOR', 'Set the author (e.g. "Max Musterman")' ) do |a|        
       @@options.author = a
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

     opts.on_tail('-h', '--help', 'Display this screen' ) do
       puts opts
       exit
     end
   end

   optparse.parse!
   @@options.directory = ARGV[0] unless ARGV[0].nil?

   log "License will b set to '#{@@options.license.name}'"
   scan @@options.directory, @@options.recursive
   log "Finished"
 end

 def self.scan(dir,recurse)
   log "Starting #{recurse ? 'recursive ' : ''}scan of '#{dir}'"

   if recurse
    files = Dir.glob("#{dir}/**/*")
   else
    files = Dir.glob("#{dir}/*")
   end

   files.each do |f|
     if File.file? f
       short_name = f
       short_name[dir + "/"] = ""
       log "File '#{short_name}'"

        handle_file f
     end
   end
 end

 def self.handle_file(f)
    Language::T_SPECS.each do |l|
      if l.file_matches? f
        debug "Type: #{l.name}"
        return
      end
    end

    debug "Skipped, unknown type"
 end
   
end

