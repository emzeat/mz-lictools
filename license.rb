
class License

  attr_accessor :name
  attr_accessor :files
  attr_accessor :short_header

  def initialize(name)
    self.name = name
    self.files = []
    self.short_header = ""
  end

end
