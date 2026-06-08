mod cell;
mod storage;
mod query;
mod index;
mod table;
mod planner;
mod antibody;

use std::path::PathBuf;
use std::process;

use storage::StorageEngine;
use table::Table;
use query::Query;

const VERSION: &str = "0.1.0";
const PAGES_DIR: &str = "pages";
const INDEXES_DIR: &str = "indexes";

fn usage() {
    eprintln!(
        "
  SAGCO-CELL-DB v{VERSION}  — a storage engine built from cells up

  sagco-db init
  sagco-db put  <table> <key> <value>
  sagco-db get  <table> <key>
  sagco-db del  <table> <key>
  sagco-db query <table> <filter> [<filter>...]
  sagco-db scan  <table>
  sagco-db list
  sagco-db compact <table>
  sagco-db explain <filter> [<filter>...]
  sagco-db antibody <table>
  sagco-db status

  Filters:  key=PA8   value~=chain   concept=chain_rule   key^=PA

  Examples:
    sagco-db init
    sagco-db put MAT225 PA8 \"8*x^7*e^(x^8)\"
    sagco-db get MAT225 PA8
    sagco-db query MAT225 key^=PA
    sagco-db query notes concept=chain_rule
    sagco-db antibody MAT225
"
    );
}

fn pages_dir() -> PathBuf  { PathBuf::from(PAGES_DIR) }
fn indexes_dir() -> PathBuf { PathBuf::from(INDEXES_DIR) }

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();

    if args.is_empty() || args[0] == "--help" || args[0] == "-h" {
        usage();
        return;
    }

    let cmd = args[0].as_str();

    match cmd {
        "init"    => cmd_init(),
        "put"     => cmd_put(&args),
        "get"     => cmd_get(&args),
        "del" | "delete" | "rm" => cmd_del(&args),
        "query"   => cmd_query(&args),
        "scan"    => cmd_scan(&args),
        "list"    => cmd_list(),
        "compact" => cmd_compact(&args),
        "explain" => cmd_explain(&args),
        "antibody" | "check" => cmd_antibody(&args),
        "status"  => cmd_status(),
        "version" => println!("sagco-db {}", VERSION),
        _ => {
            eprintln!("[error] unknown command: {}", cmd);
            usage();
            process::exit(1);
        }
    }
}

fn cmd_init() {
    std::fs::create_dir_all(PAGES_DIR).unwrap();
    std::fs::create_dir_all(INDEXES_DIR).unwrap();
    std::fs::create_dir_all("wafers").unwrap();
    println!("  SAGCO-CELL-DB initialized");
    println!("  pages/    -> page storage (.sagco files)");
    println!("  indexes/  -> key indexes (.sagco-idx files)");
    println!("  wafers/   -> truth tests + antibody reports");
    println!("\n  STATUS: CELL_DB_READY");
}

fn cmd_put(args: &[String]) {
    if args.len() < 4 {
        eprintln!("usage: sagco-db put <table> <key> <value>");
        process::exit(1);
    }
    let table_name = &args[1];
    let key   = args[2].as_bytes().to_vec();
    let value = args[3..].join(" ").into_bytes();

    let mut tbl = open_table(table_name);
    let offset = tbl.put(key, value).unwrap_or_else(|e| {
        eprintln!("[error] put failed: {}", e);
        process::exit(1);
    });
    println!("  PUT {} -> {}  (offset: {})", &args[2], table_name, offset);
}

fn cmd_get(args: &[String]) {
    if args.len() < 3 {
        eprintln!("usage: sagco-db get <table> <key>");
        process::exit(1);
    }
    let table_name = &args[1];
    let key = args[2].as_bytes();

    let tbl = open_table(table_name);
    match tbl.get(key).unwrap_or_else(|e| {
        eprintln!("[error] get failed: {}", e);
        process::exit(1);
    }) {
        Some(cell) => {
            println!("  key  : {}", cell.key_str());
            println!("  value: {}", cell.value_str());
            println!("  ts   : {}", cell.timestamp);
        }
        None => {
            println!("  NOT FOUND: {}", &args[2]);
            process::exit(1);
        }
    }
}

fn cmd_del(args: &[String]) {
    if args.len() < 3 {
        eprintln!("usage: sagco-db del <table> <key>");
        process::exit(1);
    }
    let table_name = &args[1];
    let key = args[2].as_bytes();

    let mut tbl = open_table(table_name);
    tbl.delete(key).unwrap_or_else(|e| {
        eprintln!("[error] delete failed: {}", e);
        process::exit(1);
    });
    println!("  DELETED {} from {}", &args[2], table_name);
}

fn cmd_query(args: &[String]) {
    if args.len() < 3 {
        eprintln!("usage: sagco-db query <table> <filter> [filter...]");
        process::exit(1);
    }
    let table_name = &args[1];
    let filter_strs: Vec<&str> = args[2..].iter().map(|s| s.as_str()).collect();

    let q = Query::parse(&filter_strs).unwrap_or_else(|e| {
        eprintln!("[error] bad filter: {}", e);
        process::exit(1);
    });

    println!("  {}", planner::explain(&q));

    let tbl = open_table(table_name);
    let results = tbl.query(&q).unwrap_or_else(|e| {
        eprintln!("[error] query failed: {}", e);
        process::exit(1);
    });

    println!("  {} result(s):", results.len());
    for cell in &results {
        println!("    {} = {}", cell.key_str(), cell.value_str());
    }
}

fn cmd_scan(args: &[String]) {
    if args.len() < 2 {
        eprintln!("usage: sagco-db scan <table>");
        process::exit(1);
    }
    let table_name = &args[1];
    let tbl = open_table(table_name);
    let cells = tbl.scan_all().unwrap_or_else(|e| {
        eprintln!("[error] scan failed: {}", e);
        process::exit(1);
    });
    println!("  {} cell(s) in {}:", cells.len(), table_name);
    for cell in &cells {
        println!("    {} = {}", cell.key_str(), cell.value_str());
    }
}

fn cmd_list() {
    let engine = StorageEngine::open(pages_dir()).unwrap_or_else(|e| {
        eprintln!("[error] cannot open pages dir: {}", e);
        process::exit(1);
    });
    let tables = engine.list_tables().unwrap_or_default();
    if tables.is_empty() {
        println!("  No tables. Run: sagco-db init");
    } else {
        println!("  Tables ({}):", tables.len());
        for t in &tables {
            println!("    {}", t);
        }
    }
}

fn cmd_compact(args: &[String]) {
    if args.len() < 2 {
        eprintln!("usage: sagco-db compact <table>");
        process::exit(1);
    }
    let table_name = &args[1];
    let tbl = open_table(table_name);
    let (kept, removed) = tbl.compact().unwrap_or_else(|e| {
        eprintln!("[error] compact failed: {}", e);
        process::exit(1);
    });
    println!("  COMPACT {}:  kept={} removed={}", table_name, kept, removed);
}

fn cmd_explain(args: &[String]) {
    if args.len() < 2 {
        eprintln!("usage: sagco-db explain <filter> [filter...]");
        process::exit(1);
    }
    let filter_strs: Vec<&str> = args[1..].iter().map(|s| s.as_str()).collect();
    let q = Query::parse(&filter_strs).unwrap_or_else(|e| {
        eprintln!("[error] bad filter: {}", e);
        process::exit(1);
    });
    println!("  {}", planner::explain(&q));
}

fn cmd_antibody(args: &[String]) {
    if args.len() < 2 {
        eprintln!("usage: sagco-db antibody <table>");
        process::exit(1);
    }
    let table_name = &args[1];
    let engine = StorageEngine::open(pages_dir()).unwrap_or_else(|e| {
        eprintln!("[error] {}", e);
        process::exit(1);
    });
    let checks = antibody::run(&engine, table_name).unwrap_or_else(|e| {
        eprintln!("[error] {}", e);
        process::exit(1);
    });
    antibody::print_diagnosis(table_name, &checks);
}

fn cmd_status() {
    println!("  SAGCO-CELL-DB v{}", VERSION);
    let engine = StorageEngine::open(pages_dir()).unwrap_or_else(|e| {
        eprintln!("[error] {}", e);
        process::exit(1);
    });
    let tables = engine.list_tables().unwrap_or_default();
    println!("  Tables: {}", tables.len());
    for t in &tables {
        if let Some(h) = engine.page_header(t).unwrap_or(None) {
            println!("    {} - {} cells", t, h.cell_count);
        }
    }
    println!("  STATUS: CELL_DB_ALIVE");
}

fn open_table(name: &str) -> Table {
    Table::open(pages_dir(), indexes_dir(), name).unwrap_or_else(|e| {
        eprintln!("[error] cannot open table {}: {}", name, e);
        process::exit(1);
    })
}
