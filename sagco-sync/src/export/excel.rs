use rust_xlsxwriter::{
    Chart, ChartType, Format, Workbook, XlsxError,
};
use crate::calc::evm::EVMSnapshot;
use crate::calc::trend;
use crate::ingest::ra_sheet::RASheet;

pub fn export_excel(ra: &RASheet, path: &str) -> Result<(), Box<dyn std::error::Error>> {
    let mut workbook = Workbook::new();

    // Formats
    let bold = Format::new().set_bold();
    let red_fill = Format::new()
        .set_background_color(rust_xlsxwriter::Color::Red)
        .set_font_color(rust_xlsxwriter::Color::White);
    let yellow_fill = Format::new()
        .set_background_color(rust_xlsxwriter::Color::Yellow);
    let green_fill = Format::new()
        .set_background_color(rust_xlsxwriter::Color::Lime);
    let num2 = Format::new().set_num_format("0.00");

    // ── Sheet 1: Summary ────────────────────────────────────────────
    {
        let sheet = workbook.add_worksheet();
        sheet.set_name("Summary")?;

        let headers = ["Circuit", "PV", "AC", "EV", "CPI", "SPI", "CV", "EAC", "Status"];
        for (col, h) in headers.iter().enumerate() {
            sheet.write_with_format(0, col as u16, *h, &bold)?;
        }
        sheet.set_column_width(0, 20)?;
        sheet.set_column_width(8, 15)?;

        let mut row: u32 = 1;
        for circ in &ra.circuits {
            let snap = EVMSnapshot::from_circuit(circ);
            sheet.write(row, 0, circ.id.as_str())?;
            sheet.write(row, 1, snap.pv)?;
            sheet.write(row, 2, snap.ac)?;
            sheet.write(row, 3, snap.ev)?;

            let cpi_fmt = if snap.cpi < 0.8 {
                &red_fill
            } else if snap.cpi < 1.0 {
                &yellow_fill
            } else {
                &green_fill
            };
            sheet.write_with_format(row, 4, snap.cpi, cpi_fmt)?;
            sheet.write_with_format(row, 5, snap.spi, &num2)?;
            sheet.write(row, 6, snap.cv)?;
            if snap.eac.is_finite() {
                sheet.write(row, 7, snap.eac)?;
            } else {
                sheet.write(row, 7, "∞")?;
            }
            sheet.write(row, 8, format!("{} {}", snap.status_icon(), snap.status()))?;
            row += 1;
        }

        // Totals row
        let proj = EVMSnapshot::from_project(ra);
        let totals_fmt = Format::new().set_bold().set_border_top(rust_xlsxwriter::FormatBorder::Thin);
        sheet.write_with_format(row, 0, "PROJECT TOTAL", &totals_fmt)?;
        sheet.write_with_format(row, 1, proj.pv, &totals_fmt)?;
        sheet.write_with_format(row, 2, proj.ac, &totals_fmt)?;
        sheet.write_with_format(row, 3, proj.ev, &totals_fmt)?;
        let proj_cpi_fmt = if proj.cpi < 0.8 {
            Format::new().set_bold().set_background_color(rust_xlsxwriter::Color::Red)
                .set_font_color(rust_xlsxwriter::Color::White)
        } else if proj.cpi < 1.0 {
            Format::new().set_bold().set_background_color(rust_xlsxwriter::Color::Yellow)
        } else {
            Format::new().set_bold().set_background_color(rust_xlsxwriter::Color::Lime)
        };
        sheet.write_with_format(row, 4, proj.cpi, &proj_cpi_fmt)?;
        sheet.write_with_format(row, 5, proj.spi, &totals_fmt)?;
        sheet.write_with_format(row, 6, proj.cv, &totals_fmt)?;
        if proj.eac.is_finite() {
            sheet.write_with_format(row, 7, proj.eac, &totals_fmt)?;
        } else {
            sheet.write_with_format(row, 7, "∞", &totals_fmt)?;
        }
        sheet.write_with_format(row, 8, format!("{} {}", proj.status_icon(), proj.status()), &totals_fmt)?;
    }

    // ── Sheet 2: S-Curve ────────────────────────────────────────────
    {
        let sheet = workbook.add_worksheet();
        sheet.set_name("S-Curve")?;

        // Headers: Circuit | PV | AC | EV
        sheet.write_with_format(0, 0, "Circuit", &bold)?;
        sheet.write_with_format(0, 1, "PV", &bold)?;
        sheet.write_with_format(0, 2, "AC", &bold)?;
        sheet.write_with_format(0, 3, "EV", &bold)?;
        sheet.set_column_width(0, 20)?;

        let n_circuits = ra.circuits.len() as u32;
        for (i, circ) in ra.circuits.iter().enumerate() {
            let snap = EVMSnapshot::from_circuit(circ);
            let row = (i as u32) + 1;
            sheet.write(row, 0, circ.id.as_str())?;
            sheet.write(row, 1, snap.pv)?;
            sheet.write(row, 2, snap.ac)?;
            sheet.write(row, 3, snap.ev)?;
        }

        // Clustered bar chart
        let mut chart = Chart::new(ChartType::Column);
        chart.set_name("Planned vs Actual vs Earned — Circuit Level");

        let data_range_end = n_circuits; // rows 1..=n_circuits

        // PV series
        chart
            .add_series()
            .set_categories(("S-Curve", 1, 0, data_range_end, 0))
            .set_values(("S-Curve", 1, 1, data_range_end, 1))
            .set_name("PV (Planned)");

        // AC series
        chart
            .add_series()
            .set_categories(("S-Curve", 1, 0, data_range_end, 0))
            .set_values(("S-Curve", 1, 2, data_range_end, 2))
            .set_name("AC (Actual)");

        // EV series
        chart
            .add_series()
            .set_categories(("S-Curve", 1, 0, data_range_end, 0))
            .set_values(("S-Curve", 1, 3, data_range_end, 3))
            .set_name("EV (Earned)");

        chart.title().set_name("Planned vs Actual vs Earned — Circuit Level");
        chart.x_axis().set_name("Circuit");
        chart.y_axis().set_name("Hours");

        let sheet2 = workbook.worksheet_from_name("S-Curve")?;
        sheet2.insert_chart(2, 5, &chart)?;
    }

    // ── Sheet 3: CPI Trend ──────────────────────────────────────────
    {
        let sheet = workbook.add_worksheet();
        sheet.set_name("CPI Trend")?;

        let proj_snap = EVMSnapshot::from_project(ra);
        let demo = trend::demo_trend(proj_snap.cpi);

        sheet.write_with_format(0, 0, "Period", &bold)?;
        sheet.write_with_format(0, 1, "CPI", &bold)?;
        sheet.write_with_format(0, 2, "Rolling3Day", &bold)?;
        sheet.write_with_format(0, 3, "Reference_1.0", &bold)?;

        for (i, reading) in demo.readings.iter().enumerate() {
            let row = (i as u32) + 1;
            sheet.write(row, 0, reading.period as u32)?;
            sheet.write(row, 1, reading.cpi)?;
            sheet.write(row, 2, demo.rolling_3day[i])?;
            sheet.write(row, 3, 1.0_f64)?;
        }

        let n_rows = demo.readings.len() as u32;

        let mut chart = Chart::new(ChartType::Line);
        chart.set_name("CPI Trend — Decay Watch");

        chart
            .add_series()
            .set_categories(("CPI Trend", 1, 0, n_rows, 0))
            .set_values(("CPI Trend", 1, 1, n_rows, 1))
            .set_name("CPI");

        chart
            .add_series()
            .set_categories(("CPI Trend", 1, 0, n_rows, 0))
            .set_values(("CPI Trend", 1, 2, n_rows, 2))
            .set_name("Rolling 3-Day");

        chart
            .add_series()
            .set_categories(("CPI Trend", 1, 0, n_rows, 0))
            .set_values(("CPI Trend", 1, 3, n_rows, 3))
            .set_name("Reference 1.0");

        chart.title().set_name("CPI Trend — Decay Watch");
        chart.x_axis().set_name("Period");
        chart.y_axis().set_name("CPI");

        let sheet3 = workbook.worksheet_from_name("CPI Trend")?;
        sheet3.insert_chart(2, 5, &chart)?;
    }

    workbook.save(path).map_err(|e: XlsxError| Box::new(e) as Box<dyn std::error::Error>)?;
    Ok(())
}
