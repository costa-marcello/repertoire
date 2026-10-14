# Chart Types Reference

## Contents

1. [Comparison Charts](#comparison-charts)
2. [Trend & Time Series](#trend--time-series)
3. [Distribution Charts](#distribution-charts)
4. [Composition Charts](#composition-charts)
5. [Relationship Charts](#relationship-charts)
6. [Specialized Charts](#specialized-charts)
7. [Selection Guidelines](#selection-guidelines)

Quick reference for selecting the right visualization. Contains 25+ chart types organized by analytical purpose.

## Comparison Charts

Compare values across categories or time.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Bar Chart** | Comparing discrete categories | 1 categorical + 1 numeric | Revenue by product line |
| **Grouped Bar** | Comparing multiple series across categories | 1 categorical + 2-4 numeric | Sales by region per quarter |
| **Stacked Bar** | Part-to-whole within categories | 1 categorical + 2-5 numeric | Revenue breakdown by channel |
| **Horizontal Bar** | Long category labels, ranking | 1 categorical + 1 numeric | Top 10 customers by spend |
| **Lollipop Chart** | Clean comparison with emphasis | 1 categorical + 1 numeric | Feature adoption rates |
| **Bullet Chart** | Performance vs target | 1 numeric + target + ranges | KPI dashboards, quota tracking |

## Trend & Time Series

Show changes over time.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Line Chart** | Continuous trends | 1 time + 1-5 numeric | Stock prices, traffic over time |
| **Area Chart** | Trends with volume emphasis | 1 time + 1-3 numeric | Cumulative revenue, user growth |
| **Stacked Area** | Part-to-whole over time | 1 time + 2-5 numeric | Traffic sources over time |
| **Step Chart** | Discrete changes | 1 time + 1 numeric | Pricing tiers, state changes |
| **Sparkline** | Inline micro-trends | 1 time + 1 numeric | Dashboard KPI cards |

## Distribution Charts

Show how data is spread.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Histogram** | Frequency distribution | 1 numeric (continuous) | Response time distribution |
| **Box Plot** | Distribution summary + outliers | 1 numeric + optional categorical | Salary ranges by department |
| **Violin Plot** | Distribution shape comparison | 1 numeric + 1 categorical | Test score distributions |
| **Density Plot** | Smooth distribution curves | 1 numeric | Age distribution of users |

## Composition Charts

Show parts of a whole.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Pie Chart** | Simple part-to-whole (2-5 parts) | 1 categorical + 1 numeric | Market share (few competitors) |
| **Donut Chart** | Part-to-whole with center metric | 1 categorical + 1 numeric | Budget allocation with total |
| **Treemap** | Hierarchical part-to-whole | Nested categorical + 1 numeric | File system usage, org spend |
| **Sunburst** | Multi-level hierarchy | Nested categorical + 1 numeric | Product category breakdown |
| **Waffle Chart** | Percentage visualization | 1 numeric (percentage) | Survey results, progress |

## Relationship Charts

Show correlations and connections.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Scatter Plot** | Correlation between 2 variables | 2 numeric | Price vs quality ratings |
| **Bubble Chart** | 3-variable relationships | 2 numeric + 1 for size | Revenue vs growth vs market size |
| **Heatmap** | Patterns in 2D matrix | 2 categorical + 1 numeric | Correlation matrix, activity by day/hour |
| **Network Graph** | Connections between entities | Nodes + edges | Social networks, dependencies |
| **Sankey Diagram** | Flow between stages | Source + target + value | User journey, budget flow |
| **Chord Diagram** | Bi-directional relationships | Matrix of relationships | Migration patterns, trade flows |

## Specialized Charts

Purpose-built visualizations.

| Chart Type | Best For | Data Requirements | Example Use Case |
|------------|----------|-------------------|------------------|
| **Gauge Chart** | Single metric vs target | 1 numeric + target | CPU usage, goal progress |
| **Radar/Spider** | Multi-dimensional comparison | 1 categorical + 5-8 numeric | Skill assessments, product comparison |
| **Funnel Chart** | Conversion stages | Ordered stages + values | Sales funnel, signup flow |
| **Waterfall** | Cumulative effect of changes | Sequential values | Financial statements, delta analysis |
| **Candlestick** | Financial OHLC data | Open, High, Low, Close + time | Stock trading charts |
| **Gantt Chart** | Project timelines | Tasks + start/end dates | Project management |

---

## Selection Guidelines

### By Question Type

| Question | Recommended Charts |
|----------|-------------------|
| "How much?" | Bar, Bullet, Gauge |
| "How does it change over time?" | Line, Area, Sparkline |
| "What's the breakdown?" | Pie, Donut, Treemap, Stacked Bar |
| "How is it distributed?" | Histogram, Box Plot, Violin |
| "Is there a relationship?" | Scatter, Bubble, Heatmap |
| "How does it flow?" | Sankey, Funnel |

### By Data Size

| Data Points | Recommended | Avoid |
|-------------|-------------|-------|
| 2-5 items | Pie, Bar, Donut | Scatter, Heatmap |
| 6-12 items | Bar, Line, Treemap | Pie (too many slices) |
| 13-50 items | Heatmap, Scatter, Treemap | Pie, grouped bars |
| 50+ items | Scatter, Histogram, Heatmap | Most categorical charts |

### Common Mistakes

| Mistake | Why It's Bad | Better Alternative |
|---------|-------------|-------------------|
| Pie with 10+ slices | Impossible to compare | Horizontal bar, sorted |
| 3D charts | Distorts perception | 2D equivalents |
| Dual Y-axes | Misleading correlations | Separate charts or normalize |
| Truncated Y-axis | Exaggerates differences | Start at zero or show break |
| Too many lines (>5) | Visual noise | Highlight key series, dim others |
