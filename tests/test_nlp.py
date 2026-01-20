#!/usr/bin/env python3
"""
Test script for NLP functionality
This script tests the natural language processing capabilities of the restaurant ordering system.

Usage:
    python test_nlp.py
    python test_nlp.py --csv data/sample_orders.csv
    python test_nlp.py --interactive
"""

import sys
import argparse
import pandas as pd
from typing import List, Dict, Any
import json
from datetime import datetime

# Add the backend directory to Python path
sys.path.append('.')
sys.path.append('./backend')

try:
    from nlp import parse_order
    from firebase_client import firebase_client
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

class NLPTester:
    """Test suite for NLP functionality"""
    
    def __init__(self):
        self.sample_menu = [
            "Chicken Pizza", "Margherita Pizza", "Pepperoni Pizza",
            "Chicken Burger", "Beef Burger", "Fish Burger", "Veggie Burger",
            "Coke", "Pepsi", "Hot Tea", "Coffee", "Orange Juice",
            "French Fries", "Chicken Wings", "Samosa",
            "Chicken Biryani", "Chicken Karahi",
            "Ice Cream", "Chocolate Cake"
        ]
        
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "intent_accuracy": 0.0,
            "item_accuracy": 0.0,
            "quantity_accuracy": 0.0,
            "details": []
        }
    
    def test_basic_functionality(self):
        """Test basic NLP functionality"""
        print("Testing Basic NLP Functionality")
        print("=" * 50)
        
        test_cases = [
            {
                "text": "I want 2 chicken pizzas and 1 coke",
                "expected_intent": "order_food",
                "expected_items": ["Chicken Pizza", "Coke"],
                "expected_quantities": [2, 1]
            },
            {
                "text": "Show me the menu",
                "expected_intent": "show_menu",
                "expected_items": [],
                "expected_quantities": []
            },
            {
                "text": "Hello there",
                "expected_intent": "greeting", 
                "expected_items": [],
                "expected_quantities": []
            },
            {
                "text": "Cancel my order",
                "expected_intent": "cancel_order",
                "expected_items": [],
                "expected_quantities": []
            },
            {
                "text": "I need help",
                "expected_intent": "help",
                "expected_items": [],
                "expected_quantities": []
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}: {test_case['text']}")
            result = parse_order(test_case["text"], self.sample_menu)
            
            # Check results
            intent_correct = result["intent"] == test_case["expected_intent"]
            items_correct = set(result["items"]) == set(test_case["expected_items"])
            quantities_correct = result["quantities"] == test_case["expected_quantities"]
            
            print(f"  Expected Intent: {test_case['expected_intent']}")
            print(f"  Actual Intent:   {result['intent']} {'✅' if intent_correct else '❌'}")
            
            print(f"  Expected Items:  {test_case['expected_items']}")
            print(f"  Actual Items:    {result['items']} {'✅' if items_correct else '❌'}")
            
            print(f"  Expected Qty:    {test_case['expected_quantities']}")
            print(f"  Actual Qty:      {result['quantities']} {'✅' if quantities_correct else '❌'}")
            
            print(f"  Confidence:      {result['confidence']}")
            
            # Record results
            test_passed = intent_correct and items_correct and quantities_correct
            self.test_results["total_tests"] += 1
            if test_passed:
                self.test_results["passed"] += 1
                print("  Result: ✅ PASS")
            else:
                self.test_results["failed"] += 1
                print("  Result: ❌ FAIL")
            
            self.test_results["details"].append({
                "test_case": test_case["text"],
                "expected": test_case,
                "actual": result,
                "passed": test_passed,
                "intent_correct": intent_correct,
                "items_correct": items_correct,
                "quantities_correct": quantities_correct
            })
    
    def test_from_csv(self, csv_file: str):
        """Test NLP from CSV file"""
        print(f"Testing NLP from CSV file: {csv_file}")
        print("=" * 50)
        
        try:
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} test cases from CSV")
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return
        
        intent_correct_count = 0
        item_correct_count = 0
        quantity_correct_count = 0
        
        for index, row in df.iterrows():
            order_text = row['order_text']
            expected_intent = row['expected_intent']
            expected_items = row['expected_items'].split(',') if row['expected_items'] else []
            expected_quantities = [int(x) for x in row['expected_quantities'].split(',')] if row['expected_quantities'] else []
            
            # Clean up expected items (remove empty strings)
            expected_items = [item.strip() for item in expected_items if item.strip()]
            
            result = parse_order(order_text, self.sample_menu)
            
            # Check accuracy
            intent_correct = result["intent"] == expected_intent
            items_correct = set(result["items"]) == set(expected_items)
            quantities_correct = result["quantities"] == expected_quantities
            
            if intent_correct:
                intent_correct_count += 1
            if items_correct:
                item_correct_count += 1  
            if quantities_correct:
                quantity_correct_count += 1
            
            # Record detailed results
            test_passed = intent_correct and items_correct and quantities_correct
            self.test_results["total_tests"] += 1
            if test_passed:
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1
            
            self.test_results["details"].append({
                "test_case": order_text,
                "expected": {
                    "intent": expected_intent,
                    "items": expected_items, 
                    "quantities": expected_quantities
                },
                "actual": result,
                "passed": test_passed,
                "intent_correct": intent_correct,
                "items_correct": items_correct,
                "quantities_correct": quantities_correct
            })
            
            # Print progress every 10 tests
            if (index + 1) % 10 == 0:
                print(f"Processed {index + 1}/{len(df)} tests...")
        
        # Calculate accuracies
        total_tests = len(df)
        self.test_results["intent_accuracy"] = intent_correct_count / total_tests * 100
        self.test_results["item_accuracy"] = item_correct_count / total_tests * 100
        self.test_results["quantity_accuracy"] = quantity_correct_count / total_tests * 100
        
        print(f"\nCSV Test Results:")
        print(f"Intent Accuracy:    {self.test_results['intent_accuracy']:.1f}%")
        print(f"Item Accuracy:      {self.test_results['item_accuracy']:.1f}%")
        print(f"Quantity Accuracy:  {self.test_results['quantity_accuracy']:.1f}%")
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        print("\nTesting Edge Cases")
        print("=" * 50)
        
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "xyz abc def",  # Gibberish
            "I want 100 pizzas",  # Large quantity
            "Give me -2 burgers",  # Negative quantity (though regex won't catch this)
            "I want pizza burger coke tea samosa wings fries cake ice cream",  # Many items
            "piza burgar cok",  # Misspellings
            "I WANT PIZZA",  # All caps
            "i want pizza",  # All lowercase
            "I want... uh... maybe... pizza?",  # Hesitation
            "🍕🍔🥤",  # Emojis only
        ]
        
        for i, test_text in enumerate(edge_cases, 1):
            print(f"\nEdge Case {i}: '{test_text}'")
            try:
                result = parse_order(test_text, self.sample_menu)
                print(f"  Intent: {result['intent']}")
                print(f"  Items: {result['items']}")
                print(f"  Quantities: {result['quantities']}")
                print(f"  Confidence: {result['confidence']}")
                print("  Result: ✅ HANDLED")
            except Exception as e:
                print(f"  Error: {e}")
                print("  Result: ❌ ERROR")
    
    def interactive_test(self):
        """Interactive testing mode"""
        print("\nInteractive NLP Testing Mode")
        print("=" * 50)
        print("Enter natural language orders to test the NLP system.")
        print("Type 'quit' or 'exit' to stop.\n")
        
        while True:
            try:
                user_input = input("Enter order: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                result = parse_order(user_input, self.sample_menu)
                
                print(f"\n📋 Parse Result:")
                print(f"  Intent: {result['intent']}")
                print(f"  Items: {result['items']}")
                print(f"  Quantities: {result['quantities']}")
                print(f"  Confidence: {result['confidence']}")
                
                # Simulate order processing
                if result['intent'] == 'order_food' and result['items']:
                    total_price = 0
                    print(f"\n💰 Simulated Order:")
                    quantities = result['quantities'] if result['quantities'] else [1] * len(result['items'])
                    
                    for i, item in enumerate(result['items']):
                        qty = quantities[i] if i < len(quantities) else 1
                        # Dummy prices
                        price = 300 if 'pizza' in item.lower() else 250 if 'burger' in item.lower() else 100
                        item_total = price * qty
                        total_price += item_total
                        print(f"  {qty}x {item} @ ${price} = ${item_total}")
                    
                    print(f"  Total: ${total_price}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nGoodbye!")
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("NLP TESTING REPORT")
        print("=" * 60)
        
        total = self.test_results["total_tests"]
        passed = self.test_results["passed"]
        failed = self.test_results["failed"]
        
        if total > 0:
            success_rate = (passed / total) * 100
            
            print(f"Total Tests:        {total}")
            print(f"Passed:            {passed}")
            print(f"Failed:            {failed}")
            print(f"Success Rate:      {success_rate:.1f}%")
            
            if "intent_accuracy" in self.test_results and self.test_results["intent_accuracy"] > 0:
                print(f"Intent Accuracy:   {self.test_results['intent_accuracy']:.1f}%")
                print(f"Item Accuracy:     {self.test_results['item_accuracy']:.1f}%")
                print(f"Quantity Accuracy: {self.test_results['quantity_accuracy']:.1f}%")
            
            # Performance assessment
            if success_rate >= 90:
                print("📈 Performance: EXCELLENT")
            elif success_rate >= 80:
                print("📈 Performance: GOOD")
            elif success_rate >= 70:
                print("📈 Performance: ACCEPTABLE")
            else:
                print("📈 Performance: NEEDS IMPROVEMENT")
            
            # Recommendations
            print(f"\n💡 Recommendations:")
            if self.test_results.get("intent_accuracy", 0) < 85:
                print("  - Improve intent classification accuracy")
            if self.test_results.get("item_accuracy", 0) < 80:
                print("  - Enhance item extraction and fuzzy matching")
            if self.test_results.get("quantity_accuracy", 0) < 75:
                print("  - Better quantity parsing and number recognition")
            
            # Save detailed report to file
            self.save_detailed_report()
        else:
            print("No tests were run.")
    
    def save_detailed_report(self):
        """Save detailed test results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nlp_test_report_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
            print(f"📄 Detailed report saved to: {filename}")
        except Exception as e:
            print(f"❌ Failed to save report: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test NLP functionality for restaurant ordering system")
    parser.add_argument("--csv", help="Path to CSV file with test cases")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--basic", action="store_true", help="Run basic tests only")
    parser.add_argument("--edge", action="store_true", help="Run edge case tests only")
    
    args = parser.parse_args()
    
    tester = NLPTester()
    
    print("🤖 Smart Restaurant NLP Testing Suite")
    print("=" * 60)
    
    if args.interactive:
        tester.interactive_test()
    elif args.csv:
        tester.test_from_csv(args.csv)
        tester.generate_report()
    elif args.basic:
        tester.test_basic_functionality()
        tester.generate_report()
    elif args.edge:
        tester.test_edge_cases()
    else:
        # Run all tests
        tester.test_basic_functionality()
        tester.test_edge_cases()
        
        # Try to run CSV tests if file exists
        csv_file = "data/sample_orders.csv"
        try:
            tester.test_from_csv(csv_file)
        except:
            print(f"Could not load CSV file: {csv_file}")
        
        tester.generate_report()

if __name__ == "__main__":
    main()