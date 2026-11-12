/** Ilustrações próprias em SVG. As cores vêm dos tokens, então funcionam no tema claro e no escuro. */
import type { Alvo } from "@/lib/alvos";

export function Logo() {
  return (
    <>
      <span
        aria-hidden
        style={{ width: 36, height: 36, borderRadius: 11, background: "var(--accent)", color: "var(--accent-ink)", display: "grid", placeItems: "center" }}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
          <path d="M12 4v16M4 12h16" />
        </svg>
      </span>
      Plantão de Estudo
    </>
  );
}

/** Capa de cada cartão: hospital, campus ou cidade, na cor do alvo. */
export function ArteAlvo({ alvo }: { alvo: Alvo }) {
  const c = `var(${alvo.cor})`;
  const suave = `color-mix(in srgb, var(${alvo.cor}) 35%, var(--surface))`;
  const janela = "var(--surface)";
  const janelas = (x: number, y: number, n: number, colunas: number) =>
    Array.from({ length: n }, (_, i) => (
      <rect key={`${x}-${y}-${i}`} x={x + (i % colunas) * 14} y={y + Math.floor(i / colunas) * 13} width="8" height="7" rx="1.5" fill={janela} />
    ));
  return (
    <svg viewBox="0 0 300 92" preserveAspectRatio="xMidYMax slice" aria-hidden>
      <circle cx="250" cy="22" r="12" fill={suave} />
      <path d="M0 92h300" stroke={c} strokeWidth="2" />
      {alvo.forma === "hosp" && (
        <>
          <rect x="90" y="18" width="120" height="74" rx="4" fill={c} />
          {janelas(102, 30, 24, 8)}
          <rect x="138" y="70" width="24" height="22" fill={janela} />
          <rect x="141" y="4" width="18" height="18" rx="3" fill={janela} stroke={c} strokeWidth="2" />
          <path d="M150 8v10M145 13h10" stroke={c} strokeWidth="2.6" />
          <rect x="40" y="46" width="44" height="46" rx="3" fill={suave} />
          <rect x="216" y="40" width="50" height="52" rx="3" fill={suave} />
        </>
      )}
      {alvo.forma === "uni" && (
        <>
          <path d="M70 40l80-28 80 28z" fill={c} />
          <rect x="80" y="40" width="140" height="10" fill={c} />
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <rect key={i} x={90 + i * 22} y="52" width="9" height="34" rx="2" fill={c} />
          ))}
          <rect x="72" y="86" width="156" height="6" fill={c} />
          <circle cx="35" cy="70" r="16" fill={suave} />
          <rect x="33" y="78" width="4" height="14" fill={suave} />
          <circle cx="265" cy="68" r="18" fill={suave} />
          <rect x="263" y="78" width="4" height="14" fill={suave} />
        </>
      )}
      {alvo.forma === "city" && (
        <>
          <rect x="20" y="40" width="46" height="52" rx="3" fill={suave} />
          <rect x="72" y="20" width="52" height="72" rx="3" fill={c} />
          {janelas(80, 30, 12, 3)}
          <rect x="130" y="50" width="40" height="42" rx="3" fill={suave} />
          <rect x="176" y="10" width="44" height="82" rx="3" fill={c} />
          {janelas(183, 20, 15, 3)}
          <rect x="226" y="44" width="56" height="48" rx="3" fill={suave} />
        </>
      )}
    </svg>
  );
}

/** Fundo da capa: blocos de cor, linha de ECG, relógio de plantão, estetoscópio e prancheta. */
export function ArteCapa() {
  return (
    <svg viewBox="0 0 520 600" fill="none" aria-hidden>
      <circle cx="390" cy="150" r="130" fill="color-mix(in srgb, var(--accent) 16%, transparent)" />
      <circle cx="120" cy="470" r="110" fill="color-mix(in srgb, var(--coral) 14%, transparent)" />
      <path d="M0 330h130l22-50 30 110 28-150 26 120 18-30h266" stroke="var(--accent)" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" opacity=".55" />
      <g transform="translate(400 420)">
        <circle r="54" fill="var(--surface)" stroke="var(--ink)" strokeWidth="5" />
        <path d="M0-34v34l22 14" stroke="var(--coral)" strokeWidth="6" strokeLinecap="round" />
        <circle r="5" fill="var(--ink)" />
        <path d="M-14-62h28" stroke="var(--ink)" strokeWidth="7" strokeLinecap="round" />
      </g>
      <g transform="translate(40 70)">
        <rect width="104" height="132" rx="14" fill="var(--surface)" stroke="var(--ink)" strokeWidth="5" />
        <rect x="30" y="-10" width="44" height="22" rx="7" fill="var(--gold)" stroke="var(--ink)" strokeWidth="5" />
        <path d="M22 44l8 8 14-16M22 78l8 8 14-16" stroke="var(--accent)" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M56 46h28M56 80h28M22 110h62" stroke="var(--line)" strokeWidth="6" strokeLinecap="round" />
      </g>
      <path
        d="M430 250c0 60-30 90-70 90s-60-28-60-62v-40M300 238a12 12 0 1 0 0-.1M430 250c20 0 30 18 30 34s-14 30-30 30-30-14-30-30"
        stroke="var(--ink)"
        strokeWidth="6"
        strokeLinecap="round"
        opacity=".85"
      />
      <circle cx="430" cy="314" r="14" fill="var(--accent)" stroke="var(--ink)" strokeWidth="5" />
    </svg>
  );
}
