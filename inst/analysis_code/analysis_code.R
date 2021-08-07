# this is my external script

## @ knitr setup
library(aug15)
library(DT)
library(dplyr)
library(ggplot2)
library(tidytext)
library(magrittr)

prep_dt <- function(df) {
  df %>%
    select(
      Year = year,
      `Prime Minister` = pm,
      Party = party,
      Title = title,
      `English text` = text,
      Source = source,
      Footnote = footnote,
      URL = url
    )

}

draw_dt <- function(df) {
  datatable(df,
            class = "cell-border stripe order-column compact",
            selection = list(mode = "single", target = "cell"),
            extensions = "Responsive",
            options = list(
              columnDefs = list(
                list(
                  # ellipsis for long text cols
                  targets = c(4:7),
                  render = JS(
                    "function(data, type, row, meta) {",
                    "return type === 'display' && data.length > 20 ?",
                    "'<span title=\"' + data + '\">' + data.substr(0, 20) + '...</span>' : data;",
                    "}"
                  )
                )
              )
            ),
            rownames = FALSE,
            filter = "top",
            escape = FALSE
  )
}

head(corpus) %>%
  prep_dt() %>%
  draw_dt()

## @knitr word_counts
# corpus %>%
#   unnest_tokens(word, text) %>%
#   group_by(year, pm, party) %>%
#   count(word) %>%
#   group_by(year, pm, party) %>%
#   summarise(sum = sum(n)) %>%
#   mutate(sum = ifelse(sum == 1, NA, sum)) %>%
#   ggplot(aes(x = year, y = sum)) +
#   geom_point(aes(color = party)) +
#   theme(legend.position = "bottom")
