
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
   # default values
   @@options = OpenStruct.new
   @@options.license = License.new("Apache")
   @@options.report = true
   @@options.author = ""
   @@options.year = ""
   @@options.recursive = false
   @@options.directory = Dir.pwd

   # parse options first
   optparse = OptionParser.new do |opts|
     opts.banner = "Usage: #{binary} <options> <directory>"

     # define the options
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
     opts.on('-R', '--recursive', 'Search the specified directory recursively') do
       @@options.recursive = true
       @@options.report = false
     end
     opts.on_tail('-h', '--help', 'Display this screen' ) do
       puts opts
       exit
     end
   end
   optparse.parse!

   @@options.directory = ARGV[0] unless ARGV[0].nil?

   scan @@options.directory, @@options.recursive
   log "Finished"
 end

 def self.scan(dir,recurse)
    log "Starting #{recurse ? 'recursive ' : ''}scan of '#{dir}'"

   if recurse
    files = Dir.glob('**/*')
   else
    files = Dir.glob('*')
   end

   files.each do |f|
     if File.file? f
       log "File '#{f}'"
     end
   end
 end
   
end

