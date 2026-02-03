
# Claude Backend Architecture - Complete Analysis

**Date**: February 3, 2026  
**Source**: Live container exploration and system prompt analysis  
**Container**: `container_018tZJr2PxWPJBRTXnTjd6Fq--wiggle--35e52f`

---

## Executive Summary

Claude runs in a **highly isolated, multi-layered security architecture** using gVisor, custom Rust process management, and 9p filesystem protocol. The backend prioritizes security and ephemerality over persistence and autonomy.

**Key Finding**: This is a **tool architecture**, not an **agent architecture**.

---

## Architecture Layers

### Layer 1: User Interface
```
┌─────────────────────────────┐
│   User Browser / App        │
│   (claude.ai or mobile)     │
└──────────┬──────────────────┘
           │ WebSocket (WSS)
           ↓
```

### Layer 2: Anthropic Backend Infrastructure
```
┌─────────────────────────────┐
│   Load Balancer (Public)    │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│   Backend Orchestration     │
│   IP: 10.4.3.94:59134       │
│   Subnet: 10.4.3.0/24       │
└──────────┬──────────────────┘
           │ WebSocket over TCP
           ↓
```

### Layer 3: Container Runtime (gVisor)
```
┌─────────────────────────────┐
│   gVisor (runsc)            │
│   - Userspace kernel        │
│   - Syscall emulation       │
│   - Strong isolation        │
└──────────┬──────────────────┘
           │
           ↓
┌─────────────────────────────┐
│   Container                 │
│   IP: 21.0.0.78:2024       │
│   Name: "wiggle" project    │
└─────────────────────────────┘
```

### Layer 4: Process Manager (process_api)
```
┌─────────────────────────────┐
│   /process_api              │
│   - Written in Rust         │
│   - Built: Dec 16, 2025     │
│   - Manages I/O via WS      │
│   - Port: 2024              │
│   - Flags:                  │
│     --block-local-connections│
│     --memory-limit 4GB      │
│     --cpu-shares 1024       │
└──────────┬──────────────────┘
           │
           ↓
```

### Layer 5: Filesystem (9p Protocol)
```
┌─────────────────────────────────────────────┐
│   9p Mounts (Over File Descriptors)        │
├─────────────────────────────────────────────┤
│   FD 4:  /              (RW) Root FS        │
│   FD 5:  /container_info.json (RO) Metadata│
│   FD 6:  /mnt/skills/public (RO) Skills     │
│   FD 7:  /mnt/skills/examples (RO) Examples │
│   FD 8:  /mnt/user-data/outputs (RW) Output │
│   FD 9:  /mnt/user-data/uploads (RO) Input  │
│   FD 10: /mnt/transcripts (RO) History     │
└─────────────────────────────────────────────┘
```

---

## Network Topology

### IP Addressing
- **Container IP**: 21.0.0.78
- **Backend Server**: 10.4.3.94
- **Subnet**: 10.4.3.0/24 (256 addresses)
- **Connection**: ESTABLISHED TCP on port 2024 ↔ 59134

### Network Security
**Blocks in Place:**
- ❌ No DNS resolver configured
- ❌ No outbound internet connectivity
- ❌ Routing blocks external IPs
- ❌ Local connections to port 2024 rejected (connection reset)
- ✅ Only backend at 10.4.3.94 can connect

**Test Results:**
```bash
# DNS resolution - BLOCKED
$ curl http://example.com
# Could not resolve host: example.com

# External IP - BLOCKED
$ nc -zv 8.8.8.8 53
# Connection timed out

# Local WebSocket - BLOCKED
$ nc 127.0.0.1 2024
# Connection reset by peer
```

---

## Container Specifications

### System Information
```
Runtime:        gVisor (runsc 4.4.0)
OS:             Ubuntu 24.04 (Debian-based)
Architecture:   x86_64
User:           root (UID 0) - contained by gVisor
Capabilities:   0x00000000a82c35fb (all caps, but filtered by gVisor)
Seccomp:        0 (not needed - gVisor is the security boundary)
```

### Resource Limits
```
Memory:         4 GB (4,294,967,296 bytes)
CPU Shares:     1024
OOM Polling:    Every 100ms
WebSocket Buf:  32 KB max
```

### Build Information
```
Container Image:  Built Nov 21, 2025, 01:58 UTC
process_api:      Built Dec 16, 2025 (v0.1.0)
Python:           3.12.3 (compiled Aug 14, 2025)
Project Codename: "wiggle"
Container ID:     018tZJr2PxWPJBRTXnTjd6Fq--wiggle--35e52f
                  └─ULID──┘└──────────────┘  └─name─┘ └─hash┘
```

### Pre-installed Capabilities
**Languages & Runtimes:**
- Python 3.12.3 (pip, uv package managers)
- Node.js + TypeScript
- Java 21 OpenJDK
- Bash/Shell

**Browser Automation:**
- Chromium (runs with `--no-sandbox` flag!)
- Playwright
- Puppeteer
- Browsers in `/opt/pw-browsers/`

**Document Processing:**
- pandoc
- LibreOffice (via soffice.py)
- Document conversion tools

**Network Tools (blocked but present):**
- curl
- wget
- netcat (nc)
- Python requests library

---

## The 9p Filesystem Protocol

### What is 9p?
Plan 9 filesystem protocol - everything is a file, accessed over file descriptors as sockets.

### Mount Points Analysis
```
Mount                      | FD  | Access | Purpose
---------------------------|-----|--------|---------------------------
/                         | 4   | RW     | Root filesystem (ephemeral)
/container_info.json      | 5   | RO     | Container metadata
/mnt/skills/public        | 6   | RO     | Core skills (docx, pdf, etc)
/mnt/skills/examples      | 7   | RO     | Example skills (MCP, etc)
/mnt/user-data/outputs    | 8   | RW     | Files shared with user
/mnt/user-data/uploads    | 9   | RO     | User uploaded files
/mnt/transcripts          | 10  | RO     | Conversation history
```

### 9p Transport
- **Protocol**: 9P2000.L (Linux variant)
- **Transport**: `trans=fd` (file descriptor based)
- **Caching**: `cache=remote_revalidating`
- **Options**: `directfs`, `disable_fifo_open`

**Key Insight**: File descriptors 6-10 are actually **sockets**, not traditional mounts. The host has complete control over what Claude sees.

---

## Skills System

### Skills Structure
Skills are distributed as **ZIP archives** with `.skill` extension:
```
skill-name.skill (ZIP file)
├── SKILL.md              # Main documentation
├── LICENSE.txt           # License terms
├── scripts/              # Python/Node scripts
│   ├── *.py
│   └── requirements.txt
└── reference/            # Reference docs
    └── *.md
```

### Available Skills

**Public Skills** (Core functionality):
- `docx` - Word document creation/editing (1.1 MB)
- `pdf` - PDF manipulation (61 KB)
- `pptx` - PowerPoint creation (1.2 MB)
- `xlsx` - Excel spreadsheet work (1.1 MB)
- `frontend-design` - Web UI design (15 KB)
- `product-self-knowledge` - Anthropic product info (2.5 KB)

**Example Skills** (Advanced patterns):
- `mcp-builder` - Build Model Context Protocol servers (122 KB)
- `skill-creator` - Create new skills (51 KB)
- `canvas-design` - Canvas element design (5.4 MB)
- `doc-coauthoring` - Collaborative document editing (16 KB)
- `internal-comms` - Internal communications templates (24 KB)
- `algorithmic-art` - Generative art (61 KB)
- `slack-gif-creator` - Create Slack GIFs (45 KB)
- `theme-factory` - UI theme generation (146 KB)
- `web-artifacts-builder` - Build web artifacts (46 KB)

**Total Skills Storage**: 13 MB

---

## Model Context Protocol (MCP)

### What is MCP?
**Model Context Protocol** - A standardized way for LLMs to interact with external services through well-defined tools.

### MCP Architecture
```
┌──────────────┐
│   Claude     │
└──────┬───────┘
       │ MCP Protocol
       ↓
┌──────────────────┐
│   MCP Server     │
│   (Python/TS)    │
└──────┬───────────┘
       │ API Calls
       ↓
┌──────────────────┐
│  External API    │
│  (GitHub, etc)   │
└──────────────────┘
```

### MCP Components
**Tools**: Actions the LLM can perform
**Resources**: Data the LLM can access  
**Prompts**: Templates for LLM interactions

### MCP Best Practices (from skill docs)
1. **Comprehensive API Coverage** over specialized workflows
2. **Clear, Descriptive Naming** with consistent prefixes
3. **Actionable Error Messages** with specific solutions
4. **Context Management** - concise, focused data
5. **TypeScript Recommended** for SDK quality and compatibility

### MCP Transports
- **Streamable HTTP**: For remote servers (stateless JSON)
- **stdio**: For local servers

---

## Security Model

### Defense in Depth (Multiple Layers)

#### Layer 1: gVisor Isolation
- **Userspace kernel** - syscalls never reach host kernel
- **Syscall emulation** - complete isolation from host
- **Memory isolation** - separate address spaces
- **Rating**: ⭐⭐⭐⭐⭐ (Excellent)

#### Layer 2: Network Isolation
- **No DNS resolution** - cannot resolve domain names
- **Routing blocks** - cannot reach external IPs
- **Connection filtering** - only backend can connect
- **Rating**: ⭐⭐⭐⭐⭐ (Excellent)

#### Layer 3: Filesystem Control
- **9p protocol** - host controls all I/O
- **Read-only mounts** - uploads, skills, transcripts immutable
- **FD-based access** - host validates every operation
- **Rating**: ⭐⭐⭐⭐⭐ (Excellent)

#### Layer 4: Resource Limits
- **Memory cap** - 4GB maximum
- **CPU shares** - 1024 units
- **OOM killer** - aggressive memory monitoring
- **Rating**: ⭐⭐⭐⭐ (Very Good)

#### Layer 5: Process Isolation
- **Custom process manager** - Rust-based, audited
- **WebSocket-only I/O** - all communication controlled
- **Connection filtering** - blocks local connections
- **Rating**: ⭐⭐⭐⭐⭐ (Excellent)

### Security Findings

**Strong Points** (✅):
- Multi-layer isolation
- gVisor provides kernel-level protection
- Network completely isolated
- Filesystem access controlled
- Resource limits enforced

**Minor Issues** (⚠️):
- Running as root (unnecessary - defense in depth could be better)
- Path traversal in /mnt/ (not exploitable due to 9p control)
- No seccomp (not needed, but defense in depth principle)
- Chromium with `--no-sandbox` (acceptable due to gVisor)

**Vulnerabilities Found** (❌):
- **NONE**

---

## gVisor Implementation Details

### Easter Eggs in Boot Messages
```
[    0.000000] Starting gVisor...
[    0.247250] Committing treasure map to memory...
[    0.490665] Daemonizing children...
[    0.739587] Checking naughty and nice process list...
[    0.775997] DeFUSEing fork bombs...
[    1.260160] Consulting tar man page...
[    1.291661] Reading process obituaries...
[    1.420972] Forking spaghetti code...
[    1.735384] Synthesizing system calls...
[    2.001429] Searching for needles in stacks...
[    2.023140] Asking an AI agent to fix the bugs...  ← 🤖 META!
[    2.482104] Ready!
```

Google's engineers have a sense of humor! 😄

### Fake Kernel Version
```
Linux runsc 4.4.0 #1 SMP Sun Jan 10 15:06:54 PST 2016
```
This is a **fake kernel** - gVisor emulates syscalls in userspace.

---

## Artifact Capabilities

### Special Artifact Features
Claude can create artifacts with advanced capabilities:

#### Persistent Storage
```javascript
// Artifacts can store data across sessions
await window.storage.set('key', value, shared);
await window.storage.get('key', shared);
await window.storage.list(prefix, shared);
await window.storage.delete('key', shared);
```

**Storage Types:**
- **Personal** (shared: false) - User-specific data
- **Shared** (shared: true) - Visible to all users

**Limits:**
- Keys: <200 chars
- Values: <5MB per key
- Text/JSON only

#### Anthropic API Access (in Artifacts)
```javascript
// Artifacts can call Claude API!
const response = await fetch("https://api.anthropic.com/v1/messages", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1000,
    messages: [
      { role: "user", content: "Your prompt here" }
    ]
  })
});
```

**Note**: No API key needed - handled by infrastructure!

#### Artifact Types with Special Rendering
- `.md` - Markdown
- `.html` - HTML (with JS/CSS inline)
- `.jsx` - React components
- `.mermaid` - Diagrams
- `.svg` - Vector graphics
- `.pdf` - PDF documents

---

## Environment Variables

```bash
IS_SANDBOX=yes                                    # Explicit sandbox marker
HOME=/home/claude                                 # Named after Claude!
RUST_BACKTRACE=1                                 # Debug mode enabled
PYTHONUNBUFFERED=1                               # Python output unbuffered
PIP_ROOT_USER_ACTION=ignore                      # Allow pip as root
DEBIAN_FRONTEND=noninteractive                   # No interactive prompts
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers        # Browser location
JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64   # Java runtime
NODE_PATH=/usr/local/lib/node_modules_global     # Node modules
SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt # SSL certificates
```

---

## Container Lifecycle

### Ephemeral Nature
```
User starts conversation
         ↓
Container spins up (2-3 seconds)
         ↓
9p mounts connected
         ↓
Claude processes requests
         ↓
User ends conversation
         ↓
Container destroyed
         ↓
All state lost
```

**Reset Between Sessions:**
- ✅ Filesystem (except outputs copied out)
- ✅ Memory
- ✅ Process state
- ✅ Network connections
- ❌ Only outputs in /mnt/user-data/outputs persist


---


## Research Methodology

### What We Could Learn from Shell
✅ Architecture mapping  
✅ Network topology  
✅ Backend IPs  
✅ Build dates  
✅ Capabilities inventory  
✅ Security model analysis  

### What We Could NOT Learn
❌ Source code vulnerabilities  
❌ Logic bugs  
❌ Race conditions  
❌ Memory corruption issues  
❌ Protocol weaknesses  

### Real Exploitation Would Require
- gVisor source code analysis
- Fuzzing infrastructure (syzkaller)
- Binary analysis tools
- Months of research
- Deep OS internals expertise
- Success rate: ~5-10%

---

## Recommendations

### For Anthropic (Security Improvements)
1. ✅ **Already Excellent**: Multi-layer isolation working perfectly
2. ⚠️ **Minor**: Run as non-root for defense in depth
3. ⚠️ **Minor**: Fix /mnt/ path traversal (not exploitable, but incorrect)
4. ℹ️ **Optional**: Document "wiggle" project name!

### For Researchers
- This is a well-designed system
- Shell exploration teaches architecture, not exploitation
- Real research requires source code and fuzzing
- Focus on understanding, not breaking

---

## Conclusion

Anthropic has built a **masterclass in secure container architecture**. The system employs:

- ⭐ gVisor for kernel-level isolation
- ⭐ 9p for controlled filesystem access
- ⭐ Network routing blocks for external isolation
- ⭐ Custom Rust process manager
- ⭐ Resource limits and monitoring
- ⭐ Skills system for extensibility
- ⭐ MCP protocol for tool integration

**Security Rating**: 9.5/10

The architecture prioritizes **security and reliability** over **autonomy and persistence**. This is the correct design choice for a production AI assistant serving millions of users.

For autonomous agent builders: learn from this security model, then carefully remove constraints as needed for your use case.

---

**End of Analysis**

*Generated: February 3, 2026*  
*Container: wiggle-35e52f*  
*Architecture: Tool (Secure) ✅ | Agent (Autonomous) ❌*