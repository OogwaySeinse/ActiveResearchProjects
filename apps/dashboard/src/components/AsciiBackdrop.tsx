import { useEffect, useRef } from 'react';

interface Cluster {
  x: number;
  y: number;
  vx: number;
  vy: number;
  rows: string[];
  color: string;
}

const PALETTE = [
  'rgba(244, 240, 224, 0.20)',
  'rgba(196, 200, 184, 0.16)',
  'rgba(200, 169, 110, 0.15)',
  'rgba(107, 158, 120, 0.14)',
];

// Drifting ASCII clusters with mathematical, statistical, financial, AI & economic formulas
const PATTERNS: string[][] = [
  [
    '   .  *  ∫_Ω ∇·F dV  .  ',
    ' .  +  ===  :  ===  + . ',
    '   :  [ ∂u/∂t = Δu ] :  ',
    ' .  *  ===  .  ===  * . ',
    '     .   +   :   .      ',
  ],
  [
    '  /\\  /\\  dS = μSdt + σSdW ',
    ' /  \\/  \\  *  .  +  .     ',
    ' \\      / === [ E[R|ℱ_t] ] ',
    '  \\    /  .  *  :  +  .   ',
  ],
  [
    '   +---[ θ* = argmin L(θ) ]---+ ',
    '   |  .  :  #  *  #  :  .     | ',
    '   |  *  P(Y|X,do(Z))   *     | ',
    '   +--------------------------+ ',
  ],
  [
    '      .   *   .     ',
    '   *  .:::#:::.  *  ',
    '  .  .::#####::.  . ',
    '   *  .:::#:::.  *  ',
    '      .   *   .     ',
  ],
  [
    '  ::  01001101  ::  ',
    '  ::  10110100  ::  ',
    '  ::  [LEAN 4]  ::  ',
    '  ::  ⊢ ∀ ε > 0 ::  ',
  ],
  [
    '   .  +  *  +  .   ',
    '  +  /-------\\  +  ',
    '  *  | L_t   |  *  ',
    '  +  \\-------/  +  ',
    '   .  +  *  +  .   ',
  ],
];

export function AsciiBackdrop() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationId = 0;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', handleResize);

    const clusterCount = Math.min(14, Math.max(7, Math.floor((width * height) / 140000)));
    const clusters: Cluster[] = Array.from({ length: clusterCount }, (_, idx) => {
      const pattern = PATTERNS[idx % PATTERNS.length];
      return {
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 0.16,
        vy: (Math.random() - 0.5) * 0.12,
        rows: pattern,
        color: PALETTE[idx % PALETTE.length],
      };
    });

    let tick = 0;
    const render = () => {
      tick += 1;
      ctx.clearRect(0, 0, width, height);
      ctx.font = '11px "JetBrains Mono", monospace';
      ctx.textBaseline = 'top';

      for (const c of clusters) {
        c.x += c.vx;
        c.y += c.vy;

        if (c.x > width + 180) c.x = -260;
        if (c.x < -260) c.x = width + 180;
        if (c.y > height + 120) c.y = -120;
        if (c.y < -120) c.y = height + 120;

        ctx.fillStyle = c.color;
        for (let r = 0; r < c.rows.length; r++) {
          const shimmer = Math.sin((tick + r * 17) * 0.025) > 0.65 ? 0.85 : 1;
          ctx.globalAlpha = shimmer;
          ctx.fillText(c.rows[r], c.x, c.y + r * 14);
        }
      }
      ctx.globalAlpha = 1;
      animationId = window.requestAnimationFrame(render);
    };

    render();

    return () => {
      window.cancelAnimationFrame(animationId);
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 opacity-75"
    />
  );
}

