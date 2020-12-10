
import numpy as np
from datetime import datetime

# Import to handle data parsed to bokeh plots
from bokeh.models import ColumnDataSource

# Import to create plot, show plot, and output plot
from bokeh.plotting import figure, output_file, show

# Import to allow for bokeh plot components to be returned
from bokeh.embed import components

# Import to handle layout of the bokeh plots
from bokeh.layouts import column, row, layout

# Importing the RangeTool used in the Timeline plot
from bokeh.models import RangeTool

# Import to set the range of the Timeline
from bokeh.models import Range1d

# Import for the button and datepicker widget
from bokeh.models import Button, DatePicker

# Import for callback on an event
from bokeh.events import ButtonClick

# Import legend to show the legend for the timeline and histogram
from bokeh.models import Legend

# Import for CustomJs callbacks
from bokeh.models.callbacks import CustomJS

# screen resolution
# TODO adjust to local resolution
screen_height = 1080
screen_length = 1920


def render_timeline(dates, densities):

    time_data = np.array(
        [datetime.strptime(date, '"%Y-%m-%d"') for date in dates])

    # Set the global max and min for the date ranges
    min_date_interval = time_data.min().date()
    max_date_interval = time_data.max().date()

    # Tranforming the max and min dates into np datetime
    # for the x_range of timeline_zoom
    min_date_timestamp = np.datetime64(min_date_interval.isoformat())
    max_date_timestamp = np.datetime64(max_date_interval.isoformat())

    # Create the Timeline figure
    timeline_select = figure(
        background_fill_color="#fafafa",
        x_axis_type='datetime',
        x_axis_label="Date",
        # y_axis_type=None,
        y_axis_label="Amount of tweets",
        tools="pan,box_zoom,wheel_zoom,reset",
        toolbar_location=None,  # "above",
        plot_width=int(screen_length*0.7),
        plot_height=int(screen_height*0.3))

    # Load the data for the timeline into a ColumnDataSource for the plot
    source_total = ColumnDataSource(data=dict(date=time_data, freq=densities))

    # Plot a line on the graph for the total amount of tweets per day
    total_tweets_per_day = timeline_select.line(
        'date',
        'freq',
        source=source_total,
        line_color="black")

    # Load the data for the geo-selected line,
    # at initialization its 0 for all dates
    source_selected = ColumnDataSource(data=dict(
        date=time_data, freq=np.zeros(len(time_data))))

    # Plot the line for the selected tweets
    selected_tweets_per_day = timeline_select.line(
        'date',
        'freq',
        source=source_selected,
        line_color="blue")

    # Set the selected line to not be visible initially
    selected_tweets_per_day.visible = False

    # Zoom graph (START) #

    timeline_zoom = figure(
        background_fill_color="#fafafa",
        x_axis_type='datetime',
        # x_axis_label="Date",
        x_axis_location="above",
        x_range=Range1d(min_date_timestamp, max_date_timestamp),
        # y_axis_type=None,
        y_axis_label="Amount of tweets",
        tools="xpan",
        toolbar_location=None,
        plot_width=int(screen_length*0.7)+108,
        plot_height=int(screen_height*0.3))

    total_tweets_per_day_zoom = timeline_zoom.line(
        'date',
        'freq',
        source=source_total,
        line_color="black",
        line_width=2)

    # Plot the line for the selected tweets
    selected_tweets_per_day_zoom = timeline_zoom.line(
        'date',
        'freq',
        source=source_selected,
        line_color="blue",
        line_width=2)

    # Set the selected line to not be visible initially
    selected_tweets_per_day_zoom.visible = False

    # Zoom graph (END) #

    # Legend Select Plot (START) #

    # Declare an empty list to contain the items in the legend
    legend_items = []

    # Add the total tweets to the legend
    legend_items.append(("Total", [total_tweets_per_day]))

    # Add the selected tweets to the legend
    legend_items.append(("Selection", [selected_tweets_per_day]))

    # Add the legend_items to the legend object
    legend = Legend(items=legend_items)

    # Set the onclick action of the legend to hide
    legend.click_policy = "hide"

    timeline_select.add_layout(legend)

    # Legend Select Plot(END) #

    # Legend Zoom Plot (START) #

    # # Declare an empty list to contain the items in the legend
    legend_items_zoom = []

    # Add the total tweets to the legend
    legend_items_zoom.append(("Total", [total_tweets_per_day_zoom]))

    # Add the selected tweets to the legend
    legend_items_zoom.append(("Selection", [selected_tweets_per_day_zoom]))

    # Add the legend_items to the legend object
    legend_zoom = Legend(items=legend_items_zoom)

    # Set the onclick action of the legend to hide
    legend_zoom.click_policy = "hide"

    timeline_zoom.add_layout(legend_zoom)

    # Legend (END) #

    # Declare a button which will update the values in Map
    # according to the time period
    update_time_button = Button(
        label="Update",
        button_type="success",
        width=96,  # int(screen_length*0.05),
        height=38)  # int(screen_height*0.035))

    # Create a datepicker for the start date
    start_date_input = DatePicker(
        title='Start date',
        value=min_date_interval,
        min_date=min_date_interval,
        max_date=max_date_interval,
        width=96,  # int(screen_length*0.05),
        height=54)  # int(screen_height*0.05))

    # Create a datepicker for the end date
    end_date_input = DatePicker(
        title='End date',
        value=max_date_interval,
        min_date=min_date_interval,
        max_date=max_date_interval,
        width=96,  # int(screen_length*0.05),
        height=54)  # int(screen_height*0.05))

    # Declare a RangeTool for the selection of the date ranges
    range_tool = RangeTool(x_range=timeline_zoom.x_range)

    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.1

    # Add the range_tool to the Timeline plot
    timeline_select.add_tools(range_tool)
    timeline_select.toolbar.active_multi = range_tool

    # DEVELOPMENT HELP #

    # print_button = Button(
    #     label="Print",
    #     button_type="success",
    #     width=int(screen_length*0.05),
    #     height=int(screen_height*0.075))

    # print_callback = CustomJS(
    #     args=dict(
    #         min_date_interval=min_date_interval,
    #         max_date_interval=max_date_interval),
    #     code="""
    #     console.log(min_date_interval, max_date_interval)
    # """)

    # print_button.js_on_click(print_callback)

    # #

    # Callback to handle the changing x range of the range tool
    # Will update the corresponding start and end dates in the datepickers
    # datepickers: start_date_input and end_date_input
    range_tool_to_datepicker_callback = CustomJS(
        args=dict(
            x_range=range_tool.x_range,
            start_input=start_date_input,
            end_input=end_date_input,
            min_date=min_date_interval,
            max_date=max_date_interval,
            ),
        code="""
        // Check if the value is a drag input
        if ((x_range.start % 1000) != 0){

            // Create date objects of the DatePicker inputs
            const picker_start_date = new Date(start_input.value)

            // Extract the start value of the interval
            // and convert it into correct format for datepicker
            const start_date = new Date(x_range.start)

            // Declare the minimum date of the range
            const minimum = new Date(min_date)

            // Check whether the date is less than the minimum of of the data
            if(start_date >= minimum){
                // If the date is after the global minimum
                // then take the current x range value
                start_input.value = start_date
            }
            else{
                // If the date is before the global minimum
                // then take the global minimum as the start of the range
                start_input.value = min_date
            }
            start_input.change.emit()
        }

        // Similar for the end of the range tool
        if ((x_range.end % 1000) != 0){

            // Create date objects of the DatePicker inputs
            const picker_end_date = new Date(end_input.value)

            // Extract the end value of the interval
            // and convert it into correct format for datepicker
            const end_date = new Date(x_range.end)

            // Declare the maximum of the range
            const maximum = new Date(max_date)

            // Check whether the date is less than the maximum of of the data
            if(end_date <= maximum){
                // If the date is before the global maximum
                // then take the x range value
                end_input.value = end_date
            }
            else{
                // If the date is after the global maximum
                // then take the global maximum as the end of the range
                end_input.value = max_date
            }
            end_input.change.emit()
        }

        """
        )

    # Link the range_tool to the callbacks for its interval
    range_tool.x_range.js_on_change('start', range_tool_to_datepicker_callback)
    range_tool.x_range.js_on_change('end', range_tool_to_datepicker_callback)

    # Callback for when the datepicker of starting date changes
    # AND button is pressed (due to asynchronus behavior of udpates)
    date_picker_to_range_tool_callback = CustomJS(
        args=dict(
            x_range=range_tool.x_range,
            start_input=start_date_input,
            end_input=end_date_input
            ),
        code="""
        const start_date = new Date(start_input.value)
        const end_date = new Date(end_input.value)

        x_range.start = start_date.valueOf()
        x_range.end = end_date.valueOf()
        x_range.change.emit()
        """
        )

    update_time_button.js_on_click(date_picker_to_range_tool_callback)

    # Callback for the update button, which sends start and end dates to backend
    selection_to_backend_callback = CustomJS(
        args=dict(
            start_input=start_date_input,
            end_input=end_date_input
            ),
        code="""
        const start_date = new Date(start_input.value)
        const end_date = new Date(end_input.value)

        x_range.start = start_date.valueOf()
        x_range.end = end_date.valueOf()
        x_range.change.emit()
        """
        )

    # Create the layout for the Timeline plot
    plots = layout([
        [timeline_zoom],
        [
            timeline_select,
            [
                start_date_input,
                end_date_input,
                update_time_button]
        ],
    ])

    # Store components
    script, div = components(plots)

    return script, div
