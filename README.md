# EightDAD

[![PyTest](https://github.com/pyglet/pyglet/actions/workflows/unittests.yml/badge.svg)](https://github.com/pyglet/pyglet/actions/workflows/unittests.yml)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-brightgreen.svg)](https://opensource.org/licenses/BSD-2-Clause)

## Overview

### What
For now, it's only a [Chip-8 Virtual Machine](https://en.wikipedia.org/wiki/CHIP-8) in python.

The name comes from the tools I hope to add:

- [x] **Eight**, as in Chip-8 VM
- [ ] **D**ebugger
- [ ] **A**ssembler
- [ ] **D**isassembler

Only the [classic CHIP-8 instruction set](https://github.com/mattmikolay/chip-8/wiki/CHIP%E2%80%908-Technical-Reference)
is currently supported. [XO-CHIP](http://johnearnest.github.io/Octo/docs/XO-ChipSpecification.html) and other extensions
are not currently supported, but may be added one day.

### How

#### Requirements
1. Python Version >= 3.8
2. (GUI only) OpenGL 3.3+, Python version < 3.12
3. (TUI only) Unicode support in your terminal

The GUI does not yet work with Python 3.11 due to arcade's dependencies not yet supporting it.

#### Installing

1. Clone this repo locally
2. [Make a new virtualenv and activate it](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment)
3. Change directories into the repo copy
4. `pip install .` if you only want to run ROMs, or `pip install -e .` to install an editable copy.

Dependencies will be automatically installed.

#### Running roms

*Reminder: only the original CHIP-8 instruction set is supported.*

To run a ROM, make sure you're in the activated virtual environment, then use the following:
```commandline
eightdad -r path/to/chip8.rom
```

If you want to use the TUI, run `eightdad-tui` instead.

```commandline
eightdad-tui -r path/to/chip8.rom
```

For additional information, use the help option:
```
eightdad --help
```

### Why

I want to learn more about assemblers, Virtual Machines, and implementing
languages! This is a step toward other projects and becoming a better
developer.
 
#### But [Octo](https://github.com/JohnEarnest/Octo) already exists!

I know. I like it, and I've contributed to both Octo and its more resource-effiicent C implementation, [c-octo](https://github.com/JohnEarnest/c-octo). Writing my own tools will help me more with the goals above.
