# Active Research & Conference Projects Arena

> **Live, daily-updated index of active and upcoming research projects, academic conferences, Calls for Papers (CFPs), research institute programs, formal mathematics collaborations, and research grants** across **Mathematics**, **Finance**, **Statistics**, **Data Science**, **Artificial Intelligence**, and **Economy**.

Built as the sister index to [**ActiveQuantCompetitions**](https://oogwayseinse.github.io/ActiveQuantCompetitions/) and [**ActiveMLCompetitions**](https://oogwayseinse.github.io/ActiveMLCompetitions/#live-arena).

---

## Core Disciplines Monitored

1. **Mathematics** — ICM, Joint Mathematics Meetings (JMM), SIAM Annual & Financial Math (FM), Lean 4 / Mathlib formalization projects (Prime Number Theorem+, Fermat's Last Theorem, Liquid Tensor / Sphere Eversion), AIMO Progress Prize, FrontierMath, Clay Millennium Problems, SLMath (MSRI), Isaac Newton Institute, IPAM, and ICERM thematic programs.
2. **Finance** — American Finance Association (AFA), Western Finance Association (WFA), European Finance Association (EFA), NBER Asset Pricing & Corporate Finance Summer Institute, Society for Financial Econometrics (SoFiE), Bachelier Finance Society World Congress, ACM ICAIF, INQUIRE Europe, Q-Group, and Institut Louis Bachelier / EIF research grants.
3. **Statistics** — Joint Statistical Meetings (JSM), IMS Annual Meeting, ENAR/WNAR, Royal Statistical Society (RSS) Conference, ISBA Bayesian World Meeting, Bernie/IMS World Congress, and NSF Division of Mathematical Sciences (DMS) statistics grants.
4. **Data Science** — ACM SIGKDD, IEEE ICDM, ACM WSDM, SIAM International Conference on Data Mining (SDM), VLDB, ACM SIGMOD/PODS, SemEval, and CLEF Evaluation Labs.
5. **Artificial Intelligence** — NeurIPS, ICML, ICLR, AAAI, CVPR, ACL, COLT, AISTATS, UAI, ACM FAccT, ARC Prize, and AI for Mathematical Discovery initiatives.
6. **Economy** — ASSA / AEA Annual Meeting, Econometric Society World Congress & Regional Meetings, NBER Calls for Papers, EEA-ESEM Congress, CEPR Annual Symposium, SED Annual Meeting, QuantEcon, Institute for Replication (I4R), and DoubleML open research projects.

---

## Architecture

```text
Active Research_or_Conference Projects/
├── .github/workflows/daily-update.yml   # Daily 06:00 UTC scraper + GitHub Pages deploy
├── scraper/                             # Modular Python 3.11+ aggregation pipeline
│   ├── models.py                        # ResearchProject schema + backward-compatible fields
│   ├── normalize.py                     # Multi-currency FX, dates, discipline & kind classifier
│   ├── dedupe.py                        # RapidFuzz title + URL canonicalization
│   ├── pipeline.py                      # Concurrent execution, JSON/CSV emission
│   └── sources/                         # 6 specialized source adapters
│       ├── ai_ds_conferences.py         # NeurIPS, ICML, ICLR, AAAI, KDD, CVPR, ACL, COLT, AISTATS, UAI...
│       ├── math_stats_conferences.py    # ICM, JMM, SIAM, JSM, IMS, ISBA, SLMath, Newton, IPAM, ICERM...
│       ├── finance_econ_conferences.py  # AFA, WFA, EFA, NBER, Econometric Society, SoFiE, Bachelier, ICAIF...
│       ├── open_research_projects.py    # Lean 4 / Mathlib, Polymath, AIMO, FrontierMath, QuantEcon, I4R...
│       ├── research_grants_fellowships.py # NSF DMS, ERC, Simons, Sloan, INQUIRE, Q-Group, NBER Grants...
│       └── workshop_research_challenges.py # MLContests live feed, ADIA Lab, ENS Challenge Data, SemEval...
├── data/
│   ├── projects.json                    # Full structured dataset + feed telemetry
│   ├── projects.csv                     # Flat spreadsheet export
│   └── history/                         # Daily historical snapshots
├── apps/dashboard/                      # React 18 + TypeScript + Vite 6 + Tailwind v4 SPA
└── workers/recommender/                 # Optional Cloudflare Worker proxy for Gemini 3.8 Flash
```

---

## Quickstart

### 1. Run the Python Scraper & Tests

```bash
pip install -r requirements.txt
pytest -q
python -m scraper
```

### 2. Run the React Dashboard Locally

```bash
cd apps/dashboard
npm install
npm run dev
```

### 3. Production Build

```bash
cd apps/dashboard
npm run build
```

