"""Session metrics from 1 Hz streams. Formulas: framework/data-schema.md section 11."""

from .streams import sample_weights


def _valid(values, weights):
    return [(v, w) for v, w in zip(values, weights) if v is not None]


def mean(values, weights=None):
    weights = weights or [1] * len(values)
    pairs = _valid(values, weights)
    tot = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / tot if tot else None


def zone_minutes(hr, time, z1_cap, lthr):
    """Minutes in the 3 physiological zones: Z1 < z1_cap <= Z2 < lthr <= Z3."""
    w = sample_weights(time)
    z = [0.0, 0.0, 0.0]
    for h, dt in _valid(hr, w):
        z[0 if h < z1_cap else 1 if h < lthr else 2] += dt
    return [round(s / 60, 1) for s in z]


def hr_tss(hr, time, lthr):
    """hrTSS = sum(dt/3600 * (HR/LTHR)^2 * 100)."""
    w = sample_weights(time)
    return round(sum(dt / 3600 * (h / lthr) ** 2 * 100 for h, dt in _valid(hr, w)), 1)


def if_hr(hr, time, lthr):
    m = mean(hr, sample_weights(time))
    return round(m / lthr, 2) if m else None


def normalized_power(watts, window=30):
    """4th root of the mean of the 30 s rolling average of power^4 (1 Hz assumed)."""
    p = [x or 0 for x in watts]
    if len(p) < window:
        return None
    roll, s = [], sum(p[:window])
    roll.append(s / window)
    for i in range(window, len(p)):
        s += p[i] - p[i - window]
        roll.append(s / window)
    return round((sum(r ** 4 for r in roll) / len(roll)) ** 0.25, 1)


def efficiency(output, hr):
    """EF = mean output (power or speed) / mean HR, over samples where both exist."""
    pairs = [(o, h) for o, h in zip(output, hr) if o is not None and h]
    if not pairs:
        return None
    return sum(o for o, _ in pairs) / len(pairs) / (sum(h for _, h in pairs) / len(pairs))


def decoupling_pct(output, hr, mask=None):
    """(EF 1st half - EF 2nd half) / EF 1st half * 100. `mask` selects samples (e.g. moving)."""
    idx = [i for i in range(len(hr)) if (mask is None or mask[i])]
    if len(idx) < 120:
        return None
    half = len(idx) // 2
    a, b = idx[:half], idx[half:]
    ef1 = efficiency([output[i] for i in a], [hr[i] for i in a])
    ef2 = efficiency([output[i] for i in b], [hr[i] for i in b])
    if not ef1 or ef2 is None:
        return None
    return round((ef1 - ef2) / ef1 * 100, 1)


def over_cap(hr, time, cap, windows=None):
    """Seconds above `cap` within `windows` [(start_s, end_s)] (all samples if None).
    Returns (seconds_over, seconds_total, pct)."""
    w = sample_weights(time)
    over = tot = 0
    for t, h, dt in zip(time, hr, w):
        if h is None:
            continue
        if windows is not None and not any(a <= t < b for a, b in windows):
            continue
        tot += dt
        if h > cap:
            over += dt
    return over, tot, round(100 * over / tot, 1) if tot else None
