from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                           QComboBox, QFrame, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models.models import session, MasterIngredient, Ingredient

class IngredientManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("FEAST MASTER - Ingredient Management")
        self.setMinimumSize(1000, 600)
        
        self.setup_ui()
        self.load_ingredients()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QFrame()
        header_layout = QHBoxLayout(header)
        title = QLabel("Master Ingredients")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Search and filter controls
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search ingredients...")
        search_box.setObjectName("search-box")
        search_box.textChanged.connect(self.filter_ingredients)
        header_layout.addWidget(search_box)
        
        main_layout.addWidget(header)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Ingredient Name", 
            "Category", 
            "Preferred UOM", 
            "Times Used",
            "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 150)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 100)
        main_layout.addWidget(self.table)

        # Bottom buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("+ Add New Ingredient")
        add_btn.setObjectName("button-success")
        add_btn.clicked.connect(self.add_new_ingredient)
        
        merge_btn = QPushButton("Merge Selected")
        merge_btn.setObjectName("button-primary")
        merge_btn.clicked.connect(self.merge_ingredients)
        
        back_btn = QPushButton("Back")
        back_btn.setObjectName("button-secondary")
        back_btn.clicked.connect(self.back_to_main)
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(merge_btn)
        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        
        main_layout.addLayout(button_layout)

    def load_ingredients(self):
        ingredients = session.query(MasterIngredient).order_by(MasterIngredient.name).all()
        self.table.setRowCount(len(ingredients))
        
        for row, ingredient in enumerate(ingredients):
            # Name
            name_item = QTableWidgetItem(ingredient.name)
            name_item.setData(Qt.ItemDataRole.UserRole, ingredient.id)
            self.table.setItem(row, 0, name_item)
            
            # Category
            category_combo = QComboBox()
            categories = ["", "Protein", "Produce", "Dairy", "Dry Goods", "Spices", "Bakery", "Frozen", "Condiments"]
            category_combo.addItems(categories)
            if ingredient.category:
                index = category_combo.findText(ingredient.category)
                if index >= 0:
                    category_combo.setCurrentIndex(index)
            category_combo.currentTextChanged.connect(
                lambda text, ing_id=ingredient.id: self.update_category(ing_id, text)
            )
            self.table.setCellWidget(row, 1, category_combo)
            
            # Preferred UOM
            uom_combo = QComboBox()
            uoms = ["", "oz", "lb", "cup", "tsp", "tbsp", "qt", "gallon", "each"]
            uom_combo.addItems(uoms)
            if ingredient.preferred_uom:
                index = uom_combo.findText(ingredient.preferred_uom)
                if index >= 0:
                    uom_combo.setCurrentIndex(index)
            uom_combo.currentTextChanged.connect(
                lambda text, ing_id=ingredient.id: self.update_uom(ing_id, text)
            )
            self.table.setCellWidget(row, 2, uom_combo)
            
            # Times Used
            times_used = session.query(Ingredient).filter_by(
                master_ingredient_id=ingredient.id
            ).count()
            usage_item = QTableWidgetItem(str(times_used))
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, usage_item)
            
            # Delete button
            delete_btn = QPushButton("×")
            delete_btn.setObjectName("button-delete")
            delete_btn.clicked.connect(lambda _, ing_id=ingredient.id: self.delete_ingredient(ing_id))
            self.table.setCellWidget(row, 4, delete_btn)
    def update_category(self, ingredient_id, new_category):
        try:
            ingredient = session.query(MasterIngredient).get(ingredient_id)
            if ingredient:
                ingredient.category = new_category if new_category != "" else None
                session.commit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update category: {str(e)}")

    def update_uom(self, ingredient_id, new_uom):
        try:
            ingredient = session.query(MasterIngredient).get(ingredient_id)
            if ingredient:
                ingredient.preferred_uom = new_uom if new_uom != "" else None
                session.commit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update UOM: {str(e)}")

    def delete_ingredient(self, ingredient_id):
        try:
            ingredient = session.query(MasterIngredient).get(ingredient_id)
            if ingredient:
                # Check if ingredient is in use
                usage_count = session.query(Ingredient).filter_by(
                    master_ingredient_id=ingredient_id
                ).count()
                
                if usage_count > 0:
                    QMessageBox.warning(
                        self,
                        "Cannot Delete",
                        f"This ingredient is used in {usage_count} recipes and cannot be deleted."
                    )
                    return

                confirm = QMessageBox(self)
                confirm.setWindowTitle("Confirm Delete")
                confirm.setText(f"Are you sure you want to delete '{ingredient.name}'?")
                confirm.setIcon(QMessageBox.Icon.Question)
                confirm.setStandardButtons(
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                confirm.setStyleSheet("""
                    QMessageBox {
                        background-color: #2d2d2d;
                        color: white;
                    }
                    QPushButton {
                        background-color: #4a90e2;
                        color: white;
                        border: none;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                    QPushButton:hover {
                        background-color: #357abd;
                    }
                """)
                
                if confirm.exec() == QMessageBox.StandardButton.Yes:
                    session.delete(ingredient)
                    session.commit()
                    self.load_ingredients()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete ingredient: {str(e)}")

    def add_new_ingredient(self):
        try:
            # Find the first empty row or add a new one
            found_empty = False
            for row in range(self.table.rowCount()):
                if not self.table.item(row, 0) or not self.table.item(row, 0).text():
                    found_empty = True
                    break
            
            if not found_empty:
                row = self.table.rowCount()
                self.table.setRowCount(row + 1)
            
            # Add empty name cell that's editable
            name_item = QTableWidgetItem("New Ingredient")
            name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, name_item)
            
            # Add combo boxes for category and UOM
            category_combo = QComboBox()
            categories = ["", "Protein", "Produce", "Dairy", "Dry Goods", "Spices", "Other"]
            category_combo.addItems(categories)
            self.table.setCellWidget(row, 1, category_combo)
            
            uom_combo = QComboBox()
            uoms = ["", "oz", "lb", "cup", "tsp", "tbsp", "qt", "gallon", "each"]
            uom_combo.addItems(uoms)
            self.table.setCellWidget(row, 2, uom_combo)
            
            # Usage count starts at 0
            usage_item = QTableWidgetItem("0")
            usage_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 3, usage_item)
            
            # Add delete button
            delete_btn = QPushButton("×")
            delete_btn.setObjectName("button-delete")
            self.table.setCellWidget(row, 4, delete_btn)
            
            # Edit the name
            self.table.editItem(name_item)
            
            # Save when editing is finished
            name_item.setData(Qt.ItemDataRole.UserRole, None)  # No ID yet
            self.table.itemChanged.connect(self.save_new_ingredient)
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add new ingredient: {str(e)}")

    def save_new_ingredient(self, item):
        if item.column() != 0:  # Only handle name column
            return
            
        try:
            ingredient_id = item.data(Qt.ItemDataRole.UserRole)
            if ingredient_id is None:  # This is a new ingredient
                name = item.text().strip()
                if not name:
                    return
                
                # Check for duplicates
                existing = session.query(MasterIngredient).filter(
                    MasterIngredient.name.ilike(name)
                ).first()
                if existing:
                    QMessageBox.warning(
                        self,
                        "Duplicate Ingredient",
                        f"An ingredient named '{name}' already exists."
                    )
                    self.load_ingredients()
                    return
                
                # Create new ingredient
                new_ingredient = MasterIngredient(
                    name=name,
                    category=self.table.cellWidget(item.row(), 1).currentText() or None,
                    preferred_uom=self.table.cellWidget(item.row(), 2).currentText() or None
                )
                session.add(new_ingredient)
                session.commit()
                
                # Reload to get everything in order
                self.table.itemChanged.disconnect(self.save_new_ingredient)
                self.load_ingredients()
                self.table.itemChanged.connect(self.save_new_ingredient)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save ingredient: {str(e)}")

    def merge_ingredients(self):
        # Get selected ingredients
        selected_items = self.table.selectedItems()
        if len(selected_items) < 2:
            QMessageBox.warning(
                self,
                "Selection Required",
                "Please select at least two ingredients to merge."
            )
            return
            
        try:
            # Get the first selected item as the primary
            primary_row = selected_items[0].row()
            primary_name = self.table.item(primary_row, 0).text()
            primary_id = self.table.item(primary_row, 0).data(Qt.ItemDataRole.UserRole)
            
            # Confirm merge
            confirm = QMessageBox(self)
            confirm.setWindowTitle("Confirm Merge")
            confirm.setText(
                f"Merge selected ingredients into '{primary_name}'?\n"
                "This cannot be undone."
            )
            confirm.setIcon(QMessageBox.Icon.Question)
            confirm.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm.exec() == QMessageBox.StandardButton.Yes:
                # Update all references to point to the primary ingredient
                for item in selected_items[1:]:
                    old_id = self.table.item(item.row(), 0).data(Qt.ItemDataRole.UserRole)
                    session.query(Ingredient).filter_by(
                        master_ingredient_id=old_id
                    ).update({"master_ingredient_id": primary_id})
                    
                    # Delete the old master ingredient
                    session.query(MasterIngredient).filter_by(id=old_id).delete()
                
                session.commit()
                self.load_ingredients()
                
                QMessageBox.information(
                    self,
                    "Success",
                    "Ingredients merged successfully!"
                )
                
        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Error", f"Failed to merge ingredients: {str(e)}")

    def filter_ingredients(self, search_text):
        search_text = search_text.lower()
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if name_item:
                name = name_item.text().lower()
                self.table.setRowHidden(row, search_text not in name)

    def back_to_main(self):
        self.close()
        self.main_window.show()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 14px;
            }
            
            QTableWidget {
                background-color: #2d2d2d;
                border: none;
                border-radius: 5px;
                gridline-color: #3d3d3d;
            }
            
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            
            QHeaderView::section {
                background-color: #2d2d2d;
                padding: 5px;
                border: none;
                border-right: 1px solid #3d3d3d;
                border-bottom: 1px solid #3d3d3d;
            }
            
            QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 3px;
                padding: 5px;
                min-width: 6em;
            }
            
            QComboBox:hover {
                border: 1px solid #4a90e2;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 3px;
                padding: 5px;
            }
            
            QPushButton {
                padding: 8px 15px;
                border-radius: 3px;
                border: none;
            }
            
            #button-success {
                background-color: #45a049;
                color: white;
            }
            
            #button-primary {
                background-color: #4a90e2;
                color: white;
            }
            
            #button-secondary {
                background-color: #404040;
                color: white;
            }
            
            #button-delete {
                background-color: #e25555;
                color: white;
                font-weight: bold;
                padding: 2px 8px;
            }
            
            QPushButton:hover {
                opacity: 0.8;
            }
        """)