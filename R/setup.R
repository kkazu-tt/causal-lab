# 各ページの最初に読む。図の見た目と、推定値の記録（ダッシュボードと CI の検査が読む）をそろえる。
library(ggplot2)

reticulate::use_python(".venv/bin/python", required = TRUE)

# SVG にして、日本語の文字はブラウザのフォントで描かせる（CI に日本語フォントを入れずに済む）。
knitr::opts_chunk$set(dev = "svglite", fig.width = 7, fig.height = 3.6)

col_main <- "#2a78d6"
col_second <- "#eb6834"

theme_set(
  theme_minimal(base_size = 12) +
    theme(
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(colour = "#e5e4e0", linewidth = 0.3),
      axis.text = element_text(colour = "#52514e"),
      plot.title.position = "plot",
      legend.position = "top",
      legend.justification = "left"
    )
)

# 推定値を _results/<key>.json に書く。index.qmd が読んで表にし、scripts/check_results.py が範囲を確かめる。
record <- function(key, ...) {
  dir.create("_results", showWarnings = FALSE)
  jsonlite::write_json(
    list(...),
    file.path("_results", paste0(key, ".json")),
    auto_unbox = TRUE, digits = NA, pretty = TRUE
  )
}
