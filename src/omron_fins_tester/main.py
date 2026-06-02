import sys
import os

# src klasörünü Python path'ine ekliyoruz ki absolute import'lar çalışsın
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from omron_fins_tester.gui.app import run_app
import logging

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run GUI application
    run_app()

if __name__ == "__main__":
    main()
