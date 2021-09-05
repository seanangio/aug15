library(aug15)
library(dplyr)
library(tidytext)
library(ggplot2)
library(forcats)
library(stringr)
library(tidyr)
library(ggiraph)
library(scales)

years <- c(min(corpus$year), max(corpus$year))
pms <- unique(corpus$pm)
parties <- unique(corpus$party)
facet_var <- "party"
default_max_words <- 12
point_size <- 5

# data prep ---------------------------------------------------------------

filter_corpus <- function(df, years, pms, parties) {
  # df is aug15::corpus
  df %>%
    select(year, pm, party, text) %>%
    filter(
      year >= years[1] & year <= years[2],
      pm %in% pms,
      party %in% parties
    )
}

make_corpus_tidy <- function(df_filtered) {
  df_filtered %>%
    unnest_tokens(word, text)
}

custom_stopwords <- bind_rows(
  #tibble(word = c("india"),lexicon = c("custom")),
  get_stopwords()
)

remove_stopwords <- function(df_tidy) {
  df_tidy %>%
    anti_join(custom_stopwords) # add custom words
}

calculate_tf_idf <- function(df_tidy) {

  words_counted <- df_tidy %>%
    count(year, pm, party, word)

  total_words <- words_counted %>%
    group_by(year, pm, party) %>%
    summarise(total = sum(n), .groups = "drop")

  words_counted %>%
    left_join(total_words) %>%
    # only year really makes sense
    bind_tf_idf(word, year, n) %>%
    select(-total) %>%
    arrange(desc(tf_idf))
}

calculate_sentiment_words <- function(df_nonstop) {
  df_nonstop %>%
    inner_join(get_sentiments("bing"))
}

calculate_net_sentiment <- function(df_bing) {
  df_bing %>%
    group_by(year, pm, party, sentiment) %>%
    summarise(sum = n(), .groups = "drop") %>%
    pivot_wider(names_from = sentiment,
                values_from = sum) %>%
    mutate(sentiment = positive - negative)
}

get_current_n <- function(df) {
  # 2 speeches missing
  total_n <- nrow(corpus) - 2
  n <- nrow(df) - 2

  if (n == total_n) {
    str_glue("{total_n} speeches included.")
  } else {
    str_glue("{n} of {total_n} speeches included.")
  }
}
# data viz ----------------------------------------------------------------

## speech length
plot_speech_length <- function(df) {
  gg <- df %>%
    group_by(year, pm, party) %>%
    summarise(word_count = n(), .groups = "drop") %>%
    mutate(
      word_count = if_else(word_count == 1,
                                NA_integer_,
                                word_count),
      tip = str_glue("{year}: {comma(word_count, accuracy = 1)}")
    ) %>%
    ggplot(aes(x = year, y = word_count/1000,
               color = party, tooltip = tip)) +
    geom_point_interactive(size = point_size) +
    scale_x_continuous("") +
    scale_y_continuous("Words (Thousands)") +
    scale_color_discrete("Party") +
    ggtitle("Total words per speech")
}

add_plot_style <- function(gg) {
  gg <- gg +
    theme_bw(base_size = 24) +
    theme(legend.position = "bottom")

  girafe(ggobj = gg,
         width_svg = 15,
         height_svg = 10)
}

## most frequent words
plot_freq_words <- function(df, facet_var, max_words) {
  if (facet_var == "none") {
    gg <- df %>%
      count(word, sort = TRUE) %>%
      slice_head(n = max_words) %>%
      mutate(word = reorder(word, n)) %>%
      ggplot(aes(fct_reorder(word, n), n)) +
      geom_col_interactive(aes(tooltip = comma(n,
                                        accuracy = 1)))
  } else {
    gg <- df %>%
      group_by(!!rlang::sym(facet_var)) %>%
      count(word, sort = TRUE) %>%
      slice_head(n = max_words) %>%
      ungroup() %>%
      mutate(word = reorder_within(word, n,
                                   !!rlang::sym(facet_var))) %>%
      ggplot(aes(word, n,
                 fill = !!rlang::sym(facet_var))) +
      geom_col_interactive(aes(tooltip = comma(n,
                                          accuracy = 1)),
                           show.legend = FALSE) +
      facet_wrap(as.formula(paste("~", facet_var)),
                 scales = "free") +
      scale_x_reordered()
  }

  gg <- gg +
    labs(x = NULL, y = "Word count") +
    coord_flip() +
    ggtitle("Most frequent words among included speeches")
}

## most important words
plot_tf_idf <- function(df, max_words) {
  gg <- df %>%
    group_by(year) %>%
    slice_head(n = max_words) %>%
    ungroup() %>%
    mutate(word = reorder_within(word, tf_idf,
                                 year)) %>%
    ggplot(aes(word, tf_idf)) +
    geom_col_interactive(aes(tooltip = round(tf_idf,4)),
                         show.legend = FALSE) +
    facet_wrap(~ year,
               scales = "free") +
    scale_x_reordered() +
    scale_y_continuous("TF-IDF") +
    labs(x = NULL) +
    coord_flip() +
    ggtitle("Most 'important' words according to TF-IDF")
}

## +/- words
plot_sentiment_words <- function(df, facet_var,
                                 max_words) {
  if (facet_var == "none") {
    gg <- df %>%
      group_by(word, sentiment) %>%
      summarize(n = n(), .groups = "drop") %>%
      slice_max(n, n = max_words, with_ties = FALSE) %>%
      ggplot(aes(x = fct_reorder(word, n), y = n,
                 fill = sentiment))
  } else {
    gg <- df %>%
      group_by(!!rlang::sym(facet_var),
               word, sentiment) %>%
      summarize(n = n(), .groups = "drop") %>%
      group_by(!!rlang::sym(facet_var)) %>%
      slice_max(n, n = max_words, with_ties = FALSE) %>%
      ungroup() %>%
      mutate(word = reorder_within(word, n,
                    !!rlang::sym(facet_var))) %>%
      ggplot(aes(x = word, y = n,
                 fill = sentiment)) +
      facet_wrap(as.formula(paste("~", facet_var)),
                 scales = "free") +
      scale_x_reordered()
  }
  gg <- gg +
    geom_col_interactive(aes(tooltip = n)) +
    labs(x = NULL) +
    scale_y_continuous("Word Count") +
    scale_fill_discrete("Sentiment") +
    coord_flip() +
    ggtitle("Most frequent positive and negative words")
}

## net sentiment
plot_net_sentiment <- function(df) {
  gg <- df %>%
    mutate(tip = str_glue("{year}: {positive} - {negative} = {sentiment}")) %>%
    ggplot(aes(x = year, y = sentiment,
               color = party)) +
    geom_point_interactive(aes(tooltip = tip),
                           size = point_size) +
    geom_hline(yintercept = 0, linetype="dashed",
               color = "gray", size = 1.5) +
    scale_x_continuous("") +
    scale_y_continuous("Net Sentiment") +
    scale_color_discrete("Party") +
    ggtitle("Difference in Counts of Positive and Negative Words")
}

## specific word trend
plot_specific_word_trend <- function(df, chosen_word) {
  gg <- df %>%
    group_by(year, pm, party, .drop = FALSE) %>%
    filter(word == str_to_lower(chosen_word)) %>%
    summarise(n = n(), .groups = "drop") %>%
    # remove 0 counts for missing years
    filter(year != 1962, year != 1995) %>%
    mutate(tip = str_glue("{year}: {n}")) %>%
    ggplot(aes(x = year, y = n,
               color=party, group = NA)) +
    geom_point_interactive(aes(tooltip = tip),
                           size = point_size) +
    geom_line() +
    scale_x_continuous("") +
    scale_y_continuous("Term Count") +
    scale_color_discrete("Party") +
    ggtitle(str_glue("Frequency of the term '{chosen_word}' among speeches"))
}

plot_chosen <- function(plot_type, df,
                        facet_var,
                        max_words,
                        chosen_word) {

  if (plot_type == "Speech Length") {
    plot_speech_length(df)
  } else if (plot_type == "Most Frequent Words") {
    plot_freq_words(df, facet_var, max_words)
  } else if (plot_type == "Most Important Words") {
    plot_tf_idf(df, max_words)
  } else if (plot_type == "+/- Sentiment Words") {
    plot_sentiment_words(df, facet_var, max_words)
  } else if (plot_type == "Net Sentiment") {
    plot_net_sentiment(df)
  } else if (plot_type == "Specific Word Trend") {
    plot_specific_word_trend(df, chosen_word)
  }
}

plot_explanations <- tribble(
  ~type, ~explanation,
  "Speech Length", "'Speech Length' is a simple count of all words in a speech over time.",
  "Most Frequent Words", "'Most Frequent Words' plots the most frequent words among included speeches, after excluding a generic list of stopwords (a, the, etc). It can be faceted by variables like year, party, or prime minister.",
  "Most Important Words", "'Most Important Words' sorts words according to TF-IDF, which is a statistic that attempts to measure the 'importance' of a word in a speech by adjusting the frequency of a word by how rarely it is otherwise used.",
  "+/- Sentiment Words", "'+/- Sentiment Words' uses the Bing lexicon to label words among included speeches as either positive or negative. It then plots the most frequent positive and/or negative words.",
  "Net Sentiment", "'Net Sentiment' plots the difference between the number of positive and negative words as determined by the Bing lexicon.",
  "Specific Word Trend", "'Specific Word Trend' plots the counts of any user-given word. 'freedom' is provided as an example."
)

print_plot_explanation <- function(plot_type) {
  plot_explanations %>%
    filter(type == plot_type) %>%
    pull(explanation)
}
