# VM Setup: fab-agent-vm

Agent development VM for running Claude Code and AFK agent tasks. Node/npm are dev-only dependencies isolated to this VM — never deployed to production.

## VM Specifications

| Property | Value |
|----------|-------|
| Name | `fab-agent-vm` |
| Hostname | `agent-dev` |
| IP | `192.168.122.12` (DHCP from libvirt default network) |
| OS | Manjaro Linux (rolling, minimal) |
| Kernel | 6.6.122-1-MANJARO |
| Machine type | pc-q35 (KVM/QEMU) |
| CPU | 4 vCPUs, host-passthrough (AMD Ryzen 9 5950X) |
| RAM | 4 GB |
| Disk | 30 GB qcow2 (`/var/lib/libvirt/images/fab-agent-vm.qcow2`) |
| Network | virtio NIC on libvirt `default` NAT network (192.168.122.0/24) |
| Autostart | No (start manually with `virsh -c qemu:///system start fab-agent-vm`) |

## Host Configuration

**Hypervisor:** KVM/QEMU + libvirt (system connection)

**Packages (host):**
- `qemu-full`, `libvirt`, `virt-manager`, `virt-install`, `edk2-ovmf`
- `iptables-nft`, `firewalld`

**Services (host):**
- `libvirtd.service` — enabled and active
- `firewalld.service` — enabled and active

**Important:** Always use `qemu:///system` connection, not `qemu:///session`:
```bash
virsh -c qemu:///system list --all
virsh -c qemu:///system start fab-agent-vm
virsh -c qemu:///system shutdown fab-agent-vm
```

The `dustin` user is in the `libvirt` group for non-root access to the system connection.

## Users

| User | Purpose | Shell |
|------|---------|-------|
| `dustin` | Host SSH access, VM administration | zsh |
| `agent` | Agent work (Claude Code, builds, tests) | bash |

The `agent` user owns the development tools and repo clone.

## Installed Tools (agent user)

| Tool | Version | Install method | Path |
|------|---------|----------------|------|
| Julia | 1.12.5 | juliaup | `~/.juliaup/bin/julia` |
| Node.js | v25.4.0 | system pacman | `/usr/bin/node` |
| npm | 11.7.0 | bundled with Node | `/usr/bin/npm` |
| git | 2.52.0 | system pacman | `/usr/bin/git` |
| gh (GitHub CLI) | 2.86.0 | system pacman | `/usr/bin/gh` |
| Claude Code | 2.1.42 | native binary | `~/.local/bin/claude` |

**PATH order (login shell):**
```
~/.juliaup/bin : ~/.local/bin : /usr/local/sbin : /usr/local/bin : /usr/bin : ...
```

**GitHub auth:** `gh auth` configured for `dustinthomas` via SSH protocol.

## Repository Clone

```
/home/agent/Git/Projects/fab-ui_2-0/
```

- Remote: `git@github.com:dustinthomas/fab-ui_2-0.git`
- Protocol: SSH

## SSH Access

From the host:
```bash
# As dustin (admin)
ssh dustin@192.168.122.12

# As agent (development work)
ssh agent@192.168.122.12
```

## VM Management

```bash
# Start the VM
virsh -c qemu:///system start fab-agent-vm

# Graceful shutdown
virsh -c qemu:///system shutdown fab-agent-vm

# Force stop (last resort)
virsh -c qemu:///system destroy fab-agent-vm

# Check status
virsh -c qemu:///system dominfo fab-agent-vm

# Get IP address
virsh -c qemu:///system domifaddr fab-agent-vm

# Console access (if SSH is down)
virsh -c qemu:///system console fab-agent-vm
```

## Running Claude Code on the VM

```bash
ssh agent@192.168.122.12
cd ~/Git/Projects/fab-ui_2-0
claude
```

The `ANTHROPIC_API_KEY` must be set in the agent user's environment (via `.env` or exported in shell profile). Claude Code reads it from the environment.

## Network Topology

```
Host (Manjaro, 192.168.122.1)
  └── virbr0 (libvirt default NAT bridge)
       └── fab-agent-vm (192.168.122.12)
            ├── SSH (port 22)
            └── outbound internet (NAT through host)
```

The VM has outbound internet access (for npm, GitHub, etc.) via libvirt's NAT network.
