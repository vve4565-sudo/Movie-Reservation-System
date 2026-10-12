const API_BASE = "/api";

const demoMovies = [
  { id: "1", title: "Дюна: Часть вторая", genre: "Фантастика", director: "Дени Вильнёв", description: "Пол Атрейдес объединяется с Чани и фременами, чтобы отомстить за свою семью." },
  { id: "2", title: "Оппенгеймер", genre: "Драма", director: "Кристофер Нолан", description: "История учёного, стоявшего за созданием атомной бомбы." },
  { id: "3", title: "Барби", genre: "Комедия", director: "Грета Гервиг", description: "Самое розовое приключение выходит за пределы идеального мира." },
  { id: "4", title: "Интерстеллар", genre: "Фантастика", director: "Кристофер Нолан", description: "Путешествие сквозь пространство и время ради будущего человечества." }
];

const movieGrid = document.querySelector("#movieGrid");
const moviePage = document.querySelector("#moviePage");
const movieDetail = document.querySelector("#movieDetail");
const movieShowList = document.querySelector("#movieShowList");
const startDateInput = document.querySelector("#startDate");
const bookingDialog = document.querySelector("#bookingDialog");
const loginDialog = document.querySelector("#loginDialog");
const registerDialog = document.querySelector("#registerDialog");
const reservationsDialog = document.querySelector("#reservationsDialog");
const myReservationsBtn = document.querySelector("#myReservationsBtn");

let movies = demoMovies;
let selectedSeat = null;
let selectedShow = null;
let currentMovie = null;

function getStoredUser() {
  try {
    return JSON.parse(sessionStorage.getItem("cinemaUser") || "null");
  } catch {
    return null;
  }
}

function syncAuthUI() {
  const loginBtn = document.querySelector("#loginBtn");
  const registerBtn = document.querySelector("#registerBtn");
  const bookingsBtn = document.querySelector("#myReservationsBtn");
  if (!loginBtn) return;

  const isLoggedIn = Boolean(getStoredUser() || sessionStorage.getItem("cinemaAccessToken"));
  const adminLogout = document.querySelector("#adminLogout");
  const isAdminUser = typeof window.isAdmin === "function" ? window.isAdmin() : false;

  loginBtn.classList.toggle("is-authenticated", isLoggedIn);
  loginBtn.setAttribute("title", isLoggedIn ? "Вы авторизованы" : "Войти");
  loginBtn.innerHTML = isLoggedIn
    ? '<span class="login-btn-icon" aria-hidden="true">✓</span>'
    : '<span class="login-btn-text">Войти</span>';

  if (registerBtn) {
    registerBtn.hidden = isLoggedIn;
  }

  if (bookingsBtn) {
    bookingsBtn.hidden = !isLoggedIn;
  }

  if (adminLogout) {
    adminLogout.hidden = !isAdminUser;
  }
}

async function openMyReservations() {
  const userId = getStoredUser()?.id || getTokenUserId();
  if (!userId) {
    loginDialog?.showModal();
    return;
  }

  const list = document.querySelector("#reservationsList");
  if (!list) return;

  list.innerHTML = '<div class="loading-state">Загружаем ваши бронирования…</div>';
  reservationsDialog?.showModal();

  try {
    const raw = await api(`/reservation/user/${userId}`);
    const reservations = Array.isArray(raw) ? raw : [];
    const ownReservations = reservations.filter(reservation =>
      String(reservation.user_id ?? reservation.user?.id ?? "") === String(userId)
    );

    if (!ownReservations.length) {
      list.innerHTML = '<div class="empty-state">У вас пока нет активных бронирований.</div>';
      return;
    }

    list.innerHTML = ownReservations.map(reservation => {
      const show = reservation.show || {};
      const title = show.movie?.title || show.title || "Сеанс";
      const hall = show.hall?.hall_number ?? show.hall_number ?? "Зал";
      const start = show.start || "";
      const seat = reservation.chair?.chair_number ?? reservation.chair_id ?? "—";
      const formattedDate = start ? `${formatDate(start)} · ${formatTime(start)}` : "Дата не указана";
      return `
        <article class="reservation-item">
          <div>
            <strong>${escapeHtml(title)}</strong>
            <div class="reservation-meta">${escapeHtml(formattedDate)} · ${escapeHtml(`Зал ${hall}`)}</div>
          </div>
          <span class="reservation-seat">Место ${escapeHtml(seat)}</span>
        </article>`;
    }).join("");
  } catch (error) {
    console.error("Не удалось загрузить бронирования:", error);
    list.innerHTML = '<div class="empty-state">Не удалось загрузить ваши бронирования.</div>';
  }
}

async function api(path, options = {}) {
  const res = await cinemaApiFetch(API_BASE, path, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

async function loadData() {
  try {
    const raw = await api("/movies/");
    movies = Array.isArray(raw) ? raw : raw ? [raw] : [];
  } catch (error) {
    console.error("Не удалось загрузить фильмы:", error);
    movies = demoMovies;
  }
  renderMovies("all");
}

function renderMovies(filter = "all") {
  const list = filter === "all" ? movies : movies.filter(m => m.genre === filter);
  movieGrid.innerHTML = list.map(m => `
    <article class="movie-card" data-movie-id="${escapeHtml(m.id)}" tabindex="0" role="button" aria-label="Открыть фильм ${escapeHtml(m.title)}">
      <div class="poster" style="background-image: linear-gradient(transparent 25%, #000d), url('${getImageUrl(m.image)}'); background-size:cover; background-position:center;">
        <span class="poster-title">${escapeHtml(m.title)}</span>
      </div>
      <div class="movie-info">
        <div class="movie-meta"><span>${escapeHtml(m.genre)}</span><span>${escapeHtml(m.director)}</span></div>
        <p>${escapeHtml(m.description)}</p>
        <button class="primary-btn full movie-open-btn" type="button">Подробнее и сеансы <span>→</span></button>
      </div>
    </article>`).join("");

  movieGrid.querySelectorAll(".movie-card").forEach(card => {
    const open = () => openMoviePage(card.dataset.movieId);
    card.addEventListener("click", open);
    card.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(); }
    });
  });
}

async function openMoviePage(movieId) {
  currentMovie = movies.find(m => String(m.id) === String(movieId));
  if (!currentMovie) return;

  document.querySelector("#movies").hidden = true;
  document.querySelector("#how").hidden = true;
  moviePage.hidden = false;
  history.pushState({ movieId: currentMovie.id }, "", `#movie/${encodeURIComponent(currentMovie.id)}`);

  movieDetail.innerHTML = `
    <div class="movie-detail-poster" style="background-image: linear-gradient(transparent 35%, #000d), url('${getImageUrl(currentMovie.image)}');"></div>
    <div class="movie-detail-copy">
      <div class="eyebrow">ФИЛЬМ</div>
      <h1>${escapeHtml(currentMovie.title)}</h1>
      <div class="movie-detail-meta">
        <span>${escapeHtml(currentMovie.genre)}</span>
        <span>${escapeHtml(currentMovie.director)}</span>
      </div>
      <p>${escapeHtml(currentMovie.description)}</p>
    </div>`;

  const today = new Date();
  startDateInput.value = toDateInput(today);

  await loadAvailableShows();
  moviePage.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function loadAvailableShows() {
  if (!currentMovie) return;
  const startDate = startDateInput.value;

  if (!startDate) return;

  movieShowList.innerHTML = `<div class="loading-state">Загружаем доступные сеансы…</div>`;

  try {
    const params = new URLSearchParams({
      movie_id: String(currentMovie.id),
      start: `${startDate}T00:00:00`,
    });
    const raw = await api(`/shows/available?${params.toString()}`);
    const shows = Array.isArray(raw) ? raw : (raw ? [raw] : []);
    renderAvailableShows(shows);
  } catch (error) {
    console.error("Не удалось загрузить доступные сеансы:", error);
    movieShowList.innerHTML = `<div class="empty-state">Не удалось загрузить сеансы. Проверьте API и параметры запроса.</div>`;
  }
}

function renderAvailableShows(shows) {
  if (!shows.length) {
    movieShowList.innerHTML = `<div class="empty-state">На выбранную дату доступных сеансов нет.</div>`;
    return;
  }

  movieShowList.innerHTML = shows.map(show => {
    const date = show.start_date || show.date || "";
    const time = show.start_time || show.time || formatTime(show.start_date);
    const hall = 'Зал: ' + show.hall.hall_number;
    const title = show.title || currentMovie.title;
    return `
      <article class="show">
        <div>
          <div class="show-title">${escapeHtml(title)}</div>
          <div class="show-meta">${escapeHtml(hall)}${date ? ` · ${escapeHtml(formatDate(date))}` : ""}</div>
        </div>
        <div class="times">
          <button class="time-btn" type="button" data-show-id="${escapeHtml(show.id ?? "")}">${escapeHtml(time || "Выбрать")}</button>
        </div>
        
      </article>`;
  }).join("");

  movieShowList.querySelectorAll(".time-btn").forEach((button, index) => {
    button.addEventListener("click", () => openBookingFromApiShow(shows[index], button.textContent));
  });
}

async function openBookingFromApiShow(show, time) {
  selectedShow = show;
  selectedSeat = null;
  document.querySelector("#modalTitle").textContent = currentMovie?.title || show.title || "Выберите место";
  const hallNumber = show.hall?.hall_number ?? show.hall_number;
  const showDate = show.start || show.start_date || show.date || "";
  document.querySelector("#modalShow").textContent =
    `${hallNumber ? `Зал ${hallNumber} · ` : ""}${showDate ? formatDate(showDate) : ""} ${time || ""}`.trim();
  const seatMap = document.querySelector("#seatMap");
  const confirmButton = document.querySelector("#confirmBtn");
  seatMap.innerHTML = `<p class="seat-map-message" role="status">Загружаем схему зала…</p>`;
  confirmButton.disabled = true;
  bookingDialog.showModal();

  const hallId = show.hall_id || show.hall?.id;
  if (!hallId || !show.id) {
    seatMap.innerHTML = `<p class="seat-map-message" role="alert">Не удалось определить зал или сеанс.</p>`;
    console.error("Не удалось загрузить кресла: в данных сеанса отсутствует hall_id или id.");
    return;
  }

  try {
    const [chairsResponse, reservationsResponse] = await Promise.all([
      api(`/shows/hall/${encodeURIComponent(hallId)}/`),
      api(`/reservation/${encodeURIComponent(show.id)}/`)
    ]);
    if (!Array.isArray(chairsResponse)) {
      throw new Error("API вернул некорректную структуру кресел.");
    }
    const chairs = chairsResponse;
    const reservations = Array.isArray(reservationsResponse)
      ? reservationsResponse
      : reservationsResponse
        ? [reservationsResponse]
        : [];
    renderSeatMap(chairs, reservations);
  } catch (error) {
    console.error("Не удалось загрузить схему зала и бронирования:", error);
    seatMap.innerHTML = `<p class="seat-map-message" role="alert">Не удалось загрузить схему зала. Попробуйте позже.</p>`;
  }
}

function renderSeatMap(chairs, reservations) {
  const seatMap = document.querySelector("#seatMap");
  const confirmButton = document.querySelector("#confirmBtn");
  const reservedChairIds = new Set(
    reservations
      .map(reservation => reservation.chair_id)
      .filter(Boolean)
      .map(chairId => String(chairId).toLowerCase())
  );

  if (!chairs.length) {
    seatMap.innerHTML = `<p class="seat-map-message" role="status">В этом зале нет кресел.</p>`;
    return;
  }

  seatMap.innerHTML = chairs
    .slice()
    .sort((left, right) => left.chair_number - right.chair_number)
    .map(chair => {
      const chairId = String(chair.id);
      const chairNumber = Number(chair.chair_number);
      const busy = reservedChairIds.has(chairId.toLowerCase());
      return `
        <button type="button" class="seat ${busy ? "busy" : "free"}" data-chair-id="${escapeHtml(chairId)}"
          data-chair-number="${chairNumber}" ${busy ? "disabled" : ""}
          aria-label="${busy ? "Занято, " : ""}Место ${chairNumber}" title="Место ${chairNumber}">
          ${chairNumber}
        </button>`;
    })
    .join("");

  seatMap.querySelectorAll(".seat.free").forEach(seat => {
    seat.addEventListener("click", () => {
      seatMap.querySelectorAll(".seat.selected").forEach(selected => selected.classList.remove("selected"));
      seat.classList.add("selected");
      selectedSeat = {
        id: seat.dataset.chairId,
        chair_number: Number(seat.dataset.chairNumber)
      };
      confirmButton.disabled = false;
    });
  });
}

document.querySelector("#confirmBtn").addEventListener("click", async () => {
  if (!selectedSeat) return alert("Выберите место.");
  try {
    await api("/reservation/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ show_id: selectedShow.id, chair_id: selectedSeat.id })
    });
    alert("Билет забронирован!");
  } catch {
    alert(`Не удалось забронировать место ${selectedSeat.chair_number}. Проверьте авторизацию и подключение к API.`);
  }
  bookingDialog.close();
});

document.querySelectorAll(".filter").forEach(btn => btn.addEventListener("click", () => {
  document.querySelectorAll(".filter").forEach(x => x.classList.remove("active"));
  btn.classList.add("active");
  renderMovies(btn.dataset.genre);
}));

startDateInput.addEventListener("change", loadAvailableShows);

document.querySelector("#backToMovies").addEventListener("click", () => {
  moviePage.hidden = true;
  document.querySelector("#movies").hidden = false;
  document.querySelector("#how").hidden = false;
  history.pushState({}, "", "#movies");
  document.querySelector("#movies").scrollIntoView({ behavior: "smooth" });
});

window.addEventListener("popstate", () => {
  if (!location.hash.startsWith("#movie/")) {
    moviePage.hidden = true;
    document.querySelector("#movies").hidden = false;
    document.querySelector("#how").hidden = false;
  }
});

document.querySelector("#loginBtn").addEventListener("click", () => {
  if (getStoredUser() || sessionStorage.getItem("cinemaAccessToken")) {
    openMyReservations();
    return;
  }
  loginDialog.showModal();
});
document.querySelector("#registerBtn")?.addEventListener("click", () => {
  if (getStoredUser() || sessionStorage.getItem("cinemaAccessToken")) {
    return;
  }
  registerDialog?.showModal();
});
document.querySelector("#openRegisterBtn")?.addEventListener("click", () => {
  loginDialog?.close();
  registerDialog?.showModal();
});
document.querySelector("#myReservationsBtn")?.addEventListener("click", openMyReservations);
document.querySelectorAll("[data-close-reservations]").forEach(button => {
  button.addEventListener("click", () => reservationsDialog?.close());
});
const storedUser = JSON.parse(sessionStorage.getItem("cinemaUser") || "null");
if (storedUser?.role === "admin") {
  const adminLink = document.querySelector("#adminLink");
  if (adminLink) adminLink.hidden = false;
}
syncAuthUI();
document.querySelector("#loginForm").addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.currentTarget);
  try {
    const user = await api("/auth/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: fd.get("email"), password: fd.get("password") }) });
    sessionStorage.setItem("cinemaUser", JSON.stringify(user));
    syncAuthUI();
    document.querySelector("#loginNote").textContent = "Вы вошли в аккаунт.";
    if (user.role === "admin") {
      if (location.pathname.endsWith("/admin.html")) {
        window.dispatchEvent(new CustomEvent("cinema:authenticated", { detail: user }));
      } else {
        location.href = "admin.html";
        return;
      }
    }
    setTimeout(() => loginDialog.close(), 700);
  } catch {
    document.querySelector("#loginNote").textContent = "Не удалось выполнить вход через API.";
  }
});

document.querySelector("#registerForm")?.addEventListener("submit", async e => {
  e.preventDefault();
  const fd = new FormData(e.currentTarget);
  try {
    const user = await api("/auth/registration", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        nickname: fd.get("nickname"),
        email: fd.get("email"),
        password: fd.get("password")
      })
    });
    sessionStorage.setItem("cinemaUser", JSON.stringify(user));
    syncAuthUI();
    document.querySelector("#registerNote").textContent = "Аккаунт создан. Вы вошли в систему.";
    setTimeout(() => registerDialog?.close(), 700);
  } catch (error) {
    console.error("Не удалось зарегистрироваться:", error);
    document.querySelector("#registerNote").textContent = "Не удалось создать аккаунт. Проверьте данные и попробуйте снова.";
  }
});

function getImageUrl(image) {
  if (!image) return "";
  if (/^https?:\/\//i.test(image)) return image;
  return `${API_BASE.replace(/\/$/, "")}/movies/images/${image}`;
}
function toDateInput(date) { return date.toISOString().slice(0, 10); }
function formatDate(value) {
  if (!value) return "";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
}
function formatTime(value) {
  if (!value) return "";
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? String(value) : d.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" });
}
function getTokenUserId() {
  const token = sessionStorage.getItem("cinemaAccessToken");
  if (!token) return "";
  try {
    const payload = JSON.parse(atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/")));
    return payload.sub || "";
  } catch {
    return "";
  }
}
function escapeHtml(v = "") { return String(v).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c])); }

loadData();
