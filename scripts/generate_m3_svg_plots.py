import os
from pathlib import Path

FIG_DIR = Path("C:/Users/itsme/OneDrive/Documents/PROJECTS 2026/uni projects/AI-Food-Packaging-Optimizer/docs/m3_figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

def create_indian_coverage_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" style="background-color:#ffffff; font-family:Arial, sans-serif;">
  <title>Indian Commodity Evidence Coverage (M3 Profiling)</title>
  <text x="400" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#111827">Indian Commodity Evidence Coverage</text>
  <text x="400" y="55" text-anchor="middle" font-size="14" fill="#4B5563">Milestone 3 — Data Profiling Audit</text>

  <!-- Headers -->
  <text x="50" y="90" font-size="14" font-weight="bold" fill="#1F2937">Commodity</text>
  <text x="220" y="90" font-size="14" font-weight="bold" fill="#1F2937">Proximate Comp.</text>
  <text x="370" y="90" font-size="14" font-weight="bold" fill="#1F2937">Respiration</text>
  <text x="500" y="90" font-size="14" font-weight="bold" fill="#1F2937">MAP Targets</text>
  <text x="640" y="90" font-size="14" font-weight="bold" fill="#1F2937">Shelf Life</text>

  <line x1="40" y1="100" x2="760" y2="100" stroke="#E5E7EB" stroke-width="2"/>

  <!-- Rows -->
  <!-- Alphonso Mango -->
  <text x="50" y="130" font-size="13" fill="#111827">Alphonso Mango</text>
  <rect x="220" y="115" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="131" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="115" width="100" height="22" rx="4" fill="#059669"/><text x="420" y="131" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="500" y="115" width="100" height="22" rx="4" fill="#059669"/><text x="550" y="131" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="640" y="115" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="131" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <!-- Kesar Mango -->
  <text x="50" y="170" font-size="13" fill="#111827">Kesar Mango</text>
  <rect x="220" y="155" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="171" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="155" width="100" height="22" rx="4" fill="#059669"/><text x="420" y="171" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="500" y="155" width="100" height="22" rx="4" fill="#059669"/><text x="550" y="171" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="640" y="155" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="171" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <!-- Guava -->
  <text x="50" y="210" font-size="13" fill="#111827">Guava (Allahabad)</text>
  <rect x="220" y="195" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="211" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="195" width="100" height="22" rx="4" fill="#059669"/><text x="420" y="211" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="500" y="195" width="100" height="22" rx="4" fill="#059669"/><text x="550" y="211" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="640" y="195" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="211" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <!-- Okra -->
  <text x="50" y="250" font-size="13" fill="#111827">Okra (Bhindi)</text>
  <rect x="220" y="235" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="251" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="235" width="100" height="22" rx="4" fill="#D97706"/><text x="420" y="251" font-size="11" fill="#FFFFFF" text-anchor="middle">PARTIAL</text>
  <rect x="500" y="235" width="100" height="22" rx="4" fill="#D97706"/><text x="550" y="251" font-size="11" fill="#FFFFFF" text-anchor="middle">PARTIAL</text>
  <rect x="640" y="235" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="251" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <!-- Paneer -->
  <text x="50" y="290" font-size="13" fill="#111827">Paneer (Dairy)</text>
  <rect x="220" y="275" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="291" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="275" width="100" height="22" rx="4" fill="#9CA3AF"/><text x="420" y="291" font-size="11" fill="#FFFFFF" text-anchor="middle">N/A</text>
  <rect x="500" y="275" width="100" height="22" rx="4" fill="#059669"/><text x="550" y="291" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="640" y="275" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="291" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <!-- Basmati Rice -->
  <text x="50" y="330" font-size="13" fill="#111827">Basmati Rice</text>
  <rect x="220" y="315" width="100" height="22" rx="4" fill="#059669"/><text x="270" y="331" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="370" y="315" width="100" height="22" rx="4" fill="#9CA3AF"/><text x="420" y="331" font-size="11" fill="#FFFFFF" text-anchor="middle">N/A</text>
  <rect x="500" y="315" width="100" height="22" rx="4" fill="#059669"/><text x="550" y="331" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>
  <rect x="640" y="315" width="100" height="22" rx="4" fill="#059669"/><text x="690" y="331" font-size="11" fill="#FFFFFF" text-anchor="middle">VERIFIED</text>

  <line x1="40" y1="360" x2="760" y2="360" stroke="#E5E7EB" stroke-width="2"/>
</svg>"""
    with open(FIG_DIR / "indian_commodity_coverage.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Generated indian_commodity_coverage.svg")

def create_material_barrier_svg():
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="380" style="background-color:#ffffff; font-family:Arial, sans-serif;">
  <title>Packaging Material Barrier Properties (M3 Profiling)</title>
  <text x="400" y="30" text-anchor="middle" font-size="20" font-weight="bold" fill="#111827">Packaging Material Barrier Properties (Log Scale Comparison)</text>
  <text x="400" y="55" text-anchor="middle" font-size="14" fill="#4B5563">OTR (cc/m²-day-atm) vs WVTR (g/m²-day)</text>

  <!-- Axes -->
  <line x1="120" y1="300" x2="720" y2="300" stroke="#9CA3AF" stroke-width="2"/>
  <line x1="120" y1="80" x2="120" y2="300" stroke="#9CA3AF" stroke-width="2"/>

  <!-- Material Bars for OTR -->
  <!-- LDPE -->
  <text x="140" y="320" font-size="11" fill="#1F2937">LDPE</text>
  <rect x="140" y="100" width="25" height="200" fill="#2563EB"/>
  <rect x="170" y="288" width="25" height="12" fill="#DC2626"/>

  <!-- HDPE -->
  <text x="230" y="320" font-size="11" fill="#1F2937">HDPE</text>
  <rect x="230" y="150" width="25" height="150" fill="#2563EB"/>
  <rect x="260" y="296" width="25" height="4" fill="#DC2626"/>

  <!-- BOPP -->
  <text x="320" y="320" font-size="11" fill="#1F2937">BOPP</text>
  <rect x="320" y="165" width="25" height="135" fill="#2563EB"/>
  <rect x="350" y="295" width="25" height="5" fill="#DC2626"/>

  <!-- BOPET -->
  <text x="410" y="320" font-size="11" fill="#1F2937">BOPET</text>
  <rect x="410" y="230" width="25" height="70" fill="#2563EB"/>
  <rect x="440" y="100" width="25" height="200" fill="#DC2626"/>

  <!-- BOPA 6 -->
  <text x="500" y="320" font-size="11" fill="#1F2937">BOPA 6</text>
  <rect x="500" y="260" width="25" height="40" fill="#2563EB"/>
  <rect x="530" y="80" width="25" height="220" fill="#DC2626"/>

  <!-- EVOH (F101B) -->
  <text x="590" y="320" font-size="11" fill="#1F2937">EVOH (Dry)</text>
  <rect x="590" y="295" width="25" height="5" fill="#2563EB"/>
  <rect x="620" y="70" width="25" height="230" fill="#DC2626"/>

  <!-- Legend -->
  <rect x="550" y="15" width="15" height="15" fill="#2563EB"/>
  <text x="572" y="27" font-size="12" fill="#1F2937">OTR (cc/m²-day-atm)</text>
  <rect x="680" y="15" width="15" height="15" fill="#DC2626"/>
  <text x="702" y="27" font-size="12" fill="#1F2937">WVTR (g/m²-day)</text>
</svg>"""
    with open(FIG_DIR / "material_barrier_properties.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("Generated material_barrier_properties.svg")

if __name__ == "__main__":
    create_indian_coverage_svg()
    create_material_barrier_svg()
