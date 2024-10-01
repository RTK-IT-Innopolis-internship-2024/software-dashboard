from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontMetrics
from pyqt6_multiselect_combobox import MultiSelectComboBox


class CustomMultiSelectComboBox(MultiSelectComboBox):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def showPopup(self) -> None:  # noqa: N802
        self.setPopupMinimumWidthForItems()
        super().showPopup()

    def setPopupMinimumWidthForItems(self) -> None:  # noqa: N802
        # we like the popup to always show the full contents
        # under Linux/GNOME popups always do this
        # but under Windows they get truncated/ellipsised
        # here we calculate the maximum width among the items
        # and set QComboBox.view() to accomodate this
        # which makes items show full width under Windows
        view = self.view()
        fm = self.fontMetrics()
        max_width = max([fm.boundingRect(self.itemText(i)).width() for i in range(self.count())])
        if max_width:
            view.setMinimumWidth(max_width + 40)

    def checked_mask(self) -> list[bool]:
        return [self.model().item(i).checkState() == Qt.CheckState.Checked for i in range(1, self.model().rowCount())]

    def updateText(self) -> None:  # noqa: N802
        """
        Update the displayed text based on selected items.
        """
        display_type = self.getDisplayType()
        delimiter = self.getDisplayDelimiter()
        texts = [
            self.typeSelection(i, display_type) for i in range(1, self.model().rowCount()) if self.model().item(i).checkState() == Qt.CheckState.Checked
        ]

        text = delimiter.join(texts) if texts else self.placeholderText if hasattr(self, "placeholderText") else ""

        if all(self.checked_mask()):
            text = "(все)"

        metrics = QFontMetrics(self.lineEdit().font())
        elided_text = metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elided_text)
