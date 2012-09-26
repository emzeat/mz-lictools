
class License

  attr_accessor :name
  attr_accessor :files
  attr_accessor :short_header

  def initialize(name)
    self.name = name
    self.files = Dir.glob("#{File.dirname(__FILE__)}/#{name}/*")
    self.short_header = IO.read("#{File.dirname(__FILE__)}/#{name}.erb")
  end

end
