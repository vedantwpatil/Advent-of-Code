use std::fs::File;
use std::io::Result;
use std::io::{BufRead, BufReader};

fn main() -> Result<()> {
    let file = File::open("../../input")?;
    let buf_reader = BufReader::new(file);

    println!("Hello, secret entrance");

    Ok(())
}
