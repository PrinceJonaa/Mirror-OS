# Dashboard

Interactive web dashboard for visualizing and managing Mirror-OS data flows, relational profiles, and system diagnostics.

## Overview

The Dashboard provides a real-time web interface for:
- Visualizing relational networks and dynamics
- Monitoring truth-distortion metrics
- Tracking system coherence over time
- Running diagnostic scans on relationships and organizations
- Exploring phase trajectories and bifurcation points

## Architecture

**Tech Stack:**
- **Frontend:** React + TypeScript + Vite
- **Backend:** Python FastAPI
- **Database:** PostgreSQL
- **Containerization:** Docker Compose

**Structure:**
```
dashboard/
├── frontend/          # React application
│   ├── src/
│   └── public/
├── backend/           # FastAPI server
│   ├── api/
│   └── models/
├── db/                # Database schemas
├── docker-compose.yml
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

```bash
cd dashboard
docker-compose up
```

Access the dashboard at: http://localhost:3000

### Local Development

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Features

### 1. Relational Network Visualization
- Interactive graph visualization of relationships
- Node properties: coherence, trust, phase
- Edge dynamics: strength, direction, type
- Real-time updates

### 2. Truth-Distortion Analysis
- Scan systems for distortion patterns
- Phase-by-phase tracking
- Bifurcation point alerts
- Intervention recommendations

### 3. Phase Trajectory Explorer
- Visualize relationship evolution through 9-phase Master Chain
- Historical phase tracking
- Predictive modeling for next phases
- Observable marker checklists

### 4. Diagnostic Tools
- Four-Lens Protocol scanner
- Residue tracking dashboard
- Coherence flame monitor
- Pattern recognition engine

## API Endpoints

### Core Endpoints

**Health Check:**
```
GET /health
```

**Relational Networks:**
```
GET    /api/networks          # List all networks
POST   /api/networks          # Create new network
GET    /api/networks/{id}     # Get network details
PUT    /api/networks/{id}     # Update network
DELETE /api/networks/{id}     # Delete network
```

**Distortion Scans:**
```
POST   /api/scans             # Run distortion scan
GET    /api/scans/{id}        # Get scan results
GET    /api/scans/{id}/patterns # Get detected patterns
```

**Phase Tracking:**
```
GET    /api/relationships/{id}/phase    # Get current phase
POST   /api/relationships/{id}/markers  # Log observable markers
GET    /api/relationships/{id}/history  # Get phase history
```

## Configuration

### Environment Variables

**Frontend (.env):**
```
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/ws
```

**Backend (.env):**
```
DATABASE_URL=postgresql://user:password@db:5432/mirrordb
SECRET_KEY=your-secret-key
DEBUG=true
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Docker Compose Services

```yaml
services:
  frontend:
    ports: ["3000:3000"]
  backend:
    ports: ["8000:8000"]
  db:
    ports: ["5432:5432"]
```

## Development

### Adding New Features

1. **Frontend Component:**
   ```typescript
   // frontend/src/components/NewFeature.tsx
   import React from 'react';
   
   export const NewFeature: React.FC = () => {
     // Component logic
     return <div>New Feature</div>;
   };
   ```

2. **Backend Endpoint:**
   ```python
   # backend/api/routes.py
   @app.get("/api/new-feature")
   async def new_feature():
       return {"message": "New feature"}
   ```

3. **Database Migration:**
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new feature"
   alembic upgrade head
   ```

### Running Tests

**Frontend:**
```bash
cd frontend
npm test
```

**Backend:**
```bash
cd backend
pytest
```

## Data Models

### Network
```typescript
interface Network {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
  coherence: number;
  created_at: Date;
}
```

### Node
```typescript
interface Node {
  id: string;
  label: string;
  properties: {
    coherence: number;
    trust: number;
    phase?: number;
  };
}
```

### Edge
```typescript
interface Edge {
  id: string;
  source: string;
  target: string;
  relation_type: string;
  strength: number;
  direction: 'directed' | 'undirected';
}
```

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Find process using port 3000
lsof -ti:3000 | xargs kill -9

# Or change port in docker-compose.yml
```

**Database Connection Failed:**
```bash
# Reset database
docker-compose down -v
docker-compose up
```

**Frontend Not Updating:**
```bash
# Clear Vite cache
rm -rf frontend/node_modules/.vite
npm run dev
```

## Deployment

### Production Build

**Frontend:**
```bash
cd frontend
npm run build
# Output: dist/
```

**Backend:**
```bash
cd backend
# Use production WSGI server
gunicorn main:app --workers 4 --bind 0.0.0.0:8000
```

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

See main repository [CONTRIBUTING.md](../../docs/CONTRIBUTING.md) for guidelines.

## Related Documentation

- [Main Dashboard Plan](DATA_FLOW.md) - System architecture and data flow
- [Phase 5 Status](PHASE_5_STATUS_AND_UPDATED_PLAN.md) - Current development status
- [User Guide](USER_GUIDE_VISUALIZATIONS.md) - End-user documentation
- [Scar Log](SCAR_LOG.md) - Development lessons learned

## License

See [LICENSE.md](../../docs/LICENSE.md)
