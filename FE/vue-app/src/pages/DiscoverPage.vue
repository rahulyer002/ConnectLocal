<template>
  <MainLayout>
    <section class="hero">
      <h2>Find your next <em>warm moment</em></h2>
      <p>Free and low-cost activities near {{ nearbyLabel }}</p>

      <form class="location-picker" @submit.prevent="applyManualLocation">
        <input class="location-input" v-model="locationInput" type="text" aria-label="Location"
          placeholder="Please enter suburb or postcode in Australia." />
        <button type="button" class="change-btn" :disabled="isLocating" @click="getLocation">
          {{ isLocating ? "Locating..." : "Locate" }}
        </button>
        <button type="submit" class="apply-btn" :disabled="isApplying || !locationInput.trim()">
          {{ isApplying ? "Updating..." : "Change" }}
        </button>
      </form>

      <div class="chips">
        <button v-for="chip in chips" :key="chip.key" class="chip" :class="{ solid: activeFilters[chip.key] }"
          @click="toggleFilter(chip.key)">
          {{ chip.label }}
        </button>
      </div>
    </section>

    <section class="results-header">
      <h3>{{ filteredActivities.length }} activities</h3>
      <button class="print-btn" type="button" @click="printList">
        Print list
      </button>
    </section>

    <section class="activity-list" v-if="!isLoading && !loadError && filteredActivities.length">
      <article class="event-card" v-for="activity in pagedActivities" :key="activity.id">
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
          <a v-if="activity.link" :href="activity.link" target="_blank" rel="noreferrer">View details →</a>
          <span v-else>Details coming soon</span>
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

        <button class="page-btn" type="button" :disabled="currentPage === totalPages"
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
        <template v-if="activities.length">
          Loaded {{ activities.length }} activities, but none match current
          filters. Try removing one or two filters.
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
const FETCH_LIMIT = 20;
const MAX_FETCH = 30;
const UI_PAGE_SIZE = 3;

const locationInput = ref("");
const nearbyLabel = ref("your area");
const isLocating = ref(false);
const isApplying = ref(false);
const activities = ref([]);
const isLoading = ref(false);
const loadError = ref("");
const currentPage = ref(1);

const activeFilters = reactive({
  free: true,
  thisWeek: true,
  closeHome: true,
  indoor: false,
  easyAccess: false,
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
const total = (p) => n(p?.total);

const normalize = (r, i) => {
  const date = d(r.datetime_start);
  const km = n(r.distance_km);
  const cost = n(r.min_price);
  const isFree = b(r.is_free) || (cost != null && cost <= 10);
  const indoor = b(r.indoor);
  const easyAccess = b(r.easy_access);
  const venue = r.venue || "Location TBC";
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
        ? "Spots info unavailable"
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

const fetchActivities = async () => {
  isLoading.value = true;
  loadError.value = "";
  try {
    const out = [];
    const seen = new Set();
    let off = 0;
    let hint = null;
    let req = 0;
    for (let i = 0; i < MAX_FETCH; i += 1) {
      const u = new URL(API);
      u.searchParams.set("offset", off);
      u.searchParams.set("rows", FETCH_LIMIT);
      u.searchParams.set("is_free", activeFilters.free ? "true" : "false");
      if (locationInput.value.trim()) {
        u.searchParams.set("suburb", locationInput.value.trim().toLowerCase());
      }
      const r = await fetch(u.toString());
      if (!r.ok) throw new Error(`Failed to load activities (${r.status})`);
      const p = await r.json();
      const list = arr(p);
      hint = total(p) ?? hint;
      req += 1;
      if (!list.length) break;
      let added = 0;
      for (const e of list) {
        const k = String(e?.id ?? e?._id ?? JSON.stringify(e));
        if (seen.has(k)) continue;
        seen.add(k);
        out.push(e);
        added += 1;
      }
      if (!added) break;
      off += list.length;
      if (hint != null && out.length >= hint) break;
    }
    if (!out.length) {
      const r = await fetch(API);
      if (!r.ok) throw new Error(`Failed to load activities (${r.status})`);
      out.push(...arr(await r.json()));
    }
    activities.value = out.map(normalize);
    console.info(
      `Loaded ${activities.value.length} activities${hint ? ` total=${hint}` : ""}`,
    );
  } catch (e) {
    loadError.value = "Unable to load activities right now. Please try again later.";
    activities.value = [];
  } finally {
    isLoading.value = false;
  }
};

const setLocation = (text, suburb = "") => {
  locationInput.value = text;
  nearbyLabel.value = suburb || text.split(",")[0] || "your area";
  setDetectedLocation(text);
};

const parseAddress = (a = {}) => {
  const suburb =
    a.suburb || a.neighbourhood || a.city_district || a.town || a.village || a.city || "";
  const state = (a["ISO3166-2-lvl4"] || "").split("-")[1] || a.state || "";
  const text = `${[suburb, state].filter(Boolean).join(", ")} ${a.postcode || ""}`.trim();
  return { suburb, text };
};

const getLocation = () => {
  if (!navigator.geolocation)
    return (
      (locationInput.value = "Geolocation not supported"),
      setDetectedUnavailable()
    );
  isLocating.value = true;
  navigator.geolocation.getCurrentPosition(
    async ({ coords }) => {
      try {
        const r = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${coords.latitude}&lon=${coords.longitude}&accept-language=en`,
        );
        const f = parseAddress((await r.json()).address || {});
        setLocation(
          f.text ||
          `${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`,
          f.suburb,
        );
      } catch {
        setLocation(
          `${coords.latitude.toFixed(5)}, ${coords.longitude.toFixed(5)}`,
        );
      }
      isLocating.value = false;
    },
    () => {
      locationInput.value = "Unable to get location";
      setDetectedUnavailable();
      isLocating.value = false;
    },
  );
};

const applyManualLocation = async () => {
  const q = locationInput.value.trim();
  if (!q) return;
  isApplying.value = true;
  try {
    const r = await fetch(
      `https://nominatim.openstreetmap.org/search?format=jsonv2&q=${encodeURIComponent(q)}&addressdetails=1&limit=1&accept-language=en`,
    );
    const top = (await r.json())?.[0];
    if (!top) locationInput.value = "Address not found";
    else {
      const f = parseAddress(top.address || {});
      setLocation(f.text || top.display_name || q, f.suburb || q);
    }
  } catch {
    locationInput.value = "Unable to update location";
  }
  isApplying.value = false;
};

const isThisWeek = (a) =>
  a.date &&
  a.date >= new Date() &&
  a.date <= new Date(Date.now() + 7 * 86400000);
const isClose = (a) =>
  a.distanceKm != null
    ? a.distanceKm <= CLOSE_KM
    : !nearbyLabel.value ||
    nearbyLabel.value === "your area" ||
    `${a.suburb || a.venue}`
      .toLowerCase()
      .includes(nearbyLabel.value.toLowerCase());

const filteredActivities = computed(() =>
  activities.value.filter(
    (a) =>
      (!activeFilters.free || a.isFree) &&
      (!activeFilters.thisWeek || isThisWeek(a)) &&
      (!activeFilters.closeHome || isClose(a)) &&
      (!activeFilters.indoor || a.indoor) &&
      (!activeFilters.easyAccess || a.easyAccess),
  ),
);
const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredActivities.value.length / UI_PAGE_SIZE)),
);
const pagedActivities = computed(() =>
  filteredActivities.value.slice(
    (currentPage.value - 1) * UI_PAGE_SIZE,
    currentPage.value * UI_PAGE_SIZE,
  ),
);
const visiblePages = computed(() => {
  const total = totalPages.value;
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  return Array.from({ length: total }, (_, i) => i + 1).slice(
    Math.max(0, currentPage.value - 3),
    Math.min(total, currentPage.value + 3)
  );
});
const formatMeta = (a) => `${a.dateText} · ${a.timeText} · ${a.venue}`;
const toggleFilter = (k) => (activeFilters[k] = !activeFilters[k]);
const goToPage = (p) =>
  (currentPage.value = Math.min(totalPages.value, Math.max(1, p)));
const printList = () => window.print();

watch(filteredActivities, () => {
  if (currentPage.value > totalPages.value)
    currentPage.value = totalPages.value;
});

onMounted(async () => {
  await fetchActivities();
  getLocation();
});
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg,
      #0c8b7d 0%,
      #0a756a 100%);
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
  color: #d8f3ef;
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

/* ✅ 按钮统一绿色 */
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
  background: rgba(12, 139, 125, 0.5);
}

.apply-btn:hover {
  background: rgba(12, 139, 125, 0.7);
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

/* ✅ filter 选中绿色 */
.chip.solid {
  border-color: #0c8b7d;
  background: #e3faf5;
  color: #0c8b7d;
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

/* ✅ pagination 绿色 */
.page-btn.active {
  border-color: #0c8b7d;
  background: #0c8b7d;
  color: #fff;
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
  cursor: pointer;
}

.page-btn:disabled {
  opacity: 0.45;
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

.tag.green {
  background: #0c8b7d;
  color: #fff;
}

.distance {
  margin-left: auto;
  background: #e3faf5;
  border: 2px solid #a2d8d1;
  color: #0c8b7d;
  border-radius: 14px;
  padding: 7px 11px;
  font-size: calc(16px * var(--font-scale));
  font-weight: 800;
}

.event-foot a {
  color: #0c8b7d;
}
</style>