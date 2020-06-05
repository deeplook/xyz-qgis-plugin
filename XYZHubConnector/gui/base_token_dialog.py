# -*- coding: utf-8 -*-
###############################################################################
#
# Copyright (c) 2019 HERE Europe B.V.
#
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
#
###############################################################################

from qgis.PyQt.QtGui import QStandardItem
from qgis.PyQt.QtWidgets import QDialog

from ..xyz_qgis.models.token_model import EditableGroupTokenInfoModel
from . import get_ui_class
from .token_info_dialog import EditTokenInfoDialog, NewTokenInfoDialog
from .util_dialog import ConfirmDialog

TokenUI = get_ui_class('token_dialog.ui')

class BaseTokenDialog(QDialog, TokenUI):
    title = "Token Manager"
    message = ""
    token_info_keys = ["name", "token"]
    NewInfoDialog = NewTokenInfoDialog
    EditInfoDialog = EditTokenInfoDialog
    
    def __init__(self, parent=None):
        """init window"""
        QDialog.__init__(self, parent)
        TokenUI.setupUi(self, self)
        self.setWindowTitle(self.title)
        if self.message:
            self.label_msg.setText(self.message)
            self.label_msg.setVisible(True)

        self.is_used_token_changed = False
        self._active_idx = 0
        self._active_server_idx = 0

    def set_server(self, server):
        self.token_model.set_server(server)
        self.token_model.reset_used_token_idx()

    def config(self, token_model: EditableGroupTokenInfoModel):
        self._config( token_model)
        self.tableView.setSelectionMode(self.tableView.SingleSelection)
        self.tableView.setSelectionBehavior(self.tableView.SelectRows)
        self.tableView.setEditTriggers(self.tableView.NoEditTriggers)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        # dont use pressed, activated
        self.tableView.selectionModel().currentChanged.connect(self.ui_enable_btn)

        self.btn_add.clicked.connect( self.ui_add_token)
        self.btn_edit.clicked.connect( self.ui_edit_token)
        self.btn_delete.clicked.connect( self.ui_delete_token)
        self.btn_up.clicked.connect( self.ui_move_token_up)
        self.btn_down.clicked.connect( self.ui_move_token_down)

    def _config(self, token_model: EditableGroupTokenInfoModel):
        self.token_model = token_model
        self.tableView.setModel( token_model)
        self.accepted.connect( token_model.cb_write_token)
        self.rejected.connect( token_model.cb_refresh_token)
        
    def exec_(self):
        # self.tableView.resizeColumnsToContents()
        # self.tableView.clearFocus()
        self.tableView.selectRow(self.get_active_idx())
        self.ui_enable_btn()
        self.is_used_token_changed = False
        ret = super().exec_()
        if ret == self.Accepted:
            self.is_used_token_changed = True
            idx = self.tableView.currentIndex().row()
            if idx >= 0: self.set_active_idx(idx)
        return ret
    def set_active_idx(self,idx):
        self._active_idx = idx
    def get_active_idx(self):
        return self._active_idx
    def set_active_server_idx(self, idx):
        self._active_server_idx = idx
    def get_active_server_idx(self):
        return self._active_server_idx
    def ui_enable_btn(self, *a):
        index = self.tableView.currentIndex()
        flag = index.isValid()
        for btn in [
            self.btn_edit,
            self.btn_delete,
            self.btn_up,
            self.btn_down,
        ]:
            btn.setEnabled(flag)

    def _get_current_token_info(self):
        row = self.tableView.currentIndex().row()
        return self.token_model.get_token_info(row)

    def _make_delete_message(self, token_info):
        token_msg = ", ".join("%s: %s"%it for it in token_info.items())
        return "Do you want to Delete token (%s)?"%token_msg
        
    def ui_add_token(self):
        dialog = self.NewInfoDialog(self)
        dialog.accepted.connect(lambda: self._add_token(
            dialog.get_info()
        ))
        dialog.exec_()
        self.tableView.selectRow(self.token_model.rowCount()-1)

    def ui_edit_token(self):
        dialog = self.EditInfoDialog(self)
        token_info = self._get_current_token_info()
        dialog.set_info(token_info)
        dialog.accepted.connect(lambda: self._edit_token(
            dialog.get_info()
        ))
        dialog.exec_()

    def ui_delete_token(self):
        row = self.tableView.currentIndex().row()
        token_info = self.token_model.get_token_info(row)
        dialog = ConfirmDialog(self._make_delete_message(token_info))
        ret = dialog.exec_()
        if ret != dialog.Ok: return

        self.token_model.takeRow(row)
        self.check_used_token_changed(row)

    def ui_move_token_up(self):
        row = self.tableView.currentIndex().row()
        it = self.token_model.takeRow(row)
        self.check_used_token_changed(row)

        row = max(row-1,0)
        self.token_model.insertRow(max(row,0), it)
        self.tableView.selectRow(row)
        self.check_used_token_changed(row)

    def ui_move_token_down(self):
        row = self.tableView.currentIndex().row()
        it = self.token_model.takeRow(row)
        self.check_used_token_changed(row)

        row = min(row+1, self.token_model.rowCount())
        self.token_model.insertRow(row, it)
        self.tableView.selectRow(row)
        self.check_used_token_changed(row)

    def _add_token(self, token_info: dict):
        self.token_model.appendRow([
            QStandardItem(token_info[k])
            for k in self.token_info_keys
        ])
    
    def _edit_token(self, token_info: dict):
        row = self.tableView.currentIndex().row()
        self.token_model.insertRow(row+1, [
            QStandardItem(token_info[k])
            for k in self.token_info_keys
        ])
        it = self.token_model.takeRow(row)
        self.check_used_token_changed(row)
        
    def check_used_token_changed(self, idx):
        flag = idx == self.token_model.get_used_token_idx()
        self.is_used_token_changed = self.is_used_token_changed or flag
