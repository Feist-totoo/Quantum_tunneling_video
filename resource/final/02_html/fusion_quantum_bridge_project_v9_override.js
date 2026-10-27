// Resolve delivery override for fusion_quantum_bridge_project_v9.html.
// The original V3 implementation is intentionally preserved in the HTML for comparison.

function arrow2D(x1, y1, x2, y2, color, alpha = 1, widthPx = 3, head = 14) {
  line(x1, y1, x2, y2, color, widthPx, alpha);
  const angle = Math.atan2(y2 - y1, x2 - x1);
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - head * Math.cos(angle - .48), y2 - head * Math.sin(angle - .48));
  ctx.lineTo(x2 - head * Math.cos(angle + .48), y2 - head * Math.sin(angle + .48));
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

function drawContinuousSunV7(x, topY, radius, brightness, t, alpha = 1) {
  // The same sun exists from the first frame onward. When its radius is huge
  // and its centre is below the canvas, only the natural limb and halo of the
  // full sun are visible; there is no second renderer and no later fade-in.
  ctx.save();
  ctx.translate(x, topY + radius);
  ctx.globalAlpha = alpha;

  // At the opening scale the physical disc is still far below frame.  Keep
  // only a very transparent amber limb in view; reveal the same disc
  // continuously as the virtual camera pulls back.  This prevents the first
  // frames from reading as an orange-red solar body that appears too early.
  const coreReveal = smooth((height * 3.05 - radius) / (height * 2.15));
  const rimStrength = lerp(.16, 1.0, coreReveal);

  // Keep the original solar edge glow, but cap its thickness in screen space.
  // Otherwise a 100:1 off-screen sun would tint the entire canvas instead of
  // leaving the requested shallow luminous rim near the lower boundary.
  const haloSpread = Math.min(radius * .72, height * .23);
  const haloInner = Math.max(0, radius - haloSpread * .24);
  const haloOuter = radius + haloSpread;
  const halo = ctx.createRadialGradient(0, 0, haloInner, 0, 0, haloOuter);
  halo.addColorStop(0, 'rgba(255,214,86,0)');
  halo.addColorStop(.16, `rgba(255,229,137,${.64 * brightness * rimStrength})`);
  halo.addColorStop(.34, `rgba(255,174,68,${.28 * brightness * rimStrength})`);
  halo.addColorStop(1, 'rgba(252,98,85,0)');
  ctx.fillStyle = halo;
  ctx.beginPath(); ctx.arc(0, 0, haloOuter, 0, Math.PI * 2); ctx.fill();

  const core = ctx.createRadialGradient(-radius * .28, -radius * .32, radius * .06, 0, 0, radius);
  core.addColorStop(0, '#fffde3');
  core.addColorStop(.34, '#ffd65f');
  core.addColorStop(.72, C.orange);
  core.addColorStop(1, '#8b2419');
  ctx.globalAlpha = alpha * coreReveal;
  ctx.fillStyle = core;
  ctx.beginPath(); ctx.arc(0, 0, radius, 0, Math.PI * 2); ctx.fill();

  // Surface texture becomes resolvable gradually as the same disc recedes.
  const detailAlpha = smooth((width * 1.7 - radius) / (width * .82));
  ctx.globalCompositeOperation = 'screen';
  ctx.globalAlpha = alpha * detailAlpha * coreReveal;
  for (let i = 0; i < 10; i++) {
    const a = i * .93 + t * (.045 + i * .001);
    const rr = radius * (.18 + seeded(i + 77) * .64);
    ctx.fillStyle = `rgba(255,255,190,${.05 + seeded(i + 21) * .06})`;
    ctx.beginPath();
    ctx.ellipse(Math.cos(a) * rr * .62, Math.sin(a * 1.23) * rr * .42, radius * (.13 + seeded(i + 3) * .11), radius * .06, a, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function sceneSunV7(t) {
  if (t >= 9.05) return;
  const exit = 1 - smooth((t - 8.55) / (9.033333 - 8.55));
  const titleIn = heavyOut(t / .52);
  // The sun reaches its complete on-screen composition at F00177.
  const camera = heavyInOut((t - .55) / (2.95 - .55));

  // The measured Chinese title width is the unit of scale. Both title and sun
  // share the same exponential camera zoom, so sun diameter / title width = 100.
  const baseTitleSize = Math.min(190, width * .099);
  ctx.save();
  ctx.font = `720 ${baseTitleSize}px ${FONT}`;
  const baseTitleWidth = ctx.measureText('核聚变').width;
  ctx.restore();
  const finalSunDiameter = Math.min(width * .365, height * .64);
  const finalScale = finalSunDiameter / (baseTitleWidth * 100);
  const cameraScale = Math.exp(lerp(0, Math.log(finalScale), camera));
  const titleSize = baseTitleSize * cameraScale;
  const titleWidth = baseTitleWidth * cameraScale;
  const sunRadius = titleWidth * 50;
  const sunTop = lerp(height * .858, height * .248, camera);
  const brightness = lerp(.86, 1.10, smooth((t - 1.65) / 1.30));
  drawContinuousSunV7(width / 2, sunTop, sunRadius, brightness, t, exit);

  const titleY = lerp(height * .465, height * .242, camera);
  const thresholdAlpha = smooth((titleWidth - 8) / 16);
  const titleAlpha = titleIn * exit * thresholdAlpha;
  if (titleAlpha > .001) {
    label('核聚变', width / 2, titleY, titleSize, C.white, 'center', 720, FONT, titleAlpha);
    const halfLine = titleWidth * .34;
    line(width / 2 - halfLine, titleY + titleSize * .68, width / 2 + halfLine, titleY + titleSize * .68, C.cyan, Math.max(.8, 3 * cameraScale), titleAlpha * .92);
  }

  // F00350: the age callout only begins after the spoken phrase has landed.
  const ageIn = smooth((t - 5.833333) / .58) * exit;
  label('46 亿年', width * .72, height * .54, 48, C.orange, 'left', 720, FONT, ageIn);
  line(width * .655, height * .54, width * .705, height * .54, C.orange, 2, ageIn);
}

function formatTemperatureTickV7(value) {
  if (value === 0) return '0';
  return value.toFixed(2).replace(/0+$/, '').replace(/\.$/, '');
}

function drawAxisTickLayerV7(left, right, axisY, gridTop, axisMax, step, alpha, labelScale) {
  if (alpha <= .002) return;
  const axisW = right - left;
  const minorStep = step / 5;
  ctx.save();
  ctx.beginPath();
  ctx.rect(left - 2, gridTop, axisW + 4, axisY - gridTop + 64);
  ctx.clip();

  for (let value = minorStep; value <= axisMax + 1e-6; value += minorStep) {
    const x = left + axisW * (value / axisMax);
    const isMajor = Math.abs(value / step - Math.round(value / step)) < 1e-5;
    line(x, gridTop, x, axisY, isMajor ? C.muted : '#36404c', isMajor ? 1.4 : .75, alpha * (isMajor ? .28 : .16));
    line(x, axisY - (isMajor ? 15 : 8), x, axisY + (isMajor ? 15 : 8), isMajor ? C.yellow : C.muted, isMajor ? 2.2 : 1.2, alpha * (isMajor ? .92 : .38));
    if (isMajor) {
      const align = x > right - 45 ? 'right' : (x < left + 45 ? 'left' : 'center');
      label(formatTemperatureTickV7(value), x, axisY + 42, 23 * labelScale, C.yellow, align, 700, MONO, alpha);
    }
  }
  ctx.restore();
}

function drawTemperatureChartV7(t) {
  if (t < 9.033333 || t >= 22.116667) return;
  // F00542-F00680: the full-width axis enters under the physicists' estimate.
  const enter = smooth((t - 9.033333) / (11.333333 - 9.033333));
  // F01250-F01327: hand the frame continuously to the reaction diagram.
  const exit = 1 - smooth((t - 20.833333) / (22.116667 - 20.833333));
  // F00858-F01106: constant-speed growth with no pause at the hand-off.
  const redP = clamp((t - 14.30) / (18.433333 - 14.30));
  // F01107 is already the first zoomed frame; F01171 is the settled 10^8 view.
  const zoomStart = 18.433333;
  const zoomDuration = 19.516667 - zoomStart;
  const zoomLinear = clamp((t - zoomStart) / zoomDuration);
  const zoomP = 1 - Math.pow(1 - zoomLinear, 2.2); // fast start, smooth deceleration
  const zoomHighlight = Math.sin(Math.PI * zoomLinear);
  const alpha = enter * exit;
  const axisW = width * (2 / 3);
  const left = width / 2 - axisW / 2;
  const right = width / 2 + axisW / 2;
  const axisY = height * .775;
  const redY = height * .395;
  const blueY = height * .565;
  const barH = Math.min(58, height * .054);
  const axisMax = lerp(1.5, 10, zoomP); // Units of 10^7 K.
  const blueW = axisW * (1.5 / axisMax);
  const redW = axisW * redP;

  ctx.save();
  ctx.globalAlpha = alpha;
  label('中心温度与点火阈值', width / 2, height * .135, 42, C.white, 'center', 700, FONT);

  // GeoGebra-like zoom: tick values stay meaningful while their screen
  // spacing compresses. Successive "nice" step layers crossfade as new ticks
  // enter from the right edge. No scale-limit card or per-grid annotation.
  const fineWeight = 1 - smooth((zoomP - .12) / .20);
  const halfWeight = smooth((zoomP - .08) / .19) * (1 - smooth((zoomP - .42) / .20));
  const oneWeight = smooth((zoomP - .36) / .19) * (1 - smooth((zoomP - .72) / .18));
  const twoWeight = smooth((zoomP - .65) / .22);
  const labelScale = 1 + .09 * zoomHighlight;
  const gridTop = redY - 44;
  drawAxisTickLayerV7(left, right, axisY, gridTop, axisMax, .25, fineWeight, labelScale);
  drawAxisTickLayerV7(left, right, axisY, gridTop, axisMax, .5, halfWeight, labelScale);
  drawAxisTickLayerV7(left, right, axisY, gridTop, axisMax, 1, oneWeight, labelScale);
  drawAxisTickLayerV7(left, right, axisY, gridTop, axisMax, 2, twoWeight, labelScale);
  line(left, axisY, right, axisY, C.muted, 2.2, .84);
  line(left, axisY - 18, left, axisY + 18, C.yellow, 2.2, .92);
  label('0', left, axisY + 42, 23 * labelScale, C.yellow, 'center', 700, MONO);
  label('× 10⁷ K', right, axisY + 82, 20, C.muted, 'right', 600, MONO);

  ctx.fillStyle = C.red;
  roundedRectPath(left, redY, redW, barH, 12); ctx.fill();
  label('经典点火阈值  1.0 × 10⁸ K', left, redY - 34, 24, C.red, 'left', 700, FONT, smooth((t - 14.30) / .38));

  ctx.fillStyle = C.blue;
  roundedRectPath(left, blueY, blueW, barH, 12); ctx.fill();
  label('太阳中心  1.5 × 10⁷ K', left, blueY - 34, 24, C.blue, 'left', 700, FONT, 1);
  if (blueW > 6) {
    ctx.fillStyle = C.white;
    ctx.beginPath(); ctx.arc(left + blueW, blueY + barH / 2, 5.5, 0, Math.PI * 2); ctx.fill();
  }
  ctx.restore();
}

function nucleonV4(x, y, r, fill, alpha = 1) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.shadowColor = fill;
  ctx.shadowBlur = 13;
  ctx.fillStyle = fill;
  ctx.strokeStyle = 'rgba(244,244,244,.42)';
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
  ctx.restore();
}

function nucleusV4(x, y, kind, alpha = 1) {
  const r = Math.min(width, height) * .035;
  if (kind === 'D') {
    nucleonV4(x - r * .48, y, r, C.cyan, alpha);
    nucleonV4(x + r * .48, y, r, '#515b66', alpha);
    label('²H', x, y + r * 1.72, 28, C.white, 'center', 650, MONO, alpha);
  } else if (kind === 'T') {
    nucleonV4(x, y - r * .53, r, C.purple, alpha);
    nucleonV4(x - r * .53, y + r * .44, r, '#515b66', alpha);
    nucleonV4(x + r * .53, y + r * .44, r, C.purple, alpha);
    label('³H', x, y + r * 2.10, 28, C.white, 'center', 650, MONO, alpha);
  } else if (kind === 'He') {
    nucleonV4(x - r * .50, y - r * .48, r, C.orange, alpha);
    nucleonV4(x + r * .50, y - r * .48, r, '#515b66', alpha);
    nucleonV4(x - r * .50, y + r * .48, r, '#515b66', alpha);
    nucleonV4(x + r * .50, y + r * .48, r, C.orange, alpha);
    label('⁴He', x, y + r * 2.05, 28, C.white, 'center', 650, MONO, alpha);
  }
}

function drawFusionSequenceV4(t) {
  if (t < 20.833333 || t >= 40.50) return;
  const sceneEnter = smooth((t - 20.833333) / (22.116667 - 20.833333));
  ctx.save();
  ctx.fillStyle = `rgba(0,0,0,${.80 * sceneEnter})`;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();

  const reactionAlpha = sceneEnter * (1 - smooth((t - 28.38) / .62));
  if (reactionAlpha > 0) {
    const enter = sceneEnter;
    label('²H  +  ³H   →   ⁴He  +  n', width / 2, height * .13, 46, C.white, 'center', 650, MONO, enter * reactionAlpha);
    const collide = heavyInOut((t - 22.116667) / (25.0 - 22.116667));
    const cx = width / 2;
    const cy = height * .49;
    if (t < 25.0) {
      const dx = lerp(width * .28, width * .035, collide);
      nucleusV4(cx - dx, cy, 'D', enter * reactionAlpha);
      nucleusV4(cx + dx, cy, 'T', enter * reactionAlpha);
      arrow2D(cx - width * .17, cy, cx - width * .07, cy, C.cyan, .82 * enter * reactionAlpha, 3, 15);
      arrow2D(cx + width * .17, cy, cx + width * .07, cy, C.purple, .82 * enter * reactionAlpha, 3, 15);
    } else {
      const flashP = clamp((t - 25.0) / .34);
      if (flashP < 1) {
        const glow = ctx.createRadialGradient(cx, cy, 0, cx, cy, 115 * heavyOut(flashP));
        glow.addColorStop(0, `rgba(255,255,255,${1 - flashP * .35})`);
        glow.addColorStop(.42, `rgba(255,255,0,${.80 * (1 - flashP)})`);
        glow.addColorStop(1, 'rgba(255,134,47,0)');
        ctx.fillStyle = glow; ctx.beginPath(); ctx.arc(cx, cy, 115 * heavyOut(flashP), 0, Math.PI * 2); ctx.fill();
      }
      const scatter = heavyOut((t - 25.05) / (26.25 - 25.05));
      const hx = lerp(cx, width * .30, scatter);
      const hy = lerp(cy, height * .67, scatter);
      const nx = lerp(cx, width * .76, scatter);
      const ny = lerp(cy, height * .30, scatter);
      line(cx, cy, hx, hy, C.orange, 2, .44 * scatter * reactionAlpha);
      line(cx, cy, nx, ny, C.white, 2, .38 * scatter * reactionAlpha);
      nucleusV4(hx, hy, 'He', scatter * reactionAlpha);
      nucleonV4(nx, ny, Math.min(width, height) * .025, '#cbd5e1', scatter * reactionAlpha);
      label('n', nx, ny + 45, 24, C.white, 'center', 650, MONO, scatter * reactionAlpha);
    }
  }

  if (t < 28.38) return;
  const graphIn = smooth((t - 28.38) / (30.583333 - 28.38));
  const tunnelStart = 38.383333;
  const tunnelEnd = 40.30;
  const graphAlpha = graphIn * (1 - smooth((t - tunnelEnd) / .20));
  const ox = width * .145;
  const right = width * .885;
  const oy = height * .80;
  const top = height * .18;
  const gw = right - ox;
  const gh = oy - top;
  const peakX = ox + gw * .16;
  line(ox, oy, right, oy, C.muted, 2.2, graphAlpha);
  line(ox, oy, ox, top, C.muted, 2.2, graphAlpha);
  label('r', right + 12, oy + 18, 28, C.white, 'left', 600, MONO, graphAlpha);
  label('V(r)', ox - 20, top, 28, C.purple, 'right', 650, MONO, graphAlpha);

  ctx.save();
  ctx.globalAlpha = graphAlpha;
  ctx.strokeStyle = C.purple;
  ctx.lineWidth = 5;
  ctx.beginPath();
  ctx.moveTo(ox + gw * .015, oy - gh * .02);
  ctx.lineTo(ox + gw * .055, oy - gh * .02);
  ctx.bezierCurveTo(ox + gw * .09, oy - gh * .05, peakX - gw * .018, oy - gh * .68, peakX, oy - gh * .88);
  for (let i = 0; i <= 120; i++) {
    const u = i / 120;
    const x = peakX + u * (right - peakX);
    const frac = .18 + .70 * Math.exp(-3.35 * u);
    ctx.lineTo(x, oy - gh * frac);
  }
  ctx.stroke();
  ctx.restore();

  const curvePoint = u => ({
    x: peakX + clamp(u) * (right - peakX),
    y: oy - gh * (.18 + .70 * Math.exp(-3.35 * clamp(u)))
  });

  if (t >= 30.583333 && t < 33.45) {
    const alpha = smooth((t - 30.583333) / .30) * (1 - smooth((t - 33.066667) / .38));
    const ey = oy - gh * .73;
    line(ox + 12, ey, right - 4, ey, C.red, 2.2, alpha, [10, 8]);
    label('E_classical', right - 8, ey - 28, 23, C.red, 'right', 650, MONO, alpha);
    const climb = heavyInOut((t - 30.583333) / (33.066667 - 30.583333));
    const u = lerp(.92, .055, climb);
    const pt = curvePoint(u);
    particle(pt.x, pt.y, 13, C.orange, '+', 10);
  }

  if (t >= 33.066667 && t < tunnelEnd) {
    const alpha = smooth((t - 33.066667) / .38) * graphAlpha;
    const ey = oy - gh * .31;
    line(ox + 12, ey, right - 4, ey, C.cyan, 2.5, alpha, [10, 8]);
    label(t >= tunnelStart ? '1500 万 K' : 'E_sun', right - 8, ey - 28, 24, C.cyan, 'right', 650, MONO, alpha);
    const turningX = ox + gw * .52;
    if (t < tunnelStart) {
      const approach = heavyInOut((t - 33.066667) / (35.566667 - 33.066667));
      const bounce = heavyOut((t - 35.566667) / (tunnelStart - 35.566667));
      const px = t < 35.566667 ? lerp(right - gw * .03, turningX, approach) : lerp(turningX, turningX + gw * .24, bounce);
      particle(px, ey, 13, C.orange, '+', 10);
      if (bounce > .08) arrow2D(turningX + 8, ey - 46, turningX + gw * .13, ey - 46, C.red, bounce * alpha, 2.5, 13);
    } else {
      // F02303-F02417: the 15-million-kelvin nucleus stays below the
      // Coulomb peak, attenuates through the forbidden span, then reappears.
      const p = clamp((t - tunnelStart) / (tunnelEnd - tunnelStart));
      const leftExit = ox + gw * .065;
      // Match the previous bounce's exact final x-position to avoid a cut.
      const rightEntry = turningX + gw * .24;
      const barrierEntry = turningX + gw * .012;
      const positionAt = value => {
        if (value < .22) return lerp(rightEntry, barrierEntry, smooth(value / .22));
        return lerp(barrierEntry, leftExit, heavyInOut((value - .22) / .78));
      };
      const px = positionAt(p);
      const inside = smooth((p - .20) / .12) * (1 - smooth((p - .78) / .13));
      const particleAlpha = alpha * lerp(1, .28, inside);
      const particleRadius = lerp(13, 9.5, inside);

      const wash = ctx.createLinearGradient(leftExit, 0, barrierEntry, 0);
      wash.addColorStop(0, 'rgba(174,116,199,0)');
      wash.addColorStop(.20, `rgba(174,116,199,${.10 * inside})`);
      wash.addColorStop(.80, `rgba(174,116,199,${.10 * inside})`);
      wash.addColorStop(1, 'rgba(174,116,199,0)');
      ctx.save();
      ctx.fillStyle = wash;
      ctx.fillRect(leftExit, ey - 34, barrierEntry - leftExit, 68);
      ctx.restore();

      for (let i = 7; i >= 1; i--) {
        const echoP = Math.max(0, p - i * .018);
        const echoX = positionAt(echoP);
        ctx.save();
        ctx.globalAlpha = particleAlpha * (.035 + (7 - i) * .018);
        particle(echoX, ey, Math.max(3.5, particleRadius - i * .85), C.orange, '', 5);
        ctx.restore();
      }

      ctx.save();
      ctx.globalAlpha = particleAlpha;
      particle(px, ey, particleRadius, C.orange, '+', lerp(16, 7, inside));
      ctx.restore();

      const emerge = smooth((p - .82) / .18);
      if (emerge > .001) {
        const ringR = lerp(16, 54, emerge);
        ctx.save();
        ctx.globalAlpha = alpha * (1 - emerge) * .82;
        ctx.strokeStyle = C.cyan;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(leftExit, ey, ringR, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }
    }
  }
}

function drawQuestionAndFinalV6(t) {
  if (t >= 40.30 && t < 44.083333) {
    const cover = smooth((t - 40.30) / .20);
    ctx.fillStyle = `rgba(0,0,0,${cover})`;
    ctx.fillRect(0, 0, width, height);
    const enter = heavyOut((t - 40.30) / .32);
    ctx.save();
    ctx.translate(width / 2, height * .47);
    label('?', 0, 0, Math.min(390, height * .40), C.white, 'center', 760, FONT, enter);
    ctx.restore();
  }
  if (t >= 44.083333) {
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, width, height);
    // Hard cut: at 60 fps the last question frame and first title frame are
    // consecutive. The title then grows slowly from 50% to 55% screen width.
    const growP = clamp((t - 44.083333) / (MAX_TIME - 44.083333));
    const scale = lerp(1, 1.10, growP);
    const testSize = 200;
    ctx.save();
    ctx.font = `720 ${testSize}px ${FONT}`;
    const measured = ctx.measureText('量子隧穿').width;
    ctx.restore();
    const baseSize = testSize * (width * .50 / measured);
    const baseWidth = width * .50;
    ctx.save();
    ctx.translate(width / 2, height / 2);
    ctx.scale(scale, scale);
    label('量子隧穿', 0, -12, baseSize, C.white, 'center', 720, FONT, 1);
    line(-baseWidth * .30, baseSize * .72, baseWidth * .30, baseSize * .72, C.cyan, 3, 1);
    ctx.restore();
  }
}

// Existing controls, timeline and subtitle logic remain intact.
render = function renderRound9(t) {
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  drawBackground(t);
  sceneSunV7(t);
  drawTemperatureChartV7(t);
  drawFusionSequenceV4(t);
  drawQuestionAndFinalV6(t);
  const current = subtitles.find(item => t >= item.s && t < item.e);
  subtitleEl.textContent = current ? current.t : '';
  timeline.value = String(t);
  timecodeEl.textContent = formatTime(t);
};

render(time);
