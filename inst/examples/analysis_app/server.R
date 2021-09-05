library(shiny)
source("global.R")

shinyServer(function(input, output, session) {
    session$onSessionEnded(stopApp)

    corpus_filtered <- reactive({
        filter_corpus(corpus, input$pick_year,
                      input$pick_pm, input$pick_party)
    })

    corpus_tidy <- reactive({
        make_corpus_tidy(corpus_filtered())
    })

    corpus_nonstop <- reactive({
        remove_stopwords(corpus_tidy())
    })

    corpus_tf_idf <- reactive({
        calculate_tf_idf(corpus_tidy())
    })

    corpus_bing <- reactive({
        calculate_sentiment_words(corpus_nonstop())
    })

    corpus_net_sentiment <- reactive({
        calculate_net_sentiment(corpus_bing())
    })

    data_to_plot <- reactive({
        switch(input$plot_type,
               "Speech Length" = corpus_tidy(),
               "Most Frequent Words" = corpus_nonstop(),
               "Most Important Words" = corpus_tf_idf(),
               "+/- Sentiment Words" = corpus_bing(),
               "Net Sentiment" = corpus_net_sentiment(),
               "Specific Word Trend" = corpus_tidy())
    })

    chosen_plot <- reactive({
        plot_chosen(input$plot_type, data_to_plot(),
                    input$facet_var, input$max_words,
                    input$chosen_word)
    })

    output$plot <- renderGirafe({
        add_plot_style(chosen_plot())
    })

    output$plot_explanation <- renderText({
        print_plot_explanation(input$plot_type)
    })

    output$current_n <- renderText({
        get_current_n(corpus_filtered())
    })

    observeEvent(input$reset_inputs, {
        updateSliderTextInput(session, "pick_year",
                              selected = c(min(corpus$year),
                                           max(corpus$year)))
        updatePickerInput(session, "pick_pm",
                          selected = unique(corpus$pm))
        updatePickerInput(session, "pick_party",
                          selected = unique(corpus$party))
        updateNumericInput(session, "max_words",
                           value = default_max_words)
        updatePickerInput(session, "facet_var",
                          selected = "none")
        updateTextInput(session, "chosen_word",
                        value = "freedom")
    })

})
