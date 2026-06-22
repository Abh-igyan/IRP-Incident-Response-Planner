const bengaluru = [12.971599, 77.594566];
let inputMarker;
let incidentMarker;
let routeLine;
let lastPrediction = null;

const inputMap = L.map("inputMap", { zoomControl: true }).setView(bengaluru, 12);
const routeMap = L.map("routeMap", { zoomControl: true }).setView(bengaluru, 12);

const tiles = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
const attribution = "&copy; OpenStreetMap contributors";
L.tileLayer(tiles, { attribution, maxZoom: 19 }).addTo(inputMap);
L.tileLayer(tiles, { attribution, maxZoom: 19 }).addTo(routeMap);

function titleize(value) {
  if (value === null || value === undefined || value === "") return "-";
  return String(value)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function setSelect(id, values, fallback) {
  const select = document.getElementById(id);
  const cleanValues = [...new Set((values || []).filter(Boolean))];
  if (!cleanValues.length && fallback) cleanValues.push(fallback);
  select.innerHTML = cleanValues
    .map((value) => `<option value="${String(value).replaceAll('"', "&quot;")}">${titleize(value)}</option>`)
    .join("");
}

function setCurrentDatetime() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  document.getElementById("incident_datetime").value = now.toISOString().slice(0, 16);
}

function setIncidentLocation(lat, lng) {
  document.getElementById("latitude").value = lat.toFixed(6);
  document.getElementById("longitude").value = lng.toFixed(6);
  if (!inputMarker) {
    inputMarker = L.marker([lat, lng]).addTo(inputMap);
  } else {
    inputMarker.setLatLng([lat, lng]);
  }
}

function renderDl(id, items) {
  const dl = document.getElementById(id);
  dl.innerHTML = Object.entries(items)
    .map(([key, value]) => `<div class="kv"><dt>${titleize(key)}</dt><dd>${titleize(value)}</dd></div>`)
    .join("");
}

function renderPrediction(data) {
  lastPrediction = data;
  document.getElementById("closure_probability").textContent = `${Math.round(data.closure_probability * 100)}%`;
  document.getElementById("impact_score").textContent = data.impact_score.toFixed(2);
  document.getElementById("impact_class").textContent = data.impact_class;
  document.getElementById("response_priority").textContent = data.response_priority;

  renderDl("resourcePlan", data.resource_plan);
  renderDl("responsePlan", {
    eta_target: data.eta_target,
    diversion_strategy: data.diversion_strategy,
    model_status: data.model_status,
  });
  renderDl("trafficForecast", data.traffic_forecast);
  const diversionDistance = data.diversion_plan.best_diversion_distance_km;
  const diversionEta = data.diversion_plan.best_diversion_eta_mins;
  renderDl("diversionPlan", {
    best_diversion_distance_km:
      diversionDistance === null || diversionDistance === undefined ? "-" : `${Number(diversionDistance).toFixed(2)} km`,
    best_diversion_eta_mins:
      diversionEta === null || diversionEta === undefined ? "-" : `${Number(diversionEta).toFixed(1)} mins`,
    diversion_road_name: data.diversion_plan.diversion_road_name,
    alternate_roads: (data.diversion_plan.alternate_roads || []).join(", ") || "-",
    routing_status: data.diversion_plan.routing_status || "-",
  });

  const ctx = data.derived_context;
  document.getElementById("contextStrip").innerHTML = `
    <span>Corridor: ${titleize(ctx.corridor)}</span>
    <span>Zone: ${titleize(ctx.zone)}</span>
    <span>Station: ${titleize(ctx.police_station)}</span>
    <span>Time: ${ctx.hour}:00, ${ctx.is_peak_hour ? "Peak" : "Off-peak"}</span>
  `;

  const lat = Number(document.getElementById("latitude").value);
  const lng = Number(document.getElementById("longitude").value);
  if (incidentMarker) incidentMarker.remove();
  incidentMarker = L.marker([lat, lng]).addTo(routeMap).bindPopup("Incident").openPopup();

  if (routeLine) routeLine.remove();
  const coords = data.diversion_plan.route_coords || [];
  if (coords.length > 1) {
    routeLine = L.polyline(coords, { color: "#1769aa", weight: 5, opacity: 0.86 }).addTo(routeMap);
    routeMap.fitBounds(routeLine.getBounds().pad(0.18));
  } else {
    routeMap.setView([lat, lng], 13);
  }

  routeMap.invalidateSize();
}

async function loadOptions() {
  const response = await fetch("/options");
  const options = await response.json();
  setSelect("event_type", options.event_type, "unplanned");
  setSelect("event_cause", options.event_cause, "vehicle_breakdown");
  setSelect("veh_type", options.veh_type, "Unknown");
  setSelect("priority", options.priority, "High");
}

document.getElementById("incidentForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = document.getElementById("predictButton");
  button.disabled = true;
  button.textContent = "Predicting";

  const payload = {
    event_type: document.getElementById("event_type").value,
    event_cause: document.getElementById("event_cause").value,
    veh_type: document.getElementById("veh_type").value,
    priority: document.getElementById("priority").value,
    authenticated: document.getElementById("authenticated").checked,
    latitude: Number(document.getElementById("latitude").value),
    longitude: Number(document.getElementById("longitude").value),
    incident_datetime: document.getElementById("incident_datetime").value,
  };

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    renderPrediction(await response.json());
  } catch (error) {
    alert(`Prediction failed: ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = "Run Prediction";
  }
});

inputMap.on("click", (event) => {
  setIncidentLocation(event.latlng.lat, event.latlng.lng);
});

document.getElementById("latitude").addEventListener("change", () => {
  setIncidentLocation(Number(document.getElementById("latitude").value), Number(document.getElementById("longitude").value));
});

document.getElementById("longitude").addEventListener("change", () => {
  setIncidentLocation(Number(document.getElementById("latitude").value), Number(document.getElementById("longitude").value));
});

setCurrentDatetime();
setIncidentLocation(bengaluru[0], bengaluru[1]);
setTimeout(() => {
  inputMap.invalidateSize();
  routeMap.invalidateSize();
}, 0);

window.addEventListener("resize", () => {
  inputMap.invalidateSize();
  routeMap.invalidateSize();
});

loadOptions();
