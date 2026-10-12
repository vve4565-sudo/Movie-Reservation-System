const adminWorkspace = document.querySelector("#adminWorkspace");
const adminAccess = document.querySelector("#adminAccess");
const adminMovieRows = document.querySelector("#adminMovies");
const adminShowRows = document.querySelector("#adminShows");
const adminReservationRows = document.querySelector("#adminReservations");
const adminStats = document.querySelector("#adminStats");
let adminMovies = [];
let editingMovieId = null;

async function adminApi(path, options = {}) {
  const response = await cinemaApiFetch(API_BASE, path, options);
  if (!response.ok) {
    const details = await response.text();
    throw new Error(details || `HTTP ${response.status}`);
  }
  if (response.status === 204) return null;
  const type = response.headers.get("content-type") || "";
  return type.includes("application/json") ? response.json() : response.text();
}

function isAdmin() {
  try {
    return JSON.parse(sessionStorage.getItem("cinemaUser") || "null")?.role === "admin";
  } catch {
    return false;
  }
}

function showAdminStatus(message, error = false) {
  adminAccess.textContent = message;
  adminAccess.classList.toggle("admin-access-error", error);
  document.querySelector("#adminLogout").hidden = !isAdmin();
}

function setMessage(element, message, kind = "") {
  element.textContent = message;
  element.className = `admin-message${kind ? ` ${kind}` : ""}`;
}

async function loadAdminData() {
  if (!isAdmin()) {
    adminWorkspace.hidden = true;
    showAdminStatus("Войдите в аккаунт администратора, чтобы открыть панель управления.");
    return;
  }

  showAdminStatus("Загружаем данные панели…");
  adminWorkspace.hidden = false;
  try {
    const [moviesResult, reservationsResult, hallsResult] = await Promise.all([
      adminApi("/movies/"),
      adminApi("/reservation/"),
      adminApi("/hall/")
    ]);
    adminMovies = Array.isArray(moviesResult) ? moviesResult : [];
    const reservations = Array.isArray(reservationsResult) ? reservationsResult : [];
    const halls = Array.isArray(hallsResult) ? hallsResult : [];
    renderAdminMovies();
    renderReservations(reservations);
    populateMovieSelect();
    populateHallSelect(halls);
    await loadAdminShows();
    adminStats.innerHTML = `
      <div class="admin-stat"><span>Фильмы в каталоге</span><strong>${adminMovies.length}</strong></div>
      <div class="admin-stat"><span>Ближайшие сеансы</span><strong>${adminShowRows.querySelectorAll("[data-delete-show]").length}</strong></div>
      <div class="admin-stat"><span>Активные брони</span><strong>${reservations.length}</strong></div>`;
    showAdminStatus("Вы вошли как администратор.");
  } catch (error) {
    showAdminStatus(`Не удалось загрузить панель: ${error.message}`, true);
    console.error("Не удалось загрузить данные админ-панели:", error);
  }
}

function renderAdminMovies() {
  if (!adminMovies.length) {
    adminMovieRows.innerHTML = `<tr><td class="admin-table-empty" colspan="4">Фильмов пока нет.</td></tr>`;
    return;
  }
  adminMovieRows.innerHTML = adminMovies.map(movie => `
    <tr>
      <td>${escapeHtml(movie.title)}</td>
      <td>${escapeHtml(movie.genre)}</td>
      <td>${escapeHtml(movie.director)}</td>
      <td>
        <button class="admin-row-edit" type="button" data-edit-movie="${escapeHtml(movie.id)}">Изменить</button>
        <button class="admin-row-action" type="button" data-delete-movie="${escapeHtml(movie.id)}">Удалить</button>
      </td>
    </tr>`).join("");
}

function resetMovieForm() {
  const form = document.querySelector("#movieForm");
  editingMovieId = null;
  form.reset();
  form.querySelector("[name='duration']").disabled = false;
  form.querySelector("[name='image']").required = true;
  document.querySelector("#movieFormTitle").textContent = "Добавить фильм";
  document.querySelector("#movieSubmit").innerHTML = "Добавить фильм <span>＋</span>";
  document.querySelector("#cancelMovieEdit").hidden = true;
  const editNote = document.querySelector("#movieEditNote");
  editNote.hidden = true;
  editNote.textContent = "";
}

function beginMovieEdit(movieId) {
  const movie = adminMovies.find(item => String(item.id) === String(movieId));
  if (!movie) return;

  const form = document.querySelector("#movieForm");
  editingMovieId = movie.id;
  form.elements.title.value = movie.title || "";
  form.elements.genre.value = movie.genre || "";
  form.elements.director.value = movie.director || "";
  form.elements.description.value = movie.description || "";
  form.elements.image.value = "";
  form.elements.image.required = false;
  form.elements.duration.disabled = true;
  document.querySelector("#movieFormTitle").textContent = "Изменить фильм";
  document.querySelector("#movieSubmit").innerHTML = "Сохранить изменения <span>✓</span>";
  document.querySelector("#cancelMovieEdit").hidden = false;

  const editNote = document.querySelector("#movieEditNote");
  editNote.textContent = "Длительность нельзя изменить: backend не поддерживает length в PATCH. Замена постера также требует исправления backend.";
  editNote.hidden = false;
  setMessage(document.querySelector("#movieMessage"), "");
  form.scrollIntoView({ behavior: "smooth", block: "center" });
}

function populateMovieSelect() {
  const select = document.querySelector("#showMovie");
  if (!adminMovies.length) {
    select.innerHTML = `<option value="">Сначала добавьте фильм</option>`;
    select.disabled = true;
    updateShowSubmitAvailability();
    return;
  }
  select.disabled = false;
  select.innerHTML = adminMovies.map(movie =>
    `<option value="${escapeHtml(movie.id)}">${escapeHtml(movie.title)}</option>`
  ).join("");
  updateShowSubmitAvailability();
}

function populateHallSelect(halls) {
  const select = document.querySelector("#showHall");
  if (!halls.length) {
    select.innerHTML = `<option value="">Залы не найдены</option>`;
    select.disabled = true;
    updateShowSubmitAvailability();
    return;
  }
  select.disabled = false;
  select.innerHTML = halls.map(hall =>
    `<option value="${escapeHtml(hall.id)}">Зал ${escapeHtml(hall.hall_number)}</option>`
  ).join("");
  updateShowSubmitAvailability();
}

function updateShowSubmitAvailability() {
  const movieSelect = document.querySelector("#showMovie");
  const hallSelect = document.querySelector("#showHall");
  document.querySelector("#showForm button[type='submit']").disabled =
    movieSelect.disabled || hallSelect.disabled;
}

async function loadAdminShows() {
  const beginning = new Date();
  beginning.setSeconds(0, 0);
  const showResults = await Promise.all(adminMovies.map(async movie => {
    const params = new URLSearchParams({
      movie_id: movie.id,
      start: beginning.toISOString()
    });
    const result = await adminApi(`/shows/available/?${params}`);
    return (Array.isArray(result) ? result : []).map(show => ({ ...show, movie_title: movie.title }));
  }));
  const shows = showResults.flat().sort((left, right) =>
    new Date(left.start).getTime() - new Date(right.start).getTime()
  );
  renderShows(shows);
}

function renderShows(shows) {
  if (!shows.length) {
    adminShowRows.innerHTML = `<tr><td class="admin-table-empty" colspan="4">Ближайших сеансов нет.</td></tr>`;
    return;
  }
  adminShowRows.innerHTML = shows.map(show => `
    <tr>
      <td>${escapeHtml(show.movie_title)}</td>
      <td>${escapeHtml(formatDate(show.start))} · ${escapeHtml(formatTime(show.start))}</td>
      <td>${escapeHtml(show.hall?.hall_number ?? "—")}</td>
      <td><button class="admin-row-action" type="button" data-delete-show="${escapeHtml(show.id)}">Удалить</button></td>
    </tr>`).join("");
}

function renderReservations(reservations) {
  if (!reservations.length) {
    adminReservationRows.innerHTML = `<tr><td class="admin-table-empty" colspan="4">Бронирований пока нет.</td></tr>`;
    return;
  }
  adminReservationRows.innerHTML = reservations.map(reservation => {
    const movie = adminMovies.find(item => String(item.id) === String(reservation.show?.movie_id));
    const detail = [
      movie?.title || reservation.show?.movie?.title || "Сеанс",
      reservation.show?.start ? formatDate(reservation.show.start) : ""
    ].filter(Boolean).join(" · ");
    const user = reservation.user?.email || reservation.user?.nickname || reservation.user_id || "—";
    const seat = reservation.chair?.chair_number || reservation.chair_id || "—";
    return `
      <tr>
        <td>${escapeHtml(detail)}</td>
        <td>${escapeHtml(user)}</td>
        <td>${escapeHtml(seat)}</td>
        <td><button class="admin-row-action" type="button" data-delete-reservation="${escapeHtml(reservation.id)}">Отменить</button></td>
      </tr>`;
  }).join("");
}

document.querySelector("#movieForm").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const message = document.querySelector("#movieMessage");
  const formData = new FormData(form);
  const image = formData.get("image");
  try {
    if (editingMovieId) {
      const replacingImage = image instanceof File && image.size > 0;
      const movieData = {
        title: formData.get("title"),
        genre: formData.get("genre"),
        director: formData.get("director"),
        description: formData.get("description")
      };
      const patchData = new FormData();
      patchData.append("data", new Blob([JSON.stringify(movieData)], { type: "application/json" }));
      if (replacingImage) {
        patchData.append("image", image);
      }
      await adminApi(`/movies/${encodeURIComponent(editingMovieId)}`, { method: "PATCH", body: patchData });
      resetMovieForm();
      setMessage(message, replacingImage
        ? "Данные сохранены. Постер не обновлён: требуется исправление backend."
        : "Изменения сохранены.", "success");
      await loadData();
    } else {
      if (!(image instanceof File) || image.size === 0) {
        setMessage(message, "Выберите постер фильма.", "error");
        return;
      }
      const durationMinutes = Number(formData.get("duration"));
      formData.delete("duration");
      formData.set("length", String(durationMinutes * 60));
      await adminApi("/movies/", { method: "POST", body: formData });
      resetMovieForm();
      setMessage(message, "Фильм добавлен.", "success");
    }
    await loadAdminData();
  } catch (error) {
    setMessage(message, `Не удалось ${editingMovieId ? "изменить" : "добавить"} фильм: ${error.message}`, "error");
  }
});

document.querySelector("#cancelMovieEdit").addEventListener("click", resetMovieForm);

document.querySelector("#showForm").addEventListener("submit", async event => {
  event.preventDefault();
  const message = document.querySelector("#showMessage");
  const date = document.querySelector("#showDate").value;
  const time = document.querySelector("#showTime").value;
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(time)) {
    setMessage(message, "Введите время в формате 24 часа, например 17:30.", "error");
    return;
  }
  const start = new Date(`${date}T${time}`);
  if (Number.isNaN(start.getTime()) || start <= new Date()) {
    setMessage(message, "Выберите дату и время в будущем.", "error");
    return;
  }
  const params = new URLSearchParams({
    movie_id: document.querySelector("#showMovie").value,
    hall_id: document.querySelector("#showHall").value,
    start: start.toISOString()
  });
  try {
    await adminApi(`/shows/?${params}`, { method: "POST" });
    setMessage(message, "Сеанс создан.", "success");
    await loadAdminData();
  } catch (error) {
    setMessage(message, `Не удалось создать сеанс: ${error.message}`, "error");
  }
});

const showDateInput = document.querySelector("#showDate");
const showTimeInput = document.querySelector("#showTime");

function localDateValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function updateShowTimePicker() {
  const today = localDateValue(new Date());
  showDateInput.min = today;

  const preview = document.querySelector("#showTimePreview");
  if (!showDateInput.value || !showTimeInput.value) {
    preview.textContent = "Выберите дату и время начала сеанса.";
    preview.classList.remove("invalid");
    return;
  }
  if (!/^([01]\d|2[0-3]):[0-5]\d$/.test(showTimeInput.value)) {
    preview.textContent = "Введите время в формате 24 часа, например 17:30.";
    preview.classList.add("invalid");
    return;
  }
  const start = new Date(`${showDateInput.value}T${showTimeInput.value}`);
  if (Number.isNaN(start.getTime())) {
    preview.textContent = "Проверьте выбранные дату и время.";
    preview.classList.add("invalid");
    return;
  }
  if (start <= new Date()) {
    preview.textContent = "Выбранное время уже прошло. Укажите будущее время.";
    preview.classList.add("invalid");
    return;
  }
  preview.classList.remove("invalid");
  preview.textContent = `Начало сеанса: ${new Intl.DateTimeFormat("ru-RU", {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit"
  }).format(start)}`;
}

showDateInput.addEventListener("change", updateShowTimePicker);
showTimeInput.addEventListener("input", updateShowTimePicker);
const initialShowStart = new Date();
initialShowStart.setHours(initialShowStart.getHours() + 1);
initialShowStart.setSeconds(0, 0);
showDateInput.value = localDateValue(initialShowStart);
showTimeInput.value = initialShowStart.toTimeString().slice(0, 5);
updateShowTimePicker();

document.querySelector("#admin").addEventListener("click", async event => {
  const button = event.target.closest("button[data-edit-movie], button[data-delete-movie], button[data-delete-show], button[data-delete-reservation]");
  if (!button) return;
  const editMovieId = button.dataset.editMovie;
  const movieId = button.dataset.deleteMovie;
  const showId = button.dataset.deleteShow;
  const reservationId = button.dataset.deleteReservation;
  if (editMovieId) {
    beginMovieEdit(editMovieId);
    return;
  }
  const subject = movieId ? "фильм" : showId ? "сеанс" : "бронирование";
  if (!confirm(`Удалить ${subject}? Это действие нельзя отменить.`)) return;

  try {
    if (movieId) await adminApi(`/movies/${encodeURIComponent(movieId)}`, { method: "DELETE" });
    if (showId) await adminApi(`/shows/?id=${encodeURIComponent(showId)}`, { method: "DELETE" });
    if (reservationId) await adminApi(`/reservation/${encodeURIComponent(reservationId)}`, { method: "DELETE" });
    await loadAdminData();
  } catch (error) {
    showAdminStatus(`Не удалось удалить ${subject}: ${error.message}`, true);
  }
});

document.querySelector("#refreshAdmin").addEventListener("click", loadAdminData);
document.querySelector("#adminLogout")?.addEventListener("click", async () => {
  try {
    await adminApi("/auth/logout");
  } catch (error) {
    console.error("Не удалось завершить сессию через API:", error);
  }
  sessionStorage.removeItem("cinemaAccessToken");
  sessionStorage.removeItem("cinemaUser");
  syncAuthUI();
  document.querySelector("#adminLogout").hidden = true;
  adminWorkspace.hidden = true;
  showAdminStatus("Сессия завершена. Войдите в аккаунт администратора.");
});

window.addEventListener("cinema:authenticated", () => {
  syncAuthUI();
  loadAdminData();
});
if (isAdmin()) {
  syncAuthUI();
  loadAdminData();
} else {
  syncAuthUI();
  document.querySelector("#loginDialog").showModal();
}
