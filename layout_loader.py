# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayoutLoader
                                 A QGIS plugin
 This plugin builds layouts for your map from a number of pre-designed layouts.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-11-17
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Klas Karlsson
        email                : klaskarlsson@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .layout_loader_dialog import LayoutLoaderDialog
import os.path
# Import the code for the project
from qgis.core import QgsProject, QgsPrintLayout, QgsReadWriteContext
from PyQt5.QtXml import QDomDocument
from qgis.utils import iface
from os.path import dirname


class LayoutLoader:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LayoutLoader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LayoutLoaderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LayoutLoader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LayoutLoader')
        self.toolbar.setObjectName(u'LayoutLoader')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LayoutLoader', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/layout_loader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layout Loader'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&LayoutLoader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
       
    # Function by mgrant on stack overflow
    def recursive_overwrite(ignore=None):
    	  src = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'python')
    	  dest = dirname(dirname(os.path.dirname(os.path.realpath(__file__))))
    	  if os.path.isdir(src):
           if not os.path.isdir(dest):
              os.makedirs(dest)
    	  files = os.listdir(src)
    	  if ignore is not None:
           ignored = ignore(src, files)
    	  else:
           ignored = set()
    	  for f in files:
           if f not in ignored:
              recursive_overwrite(os.path.join(src, f), os.path.join(dest, f), ignore)
    	  else:
           shutil.copyfile(src, dest)
    
    def popCategories(self):
    	  """Add content to UI dialogue Category from files and folders in templates folder"""
    	  plugin_path = os.path.dirname(os.path.realpath(__file__))
    	  #Add categories
    	  self.dlg.cmbCategory.clear()
    	  category_path = os.path.join(plugin_path, 'templates')
    	  categories = [f.name for f in os.scandir(category_path) if f.is_dir() ]
    	  categories.sort()
    	  for category in categories:
    	     self.dlg.cmbCategory.addItem(category)
    	  self.dlg.cmbCategory.currentIndexChanged.connect(self.popTemplates)
    
    def popTemplates(self, i):
    	  """Add content to UI dialogue Templates from files in subfolder to category folder"""
    	  plugin_path = os.path.dirname(os.path.realpath(__file__))
    	  templates_path = os.path.join(plugin_path, 'templates',self.dlg.cmbCategory.currentText())
    	  #Add Templates
    	  self.dlg.cmbTemplate.clear()
    	  templates = [f.name for f in os.scandir(templates_path) if f.is_file() ]
    	  templates.sort()
    	  for template in templates:
    	  	  self.dlg.cmbTemplate.addItem(os.path.splitext(template)[0])
    	  
    def makeLayout(self):
    	  """
        This script creates a QGIS Layout based on a template, and it changes it based on some variables, and the canvas.

        Created by
        Klas Karlsson (@klaskarlsson) 2018
        """

        # Source file and customisation variables
    	  layout_name = self.dlg.txtLayoutName.text()
    	  template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates',self.dlg.cmbCategory.currentText(),self.dlg.cmbTemplate.currentText()+'.qpt')
    	  map_title = self.dlg.txtTitle.text()


        # Get the layout manager
    	  manager = QgsProject.instance().layoutManager()

        # Create the layout
    	  layout = QgsPrintLayout(QgsProject.instance())

        # Open and add the template to the layout
    	  template_file = open(template_path)
    	  template_content = template_file.read()
    	  template_file.close()
    	  document = QDomDocument()
    	  document.setContent(template_content)
    	  context = QgsReadWriteContext()
    	  layout.loadFromTemplate(document, context)

        # Change the layout
    	  layout.setName(layout_name)
    	  canvas = iface.mapCanvas()
    	  map_item = layout.itemById('main')
    	  map_item.zoomToExtent(canvas.extent())
    	  for item in layout.items():
           try:
              if item.id()=='title':
                 item.setText(map_title)
           except:
              pass

        # Add the layout to the layout manager
    	  manager.addLayout(layout)

        # Open the layout in the designer
    	  iface.openLayoutDesigner(layout)    

    def run(self):
        """Run method that performs all the real work"""
        #self.recursive_overwrite()
        self.popCategories()
        self.popTemplates(0)
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.makeLayout()
