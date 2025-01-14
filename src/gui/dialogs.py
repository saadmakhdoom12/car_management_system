import logging
from datetime import datetime
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QSpinBox,
    QVBoxLayout,
    QTextEdit,
    QLabel,
)


class NewEstimateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.estimate_data = None
            self.setup_ui()
        except Exception as e:
            logging.error(f"Error initializing NewEstimateDialog: {str(e)}")
            raise

    def setup_ui(self):
        layout = QFormLayout()
        
        # Initialize form fields
        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_email = QLineEdit()
        self.vehicle_make = QLineEdit()
        self.vehicle_model = QLineEdit()
        self.vehicle_year = QSpinBox()
        self.vehicle_year.setRange(1900, QDate.currentDate().year())
        self.vehicle_vin = QLineEdit()
        
        # Initialize amount fields
        self.subtotal = QDoubleSpinBox()
        self.subtotal.setMaximum(999999.99)
        self.subtotal.setDecimals(2)
        self.subtotal.valueChanged.connect(self.calculate_totals)
        
        # Add fields to layout
        layout.addRow("Customer Name*:", self.customer_name)
        layout.addRow("Phone:", self.customer_phone)
        layout.addRow("Email:", self.customer_email)
        layout.addRow("Vehicle Make*:", self.vehicle_make)
        layout.addRow("Vehicle Model*:", self.vehicle_model)
        layout.addRow("Year:", self.vehicle_year)
        layout.addRow("VIN:", self.vehicle_vin)
        layout.addRow("Subtotal*:", self.subtotal)
        
        # Add buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
        
        self.setLayout(layout)

    def calculate_totals(self):
        subtotal = self.subtotal.value()
        self.nhil = subtotal * 0.025
        self.getfund = subtotal * 0.025
        self.covid_levy = subtotal * 0.01
        self.subtotal_with_levies = subtotal + self.nhil + self.getfund + self.covid_levy
        self.vat = self.subtotal_with_levies * 0.15
        self.total = self.subtotal_with_levies + self.vat

    def validate_and_accept(self):
        try:
            if not all([
                self.customer_name.text(),
                self.vehicle_make.text(),
                self.vehicle_model.text(),
                self.subtotal.value() > 0
            ]):
                QMessageBox.warning(self, "Validation Error", 
                    "Please fill all required fields and ensure subtotal is greater than 0")
                return

            self.calculate_totals()
            self.estimate_data = {
                'customer_name': self.customer_name.text(),
                'customer_phone': self.customer_phone.text(),
                'customer_email': self.customer_email.text(),
                'vehicle_make': self.vehicle_make.text(),
                'vehicle_model': self.vehicle_model.text(),
                'vehicle_year': self.vehicle_year.value(),
                'vehicle_vin': self.vehicle_vin.text(),
                'subtotal': self.subtotal.value(),
                'nhil': self.nhil,
                'getfund': self.getfund,
                'covid_levy': self.covid_levy,
                'vat': self.vat,
                'total_amount': self.total,
                'date': QDate.currentDate().toString("yyyy-MM-dd"),
                'status': 'Pending'
            }
            self.accept()
            
        except Exception as e:
            logging.error(f"Error in estimate validation: {str(e)}")
            QMessageBox.critical(self, "Error", str(e))


class ServiceEntryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Service")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        self.description = QLineEdit()
        self.parts_cost = QDoubleSpinBox()
        self.parts_cost.setMaximum(999999.99)
        self.labor_cost = QDoubleSpinBox()
        self.labor_cost.setMaximum(999999.99)
        
        layout.addRow("Description*:", self.description)
        layout.addRow("Parts Cost:", self.parts_cost)
        layout.addRow("Labor Cost:", self.labor_cost)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def validate_and_accept(self):
        if not self.description.text():
            QMessageBox.warning(
                self, "Validation Error", "Service description is required!"
            )
            return
        self.accept()

    def get_data(self):
        return {
            'description': self.description.text(),
            'parts_cost': self.parts_cost.value(),
            'labor_cost': self.labor_cost.value(),
            'total_cost': self.parts_cost.value() + self.labor_cost.value()
        }


class InventoryItemDialog(QDialog):
    def __init__(self, parent=None, item_data=None):
        super().__init__(parent)
        self.setWindowTitle("Inventory Item")
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        self.item_code = QLineEdit()
        self.description = QLineEdit()
        self.quantity = QSpinBox()
        self.quantity.setMaximum(9999)
        self.unit_price = QDoubleSpinBox()
        self.unit_price.setMaximum(999999.99)
        
        if self.item_data:
            self.item_code.setText(self.item_data.get('item_code', ''))
            self.description.setText(self.item_data.get('description', ''))
            self.quantity.setValue(self.item_data.get('quantity', 0))
            self.unit_price.setValue(self.item_data.get('unit_price', 0.0))
        
        layout.addRow("Item Code*:", self.item_code)
        layout.addRow("Description*:", self.description)
        layout.addRow("Quantity:", self.quantity)
        layout.addRow("Unit Price:", self.unit_price)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def validate_and_accept(self):
        if not self.item_code.text() or not self.description.text():
            QMessageBox.warning(
                self, "Validation Error", 
                "Item code and description are required!"
            )
            return
        self.accept()

    def get_data(self):
        return {
            'item_code': self.item_code.text(),
            'description': self.description.text(),
            'quantity': self.quantity.value(),
            'unit_price': self.unit_price.value()
        }


class ReportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Report")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        self.report_type = QComboBox()
        self.report_type.addItems(["Estimates", "Inventory"])
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
       
        layout.addRow("Report Type:", self.report_type)
        layout.addRow("From Date:", self.date_from)
        layout.addRow("To Date:", self.date_to)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
   
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def validate_and_accept(self):
        if self.date_from.date() > self.date_to.date():
            QMessageBox.warning(
                self, "Validation Error", "From date must be before To date!"
            )
            return
        self.accept()

    def get_data(self):
        return {
            'report_type': self.report_type.currentText(),
            'date_from': self.date_from.date().toPyDate(),
            'date_to': self.date_to.date().toPyDate()
        }


class JobCardDialog(QDialog):
    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Add Job Card")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout()
        
        self.technician = QLineEdit()
        self.status = QComboBox()
        self.status.addItems([
            'pending',
            'in_progress',
            'completed',
            'cancelled'
        ])
        self.labor_hours = QDoubleSpinBox()
        self.labor_hours.setRange(0, 999.99)
        self.notes = QTextEdit()
        
        layout.addRow("Technician:", self.technician)
        layout.addRow("Status:", self.status)
        layout.addRow("Labor Hours:", self.labor_hours)
        layout.addRow("Notes:", self.notes)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(buttons)
        self.setLayout(main_layout)

    def validate_and_accept(self):
        # First create an estimate
        estimate_data = {
            'customer_id': self.customer_id.value(),
            'vehicle_id': self.vehicle_id.value(),
            'date': self.date.date().toString("yyyy-MM-dd"),
            'total_amount': self.total_amount.value(),
            'status': 'Pending'
        }
        
        estimate_id = self.db_manager.add_estimate(estimate_data)
        
        if estimate_id:
            # Then create job card with estimate_id
            job_card_data = {
                'estimate_id': estimate_id,
                'description': self.description.text(),
                'start_date': self.start_date.date().toString("yyyy-MM-dd"),
                'end_date': self.end_date.date().toString("yyyy-MM-dd"),
                'status': 'In Progress'
            }
            
            if self.db_manager.add_job_card(job_card_data):
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Failed to add job card")
        else:
            QMessageBox.warning(self, "Error", "Failed to create estimate")

    def get_data(self):
        return {
            'technician': self.technician.text(),
            'status': self.status.currentText(),
            'labor_hours': self.labor_hours.value(),
            'notes': self.notes.toPlainText(),
            'start_date': datetime.now().isoformat(),
            'completion_date': None
        }
