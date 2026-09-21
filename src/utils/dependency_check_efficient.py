import shutil
import sys
import importlib
import platform
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class Status(Enum):
    OK = "OK"
    MISSING = "MISSING"
    WARNING = "WARNING"


@dataclass
class DependencyResult:
    name: str
    status: Status
    version: Optional[str] = None
    path: Optional[str] = None
    message: str = ""


@dataclass
class DependencyReport:
    results: list[DependencyResult] = field(default_factory=list)

    def add(self, result: DependencyResult):
        self.results.append(result)

    def summary(self):
        ok = sum(1 for r in self.results if r.status == Status.OK)
        missing = sum(1 for r in self.results if r.status == Status.MISSING)
        warnings = sum(1 for r in self.results if r.status == Status.WARNING)
        return ok, missing, warnings

    def print_report(self):
        print("\n" + "=" * 60)
        print("DEPENDENCY CHECK REPORT")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print("=" * 60)

        for r in self.results:
            icon = {"OK": "[+]", "MISSING": "[-]", "WARNING": "[!]"}[r.status.value]
            version_str = f" v{r.version}" if r.version else ""
            print(f"{icon} {r.name}{version_str}")
            if r.path:
                print(f"    Path: {r.path}")
            if r.message:
                for line in r.message.split("\n"):
                    print(f"    {line}")

        print("=" * 60)
        ok, missing, warnings = self.summary()
        print(f"Summary: {ok} OK, {missing} Missing, {warnings} Warnings")
        print("=" * 60)

        return missing == 0


def check_python():
    result = DependencyResult(
        name="Python",
        status=Status.OK,
        version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )
    if sys.version_info < (3, 10):
        result.status = Status.WARNING
        result.message = "Python 3.10+ recommended for best compatibility"
    return result


def check_executable(name: str, install_hint: str = "") -> DependencyResult:
    path = shutil.which(name)
    if path:
        return DependencyResult(name=name, status=Status.OK, path=path)
    msg = f"Not found in PATH.\n{install_hint}" if install_hint else "Not found in PATH."
    return DependencyResult(name=name, status=Status.MISSING, message=msg)


def check_tshark() -> DependencyResult:
    return check_executable(
        "tshark",
        "Install Wireshark: https://www.wireshark.org/download.html\n"
        "Ensure TShark is included during installation and added to PATH.",
    )


def check_dumpcap() -> DependencyResult:
    return check_executable(
        "dumpcap",
        "Part of Wireshark suite. Install Wireshark and ensure dumpcap is in PATH.",
    )


def check_editcap() -> DependencyResult:
    return check_executable(
        "editcap",
        "Part of Wireshark suite. Install Wireshark and ensure editcap is in PATH.",
    )


def check_mergecap() -> DependencyResult:
    return check_executable(
        "mergecap",
        "Part of Wireshark suite. Install Wireshark and ensure mergecap is in PATH.",
    )


def check_npcap() -> DependencyResult:
    if platform.system() != "Windows":
        return DependencyResult(
            name="Npcap",
            status=Status.WARNING,
            message="Npcap is Windows-only. On Linux, use libpcap.",
        )
    path = shutil.which("npcap")
    if path:
        return DependencyResult(name="Npcap", status=Status.OK, path=path)
    return DependencyResult(
        name="Npcap",
        status=Status.WARNING,
        message="Npcap not found in PATH (may still be installed).\n"
        "Download from https://npcap.com/ if capturing on Windows.",
    )


def check_libpcap() -> DependencyResult:
    if platform.system() == "Windows":
        return DependencyResult(
            name="libpcap",
            status=Status.WARNING,
            message="libpcap is Linux/macOS-only. On Windows, use Npcap.",
        )
    path = shutil.which("dumpcap") or shutil.which("tcpdump")
    if path:
        return DependencyResult(name="libpcap", status=Status.OK, path=path)
    return DependencyResult(
        name="libpcap",
        status=Status.WARNING,
        message="libpcap/dumpcap not found. Install via your package manager.",
    )


def check_package(import_name: str, display_name: str, required: bool = True) -> DependencyResult:
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", None)
        if not version:
            for attr in ("VERSION", "version"):
                val = getattr(mod, attr, None)
                if val:
                    version = str(val) if not isinstance(val, str) else val
                    break
        status = Status.OK if required else Status.WARNING
        return DependencyResult(name=display_name, status=status, version=version)
    except ImportError:
        status = Status.MISSING if required else Status.WARNING
        msg = f"pip install {import_name}" if required else f"Optional: pip install {import_name}"
        return DependencyResult(name=display_name, status=status, message=msg)


def check_core_packages() -> list[DependencyResult]:
    core = [
        ("pyshark", "PyShark", True),
        ("streamlit", "Streamlit", True),
        ("pandas", "Pandas", True),
        ("numpy", "NumPy", True),
        ("requests", "Requests", True),
        ("python_dotenv", "python-dotenv", True),
    ]
    return [check_package(n, d, r) for n, d, r in core]


def check_visualization_packages() -> list[DependencyResult]:
    viz = [
        ("plotly", "Plotly", True),
        ("altair", "Altair", True),
        ("pillow", "Pillow", False),
    ]
    return [check_package(n, d, r) for n, d, r in viz]


def check_ai_packages() -> list[DependencyResult]:
    ai = [
        ("google.genai", "Google GenAI", False),
        ("httpx", "HTTPX", False),
    ]
    return [check_package(n, d, r) for n, d, r in ai]


def check_network_packages() -> list[DependencyResult]:
    net = [
        ("cryptography", "Cryptography", False),
        ("lxml", "lxml", False),
        ("pyasn1", "pyasn1", False),
        ("pyasn1_modules", "pyasn1-modules", False),
    ]
    return [check_package(n, d, r) for n, d, r in net]


def check_api_keys():
    results = []
    import os
    dotenv_path = os.path.join(os.getcwd(), ".env")
    has_dotenv_file = os.path.exists(dotenv_path)

    if has_dotenv_file:
        results.append(DependencyResult(name=".env file", status=Status.OK))
    else:
        results.append(DependencyResult(
            name=".env file",
            status=Status.WARNING,
            message="No .env file found. AI features may not work.",
        ))

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if gemini_key:
        results.append(DependencyResult(name="GEMINI_API_KEY", status=Status.OK))
    else:
        results.append(DependencyResult(
            name="GEMINI_API_KEY",
            status=Status.WARNING,
            message="Not set. AI analysis features will be disabled.",
        ))

    return results


def check_optional_tools() -> list[DependencyResult]:
    tools = [
        ("tcpdump", "tcpdump"),
        ("nmap", "Nmap"),
    ]
    return [check_executable(name, display) for name, display in tools]


def all_dependency_check() -> bool:
    report = DependencyReport()

    report.add(check_python())
    report.add(check_tshark())
    report.add(check_dumpcap())
    report.add(check_editcap())
    report.add(check_mergecap())

    if platform.system() == "Windows":
        report.add(check_npcap())
    else:
        report.add(check_libpcap())

    report.results.extend(check_core_packages())
    report.results.extend(check_visualization_packages())
    report.results.extend(check_ai_packages())
    report.results.extend(check_network_packages())
    report.results.extend(check_api_keys())
    report.results.extend(check_optional_tools())

    return report.print_report()


if __name__ == "__main__":
    success = all_dependency_check()
    sys.exit(0 if success else 1)
