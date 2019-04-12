class Ruler(AxesWidget):
    """
    A ruler to measure distances and angles on an axes instance.
    For the ruler to remain responsive you must keep a reference to it.
     Parameters
    ----------
    *ax*  : the  :class:`matplotlib.axes.Axes` instance
    *active* : bool, default is True
        Whether the ruler is active or not.
    *length_unit*  : string, a unit identifier to use in displayed text
        i.e. ('ft', or 'm')
    *angle_unit*  : "degrees" or "radians"
        The type of angle unit ('degrees' or 'radians')
    *print_text*  : bool, default is False
        Whether the length measure string is printed to the console
    *useblit* : bool, default is False
        If True, use the backend-dependent blitting features for faster
        canvas updates.
    *lineprops* : dict, default is None
      Dictionary of :class:`matplotlib.lines.Line2D` properties
    *markerprops* : dict, default is None
      Dictionary of :class:`matplotlib.markers.MarkerStyle` properties
    *textprops*: dict, default is None
        Dictionary of :class:`matplotlib.text.Text` properties. To reposition
        the textbox you can overide the defaults which position the box in the
        top left corner of the axes.
    Usage:
    ----------
    1. Hold left click drag and release to draw the ruler in the axes.
      - Hold shift while dragging to lock the ruler to the horizontal axis.
      - Hold control while drawing to lock the ruler to the vertical axis.
    2. Right click one of the markers to move the ruler.
    The keyboard can be used to activate and deactivate the ruler and toggle
    visibility of the line and text:
    'm' : Toggles the ruler on and off.
    'ctl+m' : Toggles the visibility of the ruler and text.
    Example
    ----------
    >>> xCoord = np.arange(0, 5, 1)
    >>> yCoord = [0, 1, -3, 5, -3]
    >>> fig = plt.figure()
    >>> ax = fig.add_subplot(111)
    >>> markerprops = dict(marker='o', markersize=5, markeredgecolor='red')
    >>> lineprops = dict(color='red', linewidth=2)
    >>> ax.grid(True)
    >>> ax.plot(xCoord, yCoord)
    >>> ruler = Ruler(ax=ax,
                  useblit=True,
                  markerprops=markerprops,
                  lineprops=lineprops)
    >>> plt.show()
    """

    def __init__(self,
                 ax,
                 active=True,
                 length_unit=None,
                 angle_unit='degree',
                 print_text=False,
                 useblit=False,
                 lineprops=None,
                 textprops=None,
                 markerprops=None):
        """
        Add a ruler to *ax*. If ``ruler_active=True``, the ruler will be
        activated when the plot is first created. If ``ruler_unit`` is set the
        string will be appended to the length text annotations.
        """
        AxesWidget.__init__(self, ax)

        self.connect_events()

        self.ax = ax
        self.fig = ax.figure
        self.canvas = ax.figure.canvas
        self.print_text = print_text
        self.visible = True
        self.active = active
        self.length_unit = length_unit
        self.angle_unit = angle_unit
        self.useblit = useblit and self.canvas.supports_blit

        self.mouse1_pressed = False
        self.mouse3_pressed = False
        self.shift_pressed = False
        self.control_pressed = False
        self.end_a_lock = False
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.line_start_coords = None
        self.line_end_coords = None
        self.ruler_marker = None
        self.background = None
        self.ruler_moving = False
        self.end_a_lock = False
        self.end_b_lock = False
        self.end_c_lock = False
        self.old_marker_a_coords = None
        self.old_marker_c_coords = None
        self.old_mid_coords = None

        if lineprops is None:
            lineprops = {}

        bbox = dict(facecolor='white',
                    alpha=0.5,
                    boxstyle='round',
                    edgecolor='0.75')

        default_textprops = dict(xy=(0, 1),
                                 xytext=(10, -10),
                                 xycoords='axes fraction',
                                 textcoords='offset points',
                                 ha='left',
                                 va='center',
                                 bbox=bbox)

        x0 = self.ax.get_xlim()[0]
        y0 = self.ax.get_ylim()[0]

        self.ruler, = self.ax.plot([x0, x0], [y0, y0], label='ruler',
                                   **lineprops)

        default_markerprops = dict(marker='s',
                                   markersize=3,
                                   markerfacecolor='white',
                                   markeredgecolor='black',
                                   markeredgewidth=0.5,
                                   picker=5,
                                   visible=False)

        # If marker or text  props are given as an argument combine with the
        # default marker props. Don't really want to override the entire props
        # if a user only gives one value.

        if markerprops is not None:
            used_markerprops = default_markerprops.copy()
            used_markerprops.update(markerprops)
        else:
            used_markerprops = default_markerprops

        if textprops is not None:
            used_textprops = default_textprops.copy()
            used_textprops.update(markerprops)
        else:
            used_textprops = default_textprops

        self.axes_text = self.ax.annotate(s='', **used_textprops)
        self.ax.add_artist(self.axes_text)

        self.marker_a, = self.ax.plot((x0, y0), **used_markerprops)
        self.marker_b, = self.ax.plot((x0, y0), **used_markerprops)
        self.marker_c, = self.ax.plot((x0, y0), **used_markerprops)

        self.artists = [self.axes_text,
                        self.ruler,
                        self.marker_a,
                        self.marker_b,
                        self.marker_c]

    def connect_events(self):
        """
        Connect all events to the various callbacks
        """
        self.connect_event('button_press_event', self.on_press)
        self.connect_event('button_release_event', self.on_release)
        self.connect_event('motion_notify_event', self.on_move)
        self.connect_event('key_press_event', self.on_key_press)
        self.connect_event('key_release_event', self.on_key_release)

    def ignore(self, event):
        """
        Ignore events if the cursor is out of the axes or the widget is locked
        """
        if not self.canvas.widgetlock.available(self):
            return True
        if event.inaxes != self.ax.axes:
            return True
        if self.active is False:
            return True

    def on_key_press(self, event):
        """
        Handle key press events.
        If shift is pressed the ruler will be constrained to horizontal axis
        If control is pressed the ruler will be constrained to vertical axis
        If m is pressed the ruler will be toggled on and off
        If ctrl+m is pressed the visibility of the ruler will be toggled
        """

        if event.key == 'shift':
            self.shift_pressed = True

        if event.key == 'control':
            self.control_pressed = True

        if event.key == 'm':
            self.toggle_ruler()

        if event.key == 'ctrl+m':
            self.toggle_ruler_visibility()

    def on_key_release(self, event):
        """
        Handle key release event, flip the flags to false.
        """
        if event.key == 'shift':
            self.shift_pressed = False

        if event.key == 'control':
            self.control_pressed = False

    def toggle_ruler(self):
        """
        Called when the 'm' key is pressed. If ruler is on turn it off, and
        vise versa
        """
        if self.active is True:
            self.active = False

        elif self.active is False:
            self.active = True

    def toggle_ruler_visibility(self):
        """
        Called when the 'ctl+m' key is pressed. If ruler is visible turn it off
        , and vise versa
        """
        if self.visible is True:
            for artist in self.artists:
                artist.set_visible(False)
            self.active = False
            self.visible = False

        elif self.visible is False:
            for artist in self.artists:
                artist.set_visible(True)
            self.visible = True

        self.fig.canvas.draw_idle()

    def on_press(self, event):
        """
        On mouse button press check which button has been pressed and handle
        """
        if self.ignore(event):
            return
        if event.button == 1 and self.mouse3_pressed is False:
            self.handle_button1_press(event)
        elif event.button == 3:
            self.handle_button3_press(event)

    def handle_button1_press(self, event):
        """
        On button 1 press start drawing the ruler line from the initial
        press position
        """

        self.mouse1_pressed = True

        self.x0 = event.xdata
        self.y0 = event.ydata

        self.marker_a.set_data((event.xdata, event.ydata))
        self.marker_a.set_visible(True)

        if self.useblit:
            self.marker_a.set_data(self.x0, self.y0)
            for artist in self.artists:
                artist.set_animated(True)
            self.fig.canvas.draw()
            self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)

    def handle_button3_press(self, event):
        """
        If button 3 is pressed (right click) check if cursor is at one of the
        ruler markers and the move the ruler accordingly.
        """
        contains_a, attrd = self.marker_a.contains(event)
        contains_b, attrd = self.marker_b.contains(event)
        contains_c, attrd = self.marker_c.contains(event)

        if contains_a and contains_b and contains_c is False:
            return

        self.end_a_lock = True if contains_a is True else False
        self.end_b_lock = True if contains_b is True else False
        self.end_c_lock = True if contains_c is True else False

        line_coords = self.ruler.get_path().vertices
        self.x0 = line_coords[0][0]
        self.y0 = line_coords[0][1]
        self.x1 = line_coords[1][0]
        self.y1 = line_coords[1][1]

        self.old_marker_a_coords = self.marker_a.get_path().vertices
        self.old_marker_c_coords = self.marker_c.get_path().vertices
        self.old_mid_coords = self.midline_coords

    def on_move(self, event):
        """
        On motion draw the ruler if button 1 is pressed. If one of the markers
        is locked indicating move the ruler according to the locked marker
        """

        if event.inaxes != self.ax.axes:
            return

        if self.end_a_lock or self.end_b_lock or self.end_c_lock is True:
            self.move_ruler(event)

        if self.mouse1_pressed is True:
            self.draw_ruler(event)

    def move_ruler(self, event):
        """
        If one of the markers is locked move the ruler according the selected
        marker.
        """

        # This flag is used to prevent the ruler from clipping when a marker is
        # first selected
        if self.ruler_moving is False:
            if self.useblit:
                for artist in self.artists:
                    artist.set_animated(True)
                self.fig.canvas.draw()
                self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
                self.ruler_moving = True

        if self.end_a_lock is True:
            # If marker a is locked only move end a.
            pos_a = event.xdata, self.x1
            pos_b = event.ydata, self.y1
            self.marker_a.set_data(event.xdata, event.ydata)
            self.ruler.set_data(pos_a, pos_b)
            self.set_midline_marker()

        if self.end_c_lock is True:
            # If marker a is locked only move end c.
            pos_a = self.x0, event.xdata
            pos_b = self.y0, event.ydata
            self.marker_c.set_data(event.xdata, event.ydata)
            self.ruler.set_data(pos_a, pos_b)
            self.set_midline_marker()

        if self.end_b_lock is True:
            # If marker b is locked shift the whole ruler.
            b_dx = event.xdata - self.old_mid_coords[0]
            b_dy = event.ydata - self.old_mid_coords[1]
            pos_a = self.x0 + b_dx, self.x1 + b_dx
            pos_b = self.y0 + b_dy, self.y1 + b_dy

            marker_a_coords = self.old_marker_a_coords[0][0] + b_dx, \
                              self.old_marker_a_coords[0][1] + b_dy
            marker_c_coords = self.old_marker_c_coords[0][0] + b_dx, \
                              self.old_marker_c_coords[0][1] + b_dy

            self.ruler.set_data(pos_a, pos_b)
            self.marker_a.set_data(marker_a_coords)
            self.marker_b.set_data(event.xdata, event.ydata)
            self.marker_c.set_data(marker_c_coords)

        self.update_text()
        self._update_artists()

    def set_midline_marker(self):
        self.marker_b.set_visible(True)
        self.marker_b.set_data(self.midline_coords)

    @property
    def midline_coords(self):
        pos0, pos1 = self.line_coords
        mid_line_coords = (pos0[0] + pos1[0]) / 2, (pos0[1] + pos1[1]) / 2

        return mid_line_coords

    def draw_ruler(self, event):
        """
        If the left mouse button is pressed and held draw the ruler as the
        mouse is dragged
        """

        self.x1 = event.xdata
        self.y1 = event.ydata

        # If shift is pressed ruler is constrained to horizontal axis
        if self.shift_pressed is True:
            pos_a = self.x0, self.x1
            pos_b = self.y0, self.y0
        # If control is pressed ruler is constrained to vertical axis
        elif self.control_pressed is True:
            pos_a = self.x0, self.x0
            pos_b = self.y0, self.y1
        # Else the ruler follow the mouse cursor
        else:
            pos_a = self.x0, self.x1
            pos_b = self.y0, self.y1

        self.ruler.set_data([pos_a], [pos_b])
        x1 = self.ruler.get_path().vertices[1][0]
        y1 = self.ruler.get_path().vertices[1][1]

        self.marker_c.set_visible(True)
        self.marker_c.set_data(x1, y1)

        self.set_midline_marker()
        self.update_text()
        self._update_artists()

    @property
    def line_coords(self):
        line_coords = self.ruler.get_path().vertices
        x0 = line_coords[0][0]
        y0 = line_coords[0][1]
        x1 = line_coords[1][0]
        y1 = line_coords[1][1]

        pos_a = x0, y0
        pos_b = x1, y1

        return pos_a, pos_b

    def _update_artists(self):
        if self.useblit:
            if self.background is not None:
                self.canvas.restore_region(self.background)

            for artist in self.artists:
                self.fig.draw_artist(artist)

            self.fig.canvas.blit(self.fig.bbox)
        else:
            self.canvas.draw_idle()

    def update_text(self):
        if self.length_unit is not None:

            detail_string = 'L: {:0.3f} {}; dx: {:0.3f} {}; dy: {:0.3f} {}; ' \
                            'angle: {:0.3f} deg'.format(self.ruler_length,
                                                        self.length_unit,
                                                        self.ruler_dx,
                                                        self.length_unit,
                                                        self.ruler_dy,
                                                        self.length_unit,
                                                        self.ruler_angle)
        else:
            detail_string = 'L: {:0.3f}; dx: {:0.3f}; dy: {:0.3f}; ' \
                            'ang: {:0.3f} deg'.format(self.ruler_length,
                                                      self.ruler_dx,
                                                      self.ruler_dy,
                                                      self.ruler_angle)

        self.axes_text.set_text(detail_string)
        if self.print_text is True:
            print(detail_string)

    def on_release(self, event):
        self.mouse1_pressed = False
        self.mouse3_pressed = False
        self.ruler_moving = False
        self.end_a_lock = False
        self.end_b_lock = False
        self.end_c_lock = False

        if event.inaxes != self.ax.axes:
            return

        if self.useblit:
            for artist in self.artists:
                artist.set_animated(False)

        self.canvas.draw_idle()

    @property
    def ruler_length(self):
        pos0, pos1 = self.line_coords

        return np.sqrt((pos1[0] - pos0[0]) ** 2 + (pos0[1] - pos1[1]) ** 2)

    @property
    def ruler_dx(self):
        pos0, pos1 = self.line_coords

        return np.abs(pos1[0] - pos0[0])

    @property
    def ruler_dy(self):
        pos0, pos1 = self.line_coords

        return np.abs(pos1[1] - pos0[1])

    @property
    def ruler_angle(self):
        pos0, pos1 = self.line_coords

        dx = pos1[0] - pos0[0]
        dy = pos1[1] - pos0[1]

        angle = np.arctan2(dy, dx)

        if self.angle_unit == 'degree':
            return angle * 180 / np.pi
        else:
            return angle
