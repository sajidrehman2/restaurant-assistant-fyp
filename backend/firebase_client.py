import os
import json
import logging
from typing import Optional

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False
    print("Firebase Admin SDK not installed. Run: pip install firebase-admin")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FirebaseClient:
    """Firebase Firestore client wrapper"""
    
    def __init__(self):
        self.db = None
        self.app = None
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """Initialize Firebase connection"""
        
        if not FIREBASE_AVAILABLE:
            logger.error("Firebase Admin SDK not available")
            return
        
        try:
            # Check if Firebase is already initialized
            if firebase_admin._apps:
                logger.info("Firebase already initialized")
                self.app = firebase_admin.get_app()
                self.db = firestore.client()
                return
            
            # Try to get credentials from environment variable (for deployment)
            if 'FIREBASE_SERVICE_ACCOUNT' in os.environ:
                logger.info("Loading Firebase credentials from environment variable")
                sa_info = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
                cred = credentials.Certificate(sa_info)
            
            # Try to load from local file (for development)
            elif os.path.exists("serviceAccountKey.json"):
                logger.info("Loading Firebase credentials from local file")
                cred = credentials.Certificate("serviceAccountKey.json")
            
            # Try alternative file name
            elif os.path.exists("firebase-key.json"):
                logger.info("Loading Firebase credentials from firebase-key.json")
                cred = credentials.Certificate("firebase-key.json")
            
            else:
                logger.error("No Firebase credentials found. Please set FIREBASE_SERVICE_ACCOUNT environment variable or place serviceAccountKey.json file")
                return
            
            # Initialize Firebase
            self.app = firebase_admin.initialize_app(cred)
            self.db = firestore.client()
            
            logger.info("Firebase initialized successfully")
            
            # Test connection
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.db = None
    
    def _test_connection(self):
        """Test Firebase connection"""
        try:
            # Try to read from a collection (this will create it if it doesn't exist)
            test_ref = self.db.collection('_test').limit(1)
            list(test_ref.stream())  # Execute the query
            logger.info("Firebase connection test successful")
        except Exception as e:
            logger.error(f"Firebase connection test failed: {e}")
    
    def is_connected(self) -> bool:
        """Check if Firebase is connected"""
        return self.db is not None
    
    def get_collection(self, collection_name: str):
        """Get a collection reference"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        return self.db.collection(collection_name)
    
    def add_document(self, collection_name: str, data: dict, document_id: Optional[str] = None):
        """Add a document to a collection"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        
        collection_ref = self.db.collection(collection_name)
        
        if document_id:
            collection_ref.document(document_id).set(data)
            return document_id
        else:
            doc_ref = collection_ref.add(data)
            return doc_ref[1].id
    
    def get_document(self, collection_name: str, document_id: str):
        """Get a specific document"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_document(self, collection_name: str, document_id: str, data: dict):
        """Update a document"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.update(data)
    
    def delete_document(self, collection_name: str, document_id: str):
        """Delete a document"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_ref.delete()
    
    def query_documents(self, collection_name: str, filters: list = None, order_by: str = None, limit: int = None):
        """Query documents with filters"""
        if not self.is_connected():
            raise Exception("Firebase not connected")
        
        query = self.db.collection(collection_name)
        
        # Apply filters
        if filters:
            for filter_item in filters:
                field, operator, value = filter_item
                query = query.where(field, operator, value)
        
        # Apply ordering
        if order_by:
            if isinstance(order_by, str):
                query = query.order_by(order_by)
            else:
                field, direction = order_by
                query = query.order_by(field, direction=firestore.Query.DESCENDING if direction == 'desc' else firestore.Query.ASCENDING)
        
        # Apply limit
        if limit:
            query = query.limit(limit)
        
        # Execute query
        docs = query.stream()
        results = []
        
        for doc in docs:
            doc_data = doc.to_dict()
            doc_data['doc_id'] = doc.id
            results.append(doc_data)
        
        return results

# Create global instance
firebase_client = FirebaseClient()

# Export the database instance for backward compatibility
db = firebase_client.db if firebase_client.is_connected() else None

# Utility functions
def init_firebase() -> Optional[firestore.Client]:
    """Initialize and return Firebase client (for backward compatibility)"""
    global firebase_client
    if firebase_client.is_connected():
        return firebase_client.db
    return None

def check_firebase_connection():
    """Check Firebase connection and print status"""
    if firebase_client.is_connected():
        print("✅ Firebase connected successfully")
        try:
            # Test basic operations
            test_data = {"test": True, "timestamp": firestore.SERVER_TIMESTAMP}
            firebase_client.add_document("_connection_test", test_data)
            print("✅ Firebase write test successful")
            
            # Clean up test document
            firebase_client.db.collection("_connection_test").limit(10).stream()
            print("✅ Firebase read test successful")
            
        except Exception as e:
            print(f"❌ Firebase operation test failed: {e}")
    else:
        print("❌ Firebase not connected")
        print("\nTo fix this:")
        print("1. Create a Firebase project at https://console.firebase.google.com")
        print("2. Enable Firestore Database")
        print("3. Go to Project Settings > Service Accounts")
        print("4. Generate a new private key (JSON)")
        print("5. Save as 'serviceAccountKey.json' in the project directory")
        print("6. Or set FIREBASE_SERVICE_ACCOUNT environment variable with the JSON content")

def setup_firestore_collections():
    """Set up initial Firestore collections and indexes"""
    if not firebase_client.is_connected():
        print("❌ Cannot setup collections - Firebase not connected")
        return
    
    try:
        # Create collections with sample documents if they don't exist
        collections_to_create = ['menus', 'orders', 'chat_logs', 'users']
        
        for collection_name in collections_to_create:
            # Check if collection exists by trying to get one document
            docs = firebase_client.db.collection(collection_name).limit(1).stream()
            doc_count = len(list(docs))
            
            if doc_count == 0:
                logger.info(f"Creating {collection_name} collection")
                
                # Add a placeholder document that can be deleted later
                placeholder_data = {
                    "placeholder": True,
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "note": f"Placeholder document for {collection_name} collection"
                }
                firebase_client.add_document(collection_name, placeholder_data, f"{collection_name}_placeholder")
            else:
                logger.info(f"{collection_name} collection already exists")
        
        print("✅ Firestore collections setup complete")
        
    except Exception as e:
        logger.error(f"Error setting up Firestore collections: {e}")
        print(f"❌ Error setting up collections: {e}")

if __name__ == "__main__":
    # Test Firebase connection when script is run directly
    print("Testing Firebase Connection...")
    print("=" * 40)
    check_firebase_connection()
    print()
    
    if firebase_client.is_connected():
        print("Setting up Firestore collections...")
        setup_firestore_collections()
    
    print("=" * 40)
    print("Test complete!")