# Event Driven Frontend

This directory contains the React-based frontend for the Incident Response Planner application. It is built with Vite and uses Material-UI for components and Leaflet for maps.

## Project Structure

Here is an overview of the project's file structure:

```
frontend/
├── index.html
├── package.json
└── src/
    ├── App.jsx
    ├── index.css
    ├── main.jsx
    ├── components/
    │   ├── Layout.jsx
    │   └── Predict/
    │       ├── DiversionPlan.jsx
    │       ├── LocationPickerMap.jsx
    │       ├── MetricBand.jsx
    │       ├── PredictComponents.css
    │       ├── ResourcePlan.jsx
    │       ├── ResponsePlan.jsx
    │       ├── RouteMap.jsx
    │       └── TrafficForecast.jsx
    ├── pages/
    │   ├── AnalyticsPage.jsx
    │   ├── HeatmapPage.jsx
    │   ├── LandingPage.jsx
    │   └── PredictPage.jsx
    ├── services/
    │   └── api.js
    └── theme/
        └── theme.js
```

## Key Components

*   **`index.html`**: The main HTML entry point for the application.
*   **`main.jsx`**: The main script entry point for the React application. It sets up the theme and routing.
*   **`App.jsx`**: The root component that defines the overall page layout and URL routes.
*   **`components/`**: Contains reusable React components.
    *   `Layout.jsx`: The main application shell with the navigation drawer and app bar.
    *   `Predict/`: Components specifically used on the prediction page for displaying results and maps.
*   **`pages/`**: Contains the main page components for each route.
    *   `PredictPage.jsx`: The core page for running incident predictions. It includes the input form, maps, and results display.
    *   `HeatmapPage.jsx`: Displays a map of historical incident data.
    *   `AnalyticsPage.jsx`: Redirects to the static analytics dashboard.
    *   `LandingPage.jsx`: The application's home page.
*   **`services/`**: Contains modules for communicating with the backend API.
    *   `api.js`: Defines functions for making API calls using `axios`.
*   **`theme/`**: Contains the Material-UI theme configuration.

## Available Scripts

In the project directory, you can run:

### `npm run dev`

Runs the app in the development mode.<br />
Open http://localhost:5173 to view it in the browser.

### `npm run build`

Builds the app for production to the `dist` folder.