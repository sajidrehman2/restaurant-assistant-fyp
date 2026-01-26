from flask import Flask, request, jsonify
from flask_cors import CORS
from firebase_client import db
from nlp import parse_order
import uuid
import datetime
import logging
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Admin keyword detection
ADMIN_KEYWORDS = ["mark", "change price", "update menu", "set price", "mark unavailable", 
                  "mark available", "update item", "delete item", "add item", "firestore"]

def is_admin_command(text: str) -> bool:
    """Check if text contains admin-only commands"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in ADMIN_KEYWORDS)

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Smart Restaurant Ordering Assistant",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    })

@app.route('/health')
def health():
    """Detailed health check"""
    try:
        db.collection('menus').limit(1).get()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    })

@app.route('/menu', methods=['GET'])
def get_menu():
    """Get all menu items"""
    try:
        docs = db.collection('menus').where('available', '==', True).stream()
        menu = []
        for doc in docs:
            item = doc.to_dict()
            item['doc_id'] = doc.id
            menu.append(item)
        
        # Remove duplicate menu items
        seen_names = set()
        unique_menu = []
        for item in menu:
            name = item.get('name', '').lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_menu.append(item)
            else:
                logger.warning(f"Duplicate menu item found and removed: {item.get('name')}")
        
        logger.info(f"Retrieved {len(unique_menu)} unique menu items (removed {len(menu) - len(unique_menu)} duplicates)")
        return jsonify({
            "success": True,
            "menu": unique_menu,
            "count": len(unique_menu)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching menu: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch menu",
            "message": str(e)
        }), 500

@app.route('/menu/<category>', methods=['GET'])
def get_menu_by_category(category):
    """Get menu items by category"""
    try:
        docs = db.collection('menus').where('category', '==', category).where('available', '==', True).stream()
        menu = []
        for doc in docs:
            item = doc.to_dict()
            item['doc_id'] = doc.id
            menu.append(item)
        
        # Remove duplicates
        seen_names = set()
        unique_menu = []
        for item in menu:
            name = item.get('name', '').lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_menu.append(item)
        
        return jsonify({
            "success": True,
            "category": category,
            "menu": unique_menu,
            "count": len(unique_menu)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching menu by category {category}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch menu by category"
        }), 500

@app.route('/order', methods=['POST'])
def place_order():
    """Process and place an order from natural language input"""
    try:
        data = request.json
        user_text = data.get('message', '').strip()
        user_info = data.get('user', {"name": "Guest", "phone": None})
        
        if not user_text:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        logger.info(f"Processing order: {user_text}")
        
        # Block admin commands
        if is_admin_command(user_text):
            return jsonify({
                "success": False,
                "error": "This action is restricted to staff/admin users. Please use the admin panel for menu management.",
                "intent": "admin_blocked"
            }), 403
        
        # Get menu items
        menu_docs = []
        for doc in db.collection('menus').where('available', '==', True).stream():
            menu_item = doc.to_dict()
            menu_item['doc_id'] = doc.id
            menu_docs.append(menu_item)
        
        # Remove duplicate menu items
        seen_names = set()
        unique_menu_docs = []
        for item in menu_docs:
            name = item.get('name', '').lower()
            if name not in seen_names:
                seen_names.add(name)
                unique_menu_docs.append(item)
        
        menu_docs = unique_menu_docs
        logger.info(f"Loaded {len(menu_docs)} unique menu items from database")
        
        menu_names = [item['name'] for item in menu_docs]
        
        # Parse the order using NLP
        parsed = parse_order(user_text, menu_names)
        
        logger.info(f"Parsed result: {parsed}")
        
        # Handle empty/unclear messages
        if not user_text or user_text.isspace():
            return jsonify({
                "success": True,
                "intent": "empty",
                "response": "I didn't receive any message. How can I help you?"
            }), 200
        
        # Handle greeting
        if parsed['intent'] == 'greeting':
            return jsonify({
                "success": True,
                "intent": "greeting",
                "response": "Hello! Welcome to our restaurant. You can order food by saying something like 'I want 2 chicken pizzas and 1 coke' or ask to 'show menu' to see available items."
            }), 200
        
        # Handle help
        elif parsed['intent'] == 'help':
            return jsonify({
                "success": True,
                "intent": "help",
                "response": "I can help you with:\n• Ordering food (e.g., 'I want 2 pizzas and 1 coke' or just '2 pizzas and coke')\n• Viewing the menu (say 'show menu')\n• Checking your orders (say 'what did I order' or 'my orders')\n• Canceling orders (say 'cancel my order')\n\nWhat would you like to do?"
            }), 200
        
        # Handle show menu
        elif parsed['intent'] == 'show_menu':
            return jsonify({
                "success": True,
                "intent": "show_menu",
                "response": "Here's our menu:",
                "menu": menu_docs
            }), 200
        
        # Handle cancel order
        elif parsed['intent'] == 'cancel_order':
            order_id_match = re.search(r'ORD_\d{8}_\d{6}_[a-f0-9]{6}', user_text, re.IGNORECASE)
            
            if order_id_match:
                order_id = order_id_match.group(0)
                try:
                    doc = db.collection('orders').document(order_id).get()
                    
                    if not doc.exists:
                        return jsonify({
                            "success": False,
                            "intent": "cancel_order",
                            "response": f"Order {order_id} not found. Please check the Order ID and try again."
                        }), 404
                    
                    order = doc.to_dict()
                    current_status = order.get('status', 'Unknown')
                    
                    if current_status in ['Delivered', 'Cancelled']:
                        return jsonify({
                            "success": False,
                            "intent": "cancel_order",
                            "response": f"Order {order_id} is already {current_status} and cannot be cancelled."
                        }), 400
                    
                    db.collection('orders').document(order_id).update({
                        'status': 'Cancelled',
                        'updated_at': datetime.datetime.now(datetime.UTC)
                    })
                    
                    return jsonify({
                        "success": True,
                        "intent": "cancel_order",
                        "response": f"Order {order_id} has been successfully cancelled.",
                        "cancelled_order_id": order_id
                    }), 200
                    
                except Exception as e:
                    logger.error(f"Error cancelling order {order_id}: {e}")
                    return jsonify({
                        "success": False,
                        "intent": "cancel_order",
                        "response": "Failed to cancel order. Please try again or contact staff."
                    }), 500
            else:
                try:
                    orders_query = db.collection('orders').where('status', 'in', ['Pending', 'Confirmed']).order_by('created_at', direction='DESCENDING').limit(1).stream()
                    
                    orders = list(orders_query)
                    
                    if not orders:
                        return jsonify({
                            "success": False,
                            "intent": "cancel_order",
                            "response": "You don't have any active orders to cancel. If you need help with a specific order, please provide the Order ID."
                        }), 404
                    
                    order_doc = orders[0]
                    order_id = order_doc.id
                    order_data = order_doc.to_dict()
                    
                    db.collection('orders').document(order_id).update({
                        'status': 'Cancelled',
                        'updated_at': datetime.datetime.now(datetime.UTC)
                    })
                    
                    total = order_data.get('total_price', 0)
                    items_count = len(order_data.get('items', []))
                    
                    return jsonify({
                        "success": True,
                        "intent": "cancel_order",
                        "response": f"Your most recent order {order_id} (PKR {total}, {items_count} items) has been cancelled.",
                        "cancelled_order_id": order_id,
                        "cancelled_order": order_data
                    }), 200
                    
                except Exception as e:
                    logger.error(f"Error cancelling recent order: {e}")
                    return jsonify({
                        "success": False,
                        "intent": "cancel_order",
                        "response": "Failed to cancel order. Please try again or contact staff."
                    }), 500
        
        # Handle view orders
        elif parsed['intent'] == 'view_orders':
            try:
                recent_orders = []
                docs = db.collection('orders').order_by('created_at', direction='DESCENDING').limit(5).stream()
                for doc in docs:
                    order = doc.to_dict()
                    recent_orders.append({
                        "order_id": order.get('order_id'),
                        "total": order.get('total_price'),
                        "status": order.get('status'),
                        "items_count": len(order.get('items', []))
                    })
                
                if recent_orders:
                    response_text = "Here are your recent orders:\n"
                    for order in recent_orders:
                        response_text += f"\n• Order {order['order_id']}: PKR {order['total']} ({order['status']}) - {order['items_count']} items"
                    
                    return jsonify({
                        "success": True,
                        "intent": "view_orders",
                        "response": response_text,
                        "orders": recent_orders
                    }), 200
                else:
                    return jsonify({
                        "success": True,
                        "intent": "view_orders",
                        "response": "You don't have any orders yet. Would you like to place an order?"
                    }), 200
                    
            except Exception as e:
                logger.error(f"Error fetching orders: {e}")
                return jsonify({
                    "success": True,
                    "intent": "view_orders",
                    "response": "I couldn't retrieve your orders right now. Please try again or contact staff."
                }), 200
        
        # ============ FIX: Enhanced clarification for generic items ============
        elif parsed.get('needs_clarification', False):
            clarification_type = parsed['clarification_type']
            
            # Handle unclear items (NEW)
            if clarification_type == "unclear_items":
                unclear = parsed.get('unclear_items', [])
                response_text = f"I couldn't identify these items: {', '.join(unclear)}.\n\n"
                response_text += "Could you please clarify? You can:\n"
                response_text += "• Say 'show menu' to see available items\n"
                response_text += "• Rephrase your order with correct item names"
                
                return jsonify({
                    "success": True,
                    "intent": "clarification_needed",
                    "needs_clarification": True,
                    "clarification_type": clarification_type,
                    "response": response_text,
                    "unclear_items": unclear
                }), 200
            
            # Handle generic items (e.g., "pizza" without type)
            available_options = parsed['available_options']
            quantity = parsed['quantities'][0] if parsed['quantities'] else 1
            
            # Filter menu to show only the relevant options with details
            filtered_menu = [item for item in menu_docs if item['name'] in available_options]
            
            # Build informative response
            response_text = f"You want {quantity} {clarification_type}{'s' if quantity > 1 else ''}. We have the following options:\n\n"
            for idx, option in enumerate(filtered_menu, 1):
                response_text += f"{idx}. {option['name']} - PKR {option['price']}\n"
            response_text += f"\nWhich one would you like?"
            
            return jsonify({
                "success": True,
                "intent": "clarification_needed",
                "needs_clarification": True,
                "clarification_type": clarification_type,
                "quantity": quantity,
                "response": response_text,
                "available_options": available_options,
                "menu_details": filtered_menu
            }), 200
        
        # Handle food ordering
        elif parsed['intent'] == 'order_food':
            # ============ FIX PROBLEM 4: Partial order processing ============
            unclear_items = parsed.get('unclear_items', [])
            
            # Check if we have ANY valid items
            if not parsed['items'] and not unclear_items:
                return jsonify({
                    "success": False,
                    "error": "I couldn't identify any menu items in your message. Could you please specify what you'd like to order? For example: 'I want 2 chicken pizzas and 1 coke' or just '2 chicken pizzas and coke'. You can also say 'show menu' to see available items."
                }), 400
            
            # Process valid items even if some are unclear
            if parsed['items']:
                # Build order items - quantities already aggregated by NLP
                order_items = []
                total_price = 0
                quantities = parsed['quantities']
                not_found_items = []
                
                logger.info(f"Processing {len(parsed['items'])} items: {parsed['items']}")
                logger.info(f"With aggregated quantities: {quantities}")
                
                for i, item_name in enumerate(parsed['items']):
                    # Find matching menu item
                    menu_item = None
                    for m in menu_docs:
                        if m['name'].lower() == item_name.lower():
                            menu_item = m
                            break
                    
                    if menu_item:
                        logger.info(f"✓ Found menu item: {menu_item['name']} (ID: {menu_item.get('item_id')})")
                        quantity = quantities[i]
                        item_total = menu_item['price'] * quantity
                        
                        order_items.append({
                            "item_id": menu_item.get('item_id', 'UNKNOWN'),
                            "name": menu_item['name'],
                            "quantity": quantity,
                            "unit_price": menu_item['price'],
                            "total_price": item_total
                        })
                        total_price += item_total
                    else:
                        logger.warning(f"✗ Menu item not found: {item_name}")
                        not_found_items.append(item_name)
                
                if not order_items:
                    # ============ FIX PROBLEM 3: Better error message ============
                    error_msg = "I couldn't match any items to our menu."
                    if unclear_items:
                        error_msg += f" Unclear items: {', '.join(unclear_items)}."
                    error_msg += " Please check the menu (say 'show menu') and try again."
                    
                    return jsonify({
                        "success": False,
                        "error": error_msg,
                        "unclear_items": unclear_items
                    }), 400
                
                # Generate order ID
                order_id = f"ORD_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
                
                # Create order document
                current_time = datetime.datetime.now(datetime.UTC)
                order_doc = {
                    "order_id": order_id,
                    "user": user_info,
                    "items": order_items,
                    "total_price": total_price,
                    "status": "Pending",
                    "original_message": user_text,
                    "created_at": current_time,
                    "updated_at": current_time
                }
                
                # Add unclear items to order metadata if any
                if unclear_items:
                    order_doc["unclear_items"] = unclear_items
                
                logger.info(f"Order document to save: {order_doc}")
                
                # Save to database
                try:
                    logger.info(f"Attempting to save order: {order_id}")
                    doc_ref = db.collection('orders').document(order_id)
                    doc_ref.set(order_doc)
                    logger.info(f"✓ Order saved successfully to Firebase: {order_id}")
                    
                    # Verify the order was saved
                    saved_order = doc_ref.get()
                    if saved_order.exists:
                        logger.info(f"✓ Order verified in database: {order_id}")
                    else:
                        logger.error(f"✗ Order not found after saving: {order_id}")
                        
                except Exception as db_error:
                    logger.error(f"Failed to save order to Firebase: {db_error}", exc_info=True)
                    return jsonify({
                        "success": False,
                        "error": "Failed to save order to database",
                        "message": str(db_error)
                    }), 500
                
                # Log the conversation
                try:
                    chat_log = {
                        "order_id": order_id,
                        "sender": "user",
                        "message": user_text,
                        "timestamp": current_time,
                        "parsed_intent": parsed['intent'],
                        "extracted_items": parsed['items']
                    }
                    db.collection('chat_logs').add(chat_log)
                    
                    # Build response message
                    response_message = f"Order confirmed! Your order ID is {order_id}.\n\nItems:\n"
                    for item in order_items:
                        response_message += f"• {item['quantity']}x {item['name']} - PKR {item['total_price']}\n"
                    response_message += f"\nTotal: PKR {total_price}"
                    
                    # ============ FIX PROBLEM 4: Inform about unclear items ============
                    if unclear_items:
                        response_message += f"\n\n⚠️ Note: I couldn't identify these items: {', '.join(unclear_items)}. They were not included in your order."
                    
                    if not_found_items:
                        response_message += f"\n\n⚠️ Note: Could not find: {', '.join(not_found_items)}"
                    
                    system_log = {
                        "order_id": order_id,
                        "sender": "system",
                        "message": response_message,
                        "timestamp": current_time
                    }
                    db.collection('chat_logs').add(system_log)
                    logger.info(f"Chat logs saved for order: {order_id}")
                except Exception as log_error:
                    logger.warning(f"Failed to save chat logs: {log_error}")
                
                logger.info(f"✓ Order placed successfully: {order_id}")
                
                return jsonify({
                    "success": True,
                    "intent": parsed['intent'],
                    "order": order_doc,
                    "response": response_message,
                    "unclear_items": unclear_items  # Include for frontend awareness
                }), 201
            
            else:
                # No valid items but have unclear items
                return jsonify({
                    "success": False,
                    "error": f"I couldn't identify any menu items. Unclear items: {', '.join(unclear_items)}. Please say 'show menu' to see available items and try again.",
                    "unclear_items": unclear_items
                }), 400
        
        # Handle unknown intent
        else:
            return jsonify({
                "success": True,
                "intent": "unknown",
                "response": "I didn't quite understand that. I can help you with:\n• Ordering food (e.g., 'I want 2 pizzas' or just '2 pizzas and coke')\n• Viewing the menu (say 'show menu')\n• Checking orders (say 'my orders')\n• Canceling orders (say 'cancel order')\n\nWhat would you like to do?"
            }), 200
    
    except Exception as e:
        logger.error(f"Error processing order: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Failed to process order",
            "message": str(e)
        }), 500

@app.route('/orders', methods=['GET'])
def list_orders():
    """Get list of orders with optional filtering"""
    try:
        limit = request.args.get('limit', 50, type=int)
        status_filter = request.args.get('status', None)
        
        query = db.collection('orders').order_by('created_at', direction='DESCENDING').limit(limit)
        
        if status_filter:
            query = query.where('status', '==', status_filter)
        
        docs = query.stream()
        orders = []
        for doc in docs:
            order = doc.to_dict()
            order['doc_id'] = doc.id
            # Convert timestamps to ISO format
            if 'created_at' in order:
                order['created_at'] = order['created_at'].isoformat() if hasattr(order['created_at'], 'isoformat') else str(order['created_at'])
            if 'updated_at' in order:
                order['updated_at'] = order['updated_at'].isoformat() if hasattr(order['updated_at'], 'isoformat') else str(order['updated_at'])
            orders.append(order)
        
        return jsonify({
            "success": True,
            "orders": orders,
            "count": len(orders)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching orders: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch orders"
        }), 500

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get specific order by ID"""
    try:
        doc = db.collection('orders').document(order_id).get()
        
        if not doc.exists:
            return jsonify({
                "success": False,
                "error": "Order not found"
            }), 404
        
        order = doc.to_dict()
        order['doc_id'] = doc.id
        
        # Convert timestamps
        if 'created_at' in order:
            order['created_at'] = order['created_at'].isoformat() if hasattr(order['created_at'], 'isoformat') else str(order['created_at'])
        if 'updated_at' in order:
            order['updated_at'] = order['updated_at'].isoformat() if hasattr(order['updated_at'], 'isoformat') else str(order['updated_at'])
        
        return jsonify({
            "success": True,
            "order": order
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch order"
        }), 500

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({
                "success": False,
                "error": "Status is required"
            }), 400
        
        valid_statuses = ['Pending', 'Confirmed', 'Preparing', 'Ready', 'Delivered', 'Cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": f"Invalid status. Valid statuses: {valid_statuses}"
            }), 400
        
        db.collection('orders').document(order_id).update({
            'status': new_status,
            'updated_at': datetime.datetime.now(datetime.UTC)
        })
        
        return jsonify({
            "success": True,
            "message": f"Order {order_id} status updated to {new_status}"
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating order status {order_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to update order status"
        }), 500

@app.route('/chat/<order_id>', methods=['GET'])
def get_chat_history(order_id):
    """Get chat history for an order"""
    try:
        docs = db.collection('chat_logs').where('order_id', '==', order_id).order_by('timestamp').stream()
        chat_history = []
        
        for doc in docs:
            chat = doc.to_dict()
            chat['doc_id'] = doc.id
            if 'timestamp' in chat:
                chat['timestamp'] = chat['timestamp'].isoformat() if hasattr(chat['timestamp'], 'isoformat') else str(chat['timestamp'])
            chat_history.append(chat)
        
        return jsonify({
            "success": True,
            "order_id": order_id,
            "chat_history": chat_history,
            "count": len(chat_history)
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching chat history for order {order_id}: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to fetch chat history"
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found",
        "message": "The requested URL was not found on this server."
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "error": "Internal server error",
        "message": "An unexpected error occurred."
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    logger.info(f"Starting Smart Restaurant Ordering Assistant on port {port}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)