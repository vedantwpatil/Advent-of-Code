use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader};

fn main() -> std::io::Result<()> {
    let file = File::open("input.txt")?;
    let buf_reader = BufReader::new(file);

    let (mut left, mut right): (Vec<i32>, Vec<i32>) = buf_reader
        .lines()
        .map(|line| {
            let line = line?;
            let mut words = line.split_whitespace();
            let l = words
                .next()
                .ok_or_else(|| {
                    std::io::Error::new(std::io::ErrorKind::InvalidData, "missing left")
                })?
                .parse::<i32>()
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
            let r = words
                .next()
                .ok_or_else(|| {
                    std::io::Error::new(std::io::ErrorKind::InvalidData, "missing right")
                })?
                .parse::<i32>()
                .map_err(|e| std::io::Error::new(std::io::ErrorKind::InvalidData, e))?;
            Ok((l, r))
        })
        .collect::<std::io::Result<Vec<(i32, i32)>>>()?
        .into_iter()
        .unzip();

    let right_counts = frequency_counter(&right);

    let similarity_score: i32 = left
        .iter()
        .map(|num| num * right_counts.get(num).unwrap_or(&0))
        .sum();

    println!("Similarity Score: {}", similarity_score);

    left.sort();
    right.sort();

    let total_distance: i32 = left.iter().zip(&right).map(|(l, r)| (l - r).abs()).sum();

    println!("Summed Distances: {}", total_distance);

    Ok(())
}

fn frequency_counter(items: &[i32]) -> HashMap<i32, i32> {
    let mut counts = HashMap::new();
    for &item in items {
        *counts.entry(item).or_default() += 1;
    }
    counts
}
