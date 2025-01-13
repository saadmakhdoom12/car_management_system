from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class ServiceTableWidget(QTableWidget):
    """Custom table widget for managing services"""

    service_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_table()

    def setup_table(self):
        headers = ["Description", "Parts Cost", "Labor Cost", "Total"]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.verticalHeader().setVisible(False)

    def add_service_row(self, service_data=None):
        row = self.rowCount()
        self.insertRow(row)

        if service_data:
            self.setItem(row, 0, QTableWidgetItem(service_data["description"]))
            self.setItem(
                row, 1, QTableWidgetItem(f"${service_data['parts_cost']:.2f}")
            )
            self.setItem(
                row, 2, QTableWidgetItem(f"${service_data['labor_cost']:.2f}")
            )
            self.setItem(
                row, 3, QTableWidgetItem(f"${service_data['total_cost']:.2f}")
            )

        self.service_changed.emit()

    def get_all_services(self):
        services = []
        for row in range(self.rowCount()):
            service = {
                "description": self.item(row, 0).text(),
                "parts_cost": float(self.item(row, 1).text().replace("$", "")),
                "labor_cost": float(self.item(row, 2).text().replace("$", "")),
                "total_cost": float(self.item(row, 3).text().replace("$", "")),
            }
            services.append(service)
        return services

    def clear_services(self):
        self.setRowCount(0)
        self.service_changed.emit()


class EstimateDetailsWidget(QWidget):
    """Widget for displaying estimate details"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Customer details section
        self.customer_label = QLabel("<b>Customer Details</b>")
        self.customer_info = QLabel()

        # Vehicle details section
        self.vehicle_label = QLabel("<b>Vehicle Details</b>")
        self.vehicle_info = QLabel()

        # Total section
        self.total_label = QLabel("<b>Total Amount:</b>")
        self.total_amount = QLabel("$0.00")
        self.total_amount.setStyleSheet("font-size: 16px; color: #2ecc71;")

        layout.addWidget(self.customer_label)
        layout.addWidget(self.customer_info)
        layout.addWidget(self.vehicle_label)
        layout.addWidget(self.vehicle_info)
        layout.addWidget(self.total_label)
        layout.addWidget(self.total_amount)
        layout.addStretch()

    def update_details(self, estimate_data):
        self.customer_info.setText(
            f"Name: {estimate_data['customer_name']}\n"
            f"Phone: {estimate_data['customer_phone']}\n"
            f"Email: {estimate_data['customer_email']}"
        )

        self.vehicle_info.setText(
            f"Make: {estimate_data['vehicle_make']}\n"
            f"Model: {estimate_data['vehicle_model']}\n"
            f"Year: {estimate_data['vehicle_year']}\n"
            f"VIN: {estimate_data['vehicle_vin']}"
        )

        self.total_amount.setText(f"${estimate_data['total_amount']:.2f}")


class StatusLabelWidget(QLabel):
    """Custom label for showing status messages"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("padding: 5px; border-radius: 3px;")

    def show_success(self, message):
        self.setText(message)
        self.setStyleSheet(
            "background-color: #2ecc71; color: white; "
            "padding: 5px; border-radius: 3px;"
        )

    def show_error(self, message):
        self.setText(message)
        self.setStyleSheet(
            "background-color: #e74c3c; color: white; "
            "padding: 5px; border-radius: 3px;"
        )

    def show_info(self, message):
        self.setText(message)
        self.setStyleSheet(
            "background-color: #3498db; color: white; "
            "padding: 5px; border-radius: 3px;"
        )


class SearchBoxWidget(QWidget):
    """Custom search box with clear button"""

    search_changed = pyqtSignal(str)

    def __init__(self, placeholder="Search...", parent=None):
        super().__init__(parent)
        self.setup_ui(placeholder)

    def setup_ui(self, placeholder):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.search_changed.emit)

        self.clear_button = QPushButton("×")
        self.clear_button.setFixedSize(20, 20)
        self.clear_button.clicked.connect(self.clear_search)

        layout.addWidget(self.search_input)
        layout.addWidget(self.clear_button)

    def clear_search(self):
        self.search_input.clear()

    def text(self):
        return self.search_input.text()


class QuantitySpinBox(QSpinBox):
    """Custom spin box for quantity input"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 9999)
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)


class MoneySpinBox(QDoubleSpinBox):
    """Custom spin box for monetary values"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999.99)
        self.setDecimals(2)
        self.setPrefix("$")
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)

