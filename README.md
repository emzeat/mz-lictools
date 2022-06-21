# license-tools

Have you ever been annoyed by the task of manually maintaining the licensing
headers for your source files?

The `license-tools` utility is here to safe the day for you :)

It will automate the task of adding a license header to new files and updating license headers of existing files:
* Configure a license for the entire repository. Several FOSS licenses are packaged, closed source licenses are supported as well, see `lictool --help`.
* When configured as [pre-commit hook](https://pre-commit.com/), the last author of a file can be automatically pulled from git so that changes automatically reflect in the copyright year and authors list of a file.
* License headers aim to be [SPDX](https://spdx.dev/) compliant.

## Requirements

Requires an installation of python3 and the jinja2 package.

## Usage

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

## Example
Let's assume the following minimal C++ program `hello.cpp`:
```C++
#include <iostream>

int main(int argc, char* argv[])
{
  std::cout << "Hello World" << std::endl;
}
```
I will be using the following minimal `.license-tools-config.json` stored right next to `hello.cpp` for auto discovery:
```json
{
  "author": {
    "from_git": true,
  },
  "license": "Unlicense",
}
```
In addition I am using a `.pre-commit-config.yaml` so that
licenses get managed automatically as part of my git hooks:
```yaml
repos:
    - repo: https://github.com/emzeat/mz-lictools
      rev: v2.2
      hooks:
          - id: license-tools
```
Committing my file to git will trigger `pre-commit` to invoke `lictool hello.cpp`. The tool will discover our config and process the new file. As it was not commited to git yet, it will check my `.gitconfig` for author information and add a header accordingly:
```C++
/*
 * hello.cpp
 *
 * Copyright (c) 2021 Marius Zwicker
 * All rights reserved.
 *
 * SPDX-License-Identifier: Unlicense
 *
 * This is free and unencumbered software released into the public domain.
 *
 * Anyone is free to copy, modify, publish, use, compile, sell, or distribute
 * this software, either in source code form or as a compiled binary, for any
 * purpose, commercial or non-commercial, and by any means.
 *
 * In jurisdictions that recognize copyright laws, the author or authors of
 * this software dedicate any and all copyright interest in the software to
 * the public domain. We make this dedication for the benefit of the public
 * at large and to the detriment of our heirs and successors. We intend this
 * dedication to be an overt act of relinquishment in perpetuity of all
 * present and future rights to this software under copyright law.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * For more information, please refer to <https://unlicense.org/>
 */

#include <iostream>

int main(int argc, char* argv[])
{
  std::cout << "Hello World" << std::endl;
}
```
I push this code and I am done.

Let's assume the next day my collegue John Doe is tasked to make an update to our program. He is doing the code changes and while commiting them the `pre-commit` hook jumps back to action invoking `lictool hello.cpp`. This time the tool detects the file was added to git before but the last author touching the file is different from before and hence needs to be added. The resulting file will look like this:
```C++
/*
 * hello.cpp
 *
 * Copyright (c) 2021 Marius Zwicker
 * Copyright (c) 2021 John Doe
 * All rights reserved.
 *
 * SPDX-License-Identifier: Unlicense
 *
 * This is free and unencumbered software released into the public domain.
 *
 * Anyone is free to copy, modify, publish, use, compile, sell, or distribute
 * this software, either in source code form or as a compiled binary, for any
 * purpose, commercial or non-commercial, and by any means.
 *
 * In jurisdictions that recognize copyright laws, the author or authors of
 * this software dedicate any and all copyright interest in the software to
 * the public domain. We make this dedication for the benefit of the public
 * at large and to the detriment of our heirs and successors. We intend this
 * dedication to be an overt act of relinquishment in perpetuity of all
 * present and future rights to this software under copyright law.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * For more information, please refer to <https://unlicense.org/>
 */

#include <iostream>

int main(int argc, char* argv[])
{
  std::cout << "Hello World" << std::endl;
  return 0;
}
```
Now imagine one year later I come back again and need to do yet another change to the file. I make the edit, commit it to git and during the `pre-commit` hooks the `lictool` is run on the file again. This time no new author needs to be added but the copyright years are outdated and get updated accordingy:
```C++
/*
 * hello.cpp
 *
 * Copyright (c) 2021 - 2022 Marius Zwicker
 * Copyright (c) 2021 John Doe
 * All rights reserved.
 *
 * SPDX-License-Identifier: Unlicense
 *
 * This is free and unencumbered software released into the public domain.
 *
 * Anyone is free to copy, modify, publish, use, compile, sell, or distribute
 * this software, either in source code form or as a compiled binary, for any
 * purpose, commercial or non-commercial, and by any means.
 *
 * In jurisdictions that recognize copyright laws, the author or authors of
 * this software dedicate any and all copyright interest in the software to
 * the public domain. We make this dedication for the benefit of the public
 * at large and to the detriment of our heirs and successors. We intend this
 * dedication to be an overt act of relinquishment in perpetuity of all
 * present and future rights to this software under copyright law.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 *
 * For more information, please refer to <https://unlicense.org/>
 */

#include <iostream>

int main(int argc, char* argv[])
{
  std::cout << "Hello World and all other Planets" << std::endl;
  return 0;
}
```


## Configuration Reference

The used license, managed files and used authors get configured through a json
file placed in the root of your project and named '.license-tools-config.json'.

A default configuration file can be generated in the current working directory
by invoking `lictool --sample-config`.

A sample configuration is given below with each option annotated for explanation. _Note: Valid JSON does not accept comments so this is for purpose of illustration only and should not show up in your actual config_.

```json5
{
  "author": {
    // determine the latest copyright author based on the last author in the git
    // history, in case the file was never commited to git use the configured
    // [user] in your local .gitconfig
    "from_git": true,
    // explicitly specify the author. Useful when the code is owned by a company
    // and copyrights should not reflect updates made by individual authors.
    // if both 'from_git' and 'name' have been specified, the 'name' setting
    // will take precedence
    "name": "My Awesome Company",
    // for some licenses an additional company name which is different from the
    // author may be wanted. This can be specified here.
    "company": "the authors",
    // in case the name of an author has changed, e.g. due to marriage you
    // can specify a mapping of old to new name. In such case any changes
    // from the old name will be considered as done by the new name and the
    // respective years simply be extended instead of adding a new author entry.
    "aliases": {
      "<old name>": "<new name"
    }
  },
  // specifies the license to be put at the top of each file. Use lictool --help
  // to get a list of supported licenses
  "license": "GPL-2.0-or-later",
  // do not retain existing licenses on the header but replace all licensing
  // information with the license specified above
  "force_license": false,
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
