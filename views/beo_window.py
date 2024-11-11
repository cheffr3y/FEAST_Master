from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTextEdit, QComboBox, QFrame,
                           QGridLayout, QScrollArea, QMessageBox, QDateEdit,
                           QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from models.models import session, Recipe, Ingredient, Allergen
from menu_categories import MENU_CATEGORIES
from datetime import datetime
from utils.unit_converter import convert_units

class BEOManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("FEAST MASTER - BEO Management")
        self.setMinimumSize(1200, 800)
        self.menu_item_selections = []
        
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Left Panel - Event Details (40% width)
        left_panel = QFrame()
        left_panel.setObjectName("left-panel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)

        # Event Details Section
        event_details = QFrame()
        event_details.setObjectName("details-section")
        details_layout = QGridLayout(event_details)
        details_layout.setSpacing(10)

        # Event Name
        self.event_name_input = QLineEdit()
        self.event_name_input.setPlaceholderText("Enter event name")
        self.event_name_input.setObjectName("detail-input")
        details_layout.addWidget(QLabel("Event Name:"), 0, 0)
        details_layout.addWidget(self.event_name_input, 0, 1)

        # Event Date with day of week
        self.event_date_input = QDateEdit()
        self.event_date_input.setDate(QDate.currentDate())
        self.event_date_input.setDisplayFormat("MM/dd/yyyy (ddd)")
        self.event_date_input.setObjectName("detail-input")
        details_layout.addWidget(QLabel("Event Date:"), 1, 0)
        details_layout.addWidget(self.event_date_input, 1, 1)

        # Guest Count
        self.guest_count_input = QLineEdit()
        self.guest_count_input.setPlaceholderText("Enter number of guests")
        self.guest_count_input.setObjectName("detail-input")
        details_layout.addWidget(QLabel("Guest Count:"), 2, 0)
        details_layout.addWidget(self.guest_count_input, 2, 1)

        # Special Requirements
        details_layout.addWidget(QLabel("Special Requirements:"), 3, 0)
        self.special_requirements_input = QTextEdit()
        self.special_requirements_input.setPlaceholderText("Enter any special requirements or notes")
        self.special_requirements_input.setObjectName("detail-input")
        self.special_requirements_input.setMaximumHeight(100)
        details_layout.addWidget(self.special_requirements_input, 3, 1)

        left_layout.addWidget(event_details)

        # Right Panel - Menu Items (60% width)
        right_panel = QFrame()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Search Box
        search_box = QLineEdit()
        search_box.setPlaceholderText("🔍 Search menu items...")
        search_box.setObjectName("search-box")
        right_layout.addWidget(search_box)

        # Menu Items Tree
        self.menu_tree = QTreeWidget()
        self.menu_tree.setHeaderLabels(["Menu Items"])
        self.menu_tree.setObjectName("menu-tree")
        self.menu_tree.setMinimumHeight(300)
        right_layout.addWidget(self.menu_tree)

        # Selected Items Section
        selected_items_frame = QFrame()
        selected_items_frame.setObjectName("selected-items-frame")
        selected_layout = QVBoxLayout(selected_items_frame)

        # Selected Items Header
        selected_header = QHBoxLayout()
        selected_header.addWidget(QLabel("Selected Items"))
        add_item_btn = QPushButton("+ Add Selected Item")
        add_item_btn.setObjectName("button-success")
        add_item_btn.clicked.connect(self.add_menu_item)
        selected_header.addWidget(add_item_btn)
        selected_layout.addLayout(selected_header)

        # Selected Items List
        self.selected_items_scroll = QScrollArea()
        self.selected_items_scroll.setWidgetResizable(True)
        self.selected_items_scroll.setObjectName("selected-items-scroll")
        
        self.selected_items_container = QWidget()
        self.selected_items_layout = QVBoxLayout(self.selected_items_container)
        self.selected_items_layout.setSpacing(8)
        self.selected_items_scroll.setWidget(self.selected_items_container)
        
        selected_layout.addWidget(self.selected_items_scroll)
        right_layout.addWidget(selected_items_frame)

        # Action Buttons
        back_btn = QPushButton("Back to Main")
        back_btn.setObjectName("button-secondary")
        generate_btn = QPushButton("📄 Generate Report")
        generate_btn.setObjectName("button-primary")
        
        for btn in [back_btn, generate_btn]:
            btn.setFixedHeight(42)

        # Add panels to main layout
        main_layout.addWidget(left_panel, 40)   # 40% width
        main_layout.addWidget(right_panel, 60)  # 60% width

        # Add button layout to main layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(back_btn)
        button_layout.addWidget(generate_btn)
        left_layout.addLayout(button_layout)

        # Load menu items into tree
        self.load_menu_items()

        # Connect signals after all methods are defined
        self.setup_connections(back_btn, generate_btn, search_box)

    def setup_connections(self, back_btn, generate_btn, search_box):
        back_btn.clicked.connect(self.back_to_main)
        generate_btn.clicked.connect(self.generate_reports)
        search_box.textChanged.connect(self.filter_menu_items)

    def load_menu_items(self):
        try:
            self.menu_tree.clear()
            
            # Create category items
            category_items = {}
            for category in sorted(MENU_CATEGORIES.keys()):
                category_item = QTreeWidgetItem([category])
                self.menu_tree.addTopLevelItem(category_item)
                category_items[category] = category_item
                
                # Add subcategories if they exist
                if MENU_CATEGORIES[category]:
                    for subcategory in MENU_CATEGORIES[category]:
                        subcat_item = QTreeWidgetItem([subcategory])
                        category_item.addChild(subcat_item)
                        category_items[f"{category}|{subcategory}"] = subcat_item

            # Add menu items to appropriate categories
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
                    self.menu_tree.addTopLevelItem(recipe_item)

            # Expand all categories
            self.menu_tree.expandAll()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load menu items: {str(e)}")

    def add_menu_item(self):
        selected_items = self.menu_tree.selectedItems()
        if not selected_items or selected_items[0].childCount() > 0:  # No selection or is a category
            return

        # Create new row for selected item
        row_widget = QFrame()
        row_widget.setObjectName("menu-item-row")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(10)

        # Menu item name (60% width)
        menu_item_name = selected_items[0].text(0)
        name_label = QLabel(menu_item_name)
        name_label.setObjectName("menu-item-label")
        row_layout.addWidget(name_label, 60)

        # Quantity input (35% width)
        quantity_input = QLineEdit()
        quantity_input.setPlaceholderText("Quantity")
        quantity_input.setObjectName("quantity-input")
        row_layout.addWidget(quantity_input, 35)

        # Delete button (5% width)
        delete_btn = QPushButton("×")
        delete_btn.setObjectName("button-delete")
        delete_btn.clicked.connect(lambda: self.delete_menu_item_row(row_widget))
        row_layout.addWidget(delete_btn, 5)

        self.selected_items_layout.addWidget(row_widget)
        self.menu_item_selections.append((menu_item_name, quantity_input))

    def delete_menu_item_row(self, row_widget):
        index = None
        for i in range(self.selected_items_layout.count()):
            if self.selected_items_layout.itemAt(i).widget() == row_widget:
                index = i
                break
        
        if index is not None:
            self.selected_items_layout.itemAt(index).widget().deleteLater()
            self.menu_item_selections.pop(index)

    def filter_menu_items(self, search_text):
        def filter_item(item, text):
            # If the item matches, show it and its parents
            if text.lower() in item.text(0).lower():
                item.setHidden(False)
                parent = item.parent()
                while parent:
                    parent.setHidden(False)
                    parent = parent.parent()
                return True
            
            # If it's a category/has children, check children
            if item.childCount() > 0:
                show_item = False
                for i in range(item.childCount()):
                    if filter_item(item.child(i), text):
                        show_item = True
                item.setHidden(not show_item)
                return show_item
            
            # No match
            item.setHidden(True)
            return False

        if not search_text:
            # Show all items if search is empty
            def show_all(item):
                item.setHidden(False)
                for i in range(item.childCount()):
                    show_all(item.child(i))
            
            for i in range(self.menu_tree.topLevelItemCount()):
                show_all(self.menu_tree.topLevelItem(i))
        else:
            # Filter based on search text
            for i in range(self.menu_tree.topLevelItemCount()):
                filter_item(self.menu_tree.topLevelItem(i), search_text)

    def generate_reports(self):
        # Now correctly indented to align with other methods
        if not self.event_name_input.text() or not self.guest_count_input.text():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Event name and guest count are required.",
                QMessageBox.StandardButton.Ok
            )
            return

        shopping_list = {}
        allergens = set()

        event_name = self.event_name_input.text()
        event_date = self.event_date_input.date()
        formatted_date = event_date.toString("dddd, MMMM d, yyyy")  # Includes day of week
        guest_count = self.guest_count_input.text()
        special_requirements = self.special_requirements_input.toPlainText()

        # Check if any menu items are selected
        if not self.menu_item_selections:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please add at least one menu item.",
                QMessageBox.StandardButton.Ok
            )
            return

        try:
            # Create organized menu items dictionary by category
            menu_items_by_category = {}
            
            # Loop through each selected menu item
            for menu_item_name, quantity_input in self.menu_item_selections:
                if not quantity_input.text().strip():
                    continue

                recipe = session.query(Recipe).filter_by(name=menu_item_name).first()
                if not recipe:
                    continue

                category = recipe.category or "Uncategorized"
                if category not in menu_items_by_category:
                    menu_items_by_category[category] = []
                
                try:
                    ordered_quantity = int(quantity_input.text())
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Input Error",
                        f"Invalid quantity for {menu_item_name}",
                        QMessageBox.StandardButton.Ok
                    )
                    return

                # Add to category list
                menu_items_by_category[category].append({
                    'recipe': recipe,
                    'quantity': ordered_quantity
                })

                # Update shopping list
                for ingredient in recipe.ingredients:
                    ingredient_name = ingredient.ingredient
                    ingredient_quantity = float(ingredient.quantity) * ordered_quantity
                    uom = ingredient.uom

                    # Convert the units if applicable
                    converted_quantity, converted_uom = convert_units(ingredient_quantity, uom)
                    if ingredient_name in shopping_list:
                        shopping_list[ingredient_name]['quantity'] += converted_quantity
                    else:
                        shopping_list[ingredient_name] = {
                            'quantity': converted_quantity, 
                            'uom': converted_uom
                        }

                # Update allergens
                allergens.update([a.allergen for a in recipe.allergens])

            self.generate_pdf_report(
                event_name, 
                formatted_date,
                guest_count, 
                special_requirements, 
                menu_items_by_category,
                shopping_list, 
                allergens
            )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to generate report: {str(e)}")

    def generate_pdf_report(self, event_name, event_date, guest_count, 
                          special_requirements, menu_items_by_category,
                          shopping_list, allergens):
        pdf_file = f"BEO_Report_{event_name.replace(' ', '_')}.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title = Paragraph(
            f"<para fontSize=24 textColor='#4a90e2' alignment=center><b>Banquet Event Order</b></para>", 
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Event Information
        event_info = Paragraph(
            f"""<para fontSize=12 leading=20>
            <b>Event:</b> {event_name}<br/>
            <b>Date:</b> {event_date}<br/>
            <b>Guest Count:</b> {guest_count}<br/>
            <b>Special Requirements:</b><br/>{special_requirements}
            </para>""",
            styles['Normal']
        )
        story.append(event_info)
        story.append(Spacer(1, 30))

        # Menu Items Section By Category
        story.append(Paragraph(
            '<para fontSize=18 textColor="#4a90e2"><b>Menu Items</b></para>', 
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        for category, items in menu_items_by_category.items():
            # Category Header
            story.append(Paragraph(
                f'<para fontSize=14><b>{category}</b></para>', 
                styles['Normal']
            ))
            story.append(Spacer(1, 10))

            for item in items:
                recipe = item['recipe']
                quantity = item['quantity']

                # Menu Item Name and Description
                story.append(Paragraph(
                    f"<b>{recipe.name}</b> (Quantity: {quantity})",
                    styles['Normal']
                ))
                if recipe.menu_description:
                    story.append(Paragraph(
                        f"<i>{recipe.menu_description}</i>",
                        styles['Normal']
                    ))
                story.append(Spacer(1, 10))

                # Ingredient Table for this item
                ingredient_data = [["Ingredient", "Quantity", "Unit"]]
                for ingredient in recipe.ingredients:
                    calculated_quantity = float(ingredient.quantity) * quantity
                    converted_quantity, converted_uom = convert_units(
                        calculated_quantity, 
                        ingredient.uom
                    )
                    ingredient_data.append([
                        ingredient.ingredient,
                        f"{converted_quantity:.2f}",
                        converted_uom
                    ])

                ingredient_table = Table(ingredient_data, colWidths=['50%', '25%', '25%'])
                ingredient_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                ]))
                story.append(ingredient_table)
                story.append(Spacer(1, 15))

            story.append(Spacer(1, 20))

        # Consolidated Shopping List
        story.append(Paragraph(
            '<para fontSize=18 textColor="#4a90e2"><b>Consolidated Shopping List</b></para>',
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        shopping_data = [["Ingredient", "Total Quantity", "Unit"]]
        for ingredient, details in sorted(shopping_list.items()):
            shopping_data.append([
                ingredient,
                f"{details['quantity']:.2f}",
                details['uom']
            ])

        shopping_table = Table(shopping_data, colWidths=['50%', '25%', '25%'])
        shopping_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ]))
        story.append(shopping_table)

        # Allergens Section
        if allergens:
            story.append(Spacer(1, 30))
            allergens_text = "Allergens: " + ", ".join(sorted(allergens))
            story.append(Paragraph(
                f"<para fontSize=12><b>{allergens_text}</b></para>", 
                styles['Normal']
            ))

        # Build the PDF
        doc.build(story)
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Success")
        msg.setText(f"BEO Report has been generated: {pdf_file}")
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
            
            QLineEdit, QTextEdit, QDateEdit {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            
            QLineEdit:focus, QTextEdit:focus, QDateEdit:focus {
                border: 1px solid #4a90e2;
            }
            
            #menu-tree {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                padding: 5px;
            }
            
            #menu-tree::item {
                padding: 5px;
                border-radius: 3px;
            }
            
            #menu-tree::item:hover {
                background-color: #3d3d3d;
            }
            
            #menu-tree::item:selected {
                background-color: #4a90e2;
            }
            
            #menu-item-row {
                background-color: #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
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
            
            #button-success {
                background-color: #45a049;
                border: none;
                border-radius: 5px;
                color: white;
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
        """)
