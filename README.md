# MorphoStruct

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

**MorphoStruct** is an AI-powered scaffold design platform for bioprinting and tissue engineering research. It provides computational tools for generating anatomically-informed 3D scaffold geometries optimized for cell seeding, nutrient diffusion, and mechanical properties.

<p align="center">
  <img src="logo-text.svg" alt="MorphoStruct" width="400">
</p>

## Overview

Tissue engineering requires scaffolds with precise microarchitectures that support cell attachment, proliferation, and tissue formation. MorphoStruct combines parametric geometry generation with AI-assisted design to produce print-ready scaffold models for extrusion-based bioprinting, stereolithography, and other additive manufacturing techniques.

The platform supports **38 scaffold types** plus **27 geometric primitives** across 9 categories, each with research-validated geometric parameters and dynamic UI controls.

## Scaffold Categories

| Category | Types | Examples |
|----------|-------|----------|
| **Primitives** | 27 | Cylinder, torus, capsule, bifurcation, pore array, lattice cell |
| **Vascular** | 3 | Blood vessels, perfusable networks, vascular networks |
| **Skeletal** | 7 | Trabecular bone, cartilage, osteochondral interfaces, meniscus |
| **Organ-Specific** | 6 | Hepatic lobules, lung alveoli, kidney tubules, cardiac patch |
| **Tubular** | 5 | Nerve conduits, trachea, bladder, spinal cord |
| **Soft Tissue** | 4 | Multilayer skin, skeletal muscle, adipose, cornea |
| **Dental** | 3 | Dentin-pulp, ear auricle, nasal septum |
| **Microfluidic** | 3 | Organ-on-chip, gradient scaffolds, perfusable networks |
| **Advanced Lattice** | 5 | Gyroid, Schwarz-P, octet truss, Voronoi, honeycomb |

## Features

### AI-Assisted Design
Integrated LLM support (Anthropic Claude or OpenAI GPT) enables natural language scaffold specification. Describe your requirements and the system generates appropriate parameters.

### Real-Time 3D Visualization
Interactive Three.js viewport with orbit controls, cross-section views, and measurement tools. Preview scaffolds before committing to fabrication.

### Dynamic Parametric Controls
- **Shape-aware UI**: Controls adapt automatically based on selected geometry type
- **27 primitive shapes** organized by category (Basic, Geometric, Architectural, Organic)
- **Fast Preview Mode**: Lower resolution for rapid iteration
- **Invert Geometry**: Swap solid/void spaces for mold creation

### Parametric Control
Fine-grained control over:
- Porosity and pore size distribution
- Strut/wall thickness
- Surface area to volume ratio
- Mechanical anisotropy
- Gradient properties

### Primitive Shapes

| Category | Shapes |
|----------|--------|
| **Basic** | Cylinder, Sphere, Box, Cone |
| **Geometric** | Torus, Capsule, Pyramid, Wedge, Prism, Tube, Ellipsoid, Hemisphere |
| **Architectural** | Fillet, Chamfer, Slot, Counterbore, Countersink, Boss, Rib |
| **Organic** | Branch, Bifurcation, Pore, Channel, Fiber, Membrane, Lattice Cell, Pore Array |

### Export Options
- **STL Binary** - Compact format for slicers
- **STL ASCII** - Human-readable for debugging
- **OBJ** - With material definitions

### User Management
- Secure authentication
- Saved scaffold library
- Preference persistence
- API key management

## Installation

### Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- An LLM API key from [Anthropic](https://console.anthropic.com/) or [OpenAI](https://platform.openai.com/)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/rsiegemit/MorphoStruct.git
cd MorphoStruct

# Run the setup script
./morphostruct.sh install

# Start the application
./morphostruct.sh
```

The application will be available at http://localhost:3000

### Manual Installation

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

## Configuration

Copy the environment template and add your credentials:

```bash
cp backend/.env.example backend/.env
```

Required environment variables:
```
ANTHROPIC_API_KEY=sk-ant-...    # For Claude
OPENAI_API_KEY=sk-...           # For GPT (alternative)
SECRET_KEY=your-secret-key      # For JWT tokens
```

## Usage

### Starting the Servers

```bash
# Both servers (recommended)
./morphostruct.sh

# Individual servers
./morphostruct.sh backend    # API on port 8000
./morphostruct.sh frontend   # UI on port 3000
```

### API Endpoints

The backend exposes a REST API at `http://localhost:8000`:

- `POST /api/generate` - Generate scaffold geometry
- `POST /api/preview` - Quick preview mesh (faster, lower resolution)
- `GET /api/types` - List scaffold types
- `GET /api/primitives/list` - List available primitive shapes
- `GET /api/primitives/schema` - Get parameter schemas for all primitives
- `GET /api/primitives/schema/{name}` - Get schema for specific primitive
- `GET /api/scaffolds` - User's saved scaffolds
- `POST /api/export/{id}` - Export to STL/OBJ

Full API documentation available at `http://localhost:8000/docs`

## Project Structure

```
MorphoStruct/
├── backend/
│   ├── app/
│   │   ├── api/              # REST endpoints
│   │   ├── geometry/         # Scaffold generators
│   │   │   ├── primitives/   # 27 primitive shapes (geometric, architectural, organic)
│   │   │   ├── skeletal/     # Bone & cartilage scaffolds
│   │   │   ├── organ/        # Organ-specific scaffolds
│   │   │   └── lattice/      # TPMS & strut-based lattices
│   │   ├── llm/              # AI integration
│   │   └── models/           # Database models
│   └── requirements.txt
├── frontend/
│   ├── app/                  # Next.js pages
│   ├── components/
│   │   ├── controls/         # Parameter panels & dynamic controls
│   │   └── viewer/           # 3D viewport
│   └── lib/
│       ├── parameterMeta/    # UI metadata for all scaffold types
│       └── store/            # Zustand state management
├── morphostruct.sh           # Runner script
└── DOCUMENTATION.md          # Detailed documentation
```

## Documentation

See [DOCUMENTATION.md](DOCUMENTATION.md) for comprehensive technical documentation including:
- Scaffold type specifications
- Parameter reference
- API documentation
- Architecture overview

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes before submitting a pull request.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

Developed for tissue engineering research applications. Scaffold geometries are based on published biomaterials literature and anatomical references.
