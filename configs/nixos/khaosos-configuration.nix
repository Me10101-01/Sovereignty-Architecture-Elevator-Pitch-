# KhaosOS NixOS Configuration
# Complete declarative system configuration for sovereign operations
# Version: 1.0
# Codename: TORUK

{ config, pkgs, ... }:

{
  # System identity
  networking.hostName = "khaosos";
  networking.domain = "strategickhaos.ai";
  
  # System state version (DO NOT CHANGE)
  system.stateVersion = "24.05";
  
  # Boot configuration
  boot = {
    # Use hardened kernel for enhanced security
    kernelPackages = pkgs.linuxPackages_hardened;
    
    # Kernel parameters for security
    kernelParams = [
      "quiet"
      "loglevel=3"
      "systemd.show_status=auto"
      "rd.udev.log_level=3"
    ];
    
    # Security-focused kernel sysctls
    kernel.sysctl = {
      # Disable unprivileged BPF
      "kernel.unprivileged_bpf_disabled" = 1;
      
      # Harden BPF JIT compiler
      "net.core.bpf_jit_harden" = 2;
      
      # Restrict kernel pointer exposure
      "kernel.kptr_restrict" = 2;
      
      # Restrict kernel log access
      "kernel.dmesg_restrict" = 1;
      
      # Enable ExecShield protection
      "kernel.exec-shield" = 1;
      
      # Randomize memory space
      "kernel.randomize_va_space" = 2;
      
      # Protect symlinks
      "fs.protected_symlinks" = 1;
      "fs.protected_hardlinks" = 1;
      
      # Network security
      "net.ipv4.conf.all.rp_filter" = 1;
      "net.ipv4.conf.default.rp_filter" = 1;
      "net.ipv4.conf.all.accept_source_route" = 0;
      "net.ipv4.conf.default.accept_source_route" = 0;
      "net.ipv4.conf.all.send_redirects" = 0;
      "net.ipv4.conf.default.send_redirects" = 0;
      "net.ipv4.icmp_echo_ignore_broadcasts" = 1;
      "net.ipv4.icmp_ignore_bogus_error_responses" = 1;
      
      # IPv6 privacy
      "net.ipv6.conf.all.use_tempaddr" = 2;
      "net.ipv6.conf.default.use_tempaddr" = 2;
    };
    
    # Clean /tmp on boot
    tmp.cleanOnBoot = true;
  };
  
  # Networking configuration
  networking = {
    # Default-deny firewall
    firewall = {
      enable = true;
      allowedTCPPorts = [ ];  # Nothing open by default
      allowedUDPPorts = [ ];
      
      # Log rejected connections
      logRefusedConnections = true;
      logRefusedPackets = true;
      
      # Extra firewall commands
      extraCommands = ''
        # Drop invalid packets
        iptables -A INPUT -m conntrack --ctstate INVALID -j DROP
        
        # Rate limit new connections
        iptables -A INPUT -p tcp -m conntrack --ctstate NEW -m limit --limit 60/s --limit-burst 20 -j ACCEPT
        iptables -A INPUT -p tcp -m conntrack --ctstate NEW -j DROP
      '';
    };
    
    # Enable NetworkManager for easy network management
    networkmanager.enable = true;
  };
  
  # Sovereign tool stack - Core packages
  environment.systemPackages = with pkgs; [
    # Core utilities
    git
    vim
    wget
    curl
    htop
    tmux
    
    # Encryption & Security
    gnupg
    age
    openssh
    
    # VPN & Networking
    wireguard-tools
    tailscale
    tor
    torsocks
    
    # Container tools
    docker
    docker-compose
    podman
    
    # Kubernetes tools
    kubectl
    k9s
    helm
    
    # Infrastructure as Code
    terraform
    ansible
    
    # Development tools
    nodejs_20
    python312
    go
    rustc
    cargo
    
    # Security tools
    nmap
    wireshark
    tcpdump
    nftables
    
    # System monitoring
    btop
    iotop
    nethogs
    
    # File utilities
    tree
    ripgrep
    fd
    jq
    yq
  ];
  
  # Ollama service for local LLM inference
  services.ollama = {
    enable = true;
    acceleration = "cuda";  # or "rocm" for AMD GPUs
    
    # Environment variables
    environmentVariables = {
      OLLAMA_MODELS = "/var/lib/ollama/models";
      OLLAMA_HOST = "127.0.0.1:11434";
    };
  };
  
  # Tailscale for mesh networking
  services.tailscale = {
    enable = true;
    useRoutingFeatures = "both";
  };
  
  # Docker configuration
  virtualisation.docker = {
    enable = true;
    autoPrune = {
      enable = true;
      dates = "weekly";
    };
    
    # Enable experimental features
    daemon.settings = {
      experimental = true;
      metrics-addr = "127.0.0.1:9323";
    };
  };
  
  # Podman as Docker alternative
  virtualisation.podman = {
    enable = true;
    dockerCompat = false;  # Don't conflict with Docker
  };
  
  # WireGuard VPN interface
  networking.wireguard.interfaces = {
    wg0 = {
      ips = [ "10.100.0.1/24" ];
      listenPort = 51820;
      
      # Private key location (generate with: wg genkey)
      privateKeyFile = "/etc/wireguard/private.key";
      
      # Example peers (configure as needed)
      # peers = [
      #   {
      #     publicKey = "PEER_PUBLIC_KEY";
      #     allowedIPs = [ "10.100.0.2/32" ];
      #   }
      # ];
    };
  };
  
  # SSH configuration
  services.openssh = {
    enable = true;
    settings = {
      PasswordAuthentication = false;
      PermitRootLogin = "no";
      KbdInteractiveAuthentication = false;
      X11Forwarding = false;
    };
    
    # Only allow key-based authentication
    extraConfig = ''
      AllowUsers khaos
      MaxAuthTries 3
      MaxSessions 2
    '';
  };
  
  # Automatic security updates
  system.autoUpgrade = {
    enable = true;
    allowReboot = false;  # Don't auto-reboot
    dates = "weekly";
    channel = "https://nixos.org/channels/nixos-24.05";
  };
  
  # Users configuration
  users.users.khaos = {
    isNormalUser = true;
    description = "KhaosOS Operator";
    extraGroups = [ "wheel" "docker" "networkmanager" "wireshark" ];
    
    # SSH public keys (REQUIRED: Add your key before deployment!)
    # Generate with: ssh-keygen -t ed25519 -C "your_email@example.com"
    # Get public key: cat ~/.ssh/id_ed25519.pub
    openssh.authorizedKeys.keys = [
      # "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIExample... user@host"
    ];
  };
  
  # Sudo configuration
  security.sudo = {
    enable = true;
    extraConfig = ''
      Defaults timestamp_timeout=15
      Defaults lecture=never
    '';
  };
  
  # GPG agent for key management
  programs.gnupg.agent = {
    enable = true;
    enableSSHSupport = true;
    pinentryPackage = pkgs.pinentry-curses;
  };
  
  # Time zone and locale
  time.timeZone = "America/Chicago";
  
  i18n.defaultLocale = "en_US.UTF-8";
  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
  };
  
  # Nix configuration
  nix = {
    # Enable flakes and nix-command
    settings = {
      experimental-features = [ "nix-command" "flakes" ];
      auto-optimise-store = true;
    };
    
    # Garbage collection
    gc = {
      automatic = true;
      dates = "weekly";
      options = "--delete-older-than 30d";
    };
  };
  
  # System-wide environment variables
  environment.variables = {
    EDITOR = "vim";
    VISUAL = "vim";
    KHAOSOS_VERSION = "1.0-TORUK";
  };
}
