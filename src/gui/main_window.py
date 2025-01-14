import logging

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,  # Add this import
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from database.db_manager import DatabaseManager

from .dialogs import (  # Add to imports
    InventoryItemDialog,
    JobCardDialog,
    NewEstimateDialog,
    ReportDialog,
)


class MainWindow(QMainWindow):
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        try:
            # Rename db_manager attribute
            self.db_manager = db_manager
            # Create status bar
            self.status_bar = self.statusBar()
            # Setup UI
            self.setup_ui()
            logging.info("MainWindow initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing MainWindow: {str(e)}")
            raise

    def setup_ui(self):
        self.setWindowTitle("Car Management System")
        self.setMinimumSize(800, 600)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create toolbar
        self.create_toolbar()

        # Create tab widget
        tabs = QTabWidget()
        tabs.addTab(self.create_estimates_tab(), "Estimates")
        tabs.addTab(self.create_inventory_tab(), "Inventory")
        tabs.addTab(self.create_reports_tab(), "Reports")
        tabs.addTab(self.create_jobcard_tab(), "JobCards")
        layout.addWidget(tabs)

    def create_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        # New Estimate Action
        new_estimate_action = QAction("New Estimate", self)
        new_estimate_action.triggered.connect(self.show_new_estimate_dialog)
        toolbar.addAction(new_estimate_action)

        # New Inventory Item Action
        new_inventory_action = QAction("New Item", self)
        new_inventory_action.triggered.connect(self.show_new_inventory_dialog)
        toolbar.addAction(new_inventory_action)

        # Generate Report Action
        generate_report_action = QAction("Generate Report", self)
        generate_report_action.triggered.connect(self.show_report_dialog)
        toolbar.addAction(generate_report_action)

    def create_estimates_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Estimates table
        self.estimates_table = QTableWidget()
        self.estimates_table.setColumnCount(7)
        self.estimates_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Customer",
                "Vehicle",
                "Date",
                "Amount",
                "Status",
                "Actions",
            ]
        )
        layout.addWidget(self.estimates_table)

        # New estimate button
        new_estimate_btn = QPushButton("New Estimate")
        new_estimate_btn.clicked.connect(self.show_new_estimate_dialog)
        layout.addWidget(new_estimate_btn)

        self.refresh_estimates_table()
        return widget

    def create_inventory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels(
            ["Item Code", "Description", "Quantity", "Unit Price", "Actions"]
        )
        layout.addWidget(self.inventory_table)

        # Add button for new inventory item
        new_item_btn = QPushButton("New Item")
        new_item_btn.clicked.connect(self.show_new_inventory_dialog)
        layout.addWidget(new_item_btn)

        self.refresh_inventory_table()
        return widget

    def create_reports_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Report generation buttons
        estimates_report_btn = QPushButton("Generate Estimates Report")
        estimates_report_btn.clicked.connect(
            lambda: self.show_report_dialog("Estimates")
        )
        layout.addWidget(estimates_report_btn)

        inventory_report_btn = QPushButton("Generate Inventory Report")
        inventory_report_btn.clicked.connect(
            lambda: self.show_report_dialog("Inventory")
        )
        layout.addWidget(inventory_report_btn)

        return widget

    def create_jobcard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # JobCards table
        self.jobcards_table = QTableWidget()
        self.jobcards_table.setColumnCount(7)
        self.jobcards_table.setHorizontalHeaderLabels(
            [
                "JobCard ID",
                "Estimate",
                "Status",
                "Technician",
                "Start Date",
                "Completion Date",
                "Actions",
            ]
        )
        layout.addWidget(self.jobcards_table)

        # Buttons
        button_layout = QHBoxLayout()
        new_jobcard_btn = QPushButton("New JobCard")
        new_jobcard_btn.clicked.connect(self.show_new_jobcard_dialog)
        button_layout.addWidget(new_jobcard_btn)
        layout.addLayout(button_layout)

        return widget

    def show_new_estimate_dialog(self):
        try:
            dialog = NewEstimateDialog(self)
            if dialog.exec():
                self.db_manager.create_estimate(dialog.estimate_data)
                self.refresh_estimates_table()
                self.status_bar.showMessage(
                    "Estimate created successfully", 3000
                )
                logging.info("New estimate created successfully")
        except Exception as e:
            error_msg = f"Failed to create estimate: {str(e)}"
            logging.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.critical(self, "Error", error_msg)

    def show_new_inventory_dialog(self):
        dialog = InventoryItemDialog(self)
        if dialog.exec():
            item_data = dialog.get_data()
            try:
                self.db_manager.update_inventory(item_data)
                self.refresh_inventory_table()
                self.status_bar.showMessage(
                    "Inventory updated successfully", 3000
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to update inventory: {str(e)}"
                )

    def show_report_dialog(self, report_type=None):
        dialog = ReportDialog(self)
        if report_type:
            dialog.report_type.setCurrentText(report_type)
        if dialog.exec():
            report_data = dialog.get_data()
            self.generate_report(report_data)

    def show_new_jobcard_dialog(self):
        """Show dialog to create new job card"""
        dialog = JobCardDialog(self)
        if dialog.exec():
            jobcard_data = dialog.get_data()
            try:
                self.db_manager.add_jobcard(jobcard_data)
                self.refresh_jobcards_table()
                self.status_bar.showMessage(
                    "Job card created successfully", 3000
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to create job card: {str(e)}"
                )

    def refresh_jobcards_table(self):
        """Refresh job cards table with latest data"""
        self.jobcards_table.setRowCount(0)
        try:
            jobcards = self.db_manager.get_jobcards()
            for row, jobcard in enumerate(jobcards):
                self.jobcards_table.insertRow(row)
                self.jobcards_table.setItem(
                    row, 0, QTableWidgetItem(str(jobcard["jobcard_id"]))
                )
                self.jobcards_table.setItem(
                    row, 1, QTableWidgetItem(str(jobcard["estimate_id"]))
                )
                self.jobcards_table.setItem(
                    row, 2, QTableWidgetItem(jobcard["status"])
                )
                self.jobcards_table.setItem(
                    row, 3, QTableWidgetItem(jobcard["technician"])
                )
                self.jobcards_table.setItem(
                    row, 4, QTableWidgetItem(str(jobcard["start_date"]))
                )
                self.jobcards_table.setItem(
                    row, 5, QTableWidgetItem(str(jobcard["completion_date"]))
                )
        except Exception as e:
            self.status_bar.showMessage(
                f"Error loading job cards: {str(e)}", 5000
            )

    def refresh_estimates_table(self):
        try:
            estimates = self.db_manager.get_all_estimates()
            self.estimates_table.setRowCount(0)
            for row, estimate in enumerate(estimates):
                self.estimates_table.insertRow(row)
                for col, value in enumerate(estimate):
                    self.estimates_table.setItem(
                        row, col, QTableWidgetItem(str(value))
                    )
        except Exception as e:
            error_msg = f"Failed to refresh estimates: {str(e)}"
            logging.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)

    def refresh_inventory_table(self):
        self.inventory_table.setRowCount(0)
        try:
            inventory_items = self.db_manager.get_inventory_items()
            for row, item in enumerate(inventory_items):
                self.inventory_table.insertRow(row)
                self.inventory_table.setItem(
                    row, 0, QTableWidgetItem(item["item_code"])
                )
                self.inventory_table.setItem(
                    row, 1, QTableWidgetItem(item["description"])
                )
                self.inventory_table.setItem(
                    row, 2, QTableWidgetItem(str(item["quantity"]))
                )
                self.inventory_table.setItem(
                    row, 3, QTableWidgetItem(f"${item['unit_price']:.2f}")
                )
        except Exception as e:
            error_message = f"Error loading inventory: {str(e)}"
            self.status_bar.showMessage(error_message, 5000)

    def generate_report(self, report_data):
        try:
            # This would be implemented based on your specific reporting needs
            report_message = (
                f"Generating {report_data['report_type']} report..."
            )
            self.status_bar.showMessage(report_message, 3000)
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to generate report: {str(e)}"
            )

    def create_estimate(self):
        try:
            dialog = NewEstimateDialog(self)
            if dialog.exec():
                if not dialog.estimate_data:
                    raise ValueError("No estimate data provided")
                if 'subtotal' not in dialog.estimate_data:
                    raise ValueError("Subtotal is required")
                
                self.db_manager.create_estimate(dialog.estimate_data)
                self.refresh_estimates_table()
                self.status_bar.showMessage("Estimate created successfully", 3000)
        except Exception as e:
            error_msg = f"Failed to create estimate: {str(e)}"
            logging.error(error_msg)
            self.status_bar.showMessage(error_msg, 5000)
            QMessageBox.critical(self, "Error", error_msg)
