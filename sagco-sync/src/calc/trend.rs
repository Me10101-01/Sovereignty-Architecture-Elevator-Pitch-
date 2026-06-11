pub struct CPIReading {
    pub period: usize,
    pub cpi: f64,
    pub ev: f64,
    pub ac: f64,
}

pub struct CPITrend {
    pub readings: Vec<CPIReading>,
    /// Rolling 3-period average CPI
    pub rolling_3day: Vec<f64>,
    /// CPI decay forecast (10 periods forward from last reading)
    pub decay_forecast: Vec<f64>,
    /// % complete at each reading
    pub pct_complete: Vec<f64>,
}

pub fn build_trend(readings: Vec<CPIReading>) -> CPITrend {
    let n = readings.len();

    // Rolling 3-period average: for i >= 2, avg readings[i-2..=i]
    let rolling_3day: Vec<f64> = (0..n)
        .map(|i| {
            if i < 2 {
                readings[i].cpi
            } else {
                (readings[i - 2].cpi + readings[i - 1].cpi + readings[i].cpi) / 3.0
            }
        })
        .collect();

    // Decay forecast: 5% regression to mean of 1.0 per period, 10 steps forward
    let last_cpi = readings.last().map(|r| r.cpi).unwrap_or(1.0);
    let decay_forecast: Vec<f64> = {
        let mut forecast = Vec::with_capacity(10);
        let mut cpi = last_cpi;
        for _ in 0..10 {
            cpi = cpi + (1.0 - cpi) * 0.05;
            forecast.push(cpi);
        }
        forecast
    };

    // pct_complete: ev / (ev + remaining_pv) — approximate as ev / (ac * cpi) = pct done
    // We approximate using ev/ac ratio relative to last reading for simplicity
    let pct_complete: Vec<f64> = readings
        .iter()
        .map(|r| {
            if r.ac == 0.0 { 0.0 } else { r.ev / (r.ev + r.ac).max(1.0) }
        })
        .collect();

    CPITrend { readings, rolling_3day, decay_forecast, pct_complete }
}

/// Returns a demo trend with 7 days of progressively decaying CPI
pub fn demo_trend(starting_cpi: f64) -> CPITrend {
    let mut readings = Vec::new();
    let mut cpi = starting_cpi;
    let mut ev_accum = 0.0_f64;
    let mut ac_accum = 0.0_f64;

    for day in 1..=7 {
        // Simulate some EV/AC
        let daily_ev = 50.0 * cpi;
        let daily_ac = 50.0;
        ev_accum += daily_ev;
        ac_accum += daily_ac;
        readings.push(CPIReading {
            period: day,
            cpi,
            ev: ev_accum,
            ac: ac_accum,
        });
        // Decay 5% toward 1.0 each day
        cpi = cpi + (1.0 - cpi) * 0.05;
    }

    build_trend(readings)
}
