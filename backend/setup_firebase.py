"""
Firebase Setup Script
This script will:
1. Test Firebase connection
2. Create initial menu items
3. Verify database structure
"""

import logging
from firebase_client import firebase_client, db
import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test Firebase connection"""
    print("\n" + "="*60)
    print("TESTING FIREBASE CONNECTION")
    print("="*60)
    
    if firebase_client.is_connected():
        print("✅ Firebase connected successfully!")
        return True
    else:
        print("❌ Firebase connection failed!")
        print("\nTroubleshooting steps:")
        print("1. Check if serviceAccountKey.json exists in the backend folder")
        print("2. Verify the JSON file has correct Firebase credentials")
        print("3. Ensure your Firebase project has Firestore enabled")
        return False

def create_menu_items():
    """Create sample menu items"""
    print("\n" + "="*60)
    print("CREATING MENU ITEMS")
    print("="*60)
    
    menu_items = [
        {
            "item_id": "MENU_001",
            "name": "Chicken Pizza",
            "description": "Delicious pizza topped with grilled chicken, cheese, and fresh vegetables",
            "price": 850,
            "category": "Pizza",
            "available": True,
            "vegetarian": False,
            "spicy": False
        },
        {
            "item_id": "MENU_002",
            "name": "Beef Burger",
            "description": "Juicy beef patty with lettuce, tomato, and special sauce",
            "price": 450,
            "category": "Burgers",
            "available": True,
            "vegetarian": False,
            "spicy": False
        },
        {
            "item_id": "MENU_003",
            "name": "Chicken Burger",
            "description": "Crispy chicken fillet with mayo and fresh vegetables",
            "price": 400,
            "category": "Burgers",
            "available": True,
            "vegetarian": False,
            "spicy": False
        },
        {
            "item_id": "MENU_004",
            "name": "French Fries",
            "description": "Crispy golden fries with seasoning",
            "price": 150,
            "category": "Sides",
            "available": True,
            "vegetarian": True,
            "spicy": False
        },
        {
            "item_id": "MENU_005",
            "name": "Coke",
            "description": "Chilled Coca-Cola 500ml",
            "price": 80,
            "category": "Beverages",
            "available": True,
            "vegetarian": True,
            "spicy": False
        },
        {
            "item_id": "MENU_006",
            "name": "Pepsi",
            "description": "Chilled Pepsi 500ml",
            "price": 80,
            "category": "Beverages",
            "available": True,
            "vegetarian": True,
            "spicy": False
        },
        {
            "item_id": "MENU_007",
            "name": "Hot Tea",
            "description": "Fresh brewed hot tea",
            "price": 50,
            "category": "Beverages",
            "available": True,
            "vegetarian": True,
            "spicy": False
        },
        {
            "item_id": "MENU_008",
            "name": "Coffee",
            "description": "Hot coffee",
            "price": 100,
            "category": "Beverages",
            "available": True,
            "vegetarian": True,
            "spicy": False
        },
        {
            "item_id": "MENU_009",
            "name": "Chicken Wings",
            "description": "Spicy chicken wings with dipping sauce",
            "price": 550,
            "category": "Appetizers",
            "available": True,
            "vegetarian": False,
            "spicy": True
        },
        {
            "item_id": "MENU_010",
            "name": "Samosa",
            "description": "Crispy vegetable samosa",
            "price": 30,
            "category": "Appetizers",
            "available": True,
            "vegetarian": True,
            "spicy": True
        },
        {
            "item_id": "MENU_011",
            "name": "Biryani",
            "description": "Aromatic chicken biryani with raita",
            "price": 350,
            "category": "Main Course",
            "available": True,
            "vegetarian": False,
            "spicy": True
        },
        {
            "item_id": "MENU_012",
            "name": "Pasta",
            "description": "Creamy white sauce pasta",
            "price": 400,
            "category": "Main Course",
            "available": True,
            "vegetarian": True,
            "spicy": False
        }
    ]
    
    created_count = 0
    for item in menu_items:
        try:
            # Check if item already exists
            existing = db.collection('menus').document(item['item_id']).get()
            
            if existing.exists:
                print(f"⚠️  {item['name']} already exists, skipping...")
            else:
                db.collection('menus').document(item['item_id']).set(item)
                print(f"✅ Created: {item['name']} (PKR {item['price']})")
                created_count += 1
        except Exception as e:
            print(f"❌ Error creating {item['name']}: {e}")
    
    print(f"\n✅ Successfully created {created_count} menu items")
    return created_count

def verify_database():
    """Verify database structure and data"""
    print("\n" + "="*60)
    print("VERIFYING DATABASE")
    print("="*60)
    
    try:
        # Check menu items
        menu_docs = list(db.collection('menus').stream())
        print(f"✅ Menu items found: {len(menu_docs)}")
        
        if menu_docs:
            print("\nSample menu items:")
            for doc in menu_docs[:3]:
                item = doc.to_dict()
                print(f"  - {item.get('name')} (PKR {item.get('price')})")
        
        # Check orders
        orders_docs = list(db.collection('orders').limit(5).stream())
        print(f"✅ Orders found: {len(orders_docs)}")
        
        # Check chat logs
        chat_docs = list(db.collection('chat_logs').limit(5).stream())
        print(f"✅ Chat logs found: {len(chat_docs)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")
        return False

def create_test_order():
    """Create a test order to verify everything works"""
    print("\n" + "="*60)
    print("CREATING TEST ORDER")
    print("="*60)
    
    try:
        import uuid
        
        order_id = f"TEST_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        current_time = datetime.datetime.now(datetime.UTC)
        
        test_order = {
            "order_id": order_id,
            "user": {
                "name": "Test User",
                "phone": "0300-1234567"
            },
            "items": [
                {
                    "item_id": "MENU_001",
                    "name": "Chicken Pizza",
                    "quantity": 1,
                    "unit_price": 850,
                    "total_price": 850
                }
            ],
            "total_price": 850,
            "status": "Pending",
            "original_message": "Test order - I want 1 chicken pizza",
            "created_at": current_time,
            "updated_at": current_time
        }
        
        db.collection('orders').document(order_id).set(test_order)
        print(f"✅ Test order created: {order_id}")
        print(f"   Order details: 1x Chicken Pizza (PKR 850)")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test order: {e}")
        return False

def display_firebase_indexes_info():
    """Display information about required Firebase indexes"""
    print("\n" + "="*60)
    print("FIREBASE INDEXES INFORMATION")
    print("="*60)
    
    print("\nIf you see index errors, follow these steps:")
    print("\n1. Go to Firebase Console:")
    print("   https://console.firebase.google.com")
    print("\n2. Select your project: restaurant-assistant-ba96a")
    print("\n3. Go to: Firestore Database → Indexes")
    print("\n4. Create these indexes if they don't exist:")
    print("\n   Collection: orders")
    print("   Fields: created_at (Descending)")
    print("\n   Collection: chat_logs")
    print("   Fields: order_id (Ascending), timestamp (Ascending)")
    print("\n5. Wait 2-3 minutes for indexes to build")
    print("\nIndexes are automatically created when you first run queries that need them.")

def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("SAJID SMARTDINE - FIREBASE SETUP")
    print("="*60)
    
    # Test connection
    if not test_connection():
        print("\n❌ Setup aborted due to connection failure")
        return False
    
    # Create menu items
    create_menu_items()
    
    # Verify database
    verify_database()
    
    # Create test order
    create_test_order()
    
    # Display index information
    display_firebase_indexes_info()
    
    print("\n" + "="*60)
    print("SETUP COMPLETE")
    print("="*60)
    print("\n✅ Your database is ready!")
    print("\nNext steps:")
    print("1. Start the backend server: python app.py")
    print("2. Start the frontend: streamlit run streamlit_app.py")
    print("3. Try placing an order through the chat interface")
    print("\n" + "="*60 + "\n")
    
    return True

if __name__ == "__main__":
    main()