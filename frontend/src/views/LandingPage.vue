<template>
  <div class="landing">

    <!-- ── NAVBAR ─────────────────────────────────────────────────────────── -->
    <nav class="land-nav">
      <div class="land-nav__inner">
        <!-- Brand: Peak (dark-green) + Path (accent-green) — matches sidebar style -->
        <router-link class="pp-brand land-brand" to="/">
          Peak<span>Path</span>
        </router-link>

        <ul class="land-nav__links">
          <li><a href="#how" class="nav-active">Explore</a></li>
          <li><a href="#featured">Guides</a></li>
          <li><a href="#stats">About</a></li>
        </ul>

        <div class="land-nav__actions">
          <router-link to="/login" class="land-btn-ghost">Login</router-link>
          <router-link to="/register" class="land-btn-orange">Get Started</router-link>
        </div>

        <!-- Mobile toggle -->
        <button class="land-nav__toggle" @click="menuOpen = !menuOpen">
          <i :class="menuOpen ? 'bi bi-x-lg' : 'bi bi-list'"></i>
        </button>
      </div>

      <!-- Mobile menu -->
      <div class="land-nav__mobile" :class="{ open: menuOpen }">
        <a href="#how" @click="menuOpen=false">Explore</a>
        <a href="#featured" @click="menuOpen=false">Guides</a>
        <a href="#stats" @click="menuOpen=false">About</a>
        <router-link to="/login" @click="menuOpen=false">Login</router-link>
        <router-link to="/register" class="land-btn-orange" style="text-align:center;" @click="menuOpen=false">Get Started</router-link>
      </div>
    </nav>

    <!-- ── HERO ───────────────────────────────────────────────────────────── -->
    <section class="land-hero" :style="{ backgroundImage: `url(${heroImg})` }">
      <div class="land-hero__overlay"></div>
      <div class="land-hero__content">
        <h1 class="land-hero__title">Explore. Book. Trek.</h1>
        <p class="land-hero__sub">
          Your next adventure starts here. Experience the world's most iconic
          trails with expert logistics and local insight.
        </p>
        <div class="land-hero__btns">
          <router-link to="/register" class="land-btn-orange land-btn-lg">
            Start Your Journey
          </router-link>
          <router-link to="/login" class="land-btn-dark land-btn-lg">
            View All Treks
          </router-link>
        </div>
      </div>
    </section>

    <!-- ── STATS BAR ──────────────────────────────────────────────────────── -->
    <section id="stats" class="land-stats">
      <div class="land-stats__grid">
        <div class="land-stat">
          <span class="land-stat__num">500+</span>
          <span class="land-stat__label">Curated Treks</span>
        </div>
        <div class="land-stat">
          <span class="land-stat__num">10K+</span>
          <span class="land-stat__label">Happy Trekkers</span>
        </div>
        <div class="land-stat">
          <span class="land-stat__num">50+</span>
          <span class="land-stat__label">Expert Guides</span>
        </div>
        <div class="land-stat">
          <span class="land-stat__num">15+</span>
          <span class="land-stat__label">States Covered</span>
        </div>
      </div>
    </section>

    <!-- ── HOW IT WORKS ───────────────────────────────────────────────────── -->
    <section id="how" class="land-how">
      <div class="land-how__head">
        <h2>How PeakPath Works</h2>
        <p>From dreaming to doing, we've streamlined the entire trekking experience.</p>
      </div>
      <div class="land-how__grid">
        <div class="land-how__card">
          <div class="land-how__icon" style="background:#1b4332;">
            <i class="bi bi-search"></i>
          </div>
          <h3>Discover</h3>
          <p>Search through hundreds of curated trails with detailed itineraries and photos.</p>
        </div>
        <div class="land-how__card">
          <div class="land-how__icon" style="background:#e67e22;">
            <i class="bi bi-calendar-event-fill"></i>
          </div>
          <h3>Book</h3>
          <p>Secure your spot with our easy booking system and flexible payment plans.</p>
        </div>
        <div class="land-how__card">
          <div class="land-how__icon" style="background:#1b4332;">
            <i class="bi bi-person-walking"></i>
          </div>
          <h3>Trek</h3>
          <p>Get on the trail with our expert staff support and 24/7 mountain safety monitoring.</p>
        </div>
      </div>
    </section>

    <!-- ── FEATURED TREKS ─────────────────────────────────────────────────── -->
    <section id="featured" class="land-featured">
      <div class="land-how__head">
        <h2>Featured Treks</h2>
        <p>Hand-picked adventures across India's most spectacular landscapes.</p>
      </div>
      <div class="land-feat__grid">
        <div v-for="t in featured" :key="t.name" class="land-feat__card">
          <div class="land-feat__badge" :class="'diff-' + t.diff.toLowerCase()">{{ t.diff }}</div>
          <div class="land-feat__body">
            <h4>{{ t.name }}</h4>
            <p class="land-feat__loc"><i class="bi bi-geo-alt-fill"></i> {{ t.loc }}</p>
            <div class="land-feat__meta">
              <span><i class="bi bi-clock"></i> {{ t.days }} days</span>
              <span><i class="bi bi-people"></i> {{ t.slots }} slots</span>
            </div>
          </div>
          <router-link to="/login" class="land-feat__link">View Details →</router-link>
        </div>
      </div>
      <div class="text-center mt-5">
        <router-link to="/login" class="land-btn-orange land-btn-lg">
          Browse All Treks <i class="bi bi-arrow-right ms-2"></i>
        </router-link>
      </div>
    </section>

    <!-- ── CTA BANNER ─────────────────────────────────────────────────────── -->
    <section class="land-cta">
      <div class="land-cta__inner">
        <h2>Ready for your next summit?</h2>
        <p>Join thousands of trekkers who trust PeakPath for their Himalayan adventures.</p>
        <router-link to="/register" class="land-btn-orange land-btn-lg mt-3">
          Create Free Account
        </router-link>
      </div>
    </section>

    <!-- ── FOOTER ─────────────────────────────────────────────────────────── -->
    <footer class="land-footer">
      <div class="land-footer__inner">
        <div class="land-footer__brand">
          <!-- Same two-tone style as sidebar, but on dark bg both parts are light -->
          <div style="font-family:'Outfit',sans-serif;font-weight:900;font-size:1.4rem;color:#fff;">
            Peak<span style="color:#74c69d;">Path</span>
          </div>
          <p class="mt-2" style="color:rgba(255,255,255,0.5);font-size:0.82rem;letter-spacing:1.5px;text-transform:uppercase;">Explore. Book. Trek.</p>
        </div>
        <div class="land-footer__links">
          <router-link to="/login">Login</router-link>
          <router-link to="/register">Register</router-link>
          <a href="#how">How it Works</a>
          <a href="#stats">About</a>
        </div>
      </div>
      <div class="land-footer__copy">
        © {{ new Date().getFullYear() }} PeakPath. All rights reserved.
      </div>
    </footer>

  </div>
</template>

<script setup>
import { ref } from 'vue'
import heroImg from '../assets/kedarnath.jpg'

const menuOpen = ref(false)

const featured = [
  { name: 'Valley of Flowers Trek', loc: 'Uttarakhand, India',  diff: 'Easy',     days: 6,  slots: 30 },
  { name: 'Roopkund Trek',          loc: 'Chamoli, Uttarakhand',diff: 'Hard',     days: 8,  slots: 20 },
  { name: 'Hampta Pass Trek',       loc: 'Kullu, Himachal Pradesh', diff: 'Moderate', days: 5, slots: 25 },
]
</script>

<style scoped>
/* ── Base ─────────────────────────────────────────────────────────────────── */
.landing { font-family: 'Inter', sans-serif; color: #1a2e22; }

/* ── NAVBAR ──────────────────────────────────────────────────────────────── */
.land-nav {
  position: sticky; top: 0; z-index: 200;
  background: #fff;
  box-shadow: 0 1px 12px rgba(0,0,0,0.08);
}
.land-nav__inner {
  max-width: 1440px; margin: auto;
  display: flex; align-items: center;
  justify-content: space-between;   /* brand far-left, actions far-right */
  padding: 0 2rem; height: 64px;
}
/* Override pp-brand for light navbar background */
.land-brand {
  font-size: 1.35rem !important;
  color: #1b4332 !important;
  text-decoration: none;
}
.land-brand :deep(span), .land-brand span { color: #40916c !important; }
.land-nav__links {
  display: flex; list-style: none; margin: 0; padding: 0; gap: 0.25rem;
  /* centered between brand and actions */
}
.land-nav__links a {
  padding: 0.4rem 0.9rem; border-radius: 6px;
  font-size: 0.92rem; font-weight: 500;
  color: #374151; text-decoration: none; transition: color 0.15s;
}
.land-nav__links a:hover, .land-nav__links a.nav-active { color: #e67e22; }
.land-nav__actions { display: flex; gap: 0.75rem; align-items: center; flex-shrink: 0; }
.land-nav__toggle { display: none; background: none; border: none; font-size: 1.4rem; cursor: pointer; color: #1b4332; }

/* ── Buttons ──────────────────────────────────────────────────────────────── */
.land-btn-orange {
  background: #e67e22; color: #fff;
  border: none; border-radius: 8px;
  font-weight: 700; padding: 0.55rem 1.3rem;
  text-decoration: none; display: inline-block;
  transition: background 0.2s, transform 0.1s;
}
.land-btn-orange:hover { background: #d35400; color: #fff; transform: translateY(-1px); }
.land-btn-ghost {
  color: #1b4332; font-weight: 600; text-decoration: none;
  padding: 0.5rem 1rem; border-radius: 8px;
  transition: background 0.15s;
}
.land-btn-ghost:hover { background: #f0faf4; }
.land-btn-dark {
  background: rgba(255,255,255,0.15);
  border: 2px solid rgba(255,255,255,0.8);
  color: #fff; border-radius: 8px; font-weight: 700;
  padding: 0.65rem 1.5rem; text-decoration: none;
  backdrop-filter: blur(4px);
  transition: background 0.2s;
}
.land-btn-dark:hover { background: rgba(255,255,255,0.25); color: #fff; }
.land-btn-lg { padding: 0.85rem 2rem; font-size: 1rem; border-radius: 10px; }

/* ── Mobile nav ──────────────────────────────────────────────────────────── */
.land-nav__mobile {
  display: none; flex-direction: column; gap: 0.5rem;
  padding: 1rem 1.5rem 1.25rem; border-top: 1px solid #e8f0eb;
  background: #fff;
}
.land-nav__mobile a { color: #374151; font-weight: 500; text-decoration: none; padding: 0.4rem 0; }

/* ── HERO ─────────────────────────────────────────────────────────────────── */
.land-hero {
  position: relative; min-height: 88vh;
  display: flex; align-items: flex-end;
  background-position: center center;
  background-size: cover;
  background-repeat: no-repeat;
}
.land-hero__overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(0,0,0,0.72) 0%, rgba(0,0,0,0.35) 60%, transparent 100%);
}
.land-hero__content {
  position: relative; z-index: 2;
  padding: 4rem 5vw 5rem;
  max-width: 640px;
}
.land-hero__title {
  font-family: 'Outfit', sans-serif;
  font-size: clamp(2.4rem, 5vw, 4rem);
  font-weight: 900; color: #fff;
  line-height: 1.1; margin-bottom: 1rem;
}
.land-hero__sub {
  font-size: 1.1rem; color: rgba(255,255,255,0.88);
  line-height: 1.6; margin-bottom: 2rem; max-width: 500px;
}
.land-hero__btns { display: flex; gap: 1rem; flex-wrap: wrap; }

/* ── STATS ────────────────────────────────────────────────────────────────── */
.land-stats {
  background: #1b4332;
  padding: 2rem 1.5rem;
}
.land-stats__grid {
  max-width: 900px; margin: auto;
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 1rem; text-align: center;
}
.land-stat__num {
  display: block; font-family: 'Outfit', sans-serif;
  font-size: 2rem; font-weight: 900; color: #e67e22;
}
.land-stat__label {
  display: block; font-size: 0.85rem;
  color: rgba(255,255,255,0.7); margin-top: 4px;
}

/* ── HOW IT WORKS ─────────────────────────────────────────────────────────── */
.land-how { padding: 5rem 1.5rem; background: #fff; }
.land-how__head {
  text-align: center; margin-bottom: 3.5rem;
}
.land-how__head h2 {
  font-family: 'Outfit', sans-serif; font-size: 2rem;
  font-weight: 800; color: #1a2e22; margin-bottom: 0.5rem;
}
.land-how__head p { color: #6c757d; font-size: 1rem; }
.land-how__grid {
  max-width: 900px; margin: auto;
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 2.5rem; text-align: center;
}
.land-how__icon {
  width: 72px; height: 72px; border-radius: 18px;
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 1.25rem; font-size: 1.8rem; color: #fff;
}
.land-how__card h3 { font-weight: 800; font-size: 1.1rem; margin-bottom: 0.6rem; }
.land-how__card p  { color: #6c757d; font-size: 0.92rem; line-height: 1.6; }

/* ── FEATURED ─────────────────────────────────────────────────────────────── */
.land-featured { padding: 5rem 1.5rem; background: #f4f7f5; }
.land-feat__grid {
  max-width: 1100px; margin: 0 auto 1rem;
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}
.land-feat__card {
  background: #fff; border-radius: 14px;
  box-shadow: 0 4px 20px rgba(45,106,79,0.1);
  overflow: hidden; display: flex; flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}
.land-feat__card:hover { transform: translateY(-4px); box-shadow: 0 8px 30px rgba(45,106,79,0.18); }
.land-feat__badge {
  padding: 0.6rem 1.25rem;
  font-weight: 700; font-size: 0.8rem; letter-spacing: 1px;
  text-transform: uppercase;
}
.diff-easy     { background: #d1fae5; color: #065f46; }
.diff-moderate { background: #fef3c7; color: #92400e; }
.diff-hard     { background: #fee2e2; color: #991b1b; }
.land-feat__body { padding: 1.25rem; flex: 1; }
.land-feat__body h4 { font-weight: 800; font-size: 1rem; margin-bottom: 0.4rem; }
.land-feat__loc { color: #6c757d; font-size: 0.85rem; margin-bottom: 0.75rem; }
.land-feat__loc i { color: #2d6a4f; margin-right: 4px; }
.land-feat__meta { display: flex; gap: 1rem; font-size: 0.82rem; color: #6c757d; }
.land-feat__meta i { margin-right: 3px; color: #40916c; }
.land-feat__link {
  display: block; padding: 0.85rem 1.25rem;
  background: #f8fffe; border-top: 1px solid #e8f0eb;
  color: #2d6a4f; font-weight: 700; font-size: 0.88rem;
  text-decoration: none; transition: background 0.15s;
}
.land-feat__link:hover { background: #d8f3dc; }

/* ── CTA ──────────────────────────────────────────────────────────────────── */
.land-cta {
  background: linear-gradient(135deg, #1b4332, #2d6a4f);
  padding: 5rem 1.5rem; text-align: center;
}
.land-cta__inner { max-width: 600px; margin: auto; }
.land-cta h2 { font-family: 'Outfit', sans-serif; font-size: 2.2rem; font-weight: 900; color: #fff; margin-bottom: 0.75rem; }
.land-cta p  { color: rgba(255,255,255,0.8); font-size: 1.05rem; }
.land-cta .land-btn-orange { margin-top: 1.5rem; }

/* ── FOOTER ──────────────────────────────────────────────────────────────── */
.land-footer { background: #0f2318; padding: 2.5rem 1.5rem 1rem; }
.land-footer__inner {
  max-width: 1100px; margin: 0 auto 1.5rem;
  display: flex; align-items: flex-start; justify-content: space-between;
  flex-wrap: wrap; gap: 2rem;
}
.land-footer__links { display: flex; gap: 1.5rem; flex-wrap: wrap; align-items: center; }
.land-footer__links a { color: rgba(255,255,255,0.55); text-decoration: none; font-size: 0.88rem; transition: color 0.15s; }
.land-footer__links a:hover { color: #74c69d; }
.land-footer__copy { text-align: center; color: rgba(255,255,255,0.25); font-size: 0.78rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.06); max-width: 1100px; margin: auto; }

/* ── Responsive ──────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
  .land-nav__links, .land-nav__actions { display: none; }
  .land-nav__toggle { display: block; margin-left: auto; }
  .land-nav__mobile { display: flex; }
  .land-nav__mobile:not(.open) { display: none; }

  .land-stats__grid { grid-template-columns: repeat(2, 1fr); }
  .land-how__grid   { grid-template-columns: 1fr; gap: 2rem; }
  .land-feat__grid  { grid-template-columns: 1fr; }
  .land-hero { min-height: 70vh; }
  .land-hero__content { padding: 2.5rem 1.5rem 3.5rem; }
}
@media (max-width: 480px) {
  .land-stats__grid { grid-template-columns: repeat(2, 1fr); }
  .land-hero__btns { flex-direction: column; }
  .land-btn-lg { text-align: center; }
}
</style>
