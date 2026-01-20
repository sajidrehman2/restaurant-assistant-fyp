import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from rapidfuzz import process, fuzz
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import advanced NLP libraries
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
    logger.info("Transformers library available - using advanced NLP")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.info("Transformers not available - using basic NLP processing")

try:
    from word2number import w2n
    WORD2NUMBER_AVAILABLE = True
except ImportError:
    WORD2NUMBER_AVAILABLE = False
    logger.info("word2number not available - using basic number parsing")

class RestaurantNLP:
    """NLP processor for restaurant orders with fuzzy matching"""
    
    def __init__(self):
        self.intent_classifier = None
        self.setup_models()
        
        # Food item aliases for better matching
        self.food_aliases = {
            'coca cola': 'coke',
            'coca-cola': 'coke',
            'cola': 'coke',
            'pepsi cola': 'pepsi',
            'french fry': 'french fries',
            'fries': 'french fries',
            'chips': 'french fries',
            'tea': 'hot tea',
            'chai': 'hot tea',
            'biryani': 'chicken biryani',
            'margherita': 'margherita pizza',
            'pepperoni': 'pepperoni pizza',
            'wings': 'chicken wings',
            'fried chicken': 'chicken wings'
        }
        
        # Common spelling mistakes mapping
        self.common_mistakes = {
            'piza': 'pizza',
            'pizz': 'pizza',
            'buger': 'burger',
            'burgar': 'burger',
            'cok': 'coke',
            'coke': 'coke',
            'coffe': 'coffee',
            'cofffee': 'coffee',
            'chiken': 'chicken',
            'chikn': 'chicken',
            'beryani': 'biryani',
            'biriyani': 'biryani'
        }
        
        # Improved intent patterns
        self.intent_patterns = {
            'view_orders': [
                r'\b(what did i|show my|view my|check my|my)\b.*\b(order|orders)\b',
                r'\b(order history|past orders|previous orders|recent orders)\b',
                r'\b(what.*order|which.*order)\b',
                r'^\b(my orders?|check orders?)\b'
            ],
            'cancel_order': [
                r'\b(cancel|remove|delete|stop)\b.*\b(order|my order)\b',
                r'\b(don\'t want|changed my mind)\b.*\b(order)?\b',
                r'^\b(cancel)\b(?!.*\border\b.*\bhistory\b)'
            ],
            'show_menu': [
                r'\b(menu|what do you have|what\'s available|show|list)\b',
                r'\b(see.*menu|menu.*please|display.*menu)\b',
                r'\b(what.*available|available.*items)\b'
            ],
            'greeting': [
                r'^\b(hello|hi|hey|good morning|good afternoon|good evening)\b',
                r'^\b(how are you|what\'s up|greetings)\b'
            ],
            'help': [
                r'\b(help|how|what can|assist)\b',
                r'\b(support|guide|instructions)\b'
            ],
            'order_food': [
                r'\b(want|need|order|get|give me|i\'ll have|can i have)\b',
                r'\b(pizza|burger|chicken|food|drink|eat)\b',
                r'\b\d+\b.*\b(pizza|burger|chicken|coke|tea|coffee)\b'
            ]
        }
        
        # Enhanced quantity words with better coverage
        self.quantity_words = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'a': 1, 'an': 1, 'single': 1, 'double': 2, 'triple': 3,
            'couple': 2, 'few': 3, 'several': 3, 'dozen': 12, 'half': 0.5
        }
        
        # Generic food types that need clarification
        self.generic_items = {
            'pizza': ['Chicken Pizza', 'Margherita Pizza', 'Pepperoni Pizza'],
            'burger': ['Chicken Burger', 'Beef Burger', 'Fish Burger', 'Veggie Burger'],
        }
        
        # Specific type indicators
        self.specific_indicators = {
            'pizza': ['chicken', 'margherita', 'pepperoni', 'beef', 'veggie', 'vegetable', 'cheese', 'supreme'],
            'burger': ['chicken', 'beef', 'fish', 'veggie', 'vegetable', 'cheese']
        }
        
        # ============ FIX: Fuzzy matching threshold ============
        self.FUZZY_MATCH_THRESHOLD = 70  # 70% similarity for fuzzy matching
        
    def setup_models(self):
        """Initialize NLP models"""
        if TRANSFORMERS_AVAILABLE:
            try:
                self.intent_classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1
                )
                logger.info("Intent classifier loaded successfully")
            except Exception as e:
                logger.warning(f"Failed to load transformer model: {e}")
                self.intent_classifier = None
    
    def normalize_text(self, text: str) -> str:
        """Normalize text by applying aliases and fixing common mistakes"""
        text_lower = text.lower()
        
        # Apply common spelling mistake corrections first
        for mistake, correction in self.common_mistakes.items():
            text_lower = re.sub(rf'\b{re.escape(mistake)}\b', correction, text_lower)
        
        # Apply aliases
        for alias, canonical in self.food_aliases.items():
            text_lower = re.sub(rf'\b{re.escape(alias)}\b', canonical, text_lower)
        
        return text_lower
    
    def fuzzy_match_menu_item(self, query: str, menu_names: List[str]) -> Optional[Tuple[str, float]]:
        """
        ============ FIX PROBLEM 2: Fuzzy matching for spelling errors ============
        Use RapidFuzz to find best matching menu item for misspelled queries
        Returns: (matched_item, confidence_score) or None
        """
        if not query or not menu_names:
            return None
        
        # Normalize query
        query_normalized = self.normalize_text(query)
        
        # First try exact match
        for menu_item in menu_names:
            if menu_item.lower() == query_normalized:
                logger.info(f"Exact match: '{query}' → '{menu_item}'")
                return (menu_item, 100.0)
        
        # Try fuzzy matching with different scorers
        best_match = None
        best_score = 0
        
        # Scorer 1: Token sort ratio (good for word order variations)
        matches = process.extract(
            query_normalized,
            [item.lower() for item in menu_names],
            scorer=fuzz.token_sort_ratio,
            limit=1
        )
        
        if matches and matches[0][1] >= self.FUZZY_MATCH_THRESHOLD:
            matched_lower = matches[0][0]
            # Find original menu item
            for menu_item in menu_names:
                if menu_item.lower() == matched_lower:
                    best_match = menu_item
                    best_score = matches[0][1]
                    break
        
        # Scorer 2: Partial ratio (good for partial matches)
        if best_score < 85:  # Try another scorer if not confident
            matches2 = process.extract(
                query_normalized,
                [item.lower() for item in menu_names],
                scorer=fuzz.partial_ratio,
                limit=1
            )
            
            if matches2 and matches2[0][1] > best_score and matches2[0][1] >= self.FUZZY_MATCH_THRESHOLD:
                matched_lower = matches2[0][0]
                for menu_item in menu_names:
                    if menu_item.lower() == matched_lower:
                        best_match = menu_item
                        best_score = matches2[0][1]
                        break
        
        if best_match:
            logger.info(f"Fuzzy match: '{query}' → '{best_match}' (score: {best_score:.1f})")
            return (best_match, best_score)
        
        logger.debug(f"No fuzzy match found for: '{query}'")
        return None
    
    def contains_food_items(self, text: str, menu_names: List[str]) -> bool:
        """Check if text contains any food items from menu (with fuzzy matching)"""
        text_normalized = self.normalize_text(text)
        
        # Check exact matches
        for menu_item in menu_names:
            menu_lower = menu_item.lower()
            if menu_lower in text_normalized:
                return True
            
            # Check individual words
            words = menu_lower.split()
            for word in words:
                if len(word) > 3 and word in text_normalized:
                    return True
        
        # Check fuzzy matches for individual words
        text_words = re.findall(r'\b\w+\b', text_normalized)
        for word in text_words:
            if len(word) > 3:  # Only check meaningful words
                fuzzy_result = self.fuzzy_match_menu_item(word, menu_names)
                if fuzzy_result and fuzzy_result[1] >= self.FUZZY_MATCH_THRESHOLD:
                    return True
        
        return False
    
    def contains_quantity(self, text: str) -> bool:
        """Check if text contains any quantity indicators"""
        text_lower = text.lower()
        
        # Check for numeric quantities
        if re.search(r'\b\d+\b', text_lower):
            return True
        
        # Check for "Nx" pattern
        if re.search(r'\b\d+x\b', text_lower):
            return True
        
        # Check for word quantities
        for word in self.quantity_words.keys():
            if re.search(rf'\b{word}\b', text_lower):
                return True
        
        return False
    
    def classify_intent(self, text: str, menu_names: List[str]) -> str:
        """Classify the intent of the input text"""
        text_lower = text.lower().strip()
        
        # Handle empty text
        if not text_lower or text_lower.isspace():
            return 'unknown'
        
        # Priority 1: View orders
        for pattern in self.intent_patterns['view_orders']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'view_orders' matched by pattern: {pattern}")
                return 'view_orders'
        
        # Priority 2: Cancel order
        for pattern in self.intent_patterns['cancel_order']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'cancel_order' matched by pattern: {pattern}")
                return 'cancel_order'
        
        # Priority 3: Show menu
        for pattern in self.intent_patterns['show_menu']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'show_menu' matched by pattern: {pattern}")
                return 'show_menu'
        
        # Priority 4: Greeting
        for pattern in self.intent_patterns['greeting']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'greeting' matched by pattern: {pattern}")
                return 'greeting'
        
        # Priority 5: Help
        for pattern in self.intent_patterns['help']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'help' matched by pattern: {pattern}")
                return 'help'
        
        # Implicit ordering: food + quantity
        if self.contains_food_items(text, menu_names) and self.contains_quantity(text):
            logger.info("Implicit order detected: food items + quantity present")
            return 'order_food'
        
        # If text contains food items (even without quantity), likely an order
        if self.contains_food_items(text, menu_names):
            logger.info("Implicit order detected: food items present")
            return 'order_food'
        
        # Explicit order food patterns
        for pattern in self.intent_patterns['order_food']:
            if re.search(pattern, text_lower, re.IGNORECASE):
                logger.debug(f"Intent 'order_food' matched by pattern: {pattern}")
                return 'order_food'
        
        # Use transformer model if available
        if self.intent_classifier is not None:
            try:
                candidate_intents = ["order_food", "show_menu", "cancel_order", "view_orders", "greeting", "help"]
                result = self.intent_classifier(text, candidate_intents)
                intent = result['labels'][0]
                confidence = result['scores'][0]
                
                if confidence > 0.5:
                    logger.debug(f"Intent '{intent}' classified by transformer with confidence {confidence:.2f}")
                    return intent
            except Exception as e:
                logger.error(f"Error in transformer classification: {e}")
        
        logger.debug(f"No clear intent detected for: {text}")
        return "unknown"
    
    def extract_quantity_from_text(self, text: str) -> Optional[int]:
        """
        ============ FIX PROBLEM 5: Enhanced quantity extraction ============
        Extract quantity from text with support for multiple formats
        """
        text_lower = text.lower().strip()
        
        # Pattern 1: "Nx" format (e.g., "3x", "2x")
        match = re.search(r'(\d+)x', text_lower)
        if match:
            return int(match.group(1))
        
        # Pattern 2: Pure numeric (e.g., "3", "2")
        match = re.search(r'\b(\d+)\b', text_lower)
        if match:
            return int(match.group(1))
        
        # Pattern 3: Word numbers
        if WORD2NUMBER_AVAILABLE:
            try:
                # Try to convert entire text
                return w2n.word_to_num(text_lower)
            except:
                pass
        
        # Pattern 4: Manual word number mapping
        for word, num in self.quantity_words.items():
            if re.search(rf'\b{word}\b', text_lower):
                return int(num)
        
        return None
    
    def extract_quantities_and_items_together(self, text: str, menu_names: List[str]) -> Tuple[List[str], List[int], List[str]]:
        """
        ============ FIX PROBLEMS 1, 2, 3, 4: Complete rewrite with fuzzy matching ============
        Extract items AND quantities with:
        - Fuzzy matching for spelling errors
        - Duplicate detection and quantity aggregation
        - Partial order processing (separate valid from invalid)
        
        Returns: (valid_items, quantities, unclear_items)
        """
        items_dict = defaultdict(int)  # Use dict to aggregate quantities
        unclear_items = []
        
        # Normalize text
        text_normalized = self.normalize_text(text)
        logger.info(f"Extracting from normalized text: {text_normalized}")
        
        # Split by common separators
        parts = re.split(r'\band\b|,|;', text_normalized)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            logger.debug(f"Processing part: '{part}'")
            
            # Extract quantity from this part
            quantity = self.extract_quantity_from_text(part)
            if quantity is None:
                quantity = 1  # Default quantity
            
            # Try to find menu item in this part
            matched_item = None
            match_score = 0
            
            # Method 1: Exact substring match
            for menu_item in menu_names:
                menu_lower = menu_item.lower()
                if menu_lower in part:
                    matched_item = menu_item
                    match_score = 100
                    logger.info(f"Exact match: '{part}' contains '{menu_item}'")
                    break
            
            # Method 2: Fuzzy match on entire part
            if not matched_item:
                fuzzy_result = self.fuzzy_match_menu_item(part, menu_names)
                if fuzzy_result:
                    matched_item, match_score = fuzzy_result
            
            # Method 3: Fuzzy match on individual words in part
            if not matched_item:
                words = re.findall(r'\b\w+\b', part)
                for word in words:
                    if len(word) > 3:  # Skip short words
                        fuzzy_result = self.fuzzy_match_menu_item(word, menu_names)
                        if fuzzy_result and fuzzy_result[1] > match_score:
                            matched_item, match_score = fuzzy_result
            
            if matched_item:
                # ============ FIX PROBLEM 1: Aggregate quantities for duplicate items ============
                items_dict[matched_item] += quantity
                logger.info(f"✓ Added: {quantity}x {matched_item} (total: {items_dict[matched_item]})")
            else:
                # ============ FIX PROBLEM 4: Track unclear items separately ============
                unclear_items.append(part)
                logger.warning(f"✗ Unclear item: '{part}'")
        
        # ============ Final pass: catch standalone menu items ============
        # This handles items mentioned without clear separators
        for menu_item in menu_names:
            menu_lower = menu_item.lower()
            
            if menu_lower in text_normalized:
                # Only add if not already processed
                if menu_item not in items_dict:
                    # Try to find nearby quantity
                    pattern = rf'(\d+)\s*{re.escape(menu_lower)}|{re.escape(menu_lower)}\s*(\d+)|(\d+)x\s*{re.escape(menu_lower)}'
                    match = re.search(pattern, text_normalized)
                    
                    if match:
                        qty_str = match.group(1) or match.group(2) or match.group(3)
                        qty = int(qty_str) if qty_str else 1
                    else:
                        qty = 1
                    
                    items_dict[menu_item] = qty
                    logger.info(f"✓ Caught in final pass: {qty}x {menu_item}")
        
        # Convert dict to lists
        items = list(items_dict.keys())
        quantities = [items_dict[item] for item in items]
        
        logger.info(f"Final extraction: Items={items}, Quantities={quantities}, Unclear={unclear_items}")
        return items, quantities, unclear_items
    
    def has_specific_type(self, text: str, generic_name: str) -> bool:
        """Check if text has specific type like 'chicken pizza'"""
        text_lower = text.lower()
        indicators = self.specific_indicators.get(generic_name, [])
        
        for indicator in indicators:
            pattern1 = rf'\b{indicator}\s+{generic_name}\b'
            pattern2 = rf'\b{generic_name}\s+{indicator}\b'
            
            if re.search(pattern1, text_lower) or re.search(pattern2, text_lower):
                logger.info(f"Found specific type '{indicator}' for '{generic_name}'")
                return True
        
        return False
    
    def check_generic_items(self, text: str, menu_names: List[str]) -> Optional[str]:
        """Check if user mentioned ONLY generic term without specific type"""
        text_normalized = self.normalize_text(text)
        
        for generic_name in self.generic_items.keys():
            if not re.search(rf'\b{generic_name}\b', text_normalized):
                continue
            
            if self.has_specific_type(text, generic_name):
                logger.info(f"Specific type found for '{generic_name}', no clarification needed")
                continue
            
            has_specific = False
            for menu_item in menu_names:
                menu_lower = menu_item.lower()
                if menu_lower in text_normalized and len(menu_lower.split()) > 1:
                    has_specific = True
                    logger.info(f"Specific menu item '{menu_item}' found")
                    break
            
            if not has_specific:
                logger.info(f"ONLY generic term '{generic_name}' found - needs clarification")
                return generic_name
        
        return None

def parse_order(text: str, menu_names: List[str]) -> Dict[str, Any]:
    """
    ============ MAIN PARSING FUNCTION - FIXED ============
    Main function to parse a restaurant order with:
    - Fuzzy matching for spelling errors
    - Quantity aggregation for duplicates
    - Partial order processing
    """
    
    if not text or not text.strip():
        return {
            "intent": "unknown",
            "items": [],
            "quantities": [],
            "confidence": 0.0,
            "needs_clarification": False,
            "clarification_type": None,
            "available_options": [],
            "unclear_items": []
        }
    
    nlp = RestaurantNLP()
    text = text.strip()
    logger.info(f"Processing order text: {text}")
    
    # Classify intent
    intent = nlp.classify_intent(text, menu_names)
    logger.info(f"Detected intent: {intent}")
    
    items = []
    quantities = []
    unclear_items = []
    needs_clarification = False
    clarification_type = None
    available_options = []
    
    # Only extract food items if intent is order_food
    if intent == "order_food":
        # STEP 1: Check for generic terms first
        generic_item = nlp.check_generic_items(text, menu_names)
        
        if generic_item:
            needs_clarification = True
            clarification_type = generic_item
            available_options = nlp.generic_items[generic_item]
            
            # Extract quantity for the generic item
            quantity = nlp.extract_quantity_from_text(text) or 1
            quantities = [quantity]
            logger.info(f"Generic term '{generic_item}' needs clarification, quantity={quantity}")
        else:
            # STEP 2: Extract ALL specific items with fuzzy matching
            items, quantities, unclear_items = nlp.extract_quantities_and_items_together(text, menu_names)
            
            # ============ FIX PROBLEM 3: Don't reject if we have SOME valid items ============
            if not items and unclear_items:
                # No valid items but have unclear ones
                needs_clarification = True
                clarification_type = "unclear_items"
                available_options = unclear_items
    
    confidence = calculate_confidence(text, intent, items, quantities)
    
    result = {
        "intent": intent,
        "items": items,
        "quantities": quantities,
        "confidence": confidence,
        "needs_clarification": needs_clarification,
        "clarification_type": clarification_type,
        "available_options": available_options,
        "unclear_items": unclear_items  # ============ NEW: Track unclear items ============
    }
    
    logger.info(f"Parse result: {result}")
    return result

def calculate_confidence(text: str, intent: str, items: List[str], quantities: List[int]) -> float:
    """Calculate confidence score"""
    confidence = 0.5
    
    # High confidence for non-order intents
    if intent in ["greeting", "help", "show_menu", "cancel_order", "view_orders"]:
        confidence += 0.3
    elif intent == "order_food":
        if items:
            confidence += 0.3
        else:
            confidence -= 0.2
    
    if items:
        confidence += 0.2
        if len(quantities) == len(items):
            confidence += 0.1
    
    text_lower = text.lower()
    ordering_phrases = ['want', 'need', 'order', 'get', 'give me', "i'll have", 'can i have']
    if any(phrase in text_lower for phrase in ordering_phrases):
        confidence += 0.1
    
    if re.search(r'\b\d+\b', text) and intent == "order_food":
        confidence += 0.1
    
    confidence = max(0.0, min(1.0, confidence))
    return round(confidence, 2)

def test_nlp_parsing():
    """Test function with all problem cases"""
    sample_menu = [
        "Chicken Pizza", "Margherita Pizza", "Pepperoni Pizza",
        "Beef Burger", "Chicken Burger", "Fish Burger", "Veggie Burger",
        "Coke", "Pepsi", "French Fries", "Chicken Wings", "Samosa",
        "Hot Tea", "Coffee", "Chicken Biryani", "Pasta", "Chicken Karahi"
    ]
    
    test_cases = [
        # Problem 1: Duplicate quantities
        "2 Chicken Karahi and two Margherita Pizza and three 1x Margherita Pizza",
        "I want 2 coke and 1 coke and 3 coke",
        
        # Problem 2: Spelling errors
        "i want piza",
        "give me 2 bugers and 1 cok",
        "I need chiken karahi",
        
        # Problem 3: Partial orders (some valid, some invalid)
        "2 chicken pizza and 1 unknown_item",
        
        # Problem 4: Various quantity formats
        "three chicken pizza",
        "2x burger and 1 fries",
        "i want two 1x coke",
        
        # Problem 5: Implicit ordering
        "two pizzas and coke",
        "3 samosas please",
    ]
    
    print("=" * 80)
    print("TESTING FIXED NLP PARSER")
    print("=" * 80)
    
    for test_text in test_cases:
        result = parse_order(test_text, sample_menu)
        print(f"\n📝 Input: '{test_text}'")
        print(f"   Intent: {result['intent']}")
        print(f"   Items: {result['items']}")
        print(f"   Quantities: {result['quantities']}")
        print(f"   Confidence: {result['confidence']}")
        if result['unclear_items']:
            print(f"   ⚠️  UNCLEAR: {result['unclear_items']}")
        if result['needs_clarification']:
            print(f"   ⚠️  CLARIFICATION: {result['clarification_type']}")
            print(f"   Options: {result['available_options']}")
        print("-" * 80)

if __name__ == "__main__":
    test_nlp_parsing()