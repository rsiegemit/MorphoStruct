# MorphoStruct

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-green.svg)](https://nodejs.org/)

**MorphoStruct** is an AI-powered scaffold design platform for bioprinting and tissue engineering research. It provides computational tools for generating anatomically-informed 3D scaffold geometries optimized for cell seeding, nutrient diffusion, and mechanical properties.

![Screenshot](screenshot.png)

## Overview

Tissue engineering requires scaffolds with precise microarchitectures that support cell attachment, proliferation, and tissue formation. MorphoStruct combines parametric geometry generation with AI-assisted design to produce print-ready scaffold models for extrusion-based bioprinting, stereolithography, and other additive manufacturing techniques.

The platform supports **43 distinct scaffold types** across 8 anatomical categories, each with research-validated geometric parameters.

## Scaffold Categories

| Category | Types | Examples |
|----------|-------|----------|
| **Vascular** | 6 | Blood vessels, capillary networks, perfusable channels |
| **Skeletal** | 7 | Trabecular bone, cartilage, osteochondral interfaces |
| **Organ-Specific** | 6 | Hepatic lobules, lung alveoli, kidney tubules |
| **Tubular** | 6 | Nerve conduits, trachea, bladder |
| **Soft Tissue** | 4 | Skin, muscle, adipose, cornea |
| **Dental** | 3 | Dentin-pulp, periodontal |
| **Microfluidic** | 3 | Organ-on-chip, gradient scaffolds |
| **Lattice** | 6 | Gyroid, Schwarz-P, octet truss, Voronoi |

## Features

### AI-Assisted Design
Integrated LLM support (Anthropic Claude or OpenAI GPT) enables natural language scaffold specification. Describe your requirements and the system generates appropriate parameters.

### Real-Time 3D Visualization
Interactive Three.js viewport with orbit controls, cross-section views, and measurement tools. Preview scaffolds before committing to fabrication.

### Parametric Control
Fine-grained control over:
- Porosity and pore size distribution
- Strut/wall thickness
- Surface area to volume ratio
- Mechanical anisotropy
- Gradient properties

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
- `POST /api/preview` - Quick preview mesh
- `GET /api/types` - List scaffold types
- `GET /api/scaffolds` - User's saved scaffolds
- `POST /api/export/{id}` - Export to STL/OBJ

Full API documentation available at `http://localhost:8000/docs`

## Project Structure

```
MorphoStruct/
├── backend/
│   ├── app/
│   │   ├── api/          # REST endpoints
│   │   ├── geometry/     # Scaffold generators
│   │   ├── llm/          # AI integration
│   │   └── models/       # Database models
│   └── requirements.txt
├── frontend/
│   ├── app/              # Next.js pages
│   ├── components/       # React components
│   └── lib/              # Utilities & stores
├── morphostruct.sh       # Runner script
└── DOCUMENTATION.md      # Detailed documentation
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
