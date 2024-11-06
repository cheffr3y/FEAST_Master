from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from models.models import session, Recipe, MasterIngredient  # Add MasterIngredient here
from .recipe_window import RecipeManagementWindow
from .beo_window import BEOManagementWindow
from .ingredient_management_window import IngredientManagementWindow  # Add this import too


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FEAST MASTER")
        self.setMinimumSize(900, 600)
        self.setup_ui()
        self.apply_styles()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header with welcome message
        header = QFrame()
        header_layout = QHBoxLayout(header)
        title = QLabel("🍽️ Welcome to FEAST MASTER")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        header_layout.addWidget(title)
        main_layout.addWidget(header)

        # Cards Container
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Recipe Management Card
        recipe_card = self.create_card(
            "Recipe Management",
            "Create, edit, and manage your recipe database",
            f"Active Recipes: {session.query(Recipe).count()}",
            self.open_recipe_management
        )
        cards_layout.addWidget(recipe_card)

        # BEO Management Card
        beo_card = self.create_card(
            "BEO Management",
            "Plan and manage banquet events",
            "Recent Events: 0",
            self.open_beo_management
        )
        cards_layout.addWidget(beo_card)

        # Ingredient Management Card
        ingredient_card = self.create_card(
            "Ingredient Management",
            "Manage master ingredients list and categories",
            f"Total Ingredients: {session.query(MasterIngredient).count()}",
            self.open_ingredient_management
        )
        cards_layout.addWidget(ingredient_card)

        main_layout.addLayout(cards_layout)

    def create_card(self, title, description, stats, click_handler):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setObjectName("card-title")
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setObjectName("card-description")
        
        stats_label = QLabel(stats)
        stats_label.setObjectName("card-stats")
        
        button = QPushButton("Open")
        button.setObjectName("card-button")
        button.clicked.connect(click_handler)
        
        card_layout.addWidget(title_label)
        card_layout.addWidget(desc_label)
        card_layout.addWidget(stats_label)
        card_layout.addWidget(button)
        
        return card

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            
            #card {
                background-color: #2d2d2d;
                border-radius: 10px;
                padding: 15px;
                min-height: 180px;
                max-width: 300px;
            }
            
            #card:hover {
                background-color: #353535;
                border: 1px solid #4a90e2;
            }
            
            #card-title {
                color: #ffffff;
                padding: 0;
                background: none;
            }
            
            #card-description {
                color: #b3b3b3;
                padding: 0;
                background: none;
            }
            
            #card-stats {
                color: #4a90e2;
                font-size: 12px;
                padding: 0;
                background: none;
            }
            
            #card-button {
                background-color: #4a90e2;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 5px;
            }
            
            #card-button:hover {
                background-color: #357abd;
            }
        """)

    def open_recipe_management(self):
        from .recipe_window import RecipeManagementWindow
        self.recipe_window = RecipeManagementWindow(self)
        self.recipe_window.show()
        self.hide()

    def open_beo_management(self):
        from .beo_window import BEOManagementWindow
        self.beo_window = BEOManagementWindow(self)
        self.beo_window.show()
        self.hide()

    def open_ingredient_management(self):
        self.ingredient_window = IngredientManagementWindow(self)
        self.ingredient_window.show()
        self.hide()