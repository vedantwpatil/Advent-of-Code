use std::fs::File;
use std::io::{self, BufRead, BufReader};

fn main() -> io::Result<()> {
    let file = File::open("input.txt")?;

    let reader = BufReader::new(file);

    for line in reader.lines() {
        let numbers: Vec<i32> = line?
            .split_whitespace()
            .map(|s| s.parse().unwrap())
            .collect();

        let num1 = numbers[0];
        let num2 = numbers[1];
    }
    Ok(())
}
