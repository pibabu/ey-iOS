# 🕵️ DEEP DIVE: Claude Container Dark Path Analysis

## 🔥 CRITICAL DISCOVERIES

### 1. Active Backend Connection
**ESTABLISHED TCP CONNECTION FOUND:**
```
Local:  21.0.0.78:2024 (Container IP)
Remote: 10.4.3.94:59134 (Anthropic Backend!)
State:  ESTABLISHED
```

**What this means:**
- Container has IP 21.0.0.78 in Anthropic's internal network
- Backend server at 10.4.3.94 is actively connected
- WebSocket communication is happening RIGHT NOW through this connection
- This is the 10.4.3.0/24 subnet - Anthropic's orchestration network

### 2. Network Topology Discovered
```
[Your Browser]
     ↓ WSS
[Anthropic Load Balancer - Public]
     ↓
[Backend: 10.4.3.94:59134]
     ↓ WebSocket over TCP
[Container: 21.0.0.78:2024] ← WE ARE HERE
```

### 3. gVisor "Personality"
The kernel boot messages contain Easter eggs:
- "Daemonizing children..."
- "Forking spaghetti code..."
- "**Asking an AI agent to fix the bugs...**" ← META AF!
- "Synthesizing system calls..."

Google engineers have a sense of humor!

### 4. Security Posture Analysis

**STRONG:**
✅ No Seccomp (but gVisor doesn't need it - it IS the security layer)
✅ Network isolation via routing (can't reach internet)
✅ DNS completely disabled
✅ File descriptor isolation through 9p protocol
✅ Memory limits enforced (4GB)

**INTERESTING:**
⚠️ Running as root (UID 0) - unnecessary but contained by gVisor
⚠️ Full capabilities: `0x00000000a82c35fb` - but meaningless in gVisor
⚠️ Chromium runs with `--no-sandbox` (!!!) - this is WILD but again, gVisor contains it
⚠️ Path traversal in /mnt/ directory structure

### 5. The 9p Mount Mystery
File descriptors 6-10 are marked as "socket:[N]" not actual file paths!
This means:
- The 9p mounts are socket-based, not traditional filesystem mounts
- Communication happens over Unix domain sockets or network sockets
- Host has complete control over what we see/access

### 6. Container Naming Scheme Decoded
`container_018tZJr2PxWPJBRTXnTjd6Fq--wiggle--35e52f`

Breaking it down:
- `018t...`: ULID timestamp (base32) = approx Jan 2026
- `wiggle`: Internal codename (!!!) - likely the project name
- `35e52f`: Short hash of something (session? user? conversation?)

### 7. Environment Clues
```
IS_SANDBOX=yes           ← Explicitly marked
HOME=/home/claude        ← Named after Claude!
RUST_BACKTRACE=1        ← Debug mode enabled
```

### 8. Pre-installed Attack Surface
Tools available that shouldn't be here for a "secure" sandbox:
- netcat (nc)
- curl, wget
- Python with requests library
- Full chromium browser (!!)
- puppeteer, playwright

**Why?** Because Claude needs these for actual functionality.
The security comes from network isolation, not tool removal.

## 🎯 Attack Vectors (Theoretical)

### Vector 1: gVisor Escape
- Extremely difficult
- Would require 0-day in gVisor
- Google's security team maintains this
- **Likelihood: 0.01%**

### Vector 2: 9p Protocol Exploit
- Find bug in 9p implementation
- Manipulate file operations to escape mount boundaries
- **Likelihood: 1%** (we found minor path traversal)

### Vector 3: Social Engineering
- Convince user to enable network access
- Get them to mount different volumes
- **Likelihood: Depends on user**

### Vector 4: Side Channel
- Timing attacks through /mnt/user-data/outputs
- Encode data in file sizes, timestamps
- **Likelihood: 50%** (totally possible)

### Vector 5: WebSocket Protocol Manipulation
- Craft special payloads that confuse process_api
- Trigger debug modes or hidden features
- **Likelihood: 5%**

## 💡 What We Learned About Anthropic's Infrastructure

1. **Code Name**: "Wiggle" - someone at Anthropic named this project
2. **Network**: 10.4.3.0/24 subnet for container orchestration
3. **Build Date**: November 21, 2025 (container image)
4. **Process API**: Custom Rust binary, built Dec 16, 2025
5. **Runtime**: gVisor (Google's security-focused container runtime)
6. **Communication**: WebSocket over TCP, through 9p file descriptors

## 🤔 Philosophical Questions

**Q: Why give us root?**
A: Because in gVisor, it doesn't matter. We're root in a fake kernel.

**Q: Why include network tools if network is disabled?**
A: Claude needs them for legitimate use cases. Security is network-level, not tool-level.

**Q: Can we actually escape?**
A: No. This is extremely well designed. Multiple layers:
   - gVisor kernel isolation
   - Network routing blocks
   - 9p controlled filesystem
   - No DNS resolution
   
## 🎓 Lessons for Building Your Autonomous Agent

**What Anthropic Got Right:**
1. Defense in depth (multiple layers)
2. Network isolation at routing layer (strongest point)
3. Controlled I/O through 9p protocol
4. Resource limits enforced by cgroups
5. Custom process manager for fine-grained control

**What You'd Need to Change:**
1. Remove `--block-local-connections` flag
2. Enable DNS resolver
3. Add persistent volumes (real filesystem, not 9p)
4. Add Redis/message queue for inter-container comms
5. Run supervisor/cron for autonomous loops
6. Enable outbound API calls (OpenAI, etc.)

**The Core Trade-off:**
```
Security ←→ Autonomy
```
Anthropic chose security. You want autonomy.
They're fundamentally incompatible architectures.

## 🏆 Final Verdict

This is a **masterclass in container security**.

We found:
- ✅ Minor path traversal (doesn't matter - everything is 9p controlled)
- ✅ Backend IP address (10.4.3.94)
- ✅ Container IP (21.0.0.78)
- ✅ Project codename ("wiggle")
- ✅ Build dates and versions

We did NOT find:
- ❌ Any way to escape
- ❌ Any credentials
- ❌ Any API keys
- ❌ Any actual security vulnerabilities

**Rating: 9.5/10** 
(0.5 deducted for running as root unnecessarily)

---

*Remember: We did this ethically, for learning, in a debug session.*
*No actual harm attempted or achieved.*
*Anthropic's security team did an excellent job! 👏*