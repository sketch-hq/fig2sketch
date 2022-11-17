# .fig to Sketch converter

fig2sketch is a command line tool that converts .fig files into .sketch design files, that can be opened with [Sketch](https://www.sketch.com/) applications.

## How does it work

fig2sketch reads the design data from the .fig file and converts it to data that can be opened by Sketch apps. The conversion is as most accurate possible. However, the kind of data supported by both .fig and .sketch files is not exactly the same. This means that some data needs to be prepared in slightly different ways so it is represented with similar fidely in Sketch apps.

### Using the source code

1. Run `python fig2sketch.py <path to .fig file> <path to store the .sketch file>`
2. Open the resulting .sketch file in Sketch

### Using a release binary

1. Run `fig2sketch <path to .fig file> <path to store the .sketch file>`
2. Open the resulting .sketch file in Sketch


### Options

- Pass `--salt 12345678` to ensure a consistent conversion order
- Pass `--dump-fig-json example/figma.json` (which whichever path/name you like) to dump the generated JSON from the fig file

Example:

`python fig2sketch.py --salt 12345678 example/shapes_party.fig output/output.sketch --dump-fig-json example/figma.json`


## Install

Use Python 3
```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### Performance

There are some performance improvements for data read from the .fig file and also for the serialization of the output data into the .sketch. If you want to enjoy those performance improvements do this:

```
sh scripts/install_patched_orjson.sh
sh scripts/install_fig_kiwi.sh
```

For the second one you will need to have [Rust](https://www.rust-lang.org/) and [Cargo](https://doc.rust-lang.org/cargo/) installed in your machine.


## Running the tests

In order to run the tests, just execute this in the project root:
```
pytest
```


## Current support

fig2ksetch supports most frequently used data from the .fig file. Effectively, common .fig documents will be converted to .sketch and represented almost identically to the original intended representation of the .fig file.

Data found in the .fig that don't have any reasonable match in Sketch will be ignored (and a warning will be issued) during the conversion. 


### Frames vs Artboards

"Frames" in .fig documents are a way to group layers contained in them. Sketch has a similar concept which is "Artboards". However, while Frames can be nested and they supposedly behave in the same way at every nesting or main level, Artboards in Sketch only exist at the main level inside the canvas. Artboards cannot be nested. 

Additionally, Frames and Artboards support different types of styling.

Because of this, fig2sketch mostly applies 2 rules to Frames transformation:
* If the Frame is nested inside another Frame, it will be converted to a Group and a background layer will be added containing the styles that the Frame had originally
* If the Frame is at the top level, but contains styles that don't match Sketch Artboards' styles, the Frame will be converted to an Artboard and a background layer will be added containing the styles that the Frame had originally

Since this kind of transformation will happen with most .fig files, a warning will not be emitted in the command output.

## About .sketch files

.sketch files are build based on an (open format)[https://github.com/sketch-hq/sketch-document]. Feel free to take a look if you want to know more about the format, and especially if you plan to contribute to the project.

## Contributing
We would love you to contribute to fig2sketch, pull requests are welcome! Please see the [CONTRIBUTING guidelines](CONTRIBUTING.md) for more information.

## License
The scripts and documentation in this project are released under the [MIT license](LICENSE)