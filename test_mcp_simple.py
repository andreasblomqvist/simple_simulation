#!/usr/bin/env python3
"""
Simple test for MCP server - Claude API integration only
"""
import requests
import json
import os

# API key should be set as environment variable
# Example: export ANTHROPIC_API_KEY="your-api-key-here"

# MCP server URL
MCP_URL = "http://localhost:8100"

def test_mcp_simple():
    """Test the MCP server with a simple question"""
    
    # Simple test request
    test_request = {
        "question": "Hello Claude! Can you explain what an organizational simulation might be used for?",
        "simulation_params": {}  # Empty params so it doesn't try to run simulation
    }
    
    try:
        print("🚀 Testing MCP Server (Simple)...")
        print(f"📡 URL: {MCP_URL}/ask")
        print(f"❓ Question: {test_request['question']}")
        print("\n" + "="*50)
        
        # Make the request
        response = requests.post(
            f"{MCP_URL}/ask",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"🤖 Claude's Answer:\n{result.get('answer', 'No answer received')}")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Is the MCP server running on port 8100?")
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT ERROR: Request took too long")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_mcp_simple() 