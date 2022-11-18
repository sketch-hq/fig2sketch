from figformat import kiwi
import fig_kiwi
from zipfile import ZipFile
from converter.positioning import Matrix


def test_kiwi_decoders():
    path = "tests/data/structure.fig"

    fig = ZipFile(path).open("canvas.fig")
    pykiwi = kiwi.decode(fig, {})
    rskiwi = fig_kiwi.decode(path, {})

    assert pykiwi == rskiwi


def test_kiwi_type_converters():
    type_converters = {
        "GUID": lambda x: (x["sessionID"], x["localID"]),
        "Matrix": lambda m: Matrix(
            [[m["m00"], m["m01"], m["m02"]], [m["m10"], m["m11"], m["m12"]], [0, 0, 1]]
        ),
    }
    path = "tests/data/structure.fig"

    fig = ZipFile(path).open("canvas.fig")
    pykiwi = kiwi.decode(fig, type_converters)
    rskiwi = fig_kiwi.decode(path, type_converters)

    assert pykiwi == rskiwi
