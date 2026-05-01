<template>
  <MainLayout>
    <section class="details-page">
      <!-- Loading state -->
      <article v-if="isLoading" class="state-card">
        Loading event details...
      </article>

      <!-- Error state -->
      <article v-else-if="loadError" class="state-card error">
        {{ loadError }}
      </article>

      <!-- Event detail content -->
      <template v-else-if="event">
        <section class="hero-section">
          <RouterLink class="back-button" to="/discover">
            <span class="back-icon">‹</span>
            Back to activities
          </RouterLink>

          <div class="tags">
            <span class="tag price-tag">{{ priceText }}</span>
            <span v-if="event.category" class="tag category-tag">
              {{ event.category }}
            </span>
          </div>

          <h1>{{ event.name }}</h1>

          <p v-if="event.source" class="organiser">
            by {{ event.source }}
          </p>

          <div class="hero-circle"></div>
        </section>

        <section class="content-section">
          <article class="info-card">
            <div class="info-row">
              <div class="icon-box">📅</div>
              <div>
                <p class="label">Date and Time</p>
                <p class="value">{{ dateTimeText }}</p>
              </div>
            </div>

            <div class="divider"></div>

            <div class="info-row">
              <div class="icon-box">📍</div>
              <div>
                <p class="label">Venue</p>
                <p class="value">{{ venueText }}</p>
              </div>
            </div>

            <div class="divider"></div>

            <div class="info-row">
              <div class="icon-box">🚶</div>
              <div>
                <p class="label">Distance from you</p>
                <p class="value">{{ distanceText }}</p>
              </div>
            </div>

            <div class="divider"></div>

            <div class="info-row">
              <div class="icon-box">👥</div>
              <div>
                <p class="label">Restrictions</p>
                <p class="value">{{ restrictionsText }}</p>
              </div>
            </div>
          </article>

          <article v-if="event.image_url" class="image-card">
            <img :src="event.image_url" :alt="event.name" />
          </article>

          <article class="about-card">
            <p class="label">About this activity</p>
            <p class="description">
              {{ event.description || "Activity details are not available yet." }}
            </p>
          </article>

          <a
            v-if="event.url"
            class="external-link"
            :href="event.url"
            target="_blank"
            rel="noopener noreferrer"
          >
            Open original event page →
          </a>
        </section>
      </template>
    </section>
  </MainLayout>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import MainLayout from "../layouts/MainLayout.vue";

const route = useRoute();

const BASE_URL =
  import.meta.env.VITE_ACTIVITIES_API_URL || "https://connectlocal.duckdns.org";

const event = ref(null);
const isLoading = ref(false);
const loadError = ref("");

const n = (value) => (Number.isFinite(+value) ? +value : null);

const buildEventDetailUrl = () => {
  const url = new URL(`${BASE_URL}/api/events/${route.params.id}`);

  if (route.query.lat && route.query.lon) {
    url.searchParams.set("lat", route.query.lat);
    url.searchParams.set("lon", route.query.lon);
  }

  return url;
};

const fetchEventDetail = async () => {
  isLoading.value = true;
  loadError.value = "";

  try {
    const response = await fetch(buildEventDetailUrl().toString());

    if (!response.ok) {
      throw new Error(`Failed to load event details (${response.status})`);
    }

    event.value = await response.json();
  } catch (error) {
    loadError.value = "Unable to load this event right now. Please try again later.";
    event.value = null;
  } finally {
    isLoading.value = false;
  }
};

const priceText = computed(() => {
  if (!event.value) return "";

  if (event.value.is_free) return "Free";

  const price = n(event.value.min_price);
  return price == null ? "Paid" : `From $${price}`;
});

const dateTimeText = computed(() => {
  if (!event.value) return "Date and time TBC";

  return (
    event.value.session_datetime_summary ||
    event.value.datetime_summary ||
    "Date and time TBC"
  );
});

const venueText = computed(() => {
  if (!event.value) return "Venue TBC";

  const venue = event.value.venue || "Venue TBC";
  const suburb = event.value.suburb || "";

  return suburb ? `${venue}, ${suburb}` : venue;
});

const distanceText = computed(() => {
  if (!event.value) return "Distance unavailable";

  const distance = n(event.value.distance_km);

  return distance == null ? "Distance unavailable" : `${distance.toFixed(1)} km`;
});

const restrictionsText = computed(() => {
  if (!event.value) return "No restrictions listed";

  return event.value.restrictions || "No restrictions listed";
});

onMounted(() => {
  fetchEventDetail();
});
</script>

<style scoped>
.details-page {
  min-height: 100vh;
  background: #f8f8fb;
}

/* State cards */
.state-card {
  margin: 18px;
  padding: 24px;
  background: var(--panel-2);
  border: 2px solid #cbccdf;
  border-radius: var(--radius-xl);
  color: #41445b;
  font-size: calc(20px * var(--font-scale));
  font-weight: 800;
}

.state-card.error {
  color: #9f2a2a;
}

/* Hero section */
.hero-section {
  position: relative;
  overflow: hidden;
  padding: 28px 36px 64px;
  background: linear-gradient(135deg, #08a99a 0%, #00796f 100%);
  color: #ffffff;
}

.back-button {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 12px 28px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.28);
  color: #ffffff;
  font-weight: 800;
  font-size: calc(18px * var(--font-scale));
  text-decoration: none;
}

.back-icon {
  font-size: calc(34px * var(--font-scale));
  line-height: 0.8;
}

.tags {
  position: relative;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 40px;
}

.tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 13px 24px;
  border-radius: 999px;
  font-weight: 800;
  font-size: calc(18px * var(--font-scale));
}

.price-tag {
  background: #ff5a45;
  color: #ffffff;
}

.category-tag {
  background: rgba(255, 255, 255, 0.28);
  border: 2px solid rgba(255, 255, 255, 0.55);
  color: #ffffff;
}

h1 {
  position: relative;
  z-index: 2;
  max-width: 1000px;
  margin: 34px 0 14px;
  font-family: "Fraunces", serif;
  font-size: clamp(
    calc(40px * var(--font-scale)),
    calc(5vw * var(--font-scale)),
    calc(72px * var(--font-scale))
  );
  line-height: 1.05;
}

.organiser {
  position: relative;
  z-index: 2;
  margin: 0;
  font-size: calc(22px * var(--font-scale));
  font-weight: 700;
}

.hero-circle {
  position: absolute;
  top: -72px;
  right: -44px;
  width: 230px;
  height: 230px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.16);
}

/* Main content */
.content-section {
  padding: 36px 30px 60px;
}

.info-card,
.about-card,
.image-card {
  background: #ffffff;
  border: 3px solid #d0d0e3;
  border-radius: 32px;
  box-shadow: 0 14px 32px rgba(43, 42, 68, 0.06);
}

.info-card {
  padding: 38px 42px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 28px;
}

.icon-box {
  width: 64px;
  height: 64px;
  border-radius: 20px;
  background: #e3faf6;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #24243b;
  font-size: calc(28px * var(--font-scale));
  flex-shrink: 0;
}

.label {
  margin: 0 0 10px;
  color: #575770;
  font-size: calc(20px * var(--font-scale));
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 1.5px;
}

.value {
  margin: 0;
  color: #25243b;
  font-size: calc(28px * var(--font-scale));
  font-weight: 900;
  line-height: 1.25;
}

.divider {
  height: 3px;
  background: #d0d0e3;
  margin: 28px 0;
}

.image-card {
  margin-top: 28px;
  overflow: hidden;
}

.image-card img {
  display: block;
  width: 100%;
  max-height: 420px;
  object-fit: cover;
}

.about-card {
  margin-top: 28px;
  padding: 40px 44px;
}

.description {
  margin: 0;
  color: #25243b;
  font-size: calc(28px * var(--font-scale));
  line-height: 1.65;
}

.external-link {
  display: inline-flex;
  margin-top: 24px;
  padding: 16px 24px;
  border-radius: 999px;
  background: #06786f;
  color: #ffffff;
  font-size: calc(20px * var(--font-scale));
  font-weight: 900;
  text-decoration: none;
}

/* Mobile layout */
@media (max-width: 768px) {
  .hero-section {
    padding: 24px 22px 48px;
  }

  .content-section {
    padding: 24px 18px 44px;
  }

  .info-card {
    padding: 28px 24px;
  }

  .info-row {
    align-items: flex-start;
    gap: 18px;
  }

  .icon-box {
    width: 54px;
    height: 54px;
    font-size: calc(24px * var(--font-scale));
  }

  .value {
    font-size: calc(23px * var(--font-scale));
  }

  .about-card {
    padding: 30px 24px;
  }

  .description {
    font-size: calc(23px * var(--font-scale));
  }
}
</style>