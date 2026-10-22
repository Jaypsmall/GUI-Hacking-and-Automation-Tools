# ⚡ GUI-Hacking-and-Automation-Tools

<p align="center">
  <b>GUI • Pentesting • Reconnaissance • Enumeration • Security Automation</b>
</p>

<p align="center">
 Una colección de interfaces gráficas y herramientas de automatización para ciberseguridad, pruebas de penetración y auditorías de seguridad autorizadas.
</p>

<p align="center">
  
![Linux](https://img.shields.io/badge/Linux-181717?style=flat&logo=linux&logoColor=FFD600)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-181717?style=flat&logo=kalilinux&logoColor=FFD600)
![Python](https://img.shields.io/badge/Python-181717?style=flat&logo=python&logoColor=FFD600)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-181717?style=flat&logo=python&logoColor=FFD600)
![Bash](https://img.shields.io/badge/Bash-181717?style=flat&logo=gnu-bash&logoColor=FFD600)

</p>

---

## 👨‍💻 Acerca de

**GUI-Hacking-and-Automation-Tools** Es una colección de interfaces gráficas personalizadas, utilidades de seguridad y proyectos de automatización diseñados para simplificar los flujos de trabajo comunes de ciberseguridad y pruebas de penetración.

El proyecto reúne varias herramientas de línea de comandos a través de interfaces gráficas, lo que permite a los investigadores de seguridad configurar y ejecutar diferentes tareas sin tener que construir manualmente comandos complejos.

El repositorio se centra en:

- 🔎 Reconnaissance
- 🌐 Web Enumeration
- ⚡ DNS Enumeration
- 🛰️ Subdomain Discovery
- 📡 Service Enumeration
- ⚡ Web Fuzzing
- 📚 Wordlist Generation
- 🔐 Authentication Auditing
- 📦 Capture & File Processing
- ⚙️ Security Workflow Automation

---

# ⚙️ Modules & Tools

```text
┌────────────────────────────────────────────────────┐
│              GUI HACKING & AUTOMATION                        │
├────────────────────────────────────────────────────┤
│                                                             │
│  🔎 Reconnaissance       → Nmap, WhatWeb, Nikto            │
│  🌐 Web Enumeration      → HTTP Headers, Technologies      │
│  ⚡ DNS Enumeration      → dig, dnsenum, DNS Records       │
│  🛰️ Subdomain Discovery  → Passive / Active Enumeration    │
│  📡 Service Enumeration  → Ports, Services, Banners        │
│  ⚡ Fuzzing              → Directories, Files, Parameters  │
│  📚 Wordlist Generation  → Custom Dictionaries             │
│  🔐 Auth Auditing        → Hydra, Credential Testing       │
│  📦 Capture Processing   → Capture Format Conversion       │
│  ⚙️ Workflow Automation  → Multi-Tool Security Workflows   │
│                                                            │
└────────────────────────────────────────────────────┘
```

---

# 🛠️ Integrated Tools

El proyecto puede proporcionar interfaces gráficas o automatización en torno a herramientas como:

| Tool | Category | Purpose |
|---|---|---|
| **Nmap** | Reconnaissance | Network and port scanning |
| **WhatWeb** | Web Recon | Web technology identification |
| **Nikto** | Web Security | Web server assessment |
| **dig** | DNS | DNS queries and record inspection |
| **dnsenum** | DNS | DNS enumeration |
| **FFUF** | Fuzzing | Web content and parameter fuzzing |
| **Hydra** | Authentication | Authorized credential auditing |
| **hcxtools** | Wireless / Capture | Capture processing and conversion |
| **Aircrack-ng** | Wireless | Wireless security auditing |

Es posible que se añadan herramientas e integraciones adicionales a medida que el proyecto evolucione.

---

# 📂 Repository Structure

```text
GUI-Hacking-and-Automation-Tools/
│
├── 📂 reconnaissance/
│   └── Scanning, service discovery and banner grabbing
│
├── 📂 web-enumeration/
│   └── Web reconnaissance, technology detection and fuzzing
│
├── 📂 dns-subdomains/
│   └── DNS enumeration and subdomain discovery
│
├── 📂 wordlists-tools/
│   └── Wordlist generators and dictionary utilities
│
├── 📂 auth-auditing/
│   └── Authorized authentication testing tools
│
├── 📂 capture-processing/
│   └── Capture and file format conversion utilities
│
├── 📂 full-suites/
│   └── Multi-purpose GUIs combining several tools
│
├── 📂 assets/
│   ├── screenshots/
│   ├── icons/
│   └── banners/
│
├── 📜 requirements.txt
├── 📜 LICENSE
└── 📜 README.md
```

---

# 🚀 Features

### 🖥️ Graphical Interfaces

Trasladar los flujos de trabajo de seguridad repetitivos de la terminal a interfaces gráficas organizadas, manteniendo el acceso a las herramientas de línea de comandos subyacentes.

### ⚙️ Command Automation

Configure las herramientas de seguridad comunes a través de una interfaz gráfica de usuario (GUI) en lugar de construir manualmente argumentos complejos de línea de comandos.

### 🔎 Reconnaissance

Combine el escaneo, la detección de servicios, la identificación de tecnología y la enumeración en flujos de trabajo organizados.

### 🌐 Web Enumeration

Realizar reconocimiento web, identificación de tecnologías, análisis HTTP y pruebas de fuzzing desde interfaces dedicadas.

### ⚡ DNS & Subdomain Enumeration

Organice las consultas DNS, la enumeración de registros y el descubrimiento de subdominios mediante herramientas gráficas. 

### 📚 Custom Wordlists

Generar y manipular diccionarios personalizados para pruebas de seguridad autorizadas.

### 🔐 Authentication Auditing

Proporcionar interfaces para configurar herramientas de auditoría de autenticación y flujos de trabajo controlados de prueba de credenciales.

### 📦 Capture & File Processing

Utilidades para procesar y convertir archivos de captura relacionados con la seguridad a los formatos requeridos por las herramientas de análisis. 

### ⚙️ Modular Architecture

Cada proyecto puede funcionar de forma independiente, lo que permite utilizar herramientas individuales sin necesidad de todo el repositorio. 

---

# 🔄 Example Workflow

Un flujo de trabajo de reconocimiento típico se puede organizar de esta manera:

```text
                         TARGET
                            │
                            ▼
                    ┌──────────────┐
                    │     NMAP     │
                    └──────┬───────┘
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
           OPEN PORTS             SERVICES
                │                     │
                └──────────┬──────────┘
                           ▼
                    ┌──────────────┐
                    │   WHATWEB    │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    NIKTO     │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  DNS / ENUM  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  SUBDOMAINS  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     FFUF     │
                    └──────┬───────┘
                           │
                           ▼
                        RESULTS
```

El propósito de la capa de automatización es organizar estas etapas sin ocultar lo que sucede subyacente.

---

# 🚀 Requirements

El repositorio está diseñado principalmente para entornos de seguridad basados ​​en Linux.

### Recommended

```text
Kali Linux
Parrot Security OS
Debian
Ubuntu
Other Debian-based distributions
```

### Base dependencies

Dependiendo de la interfaz gráfica de usuario (GUI) específica, pueden ser necesarias las siguientes herramientas:

```text
Python 3
pip
Nmap
WhatWeb
Nikto
dnsenum
dig
FFUF
Hydra
hcxtools
Aircrack-ng
```

---

# 📦 Installation

## 1. Clone the repository

```bash
git clone https://github.com/Jaypsmall/GUI-Hacking-and-Automation-Tools.git
cd GUI-Hacking-and-Automation-Tools
```

## 2. Install system dependencies

On Debian, Ubuntu or Kali Linux:

```bash
sudo apt update

sudo apt install -y \
    python3 \
    python3-pip \
    nmap \
    whatweb \
    nikto \
    dnsenum \
    bind9-dnsutils \
    hydra \
    hcxtools \
    aircrack-ng
```

> Package names can vary between distributions and versions.

## 3. Install Python dependencies

If the selected GUI provides a `requirements.txt` file:

```bash
python3 -m pip install -r requirements.txt
```

For systems that restrict global Python package installation, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install -r requirements.txt
```

## 4. Launch a GUI

Each project may have its own entry point.

For example:

```bash
python3 main.py
```

or:

```bash
python3 reconnaissance/main.py
```

Refer to the README or documentation inside each module for its specific requirements and launch command.

---

# 🔧 Verify Installed Tools

You can verify the main dependencies with:

```bash
nmap --version
whatweb --version
nikto -Version
dig -v
dnsenum --help
ffuf -V
hydra -h
```

For wireless/capture utilities:

```bash
hcxpcapngtool --help
aircrack-ng --help
```

---

# 👨‍💻 Development

El repositorio está diseñado como una colección de proyectos independientes en lugar de una única aplicación monolítica.

This makes it possible to:

```text
┌─────────────────────────────┐
│       SECURITY TOOLS        │
└──────────────┬──────────────┘
               │
               ▼
      ┌─────────────────┐
      │ AUTOMATION LAYER│
      └────────┬────────┘
               │
               ▼
       ┌───────────────┐
       │      GUI      │
       └───────┬───────┘
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
      RECON   ENUM   AUDIT
```

Individual GUIs can therefore be developed, tested and maintained independently.

---

# 📸 Screenshots

Screenshots and demonstrations of the individual tools will be added as development continues.

```text
assets/
└── screenshots/
```

---

# 🚧 Roadmap

```text
[x] Nmap GUI
[x] Web reconnaissance
[x] DNS utilities
[x] Subdomain enumeration
[x] Wordlist generation
[x] Fuzzing interfaces
[x] Authentication auditing
[x] Capture / file processing

[ ] Unified launcher
[ ] Central result manager
[ ] Scan history
[ ] Workspace system
[ ] Report generation
[ ] Export results
[ ] Multi-tool pipelines
[ ] Plugin architecture
[ ] Configuration profiles
[ ] Improved Windows compatibility
[ ] Improved result visualization
```

---

# 🎯 Project Goals

The long-term goal is to build a practical collection of GUIs that can act as an automation layer around established security tools.

```text
              EXISTING SECURITY TOOLS
                         │
                         ▼
                ┌────────────────┐
                │   AUTOMATION   │
                └───────┬────────┘
                        │
                        ▼
                ┌────────────────┐
                │      GUIs      │
                └───────┬────────┘
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
        RECON        ENUMERATION     AUDIT
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                     RESULTS
```

The idea is simple:

> **Keep the power of the command line, add the convenience of a GUI, and automate the repetitive parts.**

---

# ⚠️ Disclaimer

This repository is intended for:

- Cybersecurity education
- Security research
- CTF environments
- Personal laboratories
- Authorized penetration testing
- Systems owned by the user
- Systems for which explicit authorization has been granted

**Do not use these tools against systems, networks, accounts or services without authorization.**

Some utilities included in this repository can perform security-sensitive operations, including network scanning, fuzzing and authentication testing.

The author does not assume responsibility for damage, data loss, unauthorized access or any other consequences resulting from misuse of these tools.

Users are solely responsible for complying with applicable laws and obtaining the necessary authorization before performing security testing.

---

# 🤝 Contributing

Contributions are welcome.

You can contribute by:

```text
• Adding new GUIs
• Integrating additional security tools
• Improving automation
• Fixing bugs
• Improving interfaces
• Adding documentation
• Improving compatibility
• Adding new security utilities
• Optimizing existing modules
```

---

# ⭐ Support

If you find the project useful:

```text
⭐ Star the repository
🍴 Fork the project
🐛 Report bugs
💡 Suggest features
🔧 Submit improvements
```

---

# 📜 License

This project is distributed under the license specified in:

```text
LICENSE
```

---

# ⚡ GUI HACKING & AUTOMATION TOOLS

<p align="center">
<b>RECON • ENUMERATION • FUZZING • AUTOMATION</b>
<br>
  
![Linux](https://img.shields.io/badge/Linux-181717?style=flat&logo=linux&logoColor=FFD600)
![Kali Linux](https://img.shields.io/badge/Kali_Linux-181717?style=flat&logo=kalilinux&logoColor=FFD600)
![Python](https://img.shields.io/badge/Python-181717?style=flat&logo=python&logoColor=FFD600)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-181717?style=flat&logo=python&logoColor=FFD600)
![Bash](https://img.shields.io/badge/Bash-181717?style=flat&logo=gnu-bash&logoColor=FFD600)

<sub>Cybersecurity research • Security education • Authorized auditing</sub>

</p>
