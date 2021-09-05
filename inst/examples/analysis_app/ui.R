library(shiny)
library(shinyWidgets)
library(shinycssloaders)

ui <- fluidPage(
    theme = "my.css",
    titlePanel("Indian Independence Day Speeches"),
    sidebarLayout(
        sidebarPanel(
            actionButton("reset_inputs",
                         "Reset All Inputs",
                         icon = icon("refresh"),
                         width = "50%"),
            br(),br(),
            em(textOutput("current_n")),
            em("1962 and 1995 are missing from the data set."),
            hr(),
            sliderTextInput(
                inputId = "pick_year",
                label = "Years",
                choices = min(corpus$year):max(corpus$year),
                selected = c(min(corpus$year),
                             max(corpus$year))
            ),
            pickerInput(
                inputId = "pick_pm",
                label = "Prime Ministers",
                choices = unique(corpus$pm),
                selected = unique(corpus$pm),
                options = list(
                    `actions-box` = TRUE),
                multiple = TRUE
            ),
            pickerInput(
                inputId = "pick_party",
                label = "Parties",
                choices = unique(corpus$party),
                selected = unique(corpus$party),
                options = list(
                    `actions-box` = TRUE),
                multiple = TRUE
            ),
            hr(),
            pickerInput(
                inputId = "plot_type",
                label = "Plot Type",
                choices = plot_explanations$type,
                selected = plot_explanations$type[1]
            ),
            conditionalPanel(
                condition = "input.plot_type == 'Most Frequent Words' ||
                               input.plot_type == 'Most Important Words' ||
                               input.plot_type == '+/- Sentiment Words'",
                numericInput(
                    inputId = "max_words",
                    label = "Number of Words to Include",
                    value = default_max_words,
                    min = 1
                )
            ),
            conditionalPanel(
                condition = "input.plot_type == 'Most Frequent Words' ||
                                 input.plot_type == '+/- Sentiment Words'",
                pickerInput(
                    inputId = "facet_var",
                    label = "Facet Variable",
                    choices = c("None" = "none",
                                "Year" = "year",
                                "Prime Minister" = "pm",
                                "Party" = "party"),
                    selected = "none"
                )
            ),
            conditionalPanel(
                condition = "input.plot_type == 'Specific Word Trend'",
                textInput("chosen_word", "Word to Count",
                          value = "freedom")
            ),
            tags$a(href="https://github.com/seanangio/aug15",
                   "Code & Documentation on GitHub",
                   target="_blank")
        ),
        mainPanel(
            withSpinner(girafeOutput("plot")),
            textOutput("plot_explanation")
        )
    )
)
