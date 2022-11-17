mod kiwi;

use std::{fs::File, error::Error, io::{Read, Seek, SeekFrom}, collections::HashMap};
use crate::kiwi::KiwiReader;
use pyo3::{prelude::*, types::{PyDict, PyList, PyFunction, PyString}};

struct Field {
    name: String,
    datatype: i32,
    array: bool,
}

struct Type<'a> {
    kind: u8,
    name: String,
    fields: HashMap<u32, Field>,
    converter: Option<&'a PyFunction>
}

fn decode_type<R: std::io::Read>(py: Python, kiwi: &mut KiwiReader<R>, types: &Vec<Type>, datatype: i32, array: bool) -> PyObject {
    if array {
        if datatype == -2 {
            // Fast path for byte arrays
            let len = kiwi.uint() as usize;
            return kiwi.bytes(len).into_py(py);
        } else {
            let count = kiwi.uint();
            return PyList::new(py, (0..count).map(|_| decode_type(py, kiwi, types, datatype, false))).into();
        }
    }
    match datatype {
        -1 => kiwi.bool().into_py(py),
        -2 => kiwi.byte().into_py(py),
        -3 => kiwi.int().into_py(py),
        -4 => kiwi.uint().into_py(py),
        -5 => kiwi.float().into_py(py),
        -6 => kiwi.string().into_py(py),
        _ => {
            let t = &types[datatype as usize];
            if t.kind == 0 {
                // Enum
                t.fields.get(&kiwi.uint()).unwrap().name.clone().into_py(py)
            } else if t.kind == 1 {
                // Struct
                let fields = PyDict::new(py);

                for i in 1..=t.fields.len() {
                    let f = &t.fields[&(i as u32)];
                    fields.set_item(f.name.clone(), decode_type(py, kiwi, types, f.datatype, f.array)).unwrap();
                }

                if let Some(converter) = t.converter {
                    return converter.call1((fields,)).unwrap().extract().unwrap();
                }

                fields.into()
            } else {
                // Message
                let fields = PyDict::new(py);
                loop {
                    let fid = kiwi.uint();
                    if fid == 0 { break }
                    let field = &t.fields[&fid];
                    fields.set_item(field.name.clone(), decode_type(py, kiwi, types, field.datatype, field.array)).unwrap();
                }

                fields.into()
            }
        }
    }
}

fn read_schema(mut kiwi: KiwiReader<impl Read>, type_converters: &PyDict) -> Vec<Type> {
    let mut types = Vec::new();

    for _ in 0..kiwi.uint() {
        let name = kiwi.string();
        let kind = kiwi.byte();

        let mut fields: HashMap<u32, Field> = HashMap::new();

        for _ in 0..kiwi.uint() {
            let f = Field {
                name: kiwi.string(),
                datatype: kiwi.int(),
                array: kiwi.bool()
            };
            fields.insert(kiwi.uint(), f);
        }

        let converter = type_converters.get_item(&name).map(|c| c.extract().unwrap());

        types.push(Type { name, kind, fields, converter });
    }

    types
}

fn read_fig<'a, R: Read>(py: Python<'a>, mut fig: R, type_converters: &'a PyDict) -> Result<PyObject, Box<dyn Error>> {
    // Skip header
    let mut buf: [u8;4] = [0; 4];
    fig.read_exact(&mut buf)?;
    fig.read_exact(&mut buf)?;

    // Read version
    fig.read_exact(&mut buf)?;
    let _version = u32::from_le_bytes(buf);

    // Read schema segment
    fig.read_exact(&mut buf)?;
    let segment_len = u32::from_le_bytes(buf);

    let segment_reader = fig.by_ref().take(segment_len.into());
    let zlib = flate2::read::DeflateDecoder::new(segment_reader);

    let kiwi = KiwiReader::new(zlib.bytes());
    let types = read_schema(kiwi, type_converters);

    // Find root type
    let root_index = types.iter().enumerate().filter(|(_, t)| t.name == "Message").next().unwrap().0;

    // Read data segment
    fig.read_exact(&mut buf)?;
    let segment_len = u32::from_le_bytes(buf);

    let segment_reader = fig.by_ref().take(segment_len.into());
    let zlib = flate2::read::DeflateDecoder::new(segment_reader);

    let mut kiwi = KiwiReader::new(zlib.bytes());

    Ok(decode_type(py, &mut kiwi, &types, root_index as i32, false))
}

#[pyfunction]
fn decode<'a>(py: Python<'a>, path: &'a PyString, type_converters: &'a PyDict) -> PyResult<PyObject> {
    let mut f = File::open(path.to_string()).unwrap();
    let mut buf = [0u8; 1];
    f.read_exact(&mut buf).unwrap();

    if buf[0] == 'P' as u8 {
        let mut zip = zip::ZipArchive::new(f).unwrap();
        let fig = zip.by_name("canvas.fig").unwrap();
        Ok(read_fig(py, fig, type_converters).unwrap())
    } else {
        f.seek(SeekFrom::Start(0)).unwrap();
        Ok(read_fig(py, f, type_converters).unwrap())
    }
}

#[pymodule]
fn fig_kiwi(_: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(decode, m)?)?;

    Ok(())
}
