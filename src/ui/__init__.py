"""
User Interface Package
======================

Provides Streamlit-based interactive dashboard for GDP data visualization and
analysis. Includes chart generation, data export, and responsive UI components.

Modules
-------
app
    Main Streamlit application entry point
charts
    Chart generation functions using Plotly
views
    High-level view rendering functions
exports
    Data and chart export utilities
palette
    Centralized color scheme and styling

Architecture
------------
The UI follows a layered architecture:

::

    app.py (Entry point)
         ↓
    views.py (View composition)
         ↓
    charts.py (Visualization) + exports.py (Export)
         ↓
    palette.py (Styling)

Components
----------
**Application Layer** (app.py)
    Initializes system, manages state, coordinates views

**View Layer** (views.py)
    Composes UI sections, orchestrates charts and exports

**Visualization Layer** (charts.py)
    Generates Plotly charts with consistent styling

**Export Layer** (exports.py)
    Handles CSV downloads and chart PNG exports

**Style Layer** (palette.py)
    Defines color schemes and layout templates

Design Patterns
---------------
- **Separation of Concerns**: Each module has single responsibility
- **Pure Functions**: Charts are generated from data without side effects
- **Session State**: Streamlit session state manages figure registry
- **Responsive Design**: Charts adapt to container width

Chart Types
-----------
The package supports multiple visualization types:

Regional Analysis
    - Bar charts showing GDP by continent
    - Country comparisons within regions
    - Treemaps for hierarchical visualization

Temporal Analysis
    - Scatter plots with trend lines
    - Line charts for time series
    - Bar charts by year
    - Year-over-year growth rate analysis

Country Analysis
    - Time series specific to selected countries
    - GDP trends with interpolation

Export Capabilities
-------------------
Users can export:

1. **Filtered CSV Data**: Current filtered dataset
2. **PNG Charts**: All rendered charts as high-resolution images
3. **ZIP Archives**: Batch export of all charts

The export system handles Streamlit rerun issues and Windows-specific
Kaleido limitations with a two-phase generate-download approach.

Color Scheme
------------
All charts use a consistent custom palette defined in ``palette.py``:

- Primary: #FF5555 (Coral red)
- Secondary: #FF937E (Light coral)
- Tertiary: #C1E59F (Light green)
- Quaternary: #A3D78A (Medium green)

Charts automatically adapt to use continuous or discrete coloring based
on data size to maintain visual clarity.

Interactivity
-------------
The dashboard provides interactive filtering:

- Region selection (All or specific continent)
- Year range slider
- Country selection (when enabled)
- Aggregation method (Sum/Average)
- Top N countries toggle

State Management
----------------
The application uses Streamlit session state to:

- Cache loaded data (``@st.cache_resource``)
- Track generated charts for export
- Maintain filter selections across reruns

Examples
--------
Run the dashboard:

>>> streamlit run src/ui/app.py

The application will:
1. Load and clean data
2. Extract metadata (regions, countries, years)
3. Present interactive filters
4. Render charts based on selections
5. Provide export options

See Also
--------
app : Main application entry point
charts : Chart generation functions
views : View rendering and composition
exports : Export utilities
palette : Color scheme and styling

Notes
-----
This package requires Streamlit and Plotly. Charts are rendered using
Plotly's dark theme for consistency with the dashboard aesthetic.

The UI automatically handles large datasets by limiting displayed countries
and using efficient aggregation strategies.

Performance Considerations
--------------------------
- Data cleaning cached with ``@st.cache_resource``
- Charts generated on-demand, not pre-rendered
- Export uses lazy evaluation (generate only when requested)
"""

__all__ = ['app', 'charts', 'views', 'exports', 'palette']