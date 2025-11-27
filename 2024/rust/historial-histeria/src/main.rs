use std::collections::HashMap;
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
        let left_value: i32 = words[0].parse().unwrap();
        let right_value: i32 = words[1].parse().unwrap();

        left.push(left_value);
        right.push(right_value);
    }
    // Create frequency map of the RIGHT list
    // We pass the rerference so we don't lose ownership of 'right'
    let right_counts = frequency_counter(&right);

    // Calculate the Similarity Score
    let mut similarity_score: i32 = 0;
    for num in &left {
        // .get() returns Option<&count>, so we unwrap_or(&0) to get 0 if not found
        let count = right_counts.get(num).unwrap_or(&0);
        similarity_score += num * count;
    }

    println!("Similarity Score: {}", similarity_score);

    left.sort();
    right.sort();

    let total_distance: i32 = left
        .iter()
        .zip(right.iter())
        .map(|(l, r)| (l - r).abs())
        .sum();

    println!("Summed Distances: {}", total_distance);

    Ok(())
}

fn frequency_counter(items: &[i32]) -> HashMap<i32, i32> {
    let mut counts = HashMap::new();
    for &item in items {
        *counts.entry(item).or_insert(0) += 1;
    }
    counts
}
