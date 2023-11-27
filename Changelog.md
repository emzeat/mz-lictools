v2.7.0
------
_WIP_

* Add support for dash style comments to support lua files
* Predefine comment style for rust rst files
* Predefine comment style for toml files

v2.6.2
------
_24.09.2023_

* Fix greedy parsing of pound-style comments after license header

v2.6.1
------
_14.07.2023_

* Fix greedy parsing of slash-style comments after license header

v2.6.0
------
_21.05.2023_

* Add option to override the comment style per extension
* Add option to omit the header title
* Remove unecessary empty lines in comment headers

v2.5.0
------
_19.04.2023_

* Add BSD-3-Clause license support - thanks to Daniel Andrlik
* Relicense from GPL 3.0 to Apache 2.0 in order to simplify use
  in commercial environments
* Configurable whitespace between license and file contents
* Bugfixes

v2.4.4
------
_18.03.2023_

* Bugfixes

v2.4.3
------
_29.01.2023_

* Bugfixes

v2.4.2
------
_26.01.2023_

* Bugfixes

v2.4.1
------
_21.01.2023_

* Optimize performance on larger repositories, one some codebases
  this is showing improvements from 19s down to 2.3s

v2.4.0
------
_17.01.2023_

* Add option to use a custom title
* Add option to omit the license text
* Add option to explicitly set the range of years for an author
* Add option to use a custom license text
* Add option to override all authors

v2.3.1
------
_22.06.2022_

* Fix package version scheme to follow semver and be automatically derived from `git describe`

v2.3
------
_05.02.2022_

* Add support for .rc, .qml, .ui, .qrc, .svg, .bat, .mm, .m, .frag, .vert and .glsl file types
* Support for parsing and updating batch files
* Support for parsing and updating rc files
* Support for retaining decl types at the beginning of xml documents
* Changed the default company name from using the git author to a more generic term referring to all authors of a file

v2.2
------
_29.01.2022_

* Handle authors changing their names by adding support for aliases
* Improve parsing of author names

v2.1
------
_28.01.2022_

* Adding 'Unlicense'
* Adding 'AGPL-3.0-only'
* Extend interaction with git, a file's last author is now fetched using the git history enabling compatibility with `pre-commit run -a`
* Improved config error handling
* Support to catch additional license tags from v1.0
* Support for a dedicated company name when using propietary licenses

v2.0
------
_31.10.2021_

Complete rewrite using python.
* Adding support for pre-commit
* Use SPDX compliant annotations and license names
* Remove need for @BEGIN/@END annotations for the license body

v1.0
------
_16.01.2016_

Initial implementation using ruby.
