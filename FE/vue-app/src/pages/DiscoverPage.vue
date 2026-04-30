<template>
  <MainLayout>
    <section class="hero">
      <h2>Find your next <em>warm moment</em></h2>
      <p>Free and low-cost activities near {{ nearbyLabel }}</p>

      <form class="location-picker" @submit.prevent="applyManualLocation">
        <input class="location-input" v-model="locationInput" type="text" aria-label="Location"
          placeholder="Please enter suburb or postcode in Melbourne." @focus="handleLocationInputFocus" />
        <button type="button" class="change-btn" :disabled="isLocating" @click="getLocation">
          {{ isLocating ? "Locating..." : "Locate" }}
        </button>
        <button type="submit" class="apply-btn" :disabled="isApplying || !locationInput.trim()">
          {{ isApplying ? "Updating..." : "Change" }}
        </button>
      </form>
      <p class="location-note">
        Using search (not Locate) may return a representative point of the suburb/postcode, not your exact position.
      </p>

      <div class="chips">
        <button v-for="chip in chips" :key="chip.key" class="chip" :class="{ solid: activeFilters[chip.key] }"
          @click="toggleFilter(chip.key)">
          {{ chip.label }}
        </button>
      </div>
    </section>

    <section class="results-header">
      <h3>{{ totalCount }} activities</h3>
      <button class="print-btn" type="button" @click="printList">
        Print list
      </button>
    </section>

    <section class="activity-list" v-if="!isLoading && !loadError && activities.length">
      <article class="event-card" v-for="activity in activities" :key="activity.id">
        <div class="tags">
          <span v-for="tag in activity.displayTags" :key="`${activity.id}-${tag.text}`" class="tag" :class="tag.tone">
            {{ tag.text }}
          </span>
          <span class="distance" v-if="activity.distanceKm !== null">{{ activity.distanceKm.toFixed(1) }} km</span>
        </div>
        <h4>{{ activity.title }}</h4>
        <p class="meta">{{ formatMeta(activity) }}</p>
        <p class="desc">{{ activity.description }}</p>
        <div class="event-foot">
          <span>{{ activity.spotsLeftText }}</span>
          <RouterLink
            :to="detailsTo(activity.id)"
          >
            View details →
          </RouterLink>
        </div>
      </article>

      <nav class="pagination" v-if="totalPages > 1" aria-label="Activity pages">
        <button class="page-btn" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          Prev
        </button>

        <button v-for="page in visiblePages" :key="page" class="page-btn" type="button"
          :class="{ active: page === currentPage }" @click="goToPage(page)">
          {{ page }}
        </button>

        <button class="page-btn" type="button" :disabled="currentPage === totalPages || isLoading"
          @click="goToPage(currentPage + 1)">
          Next
        </button>
      </nav>
    </section>

    <section class="activity-list" v-else>
      <article class="event-card state-card" v-if="isLoading">
        Loading activities...
      </article>
      <article class="event-card state-card" v-else-if="loadError">
        {{ loadError }}
      </article>
      <article class="event-card state-card" v-else>
        <template v-if="!hasLocationConfirmed">
          Please locate first or enter a Melbourne suburb/postcode, then tap Change.
        </template>
        <template v-else-if="hasLocationConfirmed">
          No activities found for the current filters.
        </template>
        <template v-else> No activities found from the API. </template>
      </article>
    </section>
  </MainLayout>
</template>

<script setup>
import MainLayout from "../layouts/MainLayout.vue";
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useLocationState } from "../composables/useLocationState";

const { setDetectedLocation, setDetectedUnavailable } = useLocationState();
const BASE_URL = import.meta.env.VITE_ACTIVITIES_API_URL || "https://connectlocal.duckdns.org";
const API = `${BASE_URL}/api/events/search`;
const CLOSE_KM = 5;
const UI_PAGE_SIZE = 3;
const FETCH_LIMIT = UI_PAGE_SIZE;
const MELBOURNE_NOT_FOUND = "The location you specified was not found in Melbourne.";

const locationInput = ref("");
const nearbyLabel = ref("your area");
const isLocating = ref(false);
const isApplying = ref(false);
const activities = ref([]);
const isLoading = ref(false);
const loadError = ref("");
const currentPage = ref(1);
const hasLocationConfirmed = ref(false);
const locationLat = ref(null);
const locationLon = ref(null);
const locationQueryMode = ref("suburb");
const totalHint = ref(null);

const activeFilters = reactive({
  free: true,
  thisWeek: true,
  closeHome: true,
});
const chips = [
  { key: "free", label: "Free" },
  { key: "thisWeek", label: "This Week" },
  { key: "closeHome", label: "Close to Home" },
];

const n = (v) => (Number.isFinite(+v) ? +v : null);
const b = (v) =>
  v === true || v === 1 || /^true|yes|y|1$/i.test(String(v || ""));
const d = (v) => {
  const x = v ? new Date(String(v).replace(" ", "T")) : null;
  return x && !Number.isNaN(x.getTime()) ? x : null;
};
const arr = (p) => (Array.isArray(p?.events) ? p.events : []);
const total = (p) => n(p?.total_available ?? p?.total);
const isPostcodeInput = (q) => /^\d{4}$/.test(q);
const isSuburbInput = (q) => /^[A-Za-z][A-Za-z\s'-]{1,59}$/.test(q);
const isValidLocationInput = (q) => isPostcodeInput(q) || isSuburbInput(q);
const isVictoriaPostcodeRange = (q) => {
  const code = Number(q);
  return Number.isInteger(code) && code >= 3000 && code <= 3999;
};
const normalizePlace = (s) => String(s || "").trim().toLowerCase().replace(/\s+/g, " ");
const normalizePostcode = (s) => (String(s || "").match(/\b\d{4}\b/) || [""])[0];
const isInMelbourne = (a = {}, displayName = "") => {
  const state = String(a.state || "").toLowerCase();
  const text = String(displayName || "").toLowerCase();
  return state.includes("victoria") && text.includes("melbourne");
};

//Organize the API data into the front-end format
const normalize = (r, i) => {
  const date = d(r.datetime_start);
  const km = n(r.distance_km);
  const cost = n(r.min_price);
  const isFree = b(r.is_free) || (cost != null && cost <= 10);
  const indoor = b(r.indoor);
  const easyAccess = b(r.easy_access);
  const venue = r.venue || "Location TBC";
  const address = String(r.address || r.location_summary || "").trim();
  const suburb = r.suburb || "";
  const spots = n(r.spots_left);
  const category = String(r?.category || "").trim();
  const source = String(r?.source || "").trim();
  const cancelled = b(r.is_cancelled);
  return {
    id: r.id ?? `event-${i}`,
    title: r.name || `Activity ${i + 1}`,
    description: r.description || "Community activity details available soon.",
    venue,
    suburb,
    date,
    dateText: date
      ? date.toLocaleDateString("en-AU", {
        weekday: "short",
        day: "numeric",
        month: "short",
      })
      : r.datetime_summary || "Date TBC",
    timeText: date
      ? date.toLocaleTimeString("en-AU", { hour: "numeric", minute: "2-digit" })
      : "Time TBC",
    isFree,
    indoor,
    easyAccess,
    distanceKm: km,
    spotsLeftText:
      spots == null
        ? (address ? `Address: ${address}` : "Spots info unavailable")
        : `${Math.max(0, Math.floor(spots))} spots left`,
    link: r.url || "",
    displayTags: [
      isFree && { text: "Free / Low-cost", tone: "green" },
      km != null && km <= CLOSE_KM && { text: "Near You", tone: "lilac" },
      category && { text: category, tone: "soft" },
      source && { text: source, tone: "soft" },
      cancelled && { text: "Cancelled", tone: "warn" },
    ].filter(Boolean),
  };
};

//Generate API request address
const buildSearchUrl = (page = currentPage.value) => {
  const u = new URL(API);
  const offset = (Math.max(1, page) - 1) * FETCH_LIMIT;
  u.searchParams.set("offset", String(offset));
  u.searchParams.set("rows", String(FETCH_LIMIT));
  u.searchParams.set("is_free", activeFilters.free ? "true" : "false");
  if (activeFilters.thisWeek) {
    const today = new Date();
    const end = new Date(Date.now() + 7 * 86400000);
    u.searchParams.set("date_from", today.toISOString().slice(0, 10));
    u.searchParams.set("date_to", end.toISOString().slice(0, 10));
  }
  if (activeFilters.closeHome) {
    u.searchParams.set("radius_km", String(CLOSE_KM));
  }
  if (
    locationQueryMode.value === "latlon" &&
    locationLat.value != null &&
    locationLon.value != null
  ) {
    u.searchParams.set("lat", String(locationLat.value));
    u.searchParams.set("lon", String(locationLon.value));
  } else if (locationInput.value.trim()) {
    const suburbQuery =
      nearbyLabel.value && nearbyLabel.value !== "your area"
        ? nearbyLabel.value
        : locationInput.value.trim();
    u.searchParams.set("suburb", suburbQuery.toLowerCase());
  }
  return u;
};

//Request for activity data
const fetchActivities = async (page = currentPage.value) => {
  if (!hasLocationConfirmed.value) return;
  isLoading.value = true;
  loadError.value = "";
  try {
    const u = buildSearchUrl(page);
    const r = await fetch(u.toString());
    if (!r.ok) throw new Error(`Failed to load activities (${r.status})`);
    const p = await r.json();
    const list = arr(p);
    totalHint.value = total(p) ?? totalHint.value;
    activities.value = list.map(normalize);
    console.info(
      `Loaded page=${page} count=${activities.value.length}${totalHint.value ? ` total=${totalHint.value}` : ""}`,
    );
    currentPage.value = page;
  } catch (e) {
    loadError.value = "Unable to load activities right now. Please try again later.";
    activities.value = [];
  } finally {
    isLoading.value = false;
  }
};

//Positioning logic
const setLocation = (text, suburb = "", lat = null, lon = null) => {
  locationInput.value = text;
  nearbyLabel.value = suburb || text.split(",")[0] || "your area";
  locationLat.value = lat;
  locationLon.value = lon;
  hasLocationConfirmed.value = true;
  setDetectedLocation(text);
};
const handleLocationInputFocus = () => {
  if (locationInput.value === MELBOURNE_NOT_FOUND) {
    locationInput.value = "";
  }
};

const parseAddress = (a = {}) => {
  const suburb =
    a.suburb || a.neighbourhood || a.city_district || a.town || a.village || a.city || "";
  const postcode = a.postcode || "";
  return { suburb, postcode };
};
const formatSuburbPostcode = ({ suburb, postcode }) =>
  [suburb, postcode].filter(Boolean).join(" , ").trim();

const getLocation = () => {
  if (!navigator.geolocation)
    return (
      (locationInput.value = MELBOURNE_NOT_FOUND),
      setDetectedUnavailable()
    );
  isLocating.value = true;
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      try {
        const r = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.latitude}&lon=${coords.longitude}&accept-language=en`,
        );
        const top = await r.json();
        if (!isInMelbourne(top?.address || {}, top?.display_name || "")) {
          hasLocationConfirmed.value = false;
          locationLat.value = null;
          locationLon.value = null;
          locationInput.value = MELBOURNE_NOT_FOUND;
          setDetectedUnavailable();
        } else {
          const f = parseAddress(top.address || {});
          const value = formatSuburbPostcode(f);
          if (!value) {
            hasLocationConfirmed.value = false;
            locationLat.value = null;
            locationLon.value = null;
            locationInput.value = MELBOURNE_NOT_FOUND;
            setDetectedUnavailable();
          } else {
            setLocation(value, f.suburb || value, coords.latitude, coords.longitude);
            locationQueryMode.value = "latlon";
            await fetchActivities();
          }
        }
      } catch {
        hasLocationConfirmed.value = false;
        locationLat.value = null;
        locationLon.value = null;
        locationInput.value = MELBOURNE_NOT_FOUND;
        setDetectedUnavailable();
      }
      isLocating.value = false;
    },
    () => {
      hasLocationConfirmed.value = false;
      locationLat.value = null;
      locationLon.value = null;
      locationInput.value = MELBOURNE_NOT_FOUND;
      setDetectedUnavailable();
      isLocating.value = false;
    },
  );
};

const applyManualLocation = async () => {
  const q = locationInput.value.trim();
  if (!q) return;
  if (!isValidLocationInput(q)) {
    hasLocationConfirmed.value = false;
    locationLat.value = null;
    locationLon.value = null;
    locationInput.value = MELBOURNE_NOT_FOUND;
    setDetectedUnavailable();
    return;
  }
  if (isPostcodeInput(q) && !isVictoriaPostcodeRange(q)) {
    hasLocationConfirmed.value = false;
    locationLat.value = null;
    locationLon.value = null;
    locationInput.value = MELBOURNE_NOT_FOUND;
    setDetectedUnavailable();
    return;
  }
  isApplying.value = true;
  try {
    const queryText = isPostcodeInput(q)
      ? `${q}, Victoria, Australia`
      : `${q}, Melbourne, Victoria, Australia`;
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(queryText)}&addressdetails=1&limit=20&accept-language=en&countrycodes=au`,
    );
    const list = (await r.json()) || [];
    const top = list.find((item) => {
      const state = String(item?.address?.state || "").toLowerCase();
      const f = parseAddress(item?.address || {});
      const isoState = String(item?.address?.["ISO3166-2-lvl4"] || "").toUpperCase();
      const display = String(item?.display_name || "").toLowerCase();
      const inVictoria =
        state.includes("victoria") ||
        isoState === "AU-VIC" ||
        display.includes("victoria");
      if (isPostcodeInput(q)) {
        const postcodeMatched =
          normalizePostcode(f.postcode) === normalizePostcode(q) ||
          normalizePostcode(item?.display_name) === normalizePostcode(q);
        return inVictoria && postcodeMatched;
      }
      if (!isInMelbourne(item?.address || {}, item?.display_name || "")) return false;
      return normalizePlace(f.suburb) === normalizePlace(q);
    });
    if (!top) {
      hasLocationConfirmed.value = false;
      locationLat.value = null;
      locationLon.value = null;
      locationInput.value = MELBOURNE_NOT_FOUND;
      setDetectedUnavailable();
    } else {
      const f = parseAddress(top.address || {});
      const value = formatSuburbPostcode(f);
      if (!value) {
        hasLocationConfirmed.value = false;
        locationLat.value = null;
        locationLon.value = null;
        locationInput.value = MELBOURNE_NOT_FOUND;
        setDetectedUnavailable();
      } else {
        setLocation(value, f.suburb || value, n(top.lat), n(top.lon));
        locationQueryMode.value = "suburb";
        await fetchActivities();
      }
    }
  } catch {
    hasLocationConfirmed.value = false;
    locationLat.value = null;
    locationLon.value = null;
    locationInput.value = MELBOURNE_NOT_FOUND;
    setDetectedUnavailable();
  }
  isApplying.value = false;
};

const totalPages = computed(() =>
  Math.max(1, Math.ceil((totalHint.value ?? 0) / UI_PAGE_SIZE)),
);
const totalCount = computed(() => totalHint.value ?? 0);
const visiblePages = computed(() => {
  const total = totalPages.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  return Array.from({ length: total }, (_, i) => i + 1).slice(
    Math.max(0, currentPage.value - 3),
    Math.min(total, currentPage.value + 3)
  );
});
const formatMeta = (a) => `${a.dateText} · ${a.timeText} · ${a.venue}`;
const detailsTo = (id) => {
  const q = {};
  if (locationLat.value != null && locationLon.value != null) {
    q.lat = String(locationLat.value);
    q.lon = String(locationLon.value);
  }
  return { path: `/events/${id}`, query: q };
};
const toggleFilter = async (k) => {
  activeFilters[k] = !activeFilters[k];
  if (!hasLocationConfirmed.value) return;
  totalHint.value = null;
  await fetchActivities(1);
};
const goToPage = async (p) => {
  const target = Math.min(totalPages.value, Math.max(1, p));
  await fetchActivities(target);
};
const printList = () => window.print();

watch(activities, () => {
  if (currentPage.value > totalPages.value)
    currentPage.value = totalPages.value;
});

onMounted(async () => {
  getLocation();
});
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg,
      var(--orange) 0%,
      var(--orange-deep) 100%);
  color: #fff;
  padding: 30px 28px;
}

.hero h2 {
  margin: 0;
  font-family: "Fraunces", serif;
  font-size: clamp(calc(36px * var(--font-scale)),
      calc(4vw * var(--font-scale)),
      calc(56px * var(--font-scale)));
  line-height: 1;
}

.hero h2 em {
  color: #8af8ed;
  font-style: italic;
}

.hero p {
  margin: 10px 0 20px;
  font-size: clamp(calc(18px * var(--font-scale)),
      calc(2.2vw * var(--font-scale)),
      calc(34px * var(--font-scale)));
  font-weight: 600;
}

.location-picker {
  width: 100%;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.18);
  color: #fff;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
}

.location-input {
  flex: 1;
  border: none;
  background: transparent;
  color: #fff;
  font-size: clamp(calc(18px * var(--font-scale)),
      calc(2vw * var(--font-scale)),
      calc(28px * var(--font-scale)));
  font-weight: 800;
  outline: none;
  min-width: 0;
}

.location-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

p.location-note {
  margin: 10px 4px 0;
  font-size: calc(20px * var(--font-scale));
  line-height: 1.4;
  color: rgba(196, 194, 194, 0.9);
}

.change-btn,
.apply-btn {
  border: 2px solid rgba(255, 255, 255, 0.65);
  border-radius: 999px;
  color: #fff;
  padding: 10px 18px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
  cursor: pointer;
}

.change-btn {
  background: transparent;
}

.change-btn:hover {
  background: rgba(255, 255, 255, 0.12);
}

.apply-btn {
  background: rgba(255, 255, 255, 0.16);
}

.apply-btn:hover {
  background: rgba(255, 255, 255, 0.24);
}

.change-btn:disabled,
.apply-btn:disabled {
  opacity: 0.75;
  cursor: wait;
}

.chips {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.chip {
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.65);
  background: transparent;
  color: #fff;
  padding: 10px 16px;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
  cursor: pointer;
}

.chip.solid {
  border-color: #b08b0a;
  background: var(--yellow);
  color: #1f1d1a;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px 12px;
}

.results-header h3 {
  margin: 0;
  font-size: clamp(calc(24px * var(--font-scale)),
      calc(2.5vw * var(--font-scale)),
      calc(36px * var(--font-scale)));
}

.print-btn {
  border: 2px solid #c7c8dc;
  border-radius: 999px;
  background: transparent;
  color: #616580;
  font-size: calc(16px * var(--font-scale));
  padding: 8px 14px;
  font-weight: 700;
  cursor: pointer;
}

.activity-list {
  padding: 0 18px 24px;
  display: grid;
  gap: 14px;
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 8px;
  margin-top: 4px;
}

.page-btn {
  border: 2px solid #c7c8dc;
  border-radius: 10px;
  background: #fff;
  color: #4b4f68;
  min-width: 44px;
  padding: 8px 10px;
  font-size: calc(14px * var(--font-scale));
  font-weight: 700;
  line-height: 1.2;
  cursor: pointer;
}

.page-btn.active {
  border-color: #008c7d;
  background: #008c7d;
  color: #fff;
}

.page-btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.event-card {
  background: var(--panel-2);
  border: 2px solid #cbccdf;
  border-radius: var(--radius-xl);
  padding: 20px;
}

.state-card {
  font-size: calc(20px * var(--font-scale));
  font-weight: 700;
  color: #565973;
}

.tags {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tag {
  border-radius: 999px;
  padding: 7px 13px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
}

.tag.green {
  background: #088f7e;
  color: #fff;
}

.tag.lilac {
  background: #d9d0f5;
  color: #4a42a8;
}

.tag.soft {
  background: #e6edf8;
  color: #365279;
}

.tag.warn {
  background: #ffe1e1;
  color: #a22b2b;
}

.distance {
  margin-left: auto;
  background: #caece7;
  border: 2px solid #a2d8d1;
  color: #0c7f72;
  border-radius: 14px;
  padding: 7px 11px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
}

.event-card h4 {
  margin: 16px 0 8px;
  font-family: "Fraunces", serif;
  font-size: clamp(calc(30px * var(--font-scale)),
      calc(3vw * var(--font-scale)),
      calc(46px * var(--font-scale)));
  line-height: 1.08;
}

.meta {
  margin: 0;
  font-size: calc(18px * var(--font-scale));
  font-weight: 700;
  color: #565973;
}

.desc {
  margin: 14px 0 18px;
  font-size: calc(20px * var(--font-scale));
  line-height: 1.35;
  color: #41445b;
}

.event-foot {
  border-top: 2px solid #d7d7e5;
  padding-top: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
}

.event-foot a {
  color: #06786f;
}

@media (max-width: 980px) {
  .results-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .event-foot {
    font-size: calc(17px * var(--font-scale));
    flex-direction: column;
    align-items: flex-start;
  }

  .chip {
    font-size: calc(16px * var(--font-scale));
  }
}
</style>
