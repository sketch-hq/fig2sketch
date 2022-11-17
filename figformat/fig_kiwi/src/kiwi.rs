use std::io::{Bytes, Read};

pub struct KiwiReader<R> {
    reader: Bytes<R>
}

impl<R: Read> KiwiReader<R> {
    pub fn new(reader: Bytes<R>) -> KiwiReader<R> {
        KiwiReader { reader }
    }

    pub fn byte(&mut self) -> u8 {
        self.reader.next().unwrap().unwrap()
    }

    pub fn bool(&mut self) -> bool {
        self.byte() > 0
    }

    pub fn uint(&mut self) -> u32 {
        let mut shift: u8 = 0;
        let mut result: u32 = 0;

        loop {
          let byte = self.byte();
          result |= ((byte & 127) as u32) << shift;
          shift += 7;

          if (byte & 128) == 0 || shift >= 35 {
            break;
          }
        }

        result
    }

    pub fn bytes(&mut self, len: usize) -> Vec<u8> {
        self.reader.by_ref().take(len).map(|x| x.unwrap()).collect()
    }

    pub fn int(&mut self) -> i32 {
        let value = self.uint();
        (if (value & 1) != 0 { !(value >> 1) } else { value >> 1 }) as i32
    }

    pub fn float(&mut self) -> f32 {
        let b = self.byte();

        if b == 0 {
            return 0.0;
        }

        let mut bits: u32 =
            b as u32 |
            ((self.byte() as u32) << 8) |
            ((self.byte() as u32) << 16) |
            ((self.byte() as u32) << 24);

        bits = (bits << 23) | (bits >> 9);

        f32::from_bits(bits)
    }

    pub fn string(&mut self) -> String {
        let y = self.reader.by_ref().map_while(|x| { let y = x.unwrap(); if y!= 0 { Some(y) } else { None } });
        String::from_utf8_lossy(&y.collect::<Vec<u8>>()).to_string()
    }

}
