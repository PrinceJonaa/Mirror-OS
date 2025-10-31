# Mirror-OS App

Main Mirror-OS application interface - TypeScript/React implementation of core Mirror-OS concepts and visualization tools.

## Overview

The Mirror-OS App provides an interactive interface for exploring and applying Mirror-OS framework principles through a modern web application.

## Structure

```
mirror-os-app/
├── index.html              # Entry point
├── index.tsx               # React root
├── package.json            # Dependencies
├── tsconfig.json           # TypeScript config
├── vite.config.ts          # Vite bundler config
├── types.ts                # Type definitions
├── metadata.json           # App metadata
├── src/                    # Source code
└── docs/                   # Documentation
```

## Quick Start

### Installation

```bash
cd apps/mirror-os-app
npm install
```

### Development

```bash
npm run dev
```

Access at: http://localhost:5173

### Build for Production

```bash
npm run build
# Output: dist/
```

## Features

- Interactive exploration of Mirror-OS concepts
- Visualization of lenses, lattices, and patterns
- Real-time relational analysis
- Integration with core Mirror-OS framework

## Documentation

See the `docs/` directory for detailed documentation:
- System architecture
- Component specifications
- Data flow diagrams
- Implementation roadmap
- AI collaboration protocol

## Related Apps

- **Dashboard** - Full-featured analytics dashboard ([../dashboard/](../dashboard/))
- **Relational Analyzer** - Core computation engine ([../relational-analyzer/](../relational-analyzer/))

## License

See [LICENSE.md](../../docs/LICENSE.md)
