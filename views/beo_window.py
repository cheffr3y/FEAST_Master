from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QLineEdit, QTextEdit, QComboBox, QFrame,
                           QGridLayout, QScrollArea, QMessageBox, QDateEdit)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from models.models import session, Recipe, Ingredient, Allergen
from datetime import datetime
from utils.unit_converter import convert_units

class BEOManagementWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("FEAST MASTER - BEO Management")
        self.setMinimumSize(1200, 800)
        self.recipe_selections = []
        
        # Load recipes early for access throughout the class
        self.recipes = session.query(Recipe).all()
        
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

        # Action Buttons
        back_btn = QPushButton("Back to Main")
        back_btn.setObjectName("button-secondary")
        generate_btn = QPushButton("📄 Generate Report")
        generate_btn.setObjectName("button-primary")
        
        for btn in [back_btn, generate_btn]:
            btn.setFixedHeight(42)
            left_layout.addWidget(btn)

        left_layout.addStretch()
        main_layout.addWidget(left_panel, 40)  # 40% width
        # Right Panel - Menu Items (60% width)
        right_panel = QFrame()
        right_panel.setObjectName("right-panel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Menu Items Header
        menu_header = QHBoxLayout()
        menu_header.addWidget(QLabel("Menu Items"))
        add_menu_btn = QPushButton("+ Add Menu Item")
        add_menu_btn.setObjectName("button-success")
        add_menu_btn.clicked.connect(self.add_menu_item_row)
        menu_header.addWidget(add_menu_btn)
        right_layout.addLayout(menu_header)

        # Menu Items Scroll Area
        self.menu_scroll = QScrollArea()
        self.menu_scroll.setWidgetResizable(True)
        self.menu_scroll.setObjectName("menu-scroll")
        
        self.menu_container = QWidget()
        self.menu_items_layout = QVBoxLayout(self.menu_container)
        self.menu_items_layout.setSpacing(8)
        self.menu_scroll.setWidget(self.menu_container)
        
        right_layout.addWidget(self.menu_scroll)
        
        # Add first menu item row
        self.add_menu_item_row()
        
        main_layout.addWidget(right_panel, 60)  # 60% width

        # Connect signals
        back_btn.clicked.connect(self.back_to_main)
        generate_btn.clicked.connect(self.generate_reports)

    def add_menu_item_row(self):
        row_widget = QFrame()
        row_widget.setObjectName("menu-item-row")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(10)

        # Recipe dropdown (70% width)
        recipe_dropdown = QComboBox()
        recipe_dropdown.setObjectName("recipe-dropdown")
        recipe_dropdown.addItem("-- Select Menu Item --")
        # Sort recipes alphabetically before adding to dropdown
        sorted_recipes = sorted(self.recipes, key=lambda x: x.name)
        for recipe in sorted_recipes:
            recipe_dropdown.addItem(recipe.name)
        row_layout.addWidget(recipe_dropdown, 70)

        # Quantity (25% width)
        quantity_input = QLineEdit()
        quantity_input.setPlaceholderText("Quantity")
        quantity_input.setObjectName("quantity-input")
        row_layout.addWidget(quantity_input, 25)

        # Delete button (5% width)
        delete_btn = QPushButton("×")
        delete_btn.setObjectName("button-delete")
        delete_btn.clicked.connect(lambda: self.delete_menu_item_row(row_widget))
        row_layout.addWidget(delete_btn, 5)

        self.menu_items_layout.addWidget(row_widget)
        self.recipe_selections.append((recipe_dropdown, quantity_input))

    def delete_menu_item_row(self, row_widget):
        index = None
        for i in range(self.menu_items_layout.count()):
            if self.menu_items_layout.itemAt(i).widget() == row_widget:
                index = i
                break
        
        if index is not None:
            self.menu_items_layout.itemAt(index).widget().deleteLater()
            self.recipe_selections.pop(index)
    def generate_reports(self):
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
        # Get formatted date with day name
        formatted_date = event_date.toString("dddd, MMMM d, yyyy")
        guest_count = self.guest_count_input.text()
        special_requirements = self.special_requirements_input.toPlainText()

        # Check if any menu items are selected
        has_menu_items = False
        for recipe_dropdown, quantity_input in self.recipe_selections:
            if recipe_dropdown.currentIndex() > 0 and quantity_input.text().strip():
                has_menu_items = True
                break

        if not has_menu_items:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please add at least one menu item with quantity.",
                QMessageBox.StandardButton.Ok
            )
            return

        try:
            # Loop through each selected recipe
            for recipe_dropdown, quantity_input in self.recipe_selections:
                if recipe_dropdown.currentIndex() == 0:  # "-- Select Menu Item --"
                    continue

                recipe_name = recipe_dropdown.currentText()
                try:
                    ordered_quantity = int(quantity_input.text())
                except ValueError:
                    QMessageBox.warning(
                        self,
                        "Input Error",
                        f"Invalid quantity for {recipe_name}",
                        QMessageBox.StandardButton.Ok
                    )
                    return

                # Find the recipe object
                recipe = next((r for r in self.recipes if r.name == recipe_name), None)
                if recipe:
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
                shopping_list, 
                allergens
            )

        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to generate report: {str(e)}",
                QMessageBox.StandardButton.Ok
            )

    def generate_pdf_report(self, event_name, event_date, guest_count, 
                          special_requirements, shopping_list, allergens):
        pdf_file = f"BEO_Report_{event_name.replace(' ', '_')}.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Custom style for menu item headers
        styles.add(ParagraphStyle(
            name='MenuItemHeader',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#4a90e2'),
            spaceAfter=5
        ))

        # Title with modern styling
        title = Paragraph(
            f"""<para fontSize=24 textColor="#4a90e2" alignment=center>
                <b>Banquet Event Order</b>
            </para>""", 
            styles['Title']
        )
        story.append(title)
        story.append(Spacer(1, 20))

        # Event Information in a modern box
        event_info = f"""
            <para fontSize=12 leading=20>
            <b>Event:</b> {event_name}<br/>
            <b>Date:</b> {event_date}<br/>
            <b>Guest Count:</b> {guest_count}<br/>
            <b>Special Requirements:</b><br/>{special_requirements}
            </para>
        """
        story.append(Paragraph(event_info, styles['Normal']))
        story.append(Spacer(1, 30))

        # Menu Items Section - Each item with its own ingredients table
        story.append(Paragraph(
            '<para fontSize=18 textColor="#4a90e2"><b>Menu Items</b></para>', 
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        for recipe_dropdown, quantity_input in self.recipe_selections:
            if recipe_dropdown.currentIndex() == 0:
                continue

            recipe_name = recipe_dropdown.currentText()
            quantity = quantity_input.text()
            recipe = next((r for r in self.recipes if r.name == recipe_name), None)

            if recipe:
                # Menu Item Header
                story.append(Paragraph(
                    f"<b>{recipe_name}</b> (Quantity: {quantity})",
                    styles['MenuItemHeader']
                ))

                # Description
                if recipe.menu_description:
                    story.append(Paragraph(
                        f"<i>{recipe.menu_description}</i>",
                        styles['Normal']
                    ))
                    story.append(Spacer(1, 5))

                # Allergens for this item
                if recipe.allergens:
                    item_allergens = ", ".join(sorted(a.allergen for a in recipe.allergens))
                    story.append(Paragraph(
                        f"<b>Allergens:</b> {item_allergens}",
                        styles['Normal']
                    ))
                    story.append(Spacer(1, 5))

                # Ingredients table for this item
                ingredient_data = [["Ingredient", "Quantity", "Unit"]]
                for ingredient in recipe.ingredients:
                    # Calculate quantity based on ordered amount
                    calculated_quantity = float(ingredient.quantity) * int(quantity)
                    converted_quantity, converted_uom = convert_units(
                        calculated_quantity, 
                        ingredient.uom
                    )
                    ingredient_data.append([
                        ingredient.ingredient,
                        f"{converted_quantity:.2f}",
                        converted_uom
                    ])

                # Create and style the table
                ingredient_table = Table(ingredient_data, colWidths=['50%', '25%', '25%'])
                ingredient_table.setStyle(TableStyle([
                    # Header styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Body styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Left align ingredients
                    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Right align numbers
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
                     [colors.HexColor('#f9f9f9'), colors.HexColor('#f5f5f5')]),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                    ('TOPPADDING', (0, 1), (-1, -1), 8),
                ]))

                story.append(ingredient_table)
                story.append(Spacer(1, 20))

        # Consolidated Shopping List
        story.append(Spacer(1, 10))
        story.append(Paragraph(
            '<para fontSize=18 textColor="#4a90e2"><b>Consolidated Shopping List</b></para>',
            styles['Normal']
        ))
        story.append(Spacer(1, 15))

        # Create consolidated shopping list table
        shopping_data = [["Ingredient", "Total Quantity", "Unit"]]
        for ingredient, details in sorted(shopping_list.items()):
            shopping_data.append([
                ingredient,
                f"{details['quantity']:.2f}",
                details['uom']
            ])

        shopping_table = Table(shopping_data, colWidths=['50%', '25%', '25%'])
        shopping_table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90e2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
             [colors.HexColor('#f9f9f9'), colors.HexColor('#f5f5f5')]),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
        ]))

        story.append(shopping_table)

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
            
            QLineEdit, QTextEdit, QComboBox, QDateEdit {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 8px;
                color: white;
            }
            
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #4a90e2;
            }
            
            #menu-item-row {
                background-color: #3d3d3d;
                border-radius: 5px;
                padding: 5px;
                margin: 2px;
            }
            
            #menu-scroll {
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