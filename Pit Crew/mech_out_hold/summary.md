### PitCrew — Mechanic Summary

- **Decision:** `HOLD`  

- **Evaluated at (ET):** 2025-09-10T15:11:53.159706Z

- **Mode:** mock (seed=7, rho=-0.6, fr_sd=0.005, xai_sd=0.01)


| Profile | KPI | Failure Rate | Explainability | Events | Actions |
|---|---:|---:|---:|---:|---:|
| strict | 57.8 | 0.019 | 0.96 | 200 | 220 |
| explore | 48.8 | 0.039 | 0.90 | 200 | 208 |

**Overall KPI (weights strict=0.70, explore=0.30):** `55.1`


<sup>Visual summary — Pit Lanes</sup>

<svg xmlns='http://www.w3.org/2000/svg' width='720' height='236' role='img' aria-label='PitCrew — Strict vs Explore'><rect width='720' height='236' fill='#0D1117'/>
    <defs>
      <pattern id="expHatch-pit" patternUnits="userSpaceOnUse" width="6" height="6"
               patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="6" stroke="#F59E0B" stroke-width="2" stroke-opacity="0.6"/>
      </pattern>
      <pattern id="checkers-pit" width="6" height="6" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="3" height="3" fill="#fff"/><rect x="3" y="3" width="3" height="3" fill="#fff"/>
        <rect x="3" y="0" width="3" height="3" fill="#000"/><rect x="0" y="3" width="3" height="3" fill="#000"/>
      </pattern>
    </defs>
    <text x='132.0' y='18.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>PitCrew — Strict vs Explore</text><g transform='translate(692,10)'><circle cx='10' cy='10' r='9' fill='#D73A49'/><text x='10.0' y='10.5' fill='#fff' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='middle' dominant-baseline='middle'>!</text></g><line x1='132.0' y1='32.0' x2='132.0' y2='206.0' stroke='#1F2937' stroke-width='1' opacity='0.75' /><text x='132.0' y='218.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='middle' dominant-baseline='middle'>0</text><line x1='417.0' y1='32.0' x2='417.0' y2='206.0' stroke='#1F2937' stroke-width='1' opacity='0.75' /><text x='417.0' y='218.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='middle' dominant-baseline='middle'>50</text><line x1='702.0' y1='32.0' x2='702.0' y2='206.0' stroke='#1F2937' stroke-width='1' opacity='0.75' /><text x='702.0' y='218.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='middle' dominant-baseline='middle'>100</text><line x1='673.5' y1='34.0' x2='673.5' y2='206.0' stroke='#EF4444' stroke-width='1.5' stroke-dasharray='4,3' opacity='0.85'/><line x1='160.5' y1='34.0' x2='160.5' y2='206.0' stroke='#EF4444' stroke-width='1.5' opacity='0.85'/><text x='122.0' y='47.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>KPI</text><path d='M132,54 L132,43 L135,40 L461.46,40 L461.46,54 Z' fill='#2563EB' opacity='0.95'/><text x='467.5' y='47.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>S 57.8%</text><path d='M132,74 L132,63 L135,60 L410.15999999999997,60 L410.15999999999997,74 Z' fill='#F59E0B' opacity='0.95'/><rect x='132.0' y='60.0' width='278.2' height='14.0' fill='url(#expHatch-pit)' opacity='0.9'/><text x='416.2' y='67.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>E 48.8%</text><text x='122.0' y='95.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>Explainability</text><path d='M132,102 L132,91 L135,88 L679.542,88 L679.542,102 Z' fill='#2563EB' opacity='0.95'/><text x='685.5' y='95.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>S 96.1%</text><path d='M132,122 L132,111 L135,108 L644.316,108 L644.316,122 Z' fill='#F59E0B' opacity='0.95'/><rect x='132.0' y='108.0' width='512.3' height='14.0' fill='url(#expHatch-pit)' opacity='0.9'/><text x='650.3' y='115.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>E 89.9%</text><rect x='669.5' y='88.0' width='10' height='14.0' fill='url(#checkers-pit)'/><text x='122.0' y='143.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>Failure rate</text><path d='M132,150 L132,139 L135,136 L142.659,136 L142.659,150 Z' fill='#2563EB' opacity='0.95'/><text x='148.7' y='143.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>S 1.9%</text><path d='M132,170 L132,159 L135,156 L154.173,156 L154.173,170 Z' fill='#F59E0B' opacity='0.95'/><rect x='132.0' y='156.0' width='22.2' height='14.0' fill='url(#expHatch-pit)' opacity='0.9'/><text x='160.2' y='163.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>E 3.9%</text><rect x='132.0' y='212.0' width='14' height='10' fill='#2563EB'/><text x='152.0' y='217.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>Strict</text><rect x='202.0' y='212.0' width='14' height='10' fill='#F59E0B'/><rect x='202.0' y='212.0' width='14' height='10' fill='url(#expHatch-pit)' opacity='0.9'/><text x='222.0' y='217.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>Explore</text><text x='702.0' y='217.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>0–100%</text></svg>

<sup>Outcome mix (Redline Stacks)</sup>

<svg xmlns='http://www.w3.org/2000/svg' width='420' height='160' role='img' aria-label='PitCrew — Redline Stacks'><rect width='420' height='160' fill='#0D1117'/>
    <defs>
      <pattern id="expHatch-stack" patternUnits="userSpaceOnUse" width="6" height="6"
               patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="6" stroke="#F59E0B" stroke-width="2" stroke-opacity="0.6"/>
      </pattern>
      <pattern id="checkers-stack" width="6" height="6" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="3" height="3" fill="#fff"/><rect x="3" y="3" width="3" height="3" fill="#fff"/>
        <rect x="3" y="0" width="3" height="3" fill="#000"/><rect x="0" y="3" width="3" height="3" fill="#000"/>
      </pattern>
    </defs>
    <text x='90.0' y='20.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>Redline Stacks — outcome mix</text><rect x='90.0' y='38.0' width='274.8' height='16.0' fill='#2563EB' opacity='0.95'/><rect x='364.8' y='38.0' width='5.2' height='16.0' fill='#D73A49' opacity='0.95'/><text x='80.0' y='46.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>strict</text><line x1='104.0' y1='34.0' x2='104.0' y2='58.0' stroke='#EF4444' stroke-width='2'/><text x='378.0' y='46.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>98.1% ok / 1.9% fail</text><rect x='90.0' y='76.0' width='269.1' height='16.0' fill='#F59E0B' opacity='0.95'/><rect x='90.0' y='76.0' width='269.1' height='16.0' fill='url(#expHatch-stack)' opacity='0.9'/><rect x='359.1' y='76.0' width='10.9' height='16.0' fill='#D73A49' opacity='0.95'/><text x='80.0' y='84.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>explore</text><line x1='104.0' y1='72.0' x2='104.0' y2='96.0' stroke='#EF4444' stroke-width='2'/><text x='378.0' y='84.0' fill='#9CA3AF' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>96.1% ok / 3.9% fail</text></svg>

<sup>Explainability (Telemetry)</sup>

<svg xmlns='http://www.w3.org/2000/svg' width='420' height='160' role='img' aria-label='PitCrew — Telemetry Bars'><rect width='420' height='160' fill='#0D1117'/>
    <defs>
      <pattern id="expHatch-tele" patternUnits="userSpaceOnUse" width="6" height="6"
               patternTransform="rotate(45)">
        <line x1="0" y1="0" x2="0" y2="6" stroke="#F59E0B" stroke-width="2" stroke-opacity="0.6"/>
      </pattern>
      <pattern id="checkers-tele" width="6" height="6" patternUnits="userSpaceOnUse">
        <rect x="0" y="0" width="3" height="3" fill="#fff"/><rect x="3" y="3" width="3" height="3" fill="#fff"/>
        <rect x="3" y="0" width="3" height="3" fill="#000"/><rect x="0" y="3" width="3" height="3" fill="#000"/>
      </pattern>
    </defs>
    <text x='90.0' y='20.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>Telemetry — explainability</text><line x1='356.0' y1='28.0' x2='356.0' y2='146.0' stroke='#EF4444' stroke-dasharray='4,3' stroke-width='2'/><path d='M90,54 L90,41 L93,38 L358.968,38 L358.968,54 Z' fill='#2563EB' opacity='0.95'/><rect x='349.0' y='38.0' width='10' height='16.0' fill='url(#checkers-tele)'/><text x='80.0' y='46.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>strict</text><text x='365.0' y='46.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>96.1%</text><path d='M90,92 L90,79 L93,76 L341.664,76 L341.664,92 Z' fill='#F59E0B' opacity='0.95'/><rect x='90.0' y='76.0' width='251.7' height='16.0' fill='url(#expHatch-tele)' opacity='0.9'/><text x='80.0' y='84.0' fill='#E5E7EB' font-size='12' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='end' dominant-baseline='middle'>explore</text><text x='347.7' y='84.0' fill='#E5E7EB' font-size='10' font-family='-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif' text-anchor='start' dominant-baseline='middle'>89.9%</text></svg>