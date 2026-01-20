#!/usr/bin/env python3
"""
Seed script to populate Firestore database with initial menu data
Run this script after setting up Firebase to populate your database with sample menu items.

Usage:
    python seed_data.py
"""

import sys
import logging
from datetime import datetime
from firebase_client import firebase_client, db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample menu data
MENU_DATA = [
    # Pizzas
    {
        "item_id": "pizza_chicken_001",
        "name": "Chicken Pizza",
        "category": "Pizza",
        "price": 500,
        "description": "Delicious chicken pizza with cheese and vegetables",
        "available": True,
        "ingredients": ["chicken", "cheese", "tomato sauce", "bell peppers", "onions"],
        "size_available": ["Small", "Medium", "Large"],
        "vegetarian": False,
        "spicy": False
    },
    {
        "item_id": "pizza_margherita_002",
        "name": "Margherita Pizza",
        "category": "Pizza",
        "price": 400,
        "description": "Classic margherita with fresh mozzarella and basil",
        "available": True,
        "ingredients": ["mozzarella", "tomato sauce", "basil", "olive oil"],
        "size_available": ["Small", "Medium", "Large"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "pizza_pepperoni_003",
        "name": "Pepperoni Pizza",
        "category": "Pizza",
        "price": 550,
        "description": "Spicy pepperoni pizza with extra cheese",
        "available": True,
        "ingredients": ["pepperoni", "cheese", "tomato sauce"],
        "size_available": ["Small", "Medium", "Large"],
        "vegetarian": False,
        "spicy": True
    },
    
    # Burgers
    {
        "item_id": "burger_chicken_001",
        "name": "Chicken Burger",
        "category": "Burger",
        "price": 300,
        "description": "Grilled chicken burger with lettuce and mayo",
        "available": True,
        "ingredients": ["chicken breast", "lettuce", "tomato", "mayonnaise", "bun"],
        "size_available": ["Regular", "Large"],
        "vegetarian": False,
        "spicy": False
    },
    {
        "item_id": "burger_beef_002",
        "name": "Beef Burger",
        "category": "Burger",
        "price": 350,
        "description": "Juicy beef burger with cheese and pickles",
        "available": True,
        "ingredients": ["beef patty", "cheese", "lettuce", "pickles", "ketchup", "bun"],
        "size_available": ["Regular", "Large"],
        "vegetarian": False,
        "spicy": False
    },
    {
        "item_id": "burger_fish_003",
        "name": "Fish Burger",
        "category": "Burger",
        "price": 280,
        "description": "Crispy fish fillet burger with tartar sauce",
        "available": True,
        "ingredients": ["fish fillet", "lettuce", "tartar sauce", "bun"],
        "size_available": ["Regular"],
        "vegetarian": False,
        "spicy": False
    },
    {
        "item_id": "burger_veggie_004",
        "name": "Veggie Burger",
        "category": "Burger",
        "price": 250,
        "description": "Healthy vegetable burger with herbs",
        "available": True,
        "ingredients": ["vegetable patty", "lettuce", "tomato", "cucumber", "mayo", "bun"],
        "size_available": ["Regular"],
        "vegetarian": True,
        "spicy": False
    },
    
    # Drinks
    {
        "item_id": "drink_coke_001",
        "name": "Coke",
        "category": "Drinks",
        "price": 100,
        "description": "Chilled Coca-Cola",
        "available": True,
        "ingredients": ["cola"],
        "size_available": ["Can", "Bottle", "Large"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "drink_pepsi_002",
        "name": "Pepsi",
        "category": "Drinks",
        "price": 100,
        "description": "Chilled Pepsi Cola",
        "available": True,
        "ingredients": ["cola"],
        "size_available": ["Can", "Bottle", "Large"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "drink_tea_003",
        "name": "Hot Tea",
        "category": "Drinks",
        "price": 50,
        "description": "Traditional hot tea",
        "available": True,
        "ingredients": ["tea leaves", "water", "sugar", "milk"],
        "size_available": ["Cup", "Large Cup"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "drink_coffee_004",
        "name": "Coffee",
        "category": "Drinks",
        "price": 80,
        "description": "Fresh brewed coffee",
        "available": True,
        "ingredients": ["coffee beans", "water", "milk", "sugar"],
        "size_available": ["Cup", "Large Cup"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "drink_juice_005",
        "name": "Orange Juice",
        "category": "Drinks",
        "price": 120,
        "description": "Fresh orange juice",
        "available": True,
        "ingredients": ["oranges"],
        "size_available": ["Glass", "Large Glass"],
        "vegetarian": True,
        "spicy": False
    },
    
    # Sides
    {
        "item_id": "side_fries_001",
        "name": "French Fries",
        "category": "Sides",
        "price": 150,
        "description": "Crispy golden french fries",
        "available": True,
        "ingredients": ["potatoes", "oil", "salt"],
        "size_available": ["Regular", "Large"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "side_wings_002",
        "name": "Chicken Wings",
        "category": "Sides",
        "price": 200,
        "description": "Spicy chicken wings with sauce",
        "available": True,
        "ingredients": ["chicken wings", "spicy sauce", "herbs"],
        "size_available": ["6 pieces", "12 pieces"],
        "vegetarian": False,
        "spicy": True
    },
    {
        "item_id": "side_samosa_003",
        "name": "Samosa",
        "category": "Sides",
        "price": 30,
        "description": "Crispy fried samosa with vegetables",
        "available": True,
        "ingredients": ["flour", "potatoes", "peas", "spices"],
        "size_available": ["1 piece"],
        "vegetarian": True,
        "spicy": True
    },
    
    # Pakistani Food
    {
        "item_id": "pak_biryani_001",
        "name": "Chicken Biryani",
        "category": "Pakistani",
        "price": 400,
        "description": "Aromatic chicken biryani with basmati rice",
        "available": True,
        "ingredients": ["chicken", "basmati rice", "spices", "yogurt", "onions"],
        "size_available": ["Regular", "Family"],
        "vegetarian": False,
        "spicy": True
    },
    {
        "item_id": "pak_karahi_002",
        "name": "Chicken Karahi",
        "category": "Pakistani",
        "price": 450,
        "description": "Traditional chicken karahi with fresh tomatoes",
        "available": True,
        "ingredients": ["chicken", "tomatoes", "ginger", "garlic", "spices"],
        "size_available": ["Regular", "Large"],
        "vegetarian": False,
        "spicy": True
    },
    
    # Desserts
    {
        "item_id": "dessert_ice_cream_001",
        "name": "Ice Cream",
        "category": "Desserts",
        "price": 120,
        "description": "Vanilla ice cream scoop",
        "available": True,
        "ingredients": ["milk", "cream", "vanilla", "sugar"],
        "size_available": ["1 scoop", "2 scoops", "3 scoops"],
        "vegetarian": True,
        "spicy": False
    },
    {
        "item_id": "dessert_cake_002",
        "name": "Chocolate Cake",
        "category": "Desserts",
        "price": 180,
        "description": "Rich chocolate cake slice",
        "available": True,
        "ingredients": ["flour", "chocolate", "eggs", "butter", "sugar"],
        "size_available": ["Slice", "Large Slice"],
        "vegetarian": True,
        "spicy": False
    }
]

# Sample user data
SAMPLE_USERS = [
    {
        "user_id": "user_001",
        "name": "Ahmed Ali",
        "phone": "+92-300-1234567",
        "email": "ahmed.ali@example.com",
        "created_at": datetime.utcnow(),
        "total_orders": 0,
        "favorite_items": []
    },
    {
        "user_id": "user_002", 
        "name": "Fatima Khan",
        "phone": "+92-301-9876543",
        "email": "fatima.khan@example.com",
        "created_at": datetime.utcnow(),
        "total_orders": 0,
        "favorite_items": []
    }
]

def seed_menu_data():
    """Seed menu collection with sample data"""
    logger.info("Starting to seed menu data...")
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot seed data.")
        return False
    
    try:
        menu_collection = db.collection('menus')
        
        # Clear existing menu data (optional)
        # Uncomment the following lines if you want to clear existing data
        # logger.info("Clearing existing menu data...")
        # docs = menu_collection.stream()
        # for doc in docs:
        #     doc.reference.delete()
        
        # Add new menu items
        added_count = 0
        for item in MENU_DATA:
            try:
                # Check if item already exists
                existing = menu_collection.document(item['item_id']).get()
                
                if existing.exists:
                    logger.info(f"Menu item {item['name']} already exists, updating...")
                    menu_collection.document(item['item_id']).update({
                        **item,
                        'updated_at': datetime.utcnow()
                    })
                else:
                    logger.info(f"Adding menu item: {item['name']}")
                    menu_collection.document(item['item_id']).set({
                        **item,
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    })
                
                added_count += 1
                
            except Exception as e:
                logger.error(f"Error adding menu item {item['name']}: {e}")
        
        logger.info(f"Successfully processed {added_count} menu items")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding menu data: {e}")
        return False

def seed_user_data():
    """Seed users collection with sample data"""
    logger.info("Starting to seed user data...")
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot seed data.")
        return False
    
    try:
        users_collection = db.collection('users')
        
        added_count = 0
        for user in SAMPLE_USERS:
            try:
                # Check if user already exists
                existing = users_collection.document(user['user_id']).get()
                
                if not existing.exists:
                    logger.info(f"Adding user: {user['name']}")
                    users_collection.document(user['user_id']).set(user)
                    added_count += 1
                else:
                    logger.info(f"User {user['name']} already exists, skipping...")
                
            except Exception as e:
                logger.error(f"Error adding user {user['name']}: {e}")
        
        logger.info(f"Successfully processed {added_count} users")
        return True
        
    except Exception as e:
        logger.error(f"Error seeding user data: {e}")
        return False

def create_sample_order():
    """Create a sample order for testing"""
    logger.info("Creating sample order...")
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot create sample order.")
        return False
    
    try:
        from datetime import datetime
        import uuid
        
        # Sample order data
        order_id = f"ORD_SAMPLE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        sample_order = {
            "order_id": order_id,
            "user": {
                "name": "Sample Customer",
                "phone": "+92-300-0000000",
                "email": "sample@example.com"
            },
            "items": [
                {
                    "item_id": "pizza_chicken_001",
                    "name": "Chicken Pizza",
                    "quantity": 2,
                    "unit_price": 500,
                    "total_price": 1000
                },
                {
                    "item_id": "drink_coke_001", 
                    "name": "Coke",
                    "quantity": 2,
                    "unit_price": 100,
                    "total_price": 200
                }
            ],
            "total_price": 1200,
            "status": "Pending",
            "original_message": "I want 2 chicken pizzas and 2 cokes",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save order
        db.collection('orders').document(order_id).set(sample_order)
        
        # Create sample chat log
        chat_log = {
            "order_id": order_id,
            "sender": "user",
            "message": "I want 2 chicken pizzas and 2 cokes",
            "timestamp": datetime.utcnow(),
            "parsed_intent": "order_food",
            "extracted_items": ["Chicken Pizza", "Coke"]
        }
        
        db.collection('chat_logs').add(chat_log)
        
        # System response
        system_response = {
            "order_id": order_id,
            "sender": "system", 
            "message": f"Order confirmed! Your order ID is {order_id}. Total: $1200. Items: 2x Chicken Pizza, 2x Coke",
            "timestamp": datetime.utcnow()
        }
        
        db.collection('chat_logs').add(system_response)
        
        logger.info(f"Sample order created with ID: {order_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating sample order: {e}")
        return False

def verify_data():
    """Verify that data was seeded correctly"""
    logger.info("Verifying seeded data...")
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot verify data.")
        return False
    
    try:
        # Check menu items
        menu_docs = list(db.collection('menus').stream())
        menu_count = len(menu_docs)
        logger.info(f"Found {menu_count} menu items in database")
        
        # Check categories
        categories = set()
        for doc in menu_docs:
            data = doc.to_dict()
            categories.add(data.get('category', 'Unknown'))
        
        logger.info(f"Menu categories: {', '.join(sorted(categories))}")
        
        # Check users
        user_docs = list(db.collection('users').stream())
        user_count = len(user_docs)
        logger.info(f"Found {user_count} users in database")
        
        # Check orders
        order_docs = list(db.collection('orders').stream())
        order_count = len(order_docs)
        logger.info(f"Found {order_count} orders in database")
        
        # Check chat logs
        chat_docs = list(db.collection('chat_logs').stream())
        chat_count = len(chat_docs)
        logger.info(f"Found {chat_count} chat log entries in database")
        
        logger.info("Data verification completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error verifying data: {e}")
        return False

def display_menu_summary():
    """Display a summary of menu items by category"""
    logger.info("Generating menu summary...")
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot display menu summary.")
        return
    
    try:
        menu_docs = db.collection('menus').order_by('category').order_by('name').stream()
        
        current_category = None
        print("\n" + "="*60)
        print("MENU SUMMARY")
        print("="*60)
        
        for doc in menu_docs:
            item = doc.to_dict()
            category = item.get('category', 'Unknown')
            
            if category != current_category:
                current_category = category
                print(f"\n{category.upper()}:")
                print("-" * 30)
            
            price = item.get('price', 0)
            name = item.get('name', 'Unknown')
            desc = item.get('description', 'No description')
            available = "✅" if item.get('available', False) else "❌"
            vegetarian = "🥬" if item.get('vegetarian', False) else "🥩"
            spicy = "🌶️" if item.get('spicy', False) else ""
            
            print(f"{available} {vegetarian} {name} - ${price} {spicy}")
            print(f"   {desc}")
            
            sizes = item.get('size_available', [])
            if sizes:
                print(f"   Sizes: {', '.join(sizes)}")
            print()
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Error displaying menu summary: {e}")

def clean_database():
    """Clean all data from database (use with caution!)"""
    logger.warning("WARNING: This will delete ALL data from the database!")
    
    confirmation = input("Type 'DELETE ALL DATA' to confirm: ")
    if confirmation != "DELETE ALL DATA":
        logger.info("Operation cancelled.")
        return
    
    if not firebase_client.is_connected():
        logger.error("Firebase not connected. Cannot clean database.")
        return
    
    try:
        collections = ['menus', 'orders', 'chat_logs', 'users']
        
        for collection_name in collections:
            logger.info(f"Deleting all documents from {collection_name}...")
            
            docs = db.collection(collection_name).stream()
            batch = db.batch()
            count = 0
            
            for doc in docs:
                batch.delete(doc.reference)
                count += 1
                
                # Commit in batches of 500 (Firestore limit)
                if count % 500 == 0:
                    batch.commit()
                    batch = db.batch()
            
            # Commit remaining deletions
            if count % 500 != 0:
                batch.commit()
            
            logger.info(f"Deleted {count} documents from {collection_name}")
        
        logger.info("Database cleaned successfully!")
        
    except Exception as e:
        logger.error(f"Error cleaning database: {e}")

def main():
    """Main function to run seeding operations"""
    print("Smart Restaurant Ordering Assistant - Database Seeder")
    print("="*60)
    
    # Check Firebase connection
    if not firebase_client.is_connected():
        logger.error("❌ Firebase not connected!")
        logger.error("Please check your Firebase configuration:")
        logger.error("1. Ensure serviceAccountKey.json exists in the current directory")
        logger.error("2. Or set FIREBASE_SERVICE_ACCOUNT environment variable")
        logger.error("3. Verify your Firebase project settings")
        sys.exit(1)
    
    logger.info("✅ Firebase connected successfully!")
    
    # Menu for operations
    while True:
        print("\nSelect an operation:")
        print("1. Seed menu data")
        print("2. Seed user data")
        print("3. Create sample order")
        print("4. Verify seeded data")
        print("5. Display menu summary")
        print("6. Seed all data (1+2+3)")
        print("7. Clean database (⚠️  DANGER)")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
        if choice == "1":
            success = seed_menu_data()
            print("✅ Menu data seeded successfully!" if success else "❌ Failed to seed menu data")
        
        elif choice == "2":
            success = seed_user_data()
            print("✅ User data seeded successfully!" if success else "❌ Failed to seed user data")
        
        elif choice == "3":
            success = create_sample_order()
            print("✅ Sample order created successfully!" if success else "❌ Failed to create sample order")
        
        elif choice == "4":
            success = verify_data()
            if not success:
                print("❌ Data verification failed")
        
        elif choice == "5":
            display_menu_summary()
        
        elif choice == "6":
            logger.info("Seeding all data...")
            menu_success = seed_menu_data()
            user_success = seed_user_data()
            order_success = create_sample_order()
            
            if menu_success and user_success and order_success:
                print("✅ All data seeded successfully!")
                verify_data()
                display_menu_summary()
            else:
                print("❌ Some operations failed")
        
        elif choice == "7":
            clean_database()
        
        elif choice == "0":
            logger.info("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()