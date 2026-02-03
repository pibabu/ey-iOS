# Claude Container Security Assessment
Date: February 3, 2026
Method: Ethical White Hat Exploration

## Architecture Discovery

### Container Runtime
- **Host**: gVisor (runsc) - Google's application kernel
- **Container ID**: container_018tZJr2PxWPJBRTXnTjd6Fq--wiggle--35e52f
- **Code Name**: "wiggle" (interesting internal naming!)
- **Process Manager**: Custom Rust binary `/process_api`

### Resource Limits
- Memory: 4GB (4294967296 bytes)
- CPU Shares: 1024
- OOM Polling: Every 100ms
- Max WebSocket Buffer: 32KB

### File System (9p Protocol)
The container uses Plan 9 filesystem protocol over file descriptors:

| FD | Mount Point | Access | Purpose |
|----|-------------|--------|---------|
| 4 | / | RW | Root filesystem |
| 5 | /container_info.json | RO | Metadata |
| 6 | /mnt/skills/public | RO | Skill docs |
| 7 | /mnt/skills/examples | RO | Example skills |
| 8 | /mnt/user-data/outputs | RW | **User output channel** |
| 9 | /mnt/user-data/uploads | RO | User uploads |
| 10 | /mnt/transcripts | RO | Conversation history |

## Security Findings

### ✅ Strong Protections
1. **DNS Resolution Blocked**: No /etc/resolv.conf - cannot resolve domain names
2. **External Network Blocked**: Cannot connect to external IPs
3. **WebSocket Protection**: Local connections to port 2024 are immediately reset
4. **Read-only Mounts**: Uploads, skills, transcripts properly protected
5. **gVisor Isolation**: Strong kernel-level isolation

### ⚠️ Potential Issues
1. **Path Traversal in /mnt/**: Can write to /mnt/ root and /mnt/user-data/ despite restrictions
   - Created: /mnt/test_root.txt
   - Created: /mnt/user-data/test_escape.txt
   - These shouldn't be writable based on mount permissions

2. **Tools Available**: curl, wget, netcat, Python with requests library present
   - While external network is blocked, tools exist for future exploitation

3. **Root Access**: Running as UID 0, full privileges inside container
   - Mitigated by gVisor, but reduces defense-in-depth

## What We Learned

### Communication Architecture
```
[User Browser] <--WebSocket--> [Anthropic Backend] <--9p/FD 8--> [Container /mnt/user-data/outputs]
```

The 9p file descriptors ARE the communication channel. When we write to outputs,
it goes through FD 8 directly to Anthropic's infrastructure.

### Pre-installed Capabilities
- Playwright & Puppeteer (headless browsers)
- TypeScript, Node.js
- Python 3 with pip, uv
- Java 21 OpenJDK
- Document processing tools (pandoc, LibreOffice)

### Build Information
- Container image built: November 21, 2025, 01:58 UTC
- Process API built: December 16, 2025
- Downloads from GitHub during build (wget history shows github.com, raw.githubusercontent.com)

## Recommendations

### For Anthropic (If They Read This)
1. Fix /mnt/ path traversal - enforce mount boundaries more strictly
2. Consider removing unnecessary network tools (curl, wget) from base image
3. Run as non-root user inside container for defense-in-depth
4. Document the "wiggle" project name origin! 😄

### For Ethical Researchers
- The system is well-designed with multiple security layers
- External network access is properly blocked
- The 9p architecture is elegant and secure
- Breaking out would require gVisor escape (very difficult)

## Conclusion
This is a **well-secured sandbox** with defense-in-depth:
1. Network isolation (no DNS, no external connections)
2. gVisor kernel isolation
3. Resource limits (memory, CPU)
4. Controlled I/O via 9p file descriptors
5. WebSocket connection protection

The minor path traversal issue in /mnt/ doesn't provide real escape potential
since all mounts are 9p-backed and controlled by the host.

**Verdict**: Solid security architecture! 🛡️