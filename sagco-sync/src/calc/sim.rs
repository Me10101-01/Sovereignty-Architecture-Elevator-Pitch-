use rand::Rng;
use crate::calc::evm::EVMSnapshot;

fn sample_normal(rng: &mut impl Rng, mean: f64, std: f64) -> f64 {
    // Box-Muller transform
    let u1: f64 = rng.gen_range(1e-10_f64..1.0_f64);
    let u2: f64 = rng.gen();
    mean + std * (-2.0 * u1.ln()).sqrt() * (2.0 * std::f64::consts::PI * u2).cos()
}

pub struct SimResult {
    pub n_simulations: usize,
    pub p20_eac: f64,
    pub p50_eac: f64,
    pub p80_eac: f64,
    pub mean_eac: f64,
    pub cpi_std: f64,
}

pub fn simulate(snapshot: &EVMSnapshot, n: usize) -> SimResult {
    let mut rng = rand::thread_rng();

    // Industry rule of thumb: CPI std dev = 15% of current CPI
    let cpi_std = snapshot.cpi * 0.15;

    let mut eac_samples: Vec<f64> = (0..n)
        .map(|_| {
            let cpi_sample = sample_normal(&mut rng, snapshot.cpi, cpi_std).max(0.1);
            snapshot.pv / cpi_sample
        })
        .collect();

    eac_samples.sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));

    let percentile = |p: f64| -> f64 {
        let idx = ((p / 100.0) * (n as f64)) as usize;
        eac_samples[idx.min(n - 1)]
    };

    let mean_eac = eac_samples.iter().sum::<f64>() / (n as f64);

    SimResult {
        n_simulations: n,
        p20_eac: percentile(20.0),
        p50_eac: percentile(50.0),
        p80_eac: percentile(80.0),
        mean_eac,
        cpi_std,
    }
}
