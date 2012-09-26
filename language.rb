
class Language

  attr_accessor :name
  attr_accessor :comment_begin
  attr_accessor :comment
  attr_accessor :comment_end
  attr_accessor :stems

  def initialize(name, c_begin, c, c_end, stems)
    self.name = name
    self.comment_begin = c_begin
    self.comment = c
    self.comment_end = c_end
    self.stems = stems
  end

  def file_matches?( path )
    self.stems.each do |s|
        return true if path.end_with? s
    end

    return false
  end

  T_SPECS = [
    Language.new('C/C++','/*','*','*/',['.h','.cc','.c','.cxx','.cpp']),
    Language.new('Ruby','#','#','#',['.rb']),
    Language.new('Bash','#','#','#',['.sh']),
    Language.new('XML','<!--','','-->',['.xml','.ui']),
    Language.new('CMake','#','#','#',['CMakeLists.txt','.cmake'])
  ]

end
