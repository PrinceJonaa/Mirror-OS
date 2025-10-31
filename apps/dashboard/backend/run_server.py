#!/usr/bin/env python3
"""
Simplified backend server startup
"""
import sys
sys.path.insert(0, '/Users/princejona/a1/dashboard/backend')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
