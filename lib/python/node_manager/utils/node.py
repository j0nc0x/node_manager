#!/usr/bin/env python

"""NodeManager Node related utils."""

import logging

import hou
import nodegraphutils


logger = logging.getLogger(__name__)


def node_comment(current_node, edit=False):
    """Set the comment on a node.

    Args:
        current_node(hou.Node): The node to set the comment on.
        edit(bool): Whether the node is editable or not.
    """
    state = "Published"
    if edit:
        state = "Editable"
    current_node.setComment("Node Manager: {state}".format(state=state))
    current_node.setGenericFlag(hou.nodeFlag.DisplayComment, True)


def remove_node_graphic():
    """
    """
    print("remove here")

def node_graphic(current_node, edit=False):
    """Set the node graphic.

    
    """
    width_ratio = 0.8
    image_path = "/Users/jcox/Documents/test.png"

    #set up background image plane
    editor = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor)
    image = hou.NetworkImage()
    image.setPath(image_path)

    image_resolution = hou.imageResolution(image_path)
    ratio = 1.0 * image_resolution[1] / image_resolution[0]
    logger.debug("Current node size {size}".format(size=current_node.size()))
    # rect = hou.BoundingRect(0, -current_node.size()[1]*1.1, width_ratio, -width_ratio*ratio - current_node.size()[1]*1.1)
    # x1 = width_ratio
    # y1 = -width_ratio*ratio - current_node.size()[1]*1.1
    # x2 = current_node.size()[0] * 2.1
    # y2 = 0
    x1 = current_node.size()[0] * 1
    y1 = 0
    x2 = current_node.size()[0] * 1 + width_ratio
    y2 = width_ratio * ratio
    logger.debug("Using size {x1}, {y1}, {x2}, {y2}".format(x1=x1, y1=y1, x2=x2, y2=y2))
    rect = hou.BoundingRect(x1, y1, x2, y2)
    logger.debug("Using bounding rectangle {rect}".format(rect=rect))
    image.setRelativeToPath(current_node.path())
    image.setRect(rect)

    #following is adding a spare parm with image path to be able to know which node corresponds to which background image
    #could have used a user attribute or relativeToPath() and smarter logic but it works and it helps me visualize filepath

    # hou_parm_template_group = hou.ParmTemplateGroup()
    # hou_parm_template = hou.LabelParmTemplate("houdinipath", "Label", column_labels=(['\\'+houdinipath]))
    # hou_parm_template.hideLabel(True)
    # hou_parm_template_group.append(hou_parm_template)
    # nullNode.setParmTemplateGroup(hou_parm_template_group)


    #attach a function that deletes the background image plane if the corresponding node is deleted (faster than doing it by hand)
    current_node.addEventCallback((hou.nodeEventType.BeingDeleted,), remove_node_graphic)

    # #attach a function to change visibility or opacity if corresponding node flags are changed
    # nullNode.addEventCallback((hou.nodeEventType.FlagChanged,), changeBackgroundImageBrightness)

    #add image to network background
    backgroundImagesDic = editor.backgroundImages()
    backgroundImagesDic = backgroundImagesDic + (image,)
    editor.setBackgroundImages(backgroundImagesDic)
    nodegraphutils.saveBackgroundImages(editor.pwd(), backgroundImagesDic)
