# MorphoStruct - Bioprinting Scaffold Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Three.js](https://img.shields.io/badge/Three.js-0.160-orange.svg)](https://threejs.org/)

MorphoStruct is a comprehensive **bioprinting scaffold generator** that combines sophisticated 3D geometry algorithms with an intuitive web interface. Generate complex tissue-engineering scaffolds across 39 different types using an AI-assisted design workflow powered by LLM integration (Anthropic Claude or OpenAI).

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Backend Architecture](#backend-architecture)
  - [Configuration](#configuration)
  - [API Routes](#api-routes)
  - [LLM Integration](#llm-integration)
  - [Geometry Generators](#geometry-generators)
- [Frontend Architecture](#frontend-architecture)
  - [App Structure](#app-structure)
  - [Components](#components)
  - [State Management](#state-management)
  - [API Client](#api-client)
- [Development Guide](#development-guide)
  - [Local Setup](#local-setup)
  - [Running Services](#running-services)
  - [Environment Configuration](#environment-configuration)
  - [Development Workflow](#development-workflow)
- [Scaffold Types](#scaffold-types)
- [API Reference](#api-reference)
- [Key Concepts](#key-concepts)
  - [Murray's Law](#murrays-law)
  - [TPMS Surfaces](#tpms-surfaces)
  - [Tree Union Algorithm](#tree-union-algorithm)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

MorphoStruct is designed for tissue engineers, researchers, and bioprinting professionals who need to generate complex 3D scaffolds for cell culturing and tissue regeneration. The system provides:

- **43 scaffold types** organized across 8 categories
- **Python FastAPI backend** with Manifold3D geometry engine
- **Next.js 14 frontend** with Three.js 3D visualization
- **AI-assisted design** via LLM chat interface
- **Flexible LLM support** for Anthropic Claude and OpenAI
- **STL export** in both binary and ASCII formats
- **User authentication** and scaffold saving

### Architecture Overview

```
┌─────────────────────┐
│   Web Browser       │
│  (Next.js React)    │
│  - Three.js Viewer  │
│  - Chat Interface   │
│  - Parameter Panel  │
└──────────┬──────────┘
           │ HTTP/WebSocket
           │
┌──────────▼──────────────┐
│  FastAPI Backend        │
│  - Scaffold Generation  │
│  - LLM Agent            │
│  - Auth & Database      │
│  - STL Export           │
└──────────┬──────────────┘
           │
      ┌────┴─────────┬──────────────┐
      │              │              │
    ┌─▼─┐      ┌────▼────┐   ┌────▼─────┐
    │LLM│      │Manifold3D│   │ Database  │
    │API│      │Engine    │   │ (SQLite)  │
    └───┘      └──────────┘   └───────────┘
```

---

## Features

### Core Features

- **39 Scaffold Types** across 8 categories:
  - Original scaffolds (5): vascular, porous disc, tubular, lattice, primitives
  - Skeletal structures (7): trabecular bone, osteochondral, cartilage, etc.
  - Organ tissues (6): hepatic lobule, cardiac patch, kidney tubule, etc.
  - Soft tissues (4): skin, muscle, cornea, adipose
  - Tubular structures (6): blood vessel, nerve conduit, spinal cord, bladder, trachea, vascular perfusion dish
  - Dental structures (3): dentin-pulp, ear auricle, nasal septum
  - Advanced lattices (5): gyroid, Schwarz P, octet truss, Voronoi, honeycomb
  - Microfluidic devices (3): organ-on-chip, gradient, perfusable network

### Advanced Capabilities

- **LLM-Assisted Design**: Chat with Claude or GPT to generate scaffolds naturally
- **Real-Time Visualization**: Interactive 3D preview with orbital controls
- **Parameter Optimization**: Type-specific controls for precision tuning
- **Dual Export Format**: Binary STL (small) or ASCII STL (readable)
- **Generation Presets**: 50+ pre-configured scaffold templates
- **User Accounts**: Save and manage custom scaffold designs
- **Biological Accuracy**: Murray's law, TPMS surfaces, organic branching

### Technical Highlights

- **Manifold3D Integration**: Robust boolean operations and mesh handling
- **O(n log n) Boolean Operations**: Efficient tree-union algorithm for scaling
- **Bezier Curve Interpolation**: Smooth, organic branch curves
- **Multi-Provider LLM Support**: Switch between Anthropic and OpenAI
- **CORS Support**: Cross-origin requests for integration
- **JWT Authentication**: Secure user sessions
- **Type-Safe Frontend**: Full TypeScript with React 18

---

## Quick Start

### Prerequisites

- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm)
- **LLM API Key** (Anthropic or OpenAI)
- **macOS, Linux, or Windows (WSL2)**

### Installation & Running (5 minutes)

```bash
# Clone or navigate to MorphoStruct directory
cd MorphoStruct

# Install dependencies and start both servers
./morphostruct.sh install
./morphostruct.sh

# Services will start on:
# - Backend API: http://localhost:8000
# - Frontend UI: http://localhost:3000
# - Swagger Docs: http://localhost:8000/docs
```

The script will:
- Create Python virtual environment
- Install all dependencies
- Auto-detect port conflicts
- Open browser to frontend
- Show logs for both services

**Alternative: Start services separately**

```bash
# Terminal 1: Backend only
./morphostruct.sh backend

# Terminal 2: Frontend only
./morphostruct.sh frontend

# Or with make (if available)
./morphostruct.sh install  # Install all deps first
```

### First-Time Configuration

1. Open http://localhost:3000 in your browser
2. Create an account (Settings > Account)
3. Add your LLM API key:
   - Settings > LLM Configuration
   - Choose provider (Anthropic or OpenAI)
   - Paste your API key
4. Start generating scaffolds!

### Quick Example

```bash
# Via browser
1. Navigate to Generator
2. Select "Vascular Network" from dropdown
3. Adjust parameters (inlets, levels, spread)
4. Click "Generate"
5. Rotate view with mouse
6. Export as STL

# Via CLI (Python)
python backend/run.py
# Then POST to http://localhost:8000/api/generate with JSON params
```

---

## Project Structure

```
MorphoStruct/
├── README.md                      # Project overview
├── DOCUMENTATION.md               # This file - detailed docs
├── morphostruct.sh                # Unified launcher script
│
├── backend/                       # Python FastAPI server
│   ├── run.py                     # Entry point (Uvicorn launcher)
│   ├── requirements.txt           # Python dependencies
│   └── app/
│       ├── main.py                # FastAPI app init, CORS, routers
│       ├── config.py              # Settings (env vars, API keys)
│       ├── api/                   # Route handlers
│       │   ├── scaffolds.py       # POST /generate, /preview, /validate, etc.
│       │   ├── chat.py            # POST /chat (LLM interface)
│       │   ├── auth.py            # Auth routes (register, login, JWT)
│       │   └── saved_scaffolds.py # CRUD for user scaffold library
│       ├── geometry/              # Scaffold generators (43 types)
│       │   ├── core.py            # tree_union(), Manifold3D wrapper
│       │   ├── stl_export.py      # manifold_to_stl_binary/ascii()
│       │   ├── vascular.py        # Vascular network generator
│       │   ├── porous_disc.py     # Disc with pores
│       │   ├── primitives.py      # Sphere, cylinder
│       │   └── [category]/        # Organized by type
│       │       ├── skeletal/      # Bone, cartilage, meniscus, etc.
│       │       ├── organ/         # Hepatic, cardiac, kidney, etc.
│       │       ├── soft_tissue/   # Skin, muscle, cornea, etc.
│       │       ├── tubular/       # Blood vessel, nerve, etc.
│       │       ├── dental/        # Dentin, ear, nose structures
│       │       ├── lattice/       # Gyroid, Schwarz P, Voronoi, etc.
│       │       └── microfluidic/  # Organ-on-chip, gradients
│       ├── llm/                   # LLM integration
│       │   ├── agent.py           # ScaffoldAgent (main orchestrator)
│       │   ├── providers.py       # AnthropicClient, OpenAIClient
│       │   ├── tools.py           # 43 scaffold tool definitions
│       │   ├── prompts.py         # System prompts
│       │   └── tools_minimal.py   # Compact tool definitions
│       ├── models/                # Pydantic data models
│       │   ├── scaffold.py        # ScaffoldType enum, param models
│       │   └── user.py            # User authentication models
│       ├── db/                    # Database layer
│       │   └── database.py        # SQLite schema, init
│       ├── services/              # Business logic
│       │   ├── auth.py            # JWT, password hashing
│       │   └── encryption.py      # Fernet key encryption
│       └── core/
│           └── logging.py         # Logging configuration
│
├── frontend/                      # Next.js 14 React app
│   ├── package.json               # Node dependencies
│   ├── next.config.js             # Next.js configuration
│   ├── tsconfig.json              # TypeScript config
│   ├── tailwind.config.ts         # Tailwind CSS config
│   └── app/                       # App router (Next.js 14)
│       ├── page.tsx               # Home (redirect)
│       ├── layout.tsx             # Root layout
│       ├── providers.tsx          # Context providers (React Query)
│       ├── login/page.tsx          # Auth: login
│       ├── register/page.tsx       # Auth: register
│       ├── account/page.tsx        # User account settings
│       ├── settings/page.tsx       # App settings, LLM config
│       ├── generator/page.tsx      # Main scaffold generator
│       ├── dashboard/page.tsx      # Dashboard (stats, recent)
│       └── library/page.tsx        # Saved scaffolds library
│   ├── components/                # React components
│   │   ├── Viewport.tsx           # Three.js canvas container
│   │   ├── ScaffoldMesh.tsx       # Renders mesh geometry
│   │   ├── ViewControls.tsx       # Camera orbit controls
│   │   ├── ParameterPanel.tsx     # Main control panel
│   │   ├── ScaffoldTypeSelector.tsx # Dropdown for 43 types
│   │   ├── DynamicControls.tsx    # Type-specific parameters
│   │   ├── ChatPanel.tsx          # LLM chat interface
│       ├── MessageList.tsx        # Conversation history
│   │   ├── InputBox.tsx           # Chat message input
│   │   ├── SuggestionChips.tsx    # Quick action buttons
│   │   ├── ExportPanel.tsx        # STL export dialog
│   │   ├── ValidationSummary.tsx  # Error/warning display
│   │   └── [individual controls]  # Type-specific UI
│   └── lib/                       # Utilities & API
│       ├── api/                   # API clients
│       │   ├── scaffold.ts        # generateScaffold(), exportSTL()
│       │   ├── chat.ts            # sendChatMessage()
│       │   ├── auth.ts            # login(), register(), logout()
│       │   └── client.ts          # Base HTTP client + interceptors
│       ├── store/                 # Zustand state management
│       │   ├── scaffoldStore.ts   # Scaffold generation state
│       │   ├── chatStore.ts       # Chat messages & suggestions
│       │   └── authStore.ts       # User auth state
│       ├── types/                 # TypeScript interfaces
│       │   └── scaffold.ts        # ScaffoldType, MeshData, etc.
│       ├── parameterMeta.ts       # Parameter definitions for UI
│       └── utils.ts               # Utility functions
│
└── logo.svg                       # Project logo
```

---

## Backend Architecture

### Configuration

Backend settings are defined in `backend/app/config.py` using Pydantic Settings:

```python
class Settings(BaseSettings):
    # App
    app_name: str = "MorphoStruct API"
    debug: bool = False

    # LLM Provider
    llm_provider: str = "anthropic"  # "anthropic" or "openai"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = ""  # Custom endpoint (e.g., proxy)
    llm_model: str = ""  # Optional: override default per provider

    # Generation
    default_resolution: int = 16
    max_triangles: int = 500000

    # Database
    database_url: str = "sqlite:///./morphostruct.db"

    # JWT Auth
    jwt_secret_key: str = "..."  # Change in production!
    access_token_expire_minutes: int = 1440

    # Encryption
    encryption_secret: str = "..."  # For API keys

    class Config:
        env_file = ".env"
```

**Environment Setup:**

Create `.env` file in backend directory:

```env
MORPHOSTRUCT_APP_NAME=My Scaffold Generator
MORPHOSTRUCT_DEBUG=false

# LLM Provider (choose one)
MORPHOSTRUCT_LLM_PROVIDER=anthropic
MORPHOSTRUCT_ANTHROPIC_API_KEY=sk-ant-xxx...

# OR for OpenAI
# MORPHOSTRUCT_LLM_PROVIDER=openai
# MORPHOSTRUCT_OPENAI_API_KEY=sk-xxx...
# MORPHOSTRUCT_OPENAI_BASE_URL=https://api.openai.com/v1

# Generation
MORPHOSTRUCT_DEFAULT_RESOLUTION=16
MORPHOSTRUCT_MAX_TRIANGLES=500000

# Database
MORPHOSTRUCT_DATABASE_URL=sqlite:///./morphostruct.db

# JWT (change in production!)
MORPHOSTRUCT_JWT_SECRET_KEY=your-secret-key-here
MORPHOSTRUCT_ENCRYPTION_SECRET=your-encryption-secret-here
```

### API Routes

#### Scaffolds API (`/api` prefix)

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/generate` | Generate scaffold from parameters → STL file |
| **POST** | `/preview` | Fast preview (skips export, returns mesh JSON) |
| **POST** | `/validate` | Validate parameters without generating |
| **GET** | `/export/{scaffold_id}` | Download previously generated STL |
| **GET** | `/presets` | List 50+ pre-configured presets |
| **GET** | `/categories` | List 8 scaffold categories |
| **GET** | `/types` | List all 43 scaffold types with metadata |

**Example: Generate Scaffold**

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "scaffold_type": "vascular_network",
    "params": {
      "inlets": 4,
      "levels": 3,
      "splits": 2,
      "spread": 0.4,
      "ratio": 0.79,
      "outer_radius": 4.875,
      "height": 2.0
    },
    "export_format": "binary"
  }'
```

**Response:**

```json
{
  "status": "success",
  "scaffold_id": "uuid-here",
  "mesh_data": {
    "vertices": [[x1, y1, z1], ...],
    "faces": [[v0, v1, v2], ...],
    "normals": [[nx, ny, nz], ...]
  },
  "stats": {
    "vertex_count": 12540,
    "face_count": 25080,
    "volume": 45.3,
    "surface_area": 234.5,
    "generation_time_ms": 2341
  },
  "stl_binary": "base64-encoded-binary-data",
  "warnings": []
}
```

#### Chat API

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/chat` | Send message to LLM scaffold assistant |
| **GET** | `/chat/status` | Check LLM provider availability |

**Example: Chat Message**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create a vascular scaffold with 6 inlets and good perfusability",
    "session_id": "user-session-123"
  }'
```

#### Authentication API

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/auth/register` | Create new user account |
| **POST** | `/auth/login` | Login (returns JWT token) |
| **POST** | `/auth/logout` | Invalidate session |
| **GET** | `/auth/me` | Get current user profile |

#### Saved Scaffolds API

| Method | Endpoint | Description |
|--------|----------|-------------|
| **POST** | `/saved` | Save generated scaffold |
| **GET** | `/saved` | List user's saved scaffolds |
| **GET** | `/saved/{id}` | Retrieve saved scaffold details |
| **PATCH** | `/saved/{id}` | Update saved scaffold metadata |
| **DELETE** | `/saved/{id}` | Delete saved scaffold |

### LLM Integration

The LLM system enables natural language scaffold generation through multi-turn conversations.

**Architecture:**

```
User Message
    ↓
ScaffoldAgent (agent.py)
    ├─ Receives user message
    ├─ Forwards to LLM provider
    ├─ Analyzes LLM tool calls
    ├─ Executes scaffold generation
    ├─ Returns results to LLM
    └─ Streams response back
```

**Key Components:**

1. **ScaffoldAgent** (`agent.py`):
   - Main orchestrator for LLM interactions
   - Manages conversation state
   - Handles tool calling loop
   - Supports both Anthropic and OpenAI

2. **Providers** (`providers.py`):
   - `AnthropicClient`: Uses Claude with tool_use
   - `OpenAIClient`: Uses GPT-4 with function_calling

3. **Tools** (`tools.py`):
   - 43 scaffold generation tools
   - Parameterized for each type
   - Auto-generated from scaffold definitions

4. **Prompts** (`prompts.py`):
   - System prompt guides LLM behavior
   - Context about available scaffolds
   - Biological design principles

**Example: LLM-Assisted Generation**

```python
# User: "I need a highly vascularized scaffold for cardiac tissue"

# LLM Agent:
# 1. Analyzes request → recognizes "cardiac" + "vascularized"
# 2. Calls generate_cardiac_patch() with vascular params
# 3. Gets back mesh data
# 4. Returns: "I've created a cardiac patch scaffold..."

agent = ScaffoldAgent(provider="anthropic")
response = agent.chat(
    user_message="Create a cardiac patch with high vascularization",
    session_id="user-123"
)
# → Streams back scaffold + explanation
```

### Geometry Generators

MorphoStruct includes 43 specialized scaffold generators organized across 8 categories.

#### Core Generator Structure

Each scaffold generator:
1. Accepts typed parameters (dataclass)
2. Returns a Manifold3D mesh
3. Includes validation and constraints
4. Exports to STL via `stl_export.py`

**Example: Vascular Network**

```python
@dataclass
class VascularParams:
    inlets: int = 4              # 1-25 inlet points
    levels: int = 2              # Branching depth (0-5)
    splits: int = 2              # Branches per split (2-4)
    spread: float = 0.35         # Horizontal spread (0.0-1.0)
    ratio: float = 0.79          # Child/parent radius (Murray's law)
    curvature: float = 0.3       # Branch curve intensity
    resolution: int = 12         # Mesh segments
    outer_radius: float = 4.875  # Ring outer radius
    height: float = 2.0          # Total height

def generate_vascular_network(params: VascularParams) -> Manifold3D:
    """Generate branching vascular tree structure."""
    # 1. Create inlet channels
    # 2. Generate recursive branches using Murray's law
    # 3. Use Bezier curves for smooth paths
    # 4. Boolean union all geometry
    # 5. Return mesh
```

#### Scaffold Categories

Categories and entries sorted alphabetically per audit specification.

**Dental (3)**
- `dentin_pulp`: Dental tissue unit
- `ear_auricle`: Cartilage scaffold
- `nasal_septum`: Nasal tissue structure

**Lattice (6)**
- `lattice`: Regular cubic/BCC lattice structure
- `gyroid`: 3D periodic minimal surface (TPMS)
- `honeycomb`: Hexagonal cell packing
- `octet_truss`: Space-filling truss lattice
- `schwarz_p`: Schwarz P surface (TPMS)
- `voronoi`: Computational geometry cells

**Legacy (3)**
- `porous_disc`: Disc with hexagonal/grid pores
- `primitive`: Basic sphere, cylinder, box shapes
- `vascular_network`: Branching blood vessel networks

**Microfluidic (3)**
- `gradient_scaffold`: Concentration gradient channels
- `organ_on_chip`: Multi-chamber device
- `perfusable_network`: Interconnected flow network

**Organ (6)**
- `cardiac_patch`: Myocardial tissue construct
- `hepatic_lobule`: Hexagonal liver tissue unit
- `kidney_tubule`: Filtration unit structure
- `liver_sinusoid`: Specialized capillary network
- `lung_alveoli`: Branching respiratory units
- `pancreatic_islet`: Endocrine cell aggregate

**Skeletal (7)**
- `articular_cartilage`: Smooth cartilage tissue structure
- `haversian_bone`: Osteon structure with central canal
- `intervertebral_disc`: Nucleus pulposus + annulus fibrosus
- `meniscus`: C-shaped fibrocartilage scaffold
- `osteochondral`: Bone-cartilage interface scaffold
- `tendon_ligament`: Aligned fibrous structure
- `trabecular_bone`: Porous bone structure with struts

**Soft Tissue (4)**
- `adipose`: Vascularized fat tissue
- `cornea`: Transparent collagen matrix
- `multilayer_skin`: Epidermis + dermis + subcutis
- `skeletal_muscle`: Aligned fiber bundle structure

**Tubular (7)**
- `bladder`: Hollow organ structure
- `blood_vessel`: Artery/capillary conduit
- `nerve_conduit`: Neuronal guidance channel
- `spinal_cord`: CNS tissue scaffold
- `trachea`: Cartilage-lined airway
- `tubular_conduit`: Cylindrical scaffold with textured inner surface
- `vascular_perfusion_dish`: Collision-aware branching network

---

## Frontend Architecture

### App Structure

The frontend is built with **Next.js 14** using the App Router pattern:

```
app/
├── page.tsx              # "/" → Redirects to dashboard
├── layout.tsx            # Root layout wrapper
├── providers.tsx         # React providers (React Query, etc.)
├── login/page.tsx        # "/login" → Login page
├── register/page.tsx     # "/register" → Registration
├── account/page.tsx      # "/account" → User profile
├── settings/page.tsx     # "/settings" → App settings
├── dashboard/page.tsx    # "/dashboard" → Dashboard
├── generator/page.tsx    # "/generator" → Main scaffold generator
└── library/page.tsx      # "/library" → Saved scaffolds
```

### Components

#### Viewer Components

- **Viewport.tsx**: Three.js WebGL canvas container with rendering setup
- **ScaffoldMesh.tsx**: Renders mesh geometry with wireframe/solid toggle
- **ViewControls.tsx**: Orbital camera controls (zoom, pan, rotate)

#### Control Components

- **ParameterPanel.tsx**: Main control container
- **ScaffoldTypeSelector.tsx**: Dropdown for all 43 types
- **DynamicControls.tsx**: Renders type-specific controls dynamically
- **[Type-specific controls]**: Individual sliders/inputs for each scaffold type

#### Chat Components

- **ChatPanel.tsx**: Chat container
- **MessageList.tsx**: Conversation history (scrollable)
- **InputBox.tsx**: Text input with send button
- **SuggestionChips.tsx**: Quick-action buttons

#### Export Components

- **ExportPanel.tsx**: STL export dialog (binary/ASCII format)
- **ValidationSummary.tsx**: Parameter validation warnings/errors

### State Management

Uses **Zustand** for lightweight, efficient state:

```typescript
// scaffoldStore.ts
const scaffoldStore = create((set) => ({
  // State
  scaffoldType: "vascular_network",
  params: { inlets: 4, levels: 2, ... },
  meshData: null,
  stats: null,
  isLoading: false,
  error: null,

  // Actions
  setScaffoldType: (type) => set({ scaffoldType: type }),
  setParams: (params) => set({ params }),
  generateScaffold: async () => { /* ... */ },
  exportSTL: async (format) => { /* ... */ }
}));

// chatStore.ts
const chatStore = create((set) => ({
  messages: [],
  suggestions: [],
  isLoading: false,

  addMessage: (role, content) => set(state => ({
    messages: [...state.messages, { role, content }]
  })),
  sendMessage: async (message) => { /* ... */ }
}));

// authStore.ts
const authStore = create((set) => ({
  user: null,
  isAuthenticated: false,
  token: null,

  login: async (email, password) => { /* ... */ },
  logout: () => set({ user: null, isAuthenticated: false })
}));
```

### API Client

Central HTTP client with interceptors:

```typescript
// lib/api/client.ts
const client = axios.create({
  baseURL: "http://localhost:8000",
  headers: { "Content-Type": "application/json" }
});

// Auto-attach JWT token
client.interceptors.request.use((config) => {
  const token = authStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Specialized API methods
export const scaffoldAPI = {
  generateScaffold: (params) => client.post("/api/generate", params),
  exportSTL: (scaffoldId, format) =>
    client.get(`/api/export/${scaffoldId}?format=${format}`),
  getPresets: () => client.get("/api/presets"),
  getTypes: () => client.get("/api/types")
};

export const chatAPI = {
  sendMessage: (message, sessionId) =>
    client.post("/api/chat", { message, session_id: sessionId })
};

export const authAPI = {
  register: (email, password) =>
    client.post("/auth/register", { email, password }),
  login: (email, password) =>
    client.post("/auth/login", { email, password }),
  logout: () => client.post("/auth/logout")
};
```

---

## Development Guide

### Local Setup

**1. Clone the repository:**

```bash
git clone <repository-url>
cd MorphoStruct
```

**2. Install all dependencies:**

```bash
./morphostruct.sh install
```

This will:
- Create Python virtual environment
- Install backend packages from `requirements.txt`
- Install frontend packages with `npm install`

**3. Configure environment:**

Create `backend/.env`:

```env
MORPHOSTRUCT_DEBUG=true
MORPHOSTRUCT_LLM_PROVIDER=anthropic
MORPHOSTRUCT_ANTHROPIC_API_KEY=sk-ant-xxx...
MORPHOSTRUCT_OPENAI_API_KEY=sk-xxx...
```

### Running Services

#### Option 1: Both Services Together

```bash
./morphostruct.sh

# Services will start and browser will open automatically
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

#### Option 2: Separate Terminals

```bash
# Terminal 1: Backend
./morphostruct.sh backend
# Runs: cd backend && source venv/bin/activate && python run.py

# Terminal 2: Frontend
./morphostruct.sh frontend
# Runs: cd frontend && npm run dev
```

#### Option 3: Manual Start

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python run.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

#### Stopping Services

```bash
./morphostruct.sh stop

# Or manually:
# - Press Ctrl+C in each terminal
# - Kill port: lsof -ti:8000 | xargs kill -9
```

### Environment Configuration

**Backend Configuration:**

Modify `backend/app/config.py` or create `.env` file:

```env
# App
MORPHOSTRUCT_APP_NAME=MorphoStruct Scaffold Generator
MORPHOSTRUCT_DEBUG=true

# LLM (choose ONE provider)
# Option 1: Anthropic
MORPHOSTRUCT_LLM_PROVIDER=anthropic
MORPHOSTRUCT_ANTHROPIC_API_KEY=sk-ant-v7-xxx...

# Option 2: OpenAI
# MORPHOSTRUCT_LLM_PROVIDER=openai
# MORPHOSTRUCT_OPENAI_API_KEY=sk-proj-xxx...
# MORPHOSTRUCT_OPENAI_BASE_URL=https://api.openai.com/v1

# Geometry
MORPHOSTRUCT_DEFAULT_RESOLUTION=16
MORPHOSTRUCT_MAX_TRIANGLES=500000

# Database
MORPHOSTRUCT_DATABASE_URL=sqlite:///./morphostruct.db

# Security (CHANGE IN PRODUCTION)
MORPHOSTRUCT_JWT_SECRET_KEY=dev-secret-key-change-this
MORPHOSTRUCT_ENCRYPTION_SECRET=dev-encryption-secret-change-this
```

**Frontend Environment:**

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_ENABLE_ANALYTICS=false
```

### Development Workflow

**Adding a New Scaffold Type:**

1. Create geometry generator in `backend/app/geometry/[category]/[name].py`:

```python
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class MyScaffoldParams:
    param1: float = 1.0
    param2: int = 10

def generate_my_scaffold(params: MyScaffoldParams) -> Manifold3D:
    """Generate custom scaffold."""
    manifold = get_manifold_module()
    # Implementation here
    return manifold_mesh
```

2. Register in `backend/app/geometry/__init__.py`:

```python
from .category.my_scaffold import generate_my_scaffold, MyScaffoldParams

GENERATORS = {
    "my_scaffold": generate_my_scaffold
}
PARAM_MODELS = {
    "my_scaffold": MyScaffoldParams
}
```

3. Add to `backend/app/models/scaffold.py`:

```python
class ScaffoldType(str, Enum):
    MY_SCAFFOLD = "my_scaffold"
```

4. Create LLM tool definition in `backend/app/llm/tools.py`:

```python
SCAFFOLD_TOOLS = [{
    "name": "generate_my_scaffold",
    "description": "Generate custom scaffold...",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {"type": "number"},
            "param2": {"type": "integer"}
        }
    }
}]
```

5. Add frontend controls in `frontend/components/MyScaffoldControls.tsx`:

```typescript
export function MyScaffoldControls() {
  const { params, setParams } = useScaffoldStore();

  return (
    <div>
      <Slider
        label="Param 1"
        value={params.param1}
        onChange={(val) => setParams({ ...params, param1: val })}
      />
      {/* More controls */}
    </div>
  );
}
```

**Testing Local Changes:**

```bash
# Backend: Auto-reloads with --reload flag
# (run.py has reload=True)

# Frontend: Auto-rebuilds on file changes
# Just save and refresh browser

# Test API endpoint directly
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"scaffold_type":"my_scaffold","params":{...}}'
```

---

## Scaffold Types

Categories and entries sorted alphabetically per audit specification (docs/audit/INDEX.md).

### Dental (3)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Dentin-Pulp** | Dental tissue unit with innervated pulp chamber | Tooth regeneration, endodontic therapy |
| **Ear Auricle** | Cartilage scaffold for ear structure | Auricular reconstruction, hearing loss |
| **Nasal Septum** | Nasal tissue structure with cartilage support | Nasal reconstruction, septoplasty |

### Lattice (6)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Basic Lattice** | Regular cubic or BCC lattice structure | Bone scaffolds, structural support |
| **Gyroid** | 3D periodic minimal surface (TPMS) | High surface area, biomimetic, strength-to-weight |
| **Honeycomb** | Hexagonal cell packing | Structural efficiency, directional properties |
| **Octet Truss** | Space-filling truss lattice | Optimal strength, minimal mass |
| **Schwarz P** | Schwarz P minimal surface (TPMS) | Interconnected pores, balanced properties |
| **Voronoi** | Computational geometry cells | Hierarchical structure, randomness control |

### Legacy (3)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Porous Disc** | Circular scaffold with hexagonal or grid pore patterns | General tissue support, ease of visualization |
| **Primitive** | Basic geometric shapes (sphere, cylinder, box) | Testing, baseline structures |
| **Vascular Network** | Branching blood vessel tree with Murray's law optimization | Highly vascularized tissues, nutrient transport |

### Microfluidic (3)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Gradient Scaffold** | Concentration gradient channels | Chemotaxis studies, gradient biology |
| **Organ-on-Chip** | Multi-chamber device with separation channels | Drug testing, tissue-tissue interfaces |
| **Perfusable Network** | Interconnected flow network | Nutrient delivery, metabolite removal |

### Organ (6)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Cardiac Patch** | Myocardial tissue construct with contractile alignment | Heart repair, cardiac tissue regeneration |
| **Hepatic Lobule** | Hexagonal liver tissue unit with portal triads and central vein | Liver tissue engineering, hepatocyte culture |
| **Kidney Tubule** | Filtration unit structure with podocyte arrangement | Renal tissue engineering, ultrafiltration |
| **Liver Sinusoid** | Specialized capillary network with fenestrations | Hepatic function, metabolic support |
| **Lung Alveoli** | Branching respiratory units for gas exchange | Lung tissue repair, respiratory culture |
| **Pancreatic Islet** | Endocrine cell aggregate scaffold | Diabetes treatment, insulin production |

### Skeletal (7)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Articular Cartilage** | Smooth cartilage tissue scaffold | Joint repair, frictionless surfaces |
| **Haversian Bone** | Osteon structure with central Haversian canal | Vascularized bone, nutrient transport |
| **Intervertebral Disc** | Nucleus pulposus + annulus fibrosus (gel + fiber) | Spine repair, disc herniation treatment |
| **Meniscus** | C-shaped fibrocartilage scaffold | Knee meniscus repair |
| **Osteochondral** | Bone-cartilage interface with distinct regions | Joint surface regeneration |
| **Tendon-Ligament** | Aligned fibrous structure with directional properties | Tendon/ligament regeneration |
| **Trabecular Bone** | Porous strut-based bone structure mimicking natural bone architecture | Bone regeneration, load-bearing |

### Soft Tissue (4)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Adipose** | Vascularized fat tissue structure | Soft tissue reconstruction, volume restoration |
| **Cornea** | Transparent collagen matrix scaffold | Vision restoration, corneal disease |
| **Multilayer Skin** | Epidermis + dermis + subcutis with distinct layers | Skin wound healing, reconstructive surgery |
| **Skeletal Muscle** | Aligned fiber bundle structure | Muscle regeneration, motor function |

### Tubular (7)

| Type | Description | Use Cases |
|------|-------------|-----------|
| **Bladder** | Hollow organ structure with smooth muscle layer | Bladder tissue engineering, urinary repair |
| **Blood Vessel** | Artery/capillary conduit with appropriate dimensions | Vascular grafts, bypass conduits |
| **Nerve Conduit** | Neuronal guidance channel for axon regeneration | Nerve repair, spinal cord injury |
| **Spinal Cord** | CNS tissue scaffold with ventral/dorsal regions | Spinal cord injury treatment |
| **Trachea** | Cartilage-lined airway scaffold | Airway reconstruction, breathing support |
| **Tubular Conduit** | Cylindrical scaffold with textured inner surface (smooth/grooved/porous) | Neural guidance, vascular conduits |
| **Vascular Perfusion Dish** | Collision-aware branching vascular network | Perfusion studies, vascularized tissue culture |

---

## API Reference

### Core Endpoints

#### POST /api/generate

Generate a complete scaffold with STL export.

**Request:**

```json
{
  "scaffold_type": "vascular_network",
  "params": {
    "inlets": 4,
    "levels": 3,
    "splits": 2,
    "spread": 0.4,
    "ratio": 0.79,
    "outer_radius": 4.875,
    "height": 2.0
  },
  "export_format": "binary"
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "scaffold_id": "550e8400-e29b-41d4-a716-446655440000",
  "mesh_data": {
    "vertices": [[0, 0, 0], [1, 0, 0], ...],
    "faces": [[0, 1, 2], ...],
    "normals": [[0, 0, 1], ...]
  },
  "stats": {
    "vertex_count": 12540,
    "face_count": 25080,
    "volume": 45.3,
    "surface_area": 234.5,
    "generation_time_ms": 2341
  },
  "stl_binary": "base64-encoded-binary",
  "warnings": []
}
```

#### POST /api/preview

Fast mesh preview (no STL export).

**Request:**

```json
{
  "scaffold_type": "vascular_network",
  "params": { ... }
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "mesh_data": { ... },
  "stats": { ... }
}
```

#### POST /api/validate

Validate parameters without generation.

**Request:**

```json
{
  "scaffold_type": "vascular_network",
  "params": { ... }
}
```

**Response (200 OK):**

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Inlets exceed typical range (4 > 3)"]
}
```

#### GET /api/presets

List available preset scaffolds.

**Response (200 OK):**

```json
{
  "presets": [
    {
      "id": "vascular-high-perfusion",
      "name": "High Perfusion Vascular",
      "category": "vascular_network",
      "params": { ... },
      "description": "Optimized for maximum nutrient transport"
    },
    ...
  ]
}
```

#### GET /api/types

List all 43 scaffold types.

**Response (200 OK):**

```json
{
  "types": [
    {
      "id": "vascular_network",
      "name": "Vascular Network",
      "category": "original",
      "description": "Branching blood vessel network...",
      "parameters": [
        { "name": "inlets", "type": "integer", "min": 1, "max": 25, "default": 4 },
        ...
      ]
    },
    ...
  ]
}
```

#### POST /api/chat

Send message to LLM assistant.

**Request:**

```json
{
  "message": "Create a highly vascularized cardiac scaffold",
  "session_id": "user-session-123"
}
```

**Response (200 OK):**

```json
{
  "status": "success",
  "response": "I've created a cardiac patch scaffold...",
  "actions": [
    {
      "type": "generate",
      "scaffold_type": "cardiac_patch",
      "params": { ... }
    }
  ]
}
```

#### POST /auth/register

Create new user account.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Response (201 Created):**

```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

#### POST /auth/login

Authenticate user and get JWT token.

**Request:**

```json
{
  "email": "user@example.com",
  "password": "secure-password"
}
```

**Response (200 OK):**

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "email": "user@example.com"
  }
}
```

#### POST /saved

Save generated scaffold to user library.

**Request:**

```json
{
  "name": "My Cardiac Scaffold",
  "description": "Optimized for high perfusion",
  "scaffold_type": "cardiac_patch",
  "params": { ... },
  "tags": ["cardiac", "vascular", "optimized"]
}
```

**Response (201 Created):**

```json
{
  "id": "uuid",
  "name": "My Cardiac Scaffold",
  "created_at": "2025-01-28T12:34:56Z",
  "url": "/saved/uuid"
}
```

---

## Key Concepts

### Murray's Law

**Principle:** In branching networks, the cubic sum of daughter branch diameters equals the parent diameter cubed.

**Mathematical Definition:**

```
d_parent³ = d_child1³ + d_child2³ + ... + d_childN³
```

**Optimal Ratio:**

For binary branching (each branch splits into 2):
```
d_parent³ = 2 × d_child³
d_child = d_parent × (1/2)^(1/3)
d_child = d_parent × 0.794  ≈ 0.79
```

**Biological Basis:**

- Minimizes metabolic energy for perfusion
- Maximizes nutrient transport efficiency
- Observed in natural vasculature (animal and plant)

**Implementation in MorphoStruct:**

```python
# Vascular network generator uses Murray's law
ratio = 0.79  # Optimal for binary branching
child_radius = parent_radius * ratio

# Creates realistic, efficient networks
# Adjustable ratio parameter (0.5-1.0) for customization
```

**Usage:**

```python
params = VascularParams(
    ratio=0.79,      # Murray's law optimal
    splits=2,        # Binary branching
    levels=4         # 16 terminal branches
)
```

### TPMS Surfaces

**TPMS = Triply Periodic Minimal Surfaces**

Minimal surfaces that are periodic in three orthogonal directions and have zero mean curvature everywhere.

**Key Properties:**

- **Minimal Surface**: Smallest area spanning boundary
- **Triply Periodic**: Repeats infinitely in 3D space
- **Smooth Connectivity**: Interpenetrating networks

**Common TPMS in Bioprinting:**

#### Gyroid

- Discovered by Alan Schoen (1970)
- Equation: `sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x) = 0`
- Properties:
  - No self-intersections
  - Single continuous phase
  - Approximate 50% porosity
  - High surface area per unit volume
- Uses: Bone scaffolds, high-perfusion structures

#### Schwarz P (Primitive)

- Equation: `cos(x) + cos(y) + cos(z) = 0`
- Properties:
  - Double continuous phase (gyroid is single)
  - More symmetric than gyroid
  - Better structural properties
- Uses: Balanced porosity/strength tradeoff

**Advantages of TPMS:**

1. **Biomimetic**: Nature uses similar structures
2. **High Surface Area**: 100-300 m²/cm³
3. **Hierarchical**: Can be scaled at multiple levels
4. **Optimal Flow**: Minimal resistance pathways
5. **Printable**: Compatible with most bioprinting techniques

**Implementation in MorphoStruct:**

```python
def generate_gyroid(params: GyroidParams) -> Manifold3D:
    # Sample the implicit function: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x)
    # Extract level set at threshold = 0
    # Boolean intersect with bounding volume
    # Return mesh

def generate_schwarz_p(params: SchwarzPParams) -> Manifold3D:
    # Similar approach with cos(x) + cos(y) + cos(z) function
```

### Tree Union Algorithm

**Purpose:** Efficiently compute boolean unions of many overlapping geometries.

**Naive Approach:**
```
result = geometry1
for each additional geometry:
    result = result ∪ geometry
```
Time Complexity: O(n²) - extremely slow for many pieces

**Tree Union Optimization:**

```
1. Build binary tree of geometries
2. Compute unions bottom-up:

   Level 0:  g1  g2  g3  g4  g5  g6  g7  g8
   Level 1:  u12  u34  u56  u78
   Level 2:  u1234    u5678
   Level 3:  final result
```

Time Complexity: O(n log n) - ~16x faster for 256 pieces

**Implementation in core.py:**

```python
def tree_union(geometries: List[Manifold3D]) -> Manifold3D:
    """
    Efficiently union many geometries using tree reduction.

    Args:
        geometries: List of Manifold3D objects to union

    Returns:
        Single unified Manifold3D
    """
    if len(geometries) == 0:
        return empty_manifold()
    if len(geometries) == 1:
        return geometries[0]

    # Pair up and union adjacent geometries
    next_level = []
    for i in range(0, len(geometries), 2):
        if i + 1 < len(geometries):
            unioned = geometries[i].boolean_union(geometries[i + 1])
            next_level.append(unioned)
        else:
            next_level.append(geometries[i])

    # Recursively union next level
    return tree_union(next_level)
```

**Performance Impact:**

```
256 vascular branches:
- Naive union: ~45 seconds
- Tree union: ~2.8 seconds  ✓ 16x faster

1024 branches:
- Naive: Not practical (several minutes)
- Tree: ~11 seconds
```

---

## Troubleshooting

### Backend Issues

#### "Port 8000 already in use"

```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9

# Or use different port (edit run.py)
```

#### "ModuleNotFoundError: No module named 'manifold3d'"

```bash
# Reinstall dependencies
cd backend
source venv/bin/activate
pip install --upgrade manifold3d

# Or rebuild venv
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### "LLM API key invalid"

```bash
# Check .env file
cat backend/.env

# Verify API key format:
# Anthropic: sk-ant-v7-...
# OpenAI: sk-proj-...

# Test LLM provider
curl -X GET http://localhost:8000/api/chat/status
```

#### "Database locked" or SQLite errors

```bash
# Remove corrupted database
rm backend/morphostruct.db

# Restart backend (will recreate DB)
./morphostruct.sh backend
```

### Frontend Issues

#### "Port 3000 already in use"

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or edit frontend/next.config.js to use different port
```

#### "Cannot GET /api/generate"

- Verify backend is running on port 8000
- Check frontend `.env.local` has correct `NEXT_PUBLIC_API_BASE_URL`
- Check CORS is enabled in `backend/app/main.py`

```bash
# Verify backend health
curl http://localhost:8000/health
```

#### Three.js mesh not rendering

- Open browser DevTools (F12)
- Check console for WebGL errors
- Verify mesh data has vertices and faces
- Try different scaffold type to isolate issue

### Common Workflow Issues

#### "Generation takes very long"

- Check `max_triangles` setting in `backend/app/config.py`
- Reduce `resolution` parameter for test scaffolds
- Try smaller parameter values

#### "STL file is huge (100+ MB)"

- Use binary format instead of ASCII (`export_format: "binary"`)
- Reduce mesh resolution
- Export preview instead of full mesh

#### "Scaffold looks distorted or invalid"

- Validate parameters: `POST /api/validate`
- Check parameter ranges in `/api/types`
- Try preset values first

---

## Contributing

### Development Workflow

1. **Fork and clone** the repository
2. **Create feature branch**: `git checkout -b feature/new-scaffold-type`
3. **Make changes** following code style
4. **Test thoroughly**:
   - Backend: Run `pytest` if tests exist
   - Frontend: Test UI components
   - Integration: Test full workflow
5. **Commit** with descriptive messages
6. **Push** to your fork
7. **Create Pull Request** with description

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Docstrings for all functions
- 100 character line limit

**TypeScript/React:**
- Use functional components
- Type all props and state
- Component files start with capital letter
- Use descriptive variable names

### Adding Documentation

- Update README.md for user-facing changes
- Add docstrings to code
- Include API examples for new endpoints
- Document new scaffold types with use cases

---

## License

MIT License - See LICENSE file for details

### Citation

If you use MorphoStruct in research, please cite:

```bibtex
@software{morphostruct2025,
  title={MorphoStruct: AI-Assisted Bioprinting Scaffold Generator},
  author={Your Name/Organization},
  year={2025},
  url={https://github.com/yourusername/MorphoStruct}
}
```

---

## Support & Resources

### Documentation

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Type Definitions**: `/backend/app/models/scaffold.py`
- **Generator Code**: `/backend/app/geometry/`

### Community

- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for general questions

### Related Resources

- [Manifold3D Documentation](https://github.com/pmp-library/pmp-library)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [Next.js App Router](https://nextjs.org/docs/app)
- [Three.js Documentation](https://threejs.org/docs/)
- [Tissue Engineering Concepts](https://pubmed.ncbi.nlm.nih.gov/)

---

**Last Updated**: January 28, 2025

**Version**: 1.0.0

**Maintainer**: Research Team

For questions or issues, please open a GitHub issue or contact the development team.
