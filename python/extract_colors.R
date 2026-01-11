#!/usr/bin/env Rscript
# Extract color palette from ggplot2 defaults

library(ggplot2)
library(aug15)

# Get unique parties
parties <- unique(corpus$party)
cat("Parties in dataset:\n")
print(parties)
cat("\n")

# Create a dummy plot to extract default colors
dummy_data <- data.frame(
  x = 1:length(parties),
  y = 1:length(parties),
  party = parties
)

p <- ggplot(dummy_data, aes(x = x, y = y, color = party)) +
  geom_point(size = 5) +
  scale_color_discrete()

# Extract the colors
colors <- ggplot_build(p)$data[[1]]$colour

# Print color mapping
cat("Color mapping:\n")
for (i in seq_along(parties)) {
  cat(sprintf("%s: %s\n", parties[i], colors[i]))
}
