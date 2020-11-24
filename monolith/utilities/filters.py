import dateutil.parser


def do_datetime(dt, format=None):
    """Jinja template filter to format a string into datetime object."""
    if dt is None:
    # By default, render an empty string.
        return ''

    dt = dateutil.parser.parse(dt)
    if format is None:
    # No format is given in the template call.
    # Use a default format.
        formatted = dt.strftime("%a %d %b %Y, %H:%M")
    else:
        formatted = dt.strftime(format)
    return formatted

def do_parse_datetime(dt):
    """ Jinja template filter to parse a datetime string """
    return dateutil.parser.parse(dt)

def init_app(app):
    """Initialize a Flask application with custom filters."""
    app.jinja_env.filters['datetime'] = do_datetime
    app.jinja_env.filters['parse_datetime'] = do_parse_datetime