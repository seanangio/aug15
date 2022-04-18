## code to prepare `corpus` dataset goes here
library(here)
library(pdftools)
library(purrr)
library(stringr)
library(tibble)
library(readr)
library(dplyr)

# prepare text found in pdfs
file_paths <- list.files(here("inst", "extdata"),
                         full.names = TRUE)

speech_list <- file_paths %>%
  map(pdf_text) %>%
  map(str_c, collapse = "") %>%
  map(unlist)

speech_tbl <- tibble(
  year = str_sub(file_paths, -8, -5) %>%
    as.integer(),
  text = speech_list %>% unlist
)

# join with spreadsheet data
speech_data <- read_csv("data-raw/aug_15_speech_data.csv")

corpus <- speech_data %>%
  left_join(speech_tbl, by = "year") %>%
  mutate(text = str_trim(str_replace_all(text, "�", "")))

# output an rda file for the package
usethis::use_data(corpus, overwrite = TRUE)

# output a csv file for github
final_csv_folder <- here("inst", "final_csv")
if (!dir.exists(final_csv_folder)) {
  dir.create(final_csv_folder)
}
write_csv(corpus, paste0(final_csv_folder, "/corpus.csv"))
