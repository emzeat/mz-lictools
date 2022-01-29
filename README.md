license-tools
==============

A small script for adding or updating copyright information
for various file types.

Requirements
--------

Requires an installation of python3

Usage
--------

Make sure the script `lictool` is executable and run it
with `./lictool --help` to obtain a full list of available options.

Alternatively you can install it as python package via
```bash
python3 -m pip install .
lictool --help
```

We also support usage as a hook in `pre-commit`:
```yaml
-   repo: https://github.com/emzeat/mz-lictools
    hooks:
    -   id: license-tools
```


Configuration
--------

The used license, managed files and used authors get configured through a json
file placed in the root of your project and named '.license-tools-config.json'.

A default configuration file can be generated in the current working directory
by invoking `lictool --sample-config`.

A sample configuration is given below with each option explained. Note that the
actual configuration parser is accepting valid json only (which has no concept
of a comment).

```json
{
  "author": {
    // determine the copyright author based on [user] in your local .gitconfig
    "from_git": true
    // explicitly specify the author. Useful when the code is owned by a company
    // and copyrights should not reflect updates made by individual authors
    "name": "My Awesome Company"
    // when both 'from_git' and 'name' have been specified, the 'name' setting
    // will take precedence
  },
  // specifies the license to be put at the top of each file. Use lictool --help
  // to get a list of supported licenses
  "license": "GPL-2.0-or-later",
  // globbing expressions to specify files for which to maintain a license header
  // all expressions will be applied relative to the directory holding the config
  "include": [
    "**/*.py"
  ],
  // regular expressions to specify files not to be touched
  // all expressions will be applied relative to the directory holding the config
  "exclude": [
    // example to exclude all dot directories and files
    "^\\.[^/]+",
    "/\\.[^/]+"
  ]
}
```
