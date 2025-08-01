# IBM - Data Science
# Tool for Data Science
# RStudio IDE

# Lab: Creating an Interactive Map in R 

## Installing libraries related to project

# Check and install 'shiny' if not already installed
if (!requireNamespace("shiny", quietly = TRUE)) {
  install.packages("shiny")
}

# Check and install 'leaflet' if not already installed
if (!requireNamespace("leaflet", quietly = TRUE)) {
  install.packages("leaflet")
}

## Loading Libraries
library(shiny)
library(leaflet)

# user interface
ui <- fluidPage(
  leafletOutput("mymap"),
  p(),
  actionButton("recalc", "New points"),
  p(),
  textOutput("coordinates")
)

# server logic
server <- function(input, output, session) {
  
  # generate new points
  points <- eventReactive(input$recalc, {
    # Generate 40 random points within a reasonable range for Europe (longitudes around 13, latitudes around 48)
    cbind(rnorm(40) * 2 + 13, rnorm(40) + 48)
  }, ignoreNULL = FALSE)
  
  # Render with OpenStreetMap
  output$mymap <- renderLeaflet({
    leaflet() %>%
      addProviderTiles(providers$OpenStreetMap) %>%
      addMarkers(data = points())
  })
  
  # observer to update the text output with the coordinates
  observeEvent(points(), {
    coords_text <- paste(
      "The coordinates are:",
      paste(capture.output(print(points())), collapse = "\n")
    )
    output$coordinates <- renderText({
      coords_text
    })
  })
  
  # observer to show a different message on map clicks
  observeEvent(input$mymap_marker_click, {
    output$coordinates <- renderText({
      "You have selected a marker!"
    })
  })
}

shinyApp(ui, server)