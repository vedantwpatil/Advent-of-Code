use std::fs::File;
use std::io::{BufRead, BufReader};

fn main() -> std::io::Result<()> {
    let file = File::open("input.txt")?;
    let buf_reader = BufReader::new(file);

    // Need to sort the left and right lists
    // After sorting the lists we then need to part together the smallest elements from each list
    // Calculate the difference and then sum all those distances
    let mut left: Vec<i32> = Vec::new();
    let mut right: Vec<i32> = Vec::new();

    for line in buf_reader.lines() {
        // Need to add error handling in order to print
        let error_checked_line = line?;
        let words: Vec<&str> = error_checked_line.split_whitespace().collect();
        left.push(words[0].parse().unwrap());
        right.push(words[1].parse().unwrap());
    }

    left.sort();
    right.sort();

    let mut sum_distance = 0;

    for i in 0..left.len() {
        let distance = (left[i] - right[i]).abs();
        println!("Left: {}", left[i]);
        println!("Right: {}", right[i]);
        println!("Distance: {}", distance);
        sum_distance += distance;
    }

    println!("{}", sum_distance);
    Ok(())
}
