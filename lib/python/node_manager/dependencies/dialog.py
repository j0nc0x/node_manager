#!/usr/bin/env python

"""Houdini dialog utility functions."""

import logging

import hou


logger = logging.getLogger(__name__)


def display_message(
    text,
    buttons=("OK",),
    severity=hou.severityType.Message,
    default_choice=0,
    close_choice=-1,
    help=None,
    title=None,
    details=None,
    details_label=None,
    details_expanded=False,
):
    """Display a Houdini message UI element if we are in GUI mode.

    Also output to the logger, with the logging type specified by the severity.

    Args:
        text(str): The message to display.
        buttons(tuple): A sequence of strings containing the names of the
            buttons. By default the message window contains a single OK button.
        severity(hou.severityType): A hou.severityType value that determines
            which icon to display on the dialog. Note that using
            hou.severityType.Fatal will exit Houdini after the user closes the
            dialog.
        default_choice(int): The index of the button that is selected if the
            user presses enter.
        close_choice(int): The index of the button that is selected if the user
            presses Escape or closes the dialog.
        help(str): Additional help information to display below the main
            message.
        title(str): The window's title. If None, the title is "Houdini".
        details(str): A string containing extra messages that is not visible
            unless the user clicks "Show Details".
        details_label(str): A string containing the label for the
            expand/collapse button that controls whether or not the detail text
            is visible. If details_expanded is set to true this parameter has
            no effect.
        details_expanded(bool): A boolean, if true then the text area where the
            detail messages appear is always shown and cannot be collapsed. If
            false, the detail message area is initially folded when the message
            box is popped up and the user can expand to read the details.

    Returns:
        result(int): The index of the button the user pressed.
    """
    # Always log the message a line at a time
    text_split = text.split("\n")
    for line in text_split:
        if line == "":
            continue

        if severity == hou.severityType.Error or severity == hou.severityType.Fatal:
            logger.error(line)
        elif severity == hou.severityType.Warning:
            logger.warning(line)
        else:
            logger.info(line)

    result = None

    # Display the Houdini UI message if the dialog is available
    if hou.isUIAvailable():
        result = hou.ui.displayMessage(
            text,
            buttons=buttons,
            severity=severity,
            default_choice=default_choice,
            close_choice=close_choice,
            help=help,
            title=title,
            details=details,
            details_label=details_label,
            details_expanded=details_expanded,
        )
    return result
