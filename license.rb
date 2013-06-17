
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
      return ERB.new( short_license_header, 0, "%<>").result(@options.instance_eval { binding });
  end

  def make_header
    return ERB.new( header, 0, "%<>").result(@options.instance_eval { binding });   
  end

end
