import bokeh.plotting as bp
import bokeh as bk


bp.output_notebook()

def scatter(X, names, labels, sizes=1, title=None, colormap=bk.palettes.Spectral11):
    source = bp.ColumnDataSource(
        data=dict(
            x=X.T[0],
            y=X.T[1],
            color=[colormap[c%11] for c in labels],
            name=names,
            label=labels,
            radius=0.5*sizes
        )
    )
    TOOLS="wheel_zoom,pan,box_zoom,reset,hover"
    p = bp.figure(title=title, tools=TOOLS, plot_width=1000, plot_height=1000)

    p.scatter('x', 'y', source=source, fill_color='color', fill_alpha=0.7, radius='radius', line_alpha=0.1)

    hover = p.select(dict(type=bk.models.HoverTool))
    hover.tooltips = "<p style='font-size: 12px'>@name, @label</p>"

    bp.show(p)
