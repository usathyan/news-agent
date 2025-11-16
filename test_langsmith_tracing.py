#!/usr/bin/env python3
"""
Simple test program to verify LangSmith tracing works.
Based on LangSmith getting started guide.
"""

import os
from dotenv import load_dotenv
from langsmith import traceable

# Load environment variables
load_dotenv()

# Enable LangSmith tracing
os.environ["LANGSMITH_TRACING"] = "true"


@traceable(name="test_function")
def test_traced_function(message: str) -> str:
    """A simple traced function."""
    print(f"Processing: {message}")
    result = message.upper()
    print(f"Result: {result}")
    return result


@traceable(name="test_workflow")
def main():
    """Main workflow with multiple traced calls."""
    print("Starting test workflow...")

    result1 = test_traced_function("hello world")
    result2 = test_traced_function("langsmith tracing")

    combined = f"{result1} + {result2}"
    print(f"Combined: {combined}")

    return combined


if __name__ == "__main__":
    print("=" * 70)
    print("LangSmith Tracing Test")
    print("=" * 70)
    print()

    # Check configuration
    api_key = os.getenv("LANGSMITH_API_KEY")
    project = os.getenv("LANGSMITH_PROJECT", "default")
    tracing = os.getenv("LANGSMITH_TRACING")

    print(f"Configuration:")
    print(f"  LANGSMITH_API_KEY: {'✓ Set' if api_key else '✗ Not set'}")
    print(f"  LANGSMITH_PROJECT: {project}")
    print(f"  LANGSMITH_TRACING: {tracing}")
    print()

    # Run the test
    result = main()

    print()
    print("=" * 70)
    print("Test Complete!")
    print("=" * 70)
    print()
    print(f"Check LangSmith dashboard for traces in project '{project}'")
    print(f"URL: https://smith.langchain.com/")
