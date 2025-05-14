#!/usr/bin/env python3
"""
Interactive dashboard for heat transfer simulation
"""

import sys
import os
# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from python.dashboard import HeatTransferDashboard

def main():
    print("Starting Heat Transfer Simulation Dashboard...")
    print("Open http://localhost:8050 in your browser")
    
    dashboard = HeatTransferDashboard()
    dashboard.run(host='0.0.0.0', port=8050, debug=True)

if __name__ == '__main__':
    main()
