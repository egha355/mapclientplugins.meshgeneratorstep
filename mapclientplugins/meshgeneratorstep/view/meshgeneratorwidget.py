'''
Created on Aug 29, 2017

@author: Richard Christie
'''
from PySide import QtGui, QtCore
from functools import partial

from mapclientplugins.meshgeneratorstep.view.ui_meshgeneratorwidget import Ui_MeshGeneratorWidget

class MeshGeneratorWidget(QtGui.QWidget):
    '''
    classdocs
    '''

    def __init__(self, model, parent=None):
        '''
        Constructor
        '''
        super(MeshGeneratorWidget, self).__init__(parent)
        self._ui = Ui_MeshGeneratorWidget()
        self._ui.setupUi(self)
        self._model = model
        self._ui.sceneviewer_widget.setContext(model.getContext())
        self._ui.sceneviewer_widget.graphicsInitialized.connect(self._graphicsInitialized)
        self._model.registerSceneChangeCallback(self._sceneChanged)
        self._doneCallback = None
        self._refreshOptions()
        self._makeConnections()

    def _graphicsInitialized(self):
        '''
        Callback for when SceneviewerWidget is initialised
        Set custom scene from model
        '''
        sceneviewer = self._ui.sceneviewer_widget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getScene()
            sceneviewer.setScene(scene)
            #self._ui.sceneviewer_widget.setSelectModeAll()
            sceneviewer.setLookatParametersNonSkew([2.0, -2.0, 1.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
            self._viewAll()

    def _sceneChanged(self):
        sceneviewer = self._ui.sceneviewer_widget.getSceneviewer()
        if sceneviewer is not None:
            scene = self._model.getScene()
            sceneviewer.setScene(scene)

    def _makeConnections(self):
        self._ui.done_button.clicked.connect(self._doneButtonClicked)
        self._ui.viewAll_button.clicked.connect(self._viewAll)
        meshTypeNames = self._model.getAllMeshTypeNames()
        index = 0;
        for meshTypeName in meshTypeNames:
            self._ui.meshType_comboBox.addItem(meshTypeName)
            if meshTypeName == self._model.getMeshTypeName():
                self._ui.meshType_comboBox.setCurrentIndex(index)
            index = index + 1
        self._ui.meshType_comboBox.currentIndexChanged.connect(self._meshTypeChanged)
        self._ui.deleteElementsRanges_lineEdit.returnPressed.connect(self._deleteElementRangesLineEditChanged)
        self._ui.deleteElementsRanges_lineEdit.editingFinished.connect(self._deleteElementRangesLineEditChanged)

    def getModel(self):
        return self._model

    def registerDoneExecution(self, doneCallback):
        self._doneCallback = doneCallback

    def _doneButtonClicked(self):
        self._model.done()
        self._model = None
        self._doneCallback()

    def _meshTypeChanged(self, index):
        meshTypeName = self._ui.meshType_comboBox.itemText(index)
        self._model.setMeshTypeByName(meshTypeName)
        self._refreshMeshTypeOptions()

    def _meshTypeOptionCheckBoxClicked(self, checkBox):
        self._model.setMeshTypeOption(checkBox.objectName(), checkBox.isChecked())

    def _meshTypeOptionLineEditChanged(self, lineEdit):
        self._model.setMeshTypeOption(lineEdit.objectName(), lineEdit.text())
        finalValue = self._model.getMeshTypeOption(lineEdit.objectName())
        lineEdit.setText(str(finalValue))

    def _refreshMeshTypeOptions(self):
        layout = self._ui.meshTypeOptions_frame.layout()
        # remove all current mesh type widgets
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
              child.widget().deleteLater()
        optionNames = self._model.getMeshTypeOrderedOptionNames()
        for key in optionNames:
            value = self._model.getMeshTypeOption(key)
            # print('key ', key, ' value ', value)
            if type(value) is bool:
                checkBox = QtGui.QCheckBox(self._ui.meshTypeOptions_frame)
                checkBox.setObjectName(key)
                checkBox.setText(key)
                checkBox.setChecked(value)
                callback = partial(self._meshTypeOptionCheckBoxClicked, checkBox)
                checkBox.clicked.connect(callback)
                layout.addWidget(checkBox)
            else:
                label = QtGui.QLabel(self._ui.meshTypeOptions_frame)
                label.setObjectName(key)
                label.setText(key)
                layout.addWidget(label)
                lineEdit = QtGui.QLineEdit(self._ui.meshTypeOptions_frame)
                lineEdit.setObjectName(key)
                lineEdit.setText(str(value))
                callback = partial(self._meshTypeOptionLineEditChanged, lineEdit)
                lineEdit.returnPressed.connect(callback)
                lineEdit.editingFinished.connect(callback)
                layout.addWidget(lineEdit)

    def _refreshOptions(self):
        self._ui.deleteElementsRanges_lineEdit.setText(self._model.getDeleteElementsRangesText())
        self._refreshMeshTypeOptions()

    def _deleteElementRangesLineEditChanged(self):
        self._model.setDeleteElementsRangesText(self._ui.deleteElementsRanges_lineEdit.text())
        self._ui.deleteElementsRanges_lineEdit.setText(self._model.getDeleteElementsRangesText())

    def _viewAll(self):
        '''
        Ask sceneviewer to show all of scene.
        '''
        if self._ui.sceneviewer_widget.getSceneviewer() is not None:
            self._ui.sceneviewer_widget.viewAll()