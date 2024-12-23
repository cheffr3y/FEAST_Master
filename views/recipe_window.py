from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTextEdit, QComboBox, QFrame,
                           QGridLayout,QFormLayout,QListWidget, QScrollArea, QMessageBox, QCompleter,
                           QTreeWidget, QTreeWidgetItem)

from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QFont
from models.models import session, Recipe, Ingredient, Allergen, MasterIngredient
from menu_categories import MENU_CATEGORIES

class RecipeManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("FEAST MASTER - Recipe Management")
        self.setMinimumSize(1000, 700)
        self.current_recipe = None
        self.ingredient_rows = []
        self.allergens = ["Dairy", "Eggs", "Peanuts", "Tree Nuts", "Fish", "Shellfish", "Soy", "Wheat"]
        
        # Create recipe list combo box before loading names
        self.recipe_list = QComboBox()
        self.recipe_list.setObjectName("recipe-list")
        
        self.setup_ui()
        self.apply_styles()
        self.load_recipe_names()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)  # Changed to horizontal layout
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        form_layout = QFormLayout()

        # Left Panel (30% width) - Recipe List and Controls
        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)

        # Allergens List
        self.allergen_list = QListWidget()
        self.allergen_list.addItems(self.allergens)
        self.allergen_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        form_layout.addRow("Allergens:", self.allergen_list)

        # Search and Recipe Tree (replacing old recipe list)
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search menu items...")
        search_box.setObjectName("search-box")
        left_layout.addWidget(search_box)

        # New Tree Widget for recipes
        self.recipe_tree = QTreeWidget()
        self.recipe_tree.setHeaderLabels(["Menu Items"])
        self.recipe_tree.setObjectName("recipe-tree")
        self.recipe_tree.setMinimumHeight(300)
        self.recipe_tree.itemClicked.connect(self.on_recipe_selected)
        left_layout.addWidget(self.recipe_tree)

        # Action Buttons
        new_recipe_btn = QPushButton("New Recipe")
        new_recipe_btn.setObjectName("button-primary")
        edit_recipe_btn = QPushButton("Edit Selected")
        edit_recipe_btn.setObjectName("button-secondary")
        delete_recipe_btn = QPushButton("Delete Selected")
        delete_recipe_btn.setObjectName("button-danger")
        back_btn = QPushButton("Back to Main")
        back_btn.setObjectName("button-secondary")

        for btn in [new_recipe_btn, edit_recipe_btn, delete_recipe_btn, back_btn]:
            btn.setFixedHeight(36)
            left_layout.addWidget(btn)

        left_layout.addStretch()
        main_layout.addWidget(left_panel, 30)  # 30% width

        # Right Panel (70% width) - Recipe Details
        right_panel = QFrame()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Recipe Details Section
        details_layout = QGridLayout()
        details_layout.setSpacing(10)

        # Recipe Name
        self.recipe_name_input = QLineEdit()
        self.recipe_name_input.setPlaceholderText("Enter recipe name")
        self.recipe_name_input.setObjectName("recipe-name-input")
        self.recipe_name_input.setFixedHeight(36)
        details_layout.addWidget(QLabel("Recipe Name:"), 0, 0)
        details_layout.addWidget(self.recipe_name_input, 0, 1)
        
        # Menu Item Category
        category_layout = QHBoxLayout()
        
        # Main category dropdown
        self.category_combo = QComboBox()
        self.category_combo.addItem("")  # Empty option
        self.category_combo.addItems(sorted(MENU_CATEGORIES.keys()))
        self.category_combo.currentTextChanged.connect(self.update_subcategories)
        details_layout.addWidget(QLabel("Category:"), 1, 0)
        details_layout.addWidget(self.category_combo, 1, 1)

        # Subcategory dropdown
        self.subcategory_combo = QComboBox()
        self.subcategory_combo.addItem("")  # Empty option
        details_layout.addWidget(QLabel("Subcategory:"), 2, 0)
        details_layout.addWidget(self.subcategory_combo, 2, 1)

        # Description (smaller by default)
        self.menu_description_input = QTextEdit()
        self.menu_description_input.setPlaceholderText("Enter menu description")
        self.menu_description_input.setObjectName("description-input")
        self.menu_description_input.setFixedHeight(80)  # Smaller default height
        details_layout.addWidget(QLabel("Description:"), 3, 0)
        details_layout.addWidget(self.menu_description_input, 3, 1)

        right_layout.addLayout(details_layout)

        # Ingredients Section
        ingredients_frame = QFrame()
        ingredients_frame.setObjectName("ingredients-frame")
        ingredients_layout = QVBoxLayout(ingredients_frame)

        # Ingredients Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Ingredients"))
        add_btn = QPushButton("+ Add Ingredient")
        add_btn.setObjectName("button-success")
        add_btn.clicked.connect(self.add_ingredient_row)
        header_layout.addWidget(add_btn)
        ingredients_layout.addLayout(header_layout)

        # Ingredients List
        self.ingredients_scroll = QScrollArea()
        self.ingredients_scroll.setWidgetResizable(True)
        self.ingredients_scroll.setObjectName("ingredients-scroll")
        
        self.ingredients_container = QWidget()
        self.ingredients_layout = QVBoxLayout(self.ingredients_container)
        self.ingredients_layout.setSpacing(8)
        self.ingredients_scroll.setWidget(self.ingredients_container)
        
        ingredients_layout.addWidget(self.ingredients_scroll)
        right_layout.addWidget(ingredients_frame)

        # Save Button at bottom
        save_btn = QPushButton("💾 Save Recipe")
        save_btn.setObjectName("button-primary")
        save_btn.setFixedHeight(42)
        right_layout.addWidget(save_btn)

        main_layout.addWidget(right_panel, 70)  # 70% width

        # Connect signals
        new_recipe_btn.clicked.connect(self.clear_form)
        edit_recipe_btn.clicked.connect(self.edit_recipe)
        delete_recipe_btn.clicked.connect(self.delete_recipe)
        back_btn.clicked.connect(self.back_to_main)
        save_btn.clicked.connect(self.save_recipe)

    def load_recipe_names(self):
            try:
                self.recipe_tree.clear()
                
                # Create category items
                category_items = {}
                for category in sorted(MENU_CATEGORIES.keys()):
                    category_item = QTreeWidgetItem([category])
                    self.recipe_tree.addTopLevelItem(category_item)
                    category_items[category] = category_item
                    
                    # Add subcategories if they exist
                    if MENU_CATEGORIES[category]:
                        for subcategory in MENU_CATEGORIES[category]:
                            subcat_item = QTreeWidgetItem([subcategory])
                            category_item.addChild(subcat_item)
                            # Store with combined key for subcategories
                            category_items[f"{category}|{subcategory}"] = subcat_item

                # Add recipes to appropriate categories
                recipes = session.query(Recipe).order_by(Recipe.name).all()
                for recipe in recipes:
                    recipe_item = QTreeWidgetItem([recipe.name])
                    recipe_item.setData(0, Qt.ItemDataRole.UserRole, recipe.id)
                    
                    if recipe.category and recipe.subcategory:
                        # Add to subcategory
                        key = f"{recipe.category}|{recipe.subcategory}"
                        if key in category_items:
                            category_items[key].addChild(recipe_item)
                    elif recipe.category:
                        # Add to main category
                        if recipe.category in category_items:
                            category_items[recipe.category].addChild(recipe_item)
                    else:
                        # Add to root if no category
                        self.recipe_tree.addTopLevelItem(recipe_item)

                # Expand all categories
                self.recipe_tree.expandAll()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load recipes: {str(e)}")

    def on_recipe_selected(self, item):
        # Only load recipe if it's a leaf node (actual recipe, not a category)
        if item.childCount() == 0:
            recipe_name = item.text(0)
            recipe = session.query(Recipe).filter_by(name=recipe_name).first()
            if recipe:
                self.edit_recipe()

    def add_ingredient_row(self):
        row_widget = QFrame()
        row_widget.setObjectName("ingredient-row")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(10)

        # Ingredient name with autocomplete (60% width)
        ingredient_input = QLineEdit()
        ingredient_input.setPlaceholderText("Ingredient name")
        ingredient_input.setObjectName("ingredient-input")
        
        # Create completer from master ingredients
        master_ingredients = session.query(MasterIngredient.name).all()
        ingredient_list = [item[0] for item in master_ingredients]
        completer = QCompleter(ingredient_list)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        ingredient_input.setCompleter(completer)
        
        # When an ingredient is selected, automatically fill in the preferred UOM
        def on_ingredient_selected(text):
            master_ingredient = session.query(MasterIngredient).filter(
                MasterIngredient.name.ilike(text)
            ).first()
            if master_ingredient and master_ingredient.preferred_uom:
                uom_input.setText(master_ingredient.preferred_uom)
                
        ingredient_input.editingFinished.connect(
            lambda: on_ingredient_selected(ingredient_input.text())
        )
        
        row_layout.addWidget(ingredient_input, 60)

        # Quantity (20% width)
        quantity_input = QLineEdit()
        quantity_input.setPlaceholderText("Qty")
        quantity_input.setObjectName("ingredient-input")
        row_layout.addWidget(quantity_input, 20)

        # UOM (15% width)
        uom_input = QLineEdit()
        uom_input.setPlaceholderText("UOM")
        uom_input.setObjectName("ingredient-input")
        row_layout.addWidget(uom_input, 15)

        # Delete button (5% width)
        delete_btn = QPushButton("×")
        delete_btn.setObjectName("button-delete")
        delete_btn.clicked.connect(lambda: self.delete_ingredient_row(row_widget))
        row_layout.addWidget(delete_btn, 5)

        self.ingredients_layout.addWidget(row_widget)
        self.ingredient_rows.append((ingredient_input, quantity_input, uom_input))

    def delete_ingredient_row(self, row_widget):
        index = None
        for i in range(self.ingredients_layout.count()):
            if self.ingredients_layout.itemAt(i).widget() == row_widget:
                index = i
                break
        
        if index is not None:
            self.ingredients_layout.itemAt(index).widget().deleteLater()
            self.ingredient_rows.pop(index)

    def load_recipe_names(self):
        try:
            self.recipe_tree.clear()
            
            # Create category items
            category_items = {}
            for category in sorted(MENU_CATEGORIES.keys()):
                category_item = QTreeWidgetItem([category])
                self.recipe_tree.addTopLevelItem(category_item)
                category_items[category] = category_item
                
                # Add subcategories if they exist
                if MENU_CATEGORIES[category]:
                    for subcategory in MENU_CATEGORIES[category]:
                        subcat_item = QTreeWidgetItem([subcategory])
                        category_item.addChild(subcat_item)
                        # Store with combined key for subcategories
                        category_items[f"{category}|{subcategory}"] = subcat_item

            # Add recipes to appropriate categories
            recipes = session.query(Recipe).order_by(Recipe.name).all()
            for recipe in recipes:
                recipe_item = QTreeWidgetItem([recipe.name])
                recipe_item.setData(0, Qt.ItemDataRole.UserRole, recipe.id)
                
                if recipe.category and recipe.subcategory:
                    # Add to subcategory
                    key = f"{recipe.category}|{recipe.subcategory}"
                    if key in category_items:
                        category_items[key].addChild(recipe_item)
                elif recipe.category:
                    # Add to main category
                    if recipe.category in category_items:
                        category_items[recipe.category].addChild(recipe_item)
                else:
                    # Add to root if no category
                    self.recipe_tree.addTopLevelItem(recipe_item)

            # Expand all categories
            self.recipe_tree.expandAll()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load recipes: {str(e)}")

    def edit_recipe(self):
    # Get the selected item from the tree
        selected_items = self.recipe_tree.selectedItems()
        if not selected_items or selected_items[0].childCount() > 0:  # No selection or is a category
            return
            
        recipe_name = selected_items[0].text(0)
        recipe = session.query(Recipe).filter_by(name=recipe_name).first()

        if recipe:
            self.current_recipe = recipe
            self.recipe_name_input.setText(recipe.name)
            self.menu_description_input.setText(recipe.menu_description)
            
            # Set categories
            if recipe.category:
                index = self.category_combo.findText(recipe.category)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)
                    self.update_subcategories(recipe.category)
                    if recipe.subcategory:
                        subindex = self.subcategory_combo.findText(recipe.subcategory)
                        if subindex >= 0:
                            self.subcategory_combo.setCurrentIndex(subindex)

            # Clear existing ingredient rows
            self.clear_ingredient_rows()

            # Add ingredient rows for each ingredient
            for ingredient in recipe.ingredients:
                self.add_ingredient_row()
                ingredient_input, quantity_input, uom_input = self.ingredient_rows[-1]
                ingredient_input.setText(ingredient.ingredient)
                quantity_input.setText(str(ingredient.quantity))
                uom_input.setText(ingredient.uom)

            # Set allergens
            for i in range(self.allergen_list.count()):
                item = self.allergen_list.item(i)
                item.setSelected(item.text() in [a.allergen for a in recipe.allergens])
    
    def update_ingredient_completer(self):
        master_ingredients = session.query(MasterIngredient.name).all()
        ingredient_list = [item[0] for item in master_ingredients]
        for row in self.ingredient_rows:
            ingredient_input = row[0]
            completer = ingredient_input.completer()
            if completer:
                completer.setModel(QStringListModel(ingredient_list))

    def save_recipe(self):
        recipe_name = self.recipe_name_input.text()
        menu_description = self.menu_description_input.toPlainText()
        category = self.category_combo.currentText()        # Added
        subcategory = self.subcategory_combo.currentText() # Added

        if not recipe_name or not self.ingredient_rows:
            QMessageBox.warning(
                self, 
                "Validation Error", 
                "Recipe name and at least one ingredient are required.",
                QMessageBox.StandardButton.Ok
            )
            return

        try:
            if self.current_recipe:
                recipe = self.current_recipe
                recipe.name = recipe_name
                recipe.menu_description = menu_description
                recipe.category = category
                recipe.subcategory = subcategory
                recipe.ingredients.clear()
            
            else:
                recipe = Recipe(
                    name=recipe_name, 
                    menu_description=menu_description,
                    category=category,
                    subcategory=subcategory
                )        

            # Add ingredients
            for row in self.ingredient_rows:
                ingredient_input, quantity_input, uom_input = row
                ingredient_name = ingredient_input.text().strip()
                quantity_text = quantity_input.text().strip()
                uom = uom_input.text().strip()

                if ingredient_name and quantity_text and uom:
                    try:
                        quantity = float(quantity_text)
                        ingredient = Ingredient(
                            ingredient=ingredient_name,
                            quantity=quantity,
                            uom=uom
                        )
                        recipe.ingredients.append(ingredient)
                    except ValueError:
                        QMessageBox.warning(
                            self,
                            "Input Error",
                            f"Invalid quantity for ingredient: {ingredient_name}",
                            QMessageBox.StandardButton.Ok
                        )
                        return

                for item in self.allergen_list.selectedItems():  # Added back allergens
                    allergen = Allergen(allergen=item.text())
                    recipe.allergens.append(allergen)

            session.add(recipe)
            session.commit()

            msg = QMessageBox(self)
            msg.setWindowTitle("Success")
            msg.setText(f"Recipe '{recipe_name}' saved successfully!")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStyleSheet("""
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
            msg.exec()

            self.clear_form()
            self.load_recipe_names()

        except Exception as e:
            session.rollback()
            QMessageBox.warning(self, "Error", f"Failed to save recipe: {str(e)}")

    def delete_recipe(self):
        if self.recipe_list.currentIndex() == 0:  # "-- Select Recipe --"
            return
            
        recipe_name = self.recipe_list.currentText()
        
        confirm = QMessageBox(self)
        confirm.setWindowTitle("Confirm Delete")
        confirm.setText(f"Are you sure you want to delete '{recipe_name}'?")
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
            recipe = session.query(Recipe).filter_by(name=recipe_name).first()
            if recipe:
                try:
                    session.delete(recipe)
                    session.commit()
                    self.load_recipe_names()
                    self.clear_form()
                    
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Recipe '{recipe_name}' has been deleted.",
                        QMessageBox.StandardButton.Ok
                    )
                except Exception as e:
                    session.rollback()
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to delete recipe: {str(e)}",
                        QMessageBox.StandardButton.Ok
                    )

    def clear_form(self):
        self.current_recipe = None
        self.recipe_name_input.clear()
        self.menu_description_input.clear()
        self.clear_ingredient_rows()
        self.add_ingredient_row()
        self.recipe_list.setCurrentIndex(0)

    def clear_ingredient_rows(self):
        while self.ingredients_layout.count():
            item = self.ingredients_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.ingredient_rows = []

    def update_subcategories(self, category):
        self.subcategory_combo.clear()
        self.subcategory_combo.addItem("")  # Empty option
        if category in MENU_CATEGORIES and MENU_CATEGORIES[category]:
            self.subcategory_combo.addItems(MENU_CATEGORIES[category])
        self.subcategory_combo.setEnabled(bool(MENU_CATEGORIES.get(category, [])))

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
            
            QFrame#left-panel, QFrame#right-panel {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 20px;
            }
            
            QLineEdit, QTextEdit, QComboBox {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #4a90e2;
            }
            
            #ingredients-frame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 15px;
            }
            
            #ingredient-row {
                background-color: #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            
            #ingredients-scroll {
                border: none;
                background-color: transparent;
            }
            
            #button-primary {
                background-color: #4a90e2;
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            
            #button-secondary {
                background-color: #404040;
                border: none;
                border-radius: 5px;
            }
            
            #button-danger {
                background-color: #e25555;
                border: none;
                border-radius: 5px;
            }
            
            #button-success {
                background-color: #45a049;
                border: none;
                border-radius: 5px;
            }
            
            #button-delete {
                background-color: #e25555;
                border: none;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                padding: 0px;
            }
            
            QPushButton:hover {
                opacity: 0.8;
            }

            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 10px;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical {
                background-color: #4a90e2;
                border-radius: 5px;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }

            QLabel {
                color: #ffffff;
                background: transparent;
            }
            #recipe-tree {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                color: white;
            }
            
            #recipe-tree::item {
                padding: 5px;
                border-radius: 3px;
            }
            
            #recipe-tree::item:hover {
                background-color: #3d3d3d;
            }
            
            #recipe-tree::item:selected {
                background-color: #4a90e2;
            }
        """)