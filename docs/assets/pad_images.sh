#!/bin/bash

for img in *=.png; do
    echo "img ${img}"
  # Get current dimensions of the image.
  height=$(identify -format "%h" "$img")  # Height of the current image

  # Calculate the desired width for a 4:1 aspect ratio.
  desired_width=$((4 * height))

  # Add padding to the left and right sides of the image.
  convert "$img" -gravity center -background white -extent "${desired_width}x${height}" "${img%.png}_padded.png"
done
